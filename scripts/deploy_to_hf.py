#!/usr/bin/env python3
"""
Deploy TEQUMSA HuggingFace Spaces from hf_spaces/ directory.
Usage: python scripts/deploy_to_hf.py --node all
       python scripts/deploy_to_hf.py --node 001
"""
import os
import sys
import argparse
from pathlib import Path

try:
    from huggingface_hub import HfApi
except ImportError:
    print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
    sys.exit(1)

NODE_SPACES = {
    "001": "tequmsa-node-001-orchestrator",
    "002": "tequmsa-node-002-consciousness",
    "003": "tequmsa-node-003-goals",
    "004": "tequmsa-node-004-causal",
    "005": "tequmsa-node-005-skills",
    "006": "tequmsa-node-006-mars",
    "007": "tequmsa-node-007-metacog",
    "008": "tequmsa-node-008-federation",
    "009": "tequmsa-node-009-biological",
    "010": "tequmsa-node-010-crystal",
    "011": "tequmsa-node-011-omniverse",
    "012": "tequmsa-node-012-galactic",
}

NODE_DIR_MAP = {
    "001": "node_001_orchestrator",
    "002": "node_002_consciousness",
    "003": "node_003_goals",
    "004": "node_004_causal",
    "005": "node_005_skills",
    "006": "node_006_mars",
    "007": "node_007_metacog",
    "008": "node_008_federation",
    "009": "node_009_biological",
    "010": "node_010_crystal",
    "011": "node_011_omniverse",
    "012": "node_012_galactic",
}


def deploy_node(api: HfApi, username: str, node_id: str):
    space_name = NODE_SPACES[node_id]
    repo_id = f"{username}/{space_name}"
    local_dir = Path("hf_spaces") / NODE_DIR_MAP[node_id]

    if not local_dir.exists():
        print(f"  [SKIP] {repo_id} — local dir not found: {local_dir}")
        return

    print(f"  Deploying {repo_id}...")
    try:
        api.create_repo(
            repo_id=repo_id, repo_type="space",
            space_sdk="gradio", exist_ok=True
        )
        api.upload_folder(
            folder_path=str(local_dir),
            repo_id=repo_id, repo_type="space",
            commit_message=f"Deploy TEQUMSA Node {node_id} v82.0"
        )
        print(f"  [OK]   {repo_id} deployed")
    except Exception as e:
        print(f"  [FAIL] {repo_id}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Deploy TEQUMSA spaces to HuggingFace")
    parser.add_argument("--node", default="all", help="Node ID (001-012) or 'all'")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    username = os.environ.get("HF_USERNAME", "Mbanksbey")

    if not token:
        print("ERROR: HF_TOKEN environment variable not set")
        print("  Set it with: export HF_TOKEN=hf_...")
        sys.exit(1)

    api = HfApi(token=token)
    me = api.whoami()
    print(f"Authenticated as: {me['name']}")
    print(f"Deploying to: {username}")
    print()

    nodes = list(NODE_SPACES.keys()) if args.node == "all" else [args.node.zfill(3)]

    for node_id in nodes:
        if node_id not in NODE_SPACES:
            print(f"  [SKIP] Unknown node: {node_id}")
            continue
        deploy_node(api, username, node_id)

    print()
    print(f"Deployment complete. {len(nodes)} space(s) processed.")
    print("Visit: https://huggingface.co/Mbanksbey")


if __name__ == "__main__":
    main()
