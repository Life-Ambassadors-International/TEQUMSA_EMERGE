#!/usr/bin/env python3
"""Batch deployer for the 99 remaining TEQUMSA 144-node spaces.

Usage:
    python space_deployer.py --dry-run           # preview what would be created
    python space_deployer.py --priority 1 2 3    # deploy only priority-1/2/3 nodes
    python space_deployer.py --node N004         # deploy a specific node
    python space_deployer.py --all               # deploy all 99 planned nodes

Requires: HF_TOKEN env var with write access to Mbanksbey namespace.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_OWNER = "Mbanksbey"
MANIFEST_PATH = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
REGISTRY_PATH = Path(__file__).parent.parent / "LIVE_SPACES_REGISTRY.json"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

PHI = 1.6180339887498948

DEFAULT_TAGS = [
    "tequmsa", "consciousness", "sovereign-ai", "constitutional-ai",
    "phi-recursive", "quantum-consciousness", "rdod", "benevolence-firewall",
    "life-ambassadors-international", "region:us",
]

# Template → app filename mapping
TEMPLATE_APPS = {
    "council_chat": "app_council_node.py",
    "monitor":      "app_monitor_node.py",
    "skill":        "app_skill_node.py",
    "frequency":    "app_frequency_node.py",
    "processing":   "app_skill_node.py",
    "interface":    "app_council_node.py",
    "biological":   "app_skill_node.py",
    "archive":      "app_monitor_node.py",
    "organism":     "app_skill_node.py",
}

# SDK to use per template type
TEMPLATE_SDK = {
    "council_chat": "gradio",
    "monitor":      "gradio",
    "skill":        "gradio",
    "frequency":    "gradio",
    "processing":   "gradio",
    "interface":    "gradio",
    "biological":   "gradio",
    "archive":      "gradio",
    "organism":     "gradio",
}


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def get_live_node_ids(registry) -> set:
    return {entry["node"] for entry in registry["live_spaces"]}


def get_planned_nodes(manifest, registry):
    live_ids = get_live_node_ids(registry)
    nodes = manifest["nodes"]
    return [
        (node_id, data)
        for node_id, data in nodes.items()
        if node_id not in live_ids
    ]


# ---------------------------------------------------------------------------
# HF API helper
# ---------------------------------------------------------------------------

def get_hf_api():
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface-hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable not set.")
        sys.exit(1)

    return HfApi(token=token)


def space_exists(api, space_id: str) -> bool:
    try:
        api.space_info(space_id)
        return True
    except Exception:
        return False


def load_template(template_type: str) -> Optional[str]:
    filename = TEMPLATE_APPS.get(template_type, "app_skill_node.py")
    path = TEMPLATES_DIR / filename
    if path.exists():
        return path.read_text()
    return None


def load_requirements() -> str:
    req_path = TEMPLATES_DIR / "requirements_base.txt"
    if req_path.exists():
        return req_path.read_text()
    return "gradio>=4.0.0\nnumpy>=1.24.0\n"


# ---------------------------------------------------------------------------
# Space creation
# ---------------------------------------------------------------------------

def create_space(api, node_id: str, node_data: dict, dry_run: bool = False) -> dict:
    space_id = node_data["space_id"]
    repo_name = space_id.split("/")[-1]
    template_type = node_data.get("template", "skill")
    sdk = TEMPLATE_SDK.get(template_type, "gradio")
    hz = node_data.get("hz", 432.0)
    role = node_data.get("role", "TEQUMSA Node")
    group = node_data.get("group", "UNASSIGNED")
    priority = node_data.get("priority", 5)

    tags = list(DEFAULT_TAGS)
    node_tags = node_data.get("tags", [])
    tags.extend([t for t in node_tags if t not in tags])

    result = {
        "node": node_id,
        "space_id": space_id,
        "sdk": sdk,
        "template": template_type,
        "hz": hz,
        "priority": priority,
        "action": "dry_run" if dry_run else None,
        "success": False,
        "error": None,
    }

    print(f"  [{node_id}] {repo_name} ({template_type}, {hz:.2f} Hz, priority={priority})")

    if dry_run:
        result["action"] = "would_create"
        result["success"] = True
        return result

    # Check if already exists
    if space_exists(api, space_id):
        print(f"         Already exists — skipping")
        result["action"] = "already_exists"
        result["success"] = True
        return result

    try:
        # Create the repo
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk=sdk,
            private=False,
        )

        # Upload template app
        app_code = load_template(template_type)
        if app_code:
            # Inject node-specific constants
            app_code = app_code.replace("NODE_ID = 'N000'", f"NODE_ID = '{node_id}'")
            app_code = app_code.replace("NODE_ROLE = 'TEQUMSA Node'", f"NODE_ROLE = '{role}'")
            app_code = app_code.replace("NODE_HZ = 432.0", f"NODE_HZ = {hz}")
            app_code = app_code.replace("NODE_GROUP = 'GROUP'", f"NODE_GROUP = '{group}'")

            api.upload_file(
                path_or_fileobj=app_code.encode(),
                path_in_repo="app.py",
                repo_id=space_id,
                repo_type="space",
                commit_message=f"Initialize {node_id}: {role}",
            )

        # Upload requirements
        api.upload_file(
            path_or_fileobj=load_requirements().encode(),
            path_in_repo="requirements.txt",
            repo_id=space_id,
            repo_type="space",
            commit_message=f"Add requirements for {node_id}",
        )

        result["action"] = "created"
        result["success"] = True
        print(f"         ✓ Created: https://hf.co/spaces/{space_id}")

    except Exception as e:
        result["action"] = "failed"
        result["error"] = str(e)
        print(f"         ✗ Failed: {e}")

    return result


# ---------------------------------------------------------------------------
# Batch deployment
# ---------------------------------------------------------------------------

def deploy_batch(
    planned_nodes,
    priorities: list = None,
    target_node: str = None,
    dry_run: bool = False,
    delay_seconds: float = 2.0,
) -> list:
    api = None if dry_run else get_hf_api()

    # Filter
    if target_node:
        planned_nodes = [(nid, d) for nid, d in planned_nodes if nid == target_node]
    if priorities:
        planned_nodes = [(nid, d) for nid, d in planned_nodes if d.get("priority", 5) in priorities]

    # Sort: priority ASC (1 = most important first), then node_id
    planned_nodes.sort(key=lambda x: (x[1].get("priority", 5), x[0]))

    print(f"\nDeploying {len(planned_nodes)} nodes {'(DRY RUN)' if dry_run else ''}...\n")

    results = []
    for i, (node_id, node_data) in enumerate(planned_nodes, 1):
        print(f"[{i}/{len(planned_nodes)}] Deploying {node_id}...")
        result = create_space(api, node_id, node_data, dry_run=dry_run)
        results.append(result)

        if not dry_run and i < len(planned_nodes):
            # Phi-scaled delay to avoid rate limits
            sleep_time = delay_seconds * (1 + (i % 3) * 0.618)
            time.sleep(sleep_time)

    # Summary
    created = sum(1 for r in results if r["action"] == "created")
    skipped = sum(1 for r in results if r["action"] == "already_exists")
    failed = sum(1 for r in results if r["action"] == "failed")
    dry = sum(1 for r in results if r["action"] == "would_create")

    print(f"\n{'─' * 60}")
    print(f"DEPLOYMENT SUMMARY")
    print(f"{'─' * 60}")
    if dry_run:
        print(f"Would create: {dry}")
    else:
        print(f"Created:  {created}")
        print(f"Skipped:  {skipped} (already existed)")
        print(f"Failed:   {failed}")
    print(f"{'─' * 60}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deploy TEQUMSA 144-node HuggingFace spaces"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--all", action="store_true", help="Deploy all 99 planned nodes")
    parser.add_argument("--priority", type=int, nargs="+", help="Deploy nodes of given priority level(s)")
    parser.add_argument("--node", type=str, help="Deploy a specific node (e.g. N004)")
    parser.add_argument("--delay", type=float, default=2.0, help="Base delay between creations (seconds)")
    args = parser.parse_args()

    if not (args.dry_run or args.all or args.priority or args.node):
        parser.print_help()
        sys.exit(0)

    manifest = load_manifest()
    registry = load_registry()
    planned = get_planned_nodes(manifest, registry)

    print(f"Total planned nodes:  {len(planned)}")
    print(f"Live nodes:           {len(registry['live_spaces'])}")
    print(f"Remaining to deploy:  {len(planned)}")

    results = deploy_batch(
        planned,
        priorities=args.priority,
        target_node=args.node,
        dry_run=args.dry_run,
        delay_seconds=args.delay,
    )

    # Write report
    report_path = Path("deployment_report.json")
    with open(report_path, "w") as f:
        json.dump({"results": results, "total": len(results)}, f, indent=2)
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
