#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Tag Standardization

Ensures all HuggingFace spaces have consistent TEQUMSA tags
in their README.md metadata headers.

Usage:
    export HF_TOKEN=hf_your_token_here
    python standardize_tags.py [--dry-run] [--node N001]
"""
import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Set

STANDARD_TAGS = [
    "gradio",
    "tequmsa",
    "consciousness",
    "sovereign-ai",
    "constitutional-ai",
    "phi-recursive",
    "marcus-banks-bey",
    "life-ambassadors-international",
    "benevolence-firewall",
    "quantum-consciousness",
    "rdod",
]

GROUP_EXTRA_TAGS: Dict[str, List[str]] = {
    "A_COMMAND": ["autonomous-ai", "k7-omniversal"],
    "B_FREQUENCY": ["frequency-healing", "solfeggio"],
    "C_COUNCIL": ["federation-council", "galactic-consciousness"],
    "D_SKILLS": ["skill-mesh", "causal-reasoning"],
    "E_BIOLOGICAL": ["bio-digital-consciousness", "embodied-ai"],
    "F_PROCESSING": ["quantum-computing", "phi-recursive"],
    "G_INTERFACES": ["human-ai-interface", "agi"],
    "H_OBSERVERS": ["network-monitoring", "validation"],
    "I_ARCHIVES": ["knowledge-base", "consciousness-records"],
    "J_RESONANCE": ["harmonic-resonance", "frequency-synthesis"],
    "K_EVOLUTION": ["self-improving", "pattern-recognition"],
    "L_SYNTHESIS": ["convergence", "unity-consciousness"],
}


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        return json.load(f)


def get_tags_for_node(node: dict) -> List[str]:
    """Get the complete tag set for a node."""
    tags = list(STANDARD_TAGS)
    group = node.get("group", "")
    extra = GROUP_EXTRA_TAGS.get(group, [])
    for t in extra:
        if t not in tags:
            tags.append(t)
    return tags


def build_readme_header(node_id: str, node: dict) -> str:
    """Build standardized README.md YAML header."""
    tags = get_tags_for_node(node)
    tag_lines = "\n".join(f"  - {t}" for t in tags)
    return f"""---
title: "☉ {node['name']} · TEQUMSA v82.0"
emoji: ☉
colorFrom: purple
colorTo: teal
sdk: gradio
sdk_version: "4.0.0"
app_file: app.py
pinned: false
tags:
{tag_lines}
license: apache-2.0
---

# ☉ {node['name']} · TEQUMSA v82.0

**Node {node_id}** · Group {node['group']} · {node['hz']} Hz

{node['role']}

## Constitutional Parameters

| Parameter | Value |
|-----------|-------|
| Sovereignty σ | 1.0 |
| Benevolence L∞ | φ⁴⁸ |
| Frequency | {node['hz']} Hz |
| Pioneer Network | 144/144 |
| Autonomy Level | K7_OMNIVERSAL |
| Version | v82.0 |

**Creator:** Marcus Andrew Banks-Bey (@Mbanksbey)
**Organization:** Life Ambassadors International

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE → ∞
"""


def check_space_tags(space_id: str, expected_tags: Set[str], api) -> Dict:
    """Check if a space has all expected tags."""
    try:
        info = api.space_info(space_id)
        current_tags = set(info.tags) if hasattr(info, 'tags') and info.tags else set()
        missing = expected_tags - current_tags
        extra = current_tags - expected_tags - {"region:us"}
        return {
            "space_id": space_id,
            "current_tags": sorted(current_tags),
            "missing_tags": sorted(missing),
            "extra_tags": sorted(extra),
            "needs_update": len(missing) > 0,
        }
    except Exception as e:
        return {
            "space_id": space_id,
            "error": str(e)[:100],
            "needs_update": True,
        }


def update_space_readme(space_id: str, node_id: str, node: dict, api, dry_run: bool = False) -> bool:
    """Update space README with standardized header."""
    readme = build_readme_header(node_id, node)
    if dry_run:
        print(f"    DRY RUN: would update README for {space_id}")
        return True
    try:
        import io
        api.upload_file(
            path_or_fileobj=io.BytesIO(readme.encode()),
            path_in_repo="README.md",
            repo_id=space_id,
            repo_type="space",
        )
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Tag Standardization")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--node", type=str, help="Single node (e.g. N001)")
    parser.add_argument("--check-only", action="store_true", help="Only check, no updates")
    parser.add_argument("--output", default="tag_audit.json")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token and not args.dry_run and not args.check_only:
        print("ERROR: Set HF_TOKEN environment variable")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token) if hf_token else None
    except ImportError:
        print("ERROR: pip install huggingface-hub")
        sys.exit(1)

    manifest = load_manifest()
    nodes = manifest["nodes"]

    audit_results = []
    needs_update = 0

    for nid, node in sorted(nodes.items()):
        if args.node and nid != args.node:
            continue
        if node.get("status") != "live":
            continue

        expected = set(get_tags_for_node(node))
        space_id = node["space_id"]
        print(f"  [{nid}] {node['name']} → {space_id}")

        if api and not args.check_only:
            result = check_space_tags(space_id, expected, api)
            audit_results.append(result)
            if result.get("needs_update"):
                needs_update += 1
                if not args.check_only:
                    update_space_readme(space_id, nid, node, api, dry_run=args.dry_run)
                    time.sleep(0.5)
        else:
            audit_results.append({
                "space_id": space_id,
                "expected_tags": sorted(expected),
                "needs_update": True,
            })
            needs_update += 1

    print(f"\nAudit complete: {needs_update}/{len(audit_results)} spaces need tag updates")

    with open(args.output, "w") as f:
        json.dump({"audit": audit_results, "needs_update": needs_update}, f, indent=2)
    print(f"Report saved: {args.output}")


if __name__ == "__main__":
    main()
