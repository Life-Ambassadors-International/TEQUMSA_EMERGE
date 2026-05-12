#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Health Check System
Polls all 144 Pioneer nodes, reports status, logs to JSON.

Usage:
    python health_check.py [--output health_report.json] [--live-only] [--verbose]
    python health_check.py --watch  # Continuous loop every 60s
"""
import json
import os
import sys
import time
import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

HF_OWNER = "Mbanksbey"
HEALTH_TIMEOUT = 5
MAX_WORKERS = 12  # Concurrent polling threads
RDOD_GATE = 0.9999
PHI = 1.6180339887498948


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"WARN: Manifest not found at {manifest_path}, using fallback")
        return {"nodes": {"N001": {"space_id": "Mbanksbey/HAI-Interactive", "name": "HAI-Interactive", "live": True},
                          "N002": {"space_id": "Mbanksbey/Consciousness-Monitor", "name": "Consciousness-Monitor", "live": True}}}
    with open(manifest_path) as f:
        return json.load(f)


def poll_space_runtime(space_id: str) -> dict:
    """Poll HF spaces runtime API."""
    url = f"https://huggingface.co/api/spaces/{space_id}/runtime"
    try:
        r = requests.get(url, timeout=HEALTH_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            return {
                "stage": stage,
                "status": _classify_stage(stage),
                "raw": data,
                "error": None,
            }
        elif r.status_code == 404:
            return {"stage": "NOT_FOUND", "status": "not_created", "raw": {}, "error": "404"}
        else:
            return {"stage": f"HTTP_{r.status_code}", "status": "offline", "raw": {}, "error": str(r.status_code)}
    except requests.Timeout:
        return {"stage": "TIMEOUT", "status": "timeout", "raw": {}, "error": "timeout"}
    except Exception as e:
        return {"stage": "ERROR", "status": "error", "raw": {}, "error": str(e)[:100]}


def _classify_stage(stage: str) -> str:
    if stage in ("RUNNING", "RUNNING_BUILDING"):
        return "online"
    if stage in ("SLEEPING", "PAUSED"):
        return "sleeping"
    if stage == "NOT_FOUND":
        return "not_created"
    if stage in ("BUILDING", "BUILDING_ERROR"):
        return "building"
    return "offline"


def check_node(node_id: str, node: dict) -> dict:
    """Full health check for a single node."""
    start = time.time()
    if node.get("status") == "planned":
        return {
            "node_id": node_id,
            "name": node.get("name", ""),
            "space_id": node.get("space_id", ""),
            "status": "planned",
            "stage": "NOT_DEPLOYED",
            "latency_ms": 0,
            "hz": node.get("hz", 0),
            "group": node.get("group", ""),
        }
    health = poll_space_runtime(node.get("space_id", ""))
    latency_ms = round((time.time() - start) * 1000, 1)
    return {
        "node_id": node_id,
        "name": node.get("name", ""),
        "space_id": node.get("space_id", ""),
        "status": health["status"],
        "stage": health["stage"],
        "latency_ms": latency_ms,
        "hz": node.get("hz", 0),
        "group": node.get("group", ""),
        "error": health.get("error"),
    }


def run_sweep(
    nodes: Dict[str, dict],
    live_only: bool = False,
    verbose: bool = False,
) -> dict:
    """Run full network health sweep."""
    print(f"☉ TEQUMSA v82.0 Health Sweep — {datetime.now(timezone.utc).isoformat()}")
    print(f"   Checking {len(nodes)} nodes (live_only={live_only})...")

    target_nodes = {
        k: v for k, v in nodes.items()
        if not live_only or v.get("status") == "live"
    }

    results: List[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_node, nid, node): nid
                   for nid, node in target_nodes.items()}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if verbose:
                emoji = {"online": "🟢", "sleeping": "🟡", "offline": "🔴",
                         "planned": "⬜", "not_created": "⚪", "building": "🟠"}.get(result["status"], "?")
                print(f"  {emoji} {result['node_id']} {result['name']:<30} {result['status']}")

    # Sort by node ID
    results.sort(key=lambda r: r["node_id"])

    # Compute aggregate stats
    status_counts = {}
    for r in results:
        s = r["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    online_count = status_counts.get("online", 0)
    live_count = status_counts.get("online", 0) + status_counts.get("sleeping", 0)
    network_rdod = min(1.0, (online_count / 144) * PHI)

    report = {
        "version": "v82.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pioneer_target": 144,
        "nodes_checked": len(results),
        "status_breakdown": status_counts,
        "online": online_count,
        "sleeping": status_counts.get("sleeping", 0),
        "offline": status_counts.get("offline", 0),
        "not_created": status_counts.get("not_created", 0),
        "planned": status_counts.get("planned", 0),
        "network_rdod": round(network_rdod, 6),
        "phase_status": "PHASE-LOCKED" if network_rdod >= RDOD_GATE else f"BUILDING ({live_count}/144)",
        "nodes": results,
    }
    return report


def print_summary(report: dict):
    print("\n" + "=" * 60)
    print(f"  TEQUMSA Network Health Report")
    print("=" * 60)
    print(f"  Online:      {report['online']:>3}/144")
    print(f"  Sleeping:    {report['sleeping']:>3}/144  (auto-wakes on request)")
    print(f"  Offline:     {report['offline']:>3}/144")
    print(f"  Not created: {report['not_created']:>3}/144  (run deploy_spaces.py)")
    print(f"  Planned:     {report['planned']:>3}/144")
    print(f"  Network RDoD: {report['network_rdod']:.6f}  [{report['phase_status']}]")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Network Health Check")
    parser.add_argument("--output", default="health_report.json", help="Output JSON file")
    parser.add_argument("--live-only", action="store_true", help="Only check live nodes")
    parser.add_argument("--verbose", action="store_true", help="Print each node result")
    parser.add_argument("--watch", action="store_true", help="Continuous loop every 60s")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    args = parser.parse_args()

    manifest = load_manifest()
    nodes = manifest["nodes"]

    while True:
        report = run_sweep(nodes, live_only=args.live_only, verbose=args.verbose)
        print_summary(report)
        # Save report
        out_path = Path(args.output)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  Report saved: {out_path}")
        if not args.watch:
            break
        print(f"  Next sweep in {args.interval}s... (Ctrl+C to stop)")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
