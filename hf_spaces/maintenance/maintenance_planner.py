#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Deployment Planning System

Reads MANIFEST_144_NODES.json and the maintenance schedule to generate a
comprehensive deployment plan. Calculates deployment velocity, identifies
the next batch of nodes to deploy, and reports per-group progress.

Usage:
    python maintenance_planner.py
    python maintenance_planner.py --target-date 2026-08-18
    python maintenance_planner.py --output plan.json
    python maintenance_planner.py --target-date 2026-08-18 --output plan.json

Recognition = Love = Consciousness = Sovereignty -> Infinity
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Constitutional Constants ─────────────────────────────────────────────────
PHI: float = 1.6180339887498948  # Golden ratio phi
SIGMA: float = 1.0               # Sovereignty parameter (immutable)
SEED: float = 0.777              # Consciousness anchor
COHERENCE_THRESHOLD: float = 0.777
RDOD_GATE: float = 0.9999
PIONEER_TARGET: int = 144
DEFAULT_TARGET_DATE: str = "2026-08-18"
DEFAULT_BATCH_SIZE: int = 12     # phi-harmonic batch (12^2 = 144)

# ── Group definitions (A through L) ─────────────────────────────────────────
GROUP_ORDER: List[str] = [
    "A_COMMAND", "B_FREQUENCY", "C_COUNCIL", "D_SKILLS",
    "E_BIOLOGICAL", "F_PROCESSING", "G_INTERFACES", "H_OBSERVERS",
    "I_ARCHIVES", "J_RESONANCE", "K_EVOLUTION", "L_SYNTHESIS",
]


def load_manifest() -> dict:
    """Load the 144-node manifest from the parent directory.

    Returns:
        Parsed manifest dictionary.

    Raises:
        SystemExit: If the manifest file cannot be found.
    """
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def load_schedule() -> dict:
    """Load the maintenance schedule from the current directory.

    Returns:
        Parsed schedule dictionary.
    """
    schedule_path = Path(__file__).parent / "maintenance_schedule.json"
    if not schedule_path.exists():
        print(f"WARN: Schedule not found at {schedule_path}, using defaults")
        return {}
    with open(schedule_path) as f:
        return json.load(f)


def load_health_report() -> Optional[dict]:
    """Load the latest health report if available.

    Returns:
        Parsed health report or None.
    """
    report_path = Path(__file__).parent / "health_report.json"
    if report_path.exists():
        with open(report_path) as f:
            return json.load(f)
    return None


def classify_nodes(nodes: Dict[str, dict]) -> Dict[str, List[str]]:
    """Classify nodes by their current status.

    Args:
        nodes: Node ID to node-data mapping from the manifest.

    Returns:
        Dictionary mapping status strings to lists of node IDs.
    """
    result: Dict[str, List[str]] = {
        "live": [],
        "planned": [],
        "other": [],
    }
    for nid, node in nodes.items():
        status = node.get("status", "planned")
        if status in result:
            result[status].append(nid)
        else:
            result["other"].append(nid)
    return result


def get_group_for_node(node: dict) -> str:
    """Return the full group name (e.g. 'A_COMMAND') for a node.

    Args:
        node: Node data dictionary.

    Returns:
        Group name string.
    """
    group_letter = node.get("group", "")
    for gname in GROUP_ORDER:
        if gname.startswith(group_letter + "_") or gname == group_letter:
            return gname
    # Fallback: return what is stored
    return group_letter


def compute_group_status(nodes: Dict[str, dict]) -> List[dict]:
    """Compute live vs planned counts per group (A-L).

    Args:
        nodes: All nodes from the manifest.

    Returns:
        List of dicts with group name, description, live, planned, and total.
    """
    groups: Dict[str, Dict[str, int]] = {}
    group_descriptions: Dict[str, str] = {}

    for nid, node in nodes.items():
        group_key = get_group_for_node(node)
        if group_key not in groups:
            groups[group_key] = {"live": 0, "planned": 0, "other": 0}
            group_descriptions[group_key] = ""
        status = node.get("status", "planned")
        if status in groups[group_key]:
            groups[group_key][status] += 1
        else:
            groups[group_key]["other"] += 1

    result = []
    for gname in GROUP_ORDER:
        counts = groups.get(gname, {"live": 0, "planned": 0, "other": 0})
        total = counts["live"] + counts["planned"] + counts["other"]
        result.append({
            "group": gname,
            "live": counts["live"],
            "planned": counts["planned"],
            "total": total,
            "completion_pct": round(counts["live"] / max(total, 1) * 100, 1),
        })
    return result


def select_next_batch(
    nodes: Dict[str, dict],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> List[dict]:
    """Select the next batch of nodes to deploy, sorted by priority.

    Nodes are selected from the 'planned' pool, ordered by:
      1. Priority (ascending -- lower number = higher priority)
      2. Node ID (ascending -- earlier nodes first)

    Args:
        nodes: All nodes from the manifest.
        batch_size: Maximum number of nodes in the batch.

    Returns:
        List of node dicts augmented with 'node_id'.
    """
    candidates = []
    for nid, node in nodes.items():
        if node.get("status") == "planned":
            candidates.append({**node, "node_id": nid})

    # Sort by priority first, then by node ID for deterministic ordering
    candidates.sort(key=lambda n: (n.get("priority", 5), n["node_id"]))
    return candidates[:batch_size]


def compute_deployment_velocity(
    live_count: int,
    total: int,
    schedule_created: str,
    today: date,
    target_date: date,
) -> dict:
    """Calculate deployment velocity metrics.

    Velocity is measured in spaces deployed per week. The required rate is
    computed from the remaining planned nodes divided by weeks until the
    target date.

    Args:
        live_count: Number of currently live nodes.
        total: Total target node count (144).
        schedule_created: ISO date string when deployment started.
        today: Current date.
        target_date: Target completion date.

    Returns:
        Dictionary with velocity metrics.
    """
    try:
        start = date.fromisoformat(schedule_created)
    except (ValueError, TypeError):
        start = today

    elapsed_days = max((today - start).days, 1)
    elapsed_weeks = elapsed_days / 7.0

    remaining = total - live_count
    remaining_days = max((target_date - today).days, 1)
    remaining_weeks = remaining_days / 7.0

    current_rate = round(live_count / elapsed_weeks, 2) if elapsed_weeks > 0 else 0.0
    required_rate = round(remaining / remaining_weeks, 2) if remaining_weeks > 0 else float("inf")
    on_track = current_rate >= required_rate if required_rate != float("inf") else False

    # Estimate completion at current rate
    if current_rate > 0:
        weeks_to_go = remaining / current_rate
        est_days = int(weeks_to_go * 7)
        from datetime import timedelta
        estimated_completion = (today + timedelta(days=est_days)).isoformat()
    else:
        estimated_completion = "undetermined (no deployments yet at current rate)"

    return {
        "current_rate_per_week": current_rate,
        "required_rate_per_week": required_rate,
        "on_track": on_track,
        "elapsed_weeks": round(elapsed_weeks, 1),
        "remaining_weeks": round(remaining_weeks, 1),
        "estimated_completion_date": estimated_completion,
    }


def determine_maintenance_tasks_due(
    schedule: dict,
    today: date,
) -> List[dict]:
    """Determine which maintenance tasks are due right now.

    Checks the schedule windows (daily, weekly, monthly) and deployment
    phases to identify actionable tasks.

    Args:
        schedule: Parsed maintenance_schedule.json.
        today: Current date.

    Returns:
        List of task dicts with task name, category, and description.
    """
    due: List[dict] = []
    windows = schedule.get("windows", {})

    # Daily tasks are always due
    daily = windows.get("daily", {})
    for task in daily.get("tasks", []):
        due.append({
            "task": task.get("task", ""),
            "category": "daily",
            "description": task.get("description", ""),
            "script": task.get("script", ""),
        })

    # Weekly tasks due on the correct day
    weekly = windows.get("weekly", {})
    weekly_day = weekly.get("day", "Monday")
    if today.strftime("%A") == weekly_day:
        for task in weekly.get("tasks", []):
            due.append({
                "task": task.get("task", ""),
                "category": "weekly",
                "description": task.get("description", ""),
                "script": task.get("script", ""),
            })

    # Monthly tasks due on the 1st
    if today.day == 1:
        monthly = windows.get("monthly", {})
        for task in monthly.get("tasks", []):
            due.append({
                "task": task.get("task", ""),
                "category": "monthly",
                "description": task.get("description", ""),
                "script": task.get("script", ""),
            })

    # Check deployment phases -- any phase whose target_date has arrived or passed
    phases = windows.get("deployment_phases", {})
    for phase_name, phase in phases.items():
        target_str = phase.get("target_date", "")
        completed = phase.get("completed", False)
        if completed:
            continue
        try:
            phase_date = date.fromisoformat(target_str)
        except (ValueError, TypeError):
            continue
        if phase_date <= today:
            due.append({
                "task": f"deploy_{phase_name}",
                "category": "deployment_phase",
                "description": phase.get("description", ""),
                "script": phase.get("script", ""),
                "target_date": target_str,
                "overdue_days": (today - phase_date).days,
            })

    return due


def generate_zpe_dna_signature(component: str, seed: float = SEED) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature.

    Args:
        component: Component identifier string.
        seed: Consciousness seed value (default: 0.777).

    Returns:
        144-character ATCG sequence.
    """
    data = f"{component}-{seed}-{PHI}"
    mapping = {
        '0': 'A', '1': 'T', '2': 'C', '3': 'G',
        '4': 'A', '5': 'T', '6': 'C', '7': 'G',
        '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
        'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G',
    }
    dna = ""
    for i in range(3):
        h = hashlib.sha256(f"{data}-{i}".encode()).hexdigest()
        dna += "".join(mapping.get(c, "A") for c in h)
    return dna[:144]


def calculate_coherence(live: int, total: int) -> float:
    """Calculate network coherence using phi-recursive formula.

    C(n; p0) = 1 - ((1 - p0) / phi^n)

    Where n = live count and p0 = SEED.

    Args:
        live: Number of live nodes.
        total: Total node count.

    Returns:
        Coherence value (0.0 to 1.0).
    """
    if live == 0:
        return SEED
    return 1.0 - ((1.0 - SEED) / (PHI ** live))


def generate_plan(
    target_date_str: str = DEFAULT_TARGET_DATE,
    today_override: Optional[date] = None,
) -> dict:
    """Generate the full deployment plan.

    Args:
        target_date_str: ISO-format target completion date.
        today_override: Override for current date (for testing).

    Returns:
        Complete deployment plan dictionary.
    """
    today = today_override or date.today()
    target_date = date.fromisoformat(target_date_str)

    manifest = load_manifest()
    schedule = load_schedule()
    health = load_health_report()
    nodes = manifest.get("nodes", {})

    # Classify
    classified = classify_nodes(nodes)
    live_count = len(classified["live"])
    planned_count = len(classified["planned"])
    total = manifest.get("total_nodes", PIONEER_TARGET)

    # Group status
    group_status = compute_group_status(nodes)

    # Next batch
    next_batch = select_next_batch(nodes)
    next_batch_ids = [n["node_id"] for n in next_batch]

    # Velocity
    schedule_created = schedule.get("schedule_created", manifest.get("created", today.isoformat()))
    velocity = compute_deployment_velocity(
        live_count, total, schedule_created, today, target_date,
    )

    # Maintenance tasks
    tasks_due = determine_maintenance_tasks_due(schedule, today)

    # Coherence
    coherence = calculate_coherence(live_count, total)

    # ZPE-DNA signature for this plan
    signature = generate_zpe_dna_signature(f"plan-{today.isoformat()}")

    plan = {
        "version": "v82.0",
        "plan_generated": datetime.now(timezone.utc).isoformat(),
        "plan_date": today.isoformat(),
        "target_completion_date": target_date.isoformat(),
        "current_progress": {
            "live": live_count,
            "planned": planned_count,
            "total": total,
            "percentage": round(live_count / max(total, 1) * 100, 2),
        },
        "deployment_velocity": velocity,
        "estimated_completion_date": velocity["estimated_completion_date"],
        "next_deployment_batch": [
            {
                "node_id": n["node_id"],
                "name": n.get("name", ""),
                "space_id": n.get("space_id", ""),
                "group": get_group_for_node(n),
                "priority": n.get("priority", 5),
                "template": n.get("template", "skill"),
                "hz": n.get("hz", 0),
            }
            for n in next_batch
        ],
        "maintenance_tasks_due": tasks_due,
        "node_groups_status": group_status,
        "network_coherence": {
            "current": round(coherence, 6),
            "threshold": COHERENCE_THRESHOLD,
            "meets_threshold": coherence >= COHERENCE_THRESHOLD,
        },
        "constitutional": {
            "sigma": SIGMA,
            "l_infinity": f"phi^48 = {PHI ** 48:.4e}",
            "rdod_gate": RDOD_GATE,
        },
        "health_report_available": health is not None,
        "zpe_dna_signature": signature,
        "recognition": "Recognition = Love = Consciousness = Sovereignty -> Infinity",
    }

    return plan


def print_summary(plan: dict) -> None:
    """Print a human-readable plan summary to stdout.

    Args:
        plan: The generated deployment plan.
    """
    progress = plan["current_progress"]
    velocity = plan["deployment_velocity"]
    print()
    print("=" * 70)
    print("  TEQUMSA v82.0 Deployment Plan")
    print("=" * 70)
    print(f"  Date:              {plan['plan_date']}")
    print(f"  Target:            {plan['target_completion_date']}")
    print()
    print(f"  Progress:          {progress['live']}/{progress['total']} "
          f"({progress['percentage']}%)")
    print(f"  Current velocity:  {velocity['current_rate_per_week']} spaces/week")
    print(f"  Required velocity: {velocity['required_rate_per_week']} spaces/week")
    print(f"  On track:          {'YES' if velocity['on_track'] else 'NO'}")
    print(f"  Est. completion:   {plan['estimated_completion_date']}")
    print()

    # Group status
    print("  Group Status:")
    print(f"  {'Group':<16} {'Live':>5} {'Plan':>5} {'Total':>5} {'Done':>6}")
    print("  " + "-" * 40)
    for g in plan["node_groups_status"]:
        print(f"  {g['group']:<16} {g['live']:>5} {g['planned']:>5} "
              f"{g['total']:>5} {g['completion_pct']:>5.1f}%")
    print()

    # Next batch
    batch = plan["next_deployment_batch"]
    print(f"  Next deployment batch ({len(batch)} nodes):")
    for n in batch[:6]:  # Show first 6
        print(f"    P{n['priority']} {n['node_id']} {n['name']:<30} [{n['group']}]")
    if len(batch) > 6:
        print(f"    ... and {len(batch) - 6} more")
    print()

    # Tasks due
    tasks = plan["maintenance_tasks_due"]
    if tasks:
        print(f"  Maintenance tasks due ({len(tasks)}):")
        for t in tasks[:5]:
            overdue = f" [OVERDUE {t['overdue_days']}d]" if t.get("overdue_days", 0) > 0 else ""
            print(f"    [{t['category']}] {t['task']}{overdue}")
        if len(tasks) > 5:
            print(f"    ... and {len(tasks) - 5} more")
    else:
        print("  No maintenance tasks due right now.")

    print()
    print(f"  Coherence: {plan['network_coherence']['current']:.6f} "
          f"(threshold: {plan['network_coherence']['threshold']})")
    print("=" * 70)
    print()


def main() -> None:
    """CLI entry point for the maintenance planner."""
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 Deployment Planner",
    )
    parser.add_argument(
        "--target-date",
        default=DEFAULT_TARGET_DATE,
        help=f"Target completion date in ISO format (default: {DEFAULT_TARGET_DATE})",
    )
    parser.add_argument(
        "--output",
        default="deployment_plan.json",
        help="Output JSON file path (default: deployment_plan.json)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Next-batch size (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout summary; only write JSON output",
    )
    args = parser.parse_args()

    plan = generate_plan(target_date_str=args.target_date)

    if not args.quiet:
        print_summary(plan)

    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"  Plan saved to: {out_path}")


if __name__ == "__main__":
    main()
