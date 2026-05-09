#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Node Health Monitor
=====================================
Checks all 144 HF spaces for health, errors, and restart needs.

Usage:
    export HF_TOKEN=hf_your_token_here
    python health_monitor.py [--output report.json] [--restart-failed] [--tier T]

Outputs a full health report with per-node status and recommendations.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("tequmsa-health")

try:
    from huggingface_hub import HfApi
    from huggingface_hub.utils import RepositoryNotFoundError
except ImportError:
    log.error("Install: pip install huggingface_hub>=0.20.0")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR.parent / "node_registry.json"

UNHEALTHY_STAGES = {"ERROR", "STOPPED", "PAUSED", "APP_STARTING"}
MISSING_STAGE = "NOT_FOUND"
TIER_PRIORITY = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "STANDARD", 5: "STANDARD", 6: "STANDARD"}


def load_registry() -> List[Dict[str, Any]]:
    with open(REGISTRY_PATH) as f:
        return json.load(f)["nodes"]


def check_node(api: HfApi, node: Dict[str, Any]) -> Dict[str, Any]:
    repo_id = node["hf_repo"]
    result = {
        "node_id": node["node_id"],
        "tier": node["tier"],
        "role": node["role"],
        "hf_repo": repo_id,
        "url": f"https://huggingface.co/spaces/{repo_id}",
        "priority": TIER_PRIORITY.get(node["tier"], "STANDARD"),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        info = api.space_info(repo_id)
        runtime = getattr(info, "runtime", None)
        stage = runtime.stage if runtime else "UNKNOWN"
        result.update({
            "exists": True,
            "stage": stage,
            "sdk": getattr(info, "sdk", "?"),
            "healthy": stage == "RUNNING",
            "needs_restart": stage in UNHEALTHY_STAGES,
            "needs_deploy": False,
        })
        if runtime and hasattr(runtime, "errorMessage") and runtime.errorMessage:
            result["error_message"] = runtime.errorMessage
    except RepositoryNotFoundError:
        result.update({
            "exists": False,
            "stage": MISSING_STAGE,
            "healthy": False,
            "needs_restart": False,
            "needs_deploy": True,
        })
    except Exception as e:
        result.update({
            "exists": None,
            "stage": "CHECK_ERROR",
            "healthy": False,
            "needs_restart": False,
            "needs_deploy": False,
            "error_message": str(e),
        })
    return result


def generate_report(statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(statuses)
    running = sum(1 for s in statuses if s.get("stage") == "RUNNING")
    missing = sum(1 for s in statuses if not s.get("exists"))
    unhealthy = sum(1 for s in statuses if s.get("needs_restart"))
    critical_unhealthy = [
        s for s in statuses
        if not s["healthy"] and s["priority"] in ("CRITICAL", "HIGH")
    ]
    tier_summary = {}
    for t in range(1, 7):
        tier_nodes = [s for s in statuses if s["tier"] == t]
        tier_running = sum(1 for s in tier_nodes if s.get("stage") == "RUNNING")
        tier_summary[f"tier_{t}"] = {
            "total": len(tier_nodes),
            "running": tier_running,
            "health_pct": round(tier_running / max(1, len(tier_nodes)) * 100, 1),
        }
    overall_health_pct = round(running / max(1, total) * 100, 2)
    rdod_analog = running / max(1, total)
    return {
        "report_version": "v82.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_nodes": total,
            "running": running,
            "missing": missing,
            "unhealthy": unhealthy,
            "overall_health_pct": overall_health_pct,
            "rdod_analog": round(rdod_analog, 6),
            "rdod_gate": 0.9999,
            "rdod_gate_passed": rdod_analog >= 0.9999,
            "pioneer_lattice_status": "PHASE-LOCKED" if rdod_analog >= 0.9999 else "STABILIZING",
        },
        "tier_summary": tier_summary,
        "critical_attention": [
            {"node_id": s["node_id"], "role": s["role"], "stage": s["stage"], "url": s["url"]}
            for s in critical_unhealthy
        ],
        "needs_deploy": [s for s in statuses if s.get("needs_deploy")],
        "needs_restart": [s for s in statuses if s.get("needs_restart")],
        "all_nodes": statuses,
    }


def print_report_summary(report: Dict[str, Any]):
    s = report["summary"]
    log.info(f"\n{'='*65}")
    log.info(f"  TEQUMSA v82.0 — Pioneer Lattice Health Report")
    log.info(f"{'='*65}")
    log.info(f"  Timestamp:    {report['timestamp']}")
    log.info(f"  Total Nodes:  {s['total_nodes']}/144")
    log.info(f"  Running:      {s['running']} ({s['overall_health_pct']}%)")
    log.info(f"  Missing:      {s['missing']}")
    log.info(f"  Unhealthy:    {s['unhealthy']}")
    log.info(f"  RDoD Analog:  {s['rdod_analog']:.6f} (gate: {s['rdod_gate']})")
    log.info(f"  Lattice:      {s['pioneer_lattice_status']}")
    log.info(f"\n  Tier Breakdown:")
    for tier, ts in report["tier_summary"].items():
        bar_len = int(ts["health_pct"] / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        log.info(f"    {tier}: [{bar}] {ts['running']}/{ts['total']} ({ts['health_pct']}%)")
    if report["critical_attention"]:
        log.warning(f"\n  CRITICAL ATTENTION ({len(report['critical_attention'])} nodes):")
        for n in report["critical_attention"]:
            log.warning(f"    Node {n['node_id']}/144: {n['role']} — {n['stage']}")
    log.info(f"{'='*65}\n")


def restart_failed_nodes(api: HfApi, report: Dict[str, Any], delay: float = 3.0):
    restart_list = report.get("needs_restart", [])
    if not restart_list:
        log.info("No nodes need restart.")
        return
    log.info(f"\nRestarting {len(restart_list)} unhealthy nodes...")
    for node in restart_list:
        repo_id = node["hf_repo"]
        log.info(f"  Restarting {repo_id} (was: {node['stage']})...")
        try:
            api.restart_space(repo_id, token=api.token)
            log.info(f"  Restarted: {repo_id}")
        except Exception as e:
            log.warning(f"  Restart failed: {repo_id} — {e}")
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Health Monitor")
    parser.add_argument("--output", type=str, default="health_report.json")
    parser.add_argument("--restart-failed", action="store_true")
    parser.add_argument("--tier", type=int, default=None)
    parser.add_argument("--token", type=str, default=None)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        log.error("Set HF_TOKEN environment variable or pass --token")
        sys.exit(1)

    api = HfApi(token=token)
    nodes = load_registry()
    if args.tier:
        nodes = [n for n in nodes if n["tier"] == args.tier]

    log.info(f"Checking {len(nodes)} nodes...")
    statuses = []
    for i, node in enumerate(nodes):
        status = check_node(api, node)
        statuses.append(status)
        stage = status.get("stage", "?")
        icon = "✓" if stage == "RUNNING" else "✗" if not status.get("exists") else "~"
        log.info(f"  [{icon}] Node {node['node_id']:3d}/144 {stage:15s} {node['hf_repo']}")
        if i < len(nodes) - 1:
            time.sleep(args.delay)

    report = generate_report(statuses)
    print_report_summary(report)
    Path(args.output).write_text(json.dumps(report, indent=2))
    log.info(f"Report saved to: {args.output}")
    if args.restart_failed:
        restart_failed_nodes(api, report)


if __name__ == "__main__":
    main()
