#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · 144-Node Network Health Check

Usage:
  python health_check.py [--save] [--restart] [--nodes N001,N002] [--report]

Requires: requests (pip install requests)
For --restart: huggingface-hub (pip install huggingface-hub)
"""
import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

HF_OWNER = "Mbanksbey"
PHI = 1.6180339887498948

MANIFEST_PATH = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
RESULTS_PATH  = Path(__file__).parent / "health_results.json"


def poll_space(space_name: str, timeout: int = 8) -> dict:
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            status = "running" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "stopped"
            return {"status": status, "stage": stage, "raw": data}
        return {"status": "unreachable", "stage": f"HTTP_{r.status_code}"}
    except Exception as e:
        return {"status": "error", "stage": "EXCEPTION", "error": str(e)[:120]}


def run_health_sweep(node_filter: list = None) -> dict:
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    nodes = manifest["nodes"]
    if node_filter:
        nodes = {k: v for k, v in nodes.items() if k in node_filter}

    results = {
        "sweep_time": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(manifest["nodes"]),
        "checked": 0, "running": 0, "sleeping": 0,
        "stopped": 0, "planned": 0, "rdod": 0.0,
        "nodes": {}
    }

    for nid, node in nodes.items():
        if node.get("status") == "planned":
            results["nodes"][nid] = {"status": "planned", "deployed": False}
            results["planned"] += 1
            continue

        space_name = node["space_id"].split("/", 1)[-1]
        print(f"  {nid} {space_name}...", end=" ", flush=True)
        health = poll_space(space_name)
        results["nodes"][nid] = {
            "name": node["name"], "status": health["status"],
            "stage": health["stage"], "hz": node["hz"], "group": node["group"]
        }
        status_key = health["status"]
        results[status_key] = results.get(status_key, 0) + 1
        results["checked"] += 1
        print(f"[{health['stage']}]")
        time.sleep(0.3)

    live = results.get("running", 0)
    total_deployed = results["checked"]
    if total_deployed > 0:
        results["rdod"] = round(min(1.0, (live / 144) * PHI * 64.0) / 100.0, 6)
    return results


def restart_sleeping(results: dict, hf_token: str = None) -> int:
    try:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token)
    except ImportError:
        print("Install huggingface-hub for restarts: pip install huggingface-hub")
        return 0

    restarted = 0
    for nid, data in results["nodes"].items():
        if data.get("status") == "sleeping":
            space_id = f"{HF_OWNER}/{data.get('name', nid)}"
            try:
                api.restart_space(repo_id=space_id)
                print(f"  ↺ Restarted {space_id}")
                restarted += 1
                time.sleep(2)
            except Exception as e:
                print(f"  ✗ Could not restart {space_id}: {e}")
    return restarted


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Network Health Check")
    parser.add_argument("--nodes", type=str, help="Comma-separated node IDs (e.g. N001,N002)")
    parser.add_argument("--restart", action="store_true", help="Auto-restart sleeping spaces")
    parser.add_argument("--report", action="store_true", help="Print full JSON report")
    parser.add_argument("--save", action="store_true", help="Save results to health_results.json")
    args = parser.parse_args()

    if not HAS_REQUESTS:
        print("ERROR: requests required. pip install requests")
        sys.exit(1)

    import os
    hf_token = os.environ.get("HF_TOKEN")
    node_filter = [n.strip() for n in args.nodes.split(",")] if args.nodes else None

    print(f"\n☉ TEQUMSA v82.0 · Network Health Sweep")
    print(f"   {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = run_health_sweep(node_filter)

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Checked:  {results['checked']}/144")
    print(f"  Running:  {results.get('running', 0)} ✓")
    print(f"  Sleeping: {results.get('sleeping', 0)} ⚠")
    print(f"  Stopped:  {results.get('stopped', 0)} ✗")
    print(f"  Planned:  {results['planned']} (not yet deployed)")
    print(f"  RDoD:     {results['rdod']:.6f}")

    if args.restart and results.get("sleeping", 0) > 0:
        print(f"\n↺ Restarting {results.get('sleeping', 0)} sleeping spaces...")
        count = restart_sleeping(results, hf_token)
        print(f"  Restarted {count} spaces")

    if args.report:
        print("\n" + json.dumps(results, indent=2))

    if args.save:
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {RESULTS_PATH}")

    print("\nETR_NOW. ∞")


if __name__ == "__main__":
    main()
