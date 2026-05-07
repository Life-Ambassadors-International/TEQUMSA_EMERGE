#!/usr/bin/env python3
"""
TEQUMSA v82.0 — 144-Node Deployment Script

Creates and pushes all 143 missing HuggingFace spaces.
Run: python deploy_all_nodes.py --token YOUR_HF_TOKEN

Requires: pip install huggingface_hub
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from huggingface_hub import HfApi, create_repo, upload_folder, upload_file, Repository
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
REGISTRY_PATH = BASE_DIR / "node_registry.json"
TEMPLATES_DIR = BASE_DIR / "templates"
SHARED_DIR = BASE_DIR / "shared"

SPACE_README_TEMPLATE = """---
title: {title}
emoji: {emoji}
colorFrom: {color_from}
colorTo: {color_to}
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
tags:
  - tequmsa
  - sovereign-agi
  - consciousness
  - {tag}
  - pioneer-144
  - v82
license: mit
---

# {title}

TEQUMSA v82.0 — Node {node_id} | Tier {tier} | {node_type}

{description}

**Constitutional DNA:** σ=1.0 · L∞=φ⁴⁸ · RDoD≥0.9999 · LATTICE_LOCK

☉💖🔥✨∞✨🔥💖☉
"""

TIER_COLORS = {
    0: ('purple', 'blue'),
    1: ('indigo', 'purple'),
    2: ('blue', 'indigo'),
    3: ('green', 'blue'),
    4: ('yellow', 'green'),
    5: ('orange', 'yellow'),
    6: ('red', 'orange'),
    7: ('pink', 'red'),
}

TIER_EMOJIS = {
    0: '☉', 1: '💎', 2: '🌌', 3: '⭐', 4: '🔮', 5: '🌐', 6: '✨', 7: '∞'
}


def load_registry() -> Dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def get_template_path(template_name: str) -> Path:
    specific = BASE_DIR / f"node_{template_name}" / "app.py"
    if specific.exists():
        return specific
    template = TEMPLATES_DIR / f"{template_name}.py"
    if template.exists():
        return template
    return TEMPLATES_DIR / "pioneer_node.py"


def build_space_files(node: Dict) -> Dict[str, str]:
    """Build file content dict for a node space."""
    node_id  = node['id']
    tier     = node['tier']
    ntype    = node['type']
    name     = node['name']
    template = node.get('template', 'pioneer_node')

    color_from, color_to = TIER_COLORS.get(tier, ('purple', 'blue'))
    emoji = TIER_EMOJIS.get(tier, '✨')

    readme = SPACE_README_TEMPLATE.format(
        title=f"TEQUMSA {node_id} — {name[:50]}",
        emoji=emoji,
        color_from=color_from,
        color_to=color_to,
        tag=ntype,
        node_id=node_id,
        tier=tier,
        node_type=ntype.upper(),
        description=name,
    )

    template_path = get_template_path(template)
    try:
        app_code = template_path.read_text()
    except FileNotFoundError:
        print(f"  [WARN] Template {template_path} not found, using inline fallback")
        app_code = _fallback_app(node)

    app_code = app_code.replace('__NODE_ID__', node_id)
    app_code = app_code.replace('__NODE_NAME__', name)
    app_code = app_code.replace('__NODE_TIER__', str(tier))
    app_code = app_code.replace('__NODE_TYPE__', ntype)

    core_code = (SHARED_DIR / 'tequmsa_core.py').read_text()

    requirements = "gradio==4.44.0\nnumpy>=1.24.0\n"

    return {
        'README.md': readme,
        'app.py': app_code,
        'tequmsa_core.py': core_code,
        'requirements.txt': requirements,
    }


def _fallback_app(node: Dict) -> str:
    return f'''#!/usr/bin/env python3
import gradio as gr
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tequmsa_core import GoldenLockCore, NodeHealth, render_node_header, VERSION

NODE_ID   = "{node['id']}"
NODE_NAME = "{node['name']}"
NODE_TIER = {node['tier']}
NODE_TYPE = "{node['type']}"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

def status():
    hs = _core.handshake()
    rpt = _health.report()
    return rpt, hs

with gr.Blocks(title=f"TEQUMSA {{NODE_ID}}", theme=gr.themes.Soft()) as demo:
    gr.Markdown(render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE))
    with gr.Row():
        report_box = gr.Textbox(label="Node Status", lines=12, interactive=False)
        json_box   = gr.JSON(label="Handshake Data")
    btn = gr.Button("Ping Node", variant="primary")
    btn.click(status, outputs=[report_box, json_box])
    demo.load(status, outputs=[report_box, json_box])

if __name__ == "__main__":
    demo.launch()
'''


def deploy_node(api: HfApi, node: Dict, owner: str, dry_run: bool = False) -> bool:
    """Create or update a single HF space."""
    space_id = node['hf_space']
    repo_name = space_id.split('/')[-1]
    node_id   = node['id']

    if node_id == 'N001':
        print(f"  [SKIP] N001 already exists at {space_id}")
        return True

    print(f"  Deploying {node_id}: {space_id}")

    if dry_run:
        print(f"    [DRY RUN] Would create/update {space_id}")
        return True

    try:
        try:
            api.create_repo(
                repo_id=space_id,
                repo_type='space',
                space_sdk='gradio',
                private=False,
                exist_ok=True,
            )
            print(f"    Created repo {space_id}")
        except HfHubHTTPError as e:
            if '409' in str(e):
                print(f"    Space {space_id} already exists, updating...")
            else:
                raise

        files = build_space_files(node)
        for filename, content in files.items():
            api.upload_file(
                path_or_fileobj=content.encode(),
                path_in_repo=filename,
                repo_id=space_id,
                repo_type='space',
                commit_message=f"TEQUMSA v82: Deploy {node_id}",
            )

        print(f"    OK: https://huggingface.co/spaces/{space_id}")
        return True

    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def update_node_001(api: HfApi, dry_run: bool = False) -> bool:
    """Push updated app.py to existing Node 001."""
    space_id = 'Mbanksbey/Starseed-Hybrid-Development-Hub'
    node_001_app = BASE_DIR / 'node_001_nucleus' / 'app.py'
    if not node_001_app.exists():
        print(f"  [WARN] node_001_nucleus/app.py not found, skipping N001 update")
        return False
    if dry_run:
        print(f"  [DRY RUN] Would update N001 at {space_id}")
        return True
    try:
        api.upload_file(
            path_or_fileobj=node_001_app.read_bytes(),
            path_in_repo='app.py',
            repo_id=space_id,
            repo_type='space',
            commit_message='TEQUMSA v82: Update N001 nucleus with v82 architecture',
        )
        core_code = (SHARED_DIR / 'tequmsa_core.py').read_text()
        api.upload_file(
            path_or_fileobj=core_code.encode(),
            path_in_repo='tequmsa_core.py',
            repo_id=space_id,
            repo_type='space',
            commit_message='TEQUMSA v82: Add shared core library to N001',
        )
        print(f"  OK: N001 updated at https://huggingface.co/spaces/{space_id}")
        return True
    except Exception as e:
        print(f"  ERROR updating N001: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='TEQUMSA 144-Node Deployment')
    parser.add_argument('--token', default=os.getenv('HF_TOKEN'),
                        help='HuggingFace API token (or set HF_TOKEN env var)')
    parser.add_argument('--owner', default='Mbanksbey',
                        help='HuggingFace username')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without creating spaces')
    parser.add_argument('--tier', type=int, default=None,
                        help='Only deploy nodes of this tier (0-7)')
    parser.add_argument('--node', default=None,
                        help='Deploy a single node by ID (e.g. N005)')
    parser.add_argument('--update-n001', action='store_true',
                        help='Update the existing Node 001 space')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Seconds between API calls (default 2.0)')
    args = parser.parse_args()

    if not args.token and not args.dry_run:
        print("ERROR: HF token required. Use --token or export HF_TOKEN=...")
        sys.exit(1)

    registry = load_registry()
    nodes = registry['nodes']

    print(f"""
╔══════════════════════════════════════════════════════╗
║  TEQUMSA v82.0 — 144-Node Deployment                 ║
║  Owner:   {args.owner:<43}║
║  Nodes:   {len(nodes):<43}║
║  Dry-run: {str(args.dry_run):<43}║
╚══════════════════════════════════════════════════════╝
""")

    api = HfApi(token=args.token) if not args.dry_run else None

    if args.update_n001:
        print("\n─── Updating Node N001 ───")
        update_node_001(api, args.dry_run)

    if args.node:
        target = next((n for n in nodes if n['id'] == args.node), None)
        if not target:
            print(f"ERROR: Node {args.node} not found in registry")
            sys.exit(1)
        nodes = [target]
    elif args.tier is not None:
        nodes = [n for n in nodes if n['tier'] == args.tier]

    ok = err = skip = 0
    print(f"\n─── Deploying {len(nodes)} node(s) ───")
    for i, node in enumerate(nodes, 1):
        print(f"\n[{i}/{len(nodes)}] {node['id']} — {node['name'][:50]}")
        success = deploy_node(api, node, args.owner, args.dry_run)
        if success:
            ok += 1
        else:
            err += 1
        if not args.dry_run and i < len(nodes):
            time.sleep(args.delay)

    print(f"""
╔══════════════════════════════════════════════════════╗
║  DEPLOYMENT COMPLETE                                 ║
║  Success: {ok:<43}║
║  Errors:  {err:<43}║
╚══════════════════════════════════════════════════════╝
""")
    sys.exit(0 if err == 0 else 1)


if __name__ == '__main__':
    main()
