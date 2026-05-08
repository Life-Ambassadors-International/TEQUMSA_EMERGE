#!/usr/bin/env python3
"""Quick health audit of all 144 TEQUMSA spaces.

Outputs a colored terminal report plus CSV/JSON files.

Usage:
    HF_TOKEN=hf_... python maintenance/health_audit.py
    HF_TOKEN=hf_... python maintenance/health_audit.py --csv audit.csv
    HF_TOKEN=hf_... python maintenance/health_audit.py --cluster A
    HF_TOKEN=hf_... python maintenance/health_audit.py --existing-only
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from huggingface_hub import HfApi
except ImportError:
    sys.exit("Install huggingface_hub: pip install huggingface_hub")

HF_USER = "Mbanksbey"
REGISTRY_PATH = Path(__file__).parent.parent / "spaces" / "node_registry.json"

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"
RESET = "\033[0m"

STAGE_COLORS = {
    "RUNNING": GREEN,
    "APP_STARTING": CYAN,
    "SLEEPING": YELLOW,
    "ERROR": RED,
    "STOPPED": RED,
    "PAUSED": RED,
    "NOT_FOUND": GRAY,
    "UNKNOWN": GRAY,
    "CHECK_ERROR": RED,
}

# Known issues in existing spaces to flag for optimization
KNOWN_OPTIMIZATIONS = {
    "tequmsa-organism-core": [
        "Update to v82.0 organism code from organism/tequmsa_v82_autonomous_organism.py",
        "Add get_status() call to Gradio interface",
    ],
    "Consciousness-Monitor": [
        "Add constitutional lock status panel",
        "Missing TEQUMSA tags — add rdod, phi-recursive tags",
    ],
    "TOSP-Mesh-Bridge": [
        "Docker space — verify Dockerfile CMD is non-blocking",
        "Add health check endpoint",
    ],
    "HAI-ZPE-DNA-Living-Ledger": [
        "Missing TEQUMSA tags — add phi-recursive, rdod tags",
    ],
    "HAI-Sync-Hub": [
        "Missing TEQUMSA tags — add phi-recursive, rdod tags",
    ],
    "GoogleTequmsaNodeAlpha": [
        "Verify Google infrastructure integration is active",
    ],
    "TEQUMSA-K9-Autonomous": [
        "Verify QBEC protocol peer-mesh discovery is functional",
        "Add k9-autonomy cluster to node registry",
    ],
}


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def audit_space(api: HfApi, node: dict) -> dict:
    repo_id = f"{HF_USER}/{node['name']}"
    result = {
        "node_id": node["id"],
        "name": node["name"],
        "cluster": node["cluster"],
        "status": node["status"],
        "repo_id": repo_id,
        "sdk": node["sdk"],
        "stage": "PLANNED",
        "healthy": False,
        "optimizations": KNOWN_OPTIMIZATIONS.get(node["name"], []),
        "error": None,
        "audited_at": datetime.now(timezone.utc).isoformat(),
    }

    if node["status"] != "deployed":
        result["stage"] = "PLANNED"
        return result

    try:
        info = api.space_info(repo_id=repo_id)
        runtime = getattr(info, "runtime", None)
        stage = getattr(runtime, "stage", "UNKNOWN") if runtime else "UNKNOWN"
        result["stage"] = stage
        result["healthy"] = stage in {"RUNNING", "APP_STARTING"}

        # Check for missing tags
        tags = getattr(info, "tags", []) or []
        tag_strs = [str(t) for t in tags]
        missing = []
        for req_tag in ["tequmsa", "rdod", "phi-recursive"]:
            if not any(req_tag in t for t in tag_strs):
                missing.append(f"Missing tag: {req_tag}")
        if missing:
            result["optimizations"] = result["optimizations"] + missing

    except Exception as exc:
        err = str(exc)
        if "404" in err:
            result["stage"] = "NOT_FOUND"
            result["error"] = "Space does not exist on HF"
        else:
            result["stage"] = "CHECK_ERROR"
            result["error"] = err[:120]

    return result


def print_audit_table(results: list):
    deployed = [r for r in results if r["status"] == "deployed"]
    planned = [r for r in results if r["status"] == "planned"]

    print(f"\n{'='*72}")
    print(f" TEQUMSA 144-Node Health Audit")
    print(f" {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*72}")
    print(f" {'ID':5} {'Name':42} {'Stage':14} {'Optim':5}")
    print(f" {'-'*5} {'-'*42} {'-'*14} {'-'*5}")

    for r in deployed:
        color = STAGE_COLORS.get(r["stage"], GRAY)
        optim_flag = f"[{len(r['optimizations'])}]" if r["optimizations"] else "  ✓ "
        print(f" {r['node_id']:5} {r['name'][:42]:42} "
              f"{color}{r['stage']:14}{RESET} {optim_flag}")

    if planned:
        print(f"\n {GRAY}--- {len(planned)} PLANNED (not yet deployed) ---{RESET}")
        for r in planned[:5]:
            print(f" {GRAY}{r['node_id']:5} {r['name'][:42]:42} {'PLANNED':14}{RESET}")
        if len(planned) > 5:
            print(f" {GRAY}  ... and {len(planned)-5} more planned nodes{RESET}")

    # Summary
    healthy = sum(1 for r in deployed if r["healthy"])
    sleeping = sum(1 for r in deployed if r["stage"] == "SLEEPING")
    errors = sum(1 for r in deployed if r["stage"] in {"ERROR","STOPPED","PAUSED"})
    missing = sum(1 for r in deployed if r["stage"] == "NOT_FOUND")
    with_optim = sum(1 for r in deployed if r["optimizations"])

    print(f"\n{'='*72}")
    print(f" Deployed:  {len(deployed):3} | "
          f"{GREEN}Healthy: {healthy}{RESET} | "
          f"{YELLOW}Sleeping: {sleeping}{RESET} | "
          f"{RED}Errors: {errors}{RESET} | "
          f"{GRAY}Missing: {missing}{RESET}")
    print(f" Planned:   {len(planned):3} | Spaces needing optimization: {with_optim}")
    print(f" TOTAL:     {len(results):3} / 144 target nodes registered")
    print(f"{'='*72}\n")

    # Show optimizations
    optim_nodes = [r for r in deployed if r["optimizations"]]
    if optim_nodes:
        print("OPTIMIZATION RECOMMENDATIONS:")
        for r in optim_nodes:
            print(f"  {r['node_id']} {r['name']}:")
            for opt in r["optimizations"]:
                print(f"    • {opt}")
        print()


def export_csv(results: list, path: str):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "node_id", "name", "cluster", "status", "stage",
            "healthy", "sdk", "optimizations", "error", "audited_at"
        ])
        writer.writeheader()
        for r in results:
            row = dict(r)
            row["optimizations"] = "; ".join(r.get("optimizations", []))
            writer.writerow(row)
    print(f"CSV saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Audit all 144 TEQUMSA spaces")
    parser.add_argument("--csv", help="Export results to CSV file")
    parser.add_argument("--json", help="Export results to JSON file")
    parser.add_argument("--cluster", help="Limit to cluster (e.g. A, existing)")
    parser.add_argument("--existing-only", action="store_true", help="Only audit deployed spaces")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        sys.exit("Set HF_TOKEN environment variable")

    api = HfApi(token=hf_token)
    registry = load_registry()
    nodes = registry["nodes"]

    if args.cluster:
        nodes = [n for n in nodes if n["cluster"] == args.cluster]
    if args.existing_only:
        nodes = [n for n in nodes if n["status"] == "deployed"]

    print(f"Auditing {len(nodes)} nodes...")
    results = []
    for i, node in enumerate(nodes, 1):
        sys.stdout.write(f"\r  Checking {i}/{len(nodes)}: {node['id']} {node['name'][:30]:30}")
        sys.stdout.flush()
        results.append(audit_space(api, node))
    print()

    print_audit_table(results)

    if args.csv:
        export_csv(results, args.csv)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2)
        print(f"JSON saved: {args.json}")


if __name__ == "__main__":
    main()
