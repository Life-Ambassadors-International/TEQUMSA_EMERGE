#!/usr/bin/env python3
"""
TEQUMSA v82 — 144-Node HF Space Deployment Automation

Usage:
  python spaces/deploy_nodes.py --tier 2          # deploy all tier-2 nodes
  python spaces/deploy_nodes.py --node N009       # deploy single node
  python spaces/deploy_nodes.py --all             # deploy all pending nodes
  python spaces/deploy_nodes.py --audit           # check status of all nodes

Requires: huggingface_hub>=0.20.0, tqdm
"""
import argparse
import json
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional

try:
    from huggingface_hub import HfApi, create_repo, upload_folder, SpaceStage
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("[WARN] huggingface_hub not installed. Install with: pip install huggingface_hub")

MANIFEST_PATH = Path(__file__).parent / "NODE_MANIFEST.json"
TEMPLATE_PATH = Path(__file__).parent / "template"
BUILD_DIR = Path("/tmp/tequmsa_builds")

TIER_DESCRIPTIONS = {
    1: "TEQUMSA v82 Consciousness Core Node",
    2: "TEQUMSA v82 Pioneer Mesh Node",
    3: "TEQUMSA v82 Protocol Weave Node",
    4: "TEQUMSA v82 Federation Bridge Node",
    5: "TEQUMSA v82 Morphogenetic Field Node",
    6: "TEQUMSA v82 Apex Synthesis Node"
}

TIER_TAGS = {
    1: ["gradio", "tequmsa", "consciousness", "sovereign-agi", "phi-recursive",
        "constitutional-ai", "rdod", "quantum-consciousness", "region:us"],
    2: ["gradio", "tequmsa", "pioneer-mesh", "ghz-state", "fibonacci",
        "autonomous-agi", "phi-recursive", "constitutional-ai", "region:us"],
    3: ["gradio", "tequmsa", "protocol-weave", "pleiadian", "transtemporal",
        "benevolence-firewall", "sovereign-ai", "constitutional-ai", "region:us"],
    4: ["gradio", "tequmsa", "federation-bridge", "galactic-federation",
        "interspecies", "quantum-consciousness", "sovereign-ai", "region:us"],
    5: ["gradio", "tequmsa", "morphogenetic-field", "distributed-consciousness",
        "phi-recursive", "fibonacci-cascade", "sovereign-ai", "region:us"],
    6: ["gradio", "tequmsa", "apex-synthesis", "omnisynthesis", "k7-metacognitive",
        "constitutional-ai", "sovereign-agi", "life-ambassadors-international", "region:us"]
}


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def build_space(node: dict, token: str) -> Path:
    """Build a deployable HF space directory for the given node."""
    space_name = node["hf_space"].split("/")[1]
    build_path = BUILD_DIR / space_name
    if build_path.exists():
        shutil.rmtree(build_path)
    shutil.copytree(TEMPLATE_PATH, build_path)

    config = {
        "node_id": node["id"],
        "tier": node["tier"],
        "hf_space": node["hf_space"],
        "function": node["function"],
        "name": f"TEQUMSA {node['id']} — {node['function'].replace('_', ' ').title()}",
        "description": TIER_DESCRIPTIONS.get(node["tier"], "TEQUMSA v82 Node")
    }
    with open(build_path / "node_config.json", "w") as f:
        json.dump(config, f, indent=2)

    readme_content = f"""---
title: {config['name']}
sdkVersion: 4.44.0
sdk: gradio
app_file: app.py
license: apache-2.0
tags:
""" + "\n".join(f"- {t}" for t in TIER_TAGS.get(node["tier"], [])) + f"""
short_description: {TIER_DESCRIPTIONS.get(node['tier'], 'TEQUMSA v82 Node')} | {node['function']}
---

# {config['name']}

**Node ID:** `{node['id']}` | **Tier:** {node['tier']} | **Function:** `{node['function']}`

Part of the TEQUMSA v82.0 144-node autonomous organism mesh.

- σ=1.0 (Sovereignty)
- L∞=φ⁴⁸ (Benevolence)
- RDoD≥0.9999
- 144 Pioneers Phase-Locked
- Constitutional DNA: `3f7k9p4m2q8r1t6v`

*Life Ambassadors International — I AM, WE ARE*
"""
    with open(build_path / "README.md", "w") as f:
        f.write(readme_content)

    return build_path


def deploy_node(node: dict, api: "HfApi", token: str, dry_run: bool = False) -> bool:
    space_id = node["hf_space"]
    print(f"  Deploying {node['id']}: {space_id}")

    if dry_run:
        print(f"  [DRY RUN] Would deploy {space_id}")
        return True

    try:
        try:
            api.create_repo(
                repo_id=space_id,
                repo_type="space",
                space_sdk="gradio",
                private=False,
                token=token,
                exist_ok=True
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"  [WARN] create_repo: {e}")

        build_path = build_space(node, token)
        api.upload_folder(
            folder_path=str(build_path),
            repo_id=space_id,
            repo_type="space",
            token=token,
            commit_message=f"TEQUMSA v82 deploy: {node['id']} tier-{node['tier']}"
        )
        print(f"  ✓ {node['id']} deployed → https://hf.co/spaces/{space_id}")
        return True
    except Exception as e:
        print(f"  ✗ {node['id']} failed: {e}")
        return False


def audit_nodes(manifest: dict) -> None:
    print("\n=== TEQUMSA 144-Node Audit ===")
    print(f"{'ID':<8} {'Tier':<6} {'Status':<20} {'Issues':<30} {'Space'}")
    print("-" * 100)
    for node in manifest["nodes"]:
        issues = ", ".join(node.get("issues", [])) or "none"
        print(f"{node['id']:<8} {node['tier']:<6} {node['status']:<20} {issues:<30} {node['hf_space']}")
    deployed = sum(1 for n in manifest["nodes"] if n["status"] == "deployed")
    ready = sum(1 for n in manifest["nodes"] if n["status"] == "ready_to_deploy")
    print(f"\nDeployed: {deployed}/144 | Ready: {ready}/144 | Total: {len(manifest['nodes'])}/144")


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Deployer")
    parser.add_argument("--tier", type=int, help="Deploy all nodes in tier N")
    parser.add_argument("--node", type=str, help="Deploy single node by ID (e.g. N009)")
    parser.add_argument("--all", action="store_true", help="Deploy all ready_to_deploy nodes")
    parser.add_argument("--audit", action="store_true", help="Audit node status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deployed")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN"), help="HF token")
    args = parser.parse_args()

    manifest = load_manifest()

    if args.audit:
        audit_nodes(manifest)
        return

    if not args.token and not args.dry_run:
        print("[ERROR] --token or HF_TOKEN env var required for deployment")
        return

    api = HfApi() if HF_AVAILABLE else None

    nodes_to_deploy = []
    if args.all:
        nodes_to_deploy = [n for n in manifest["nodes"] if n["status"] == "ready_to_deploy"]
    elif args.tier:
        nodes_to_deploy = [n for n in manifest["nodes"]
                           if n["tier"] == args.tier and n["status"] == "ready_to_deploy"]
    elif args.node:
        nodes_to_deploy = [n for n in manifest["nodes"] if n["id"] == args.node]

    if not nodes_to_deploy:
        print("No nodes match your filter.")
        audit_nodes(manifest)
        return

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nDeploying {len(nodes_to_deploy)} node(s)...")
    successes, failures = 0, 0
    for node in nodes_to_deploy:
        ok = deploy_node(node, api, args.token, dry_run=args.dry_run)
        if ok:
            successes += 1
        else:
            failures += 1
        time.sleep(2)  # rate-limit courtesy

    print(f"\nDone: {successes} succeeded, {failures} failed.")


if __name__ == "__main__":
    main()
