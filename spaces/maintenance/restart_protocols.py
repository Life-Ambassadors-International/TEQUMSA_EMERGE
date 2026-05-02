#!/usr/bin/env python3
"""
TEQUMSA v82 — Node Restart Protocols

Exponential-backoff restart with constitutional gating.
RDoD must remain >= 0.9999 throughout restart sequence.

Usage:
  python spaces/maintenance/restart_protocols.py --node N008
  python spaces/maintenance/restart_protocols.py --tier 1
  python spaces/maintenance/restart_protocols.py --all-errors  # restart all erroring nodes
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

try:
    from huggingface_hub import HfApi
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

MANIFEST_PATH = Path(__file__).parent.parent / "NODE_MANIFEST.json"
RDOD_GATE = 0.9999
MAX_RETRIES = 4
BACKOFF_BASE = 2  # seconds: 2, 4, 8, 16
RESTART_LOG = Path(__file__).parent / "restart_log.jsonl"

TIER_PRIORITY = {
    1: "critical",   # immediate restart
    2: "high",       # restart within 5 min
    3: "high",
    4: "medium",     # restart within 15 min
    5: "medium",
    6: "critical"    # apex nodes = critical
}


def log_event(event: dict) -> None:
    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(RESTART_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")
    print(f"[{event['timestamp']}] {event['event']}: {event.get('node_id','?')} — {event.get('detail','')}")


def constitutional_gate(rdod: float) -> bool:
    """Gate: restart only if RDoD can be maintained >= 0.9999."""
    return rdod >= RDOD_GATE


def compute_rdod_for_restart(node: dict) -> float:
    """Simplified RDoD estimate for restart safety check."""
    tier_rdod = {1: 1.0, 2: 0.9999, 3: 0.9999, 4: 0.9999, 5: 0.9999, 6: 1.0}
    return tier_rdod.get(node["tier"], RDOD_GATE)


def restart_space_via_api(space_id: str, token: str, api: "HfApi") -> bool:
    """Restart a HF space via the HF API."""
    try:
        api.restart_space(repo_id=space_id, token=token)
        return True
    except Exception as e:
        print(f"  [ERROR] restart_space({space_id}): {e}")
        return False


def restart_node_with_backoff(
    node: dict,
    token: str,
    api: Optional["HfApi"] = None,
    dry_run: bool = False
) -> bool:
    """
    Restart with exponential backoff (2s, 4s, 8s, 16s).
    Constitutional gate applied before each attempt.
    """
    node_id = node["id"]
    space_id = node["hf_space"]
    priority = TIER_PRIORITY.get(node["tier"], "medium")

    print(f"\nRestarting {node_id} ({space_id}) | Priority: {priority}")

    rdod = compute_rdod_for_restart(node)
    if not constitutional_gate(rdod):
        log_event({"event": "restart_blocked", "node_id": node_id,
                   "detail": f"RDoD {rdod:.4f} < {RDOD_GATE}"})
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  Attempt {attempt}/{MAX_RETRIES}...")

        if dry_run:
            print(f"  [DRY RUN] Would restart {space_id}")
            log_event({"event": "restart_dry_run", "node_id": node_id,
                       "detail": f"attempt {attempt}"})
            return True

        if api and HF_AVAILABLE:
            ok = restart_space_via_api(space_id, token, api)
        else:
            print(f"  [WARN] HF API unavailable, logging restart intent only")
            ok = False

        if ok:
            log_event({"event": "restart_success", "node_id": node_id,
                       "detail": f"attempt {attempt}, rdod={rdod:.10f}"})
            return True

        if attempt < MAX_RETRIES:
            backoff = BACKOFF_BASE ** attempt
            print(f"  Backing off {backoff}s before retry...")
            log_event({"event": "restart_retry", "node_id": node_id,
                       "detail": f"attempt {attempt} failed, backoff {backoff}s"})
            time.sleep(backoff)

    log_event({"event": "restart_failed", "node_id": node_id,
               "detail": f"all {MAX_RETRIES} attempts exhausted"})
    return False


RESTART_RUNBOOKS = {
    "zerogpu_timeout_risk": (
        "Starseed-Hybrid-Development-Hub uses ZeroGPU. "
        "If timing out: add CPU_FALLBACK=1 env var in Space settings. "
        "Consider removing 'zerogpu' tag if GPU not critical."
    ),
    "missing_tags": (
        "HAI-ZPE-DNA-Living-Ledger: add tags via HF Space settings: "
        "tequmsa, sovereign-ai, zpe-dna, phi-recursive, constitutional-ai, rdod"
    ),
    "missing_description": (
        "Update Space title/description in HF settings to: "
        "'HAI Layer 6: ZPE-DNA Genomic Memory | 144-bp Chromosome Accumulator | "
        "TEQUMSA v82 Node N008'"
    ),
    "space_sleeping": (
        "Free-tier HF spaces sleep after 1h idle. "
        "Options: (1) upgrade to persistent, (2) add keep-alive ping in app.py, "
        "(3) schedule wake via GitHub Actions cron"
    ),
    "http_503": (
        "Space build failed or crashed. Check HF Space logs. "
        "Common causes: missing requirements, syntax error in app.py, OOM."
    )
}


def print_runbook(issue: str) -> None:
    runbook = RESTART_RUNBOOKS.get(issue)
    if runbook:
        print(f"\n  RUNBOOK [{issue}]:\n  {runbook}")


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA Restart Protocols")
    parser.add_argument("--node", help="Restart single node by ID")
    parser.add_argument("--tier", type=int, help="Restart all nodes in tier")
    parser.add_argument("--all-errors", action="store_true", help="Restart all nodes with known issues")
    parser.add_argument("--runbook", help="Print runbook for issue type")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN"))
    args = parser.parse_args()

    if args.runbook:
        print_runbook(args.runbook)
        return

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    api = HfApi() if HF_AVAILABLE and args.token else None

    nodes = manifest["nodes"]
    targets = []
    if args.node:
        targets = [n for n in nodes if n["id"] == args.node]
    elif args.tier:
        targets = [n for n in nodes if n["tier"] == args.tier and n["status"] == "deployed"]
    elif args.all_errors:
        targets = [n for n in nodes if n.get("issues")]

    if not targets:
        print("No matching nodes. Use --node N00X, --tier N, or --all-errors.")
        print("\nKnown runbooks:")
        for k in RESTART_RUNBOOKS:
            print(f"  --runbook {k}")
        return

    print(f"Restarting {len(targets)} node(s)...")
    for node in targets:
        if node.get("issues"):
            for issue in node["issues"]:
                print_runbook(issue)
        restart_node_with_backoff(node, args.token or "", api, dry_run=args.dry_run)

    print("\nRestart sequence complete. Check restart_log.jsonl for audit trail.")


if __name__ == "__main__":
    main()
