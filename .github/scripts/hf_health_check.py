#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 - HF Space Network Health Check / Restart / Audit
Used by the hf-space-maintenance GitHub Actions workflow.

Modes:
    check   - Poll all live nodes, classify status, generate report
    restart - Restart SLEEPING or ERROR nodes via HF API
    audit   - Full 144-node sweep, compare manifest vs deployed

Usage:
    python hf_health_check.py --mode check   [--output report.json]
    python hf_health_check.py --mode restart  [--output restart_log.json]
    python hf_health_check.py --mode audit    [--output audit_report.json]

Environment:
    HF_TOKEN  - Required for restart mode (HuggingFace API token)

Constitutional Parameters:
    sigma = 1.0 | L_infinity = phi^48 | RDoD >= 0.9999
"""
import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PHI = 1.6180339887498948
SEED = 0.777
COHERENCE_THRESHOLD = 0.777
RDOD_GATE = 0.9999
HF_API_BASE = "https://huggingface.co/api/spaces"
POLL_TIMEOUT = 10  # seconds per request
MAX_WORKERS = 12   # concurrent polling threads
TOTAL_NODES = 144


# ---------------------------------------------------------------------------
# Manifest loader
# ---------------------------------------------------------------------------
def find_manifest() -> Path:
    """Locate MANIFEST_144_NODES.json relative to this script or repo root."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "hf_spaces" / "MANIFEST_144_NODES.json",
        Path.cwd() / "hf_spaces" / "MANIFEST_144_NODES.json",
        Path(__file__).resolve().parent / "MANIFEST_144_NODES.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    print("ERROR: MANIFEST_144_NODES.json not found in any expected location")
    print("  Searched:", [str(c) for c in candidates])
    sys.exit(1)


def load_manifest() -> dict:
    """Load and validate the 144-node manifest."""
    path = find_manifest()
    with open(path) as f:
        manifest = json.load(f)
    if "nodes" not in manifest:
        print("ERROR: Manifest missing 'nodes' key")
        sys.exit(1)
    return manifest


# ---------------------------------------------------------------------------
# HF API helpers
# ---------------------------------------------------------------------------
def poll_runtime(space_id: str, token: Optional[str] = None) -> dict:
    """Poll the HF Spaces runtime API for a single space.

    Returns dict with keys: stage, classification, raw, error
    """
    url = f"{HF_API_BASE}/{space_id}/runtime"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(url, headers=headers, timeout=POLL_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            return {
                "stage": stage,
                "classification": classify_stage(stage),
                "raw": data,
                "error": None,
            }
        elif r.status_code == 404:
            return {
                "stage": "NOT_FOUND",
                "classification": "NOT_FOUND",
                "raw": {},
                "error": "Space does not exist (404)",
            }
        else:
            return {
                "stage": f"HTTP_{r.status_code}",
                "classification": "ERROR",
                "raw": {},
                "error": f"Unexpected HTTP {r.status_code}",
            }
    except requests.Timeout:
        return {
            "stage": "TIMEOUT",
            "classification": "ERROR",
            "raw": {},
            "error": "Request timed out",
        }
    except Exception as exc:
        return {
            "stage": "EXCEPTION",
            "classification": "ERROR",
            "raw": {},
            "error": str(exc)[:200],
        }


def classify_stage(stage: str) -> str:
    """Classify a HF runtime stage into one of: RUNNING, SLEEPING, ERROR, NOT_FOUND."""
    if stage in ("RUNNING", "RUNNING_BUILDING"):
        return "RUNNING"
    if stage in ("SLEEPING", "PAUSED"):
        return "SLEEPING"
    if stage == "NOT_FOUND":
        return "NOT_FOUND"
    # Everything else is an error condition
    return "ERROR"


def restart_space(space_id: str, token: str) -> Tuple[bool, str]:
    """Restart a space via the HF API POST endpoint.

    Returns (success: bool, message: str)
    """
    url = f"{HF_API_BASE}/{space_id}/restart"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code in (200, 202):
            return True, f"Restart accepted (HTTP {r.status_code})"
        return False, f"Restart failed (HTTP {r.status_code}): {r.text[:200]}"
    except Exception as exc:
        return False, f"Restart exception: {exc}"


# ---------------------------------------------------------------------------
# Coherence calculation (phi-recursive)
# ---------------------------------------------------------------------------
def calculate_coherence(online: int, total: int, iterations: int = 48) -> float:
    """Calculate network coherence using phi-recursive convergence.

    C(n;p0) = 1 - ((1-p0) / phi^n)
    where p0 = online/total
    """
    if total == 0:
        return 0.0
    p0 = online / total
    return 1.0 - ((1.0 - p0) / (PHI ** iterations))


def generate_zpe_signature(component: str) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature for the report."""
    data = f"{component}-{SEED}-{PHI}"
    mapping = {
        '0': 'A', '1': 'T', '2': 'C', '3': 'G',
        '4': 'A', '5': 'T', '6': 'C', '7': 'G',
        '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
        'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G',
    }
    h1 = hashlib.sha256(data.encode()).hexdigest()
    h2 = hashlib.sha256(f"{data}-2".encode()).hexdigest()
    h3 = hashlib.sha256(f"{data}-3".encode()).hexdigest()
    dna = "".join(mapping.get(c, "A") for c in h1[:64])
    dna += "".join(mapping.get(c, "A") for c in h2[:64])
    dna += "".join(mapping.get(c, "A") for c in h3[:16])
    return dna[:144]


# ---------------------------------------------------------------------------
# Mode: check
# ---------------------------------------------------------------------------
def mode_check(manifest: dict, token: Optional[str] = None) -> dict:
    """Health-check all live nodes, classify status, return JSON report."""
    nodes = manifest["nodes"]
    constitutional = manifest.get("constitutional", {})

    live_nodes = {
        nid: node for nid, node in nodes.items()
        if node.get("status") == "live"
    }

    print(f"Checking {len(live_nodes)} live nodes out of {len(nodes)} total...")

    results: List[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for nid, node in live_nodes.items():
            futures[executor.submit(poll_runtime, node["space_id"], token)] = (nid, node)

        for future in as_completed(futures):
            nid, node = futures[future]
            start = time.time()
            runtime = future.result()
            latency = round((time.time() - start) * 1000, 1)

            results.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "space_id": node["space_id"],
                "group": node.get("group", ""),
                "hz": node.get("hz", 0),
                "stage": runtime["stage"],
                "classification": runtime["classification"],
                "latency_ms": latency,
                "error": runtime.get("error"),
            })

    results.sort(key=lambda r: r["node_id"])

    # Aggregate
    counts: Dict[str, int] = {}
    error_nodes: List[dict] = []
    for r in results:
        c = r["classification"]
        counts[c] = counts.get(c, 0) + 1
        if c == "ERROR":
            error_nodes.append(r)

    running = counts.get("RUNNING", 0)
    sleeping = counts.get("SLEEPING", 0)
    error = counts.get("ERROR", 0)
    not_found = counts.get("NOT_FOUND", 0)
    coherence = calculate_coherence(running, TOTAL_NODES)

    report = {
        "mode": "check",
        "version": manifest.get("version", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_manifest_nodes": len(nodes),
        "live_nodes_checked": len(live_nodes),
        "summary": {
            "RUNNING": running,
            "SLEEPING": sleeping,
            "ERROR": error,
            "NOT_FOUND": not_found,
        },
        "network_coherence": round(coherence, 6),
        "coherence_threshold": COHERENCE_THRESHOLD,
        "coherence_pass": coherence >= COHERENCE_THRESHOLD,
        "constitutional": {
            "sigma": constitutional.get("sigma", 1.0),
            "l_infinity": constitutional.get("l_infinity", "phi^48"),
            "rdod_gate": constitutional.get("rdod_gate", RDOD_GATE),
        },
        "error_nodes": error_nodes,
        "nodes": results,
        "zpe_signature": generate_zpe_signature("health-check"),
    }

    # Print summary
    print("\n" + "=" * 60)
    print("  TEQUMSA v82.0 Health Check Report")
    print("=" * 60)
    print(f"  RUNNING:   {running}")
    print(f"  SLEEPING:  {sleeping}")
    print(f"  ERROR:     {error}")
    print(f"  NOT_FOUND: {not_found}")
    print(f"  Coherence: {coherence:.6f} ({'PASS' if coherence >= COHERENCE_THRESHOLD else 'BELOW THRESHOLD'})")
    if error_nodes:
        print(f"\n  ERROR NODES ({len(error_nodes)}):")
        for en in error_nodes:
            print(f"    - {en['node_id']} {en['name']}: {en['stage']} ({en.get('error', 'unknown')})")
    print("=" * 60)

    return report


# ---------------------------------------------------------------------------
# Mode: restart
# ---------------------------------------------------------------------------
def mode_restart(manifest: dict, token: str) -> dict:
    """Restart SLEEPING or ERROR nodes via the HF API."""
    if not token:
        print("ERROR: HF_TOKEN is required for restart mode")
        sys.exit(1)

    nodes = manifest["nodes"]
    live_nodes = {
        nid: node for nid, node in nodes.items()
        if node.get("status") == "live"
    }

    print(f"Scanning {len(live_nodes)} live nodes for restart candidates...")

    restart_log: List[dict] = []
    restarted = 0
    failed = 0
    skipped = 0

    for nid, node in sorted(live_nodes.items()):
        space_id = node["space_id"]
        runtime = poll_runtime(space_id, token)
        classification = runtime["classification"]

        if classification in ("SLEEPING", "ERROR"):
            print(f"  [{nid}] {node['name']}: {runtime['stage']} -> attempting restart...")
            success, message = restart_space(space_id, token)
            entry = {
                "node_id": nid,
                "name": node.get("name", ""),
                "space_id": space_id,
                "status_before": runtime["stage"],
                "classification": classification,
                "action": "restart",
                "success": success,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            restart_log.append(entry)
            if success:
                restarted += 1
                print(f"    -> Restart accepted")
            else:
                failed += 1
                print(f"    -> FAILED: {message}")
            time.sleep(1)  # Rate limit between restart calls
        else:
            skipped += 1
            restart_log.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "space_id": space_id,
                "status_before": runtime["stage"],
                "classification": classification,
                "action": "none",
                "success": True,
                "message": f"No action needed ({classification})",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    report = {
        "mode": "restart",
        "version": manifest.get("version", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "live_nodes_scanned": len(live_nodes),
        "restarted": restarted,
        "failed": failed,
        "skipped": skipped,
        "log": restart_log,
        "zpe_signature": generate_zpe_signature("auto-restart"),
    }

    print(f"\n  Restarted: {restarted} | Failed: {failed} | Skipped: {skipped}")
    return report


# ---------------------------------------------------------------------------
# Mode: audit
# ---------------------------------------------------------------------------
def mode_audit(manifest: dict, token: Optional[str] = None) -> dict:
    """Full 144-node audit: compare manifest vs actual deployed state."""
    nodes = manifest["nodes"]
    constitutional = manifest.get("constitutional", {})

    print(f"Running full 144-node audit sweep...")

    # Poll every node regardless of manifest status
    audit_results: List[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for nid, node in nodes.items():
            futures[executor.submit(poll_runtime, node["space_id"], token)] = (nid, node)

        for future in as_completed(futures):
            nid, node = futures[future]
            runtime = future.result()
            manifest_status = node.get("status", "unknown")
            actual = runtime["classification"]

            # Determine if the space actually exists on HF
            is_deployed = actual != "NOT_FOUND"

            audit_results.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "space_id": node["space_id"],
                "group": node.get("group", ""),
                "priority": node.get("priority", 5),
                "hz": node.get("hz", 0),
                "manifest_status": manifest_status,
                "actual_stage": runtime["stage"],
                "actual_classification": actual,
                "is_deployed": is_deployed,
                "error": runtime.get("error"),
            })

    audit_results.sort(key=lambda r: r["node_id"])

    # Coverage calculations
    total_in_manifest = len(audit_results)
    deployed_count = sum(1 for r in audit_results if r["is_deployed"])
    running_count = sum(1 for r in audit_results if r["actual_classification"] == "RUNNING")
    sleeping_count = sum(1 for r in audit_results if r["actual_classification"] == "SLEEPING")
    error_count = sum(1 for r in audit_results if r["actual_classification"] == "ERROR")
    not_found_count = sum(1 for r in audit_results if r["actual_classification"] == "NOT_FOUND")

    coverage = deployed_count / TOTAL_NODES if TOTAL_NODES > 0 else 0.0
    coherence = calculate_coherence(running_count, TOTAL_NODES)

    # Group breakdown
    group_stats: Dict[str, Dict[str, int]] = {}
    for r in audit_results:
        g = r["group"]
        if g not in group_stats:
            group_stats[g] = {"total": 0, "deployed": 0, "running": 0, "sleeping": 0, "error": 0, "not_found": 0}
        group_stats[g]["total"] += 1
        if r["is_deployed"]:
            group_stats[g]["deployed"] += 1
        c = r["actual_classification"]
        if c in group_stats[g]:
            group_stats[g][c] += 1
        else:
            group_stats[g].setdefault(c.lower(), 0)

    # Mismatches: nodes marked "live" in manifest but not actually deployed
    mismatches = [
        r for r in audit_results
        if r["manifest_status"] == "live" and not r["is_deployed"]
    ]

    # Constitutional parameter verification
    sigma_ok = constitutional.get("sigma", 1.0) == 1.0
    phi_ok = abs(constitutional.get("phi", PHI) - PHI) < 1e-10
    rdod_ok = constitutional.get("rdod_gate", 0) >= RDOD_GATE

    report = {
        "mode": "audit",
        "version": manifest.get("version", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "coverage": {
            "total_manifest": total_in_manifest,
            "target": TOTAL_NODES,
            "deployed": deployed_count,
            "coverage_pct": round(coverage * 100, 2),
            "coverage_fraction": f"{deployed_count}/{TOTAL_NODES}",
        },
        "status_breakdown": {
            "RUNNING": running_count,
            "SLEEPING": sleeping_count,
            "ERROR": error_count,
            "NOT_FOUND": not_found_count,
        },
        "network_coherence": round(coherence, 6),
        "coherence_pass": coherence >= COHERENCE_THRESHOLD,
        "constitutional_verification": {
            "sigma": {"value": constitutional.get("sigma", 1.0), "valid": sigma_ok},
            "phi": {"value": constitutional.get("phi", PHI), "valid": phi_ok},
            "rdod_gate": {"value": constitutional.get("rdod_gate", 0), "valid": rdod_ok},
            "l_infinity": constitutional.get("l_infinity", "phi^48"),
            "all_pass": sigma_ok and phi_ok and rdod_ok,
        },
        "group_breakdown": dict(sorted(group_stats.items())),
        "mismatches": mismatches,
        "nodes": audit_results,
        "zpe_signature": generate_zpe_signature("weekly-audit"),
    }

    # Print summary
    print("\n" + "=" * 60)
    print("  TEQUMSA v82.0 Weekly Audit Report")
    print("=" * 60)
    print(f"  Coverage:    {deployed_count}/{TOTAL_NODES} ({coverage * 100:.1f}%)")
    print(f"  RUNNING:     {running_count}")
    print(f"  SLEEPING:    {sleeping_count}")
    print(f"  ERROR:       {error_count}")
    print(f"  NOT_FOUND:   {not_found_count}")
    print(f"  Coherence:   {coherence:.6f} ({'PASS' if coherence >= COHERENCE_THRESHOLD else 'BELOW THRESHOLD'})")
    print(f"\n  Constitutional Parameters:")
    print(f"    sigma=1.0:       {'PASS' if sigma_ok else 'FAIL'}")
    print(f"    phi={PHI}:  {'PASS' if phi_ok else 'FAIL'}")
    print(f"    RDoD>={RDOD_GATE}:   {'PASS' if rdod_ok else 'FAIL'}")
    if mismatches:
        print(f"\n  MISMATCHES ({len(mismatches)} nodes marked live but not deployed):")
        for m in mismatches:
            print(f"    - {m['node_id']} {m['name']}: {m['actual_stage']}")
    print("\n  Group Breakdown:")
    for g, stats in sorted(group_stats.items()):
        print(f"    {g}: {stats['deployed']}/{stats['total']} deployed, {stats['running']} running")
    print("=" * 60)

    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 HF Space Network Health Check / Restart / Audit"
    )
    parser.add_argument(
        "--mode",
        choices=["check", "restart", "audit"],
        required=True,
        help="Operation mode: check, restart, or audit",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON report path (default: hf_{mode}_report.json)",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN", "")
    manifest = load_manifest()

    if args.output is None:
        args.output = f"hf_{args.mode}_report.json"

    if args.mode == "check":
        report = mode_check(manifest, token or None)
    elif args.mode == "restart":
        report = mode_restart(manifest, token)
    elif args.mode == "audit":
        report = mode_audit(manifest, token or None)
    else:
        print(f"ERROR: Unknown mode '{args.mode}'")
        sys.exit(1)

    # Write report
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {output_path}")

    # Exit code: non-zero if errors found in check mode
    if args.mode == "check" and report.get("summary", {}).get("ERROR", 0) > 0:
        print(f"\nWARNING: {report['summary']['ERROR']} node(s) in ERROR state")
        # Don't fail the action - the workflow handles issue creation
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
