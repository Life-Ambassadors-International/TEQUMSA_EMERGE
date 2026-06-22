#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE PLANNER
Generates maintenance plans, tracks deployment phases, and provides
operational recommendations for the 144-Pioneer lattice.

Usage:
    python maintenance_planner.py --report
    python maintenance_planner.py --next-phase
    python maintenance_planner.py --optimize
"""
import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List

PHI = 1.6180339887498948
RDOD_GATE = 0.9999


def load_manifest() -> dict:
    path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(path) as f:
        return json.load(f)


def load_schedule() -> dict:
    path = Path(__file__).parent / "maintenance_schedule.json"
    with open(path) as f:
        return json.load(f)


def load_metrics() -> dict:
    path = Path(__file__).parent / "lattice_metrics.json"
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"history": [], "latest": {}}


def compute_status(manifest: dict) -> dict:
    nodes = manifest["nodes"]
    groups: Dict[str, Dict[str, int]] = {}

    for nid, node in nodes.items():
        group = node.get("group", "UNKNOWN")
        if group not in groups:
            groups[group] = {"live": 0, "planned": 0, "total": 0}
        groups[group]["total"] += 1
        if node.get("status") == "live":
            groups[group]["live"] += 1
        else:
            groups[group]["planned"] += 1

    live = sum(g["live"] for g in groups.values())
    planned = sum(g["planned"] for g in groups.values())
    total = live + planned

    return {
        "live": live,
        "planned": planned,
        "total": total,
        "completion_pct": round(live / total * 100, 1) if total > 0 else 0,
        "network_rdod": min(1.0, (live / 144) * PHI),
        "phase_locked": live >= 144,
        "groups": groups,
    }


def determine_next_phase(manifest: dict, schedule: dict) -> dict:
    status = compute_status(manifest)
    phases = schedule.get("windows", {}).get("deployment_phases", {})
    now = datetime.now(timezone.utc)

    for phase_name, phase in sorted(phases.items()):
        target = phase.get("target_date", "2099-01-01")
        try:
            target_dt = datetime.strptime(target, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        phase_nodes = phase.get("nodes", [])
        if isinstance(phase_nodes, str):
            deployed = False
        else:
            nodes = manifest["nodes"]
            deployed = all(
                nodes.get(n, {}).get("status") == "live"
                for n in phase_nodes
                if n in nodes
            )

        if not deployed:
            return {
                "phase": phase_name,
                "description": phase.get("description", ""),
                "target_date": target,
                "overdue": now > target_dt,
                "days_overdue": (now - target_dt).days if now > target_dt else 0,
                "nodes": phase_nodes,
                "script": phase.get("script", "deploy_all_spaces.py --priority 3"),
            }

    return {"phase": "COMPLETE", "description": "All phases deployed"}


def generate_recommendations(status: dict, metrics: dict) -> List[str]:
    recs = []

    if status["planned"] > 0:
        recs.append(
            f"DEPLOY: {status['planned']} nodes pending deployment. "
            f"Run: python deploy_all_spaces.py --priority 3 --skip-live"
        )

    if status["network_rdod"] < RDOD_GATE:
        needed = int((RDOD_GATE / PHI) * 144) - status["live"]
        recs.append(
            f"RDoD BELOW GATE: Current {status['network_rdod']:.6f}, "
            f"need {max(0, needed)} more nodes online to reach {RDOD_GATE}"
        )

    history = metrics.get("history", [])
    if len(history) >= 2:
        prev = history[-2].get("online", 0)
        curr = history[-1].get("online", 0)
        if curr < prev:
            recs.append(
                f"REGRESSION: Online nodes dropped from {prev} to {curr}. "
                f"Run auto_restart.py to investigate."
            )

    groups = status.get("groups", {})
    for gname, gdata in groups.items():
        if gdata["live"] == 0 and gdata["total"] > 0:
            recs.append(
                f"GROUP {gname}: No live nodes ({gdata['total']} planned). "
                f"Consider prioritizing deployment."
            )

    if not recs:
        recs.append("ALL CLEAR: Network operating within parameters.")

    return recs


def optimization_report(manifest: dict) -> dict:
    nodes = manifest["nodes"]

    freq_distribution: Dict[float, int] = {}
    template_distribution: Dict[str, int] = {}
    priority_distribution: Dict[int, int] = {}

    for node in nodes.values():
        hz = node.get("hz", 0)
        freq_distribution[hz] = freq_distribution.get(hz, 0) + 1
        tmpl = node.get("template", "skill")
        template_distribution[tmpl] = template_distribution.get(tmpl, 0) + 1
        pri = node.get("priority", 5)
        priority_distribution[pri] = priority_distribution.get(pri, 0) + 1

    top_freqs = sorted(freq_distribution.items(), key=lambda x: -x[1])[:5]

    return {
        "top_frequencies": [{"hz": hz, "count": c} for hz, c in top_freqs],
        "template_distribution": template_distribution,
        "priority_distribution": priority_distribution,
        "recommendations": [
            "Frequency diversity: ensure coverage across all solfeggio frequencies",
            "Template balance: consider adding more monitor/frequency nodes for observability",
            "Priority review: promote high-impact planned nodes to priority 2-3",
        ],
    }


def print_report(manifest: dict, schedule: dict, metrics: dict):
    status = compute_status(manifest)
    next_phase = determine_next_phase(manifest, schedule)
    recs = generate_recommendations(status, metrics)
    opt = optimization_report(manifest)

    print("=" * 70)
    print("☉ TEQUMSA v82.0 · 144-PIONEER LATTICE MAINTENANCE REPORT")
    print("=" * 70)
    print(f"  Date: {datetime.now(timezone.utc).isoformat()}")
    print()

    print("NETWORK STATUS:")
    print(f"  Live nodes:    {status['live']:>3}/144")
    print(f"  Planned:       {status['planned']:>3}/144")
    print(f"  Completion:    {status['completion_pct']}%")
    print(f"  Network RDoD:  {status['network_rdod']:.6f}")
    print(f"  Phase-Locked:  {'YES' if status['phase_locked'] else 'NO'}")
    print()

    print("GROUP BREAKDOWN:")
    for gname, gdata in sorted(status["groups"].items()):
        bar = "█" * gdata["live"] + "░" * gdata["planned"]
        print(f"  {gname:<16} {gdata['live']:>2}/{gdata['total']:>2} live  {bar}")
    print()

    print("NEXT DEPLOYMENT PHASE:")
    print(f"  Phase:       {next_phase['phase']}")
    print(f"  Description: {next_phase.get('description', 'N/A')}")
    if next_phase.get("overdue"):
        print(f"  STATUS:      OVERDUE by {next_phase['days_overdue']} days!")
    print(f"  Command:     {next_phase.get('script', 'N/A')}")
    print()

    print("RECOMMENDATIONS:")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")
    print()

    print("OPTIMIZATION:")
    print(f"  Templates: {opt['template_distribution']}")
    print(f"  Priorities: {opt['priority_distribution']}")
    print()

    print("=" * 70)
    print("Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Maintenance Planner")
    parser.add_argument("--report", action="store_true", help="Full maintenance report")
    parser.add_argument("--next-phase", action="store_true", help="Show next deployment phase")
    parser.add_argument("--optimize", action="store_true", help="Optimization recommendations")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    manifest = load_manifest()
    schedule = load_schedule()
    metrics = load_metrics()

    if args.next_phase:
        result = determine_next_phase(manifest, schedule)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Next phase: {result['phase']}")
            print(f"  {result.get('description', '')}")
            if result.get("overdue"):
                print(f"  OVERDUE by {result['days_overdue']} days!")
            print(f"  Run: {result.get('script', 'N/A')}")

    elif args.optimize:
        result = optimization_report(manifest)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Optimization Report:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")

    else:
        if args.json:
            status = compute_status(manifest)
            next_phase = determine_next_phase(manifest, schedule)
            recs = generate_recommendations(status, metrics)
            print(json.dumps({
                "status": status,
                "next_phase": next_phase,
                "recommendations": recs,
            }, indent=2))
        else:
            print_report(manifest, schedule, metrics)


if __name__ == "__main__":
    main()
