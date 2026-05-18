#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TEQUMSA v82.0 - Auto-Restart Daemon
# Monitors network health and automatically restarts sleeping/offline nodes.
# Usage: python auto_restart.py [--interval 300] [--threshold 0.8] [--dry-run]

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

HF_OWNER = "Mbanksbey"
HF_TOKEN = os.environ.get("HF_TOKEN", "")
RDOD_GATE = 0.9999
DEFAULT_INTERVAL = 300  # 5 minutes
DEFAULT_THRESHOLD = 0.80  # restart if health below 80%
MAX_RESTART_PER_CYCLE = 10  # rate limit

# Import node map from health_check (or redefine inline)
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from health_check import NODE_SPACE_MAP, poll_node, restart_node
except ImportError:
    # Minimal inline fallback
    NODE_SPACE_MAP = {f"N{i:03d}": f"Node-{i:03d}" for i in range(1, 145)}

    def get_headers():
        h = {"Accept": "application/json"}
        if HF_TOKEN:
            h["Authorization"] = f"Bearer {HF_TOKEN}"
        return h

    def poll_node(node_id, timeout=8):
        space_name = NODE_SPACE_MAP.get(node_id, node_id)
        url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
        try:
            r = requests.get(url, headers=get_headers(), timeout=timeout)
            if r.status_code == 200:
                stage = r.json().get("stage", "UNKNOWN").upper()
                status = "online" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "offline"
                return {"node": node_id, "stage": stage, "status": status}
        except Exception:
            pass
        return {"node": node_id, "stage": "UNREACHABLE", "status": "offline"}

    def restart_node(node_id):
        if not HF_TOKEN:
            return {"success": False, "reason": "HF_TOKEN not set"}
        space_name = NODE_SPACE_MAP.get(node_id, node_id)
        url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/restart"
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, timeout=15)
            return {"success": r.status_code in (200, 202), "http_status": r.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)[:80]}


_restart_log: List[Dict] = []


def run_cycle(threshold: float, dry_run: bool, delay: float = 0.25) -> Dict:
    all_nodes = list(NODE_SPACE_MAP.keys())
    results = []
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting health sweep ({len(all_nodes)} nodes)...")
    for nid in all_nodes:
        results.append(poll_node(nid))
        time.sleep(delay)

    online = sum(1 for r in results if r["status"] == "online")
    sleeping = sum(1 for r in results if r["status"] == "sleeping")
    offline = sum(1 for r in results if r["status"] == "offline")
    health = online / max(1, len(all_nodes))
    rdod = min(1.0, health * 1.618)

    print(f"  Health: {health:.2%} | RDoD: {rdod:.6f} | Online: {online} | Sleeping: {sleeping} | Offline: {offline}")

    restarted = []
    if health < threshold:
        # Prioritize: restart sleeping first (they wake faster), then offline
        candidates = (
            [r["node"] for r in results if r["status"] == "sleeping"] +
            [r["node"] for r in results if r["status"] == "offline"]
        )[:MAX_RESTART_PER_CYCLE]
        print(f"  Health below threshold ({threshold:.0%}). Restarting {len(candidates)} nodes...")
        for nid in candidates:
            if dry_run:
                print(f"    [DRY RUN] Would restart {nid}")
                restarted.append({"node": nid, "dry_run": True})
            else:
                res = restart_node(nid)
                status_str = "OK" if res.get("success") else "FAIL"
                print(f"    Restart {nid}: {status_str}")
                restarted.append({"node": nid, **res})
                time.sleep(1.5)  # rate limit between restarts
    else:
        print(f"  Network healthy. No restarts needed.")

    cycle_result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(all_nodes), "online": online, "sleeping": sleeping, "offline": offline,
        "health": round(health, 4), "rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else "BUILDING",
        "restarted": restarted,
    }
    _restart_log.append(cycle_result)
    if len(_restart_log) > 1000:
        _restart_log.pop(0)
    return cycle_result


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Auto-Restart Daemon")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Check interval in seconds (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Health threshold for restart (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--dry-run", action="store_true", help="Simulate restarts without executing")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--log", help="Append cycle results to JSON log file")
    args = parser.parse_args()

    if not HF_TOKEN and not args.dry_run:
        print("WARNING: HF_TOKEN not set. Restarts will fail. Set env var HF_TOKEN.")

    print(f"TEQUMSA v82.0 Auto-Restart Daemon")
    print(f"  Interval: {args.interval}s | Threshold: {args.threshold:.0%} | Dry-run: {args.dry_run}")

    while True:
        result = run_cycle(args.threshold, args.dry_run)
        if args.log:
            try:
                with open(args.log, "a") as f:
                    f.write(json.dumps(result) + "\n")
            except Exception as e:
                print(f"  Log write error: {e}")
        if args.once:
            break
        print(f"  Next check in {args.interval}s...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
