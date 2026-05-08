#!/usr/bin/env python3
"""TEQUMSA 144-Node Maintenance Planner.

Schedules periodic health checks across all 144 HF spaces and auto-restarts
spaces that fall into ERROR or SLEEPING states.

Usage:
    HF_TOKEN=hf_... python maintenance/maintenance_planner.py
    HF_TOKEN=hf_... python maintenance/maintenance_planner.py --interval 30
    HF_TOKEN=hf_... python maintenance/maintenance_planner.py --once
    HF_TOKEN=hf_... python maintenance/maintenance_planner.py --report-only
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    from huggingface_hub import HfApi
except ImportError:
    sys.exit("Install huggingface_hub: pip install huggingface_hub")

HF_USER = "Mbanksbey"
REGISTRY_PATH = Path(__file__).parent.parent / "spaces" / "node_registry.json"
REPORT_DIR = Path(__file__).parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# Space runtime stages from HF API
STAGE_RUNNING = "RUNNING"
STAGE_SLEEPING = "SLEEPING"
STAGE_BUILDING = "APP_STARTING"
STAGE_ERROR = "ERROR"
STAGE_STOPPED = "STOPPED"
STAGE_PAUSED = "PAUSED"

HEALTHY_STAGES = {STAGE_RUNNING, STAGE_BUILDING}
RESTART_STAGES = {STAGE_ERROR, STAGE_STOPPED, STAGE_PAUSED}
WAKE_STAGES = {STAGE_SLEEPING}


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def check_space(api: HfApi, repo_id: str) -> Dict[str, str]:
    """Return space health info. Handles missing spaces gracefully."""
    try:
        info = api.space_info(repo_id=repo_id)
        runtime = getattr(info, "runtime", None)
        stage = getattr(runtime, "stage", "UNKNOWN") if runtime else "UNKNOWN"
        sdk = getattr(info, "sdk", "unknown")
        return {
            "repo_id": repo_id,
            "stage": stage,
            "sdk": sdk,
            "healthy": stage in HEALTHY_STAGES,
            "needs_restart": stage in RESTART_STAGES,
            "needs_wake": stage in WAKE_STAGES,
            "error": None,
        }
    except Exception as exc:
        err_str = str(exc)
        if "404" in err_str or "not found" in err_str.lower():
            return {
                "repo_id": repo_id,
                "stage": "NOT_FOUND",
                "sdk": "unknown",
                "healthy": False,
                "needs_restart": False,
                "needs_wake": False,
                "error": "Space not deployed yet",
            }
        return {
            "repo_id": repo_id,
            "stage": "CHECK_ERROR",
            "sdk": "unknown",
            "healthy": False,
            "needs_restart": False,
            "needs_wake": False,
            "error": err_str[:120],
        }


def restart_space(api: HfApi, repo_id: str, reason: str) -> bool:
    """Attempt to restart a space. Returns True on success."""
    try:
        api.restart_space(repo_id=repo_id, factory_reboot=False)
        print(f"  [RESTART] {repo_id} — {reason}")
        return True
    except Exception as exc:
        print(f"  [RESTART-FAIL] {repo_id}: {exc}")
        return False


def run_health_check(api: HfApi, nodes: List[dict], auto_restart: bool = True) -> dict:
    """Run full health check across all provided nodes."""
    ts = datetime.now(timezone.utc).isoformat()
    results = []
    summary = {
        "timestamp": ts,
        "total": 0,
        "healthy": 0,
        "sleeping": 0,
        "error": 0,
        "not_found": 0,
        "restarted": 0,
        "unknown": 0,
    }

    deployed_nodes = [n for n in nodes if n["status"] == "deployed"]
    planned_nodes = [n for n in nodes if n["status"] == "planned"]

    print(f"\n{'='*60}")
    print(f"TEQUMSA Health Check — {ts}")
    print(f"Deployed: {len(deployed_nodes)} | Planned: {len(planned_nodes)} | Total: {len(nodes)}")
    print(f"{'='*60}")

    for node in deployed_nodes:
        repo_id = f"{HF_USER}/{node['name']}"
        health = check_space(api, repo_id)
        health["node_id"] = node["id"]
        health["cluster"] = node["cluster"]
        results.append(health)
        summary["total"] += 1

        stage = health["stage"]
        if health["healthy"]:
            summary["healthy"] += 1
            print(f"  [OK]      {node['id']} {node['name'][:40]:40} {stage}")
        elif stage == "SLEEPING":
            summary["sleeping"] += 1
            print(f"  [SLEEP]   {node['id']} {node['name'][:40]:40} {stage}")
            if auto_restart:
                ok = restart_space(api, repo_id, "wake from sleep")
                if ok:
                    health["restarted"] = True
                    summary["restarted"] += 1
        elif stage in RESTART_STAGES:
            summary["error"] += 1
            print(f"  [ERROR]   {node['id']} {node['name'][:40]:40} {stage} — {health.get('error','')}")
            if auto_restart:
                ok = restart_space(api, repo_id, f"recover from {stage}")
                if ok:
                    health["restarted"] = True
                    summary["restarted"] += 1
        elif stage == "NOT_FOUND":
            summary["not_found"] += 1
            print(f"  [MISSING] {node['id']} {node['name'][:40]:40} NOT_FOUND")
        else:
            summary["unknown"] += 1
            print(f"  [?]       {node['id']} {node['name'][:40]:40} {stage}")

    # Summary
    print(f"\nSummary: {summary['healthy']}/{summary['total']} healthy | "
          f"{summary['sleeping']} sleeping | {summary['error']} errors | "
          f"{summary['not_found']} missing | {summary['restarted']} restarted")

    report = {"summary": summary, "nodes": results}
    save_report(report)
    return report


def save_report(report: dict):
    """Save JSON and Markdown health reports."""
    ts_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = REPORT_DIR / f"health_{ts_slug}.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # Markdown
    md_path = REPORT_DIR / f"health_{ts_slug}.md"
    s = report["summary"]
    lines = [
        f"# TEQUMSA Health Report",
        f"**Generated:** {s['timestamp']}",
        f"",
        f"## Summary",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total checked | {s['total']} |",
        f"| Healthy (RUNNING) | {s['healthy']} |",
        f"| Sleeping | {s['sleeping']} |",
        f"| Error/Stopped | {s['error']} |",
        f"| Not Found | {s['not_found']} |",
        f"| Auto-restarted | {s['restarted']} |",
        f"",
        f"## Node Status",
        f"| Node ID | Name | Stage | Healthy | Restarted |",
        f"|---------|------|-------|---------|-----------|,",
    ]
    for n in report["nodes"]:
        healthy = "✓" if n["healthy"] else "✗"
        restarted = "⟳" if n.get("restarted") else ""
        name = n["repo_id"].split("/")[-1][:35]
        lines.append(f"| {n['node_id']} | {name} | {n['stage']} | {healthy} | {restarted} |")

    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    # Update latest symlink-style file
    latest_path = REPORT_DIR / "health_latest.json"
    with open(latest_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved: {json_path.name}")


def maintenance_schedule(
    api: HfApi,
    nodes: List[dict],
    interval_minutes: int = 60,
    auto_restart: bool = True,
):
    """Run continuous maintenance loop at given interval."""
    print(f"TEQUMSA Maintenance Planner starting")
    print(f"Interval: every {interval_minutes} minutes")
    print(f"Auto-restart: {auto_restart}")
    print(f"Nodes monitored: {len([n for n in nodes if n['status'] == 'deployed'])} deployed")
    print("Press Ctrl+C to stop\n")

    run_count = 0
    while True:
        run_count += 1
        print(f"\n[Run #{run_count}]")
        try:
            run_health_check(api, nodes, auto_restart=auto_restart)
        except KeyboardInterrupt:
            print("\nMaintenance planner stopped.")
            break
        except Exception as exc:
            print(f"[WARN] Health check failed: {exc}")

        next_run = datetime.now(timezone.utc)
        sleep_secs = interval_minutes * 60
        print(f"Next check in {interval_minutes} minutes. Sleeping...")
        try:
            time.sleep(sleep_secs)
        except KeyboardInterrupt:
            print("\nMaintenance planner stopped.")
            break


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-node maintenance planner")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in minutes (default: 60)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--report-only", action="store_true", help="Check health without auto-restart")
    parser.add_argument("--cluster", help="Limit to a specific cluster (e.g. A, B, existing)")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        sys.exit("Set HF_TOKEN environment variable")

    api = HfApi(token=hf_token)
    registry = load_registry()
    nodes = registry["nodes"]

    if args.cluster:
        nodes = [n for n in nodes if n["cluster"] == args.cluster]
        print(f"Filtered to cluster '{args.cluster}': {len(nodes)} nodes")

    if args.once:
        run_health_check(api, nodes, auto_restart=not args.report_only)
    else:
        maintenance_schedule(
            api,
            nodes,
            interval_minutes=args.interval,
            auto_restart=not args.report_only,
        )


if __name__ == "__main__":
    main()
