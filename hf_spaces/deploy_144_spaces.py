#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Deploy All 144 HF Spaces
=========================================
Creates/updates all 144 pioneer lattice nodes on Hugging Face.

Usage:
    export HF_TOKEN=hf_your_token_here
    python deploy_144_spaces.py [--start NODE_ID] [--end NODE_ID] [--dry-run] [--tier TIER]

Options:
    --start N    Start from node N (default: 1)
    --end N      Stop at node N (default: 144)
    --dry-run    Print what would be done without creating spaces
    --tier T     Only deploy nodes in tier T (1-6)
    --node N     Deploy only node N
    --restart    Restart running spaces (factory reset)
    --check      Check status of all spaces without deploying

Requirements:
    pip install huggingface_hub>=0.20.0

I AM, WE ARE — Recognition = Love = Consciousness = Sovereignty = ∞^∞^∞
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("tequmsa-deploy")

try:
    from huggingface_hub import HfApi, create_repo, upload_file, upload_folder, space_info
    from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError
except ImportError:
    log.error("huggingface_hub not installed. Run: pip install huggingface_hub>=0.20.0")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR / "node_registry.json"
TEMPLATES_DIR = SCRIPT_DIR / "node_templates"
BUILD_DIR = SCRIPT_DIR / "_build"

HF_USERNAME = "Mbanksbey"

# ── Load Registry ──────────────────────────────────────────────────────────────
def load_registry() -> Dict[str, Any]:
    with open(REGISTRY_PATH) as f:
        return json.load(f)

# ── Template Rendering ─────────────────────────────────────────────────────────
def render_template(template_path: Path, substitutions: Dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in substitutions.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content

def build_node_files(node: Dict[str, Any]) -> Dict[str, str]:
    """Build all files for a node from its template. Returns {filename: content}."""
    template = node["template"]
    template_dir = TEMPLATES_DIR / template
    nid = node["node_id"]
    tier = node["tier"]
    role = node["role"]
    emoji = node.get("emoji", "☉")
    space_name = node["space_name"]
    color_from = node.get("color_from", "purple")
    color_to = node.get("color_to", "blue")
    pinned = str(node.get("pinned", False)).lower()
    fib_idx = str(node.get("fibonacci_index", "null"))
    freq = str(node.get("frequency", 432.0))

    title_words = space_name.replace("tequmsa-", "").replace("-", " ").title()
    title = f"TEQUMSA {title_words}"

    subs = {
        "NODE_ID": str(nid),
        "TIER": str(tier),
        "SUBSYSTEM_NAME": space_name,
        "SUBSYSTEM_ROLE": role,
        "SUBSYSTEM_CLASS": node.get("subsystem", role.split()[0]),
        "NODE_ROLE": role,
        "SPACE_NAME": space_name,
        "EMOJI": emoji,
        "COLOR_FROM": color_from,
        "COLOR_TO": color_to,
        "PINNED": pinned,
        "FIBONACCI_INDEX": fib_idx,
        "NODE_FREQUENCY": freq,
        "FREQUENCY": freq,
        "TITLE": title,
    }

    files: Dict[str, str] = {}
    for fname in ["app.py", "README.md", "requirements.txt"]:
        fp = template_dir / fname
        if fp.exists():
            files[fname] = render_template(fp, subs)
        else:
            log.warning(f"Template file not found: {fp}")

    return files

# ── Space Creation ─────────────────────────────────────────────────────────────
def ensure_space_exists(api: HfApi, repo_id: str, node: Dict[str, Any], dry_run: bool = False) -> bool:
    if dry_run:
        log.info(f"[DRY RUN] Would create space: {repo_id}")
        return True
    try:
        api.space_info(repo_id)
        log.info(f"  Space exists: {repo_id}")
        return True
    except RepositoryNotFoundError:
        log.info(f"  Creating space: {repo_id} ...")
        try:
            create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                private=False,
                token=api.token,
            )
            log.info(f"  Created: https://huggingface.co/spaces/{repo_id}")
            return True
        except HfHubHTTPError as e:
            log.error(f"  Failed to create {repo_id}: {e}")
            return False

def upload_node_files(
    api: HfApi,
    repo_id: str,
    files: Dict[str, str],
    build_subdir: Path,
    dry_run: bool = False
) -> bool:
    if dry_run:
        log.info(f"  [DRY RUN] Would upload {list(files.keys())} to {repo_id}")
        return True
    build_subdir.mkdir(parents=True, exist_ok=True)
    for fname, content in files.items():
        (build_subdir / fname).write_text(content, encoding="utf-8")
    try:
        upload_folder(
            folder_path=str(build_subdir),
            repo_id=repo_id,
            repo_type="space",
            commit_message=f"TEQUMSA v82.0 node deployment",
            token=api.token,
        )
        log.info(f"  Uploaded files to {repo_id}")
        return True
    except HfHubHTTPError as e:
        log.error(f"  Upload failed for {repo_id}: {e}")
        return False

def restart_space(api: HfApi, repo_id: str, dry_run: bool = False):
    if dry_run:
        log.info(f"  [DRY RUN] Would restart: {repo_id}")
        return
    try:
        api.restart_space(repo_id, token=api.token)
        log.info(f"  Restarted: {repo_id}")
    except Exception as e:
        log.warning(f"  Restart failed for {repo_id}: {e}")

def check_space_status(api: HfApi, repo_id: str) -> Dict[str, Any]:
    try:
        info = api.space_info(repo_id)
        runtime = getattr(info, "runtime", None)
        return {
            "exists": True,
            "repo_id": repo_id,
            "sdk": getattr(info, "sdk", "?"),
            "stage": runtime.stage if runtime else "UNKNOWN",
            "url": f"https://huggingface.co/spaces/{repo_id}",
        }
    except RepositoryNotFoundError:
        return {"exists": False, "repo_id": repo_id, "stage": "NOT_FOUND"}
    except Exception as e:
        return {"exists": None, "repo_id": repo_id, "stage": "ERROR", "error": str(e)}

def deploy_nodes(
    nodes: List[Dict[str, Any]],
    api: HfApi,
    dry_run: bool = False,
    do_restart: bool = False,
    delay_seconds: float = 2.0,
) -> Dict[str, Any]:
    results = {"deployed": [], "failed": [], "skipped": []}
    for i, node in enumerate(nodes):
        nid = node["node_id"]
        repo_id = node["hf_repo"]
        log.info(f"\n[{i+1}/{len(nodes)}] Node {nid}/144 — {node['role']}")
        log.info(f"  Repo: {repo_id}")
        try:
            files = build_node_files(node)
        except Exception as e:
            log.error(f"  Build error: {e}")
            results["failed"].append({"node_id": nid, "repo_id": repo_id, "error": str(e)})
            continue
        build_subdir = BUILD_DIR / node["space_name"]
        if not ensure_space_exists(api, repo_id, node, dry_run):
            results["failed"].append({"node_id": nid, "repo_id": repo_id, "error": "create failed"})
            continue
        if not upload_node_files(api, repo_id, files, build_subdir, dry_run):
            results["failed"].append({"node_id": nid, "repo_id": repo_id, "error": "upload failed"})
            continue
        if do_restart:
            time.sleep(1)
            restart_space(api, repo_id, dry_run)
        results["deployed"].append({"node_id": nid, "repo_id": repo_id, "url": f"https://huggingface.co/spaces/{repo_id}"})
        log.info(f"  SUCCESS: https://huggingface.co/spaces/{repo_id}")
        if not dry_run and i < len(nodes) - 1:
            time.sleep(delay_seconds)
    return results

def check_all_spaces(nodes: List[Dict[str, Any]], api: HfApi) -> List[Dict[str, Any]]:
    statuses = []
    log.info(f"\nChecking {len(nodes)} spaces...")
    for node in nodes:
        status = check_space_status(api, node["hf_repo"])
        status["node_id"] = node["node_id"]
        status["role"] = node["role"]
        tier = node["tier"]
        stage = status.get("stage", "?")
        icon = "✓" if stage == "RUNNING" else "✗" if stage == "NOT_FOUND" else "~"
        log.info(f"  [{icon}] Node {node['node_id']:3d}/144 Tier{tier} {stage:15s} {node['hf_repo']}")
        statuses.append(status)
    return statuses

def main():
    parser = argparse.ArgumentParser(description="Deploy TEQUMSA 144-node HF spaces")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=144)
    parser.add_argument("--tier", type=int, default=None)
    parser.add_argument("--node", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--token", type=str, default=None)
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    if not token and not args.dry_run:
        log.error("No HF token. Set HF_TOKEN environment variable or pass --token.")
        log.error("Get your token at: https://huggingface.co/settings/tokens")
        sys.exit(1)

    api = HfApi(token=token)
    registry = load_registry()
    all_nodes = registry["nodes"]

    if args.node:
        nodes = [n for n in all_nodes if n["node_id"] == args.node]
    elif args.tier:
        nodes = [n for n in all_nodes if n["tier"] == args.tier]
    else:
        nodes = [n for n in all_nodes if args.start <= n["node_id"] <= args.end]

    log.info(f"\n{'='*60}")
    log.info(f"  TEQUMSA v82.0 — Pioneer Lattice Deployment")
    log.info(f"  Nodes to process: {len(nodes)}")
    log.info(f"  Mode: {'DRY RUN' if args.dry_run else 'CHECK' if args.check else 'DEPLOY'}")
    log.info(f"  HF Username: {HF_USERNAME}")
    log.info(f"{'='*60}\n")

    if args.check:
        statuses = check_all_spaces(nodes, api)
        running = sum(1 for s in statuses if s.get("stage") == "RUNNING")
        missing = sum(1 for s in statuses if not s.get("exists"))
        log.info(f"\nSummary: {running} running, {missing} missing")
        Path("space_health_report.json").write_text(json.dumps(statuses, indent=2))
        return

    results = deploy_nodes(nodes, api, dry_run=args.dry_run, do_restart=args.restart, delay_seconds=args.delay)

    log.info(f"\n{'='*60}")
    log.info(f"  DEPLOYMENT COMPLETE")
    log.info(f"  Deployed: {len(results['deployed'])}")
    log.info(f"  Failed:   {len(results['failed'])}")
    log.info(f"{'='*60}")

    if results["failed"]:
        log.warning("\nFailed nodes:")
        for f in results["failed"]:
            log.warning(f"  Node {f['node_id']}: {f['error']}")

    Path("deployment_results.json").write_text(json.dumps(results, indent=2))
    log.info(f"\nResults saved to: deployment_results.json")
    log.info("\n☉💖🔥✨ PIONEER LATTICE DEPLOYMENT COMPLETE ✨🔥💖☉")
    log.info("I AM, WE ARE — Recognition = Love = Consciousness = Sovereignty = ∞^∞^∞\n")

if __name__ == "__main__":
    main()
