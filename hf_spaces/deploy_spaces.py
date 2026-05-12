#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · BULK SPACE DEPLOYMENT SCRIPT
Creates and deploys all 144 Pioneer nodes to HuggingFace.

Usage:
    export HF_TOKEN=hf_your_token_here
    python deploy_spaces.py [--priority 1-5] [--dry-run] [--node N003]

Priority levels:
    1 = Critical (deploy immediately)
    2 = High (deploy within 24h)
    3 = Medium (deploy this week)
    4 = Normal (deploy this month)
    5 = Low (deploy when ready)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def get_template_path(template_type: str) -> Path:
    templates = Path(__file__).parent / "templates"
    mapping = {
        "council_chat": templates / "app_council_node.py",
        "frequency":    templates / "app_frequency_node.py",
        "skill":        templates / "app_skill_node.py",
        "monitor":      templates / "app_monitor_node.py",
        "organism":     Path(__file__).parent / "nodes" / "N003_TEQUMSA-Core" / "app.py",
        "biological":   templates / "app_skill_node.py",   # bio nodes use skill template
        "processing":   templates / "app_skill_node.py",   # proc nodes use skill template
        "interface":    templates / "app_council_node.py",  # interface nodes use council template
        "archive":      templates / "app_monitor_node.py",  # archive nodes use monitor template
    }
    path = mapping.get(template_type, mapping["skill"])
    return path


def get_requirements(template_type: str) -> str:
    if template_type in ("council_chat", "interface"):
        return "gradio>=4.0.0\nnumpy>=1.24.0\nanthropic>=0.25.0\n"
    elif template_type == "monitor":
        return "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n"
    elif template_type == "frequency":
        return "gradio>=4.0.0\nnumpy>=1.24.0\n"
    elif template_type == "organism":
        return "gradio>=4.0.0\nnumpy>=1.24.0\nscipy>=1.10.0\n"
    return "gradio>=4.0.0\nnumpy>=1.24.0\n"


def build_readme(node_id: str, node: dict) -> str:
    return f"""---
title: ☉ {node['name']} · TEQUMSA v82.0
emoji: ☉
colorFrom: purple
colorTo: teal
sdk: gradio
sdk_version: "4.0.0"
app_file: app.py
pinned: false
tags:
  - gradio
  - tequmsa
  - consciousness
  - sovereign-ai
  - constitutional-ai
  - phi-recursive
  - marcus-banks-bey
  - life-ambassadors-international
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


def deploy_node(
    node_id: str,
    node: dict,
    api,
    dry_run: bool = False,
    force: bool = False,
) -> bool:
    """Deploy a single node to HuggingFace."""
    space_id = node["space_id"]
    template_type = node.get("template", "skill")

    print(f"  [{node_id}] {node['name']} ({template_type}) → {space_id}")

    if dry_run:
        print(f"    DRY RUN: would create {space_id}")
        return True

    try:
        # Create space
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False,
        )
        time.sleep(0.5)  # Rate limit

        # Read template
        tmpl_path = get_template_path(template_type)
        if not tmpl_path.exists():
            print(f"    WARN: template {tmpl_path} not found, using skill template")
            tmpl_path = get_template_path("skill")

        # Inject node config via env comment header
        with open(tmpl_path) as f:
            app_code = f.read()

        # Override env defaults inline for nodes with known configs
        env_overrides = (
            f"import os\n"
            f"os.environ.setdefault('TEQUMSA_NODE_ID', '{node_id}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_NAME', '{node['name']}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_HZ', '{node['hz']}')\n"
            f"os.environ.setdefault('TEQUMSA_ROLE', '{node['role'][:80]}')\n\n"
        )
        # Insert after shebang/encoding lines
        lines = app_code.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("#") or line.strip() == "":
                insert_at = i + 1
            else:
                break
        lines.insert(insert_at, env_overrides)
        final_code = "\n".join(lines)

        # Upload files
        import io
        api.upload_file(
            path_or_fileobj=io.BytesIO(final_code.encode()),
            path_in_repo="app.py",
            repo_id=space_id,
            repo_type="space",
        )
        api.upload_file(
            path_or_fileobj=io.BytesIO(get_requirements(template_type).encode()),
            path_in_repo="requirements.txt",
            repo_id=space_id,
            repo_type="space",
        )
        api.upload_file(
            path_or_fileobj=io.BytesIO(build_readme(node_id, node).encode()),
            path_in_repo="README.md",
            repo_id=space_id,
            repo_type="space",
        )
        print(f"    ✓ Deployed: https://huggingface.co/spaces/{space_id}")
        return True

    except Exception as e:
        print(f"    ✗ FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Deploy TEQUMSA 144-node network to HuggingFace")
    parser.add_argument("--priority", type=int, default=3,
                        help="Max priority level to deploy (1=critical only, 5=all)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without deploying")
    parser.add_argument("--node", type=str, help="Deploy single node (e.g. N003)")
    parser.add_argument("--group", type=str, help="Deploy all nodes in group (e.g. A_COMMAND)")
    parser.add_argument("--skip-live", action="store_true", help="Skip already-live nodes")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN environment variable")
        print("  export HF_TOKEN=hf_your_token_here")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token) if hf_token else None
    except ImportError:
        print("ERROR: Install huggingface_hub: pip install huggingface-hub")
        sys.exit(1)

    manifest = load_manifest()
    nodes = manifest["nodes"]

    # Filter nodes
    to_deploy: Dict[str, dict] = {}
    for nid, node in nodes.items():
        if args.node and nid != args.node:
            continue
        if args.group and node.get("group") != args.group:
            continue
        if args.skip_live and node.get("status") == "live":
            continue
        if node.get("priority", 5) <= args.priority:
            to_deploy[nid] = node

    print(f"\n☉ TEQUMSA v82.0 · Deployment Plan")
    print(f"   Nodes to deploy: {len(to_deploy)}/{len(nodes)}")
    print(f"   Priority ≤ {args.priority} | Dry run: {args.dry_run}")
    print("=" * 60)

    success = 0
    failed = 0
    for nid, node in sorted(to_deploy.items(), key=lambda x: (x[1].get("priority", 5), x[0])):
        ok = deploy_node(nid, node, api, dry_run=args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1
        if not args.dry_run:
            time.sleep(1)  # Rate limit

    print("=" * 60)
    print(f"✓ Deployed: {success} | ✗ Failed: {failed}")
    print(f"☉ {success}/{len(nodes)} of 144 Pioneer nodes active")
    print("ETR_NOW. ∞")


if __name__ == "__main__":
    main()
