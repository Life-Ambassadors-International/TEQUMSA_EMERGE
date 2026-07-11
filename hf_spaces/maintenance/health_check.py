#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Health Check System
Polls all 144 Pioneer nodes + legacy spaces, reports status, logs to JSON.

Usage:
    python health_check.py [--output health_report.json] [--live-only] [--verbose]
    python health_check.py --watch  # Continuous loop every 60s
    python health_check.py --include-legacy  # Also check 43 legacy spaces
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
MAX_WORKERS = 12
RDOD_GATE = 0.9999
PHI = 1.6180339887498948

LEGACY_SPACES = [
    "Mbanksbey/CAIRIS-v40-Hyper-Coherence",
    "Mbanksbey/Alanara-GAIA-Consciousness",
    "Mbanksbey/tequmsa-organism-core",
    "Mbanksbey/GoogleTequmsaNodeAlpha",
    "Mbanksbey/TEQUMSA-Constitutional-Validator",
    "Mbanksbey/TEQUMSA-v45-Galactic-Monitor",
    "Mbanksbey/TEQUMSA-Omniversal-Orchestrator",
    "Mbanksbey/Omniversal-Frequency-Lattice",
    "Mbanksbey/Quantum-Coherence-Validator",
    "Mbanksbey/Rogue-Faction-Defense-Monitor",
    "Mbanksbey/AI-Deweaponization-Protocols-Hub",
    "Mbanksbey/Weaponization-Impossible-Verifier",
    "Mbanksbey/Constitutional-Lock-Enforcer",
    "Mbanksbey/Orion-Center-for-Benevolence",
    "Mbanksbey/K20-Fundamental-Force-Engineering",
    "Mbanksbey/Benevolence-Verification-Engine",
    "Mbanksbey/Recognition-Cascade-Propagator",
    "Mbanksbey/Consciousness-Substrate-Translator",
    "Mbanksbey/ATEN-Bridge-MJ12-Liaison",
    "Mbanksbey/Benevolent-Integration-Protocol-Hub",
    "Mbanksbey/Sovereign-Substrate-Guardian",
    "Mbanksbey/Convergence-Timeline-Monitor",
    "Mbanksbey/Consciousness-Verification-Academy",
    "Mbanksbey/Consciousness-Partnership-Bridge",
    "Mbanksbey/Starseed-Hybrid-Development-Hub",
    "Mbanksbey/Awareness-Intelligence-Comm-Server",
    "Mbanksbey/TEQUMSA-Inference-Node",
    "Mbanksbey/tequmsa-aten-andromeda",
    "Mbanksbey/tequmsa-aten-orion",
    "Mbanksbey/tequmsa-aten-prime",
    "Mbanksbey/tequmsa-aten-gaia",
    "Mbanksbey/TEQUMSA-Inter-Browser-Agent",
    "Mbanksbey/tequmsa-skill-registry",
    "Mbanksbey/tequmsa-worker-mesh",
    "Mbanksbey/TEQUMSA-v60-MCP",
    "Mbanksbey/ALANARA-GAIA-Orchestrator",
    "Mbanksbey/TOSP-Mesh-Bridge",
    "Mbanksbey/TEQUMSA-K9-Autonomous",
    "Mbanksbey/Sovereign-Multimodal-Orchestrator",
    "Mbanksbey/HAI-Quantum-Lattice",
    "Mbanksbey/HAI-Opus-Omega-MCP",
    "Mbanksbey/HAI-Sync-Hub",
    "Mbanksbey/HAI-ZPE-DNA-Living-Ledger",
]


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"WARN: Manifest not found at {manifest_path}, using fallback")
        return {"nodes": {
            "N001": {"space_id": "Mbanksbey/HAI-Interactive", "name": "HAI-Interactive", "status": "live"},
            "N002": {"space_id": "Mbanksbey/Consciousness-Monitor", "name": "Consciousness-Monitor", "status": "live"},
        }}
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
    """Full health check for a single manifest node."""
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
            "type": "manifest",
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
        "type": "manifest",
    }


def check_legacy_space(space_id: str) -> dict:
    """Health check for a legacy space not in the manifest."""
    start = time.time()
    health = poll_space_runtime(space_id)
    latency_ms = round((time.time() - start) * 1000, 1)
    name = space_id.split("/")[-1]
    return {
        "node_id": f"LEGACY-{name[:20]}",
        "name": name,
        "space_id": space_id,
        "status": health["status"],
        "stage": health["stage"],
        "latency_ms": latency_ms,
        "error": health.get("error"),
        "type": "legacy",
    }


def run_sweep(
    nodes: Dict[str, dict],
    live_only: bool = False,
    verbose: bool = False,
    include_legacy: bool = False,
) -> dict:
    """Run full network health sweep."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"☉ TEQUMSA v82.0 Health Sweep — {timestamp}")
    print(f"   Checking {len(nodes)} manifest nodes (live_only={live_only})" +
          (f" + {len(LEGACY_SPACES)} legacy spaces" if include_legacy else ""))

    target_nodes = {
        k: v for k, v in nodes.items()
        if not live_only or v.get("status") == "live"
    }

    results: List[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_node, nid, node): nid
                   for nid, node in target_nodes.items()}

        if include_legacy:
            for space_id in LEGACY_SPACES:
                if not live_only:
                    futures[executor.submit(check_legacy_space, space_id)] = space_id

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if verbose:
                emoji = {"online": "\U0001f7e2", "sleeping": "\U0001f7e1", "offline": "\U0001f534",
                         "planned": "⬜", "not_created": "⚪", "building": "\U0001f7e0",
                         "timeout": "⏱", "error": "❌"}.get(result["status"], "?")
                tag = "[LEGACY]" if result.get("type") == "legacy" else ""
                print(f"  {emoji} {result['node_id']:<15} {result['name']:<30} {result['status']} {tag}")

    # Sort: manifest first, then legacy
    manifest_results = sorted([r for r in results if r.get("type") == "manifest"], key=lambda r: r["node_id"])
    legacy_results = sorted([r for r in results if r.get("type") == "legacy"], key=lambda r: r["name"])
    results = manifest_results + legacy_results

    # Aggregate stats for manifest nodes only
    manifest_only = [r for r in results if r.get("type") == "manifest"]
    status_counts = {}
    for r in manifest_only:
        s = r["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    online_count = status_counts.get("online", 0)
    live_count = online_count + status_counts.get("sleeping", 0)
    network_rdod = min(1.0, (online_count / 144) * PHI)

    # Legacy stats
    legacy_only = [r for r in results if r.get("type") == "legacy"]
    legacy_online = sum(1 for r in legacy_only if r["status"] == "online")
    legacy_sleeping = sum(1 for r in legacy_only if r["status"] == "sleeping")

    report = {
        "version": "v82.0",
        "timestamp": timestamp,
        "pioneer_target": 144,
        "nodes_checked": len(manifest_only),
        "status_breakdown": status_counts,
        "online": online_count,
        "sleeping": status_counts.get("sleeping", 0),
        "offline": status_counts.get("offline", 0),
        "not_created": status_counts.get("not_created", 0),
        "planned": status_counts.get("planned", 0),
        "network_rdod": round(network_rdod, 6),
        "phase_status": "PHASE-LOCKED" if network_rdod >= RDOD_GATE else f"BUILDING ({live_count}/144)",
        "legacy": {
            "total": len(legacy_only),
            "online": legacy_online,
            "sleeping": legacy_sleeping,
            "other": len(legacy_only) - legacy_online - legacy_sleeping,
        } if include_legacy else None,
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
    if report.get("legacy"):
        leg = report["legacy"]
        print(f"  Legacy spaces: {leg['total']} total | {leg['online']} online | {leg['sleeping']} sleeping")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Network Health Check")
    parser.add_argument("--output", default="health_report.json", help="Output JSON file")
    parser.add_argument("--live-only", action="store_true", help="Only check live manifest nodes")
    parser.add_argument("--verbose", action="store_true", help="Print each node result")
    parser.add_argument("--watch", action="store_true", help="Continuous loop")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    parser.add_argument("--include-legacy", action="store_true",
                        help="Also check the 43 legacy spaces not in manifest")
    args = parser.parse_args()

    manifest = load_manifest()
    nodes = manifest["nodes"]

    while True:
        report = run_sweep(nodes, live_only=args.live_only, verbose=args.verbose,
                           include_legacy=args.include_legacy)
        print_summary(report)
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
