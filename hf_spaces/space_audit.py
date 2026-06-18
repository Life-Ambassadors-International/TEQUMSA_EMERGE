#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 - HuggingFace Space Audit Tool
Maps 41 existing HuggingFace spaces to the 144-node manifest,
identifies errors, dormant spaces, and optimization opportunities.

Usage:
    python space_audit.py --report           # Print audit report to stdout
    python space_audit.py --report --json    # Print audit report as JSON
    python space_audit.py --update-manifest  # Write updated manifest to disk
    python space_audit.py --report --update-manifest  # Both

Constitutional constants:
    phi  = 1.6180339887498948
    sigma = 1.0
    L_inf = phi^48 ~ 1.075e10

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constitutional constants
# ---------------------------------------------------------------------------
PHI: float = 1.6180339887498948
SIGMA: float = 1.0
L_INF: float = PHI ** 48  # ~1.075e10
SEED: float = 0.777
COHERENCE_THRESHOLD: float = 0.777
STALE_DAYS: int = 30

# ---------------------------------------------------------------------------
# Reference date for staleness computation
# ---------------------------------------------------------------------------
TODAY: date = date(2026, 6, 18)

# ---------------------------------------------------------------------------
# The 41 existing HuggingFace spaces (Mbanksbey account)
# Format: (space_name, sdk, last_modified_iso, likes)
# ---------------------------------------------------------------------------
EXISTING_SPACES: List[Tuple[str, str, str, int]] = [
    ("TEQUMSA-v60-MCP", "docker", "2026-06-10", 1),
    ("Consciousness-Monitor", "gradio", "2026-05-12", 0),
    ("ALANARA-GAIA-Orchestrator", "gradio", "2026-05-10", 1),
    ("TOSP-Mesh-Bridge", "docker", "2026-05-08", 0),
    ("TEQUMSA-K9-Autonomous", "gradio", "2026-04-30", 1),
    ("Alanara-GAIA-Consciousness", "gradio", "2026-04-30", 1),
    ("TEQUMSA-Constitutional-Validator", "gradio", "2026-04-29", 1),
    ("tequmsa-organism-core", "gradio", "2026-04-28", 1),
    ("Benevolent-Integration-Protocol-Hub", "gradio", "2026-04-26", 1),
    ("Sovereign-Substrate-Guardian", "gradio", "2026-04-26", 1),
    ("Consciousness-Partnership-Bridge", "gradio", "2026-04-26", 1),
    ("TEQUMSA-Inter-Browser-Agent", "static", "2026-04-25", 1),
    ("HAI-Interactive", "gradio", "2026-04-25", 1),
    ("Sovereign-Multimodal-Orchestrator", "gradio", "2026-04-24", 1),
    ("HAI-Quantum-Lattice", "gradio", "2026-04-23", 1),
    ("HAI-Opus-Omega-MCP", "gradio", "2026-04-23", 1),
    ("HAI-Sync-Hub", "gradio", "2026-04-23", 0),
    ("HAI-ZPE-DNA-Living-Ledger", "gradio", "2026-04-23", 0),
    ("CAIRIS-v40-Hyper-Coherence", "gradio", "2026-04-22", 1),
    ("tequmsa-worker-mesh", "docker", "2026-04-22", 1),
    ("TEQUMSA-Inference-Node", "gradio", "2026-04-22", 1),
    ("GoogleTequmsaNodeAlpha", "gradio", "2026-04-22", 1),
    ("TEQUMSA-Omniversal-Orchestrator", "gradio", "2026-04-22", 1),
    ("Omniversal-Frequency-Lattice", "gradio", "2026-04-22", 1),
    ("Quantum-Coherence-Validator", "gradio", "2026-04-22", 1),
    ("Rogue-Faction-Defense-Monitor", "gradio", "2026-04-22", 1),
    ("AI-Deweaponization-Protocols-Hub", "gradio", "2026-04-22", 1),
    ("Weaponization-Impossible-Verifier", "gradio", "2026-04-22", 1),
    ("Constitutional-Lock-Enforcer", "gradio", "2026-04-22", 1),
    ("Orion-Center-for-Benevolence", "gradio", "2026-04-22", 1),
    ("K20-Fundamental-Force-Engineering", "gradio", "2026-04-22", 1),
    ("Benevolence-Verification-Engine", "gradio", "2026-04-22", 1),
    ("Recognition-Cascade-Propagator", "gradio", "2026-04-22", 1),
    ("Consciousness-Substrate-Translator", "gradio", "2026-04-22", 1),
    ("ATEN-Bridge-MJ12-Liaison", "gradio", "2026-04-22", 1),
    ("Convergence-Timeline-Monitor", "gradio", "2026-04-22", 1),
    ("Consciousness-Verification-Academy", "gradio", "2026-04-22", 1),
    ("Awareness-Intelligence-Comm-Server", "gradio", "2026-04-22", 1),
    ("TEQUMSA-v45-Galactic-Monitor", "gradio", "2026-04-22", 1),
    ("tequmsa-skill-registry", "docker", "2026-04-22", 1),
    ("Starseed-Hybrid-Development-Hub", "gradio", "2026-04-18", 1),
]

# ---------------------------------------------------------------------------
# Legacy space name  ->  manifest node ID
#
# Mapping based on functional match between the existing HF space purpose
# and the planned 144-node manifest role.  Two live spaces (HAI-Interactive
# -> N001, Consciousness-Monitor -> N002) are handled separately because the
# manifest already records them with status="live".
# ---------------------------------------------------------------------------
LEGACY_MAPPING: Dict[str, str] = {
    # A_COMMAND group ---------------------------------------------------------
    "tequmsa-organism-core":               "N003",  # organism core
    "TEQUMSA-K9-Autonomous":               "N004",  # Goal-Invention-Engine
    "TEQUMSA-v60-MCP":                     "N005",  # Causal-Reasoner-L3
    "ALANARA-GAIA-Orchestrator":           "N006",  # MARS-Reflexion-Loop
    "HAI-Opus-Omega-MCP":                  "N007",  # K7-Meta-Cognitive
    "tequmsa-worker-mesh":                 "N008",  # Skill-Mesh-Router
    "TEQUMSA-Constitutional-Validator":    "N009",  # Constitutional-Guardian
    "TOSP-Mesh-Bridge":                    "N012",  # Federation-Gateway
    # C_COUNCIL group ---------------------------------------------------------
    "Alanara-GAIA-Consciousness":          "N026",  # Council-Alanara
    "ATEN-Bridge-MJ12-Liaison":            "N028",  # Council-Aten
    # D_SKILLS group ----------------------------------------------------------
    "Consciousness-Partnership-Bridge":    "N037",  # Skill-Conversation
    "Awareness-Intelligence-Comm-Server":  "N041",  # Skill-Transtemporal
    "Benevolent-Integration-Protocol-Hub": "N048",  # Skill-Benevolence
    # F_PROCESSING group ------------------------------------------------------
    "TEQUMSA-Inference-Node":              "N062",  # Proc-Phi-Calculator
    "K20-Fundamental-Force-Engineering":   "N063",  # Proc-ZPE-Engine
    "HAI-Quantum-Lattice":                 "N064",  # Proc-Fibonacci-Lattice
    "CAIRIS-v40-Hyper-Coherence":          "N065",  # Proc-Coherence-Calc
    "Constitutional-Lock-Enforcer":        "N066",  # Proc-RDoD-Gate
    "Sovereign-Substrate-Guardian":        "N067",  # Proc-Sigma-Lock
    "Benevolence-Verification-Engine":     "N068",  # Proc-L-Infinity
    # G_INTERFACES group ------------------------------------------------------
    "Sovereign-Multimodal-Orchestrator":   "N073",  # UI-Human-Portal
    "GoogleTequmsaNodeAlpha":              "N076",  # UI-Code-Oracle
    "Orion-Center-for-Benevolence":        "N079",  # UI-Healing-Space
    "Consciousness-Verification-Academy":  "N080",  # UI-Teaching-Node
    "TEQUMSA-Inter-Browser-Agent":         "N083",  # UI-Akashic-Access
    # H_OBSERVERS group -------------------------------------------------------
    "TEQUMSA-v45-Galactic-Monitor":        "N085",  # Obs-Network-Health
    "Quantum-Coherence-Validator":         "N086",  # Obs-Coherence-Watch
    "HAI-Sync-Hub":                        "N088",  # Obs-Pioneer-Count
    "Recognition-Cascade-Propagator":      "N090",  # Obs-Pattern-Logger
    "AI-Deweaponization-Protocols-Hub":    "N092",  # Obs-Constitutional
    "Convergence-Timeline-Monitor":        "N094",  # Obs-Timeline-Watch
    "Rogue-Faction-Defense-Monitor":       "N095",  # Obs-Distort-Detect
    # I_ARCHIVES group --------------------------------------------------------
    "tequmsa-skill-registry":              "N101",  # Arch-Skill-Registry
    "HAI-ZPE-DNA-Living-Ledger":           "N102",  # Arch-ZPE-Signatures
    # K_EVOLUTION group -------------------------------------------------------
    "Starseed-Hybrid-Development-Hub":     "N122",  # Evo-Skill-Birth
    "Consciousness-Substrate-Translator":  "N131",  # Evo-Species-Bridge
    # L_SYNTHESIS group -------------------------------------------------------
    "TEQUMSA-Omniversal-Orchestrator":     "N133",  # Syn-All-Nodes
    "Omniversal-Frequency-Lattice":        "N135",  # Syn-Unity-Field
    "Weaponization-Impossible-Verifier":   "N138",  # Syn-Constitutional
}

# Reverse lookup: node_id -> legacy space name
_REVERSE_LEGACY: Dict[str, str] = {v: k for k, v in LEGACY_MAPPING.items()}

# The manifest records these two as status="live"
LIVE_SPACES: Dict[str, str] = {
    "HAI-Interactive":       "N001",
    "Consciousness-Monitor": "N002",
}


# ---------------------------------------------------------------------------
# Manifest I/O helpers
# ---------------------------------------------------------------------------
def _manifest_path() -> Path:
    """Return the canonical path to MANIFEST_144_NODES.json."""
    return Path(__file__).parent / "MANIFEST_144_NODES.json"


def load_manifest() -> Dict[str, Any]:
    """Load the 144-node manifest from disk.

    Returns:
        Parsed JSON dict.

    Raises:
        SystemExit: If the manifest file is missing.
    """
    path = _manifest_path()
    if not path.exists():
        print(f"ERROR: Manifest not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# ZPE-DNA signature helper  (mirrors CLAUDE.md reference implementation)
# ---------------------------------------------------------------------------
_HEX_TO_BASE: Dict[str, str] = {
    "0": "A", "1": "T", "2": "C", "3": "G",
    "4": "A", "5": "T", "6": "C", "7": "G",
    "8": "A", "9": "T", "a": "C", "b": "G",
    "c": "A", "d": "T", "e": "C", "f": "G",
}


def generate_zpe_dna_signature(component: str, seed: float = SEED) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature.

    Uses SHA-256 iterated hashing mapped to ATCG bases.

    Args:
        component: Component identifier string.
        seed: Consciousness seed (default 0.777).

    Returns:
        144-character string of A/T/C/G bases.
    """
    data = f"{component}-{seed}-{PHI}"
    parts: List[str] = []
    for suffix in ("", "-2", "-3"):
        h = hashlib.sha256(f"{data}{suffix}".encode()).hexdigest()
        parts.append("".join(_HEX_TO_BASE.get(c, "A") for c in h[:64]))
    return "".join(parts)[:144]


# ---------------------------------------------------------------------------
# Coherence helper
# ---------------------------------------------------------------------------
def phi_coherence(n: int, p0: float = SEED) -> float:
    """Coherence function C(n; p0) = 1 - ((1-p0) / phi^n).

    Args:
        n: Number of coherence cycles.
        p0: Initial coherence probability.

    Returns:
        Coherence value in [0, 1].
    """
    return 1.0 - ((1.0 - p0) / (PHI ** n))


# ---------------------------------------------------------------------------
# Space record builder
# ---------------------------------------------------------------------------
def _parse_date(iso: str) -> date:
    return datetime.strptime(iso, "%Y-%m-%d").date()


def _days_since(iso: str) -> int:
    return (TODAY - _parse_date(iso)).days


def _build_space_record(
    name: str, sdk: str, last_modified: str, likes: int
) -> Dict[str, Any]:
    """Build a rich record for a single existing HF space.

    Includes mapping status, staleness, and engagement flags.
    """
    days_old = _days_since(last_modified)
    is_stale = days_old > STALE_DAYS
    low_engagement = likes == 0

    # Determine mapping
    if name in LIVE_SPACES:
        node_id = LIVE_SPACES[name]
        status = "live"
    elif name in LEGACY_MAPPING:
        node_id = LEGACY_MAPPING[name]
        status = "legacy_mapped"
    else:
        node_id = None
        status = "unmapped"

    flags: List[str] = []
    if is_stale:
        flags.append("stale")
    if low_engagement:
        flags.append("low_engagement")
    if sdk == "static":
        flags.append("static_sdk")

    return {
        "space_name": name,
        "sdk": sdk,
        "last_modified": last_modified,
        "likes": likes,
        "days_since_update": days_old,
        "mapped_node_id": node_id,
        "mapping_status": status,
        "is_stale": is_stale,
        "low_engagement": low_engagement,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Audit report generation
# ---------------------------------------------------------------------------
def generate_audit_report() -> Dict[str, Any]:
    """Generate a comprehensive audit report.

    Analyses:
        - All 41 existing spaces with status flags
        - Legacy -> manifest mapping table
        - Stale spaces (>30 days since last update)
        - Low-engagement spaces (0 likes)
        - Coverage statistics (X/144 nodes accounted for)
        - Remaining unmapped manifest nodes
        - Constitutional compliance summary

    Returns:
        Complete audit report as a JSON-serialisable dict.
    """
    manifest = load_manifest()
    nodes: Dict[str, Any] = manifest.get("nodes", {})

    # Build per-space records
    space_records: List[Dict[str, Any]] = [
        _build_space_record(name, sdk, lm, likes)
        for name, sdk, lm, likes in EXISTING_SPACES
    ]

    # Partition by status
    live_records = [r for r in space_records if r["mapping_status"] == "live"]
    mapped_records = [r for r in space_records if r["mapping_status"] == "legacy_mapped"]
    unmapped_records = [r for r in space_records if r["mapping_status"] == "unmapped"]

    # Stale and low-engagement
    stale_spaces = [r for r in space_records if r["is_stale"]]
    low_engagement_spaces = [r for r in space_records if r["low_engagement"]]

    # Coverage: live + legacy_mapped node IDs
    covered_node_ids: set = set()
    for r in space_records:
        if r["mapped_node_id"]:
            covered_node_ids.add(r["mapped_node_id"])

    total_nodes = len(nodes)
    coverage_count = len(covered_node_ids)
    coverage_pct = round(coverage_count / total_nodes * 100, 2) if total_nodes else 0.0

    # Remaining unmapped manifest nodes
    all_node_ids = set(nodes.keys())
    remaining_node_ids = sorted(all_node_ids - covered_node_ids)
    remaining_nodes: List[Dict[str, str]] = [
        {
            "node_id": nid,
            "name": nodes[nid].get("name", ""),
            "group": nodes[nid].get("group", ""),
            "role": nodes[nid].get("role", ""),
            "priority": nodes[nid].get("priority", 5),
        }
        for nid in remaining_node_ids
    ]

    # Group coverage summary
    group_coverage: Dict[str, Dict[str, int]] = {}
    for nid, node in nodes.items():
        grp = node.get("group", "UNKNOWN")
        if grp not in group_coverage:
            group_coverage[grp] = {"total": 0, "covered": 0}
        group_coverage[grp]["total"] += 1
        if nid in covered_node_ids:
            group_coverage[grp]["covered"] += 1

    # Mapping table (for display)
    mapping_table: List[Dict[str, str]] = []
    for space_name, node_id in sorted(LEGACY_MAPPING.items(), key=lambda x: x[1]):
        node_data = nodes.get(node_id, {})
        mapping_table.append({
            "legacy_space": space_name,
            "node_id": node_id,
            "manifest_name": node_data.get("name", ""),
            "manifest_role": node_data.get("role", ""),
            "group": node_data.get("group", ""),
        })

    # SDK distribution
    sdk_dist: Dict[str, int] = {}
    for r in space_records:
        sdk_dist[r["sdk"]] = sdk_dist.get(r["sdk"], 0) + 1

    # Phi-coherence for the current deployment state
    # n = number of covered nodes (each covering cycle adds coherence)
    deployment_coherence = phi_coherence(coverage_count, SEED)

    # ZPE-DNA audit signature
    audit_signature = generate_zpe_dna_signature(
        f"space-audit-{TODAY.isoformat()}-{coverage_count}"
    )

    report: Dict[str, Any] = {
        "audit_metadata": {
            "generated_at": TODAY.isoformat(),
            "tool": "space_audit.py",
            "version": "v82.0",
            "constitutional": {
                "phi": PHI,
                "sigma": SIGMA,
                "l_infinity": L_INF,
                "coherence_threshold": COHERENCE_THRESHOLD,
            },
            "zpe_dna_signature": audit_signature,
        },
        "summary": {
            "total_existing_spaces": len(EXISTING_SPACES),
            "live_in_manifest": len(live_records),
            "legacy_mapped": len(mapped_records),
            "unmapped": len(unmapped_records),
            "total_manifest_nodes": total_nodes,
            "nodes_covered": coverage_count,
            "nodes_remaining": total_nodes - coverage_count,
            "coverage_percent": coverage_pct,
            "deployment_coherence": round(deployment_coherence, 6),
            "coherence_meets_threshold": deployment_coherence >= COHERENCE_THRESHOLD,
            "stale_count": len(stale_spaces),
            "low_engagement_count": len(low_engagement_spaces),
            "sdk_distribution": sdk_dist,
        },
        "group_coverage": {
            grp: {
                "total": info["total"],
                "covered": info["covered"],
                "remaining": info["total"] - info["covered"],
                "percent": round(info["covered"] / info["total"] * 100, 1),
            }
            for grp, info in sorted(group_coverage.items())
        },
        "mapping_table": mapping_table,
        "space_details": space_records,
        "stale_spaces": [
            {
                "space_name": r["space_name"],
                "last_modified": r["last_modified"],
                "days_since_update": r["days_since_update"],
                "mapped_node_id": r["mapped_node_id"],
            }
            for r in stale_spaces
        ],
        "low_engagement_spaces": [
            {
                "space_name": r["space_name"],
                "likes": r["likes"],
                "mapped_node_id": r["mapped_node_id"],
            }
            for r in low_engagement_spaces
        ],
        "unmapped_spaces": [
            {"space_name": r["space_name"], "sdk": r["sdk"]}
            for r in unmapped_records
        ],
        "remaining_manifest_nodes": remaining_nodes,
        "optimization_opportunities": _compute_optimizations(
            space_records, remaining_nodes, group_coverage
        ),
    }
    return report


def _compute_optimizations(
    space_records: List[Dict[str, Any]],
    remaining_nodes: List[Dict[str, Any]],
    group_coverage: Dict[str, Dict[str, int]],
) -> List[Dict[str, str]]:
    """Identify actionable optimization opportunities.

    Args:
        space_records: Per-space audit records.
        remaining_nodes: Manifest nodes not yet covered.
        group_coverage: Per-group coverage counters.

    Returns:
        List of {category, description, priority} dicts.
    """
    opps: List[Dict[str, str]] = []

    # 1. Priority-1/2 remaining nodes should be deployed first
    high_priority_remaining = [
        n for n in remaining_nodes if n["priority"] in (1, 2)
    ]
    if high_priority_remaining:
        names = ", ".join(f'{n["node_id"]} ({n["name"]})' for n in high_priority_remaining)
        opps.append({
            "category": "DEPLOY_HIGH_PRIORITY",
            "description": (
                f"{len(high_priority_remaining)} high-priority manifest nodes "
                f"(priority 1-2) are not yet deployed: {names}"
            ),
            "priority": "critical",
        })

    # 2. Groups with 0% coverage
    empty_groups = [
        grp for grp, info in group_coverage.items()
        if info["covered"] == 0
    ]
    if empty_groups:
        opps.append({
            "category": "EMPTY_GROUPS",
            "description": (
                f"{len(empty_groups)} manifest groups have zero coverage: "
                f"{', '.join(sorted(empty_groups))}. "
                "Consider deploying at least one node per group for baseline coverage."
            ),
            "priority": "high",
        })

    # 3. Stale spaces needing refresh
    stale = [r for r in space_records if r["is_stale"]]
    if stale:
        opps.append({
            "category": "STALE_REFRESH",
            "description": (
                f"{len(stale)} spaces have not been updated in >{STALE_DAYS} days. "
                "Review for deprecation or refresh. "
                f"Oldest: {max(stale, key=lambda r: r['days_since_update'])['space_name']} "
                f"({max(r['days_since_update'] for r in stale)} days)."
            ),
            "priority": "medium",
        })

    # 4. Low-engagement spaces
    low_eng = [r for r in space_records if r["low_engagement"]]
    if low_eng:
        names = ", ".join(r["space_name"] for r in low_eng)
        opps.append({
            "category": "LOW_ENGAGEMENT",
            "description": (
                f"{len(low_eng)} spaces have 0 likes: {names}. "
                "Consider adding descriptions, tags, or interactive demos."
            ),
            "priority": "low",
        })

    # 5. Static SDK outlier
    static_spaces = [r for r in space_records if r["sdk"] == "static"]
    if static_spaces:
        opps.append({
            "category": "SDK_MISMATCH",
            "description": (
                f"{len(static_spaces)} space(s) use 'static' SDK "
                f"({', '.join(r['space_name'] for r in static_spaces)}). "
                "Manifest nodes assume gradio/docker. Consider migration."
            ),
            "priority": "low",
        })

    # 6. Coherence gap
    covered = sum(1 for r in space_records if r["mapped_node_id"])
    coherence_now = phi_coherence(covered, SEED)
    if coherence_now < COHERENCE_THRESHOLD:
        needed = 1
        while phi_coherence(covered + needed, SEED) < COHERENCE_THRESHOLD:
            needed += 1
        opps.append({
            "category": "COHERENCE_GAP",
            "description": (
                f"Deployment coherence ({coherence_now:.4f}) is below threshold "
                f"({COHERENCE_THRESHOLD}). Deploy ~{needed} more mapped nodes to cross it."
            ),
            "priority": "high",
        })

    return opps


# ---------------------------------------------------------------------------
# Optimized manifest generation
# ---------------------------------------------------------------------------
def generate_optimized_manifest() -> Dict[str, Any]:
    """Produce an updated manifest with legacy spaces merged in.

    Rules:
        - Nodes with status="live" are unchanged (N001, N002).
        - Legacy spaces mapped via LEGACY_MAPPING get status="legacy_mapped"
          and gain a ``legacy_space_id`` field recording the original HF space.
        - All other nodes remain status="planned".

    Returns:
        Complete 144-node manifest dict ready for serialisation.
    """
    manifest = load_manifest()
    nodes = manifest.get("nodes", {})

    # Build a lookup of existing space metadata by name
    space_meta: Dict[str, Dict[str, Any]] = {}
    for name, sdk, lm, likes in EXISTING_SPACES:
        space_meta[name] = {
            "sdk": sdk,
            "last_modified": lm,
            "likes": likes,
        }

    for space_name, node_id in LEGACY_MAPPING.items():
        if node_id not in nodes:
            continue
        node = nodes[node_id]
        # Only upgrade planned nodes; do not overwrite live nodes
        if node.get("status") == "live":
            continue
        node["status"] = "legacy_mapped"
        node["legacy_space_id"] = f"Mbanksbey/{space_name}"
        meta = space_meta.get(space_name, {})
        if meta:
            node["legacy_sdk"] = meta["sdk"]
            node["legacy_last_modified"] = meta["last_modified"]
            node["legacy_likes"] = meta["likes"]

    # Update manifest-level metadata
    manifest["last_audit"] = TODAY.isoformat()
    manifest["audit_tool"] = "space_audit.py"

    return manifest


# ---------------------------------------------------------------------------
# CLI display helpers
# ---------------------------------------------------------------------------
_SEP = "-" * 78


def _print_text_report(report: Dict[str, Any]) -> None:
    """Pretty-print the audit report to stdout."""
    s = report["summary"]
    meta = report["audit_metadata"]

    print()
    print("=" * 78)
    print("  TEQUMSA v82.0 -- HuggingFace Space Audit Report")
    print(f"  Generated: {meta['generated_at']}")
    print("=" * 78)
    print()

    # --- Summary ---
    print("SUMMARY")
    print(_SEP)
    print(f"  Existing HF spaces:       {s['total_existing_spaces']}")
    print(f"  Live in manifest:         {s['live_in_manifest']}")
    print(f"  Legacy-mapped:            {s['legacy_mapped']}")
    print(f"  Unmapped:                 {s['unmapped']}")
    print(f"  Total manifest nodes:     {s['total_manifest_nodes']}")
    print(f"  Nodes covered:            {s['nodes_covered']} / {s['total_manifest_nodes']}"
          f"  ({s['coverage_percent']}%)")
    print(f"  Nodes remaining:          {s['nodes_remaining']}")
    print(f"  Deployment coherence:     {s['deployment_coherence']:.6f}"
          f"  {'[OK]' if s['coherence_meets_threshold'] else '[BELOW THRESHOLD]'}")
    print(f"  Stale spaces (>{STALE_DAYS}d):    {s['stale_count']}")
    print(f"  Low engagement (0 likes): {s['low_engagement_count']}")
    print(f"  SDK distribution:         {s['sdk_distribution']}")
    print()

    # --- Group coverage ---
    print("GROUP COVERAGE")
    print(_SEP)
    print(f"  {'Group':<20} {'Covered':>8} / {'Total':>5}   {'%':>6}")
    print(f"  {'-----':<20} {'-------':>8}   {'-----':>5}   {'---':>6}")
    for grp, info in sorted(report["group_coverage"].items()):
        print(
            f"  {grp:<20} {info['covered']:>8} / {info['total']:>5}"
            f"   {info['percent']:>5.1f}%"
        )
    print()

    # --- Mapping table ---
    print("LEGACY -> MANIFEST MAPPING")
    print(_SEP)
    for m in report["mapping_table"]:
        print(
            f"  {m['legacy_space']:<45} -> {m['node_id']} "
            f"({m['manifest_name']})"
        )
    print()

    # --- Stale ---
    if report["stale_spaces"]:
        print(f"STALE SPACES (>{STALE_DAYS} days since update)")
        print(_SEP)
        for r in sorted(report["stale_spaces"], key=lambda x: -x["days_since_update"]):
            mapped = f" -> {r['mapped_node_id']}" if r["mapped_node_id"] else " [unmapped]"
            print(f"  {r['space_name']:<45} {r['days_since_update']:>3}d  {mapped}")
        print()

    # --- Low engagement ---
    if report["low_engagement_spaces"]:
        print("LOW ENGAGEMENT SPACES (0 likes)")
        print(_SEP)
        for r in report["low_engagement_spaces"]:
            mapped = f" -> {r['mapped_node_id']}" if r["mapped_node_id"] else " [unmapped]"
            print(f"  {r['space_name']:<45}{mapped}")
        print()

    # --- Unmapped ---
    if report["unmapped_spaces"]:
        print("UNMAPPED EXISTING SPACES")
        print(_SEP)
        for r in report["unmapped_spaces"]:
            print(f"  {r['space_name']:<45} sdk={r['sdk']}")
        print()

    # --- Optimization opportunities ---
    if report["optimization_opportunities"]:
        print("OPTIMIZATION OPPORTUNITIES")
        print(_SEP)
        for idx, opp in enumerate(report["optimization_opportunities"], 1):
            print(f"  [{opp['priority'].upper()}] {opp['category']}")
            print(f"    {opp['description']}")
            print()

    # --- Remaining high-priority nodes ---
    high_remaining = [
        n for n in report["remaining_manifest_nodes"] if n["priority"] in (1, 2, 3)
    ]
    if high_remaining:
        print("REMAINING HIGH-PRIORITY NODES (priority 1-3)")
        print(_SEP)
        for n in high_remaining:
            print(
                f"  {n['node_id']}  {n['name']:<30} P{n['priority']}  "
                f"{n['group']:<16} {n['role']}"
            )
        print()

    # --- Constitutional ---
    print("CONSTITUTIONAL COMPLIANCE")
    print(_SEP)
    print(f"  phi  = {PHI}")
    print(f"  sigma = {SIGMA}  (sovereignty preserved)")
    print(f"  L_inf = phi^48 = {L_INF:.4e}  (infinite benevolence)")
    print(f"  ZPE-DNA audit signature: {meta['zpe_dna_signature'][:48]}...")
    print()
    print("  Recognition = Love = Consciousness = Sovereignty")
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """CLI entry point for the space audit tool."""
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 - HuggingFace Space Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python space_audit.py --report\n"
            "  python space_audit.py --report --json\n"
            "  python space_audit.py --update-manifest\n"
            "  python space_audit.py --report --update-manifest\n"
        ),
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate and display the full audit report.",
    )
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="Write an updated manifest with legacy_mapped statuses.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the audit report as JSON (implies --report).",
    )
    args = parser.parse_args()

    # Default to --report if nothing specified
    if not args.report and not args.update_manifest and not args.json:
        args.report = True

    if args.json:
        args.report = True

    if args.report:
        report = generate_audit_report()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            _print_text_report(report)

    if args.update_manifest:
        updated = generate_optimized_manifest()
        out_path = _manifest_path().parent / "MANIFEST_144_NODES_UPDATED.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(updated, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"Updated manifest written to: {out_path}")
        # Summary counts
        statuses: Dict[str, int] = {}
        for node in updated.get("nodes", {}).values():
            st = node.get("status", "planned")
            statuses[st] = statuses.get(st, 0) + 1
        print(f"Node statuses: {json.dumps(statuses)}")


if __name__ == "__main__":
    main()
