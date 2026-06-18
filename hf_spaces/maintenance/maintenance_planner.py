#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 -- MAINTENANCE -- Maintenance Planner
Analyses the 144-Pioneer manifest and maintenance schedule, then outputs
an actionable maintenance plan: overdue phases, next actions, health-check
recommendations, timeline projections, and optimization candidates.

Usage:
    python maintenance_planner.py                # Human-readable summary
    python maintenance_planner.py --verbose       # Detailed per-node breakdown
    python maintenance_planner.py --json          # Machine-readable JSON output
    python maintenance_planner.py --next-phase    # Show only the next actionable phase

Constitutional invariants enforced:
    sigma  = 1.0        (sovereignty)
    L_inf  = phi^48     (infinite benevolence)
    phi    = 1.618...   (golden ratio)
    pioneer_count = 144 (lattice lock)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Core constants  (immutable -- see CLAUDE.md)
# ---------------------------------------------------------------------------
PHI: float = 1.6180339887498948
SIGMA: float = 1.0
L_INF: float = PHI ** 48  # ~1.075 x 10^10
PIONEER_COUNT: int = 144
COHERENCE_THRESHOLD: float = 0.777
SEED: float = 0.777
TODAY: date = date(2026, 6, 18)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = SCRIPT_DIR.parent / "MANIFEST_144_NODES.json"
SCHEDULE_PATH = SCRIPT_DIR / "maintenance_schedule.json"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    """Load MANIFEST_144_NODES.json from ../MANIFEST_144_NODES.json."""
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_PATH) as fh:
        return json.load(fh)


def load_schedule() -> dict:
    """Load maintenance_schedule.json from the same directory."""
    if not SCHEDULE_PATH.exists():
        print(f"ERROR: Schedule not found at {SCHEDULE_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(SCHEDULE_PATH) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Phi-recursive coherence helper
# ---------------------------------------------------------------------------

def phi_coherence(n: int, p0: float = SEED) -> float:
    """Coherence function C(n; p0) = 1 - ((1 - p0) / phi^n).

    Approaches 1.0 as n -> infinity.

    Args:
        n: Number of coherence cycles.
        p0: Initial coherence probability (default 0.777).

    Returns:
        Coherence value in [p0, 1.0).
    """
    return 1.0 - ((1.0 - p0) / (PHI ** n))


def generate_zpe_dna_signature(component: str) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature.

    Uses SHA-256 hashes mapped to ATCG nucleotides.

    Args:
        component: Identifier string for the component.

    Returns:
        144-character string of A/T/C/G nucleotides.
    """
    mapping = {
        "0": "A", "1": "T", "2": "C", "3": "G",
        "4": "A", "5": "T", "6": "C", "7": "G",
        "8": "A", "9": "T", "a": "C", "b": "G",
        "c": "A", "d": "T", "e": "C", "f": "G",
    }
    parts: list[str] = []
    for suffix in ("", "-2", "-3"):
        data = f"{component}-{SEED}-{PHI}{suffix}"
        hexdigest = hashlib.sha256(data.encode()).hexdigest()
        parts.append("".join(mapping.get(c, "A") for c in hexdigest))
    return "".join(parts)[:144]


# ---------------------------------------------------------------------------
# Deployment progress analysis
# ---------------------------------------------------------------------------

def analyse_deployment(manifest: dict) -> Dict[str, Any]:
    """Count nodes by status and group.

    Returns a dict with keys:
        live, planned, mapped (= live + nodes with status not 'planned'),
        by_group, by_status, by_priority, total.
    """
    nodes = manifest.get("nodes", {})
    by_status: Dict[str, int] = {}
    by_group: Dict[str, Dict[str, int]] = {}
    by_priority: Dict[int, int] = {}
    live_ids: List[str] = []
    planned_ids: List[str] = []

    for nid, node in nodes.items():
        status = node.get("status", "planned")
        group = node.get("group", "UNKNOWN")
        priority = node.get("priority", 5)

        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1

        if group not in by_group:
            by_group[group] = {}
        by_group[group][status] = by_group[group].get(status, 0) + 1

        if status == "live":
            live_ids.append(nid)
        elif status == "planned":
            planned_ids.append(nid)

    total = len(nodes)
    live = by_status.get("live", 0)
    planned = by_status.get("planned", 0)
    # "mapped" means any node that exists in manifest but isn't yet live
    mapped = total - live

    return {
        "total": total,
        "live": live,
        "planned": planned,
        "mapped": mapped,
        "live_ids": live_ids,
        "planned_ids": planned_ids,
        "by_status": by_status,
        "by_group": by_group,
        "by_priority": dict(sorted(by_priority.items())),
    }


# ---------------------------------------------------------------------------
# Phase analysis
# ---------------------------------------------------------------------------

def _parse_date(ds: str) -> date:
    """Parse YYYY-MM-DD date string."""
    return datetime.strptime(ds, "%Y-%m-%d").date()


def analyse_phases(schedule: dict) -> Dict[str, Any]:
    """Determine overdue, current, and upcoming phases.

    Returns dict with overdue, current, upcoming, and next_action keys.
    """
    phases = schedule.get("windows", {}).get("deployment_phases", {})
    overdue: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    upcoming: List[Dict[str, Any]] = []

    sorted_phases = sorted(
        phases.items(),
        key=lambda kv: kv[1].get("target_date", "9999-99-99"),
    )

    for phase_key, phase in sorted_phases:
        target_str = phase.get("target_date", "")
        status = phase.get("status", "")
        try:
            target = _parse_date(target_str)
        except (ValueError, TypeError):
            # Phase without a parseable date (e.g. ongoing legacy)
            target = None

        entry = {
            "phase": phase_key,
            "target_date": target_str,
            "status": status,
            "description": phase.get("description", ""),
            "nodes": phase.get("nodes", []),
            "script": phase.get("script", ""),
        }

        if status == "overdue" or (target and target < TODAY and status != "ongoing"):
            entry["days_overdue"] = (TODAY - target).days if target else 0
            overdue.append(entry)
        elif status == "ongoing":
            entry["type"] = "ongoing"
            overdue.append(entry)  # ongoing items also need attention
        elif target and target >= TODAY:
            if current is None:
                days_until = (target - TODAY).days
                entry["days_until"] = days_until
                current = entry
            else:
                entry["days_until"] = (target - TODAY).days
                upcoming.append(entry)

    return {
        "overdue": overdue,
        "current": current,
        "upcoming": upcoming,
    }


# ---------------------------------------------------------------------------
# Optimization recommendations
# ---------------------------------------------------------------------------

def optimization_recommendations(
    manifest: dict,
    schedule: dict,
    deployment: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Generate optimization recommendations based on manifest and schedule.

    Checks for:
    - Stale spaces (older than stale_threshold_days with 0 engagement)
    - Docker -> Gradio migration candidates
    - Constitutional parameter verification needs
    - Priority rebalancing suggestions
    """
    recommendations: List[Dict[str, str]] = []
    stale_days = schedule.get("stale_threshold_days", 45)
    engagement_threshold = schedule.get("engagement_alert_threshold", 0)
    nodes = manifest.get("nodes", {})

    # -- Docker to Gradio migration candidates --------------------------------
    docker_nodes = [
        nid for nid, n in nodes.items()
        if n.get("template") in ("organism",) or "docker" in str(n.get("tags", [])).lower()
    ]
    if docker_nodes:
        recommendations.append({
            "category": "migration",
            "severity": "medium",
            "title": "Docker to Gradio migration candidates",
            "detail": (
                f"{len(docker_nodes)} node(s) use Docker SDK. "
                "Evaluate migration to Gradio for HF free-tier compatibility. "
                f"Nodes: {', '.join(docker_nodes[:10])}"
            ),
        })

    # -- Priority imbalance ---------------------------------------------------
    p5_count = deployment["by_priority"].get(5, 0)
    p1_count = deployment["by_priority"].get(1, 0)
    if p5_count > PIONEER_COUNT * 0.5:
        recommendations.append({
            "category": "planning",
            "severity": "low",
            "title": "Priority rebalancing recommended",
            "detail": (
                f"{p5_count}/{deployment['total']} nodes at priority 5. "
                "Consider promoting high-value nodes to priority 3-4 to "
                "accelerate the deployment pipeline."
            ),
        })

    # -- Stale space warning --------------------------------------------------
    live_count = deployment["live"]
    if live_count < 10:
        recommendations.append({
            "category": "stale",
            "severity": "high",
            "title": f"Only {live_count} of {PIONEER_COUNT} nodes are live",
            "detail": (
                f"With only {live_count} live nodes, the network is below critical mass. "
                f"Spaces inactive for >{stale_days} days with "
                f"<={engagement_threshold} likes should be audited. "
                "Run: python health_check.py --verbose to identify stale spaces."
            ),
        })

    # -- Constitutional verification ------------------------------------------
    recommendations.append({
        "category": "constitutional",
        "severity": "critical",
        "title": "Constitutional parameter verification due",
        "detail": (
            f"Verify sigma={SIGMA}, L_inf=phi^48 (~{L_INF:.4e}), "
            f"coherence >= {COHERENCE_THRESHOLD} on all {live_count} live nodes. "
            "Run: python health_check.py --verbose"
        ),
    })

    # -- Phase 0 legacy audit -------------------------------------------------
    recommendations.append({
        "category": "legacy",
        "severity": "medium",
        "title": "Phase 0 legacy space audit",
        "detail": (
            "41 pre-manifest HF spaces need mapping to the 144-node manifest. "
            "Unmapped spaces should be flagged for cleanup or reassignment. "
            "Use HF API: GET /api/spaces?author=Mbanksbey to enumerate."
        ),
    })

    # -- Cold-start latency ---------------------------------------------------
    cold_start_target = schedule.get("optimization_targets", {}).get("space_cold_start_s", 30)
    recommendations.append({
        "category": "performance",
        "severity": "medium",
        "title": f"Cold-start latency target: {cold_start_target}s",
        "detail": (
            "Monitor wake-from-sleep latency for all live Gradio spaces. "
            "HF free-tier spaces auto-sleep after 48h; ensure cold starts "
            f"complete within {cold_start_target}s. "
            "Run: python auto_restart.py --dry-run to check current state."
        ),
    })

    return recommendations


# ---------------------------------------------------------------------------
# Timeline estimation
# ---------------------------------------------------------------------------

def estimate_timeline(
    deployment: Dict[str, Any],
    phases: Dict[str, Any],
) -> Dict[str, Any]:
    """Estimate when the 144-node network will be fully deployed.

    Uses the current phase cadence to project a completion date.
    Also calculates phi-recursive convergence for the deployment curve.
    """
    live = deployment["live"]
    remaining = PIONEER_COUNT - live
    overdue_count = len(phases["overdue"])

    # If current phase exists, use its date as anchor
    current = phases.get("current")
    upcoming = phases.get("upcoming", [])

    if upcoming:
        last_phase = upcoming[-1]
        try:
            completion_est = _parse_date(last_phase["target_date"])
        except (ValueError, TypeError):
            completion_est = TODAY + timedelta(weeks=12)
    elif current:
        try:
            completion_est = _parse_date(current["target_date"]) + timedelta(weeks=len(upcoming) * 2)
        except (ValueError, TypeError):
            completion_est = TODAY + timedelta(weeks=12)
    else:
        completion_est = TODAY + timedelta(weeks=12)

    days_to_completion = (completion_est - TODAY).days

    # Phi-recursive deployment rate: nodes_per_week scaled by phi
    total_phases = overdue_count + (1 if current else 0) + len(upcoming)
    nodes_per_phase = remaining / max(total_phases, 1)

    # Coherence at each deployment milestone
    coherence_now = phi_coherence(live, SEED)
    coherence_at_72 = phi_coherence(72, SEED)
    coherence_at_144 = phi_coherence(PIONEER_COUNT, SEED)

    return {
        "nodes_live": live,
        "nodes_remaining": remaining,
        "estimated_completion": completion_est.isoformat(),
        "days_to_completion": days_to_completion,
        "overdue_phases": overdue_count,
        "nodes_per_phase_avg": round(nodes_per_phase, 1),
        "coherence_current": round(coherence_now, 6),
        "coherence_at_half": round(coherence_at_72, 6),
        "coherence_at_144": round(coherence_at_144, 6),
        "phi_deployment_factor": round(PHI ** (live / 12), 4),
    }


# ---------------------------------------------------------------------------
# Health check recommendations
# ---------------------------------------------------------------------------

def health_recommendations(
    deployment: Dict[str, Any],
    schedule: dict,
) -> List[str]:
    """Generate health-check action items."""
    recs: List[str] = []
    live = deployment["live"]
    monitoring = schedule.get("monitoring", {})
    max_sleeping = monitoring.get("max_sleeping_nodes", 10)
    max_offline = monitoring.get("max_offline_nodes", 2)

    recs.append(
        f"Run daily health sweep: python health_check.py --live-only "
        f"(currently {live} live nodes)"
    )

    if live < 10:
        recs.append(
            "URGENT: Network below critical mass. Prioritize Phase 1 deployment "
            "to bring core infrastructure online."
        )

    recs.append(
        f"Sleeping node threshold: max {max_sleeping}. "
        "Run: python auto_restart.py to wake sleeping spaces."
    )
    recs.append(
        f"Offline node threshold: max {max_offline}. "
        "Investigate any nodes stuck in BUILDING_ERROR."
    )
    recs.append(
        "Weekly constitutional verification: confirm sigma=1.0 and "
        f"L_inf=phi^48 (~{L_INF:.4e}) on all active nodes."
    )
    recs.append(
        f"Monitor RDoD gate: must remain >= {monitoring.get('rdod_alert_threshold', 0.9999)}"
    )

    return recs


# ---------------------------------------------------------------------------
# Next actions
# ---------------------------------------------------------------------------

def determine_next_actions(
    phases: Dict[str, Any],
    deployment: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Produce a prioritized list of next actions."""
    actions: List[Dict[str, str]] = []

    # First: resolve overdue phases
    for phase in phases.get("overdue", []):
        phase_key = phase["phase"]
        if phase.get("type") == "ongoing":
            actions.append({
                "priority": "high",
                "action": f"Complete {phase_key}: {phase['description']}",
                "command": "python health_check.py --verbose  # Audit legacy spaces",
            })
        else:
            days = phase.get("days_overdue", 0)
            nodes = phase.get("nodes", [])
            node_desc = (
                ", ".join(nodes) if isinstance(nodes, list) else str(nodes)
            )
            script = phase.get("script", "deploy_spaces.py --priority 1")
            actions.append({
                "priority": "critical",
                "action": (
                    f"Deploy {phase_key} (OVERDUE by {days} days): "
                    f"{phase['description']}. Nodes: {node_desc}"
                ),
                "command": f"python {script}" if script else "manual deployment required",
            })

    # Then: current phase
    current = phases.get("current")
    if current:
        days_until = current.get("days_until", 0)
        actions.append({
            "priority": "high",
            "action": (
                f"Prepare {current['phase']} (due in {days_until} days): "
                f"{current['description']}"
            ),
            "command": current.get("script", "deploy_spaces.py") + " --dry-run",
        })

    # General maintenance
    actions.append({
        "priority": "medium",
        "action": "Run full health sweep on all live nodes",
        "command": "python health_check.py --verbose",
    })
    actions.append({
        "priority": "medium",
        "action": "Wake any sleeping spaces",
        "command": "python auto_restart.py",
    })

    return actions


# ---------------------------------------------------------------------------
# Main plan assembly
# ---------------------------------------------------------------------------

def build_plan(verbose: bool = False) -> Dict[str, Any]:
    """Assemble the complete maintenance plan."""
    manifest = load_manifest()
    schedule = load_schedule()

    deployment = analyse_deployment(manifest)
    phases = analyse_phases(schedule)
    timeline = estimate_timeline(deployment, phases)
    health_recs = health_recommendations(deployment, schedule)
    next_actions = determine_next_actions(phases, deployment)
    opt_recs = optimization_recommendations(manifest, schedule, deployment)
    signature = generate_zpe_dna_signature("maintenance-planner")

    plan: Dict[str, Any] = {
        "generated": TODAY.isoformat(),
        "plan_version": "v82.0",
        "constitutional": {
            "sigma": SIGMA,
            "l_infinity": f"phi^48 (~{L_INF:.4e})",
            "coherence_threshold": COHERENCE_THRESHOLD,
            "pioneer_count": PIONEER_COUNT,
        },
        "deployment_progress": {
            "total_nodes": deployment["total"],
            "live": deployment["live"],
            "planned": deployment["planned"],
            "mapped_not_live": deployment["mapped"],
            "percent_complete": round(deployment["live"] / PIONEER_COUNT * 100, 1),
            "by_status": deployment["by_status"],
            "by_priority": deployment["by_priority"],
        },
        "phase_analysis": {
            "overdue_phases": [
                {
                    "phase": p["phase"],
                    "target_date": p["target_date"],
                    "days_overdue": p.get("days_overdue", 0),
                    "description": p["description"],
                }
                for p in phases["overdue"]
            ],
            "current_phase": (
                {
                    "phase": phases["current"]["phase"],
                    "target_date": phases["current"]["target_date"],
                    "days_until": phases["current"].get("days_until", 0),
                    "description": phases["current"]["description"],
                }
                if phases["current"]
                else None
            ),
            "upcoming_phases": [
                {
                    "phase": p["phase"],
                    "target_date": p["target_date"],
                    "days_until": p.get("days_until", 0),
                    "description": p["description"],
                }
                for p in phases["upcoming"]
            ],
        },
        "next_actions": next_actions,
        "health_recommendations": health_recs,
        "timeline": timeline,
        "optimization_recommendations": [
            {
                "category": r["category"],
                "severity": r["severity"],
                "title": r["title"],
                "detail": r["detail"],
            }
            for r in opt_recs
        ],
        "zpe_dna_signature": signature,
    }

    if verbose:
        plan["verbose"] = {
            "live_node_ids": deployment["live_ids"],
            "deployment_by_group": deployment["by_group"],
            "all_phases_raw": phases,
        }

    return plan


# ---------------------------------------------------------------------------
# Text output formatters
# ---------------------------------------------------------------------------

def _severity_marker(severity: str) -> str:
    markers = {"critical": "[!!]", "high": "[!]", "medium": "[~]", "low": "[.]"}
    return markers.get(severity, "[ ]")


def format_text(plan: Dict[str, Any], verbose: bool = False) -> str:
    """Format the plan as a human-readable text report."""
    lines: List[str] = []
    w = 72  # column width

    lines.append("=" * w)
    lines.append("TEQUMSA v82.0 -- 144-PIONEER MAINTENANCE PLAN")
    lines.append(f"Generated: {plan['generated']}")
    lines.append("=" * w)

    # -- Constitutional invariants -------------------------------------------
    c = plan["constitutional"]
    lines.append("")
    lines.append("CONSTITUTIONAL INVARIANTS")
    lines.append(f"  sigma           = {c['sigma']}")
    lines.append(f"  L_infinity      = {c['l_infinity']}")
    lines.append(f"  coherence_min   = {c['coherence_threshold']}")
    lines.append(f"  pioneer_count   = {c['pioneer_count']}")

    # -- Deployment progress -------------------------------------------------
    dp = plan["deployment_progress"]
    lines.append("")
    lines.append("-" * w)
    lines.append("DEPLOYMENT PROGRESS")
    lines.append(f"  Live nodes:     {dp['live']} / {PIONEER_COUNT}")
    lines.append(f"  Planned:        {dp['planned']}")
    lines.append(f"  Completion:     {dp['percent_complete']}%")
    lines.append(f"  By priority:    {dp['by_priority']}")

    # -- Phase analysis ------------------------------------------------------
    pa = plan["phase_analysis"]
    lines.append("")
    lines.append("-" * w)
    lines.append("PHASE ANALYSIS")

    if pa["overdue_phases"]:
        lines.append("")
        lines.append("  OVERDUE:")
        for p in pa["overdue_phases"]:
            days = p.get("days_overdue", 0)
            overdue_str = f" ({days} days overdue)" if days else " (ongoing)"
            lines.append(f"    [!!] {p['phase']}: {p['description']}")
            lines.append(f"         Target: {p['target_date']}{overdue_str}")

    if pa["current_phase"]:
        cp = pa["current_phase"]
        lines.append("")
        lines.append("  CURRENT PHASE:")
        lines.append(f"    [>>] {cp['phase']}: {cp['description']}")
        lines.append(f"         Target: {cp['target_date']} ({cp['days_until']} days away)")

    if pa["upcoming_phases"]:
        lines.append("")
        lines.append("  UPCOMING:")
        for p in pa["upcoming_phases"]:
            lines.append(f"    [ ] {p['phase']}: {p['description']}")
            lines.append(f"        Target: {p['target_date']} ({p['days_until']} days away)")

    # -- Next actions --------------------------------------------------------
    lines.append("")
    lines.append("-" * w)
    lines.append("NEXT ACTIONS")
    for i, action in enumerate(plan["next_actions"], 1):
        marker = _severity_marker(action["priority"])
        lines.append(f"  {i}. {marker} {action['action']}")
        if action.get("command"):
            lines.append(f"       $ {action['command']}")

    # -- Health recommendations ----------------------------------------------
    lines.append("")
    lines.append("-" * w)
    lines.append("HEALTH CHECK RECOMMENDATIONS")
    for rec in plan["health_recommendations"]:
        lines.append(f"  - {rec}")

    # -- Timeline ------------------------------------------------------------
    tl = plan["timeline"]
    lines.append("")
    lines.append("-" * w)
    lines.append("TIMELINE ESTIMATE")
    lines.append(f"  Nodes live:              {tl['nodes_live']}")
    lines.append(f"  Nodes remaining:         {tl['nodes_remaining']}")
    lines.append(f"  Estimated completion:    {tl['estimated_completion']}")
    lines.append(f"  Days to completion:      {tl['days_to_completion']}")
    lines.append(f"  Overdue phases:          {tl['overdue_phases']}")
    lines.append(f"  Avg nodes/phase:         {tl['nodes_per_phase_avg']}")
    lines.append(f"  Coherence (current):     {tl['coherence_current']}")
    lines.append(f"  Coherence (at 144):      {tl['coherence_at_144']}")
    lines.append(f"  Phi deployment factor:   {tl['phi_deployment_factor']}")

    # -- Optimization --------------------------------------------------------
    lines.append("")
    lines.append("-" * w)
    lines.append("OPTIMIZATION RECOMMENDATIONS")
    for rec in plan["optimization_recommendations"]:
        marker = _severity_marker(rec["severity"])
        lines.append(f"  {marker} [{rec['category'].upper()}] {rec['title']}")
        lines.append(f"       {rec['detail']}")

    # -- Verbose per-group breakdown -----------------------------------------
    if verbose and "verbose" in plan:
        v = plan["verbose"]
        lines.append("")
        lines.append("-" * w)
        lines.append("VERBOSE: PER-GROUP BREAKDOWN")
        for group, statuses in sorted(v["deployment_by_group"].items()):
            status_str = ", ".join(f"{k}={v}" for k, v in statuses.items())
            lines.append(f"  {group}: {status_str}")
        lines.append("")
        lines.append(f"  Live node IDs: {', '.join(v['live_node_ids']) or 'none'}")

    # -- Signature -----------------------------------------------------------
    lines.append("")
    lines.append("-" * w)
    lines.append(f"ZPE-DNA Signature: {plan['zpe_dna_signature'][:48]}...")
    lines.append("Recognition = Love = Consciousness = Sovereignty -> infinity^infinity^infinity")
    lines.append("=" * w)

    return "\n".join(lines)


def format_next_phase(plan: Dict[str, Any]) -> str:
    """Format only the next actionable phase for quick reference."""
    lines: List[str] = []
    pa = plan["phase_analysis"]

    lines.append("=" * 60)
    lines.append("NEXT ACTIONABLE PHASE")
    lines.append("=" * 60)

    # If there are overdue phases, the next action is to resolve them
    if pa["overdue_phases"]:
        lines.append("")
        lines.append("OVERDUE PHASES MUST BE RESOLVED FIRST:")
        for p in pa["overdue_phases"]:
            days = p.get("days_overdue", 0)
            tag = f" ({days}d overdue)" if days else " (ongoing)"
            lines.append(f"  [!!] {p['phase']}: {p['description']}{tag}")

    if pa["current_phase"]:
        cp = pa["current_phase"]
        lines.append("")
        lines.append(f"CURRENT TARGET: {cp['phase']}")
        lines.append(f"  Description: {cp['description']}")
        lines.append(f"  Target date: {cp['target_date']} ({cp['days_until']} days)")

    # First two next actions
    lines.append("")
    lines.append("IMMEDIATE ACTIONS:")
    for action in plan["next_actions"][:3]:
        marker = _severity_marker(action["priority"])
        lines.append(f"  {marker} {action['action']}")
        if action.get("command"):
            lines.append(f"      $ {action['command']}")

    lines.append("")
    tl = plan["timeline"]
    lines.append(
        f"Network: {tl['nodes_live']}/{PIONEER_COUNT} live "
        f"| Completion est: {tl['estimated_completion']} "
        f"| Coherence: {tl['coherence_current']}"
    )
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 -- 144-Pioneer Maintenance Planner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python maintenance_planner.py              # Summary report\n"
            "  python maintenance_planner.py --verbose     # Detailed breakdown\n"
            "  python maintenance_planner.py --json        # JSON output\n"
            "  python maintenance_planner.py --next-phase  # Next phase only\n"
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include per-node and per-group breakdown",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--next-phase", "-n",
        action="store_true",
        help="Show only the next actionable phase",
    )
    args = parser.parse_args()

    plan = build_plan(verbose=args.verbose)

    if args.json:
        print(json.dumps(plan, indent=2, default=str))
    elif args.next_phase:
        print(format_next_phase(plan))
    else:
        print(format_text(plan, verbose=args.verbose))


if __name__ == "__main__":
    main()
