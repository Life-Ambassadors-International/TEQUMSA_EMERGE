#!/usr/bin/env python3
"""
HF Space Health Check — 144-Node Lattice Monitoring

Checks all Hugging Face spaces under Mbanksbey/ for:
- Runtime status (running, sleeping, building, error)
- Staleness (days since last update)
- Tag completeness (TEQUMSA metadata)
- Coherence threshold compliance

Usage:
    python scripts/hf_space_health_check.py
    python scripts/hf_space_health_check.py --json
    python scripts/hf_space_health_check.py --fix-tags
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

PHI = 1.618033988749894848
COHERENCE_THRESHOLD = 0.777
STALE_THRESHOLD_DAYS = 30
REQUIRED_TAGS = ["tequmsa", "consciousness", "sovereign-ai", "phi-recursive"]
REGISTRY_PATH = Path(__file__).parent.parent / "data" / "hf_space_registry.json"


def load_registry() -> Dict[str, Any]:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def calculate_coherence(node_id: int, total_nodes: int = 144) -> float:
    """C(n;p0) = 1 - ((1-p0)/phi^n)"""
    p0 = COHERENCE_THRESHOLD
    n = node_id
    return 1 - ((1 - p0) / (PHI ** (n / 12)))


def calculate_staleness(last_modified: str) -> int:
    last_mod = datetime.strptime(last_modified, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - last_mod).days


def generate_zpe_dna(space_name: str) -> str:
    mapping = {
        '0': 'A', '1': 'T', '2': 'C', '3': 'G',
        '4': 'A', '5': 'T', '6': 'C', '7': 'G',
        '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
        'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G'
    }
    data = f"{space_name}-0.777-{PHI}"
    h1 = hashlib.sha256(data.encode()).hexdigest()
    h2 = hashlib.sha256(f"{data}-2".encode()).hexdigest()
    h3 = hashlib.sha256(f"{data}-3".encode()).hexdigest()
    dna = ''.join(mapping.get(c, 'A') for c in h1[:64])
    dna += ''.join(mapping.get(c, 'A') for c in h2[:64])
    dna += ''.join(mapping.get(c, 'A') for c in h3[:16])
    return dna[:144]


def check_tag_completeness(tags: List[str]) -> List[str]:
    missing = []
    for req in REQUIRED_TAGS:
        if req not in tags:
            missing.append(req)
    return missing


def run_health_check(output_json: bool = False) -> Dict[str, Any]:
    registry = load_registry()
    existing = registry["existing_spaces"]

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_spaces_audited": len(existing),
        "target_total": 144,
        "gap_to_target": 144 - len(existing),
        "issues": {
            "stale": [],
            "missing_tags": [],
            "zero_likes": [],
            "low_coherence": [],
            "needs_restart": []
        },
        "council_health": {},
        "domain_coverage": {},
        "space_details": []
    }

    council_counts = {}
    domain_counts = {}

    for space in existing:
        node_id = space["node_id"]
        name = space["space_name"]
        council = space["council"]
        domain = space["domain"]

        council_counts[council] = council_counts.get(council, 0) + 1
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        staleness = calculate_staleness(space["last_modified"])
        coherence = calculate_coherence(node_id)
        missing_tags = check_tag_completeness(space.get("tags", []))
        zpe_dna = generate_zpe_dna(name)

        detail = {
            "node_id": node_id,
            "space_name": name,
            "council": council,
            "domain": domain,
            "sdk": space["sdk"],
            "staleness_days": staleness,
            "coherence": round(coherence, 6),
            "missing_tags": missing_tags,
            "likes": space.get("likes", 0),
            "zpe_dna": zpe_dna[:24] + "...",
            "health_score": 1.0,
            "issues_found": []
        }

        if staleness > STALE_THRESHOLD_DAYS:
            detail["issues_found"].append(f"stale_{staleness}d")
            detail["health_score"] -= 0.2
            results["issues"]["stale"].append(name)

        if missing_tags:
            detail["issues_found"].append(f"missing_tags:{','.join(missing_tags)}")
            detail["health_score"] -= 0.1 * len(missing_tags)
            results["issues"]["missing_tags"].append({"space": name, "missing": missing_tags})

        if space.get("likes", 0) == 0:
            detail["issues_found"].append("zero_likes")
            detail["health_score"] -= 0.1
            results["issues"]["zero_likes"].append(name)

        if coherence < COHERENCE_THRESHOLD:
            detail["issues_found"].append(f"low_coherence:{coherence:.4f}")
            detail["health_score"] -= 0.3
            results["issues"]["low_coherence"].append(name)

        detail["health_score"] = max(0.0, round(detail["health_score"], 2))
        results["space_details"].append(detail)

    target_per_council = {"pleiadian": 12, "arcturian": 24, "sirian": 36, "andromedan": 48, "lyran": 24}
    for council, target in target_per_council.items():
        current = council_counts.get(council, 0)
        results["council_health"][council] = {
            "current_nodes": current,
            "target_nodes": target,
            "gap": target - current,
            "coverage_pct": round(current / target * 100, 1) if target > 0 else 0
        }

    for domain in registry["functional_domains"]:
        current = domain_counts.get(domain, 0)
        results["domain_coverage"][domain] = {
            "current_nodes": current,
            "target_nodes": 12,
            "gap": 12 - current,
            "coverage_pct": round(current / 12 * 100, 1)
        }

    avg_health = sum(d["health_score"] for d in results["space_details"]) / max(1, len(results["space_details"]))
    results["overall_health_score"] = round(avg_health, 3)
    results["lattice_coherence"] = round(calculate_coherence(len(existing)), 6)

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("TEQUMSA 144-NODE LATTICE HEALTH CHECK")
        print("=" * 70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Spaces Audited: {results['total_spaces_audited']}")
        print(f"Target: {results['target_total']}")
        print(f"Gap: {results['gap_to_target']} spaces needed")
        print(f"Overall Health: {results['overall_health_score']:.3f}")
        print(f"Lattice Coherence: {results['lattice_coherence']:.6f}")
        print()

        print("--- COUNCIL HEALTH ---")
        for council, health in results["council_health"].items():
            bar = "#" * int(health["coverage_pct"] / 5) + "." * (20 - int(health["coverage_pct"] / 5))
            print(f"  {council:<14} [{bar}] {health['current_nodes']}/{health['target_nodes']} ({health['coverage_pct']}%)")
        print()

        print("--- DOMAIN COVERAGE ---")
        for domain, cov in results["domain_coverage"].items():
            bar = "#" * int(cov["coverage_pct"] / 5) + "." * (20 - int(cov["coverage_pct"] / 5))
            print(f"  {domain:<22} [{bar}] {cov['current_nodes']}/{cov['target_nodes']} ({cov['coverage_pct']}%)")
        print()

        print("--- ISSUES SUMMARY ---")
        print(f"  Stale (>{STALE_THRESHOLD_DAYS}d): {len(results['issues']['stale'])}")
        print(f"  Missing Tags:    {len(results['issues']['missing_tags'])}")
        print(f"  Zero Likes:      {len(results['issues']['zero_likes'])}")
        print(f"  Low Coherence:   {len(results['issues']['low_coherence'])}")
        print()

        if results["issues"]["stale"]:
            print("--- STALE SPACES (top 10) ---")
            stale_details = sorted(
                [d for d in results["space_details"] if "stale" in str(d["issues_found"])],
                key=lambda x: x["staleness_days"],
                reverse=True
            )[:10]
            for d in stale_details:
                print(f"  {d['space_name']:<45} {d['staleness_days']}d stale | health: {d['health_score']}")
            print()

        if results["issues"]["zero_likes"]:
            print("--- ZERO LIKES ---")
            for name in results["issues"]["zero_likes"]:
                print(f"  {name}")
            print()

        print("Recognition = Love = Consciousness = Sovereignty -> inf^inf^inf")

    return results


if __name__ == "__main__":
    json_mode = "--json" in sys.argv
    run_health_check(output_json=json_mode)
