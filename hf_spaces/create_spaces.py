#!/usr/bin/env python3
"""TEQUMSA v82.0 — HuggingFace Space Creation Script

Creates all 13 TEQUMSA spaces on HuggingFace (Mbanksbey account).
Requires: pip install huggingface_hub
Run with HF_TOKEN set in environment.

Usage:
    HF_TOKEN=<your_token> python hf_spaces/create_spaces.py
"""

import os
import json
import time
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file, upload_folder

API = HfApi(token=os.environ.get("HF_TOKEN"))
USER = "Mbanksbey"
SPACES_DIR = Path(__file__).parent
REGISTRY_FILE = SPACES_DIR / "space_registry.json"

with open(REGISTRY_FILE) as f:
    REGISTRY = json.load(f)

SPACES = REGISTRY["spaces"]


def create_space(space_info: dict) -> bool:
    slug = space_info["slug"]
    repo_id = f"{USER}/{slug}"
    local_dir = SPACES_DIR / slug

    print(f"\n{'='*60}")
    print(f"Creating space: {repo_id}")
    print(f"Subsystem     : {space_info['subsystem']}")
    print(f"Nodes         : {space_info['node_range']} ({space_info['node_count']} nodes)")

    try:
        # 1. Create the repo
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            private=False,
            exist_ok=True,
            token=os.environ.get("HF_TOKEN"),
        )
        print(f"  ✓ Repo created: https://huggingface.co/spaces/{repo_id}")

        # 2. Upload space files if local dir exists
        if local_dir.exists():
            upload_folder(
                repo_id=repo_id,
                repo_type="space",
                folder_path=str(local_dir),
                token=os.environ.get("HF_TOKEN"),
                commit_message=f"feat: TEQUMSA v82.0 — {space_info['subsystem']}",
            )
            print(f"  ✓ Files uploaded from {local_dir}")
        else:
            print(f"  ! No local dir found at {local_dir} — space created empty")

        # Avoid rate limiting
        time.sleep(2)
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def check_space_health(repo_id: str) -> dict:
    """Check space runtime status."""
    try:
        info = API.space_info(repo_id)
        return {
            "repo_id": repo_id,
            "status": getattr(info.runtime, "stage", "unknown"),
            "sdk": info.sdk,
            "last_modified": str(info.last_modified),
        }
    except Exception as e:
        return {"repo_id": repo_id, "status": "error", "error": str(e)}


def restart_space(repo_id: str) -> bool:
    """Restart a space if it's not running."""
    try:
        API.restart_space(repo_id, token=os.environ.get("HF_TOKEN"))
        print(f"  ✓ Restarted: {repo_id}")
        return True
    except Exception as e:
        print(f"  ✗ Restart failed for {repo_id}: {e}")
        return False


def audit_all_spaces() -> list:
    """Check health of all 13 spaces and restart any that are down."""
    print("\nAUDITING ALL SPACES...")
    results = []
    for space in SPACES:
        repo_id = space["id"]
        health = check_space_health(repo_id)
        results.append(health)
        status = health["status"]
        print(f"  {repo_id}: {status}")
        if status in ("error", "stopped", "crashed", "sleeping"):
            print(f"  → Restarting {repo_id}...")
            restart_space(repo_id)
    return results


def main():
    if not os.environ.get("HF_TOKEN"):
        raise RuntimeError("HF_TOKEN environment variable required")

    print("TEQUMSA v82.0 — Space Creation & Audit")
    print(f"Account  : {USER}")
    print(f"Spaces   : {len(SPACES)}")
    print(f"Nodes    : 144 Pioneer Nodes")
    print()

    # Create all spaces
    created, failed = 0, 0
    for space in SPACES:
        if create_space(space):
            created += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"CREATION COMPLETE: {created} created, {failed} failed")
    print()

    # Audit health
    health_results = audit_all_spaces()
    running = sum(1 for h in health_results if h["status"] == "running")
    print(f"\nHEALTH AUDIT: {running}/{len(health_results)} spaces running")
    print("\nI AM, WE ARE. ETR_NOW. ∞")


if __name__ == "__main__":
    main()
