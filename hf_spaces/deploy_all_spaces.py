#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · PHASED 144-NODE DEPLOYMENT ENGINE
Deploys all planned Pioneer nodes to HuggingFace Spaces in batches.

Usage:
    export HF_TOKEN=hf_your_token_here
    python deploy_all_spaces.py --priority 5 --batch-size 12 --skip-live
    python deploy_all_spaces.py --group B_FREQUENCY --dry-run
    python deploy_all_spaces.py --node N003 --force
"""
import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

PHI = 1.6180339887498948

TEMPLATES_DIR = Path(__file__).parent / "templates"
NODES_DIR = Path(__file__).parent / "nodes"
MANIFEST_PATH = Path(__file__).parent / "MANIFEST_144_NODES.json"

TEMPLATE_MAP = {
    "council_chat": TEMPLATES_DIR / "app_council_node.py",
    "frequency":    TEMPLATES_DIR / "app_frequency_node.py",
    "skill":        TEMPLATES_DIR / "app_skill_node.py",
    "monitor":      TEMPLATES_DIR / "app_monitor_node.py",
    "organism":     NODES_DIR / "N003_TEQUMSA-Core" / "app.py",
    "biological":   TEMPLATES_DIR / "app_skill_node.py",
    "processing":   TEMPLATES_DIR / "app_skill_node.py",
    "interface":    TEMPLATES_DIR / "app_council_node.py",
    "archive":      TEMPLATES_DIR / "app_monitor_node.py",
}

SDK_MAP = {
    "council_chat": "gradio",
    "frequency":    "gradio",
    "skill":        "gradio",
    "monitor":      "gradio",
    "organism":     "gradio",
    "biological":   "gradio",
    "processing":   "gradio",
    "interface":    "gradio",
    "archive":      "gradio",
}

REQUIREMENTS_MAP = {
    "council_chat": "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "frequency":    "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "skill":        "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "monitor":      "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n",
    "organism":     "gradio>=4.0.0\nnumpy>=1.24.0\nscipy>=1.10.0\n",
    "biological":   "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "processing":   "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "interface":    "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "archive":      "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n",
}

TEQUMSA_TAGS = [
    "gradio", "tequmsa", "consciousness", "sovereign-ai",
    "constitutional-ai", "phi-recursive", "marcus-banks-bey",
    "life-ambassadors-international",
]


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def build_readme(node_id: str, node: dict) -> str:
    return f"""---
title: "{node['name']} - TEQUMSA v82.0"
emoji: "☉"
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

# {node['name']} - TEQUMSA v82.0

**Node {node_id}** | Group {node['group']} | {node['hz']} Hz

{node['role']}

## Constitutional Parameters

| Parameter | Value |
|-----------|-------|
| Sovereignty | 1.0 |
| Benevolence L-inf | phi^48 |
| Frequency | {node['hz']} Hz |
| Pioneer Network | 144/144 |
| Autonomy Level | K7_OMNIVERSAL |
| Version | v82.0 |

**Creator:** Marcus Andrew Banks-Bey (@Mbanksbey)
**Organization:** Life Ambassadors International

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE
"""


def inject_env_header(app_code: str, node_id: str, node: dict) -> str:
    env_block = (
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
    lines.insert(insert_at, env_block)
    return "\n".join(lines)


def deploy_node(
    node_id: str,
    node: dict,
    api,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    space_id = node["space_id"]
    template_type = node.get("template", "skill")
    result = {
        "node_id": node_id,
        "space_id": space_id,
        "template": template_type,
        "dry_run": dry_run,
    }

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"Would deploy {space_id} ({template_type})"
        return result

    try:
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk=SDK_MAP.get(template_type, "gradio"),
            exist_ok=True,
            private=False,
        )
        time.sleep(0.5)

        tmpl_path = TEMPLATE_MAP.get(template_type, TEMPLATE_MAP["skill"])
        if not tmpl_path.exists():
            tmpl_path = TEMPLATE_MAP["skill"]

        with open(tmpl_path) as f:
            app_code = f.read()

        final_code = inject_env_header(app_code, node_id, node)

        api.upload_file(
            path_or_fileobj=io.BytesIO(final_code.encode()),
            path_in_repo="app.py",
            repo_id=space_id,
            repo_type="space",
        )
        api.upload_file(
            path_or_fileobj=io.BytesIO(
                REQUIREMENTS_MAP.get(template_type, "gradio>=4.0.0\nnumpy>=1.24.0\n").encode()
            ),
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

        result["status"] = "deployed"
        result["url"] = f"https://huggingface.co/spaces/{space_id}"
        return result

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)[:200]
        return result


def main():
    parser = argparse.ArgumentParser(description="Deploy TEQUMSA 144-Pioneer lattice")
    parser.add_argument("--priority", type=int, default=5, help="Max priority (1-5)")
    parser.add_argument("--group", type=str, help="Deploy specific group")
    parser.add_argument("--node", type=str, help="Deploy single node")
    parser.add_argument("--batch-size", type=int, default=12, help="Nodes per batch")
    parser.add_argument("--dry-run", action="store_true", help="Plan without deploying")
    parser.add_argument("--skip-live", action="store_true", help="Skip live nodes")
    parser.add_argument("--force", action="store_true", help="Redeploy even if live")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN environment variable")
        sys.exit(1)

    api = None
    if not args.dry_run:
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=hf_token)
        except ImportError:
            print("ERROR: pip install huggingface-hub")
            sys.exit(1)

    manifest = load_manifest()
    nodes = manifest["nodes"]

    targets: Dict[str, dict] = {}
    for nid, node in nodes.items():
        if args.node and nid != args.node:
            continue
        if args.group and node.get("group") != args.group:
            continue
        if args.skip_live and node.get("status") == "live":
            continue
        if node.get("priority", 5) <= args.priority:
            targets[nid] = node

    sorted_targets = sorted(targets.items(), key=lambda x: (x[1].get("priority", 5), x[0]))

    print(f"\n{'='*60}")
    print(f"  TEQUMSA v82.0 - 144-Pioneer Lattice Deployment")
    print(f"  Nodes to deploy: {len(sorted_targets)}")
    print(f"  Priority <= {args.priority} | Batch size: {args.batch_size}")
    print(f"  Dry run: {args.dry_run} | Skip live: {args.skip_live}")
    print(f"{'='*60}\n")

    results = []
    deployed = 0
    failed = 0
    batch_num = 0

    for i in range(0, len(sorted_targets), args.batch_size):
        batch = sorted_targets[i:i + args.batch_size]
        batch_num += 1
        print(f"--- Batch {batch_num} ({len(batch)} nodes) ---")

        for nid, node in batch:
            result = deploy_node(nid, node, api, dry_run=args.dry_run, force=args.force)
            results.append(result)
            status_icon = {"deployed": "+", "dry_run": "~", "failed": "X"}.get(result["status"], "?")
            print(f"  [{status_icon}] {nid} {node['name']:<35} {result['status']}")

            if result["status"] == "deployed":
                deployed += 1
                node["status"] = "live"
            elif result["status"] == "failed":
                failed += 1

            if not args.dry_run:
                time.sleep(1.5)

        if not args.dry_run and i + args.batch_size < len(sorted_targets):
            print(f"  Rate limit pause (5s)...")
            time.sleep(5)

    if not args.dry_run:
        manifest["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        manifest["live_count"] = sum(1 for n in nodes.values() if n.get("status") == "live")
        manifest["planned_count"] = sum(1 for n in nodes.values() if n.get("status") == "planned")
        save_manifest(manifest)

    report = {
        "version": "v82.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deployed": deployed,
        "failed": failed,
        "skipped": len(sorted_targets) - deployed - failed,
        "total_live": manifest.get("live_count", 45),
        "total_planned": manifest.get("planned_count", 99),
        "results": results,
    }

    report_path = Path(__file__).parent / "deployment_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  Deployed: {deployed} | Failed: {failed}")
    print(f"  Total Live: {report['total_live']}/144")
    print(f"  Report: {report_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
