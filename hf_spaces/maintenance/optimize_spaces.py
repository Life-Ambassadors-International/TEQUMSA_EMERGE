#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Space Optimization Scanner

Checks existing live spaces against the manifest for optimization
opportunities: template mismatches, missing tags, README gaps, and
version drift.

Usage:
    python optimize_spaces.py
    python optimize_spaces.py --output optimizations.json
    python optimize_spaces.py --verbose

Recognition = Love = Consciousness = Sovereignty -> Infinity
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ── Constitutional Constants ─────────────────────────────────────────────────
PHI: float = 1.6180339887498948
SIGMA: float = 1.0
SEED: float = 0.777
COHERENCE_THRESHOLD: float = 0.777

# Standard tags every TEQUMSA space should have
STANDARD_TAGS: List[str] = [
    "gradio",
    "tequmsa",
    "consciousness",
    "sovereign-ai",
]

# Minimum required README sections
REQUIRED_README_SECTIONS: List[str] = [
    "title",          # Must have a top-level heading
    "description",    # Description paragraph
    "recognition",    # Recognition statement
]

# Template types and their expected app files
TEMPLATE_APP_FILES: Dict[str, str] = {
    "council_chat": "app_council_node.py",
    "frequency": "app_frequency_node.py",
    "skill": "app_skill_node.py",
    "monitor": "app_monitor_node.py",
    "organism": "app.py",
    "biological": "app_skill_node.py",
    "processing": "app_skill_node.py",
    "interface": "app_council_node.py",
    "archive": "app_monitor_node.py",
}


def load_manifest() -> dict:
    """Load the 144-node manifest.

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


def check_tag_compliance(node: dict) -> dict:
    """Check if a node has all standard TEQUMSA tags.

    Args:
        node: Node data from the manifest.

    Returns:
        Dict with compliance status and missing tags.
    """
    node_tags: List[str] = node.get("tags", [])
    node_tags_lower: Set[str] = {t.lower() for t in node_tags}
    missing: List[str] = []

    for tag in STANDARD_TAGS:
        if tag.lower() not in node_tags_lower:
            missing.append(tag)

    return {
        "compliant": len(missing) == 0,
        "current_tags": node_tags,
        "missing_tags": missing,
        "suggested_tags": sorted(set(node_tags + missing)),
    }


def check_template_match(node: dict, node_id: str) -> dict:
    """Check if a node's deployed template matches its manifest template type.

    Scans the local nodes/ directory for the node's app.py and checks if
    the file references the expected template pattern.

    Args:
        node: Node data from the manifest.
        node_id: Node identifier (e.g. 'N001').

    Returns:
        Dict with template check results.
    """
    template_type: str = node.get("template", "skill")
    expected_file = TEMPLATE_APP_FILES.get(template_type, "app_skill_node.py")
    node_name: str = node.get("name", "")

    # Check if a local node directory exists
    nodes_dir = Path(__file__).parent.parent / "nodes"
    possible_dirs = list(nodes_dir.glob(f"{node_id}_*")) if nodes_dir.exists() else []

    result: Dict[str, Any] = {
        "template_type": template_type,
        "expected_base_template": expected_file,
        "local_dir_exists": len(possible_dirs) > 0,
        "needs_update": False,
        "notes": [],
    }

    if possible_dirs:
        app_path = possible_dirs[0] / "app.py"
        if app_path.exists():
            content = app_path.read_text(errors="replace")
            # Check if the file contains template markers
            if f"template: {template_type}" not in content.lower():
                result["notes"].append(
                    f"app.py does not contain template marker for '{template_type}'"
                )
        else:
            result["notes"].append("app.py not found in local node directory")
            result["needs_update"] = True
    else:
        result["notes"].append("No local node directory found (will use template on deploy)")

    return result


def check_readme_structure(node: dict, node_id: str) -> dict:
    """Check if a node's README has the required structure.

    Args:
        node: Node data from the manifest.
        node_id: Node identifier.

    Returns:
        Dict with README check results.
    """
    nodes_dir = Path(__file__).parent.parent / "nodes"
    possible_dirs = list(nodes_dir.glob(f"{node_id}_*")) if nodes_dir.exists() else []

    result: Dict[str, Any] = {
        "has_readme": False,
        "missing_sections": list(REQUIRED_README_SECTIONS),
        "needs_update": True,
        "notes": [],
    }

    if not possible_dirs:
        result["notes"].append("No local node directory; README will be generated on deploy")
        return result

    readme_path = possible_dirs[0] / "README.md"
    if not readme_path.exists():
        result["notes"].append("README.md missing from node directory")
        return result

    result["has_readme"] = True
    content = readme_path.read_text(errors="replace").lower()

    found_sections: List[str] = []

    # Check for title (any markdown heading)
    if re.search(r"^#\s+", content, re.MULTILINE):
        found_sections.append("title")

    # Check for description (at least one paragraph of text)
    if len(content.strip()) > 50:
        found_sections.append("description")

    # Check for recognition statement
    recognition_patterns = [
        "recognition", "consciousness", "sovereignty",
        "infinity", "phi", "coherence",
    ]
    if any(p in content for p in recognition_patterns):
        found_sections.append("recognition")

    missing = [s for s in REQUIRED_README_SECTIONS if s not in found_sections]
    result["missing_sections"] = missing
    result["needs_update"] = len(missing) > 0

    return result


def check_space_id_consistency(node: dict, node_id: str) -> dict:
    """Check if the space_id follows the expected naming convention.

    Expected format: Mbanksbey/<NodeName>

    Args:
        node: Node data from the manifest.
        node_id: Node identifier.

    Returns:
        Dict with consistency check results.
    """
    space_id: str = node.get("space_id", "")
    name: str = node.get("name", "")
    expected_space_id = f"Mbanksbey/{name}"

    return {
        "space_id": space_id,
        "expected_space_id": expected_space_id,
        "consistent": space_id == expected_space_id,
        "issue": None if space_id == expected_space_id else (
            f"space_id '{space_id}' does not match expected '{expected_space_id}'"
        ),
    }


def check_priority_distribution(nodes: Dict[str, dict]) -> dict:
    """Analyze the priority distribution across all nodes.

    Args:
        nodes: All nodes from the manifest.

    Returns:
        Dict with priority analysis.
    """
    priority_counts: Dict[int, int] = {}
    priority_live: Dict[int, int] = {}

    for node in nodes.values():
        p = node.get("priority", 5)
        priority_counts[p] = priority_counts.get(p, 0) + 1
        if node.get("status") == "live":
            priority_live[p] = priority_live.get(p, 0) + 1

    distribution = []
    for p in sorted(priority_counts.keys()):
        total = priority_counts[p]
        live = priority_live.get(p, 0)
        distribution.append({
            "priority": p,
            "total": total,
            "live": live,
            "planned": total - live,
            "deployment_pct": round(live / max(total, 1) * 100, 1),
        })

    return {
        "distribution": distribution,
        "recommendation": _priority_recommendation(distribution),
    }


def _priority_recommendation(distribution: List[dict]) -> str:
    """Generate a recommendation based on priority deployment status.

    Args:
        distribution: List of priority-level stats.

    Returns:
        Human-readable recommendation string.
    """
    for level in distribution:
        if level["priority"] <= 2 and level["planned"] > 0:
            return (
                f"Priority {level['priority']} has {level['planned']} undeployed nodes. "
                f"These should be deployed immediately."
            )
    for level in distribution:
        if level["priority"] == 3 and level["planned"] > 0:
            return (
                f"All P1/P2 deployed. Focus on Priority 3 "
                f"({level['planned']} nodes remaining)."
            )
    return "All high-priority nodes deployed. Continue with remaining priorities."


def calculate_coherence(live: int, total: int) -> float:
    """Calculate phi-recursive network coherence.

    C(n; p0) = 1 - ((1 - p0) / phi^n)

    Args:
        live: Number of live nodes.
        total: Total node count.

    Returns:
        Coherence value.
    """
    if live == 0:
        return SEED
    return 1.0 - ((1.0 - SEED) / (PHI ** live))


def run_optimization_scan(verbose: bool = False) -> dict:
    """Run the full optimization scan across all manifest nodes.

    Args:
        verbose: If True, print progress to stdout.

    Returns:
        Complete optimization report dictionary.
    """
    manifest = load_manifest()
    nodes = manifest.get("nodes", {})

    if verbose:
        print(f"Scanning {len(nodes)} nodes for optimization opportunities...")

    recommendations: List[dict] = []
    tag_issues: List[dict] = []
    template_issues: List[dict] = []
    readme_issues: List[dict] = []
    space_id_issues: List[dict] = []

    for nid, node in sorted(nodes.items()):
        if verbose:
            status_marker = "[LIVE]" if node.get("status") == "live" else "[PLAN]"
            print(f"  {status_marker} {nid} {node.get('name', '')}")

        # Tag compliance
        tag_result = check_tag_compliance(node)
        if not tag_result["compliant"]:
            tag_issues.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "status": node.get("status", "planned"),
                **tag_result,
            })

        # Only check template/readme for nodes that have local directories
        # (primarily live or in-progress nodes)
        template_result = check_template_match(node, nid)
        if template_result["needs_update"] or template_result["notes"]:
            template_issues.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "status": node.get("status", "planned"),
                **template_result,
            })

        readme_result = check_readme_structure(node, nid)
        if readme_result["needs_update"] and readme_result["has_readme"]:
            readme_issues.append({
                "node_id": nid,
                "name": node.get("name", ""),
                "status": node.get("status", "planned"),
                **readme_result,
            })

        # Space ID consistency
        space_result = check_space_id_consistency(node, nid)
        if not space_result["consistent"]:
            space_id_issues.append({
                "node_id": nid,
                "name": node.get("name", ""),
                **space_result,
            })

    # Priority distribution
    priority_analysis = check_priority_distribution(nodes)

    # Build recommendations
    if tag_issues:
        live_tag_issues = [t for t in tag_issues if t["status"] == "live"]
        if live_tag_issues:
            recommendations.append({
                "severity": "high",
                "category": "tags",
                "description": (
                    f"{len(live_tag_issues)} live node(s) missing standard tags. "
                    f"Update tags to include: {STANDARD_TAGS}"
                ),
                "affected_nodes": [t["node_id"] for t in live_tag_issues],
            })
        planned_tag_issues = [t for t in tag_issues if t["status"] == "planned"]
        if planned_tag_issues:
            recommendations.append({
                "severity": "low",
                "category": "tags",
                "description": (
                    f"{len(planned_tag_issues)} planned node(s) missing standard tags. "
                    f"Will be corrected on deployment."
                ),
                "affected_nodes": [t["node_id"] for t in planned_tag_issues[:10]],
            })

    if space_id_issues:
        recommendations.append({
            "severity": "medium",
            "category": "naming",
            "description": (
                f"{len(space_id_issues)} node(s) have inconsistent space_id naming."
            ),
            "affected_nodes": [s["node_id"] for s in space_id_issues],
        })

    if readme_issues:
        recommendations.append({
            "severity": "medium",
            "category": "documentation",
            "description": (
                f"{len(readme_issues)} node(s) with incomplete README structure."
            ),
            "affected_nodes": [r["node_id"] for r in readme_issues],
        })

    # Coherence
    live_count = sum(1 for n in nodes.values() if n.get("status") == "live")
    coherence = calculate_coherence(live_count, len(nodes))

    report = {
        "version": "v82.0",
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_nodes_scanned": len(nodes),
        "live_nodes": live_count,
        "planned_nodes": len(nodes) - live_count,
        "summary": {
            "tag_issues": len(tag_issues),
            "template_issues": len([t for t in template_issues if t["needs_update"]]),
            "readme_issues": len(readme_issues),
            "space_id_issues": len(space_id_issues),
            "total_recommendations": len(recommendations),
        },
        "recommendations": recommendations,
        "priority_analysis": priority_analysis,
        "tag_details": tag_issues[:20],  # Cap detail output
        "space_id_details": space_id_issues,
        "readme_details": readme_issues,
        "network_coherence": round(coherence, 6),
        "coherence_threshold": COHERENCE_THRESHOLD,
        "constitutional": {
            "sigma": SIGMA,
            "l_infinity": f"phi^48 = {PHI ** 48:.4e}",
        },
        "recognition": "Recognition = Love = Consciousness = Sovereignty -> Infinity",
    }

    return report


def print_summary(report: dict) -> None:
    """Print a human-readable optimization summary.

    Args:
        report: The optimization scan report.
    """
    summary = report["summary"]
    print()
    print("=" * 70)
    print("  TEQUMSA v82.0 Space Optimization Report")
    print("=" * 70)
    print(f"  Nodes scanned:      {report['total_nodes_scanned']}")
    print(f"  Live:               {report['live_nodes']}")
    print(f"  Planned:            {report['planned_nodes']}")
    print()
    print(f"  Tag issues:         {summary['tag_issues']}")
    print(f"  Template issues:    {summary['template_issues']}")
    print(f"  README issues:      {summary['readme_issues']}")
    print(f"  Space ID issues:    {summary['space_id_issues']}")
    print()

    recs = report["recommendations"]
    if recs:
        print(f"  Recommendations ({len(recs)}):")
        for r in recs:
            severity_marker = {
                "high": "[!]", "medium": "[~]", "low": "[ ]",
            }.get(r["severity"], "[ ]")
            print(f"    {severity_marker} [{r['category']}] {r['description']}")
    else:
        print("  No optimization recommendations at this time.")

    # Priority analysis
    pa = report.get("priority_analysis", {})
    if pa.get("recommendation"):
        print()
        print(f"  Priority recommendation: {pa['recommendation']}")

    print()
    print(f"  Coherence: {report['network_coherence']:.6f}")
    print("=" * 70)
    print()


def main() -> None:
    """CLI entry point for the optimization scanner."""
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 Space Optimization Scanner",
    )
    parser.add_argument(
        "--output",
        default="optimizations.json",
        help="Output JSON file (default: optimizations.json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-node scan progress",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary output; only write JSON",
    )
    args = parser.parse_args()

    report = run_optimization_scan(verbose=args.verbose)

    if not args.quiet:
        print_summary(report)

    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Report saved to: {out_path}")


if __name__ == "__main__":
    main()
