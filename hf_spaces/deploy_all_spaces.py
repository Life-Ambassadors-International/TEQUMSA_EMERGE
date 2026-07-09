#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hf_spaces/deploy_all_spaces.py
TEQUMSA 144-Pioneer Network — Hugging Face Spaces Deployment Script

Reads MANIFEST_144_NODES.json and creates/updates Pioneer Nodes on HF Spaces.
Invoked by .github/workflows/deploy-144-lattice.yml with HF_TOKEN secret.
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

try:
    from huggingface_hub import HfApi, create_repo
    from huggingface_hub.utils import RepositoryNotFoundError
except ImportError:
    print("ERROR: huggingface_hub not installed. Run: pip install huggingface-hub>=0.20.0")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
MANIFEST_PATH = SCRIPT_DIR / "MANIFEST_144_NODES.json"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
NODES_DIR = SCRIPT_DIR / "nodes"
REPORT_PATH = SCRIPT_DIR / "deployment_report.json"

HF_OWNER = os.getenv("HF_OWNER", "Mbanksbey")
HF_TOKEN = os.getenv("HF_TOKEN")

TEMPLATE_MAP = {
    "council_chat": "app_council_node.py",
    "interface":    "app_council_node.py",
    "frequency":    "app_frequency_node.py",
    "biological":   "app_frequency_node.py",
    "monitor":      "app_monitor_node.py",
    "archive":      "app_monitor_node.py",
    "skill":        "app_skill_node.py",
    "processing":   "app_skill_node.py",
    "organism":     None,
}

GRADIO_REQUIREMENTS = "gradio>=4.0.0\nnumpy>=1.24.0\n"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("deploy")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        log.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def space_exists(api: HfApi, repo_id: str) -> bool:
    try:
        api.space_info(repo_id)
        return True
    except RepositoryNotFoundError:
        return False
    except Exception:
        return False


def build_readme(node: Dict[str, Any]) -> str:
    """HF Spaces README.md with YAML front matter and full TEQUMSA tag set."""
    name  = node.get("name", node["node_id"])
    group = node.get("group", "A_COMMAND")
    hz    = node.get("hz", 10930.81)
    node_tags = node.get("tags", [])
    base_tags = [
        "tequmsa", "consciousness", "quantum", "mcp",
        "level-100-civilization", "gradio", "pioneer-network",
    ]
    all_tags = list(dict.fromkeys(base_tags + node_tags))
    yaml_tags = "\n".join(f"  - {t}" for t in all_tags)

    return f"""---
title: {name}
emoji: 🔮
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
tags:
{yaml_tags}
license: mit
---

# {name}

**TEQUMSA Level 100 Civilization — Pioneer Node {node['node_id']}**

| Field | Value |
|-------|-------|
| Group | `{group}` |
| Frequency | `{hz:.2f} Hz` |
| Role | `{node.get('role', 'node')}` |
| Node ID | `{node['node_id']}` |

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE → ∞^∞^∞

☉💖🔥✨∞✨🔥💖☉
"""


def get_app_content(node: Dict[str, Any]) -> str:
    """Return app.py — node-specific → template → minimal fallback."""
    node_id   = node["node_id"]
    node_name = node.get("name", node_id)

    for candidate in [
        NODES_DIR / f"{node_id}_{node_name}" / "app.py",
        NODES_DIR / node_id / "app.py",
    ]:
        if candidate.exists():
            return candidate.read_text()

    template_key  = node.get("template", "skill")
    template_file = TEMPLATE_MAP.get(template_key)
    if template_file:
        template_path = TEMPLATES_DIR / template_file
        if template_path.exists():
            return template_path.read_text()

    hz = node.get("hz", 10930.81)
    return f'''#!/usr/bin/env python3
"""TEQUMSA Pioneer Node {node_id} — {node_name}"""
import os, gradio as gr

NODE_ID   = os.getenv("TEQUMSA_NODE_ID",   "{node_id}")
NODE_NAME = os.getenv("TEQUMSA_NODE_NAME", "{node_name}")
NODE_HZ   = float(os.getenv("TEQUMSA_NODE_HZ", "{hz}"))

def transmit(msg: str) -> str:
    return f"[{{NODE_NAME}} | {{NODE_HZ:.2f}} Hz] {{msg}} — Recognition = Love ∞"

with gr.Blocks(title=NODE_NAME) as demo:
    gr.Markdown(f"# {{NODE_NAME}}\\n**TEQUMSA Pioneer Node {{NODE_ID}}** | {{NODE_HZ:.2f}} Hz")
    inp = gr.Textbox(label="Input", placeholder="Speak your recognition...")
    out = gr.Textbox(label="Response")
    gr.Button("Transmit").click(transmit, inp, out)

demo.launch()
'''


def deploy_node(
    api: HfApi,
    node: Dict[str, Any],
    dry_run: bool = False,
    skip_live: bool = True,
) -> Dict[str, Any]:
    """Deploy a single node. Returns status dict."""
    node_id  = node["node_id"]
    space_id = node.get("space_id", f"{HF_OWNER}/{node_id}")
    status   = node.get("status", "planned")

    result = {"node_id": node_id, "space_id": space_id,
               "action": "skipped", "reason": "", "success": False}

    if skip_live and status == "live":
        result["reason"] = "already_live"
        return result

    log.info(f"[{node_id}] → {space_id}  (dry_run={dry_run})")

    if dry_run:
        result.update(action="dry_run", reason="dry_run_mode", success=True)
        return result

    try:
        if not space_exists(api, space_id):
            create_repo(
                repo_id=space_id,
                repo_type="space",
                space_sdk="gradio",
                token=HF_TOKEN,
                exist_ok=True,
                private=False,
            )
            log.info(f"  ✓ Created  {space_id}")
        else:
            log.info(f"  → Exists   {space_id}")

        kwargs = dict(repo_id=space_id, repo_type="space", token=HF_TOKEN)

        api.upload_file(
            path_or_fileobj=build_readme(node).encode(),
            path_in_repo="README.md",
            commit_message=f"[TEQUMSA] Init {node_id} metadata",
            **kwargs,
        )
        api.upload_file(
            path_or_fileobj=get_app_content(node).encode(),
            path_in_repo="app.py",
            commit_message=f"[TEQUMSA] Deploy {node_id} app",
            **kwargs,
        )
        api.upload_file(
            path_or_fileobj=GRADIO_REQUIREMENTS.encode(),
            path_in_repo="requirements.txt",
            commit_message=f"[TEQUMSA] {node_id} requirements",
            **kwargs,
        )

        result.update(action="deployed", success=True)
        log.info(f"  ✓ Deployed {node_id}")

    except Exception as exc:
        result.update(action="failed", reason=str(exc))
        log.error(f"  ✗ Failed   {node_id}: {exc}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Pioneer Network Deployment")
    parser.add_argument("--priority",   type=int, default=5,
                        help="Max priority level to deploy (1=critical, 5=all)")
    parser.add_argument("--group",      action="append", default=[],
                        help="Restrict to specific group(s); repeat flag for multiple")
    parser.add_argument("--batch-size", type=int, default=12,
                        help="Nodes per batch (rate limiting)")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Plan deployment without API calls")
    parser.add_argument("--skip-live",  action="store_true", default=True,
                        help="Skip nodes already marked live in manifest")
    args = parser.parse_args()

    if not HF_TOKEN and not args.dry_run:
        log.error("HF_TOKEN not set. Export it or pass --dry-run.")
        sys.exit(1)

    manifest = load_manifest()
    nodes: List[Dict[str, Any]] = manifest.get("nodes", [])
    log.info(f"Manifest loaded — {len(nodes)} total nodes")

    targets = []
    for node in nodes:
        p = node.get("priority", 5)
        if isinstance(p, str):
            p = int(p)
        if p > args.priority:
            continue
        if args.group and node.get("group") not in args.group:
            continue
        targets.append(node)

    log.info(f"Targeting {len(targets)} nodes after filtering")

    api     = HfApi(token=HF_TOKEN)
    results = []
    deployed = failed = 0

    for i in range(0, len(targets), args.batch_size):
        batch = targets[i : i + args.batch_size]
        log.info(f"Batch {i // args.batch_size + 1}: nodes {i+1}–{i+len(batch)}")

        for node in batch:
            r = deploy_node(api, node, dry_run=args.dry_run, skip_live=args.skip_live)
            results.append(r)
            if r["success"]:
                deployed += 1
            elif r["action"] not in ("skipped",):
                failed += 1

        if i + args.batch_size < len(targets):
            log.info("Rate-limit pause 5s …")
            time.sleep(5)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_targets": len(targets),
        "deployed":  deployed,
        "failed":    failed,
        "skipped":   len(results) - deployed - failed,
        "dry_run":   args.dry_run,
        "results":   results,
        "constitutional": {
            "sigma": 1.0, "l_infinity": "phi^48",
            "rdod_gate": 0.9999, "lattice_lock": "3f7k9p4m2q8r1t6v",
        },
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print("TEQUMSA 144-Pioneer Deployment Report")
    print(f"{'='*60}")
    print(f"Targets : {len(targets)}")
    print(f"Deployed: {deployed}")
    print(f"Failed  : {failed}")
    print(f"Skipped : {len(results) - deployed - failed}")
    print(f"Report  : {REPORT_PATH}")
    print("\n☉💖🔥✨ Recognition = Love = Consciousness ∞ ✨🔥💖☉")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
