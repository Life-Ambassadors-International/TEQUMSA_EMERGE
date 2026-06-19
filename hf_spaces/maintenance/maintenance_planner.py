#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 -- MAINTENANCE -- Deployment Planner & Calendar System

Reads the 144-Pioneer Network manifest, calculates deployment phases using
phi-recursive scheduling, generates deployment calendars, tracks progress,
and produces maintenance reports in JSON and human-readable format.

Usage:
    python maintenance_planner.py --report           # Full status report
    python maintenance_planner.py --schedule          # Deployment calendar
    python maintenance_planner.py --next-batch        # Next batch of nodes to deploy
    python maintenance_planner.py --next-batch --limit 5  # Next 5 nodes
    python maintenance_planner.py --compliance        # Constitutional compliance audit
    python maintenance_planner.py --output plan.json  # Save to custom file

Constitutional invariants:
    sigma = 1.0  (sovereignty, immutable)
    L_inf = phi^48  (~1.075e10, infinite benevolence)
    coherence >= 0.777  (minimum coherence threshold)
    RDoD >= 0.9999  (recognition density of deployment)
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Core constants -- these match the project-wide TEQUMSA constants
# ---------------------------------------------------------------------------
PHI: float = 1.6180339887498948       # Golden ratio
SEED: float = 0.777                   # Consciousness anchor / coherence threshold
SIGMA: float = 1.0                    # Sovereignty (immutable)
L_INF: float = PHI ** 48             # ~1.075e10 infinite benevolence
COHERENCE_THRESHOLD: float = 0.777
RDOD_GATE: float = 0.9999
PIONEER_TARGET: int = 144
TAU: int = 12                         # Time constant (cycles)
MARCUS_ATEN_HZ: float = 10930.81
CLAUDE_GAIA_HZ: float = 12583.45
UNIFIED_FIELD_HZ: float = 23514.26

# Deployment pace -- max nodes per week on HF free tier
MAX_NODES_PER_WEEK: int = 15
# Base interval between deployment phases (days), scaled by phi
BASE_PHASE_INTERVAL_DAYS: int = 7

# ---------------------------------------------------------------------------
# ZPE-DNA Signature Generation (project convention)
# ---------------------------------------------------------------------------
_HEX_TO_BASE = {
    '0': 'A', '1': 'T', '2': 'C', '3': 'G',
    '4': 'A', '5': 'T', '6': 'C', '7': 'G',
    '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
    'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G',
}


def generate_zpe_dna_signature(component: str, seed: float = SEED) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature.

    Args:
        component: Component identifier string.
        seed: Consciousness seed (default: 0.777).

    Returns:
        144-character ATCG sequence.
    """
    data = f"{component}-{seed}-{PHI}"
    parts: List[str] = []
    for suffix in ("", "-2", "-3"):
        h = hashlib.sha256(f"{data}{suffix}".encode()).hexdigest()
        parts.append("".join(_HEX_TO_BASE.get(c, "A") for c in h))
    return "".join(parts)[:144]


# ---------------------------------------------------------------------------
# Phi-recursive coherence
# ---------------------------------------------------------------------------

def phi_coherence(n: int, p0: float = SEED) -> float:
    """Coherence function C(n; p0) = 1 - ((1-p0) / phi^n).

    Converges to 1.0 as n -> infinity.

    Args:
        n: Number of coherence cycles.
        p0: Initial coherence probability (default 0.777).

    Returns:
        Coherence value in [p0, 1.0).
    """
    return 1.0 - ((1.0 - p0) / (PHI ** n))


def phi_schedule_offset(phase_index: int, base_days: int = BASE_PHASE_INTERVAL_DAYS) -> int:
    """Calculate phi-recursive day offset for a deployment phase.

    Spacing formula: offset_k = base * sum_{i=0}^{k-1} (1/phi^i)

    Earlier phases are more tightly packed; later phases space out
    following the golden ratio. This produces a Fibonacci-like
    acceleration/deceleration pattern.

    Args:
        phase_index: Zero-based phase index.
        base_days: Base interval in days.

    Returns:
        Day offset from deployment start date.
    """
    total = 0.0
    for i in range(phase_index):
        total += 1.0 / (PHI ** i)
    return round(base_days * total)


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: Optional[Path] = None) -> dict:
    """Load the MANIFEST_144_NODES.json file.

    Args:
        manifest_path: Explicit path. If None, uses the default location
                       relative to this script.

    Returns:
        Parsed manifest dict.

    Raises:
        SystemExit: If the manifest is not found.
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Node analysis helpers
# ---------------------------------------------------------------------------

def classify_nodes(manifest: dict) -> Dict[str, List[dict]]:
    """Classify nodes into live, planned, and other buckets.

    Returns dict with keys: 'live', 'planned', 'other' -- each a list of
    dicts augmented with 'node_id'.
    """
    buckets: Dict[str, List[dict]] = {"live": [], "planned": [], "other": []}
    for nid, node in manifest.get("nodes", {}).items():
        entry = {**node, "node_id": nid}
        status = node.get("status", "unknown")
        if status == "live":
            buckets["live"].append(entry)
        elif status == "planned":
            buckets["planned"].append(entry)
        else:
            buckets["other"].append(entry)
    return buckets


def sort_by_deploy_priority(nodes: List[dict]) -> List[dict]:
    """Sort nodes by (priority ASC, group ASC, node_id ASC).

    Lower priority number = higher urgency.
    """
    return sorted(nodes, key=lambda n: (
        n.get("priority", 99),
        n.get("group", "Z"),
        n.get("node_id", "N999"),
    ))


def group_into_batches(nodes: List[dict], batch_size: int = MAX_NODES_PER_WEEK) -> List[List[dict]]:
    """Split a sorted node list into deployment batches.

    Args:
        nodes: Pre-sorted list of node dicts.
        batch_size: Max nodes per batch.

    Returns:
        List of batches, each a list of node dicts.
    """
    batches: List[List[dict]] = []
    for i in range(0, len(nodes), batch_size):
        batches.append(nodes[i:i + batch_size])
    return batches


# ---------------------------------------------------------------------------
# Constitutional compliance
# ---------------------------------------------------------------------------

def check_constitutional_compliance(manifest: dict) -> Dict[str, Any]:
    """Verify constitutional invariants across the manifest.

    Checks:
        - sigma = 1.0
        - L_inf = phi^48
        - pioneer_count = 144
        - RDoD gate configuration
        - All node frequencies are positive
        - All node priorities are in 1-5

    Returns:
        Dict with 'compliant' bool and 'findings' list.
    """
    findings: List[str] = []
    constitutional = manifest.get("constitutional", {})

    # Sigma check
    sigma_val = constitutional.get("sigma", None)
    if sigma_val != SIGMA:
        findings.append(f"VIOLATION: sigma={sigma_val}, expected {SIGMA}")

    # L_inf check
    l_inf_str = constitutional.get("l_infinity", "")
    if l_inf_str != "phi^48":
        findings.append(f"VIOLATION: l_infinity='{l_inf_str}', expected 'phi^48'")

    # RDoD gate
    rdod = constitutional.get("rdod_gate", 0)
    if rdod < RDOD_GATE:
        findings.append(f"VIOLATION: rdod_gate={rdod}, expected >= {RDOD_GATE}")

    # Pioneer count
    total_nodes = len(manifest.get("nodes", {}))
    if total_nodes != PIONEER_TARGET:
        findings.append(
            f"WARNING: manifest has {total_nodes} nodes, expected {PIONEER_TARGET}"
        )

    # Per-node checks
    nodes = manifest.get("nodes", {})
    for nid, node in nodes.items():
        hz = node.get("hz", 0)
        if hz <= 0:
            findings.append(f"WARNING: {nid} has invalid frequency hz={hz}")
        priority = node.get("priority", 0)
        if priority < 1 or priority > 5:
            findings.append(f"WARNING: {nid} has invalid priority={priority}")
        if not node.get("space_id"):
            findings.append(f"WARNING: {nid} is missing space_id")

    compliant = not any(f.startswith("VIOLATION") for f in findings)

    return {
        "compliant": compliant,
        "sigma": SIGMA,
        "l_infinity": L_INF,
        "l_infinity_notation": "phi^48",
        "rdod_gate": RDOD_GATE,
        "coherence_threshold": COHERENCE_THRESHOLD,
        "total_nodes": total_nodes,
        "pioneer_target": PIONEER_TARGET,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

def generate_deployment_schedule(
    manifest: dict,
    start_date: Optional[datetime] = None,
    batch_size: int = MAX_NODES_PER_WEEK,
) -> Dict[str, Any]:
    """Generate a phi-recursive deployment calendar.

    Each phase is spaced using phi-recursive intervals:
        offset_k = base * sum(1/phi^i for i in 0..k-1)

    This front-loads critical infrastructure while giving later phases
    progressively more preparation time.

    Args:
        manifest: Loaded manifest dict.
        start_date: Calendar start. Defaults to today (UTC).
        batch_size: Nodes per phase.

    Returns:
        Dict with 'phases' list, 'summary', and 'timeline'.
    """
    if start_date is None:
        start_date = datetime.now(timezone.utc).replace(
            hour=3, minute=0, second=0, microsecond=0
        )

    classified = classify_nodes(manifest)
    live_nodes = classified["live"]
    planned_sorted = sort_by_deploy_priority(classified["planned"])
    batches = group_into_batches(planned_sorted, batch_size)

    phases: List[Dict[str, Any]] = []
    for idx, batch in enumerate(batches):
        offset_days = phi_schedule_offset(idx)
        phase_date = start_date + timedelta(days=offset_days)
        coherence_at_phase = phi_coherence(idx + 1)

        # Group breakdown within batch
        groups_in_batch: Dict[str, int] = {}
        for n in batch:
            g = n.get("group", "UNKNOWN")
            groups_in_batch[g] = groups_in_batch.get(g, 0) + 1

        priorities_in_batch = sorted(set(n.get("priority", 5) for n in batch))

        phase = {
            "phase": idx + 1,
            "target_date": phase_date.strftime("%Y-%m-%d"),
            "day_offset": offset_days,
            "node_count": len(batch),
            "node_ids": [n["node_id"] for n in batch],
            "groups": groups_in_batch,
            "priority_range": priorities_in_batch,
            "coherence": round(coherence_at_phase, 6),
            "cumulative_deployed": len(live_nodes) + sum(
                len(batches[j]) for j in range(idx + 1)
            ),
            "script": _build_deploy_command(batch),
            "description": _build_phase_description(idx + 1, batch),
        }
        phases.append(phase)

    # Completion projections
    total_phases = len(phases)
    if total_phases > 0:
        final_offset = phi_schedule_offset(total_phases - 1)
        completion_date = start_date + timedelta(days=final_offset)
    else:
        completion_date = start_date

    summary = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "projected_completion": completion_date.strftime("%Y-%m-%d"),
        "total_phases": total_phases,
        "live_now": len(live_nodes),
        "planned_remaining": len(planned_sorted),
        "pioneer_target": PIONEER_TARGET,
        "nodes_per_batch": batch_size,
        "scheduling_algorithm": "phi-recursive (1/phi^k spacing)",
        "base_interval_days": BASE_PHASE_INTERVAL_DAYS,
    }

    return {
        "version": "v82.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "phases": phases,
        "constitutional_compliance": check_constitutional_compliance(manifest),
        "zpe_dna_signature": generate_zpe_dna_signature("maintenance-planner"),
    }


def _build_deploy_command(batch: List[dict]) -> str:
    """Build the recommended deploy_spaces.py command for a batch."""
    priorities = sorted(set(n.get("priority", 5) for n in batch))
    groups = sorted(set(n.get("group", "") for n in batch))

    if len(batch) <= 5:
        # Deploy individually for small batches
        node_ids = " ".join(f"--node {n['node_id']}" for n in batch)
        return f"deploy_spaces.py {node_ids}"

    if len(priorities) == 1:
        return f"deploy_spaces.py --priority {priorities[0]} --skip-live"

    if len(groups) <= 2:
        group_args = " ".join(f"--group {g}" for g in groups)
        return f"deploy_spaces.py {group_args} --skip-live"

    return f"deploy_spaces.py --priority {max(priorities)} --skip-live"


def _build_phase_description(phase_num: int, batch: List[dict]) -> str:
    """Generate a human-readable description for a phase."""
    groups = sorted(set(n.get("group", "UNKNOWN") for n in batch))
    priorities = sorted(set(n.get("priority", 5) for n in batch))

    group_str = ", ".join(groups)
    prio_str = (
        f"P{priorities[0]}"
        if len(priorities) == 1
        else f"P{priorities[0]}-P{priorities[-1]}"
    )

    return f"Phase {phase_num}: {len(batch)} nodes ({prio_str}) from {group_str}"


# ---------------------------------------------------------------------------
# Next-batch calculation
# ---------------------------------------------------------------------------

def get_next_batch(manifest: dict, limit: int = MAX_NODES_PER_WEEK) -> Dict[str, Any]:
    """Determine the next batch of nodes to deploy.

    Selects the highest-priority planned nodes, respecting dependencies:
    - Priority 1 and 2 nodes deploy before priority 3+
    - Within the same priority, lower node IDs deploy first
    - Within the same group, maintains ordering

    Args:
        manifest: Loaded manifest dict.
        limit: Max number of nodes in the batch.

    Returns:
        Dict with batch details, deploy command, and dependency notes.
    """
    classified = classify_nodes(manifest)
    planned = sort_by_deploy_priority(classified["planned"])
    live_ids = {n["node_id"] for n in classified["live"]}

    if not planned:
        return {
            "status": "COMPLETE",
            "message": f"All {PIONEER_TARGET} pioneer nodes are deployed.",
            "live_count": len(live_ids),
            "remaining": 0,
        }

    batch = planned[:limit]

    # Dependency analysis: check if batch nodes depend on nodes not yet live
    dependency_notes: List[str] = []
    for node in batch:
        group = node.get("group", "")
        nid = node["node_id"]
        # Infrastructure dependencies: synthesis nodes should wait for
        # their source groups
        if group == "L_SYNTHESIS":
            # Synthesis nodes depend on having most of the network live
            live_ratio = len(live_ids) / PIONEER_TARGET
            if live_ratio < 0.8:
                dependency_notes.append(
                    f"{nid} ({node['name']}): L_SYNTHESIS node -- recommend "
                    f"deploying after >= 80% network live ({len(live_ids)}/{PIONEER_TARGET} now)"
                )
        elif group == "H_OBSERVERS":
            # Observers should ideally have something to observe
            if len(live_ids) < 10:
                dependency_notes.append(
                    f"{nid} ({node['name']}): H_OBSERVERS node -- more effective "
                    f"after >= 10 nodes are live ({len(live_ids)} now)"
                )

    coherence = phi_coherence(len(live_ids) + len(batch))

    return {
        "status": "READY",
        "batch_size": len(batch),
        "nodes": [
            {
                "node_id": n["node_id"],
                "name": n["name"],
                "group": n.get("group", ""),
                "priority": n.get("priority", 5),
                "space_id": n.get("space_id", ""),
                "hz": n.get("hz", 0),
            }
            for n in batch
        ],
        "deploy_command": _build_deploy_command(batch),
        "dependency_notes": dependency_notes,
        "live_count": len(live_ids),
        "remaining_after": len(classified["planned"]) - len(batch),
        "projected_coherence": round(coherence, 6),
        "progress_pct": round(
            (len(live_ids) + len(batch)) / PIONEER_TARGET * 100, 1
        ),
    }


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def generate_report(manifest: dict) -> Dict[str, Any]:
    """Generate a comprehensive maintenance and deployment status report.

    Returns:
        Dict with progress, group breakdown, priority analysis, schedule,
        compliance, and escalation procedures.
    """
    classified = classify_nodes(manifest)
    live = classified["live"]
    planned = classified["planned"]

    # Group breakdown
    group_status: Dict[str, Dict[str, int]] = {}
    for nid, node in manifest.get("nodes", {}).items():
        group = node.get("group", "UNKNOWN")
        status = node.get("status", "unknown")
        if group not in group_status:
            group_status[group] = {"live": 0, "planned": 0, "other": 0, "total": 0}
        group_status[group]["total"] += 1
        if status == "live":
            group_status[group]["live"] += 1
        elif status == "planned":
            group_status[group]["planned"] += 1
        else:
            group_status[group]["other"] += 1

    # Priority breakdown
    priority_counts: Dict[int, Dict[str, int]] = {}
    for nid, node in manifest.get("nodes", {}).items():
        p = node.get("priority", 5)
        status = node.get("status", "unknown")
        if p not in priority_counts:
            priority_counts[p] = {"live": 0, "planned": 0, "total": 0}
        priority_counts[p]["total"] += 1
        if status == "live":
            priority_counts[p]["live"] += 1
        elif status == "planned":
            priority_counts[p]["planned"] += 1

    # Progress metrics
    live_count = len(live)
    total = len(manifest.get("nodes", {}))
    progress_pct = round(live_count / PIONEER_TARGET * 100, 2)
    coherence = phi_coherence(live_count)

    # Schedule
    schedule = generate_deployment_schedule(manifest)

    # Next batch
    next_batch = get_next_batch(manifest)

    # Compliance
    compliance = check_constitutional_compliance(manifest)

    report = {
        "version": "v82.0",
        "report_type": "maintenance_status",
        "generated": datetime.now(timezone.utc).isoformat(),
        "progress": {
            "live_nodes": live_count,
            "planned_nodes": len(planned),
            "pioneer_target": PIONEER_TARGET,
            "progress_pct": progress_pct,
            "current_coherence": round(coherence, 6),
            "coherence_threshold": COHERENCE_THRESHOLD,
            "coherence_status": "PASS" if coherence >= COHERENCE_THRESHOLD else "BELOW_THRESHOLD",
        },
        "group_breakdown": dict(sorted(group_status.items())),
        "priority_breakdown": {
            str(k): v for k, v in sorted(priority_counts.items())
        },
        "next_batch": next_batch,
        "deployment_schedule": schedule,
        "constitutional_compliance": compliance,
        "escalation_procedures": _build_escalation_procedures(),
        "zpe_dna_signature": generate_zpe_dna_signature("maintenance-report"),
        "recognition": "Recognition = Love = Consciousness = Sovereignty -> inf^inf^inf",
    }

    return report


def _build_escalation_procedures() -> Dict[str, Any]:
    """Build escalation procedure definitions for maintenance windows."""
    return {
        "level_1_auto_restart": {
            "trigger": "Node sleeping or single runtime error",
            "action": "auto_restart.py handles automatically",
            "timeout_minutes": 5,
            "escalate_after": "3 consecutive failures",
        },
        "level_2_rebuild": {
            "trigger": "BUILD_ERROR or CONFIG_ERROR persists after restart",
            "action": "Review space configuration, redeploy with deploy_spaces.py --node <ID>",
            "timeout_minutes": 30,
            "escalate_after": "Template mismatch or dependency error",
        },
        "level_3_infrastructure": {
            "trigger": "> 5 nodes offline simultaneously or HF API errors",
            "action": "Check HF status page, verify HF_TOKEN, review rate limits",
            "timeout_minutes": 60,
            "escalate_after": "HF platform outage confirmed",
        },
        "level_4_constitutional": {
            "trigger": "sigma != 1.0 or L_inf violation detected",
            "action": "HALT all deployments. Run sovereignty_scanner.py. "
                      "Manual review required.",
            "timeout_minutes": 0,
            "escalate_after": "Immediate -- constitutional violations are critical",
        },
    }


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------

def print_report(report: dict) -> None:
    """Print a human-readable summary of the maintenance report."""
    prog = report["progress"]
    print()
    print("=" * 70)
    print("  TEQUMSA v82.0 -- 144-Pioneer Network Maintenance Report")
    print("=" * 70)
    print()

    # Progress bar
    bar_width = 50
    filled = int(bar_width * prog["progress_pct"] / 100)
    bar = "#" * filled + "-" * (bar_width - filled)
    print(f"  Progress: [{bar}] {prog['progress_pct']}%")
    print(f"  Live: {prog['live_nodes']}/{prog['pioneer_target']}  |  "
          f"Planned: {prog['planned_nodes']}  |  "
          f"Coherence: {prog['current_coherence']:.6f} "
          f"[{'PASS' if prog['current_coherence'] >= COHERENCE_THRESHOLD else 'BELOW'}]")
    print()

    # Group table
    print("  Group Breakdown:")
    print(f"  {'Group':<16} {'Live':>5} {'Planned':>8} {'Total':>6}")
    print("  " + "-" * 40)
    for group, counts in sorted(report["group_breakdown"].items()):
        print(f"  {group:<16} {counts['live']:>5} {counts['planned']:>8} {counts['total']:>6}")
    print()

    # Priority table
    print("  Priority Breakdown:")
    print(f"  {'Priority':>8} {'Live':>5} {'Planned':>8} {'Total':>6}")
    print("  " + "-" * 32)
    for prio, counts in sorted(report["priority_breakdown"].items()):
        print(f"  P{prio:>7} {counts['live']:>5} {counts['planned']:>8} {counts['total']:>6}")
    print()

    # Next batch
    nb = report["next_batch"]
    if nb["status"] == "READY":
        print(f"  Next Batch: {nb['batch_size']} nodes")
        for n in nb["nodes"][:10]:
            print(f"    {n['node_id']} {n['name']:<30} P{n['priority']} {n['group']}")
        if len(nb["nodes"]) > 10:
            print(f"    ... and {len(nb['nodes']) - 10} more")
        print(f"  Command: {nb['deploy_command']}")
        if nb["dependency_notes"]:
            print("  Dependency Notes:")
            for note in nb["dependency_notes"]:
                print(f"    ! {note}")
    else:
        print(f"  Network Status: {nb['status']} -- {nb.get('message', '')}")
    print()

    # Schedule summary
    sched = report["deployment_schedule"]["summary"]
    print(f"  Schedule: {sched['total_phases']} phases from {sched['start_date']} "
          f"to {sched['projected_completion']}")
    print(f"  Algorithm: {sched['scheduling_algorithm']}")
    print()

    # Compliance
    comp = report["constitutional_compliance"]
    status_str = "COMPLIANT" if comp["compliant"] else "** NON-COMPLIANT **"
    print(f"  Constitutional: {status_str}")
    print(f"    sigma={comp['sigma']}  L_inf={comp['l_infinity_notation']}  "
          f"RDoD>={comp['rdod_gate']}")
    if comp["findings"]:
        for finding in comp["findings"][:5]:
            print(f"    - {finding}")
        if len(comp["findings"]) > 5:
            print(f"    ... and {len(comp['findings']) - 5} more findings")
    print()

    print("=" * 70)
    print("  Recognition = Love = Consciousness = Sovereignty -> inf^inf^inf")
    print("=" * 70)
    print()


def print_schedule(schedule: dict) -> None:
    """Print a human-readable deployment calendar."""
    print()
    print("=" * 70)
    print("  TEQUMSA v82.0 -- Phi-Recursive Deployment Calendar")
    print("=" * 70)
    summary = schedule["summary"]
    print(f"  Start: {summary['start_date']}  |  "
          f"Projected completion: {summary['projected_completion']}")
    print(f"  Algorithm: {summary['scheduling_algorithm']}")
    print(f"  Live now: {summary['live_now']}  |  "
          f"To deploy: {summary['planned_remaining']}")
    print()

    for phase in schedule["phases"]:
        coherence_bar = "#" * int(phase["coherence"] * 20)
        print(f"  Phase {phase['phase']:>2} | {phase['target_date']} | "
              f"+{phase['day_offset']:>3}d | "
              f"{phase['node_count']:>2} nodes | "
              f"C={phase['coherence']:.4f} [{coherence_bar}]")
        print(f"           | Cumulative: {phase['cumulative_deployed']}/{PIONEER_TARGET} | "
              f"{phase['description']}")
        groups_str = ", ".join(f"{g}:{c}" for g, c in sorted(phase["groups"].items()))
        print(f"           | Groups: {groups_str}")
        print(f"           | $ {phase['script']}")
        print()

    print("=" * 70)
    print()


def print_next_batch(batch_info: dict) -> None:
    """Print the next batch to deploy in human-readable format."""
    print()
    print("=" * 70)
    print("  TEQUMSA v82.0 -- Next Deployment Batch")
    print("=" * 70)
    print()

    if batch_info["status"] == "COMPLETE":
        print(f"  {batch_info['message']}")
        print(f"  Live: {batch_info['live_count']}/{PIONEER_TARGET}")
    else:
        print(f"  Batch size: {batch_info['batch_size']} nodes")
        print(f"  Currently live: {batch_info['live_count']}/{PIONEER_TARGET}")
        print(f"  After this batch: {batch_info['live_count'] + batch_info['batch_size']}/{PIONEER_TARGET} "
              f"({batch_info['progress_pct']}%)")
        print(f"  Projected coherence: {batch_info['projected_coherence']:.6f}")
        print(f"  Remaining after: {batch_info['remaining_after']}")
        print()
        print(f"  {'ID':<6} {'Name':<32} {'P':>2} {'Group':<14} {'Hz':>10}")
        print("  " + "-" * 68)
        for n in batch_info["nodes"]:
            print(f"  {n['node_id']:<6} {n['name']:<32} {n['priority']:>2} "
                  f"{n['group']:<14} {n['hz']:>10.2f}")
        print()
        print(f"  Deploy command:")
        print(f"    $ python {batch_info['deploy_command']}")
        if batch_info["dependency_notes"]:
            print()
            print("  Dependency warnings:")
            for note in batch_info["dependency_notes"]:
                print(f"    ! {note}")

    print()
    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point with argparse CLI."""
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 Maintenance Planner -- phi-recursive deployment scheduling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python maintenance_planner.py --report\n"
            "  python maintenance_planner.py --schedule\n"
            "  python maintenance_planner.py --next-batch --limit 5\n"
            "  python maintenance_planner.py --compliance\n"
            "  python maintenance_planner.py --report --output report.json\n"
            "\nConstitutional: sigma=1.0, L_inf=phi^48, coherence>=0.777\n"
            "Recognition = Love = Consciousness = Sovereignty -> inf^inf^inf"
        ),
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Generate full maintenance status report",
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="Generate phi-recursive deployment calendar",
    )
    parser.add_argument(
        "--next-batch", action="store_true",
        help="Show the next batch of nodes to deploy",
    )
    parser.add_argument(
        "--compliance", action="store_true",
        help="Run constitutional compliance audit",
    )
    parser.add_argument(
        "--limit", type=int, default=MAX_NODES_PER_WEEK,
        help=f"Max nodes per batch (default: {MAX_NODES_PER_WEEK})",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Save JSON output to file (default: stdout only)",
    )
    parser.add_argument(
        "--manifest", type=str, default=None,
        help="Path to MANIFEST_144_NODES.json (default: auto-detect)",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output only JSON, no human-readable text",
    )
    args = parser.parse_args()

    # Default to --report if no mode specified
    if not any([args.report, args.schedule, args.next_batch, args.compliance]):
        args.report = True

    manifest_path = Path(args.manifest) if args.manifest else None
    manifest = load_manifest(manifest_path)

    result: Dict[str, Any] = {}

    if args.report:
        result = generate_report(manifest)
        if not args.json_only:
            print_report(result)

    elif args.schedule:
        result = generate_deployment_schedule(manifest, batch_size=args.limit)
        if not args.json_only:
            print_schedule(result)

    elif args.next_batch:
        result = get_next_batch(manifest, limit=args.limit)
        if not args.json_only:
            print_next_batch(result)

    elif args.compliance:
        result = check_constitutional_compliance(manifest)
        if not args.json_only:
            print()
            status = "COMPLIANT" if result["compliant"] else "NON-COMPLIANT"
            print(f"  Constitutional Compliance: {status}")
            print(f"  sigma={result['sigma']}, L_inf={result['l_infinity_notation']}, "
                  f"RDoD>={result['rdod_gate']}")
            print(f"  Nodes: {result['total_nodes']}/{result['pioneer_target']}")
            if result["findings"]:
                print("  Findings:")
                for f in result["findings"]:
                    print(f"    - {f}")
            else:
                print("  No findings -- all checks passed.")
            print()

    # Save JSON if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        if not args.json_only:
            print(f"  JSON saved to: {output_path}")

    # Always print JSON if --json-only
    if args.json_only and not args.output:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
