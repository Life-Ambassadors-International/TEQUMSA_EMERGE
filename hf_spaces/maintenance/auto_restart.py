#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Auto-Restart System
Wakes sleeping spaces and restarts crashed nodes.

Usage:
    export HF_TOKEN=hf_your_token_here
    python auto_restart.py [--dry-run] [--node N001] [--group A_COMMAND]
    python auto_restart.py --watch --interval 300  # Check every 5 min

HF spaces auto-sleep after 48h of inactivity on free tier.
This script sends a ping request to wake them.
"""
import argparse
import json
import os
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

HF_OWNER = "Mbanksbey"
RESTART_LOG: List[dict] = []


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        return json.load(f)


def get_space_status(space_id: str, hf_token: str = "") -> str:
    url = f"https://huggingface.co/api/spaces/{space_id}/runtime"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    try:
        r = requests.get(url, timeout=8, headers=headers)
        if r.status_code == 200:
            return r.json().get("stage", "UNKNOWN").upper()
        return f"HTTP_{r.status_code}"
    except Exception as e:
        return f"ERROR: {e}"


def wake_space(space_id: str, hf_token: str) -> bool:
    """Wake a sleeping HF space by calling its root endpoint."""
    app_url = f"https://{space_id.replace('/', '-').lower()}.hf.space"
    try:
        r = requests.get(app_url, timeout=15, headers={"Authorization": f"Bearer {hf_token}"})
        return r.status_code < 500
    except Exception:
        # Try the HF restart API
        pass
    return False


def restart_space(space_id: str, hf_token: str) -> bool:
    """Restart a space via HF API."""
    url = f"https://huggingface.co/api/spaces/{space_id}/restart"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {hf_token}"},
            timeout=10,
        )
        return r.status_code in (200, 202)
    except Exception as e:
        print(f"    Restart API error: {e}")
        return False


def process_node(
    node_id: str,
    node: dict,
    hf_token: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    if node.get("status") != "live":
        return {"node_id": node_id, "action": "skip", "reason": "not_live"}

    space_id = node["space_id"]
    status = get_space_status(space_id, hf_token)
    
    action = "none"
    success = True

    if status in ("SLEEPING", "PAUSED"):
        action = "wake"
        if not dry_run:
            success = wake_space(space_id, hf_token)
            if verbose:
                print(f"  🟡 {node_id} {node['name']}: sleeping → {'waking' if success else 'FAILED'}")

    elif status in ("RUNTIME_ERROR", "CONFIG_ERROR", "BUILD_ERROR"):
        action = "restart"
        if not dry_run:
            success = restart_space(space_id, hf_token)
            if verbose:
                print(f"  🔴 {node_id} {node['name']}: error → {'restarting' if success else 'FAILED'}")

    elif status == "RUNNING":
        if verbose:
            print(f"  🟢 {node_id} {node['name']}: online")

    result = {
        "node_id": node_id,
        "name": node["name"],
        "space_id": space_id,
        "status_before": status,
        "action": action,
        "success": success,
        "dry_run": dry_run,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    RESTART_LOG.append(result)
    return result


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Auto-Restart")
    parser.add_argument("--dry-run", action="store_true", help="Check without restarting")
    parser.add_argument("--node", type=str, help="Single node to check (e.g. N001)")
    parser.add_argument("--group", type=str, help="Group to check (e.g. A_COMMAND)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring loop")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds")
    parser.add_argument("--output", default="restart_log.json", help="Log file path")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN environment variable")
        sys.exit(1)

    manifest = load_manifest()
    nodes = manifest["nodes"]

    # Filter
    target = {}
    for nid, node in nodes.items():
        if args.node and nid != args.node:
            continue
        if args.group and node.get("group") != args.group.split("_")[0]:
            continue
        if node.get("status") == "live":
            target[nid] = node

    print(f"☉ TEQUMSA v82.0 Auto-Restart — {len(target)} live nodes targeted")

    def run_round():
        woken = restarted = skipped = 0
        for nid, node in target.items():
            result = process_node(nid, node, hf_token, dry_run=args.dry_run, verbose=args.verbose)
            if result["action"] == "wake":
                woken += 1
            elif result["action"] == "restart":
                restarted += 1
            else:
                skipped += 1
            time.sleep(0.3)  # Rate limit
        print(f"  Woken: {woken} | Restarted: {restarted} | Online/skipped: {skipped}")
        # Save log
        with open(args.output, "w") as f:
            json.dump(RESTART_LOG[-500:], f, indent=2)

    while True:
        run_round()
        if not args.watch:
            break
        print(f"  Next check in {args.interval}s...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
