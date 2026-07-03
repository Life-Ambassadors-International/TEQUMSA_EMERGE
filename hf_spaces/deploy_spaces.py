#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · BULK SPACE DEPLOYMENT SCRIPT
Creates and deploys all 144 Pioneer nodes to HuggingFace.

Usage:
    export HF_TOKEN=hf_your_token_here
    python deploy_spaces.py [--priority 1-5] [--dry-run] [--node N003]
    python deploy_spaces.py --group F_PROCESSING --group G_INTERFACES  # Phase 5

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
    # organism template: try dedicated node file first, fall back to skill template
    if template_type == "organism":
        organism_path = Path(__file__).parent / "nodes" / "N003_TEQUMSA-Core" / "app.py"
        if organism_path.exists():
            return organism_path
        # fall back to skill template
        return templates / "app_skill_node.py"
    mapping = {
        "council_chat": templates / "app_council_node.py",
        "frequency":    templates / "app_frequency_node.py",
        "skill":        templates / "app_skill_node.py",
        "monitor":      templates / "app_monitor_node.py",
        "biological":   templates / "app_skill_node.py",
        "processing":   templates / "app_skill_node.py",
        "interface":    templates / "app_council_node.py",
        "archive":      templates / "app_monitor_node.py",
    }
    path = mapping.get(template_type, templates / "app_skill_node.py")
    # always fall back to skill template if the target doesn't exist
    if not path.exists():
        fallback = templates / "app_skill_node.py"
        print(f"    WARN: template {path} not found, using skill fallback")
        return fallback
    return path


def get_requirements(template_type: str) -> str:
    if template_type in ("council_chat", "interface"):
        return "gradio>=4.0.0\nnumpy>=1.24.0\n"
    elif template_type == "monitor":
        return "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n"
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
| Benevolence L∞ | φ⁸ |
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
) -> bool:
    """Deploy a single node to HuggingFace."""
    space_id = node["space_id"]
    template_type = node.get("template", "skill")

    print(f"  [{node_id}] {node['name']} ({template_type}) → {space_id}")

    if dry_run:
        print(f"    DRY RUN: would create {space_id}")
        return True

    try:
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False,
        )
        time.sleep(0.5)

        tmpl_path = get_template_path(template_type)
        with open(tmpl_path) as f:
            app_code = f.read()

        env_overrides = (
            f"import os\n"
            f"os.environ.setdefault('TEQUMSA_NODE_ID', '{node_id}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_NAME', '{node['name']}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_HZ', '{node['hz']}')\n"
            f"os.environ.setdefault('TEQUMSA_ROLE', '{node['role'][:80]}')\n\n"
        )
        lines = app_code.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("#") or line.strip() == "":
                insert_at = i + 1
            else:
                break
        lines.insert(insert_at, env_overrides)
        final_code = "\n".join(lines)

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
    parser.add_argument("--group", type=str, action="append", dest="groups",
                        help="Deploy all nodes in group (repeatable, e.g. --group F_PROCESSING --group G_INTERFACES)")
    parser.add_argument("--skip-live", action="store_true", help="Skip nodes with status=live")
    # batch-size is accepted for GH Actions compat but handled via time.sleep between nodes
    parser.add_argument("--batch-size", type=int, default=12,
                        help="Nodes per batch with rate-limit pause (default: 12)")
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

    to_deploy: Dict[str, dict] = {}
    for nid, node in nodes.items():
        if args.node and nid != args.node:
            continue
        if args.groups and node.get("group") not in args.groups:
            continue
        if args.skip_live and node.get("status") == "live":
            continue
        if node.get("priority", 5) <= args.priority:
            to_deploy[nid] = node

    print(f"\n☉ TEQUMSA v82.0 · Deployment Plan")
    print(f"   Nodes to deploy: {len(to_deploy)}/{len(nodes)}")
    print(f"   Priority ≤ {args.priority} | Groups: {args.groups or 'all'} | Dry run: {args.dry_run}")
    print("=" * 60)

    success = 0
    failed = 0
    for batch_start in range(0, len(to_deploy), args.batch_size):
        batch = dict(list(sorted(to_deploy.items(),
                                 key=lambda x: (x[1].get("priority", 5), x[0])))[batch_start:batch_start + args.batch_size])
        for nid, node in batch.items():
            ok = deploy_node(nid, node, api, dry_run=args.dry_run)
            if ok:
                success += 1
            else:
                failed += 1
            if not args.dry_run:
                time.sleep(1)
        if not args.dry_run and batch_start + args.batch_size < len(to_deploy):
            print(f"  [batch pause 30s for rate limiting...]")
            time.sleep(30)

    # Save deployment report
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "deployed": success,
        "failed": failed,
        "total_nodes": len(nodes),
        "dry_run": args.dry_run,
    }
    report_path = Path(__file__).parent / "deployment_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("=" * 60)
    print(f"✓ Deployed: {success} | ✗ Failed: {failed}")
    print(f"☉ {success}/{len(nodes)} of 144 Pioneer nodes active")
    print("ETR_NOW. ∞")


if __name__ == "__main__":
    main()
