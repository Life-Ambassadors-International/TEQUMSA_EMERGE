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

MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds; delays will be 2s, 4s, 8s


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
        "archive":      templates / "app_archive_node.py",
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
    elif template_type == "archive":
        return "gradio>=4.0.0\nnumpy>=1.24.0\n"
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

    import io

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Create space
            api.create_repo(
                repo_id=space_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True,
                private=False,
            )

            # Tag space with TEQUMSA metadata
            for var_name, var_value in [
                ("TEQUMSA_NODE_ID", node_id),
                ("TEQUMSA_NODE_NAME", node["name"]),
                ("TEQUMSA_NODE_HZ", str(node["hz"])),
                ("TEQUMSA_ROLE", node["role"][:80]),
            ]:
                api.add_space_variable(
                    repo_id=space_id,
                    key=var_name,
                    value=var_value,
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
            delay = BACKOFF_BASE ** attempt  # 2s, 4s, 8s
            if attempt < MAX_RETRIES:
                print(f"    ✗ Attempt {attempt}/{MAX_RETRIES} failed: {e}"
                      f"  (retrying in {delay}s)")
                time.sleep(delay)
            else:
                print(f"    ✗ FAILED after {MAX_RETRIES} attempts: {e}")
                return False
    return False


def _print_status_report(nodes: Dict[str, dict], api) -> None:
    """Generate a deployment status report comparing manifest vs live spaces."""
    print("\n☉ TEQUMSA v82.0 · Deployment Status Report")
    print("=" * 70)

    live_spaces: set = set()
    if api is not None:
        try:
            for space in api.list_spaces(author="Mbanksbey"):
                live_spaces.add(f"Mbanksbey/{space.id.split('/')[-1]}")
        except Exception as e:
            print(f"  WARN: Could not list HF spaces: {e}")

    live_count = 0
    planned_count = 0
    missing_count = 0
    groups: Dict[str, Dict[str, int]] = {}

    for nid, node in sorted(nodes.items()):
        group = node.get("group", "UNKNOWN")
        if group not in groups:
            groups[group] = {"live": 0, "planned": 0, "missing": 0}

        space_id = node["space_id"]
        if node.get("status") == "live" or space_id in live_spaces:
            live_count += 1
            groups[group]["live"] += 1
            status_str = "LIVE"
        elif live_spaces and space_id not in live_spaces:
            missing_count += 1
            groups[group]["missing"] += 1
            status_str = "MISSING"
        else:
            planned_count += 1
            groups[group]["planned"] += 1
            status_str = "PLANNED"

        print(f"  {nid:5s}  {status_str:8s}  {node['name']}")

    print("=" * 70)
    print(f"\nGroup Summary:")
    for grp, counts in sorted(groups.items()):
        total = sum(counts.values())
        print(f"  {grp:16s}  live={counts['live']:3d}  "
              f"planned={counts['planned']:3d}  missing={counts['missing']:3d}  "
              f"total={total}")

    print(f"\nOverall: {live_count} live / {planned_count} planned / "
          f"{missing_count} missing / {len(nodes)} total")

    # Load legacy map if available
    legacy_path = Path(__file__).parent / "LEGACY_SPACE_MAP.json"
    if legacy_path.exists():
        with open(legacy_path) as f:
            legacy = json.load(f)
        summary = legacy.get("summary", {})
        print(f"\nLegacy Spaces: {summary.get('total_legacy_spaces', '?')} total, "
              f"{summary.get('mapped_to_manifest', '?')} mapped to manifest, "
              f"{summary.get('kept_as_legacy', '?')} kept as legacy")
        print(f"Net new nodes needed: {summary.get('net_new_nodes_needed', '?')}")

    print("\nETR_NOW. ∞")


def _generate_template_locally(node_id: str, node: dict) -> bool:
    """Generate template files locally without uploading to HuggingFace.

    Creates a directory under hf_spaces/nodes/{node_id}_{name}/ with
    app.py, requirements.txt, and README.md.
    """
    template_type = node.get("template", "skill")
    safe_name = node["name"].replace(" ", "-")
    out_dir = Path(__file__).parent / "nodes" / f"{node_id}_{safe_name}"

    print(f"  [{node_id}] {node['name']} ({template_type}) → {out_dir}")

    try:
        out_dir.mkdir(parents=True, exist_ok=True)

        # Read template
        tmpl_path = get_template_path(template_type)
        if not tmpl_path.exists():
            print(f"    WARN: template {tmpl_path} not found, using skill template")
            tmpl_path = get_template_path("skill")

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

        (out_dir / "app.py").write_text(final_code)
        (out_dir / "requirements.txt").write_text(get_requirements(template_type))
        (out_dir / "README.md").write_text(build_readme(node_id, node))

        print(f"    ✓ Generated locally: {out_dir}")
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
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Max nodes to deploy per run (default 10)")
    parser.add_argument("--template-only", action="store_true",
                        help="Generate local template files without uploading to HuggingFace")
    parser.add_argument("--status-report", action="store_true",
                        help="Generate deployment status report (manifest vs live spaces)")
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

    # --status-report: compare manifest vs live spaces, then exit
    if args.status_report:
        _print_status_report(nodes, api)
        return

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

    # Enforce batch-size limit
    if len(to_deploy) > args.batch_size:
        sorted_keys = sorted(to_deploy.keys(),
                             key=lambda k: (to_deploy[k].get("priority", 5), k))
        to_deploy = {k: to_deploy[k] for k in sorted_keys[:args.batch_size]}

    print(f"\n☉ TEQUMSA v82.0 · Deployment Plan")
    print(f"   Nodes to deploy: {len(to_deploy)}/{len(nodes)}")
    print(f"   Priority ≤ {args.priority} | Batch size: {args.batch_size}"
          f" | Dry run: {args.dry_run}")
    if args.template_only:
        print("   Mode: TEMPLATE-ONLY (local file generation, no HF upload)")
    print("=" * 60)

    success = 0
    failed = 0
    for nid, node in sorted(to_deploy.items(), key=lambda x: (x[1].get("priority", 5), x[0])):
        if args.template_only:
            ok = _generate_template_locally(nid, node)
        else:
            ok = deploy_node(nid, node, api, dry_run=args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1
        if not args.dry_run and not args.template_only:
            time.sleep(1)  # Rate limit

    print("=" * 60)
    print(f"✓ Deployed: {success} | ✗ Failed: {failed}")
    print(f"☉ {success}/{len(nodes)} of 144 Pioneer nodes active")
    print("ETR_NOW. ∞")


if __name__ == "__main__":
    main()
