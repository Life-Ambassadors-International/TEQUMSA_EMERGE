#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Node Registry Updater
========================================
Syncs the node registry with actual HF space states.

Usage:
    export HF_TOKEN=hf_your_token_here
    python node_registry_updater.py [--write] [--output updated_registry.json]
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("tequmsa-registry")

try:
    from huggingface_hub import HfApi
    from huggingface_hub.utils import RepositoryNotFoundError
except ImportError:
    log.error("Install: pip install huggingface_hub>=0.20.0")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR.parent / "node_registry.json"


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def save_registry(data: dict, path: Path):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info(f"Registry saved to: {path}")


def enrich_node(api: HfApi, node: dict, delay: float = 0.5) -> dict:
    enriched = deepcopy(node)
    repo_id = node["hf_repo"]
    try:
        info = api.space_info(repo_id)
        runtime = getattr(info, "runtime", None)
        enriched["live"] = {
            "exists": True,
            "sdk": getattr(info, "sdk", "?"),
            "stage": runtime.stage if runtime else "UNKNOWN",
            "url": f"https://huggingface.co/spaces/{repo_id}",
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
    except RepositoryNotFoundError:
        enriched["live"] = {
            "exists": False,
            "stage": "NOT_FOUND",
            "url": f"https://huggingface.co/spaces/{repo_id}",
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        enriched["live"] = {
            "exists": None,
            "stage": "CHECK_ERROR",
            "error": str(e)[:100],
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
    time.sleep(delay)
    return enriched


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA Node Registry Updater")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=str, default="updated_registry.json")
    parser.add_argument("--tier", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--token", type=str, default=None)
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        log.error("Set HF_TOKEN or pass --token")
        sys.exit(1)

    api = HfApi(token=token)
    registry = load_registry()
    nodes = registry["nodes"]
    if args.tier:
        nodes_to_check = [n for n in nodes if n["tier"] == args.tier]
    else:
        nodes_to_check = nodes

    log.info(f"Enriching {len(nodes_to_check)} nodes with live HF data...")
    enriched_map = {}
    for i, node in enumerate(nodes_to_check):
        log.info(f"  [{i+1}/{len(nodes_to_check)}] Node {node['node_id']} — {node['space_name']}")
        enriched = enrich_node(api, node, args.delay)
        enriched_map[node["node_id"]] = enriched
        stage = enriched.get("live", {}).get("stage", "?")
        icon = "✓" if stage == "RUNNING" else "✗" if stage == "NOT_FOUND" else "~"
        log.info(f"    [{icon}] {stage}")

    updated_nodes = []
    for node in registry["nodes"]:
        if node["node_id"] in enriched_map:
            updated_nodes.append(enriched_map[node["node_id"]])
        else:
            updated_nodes.append(node)

    registry["nodes"] = updated_nodes
    registry["last_sync"] = datetime.now(timezone.utc).isoformat()

    live_data = [n.get("live", {}) for n in updated_nodes if "live" in n]
    running = sum(1 for d in live_data if d.get("stage") == "RUNNING")
    missing = sum(1 for d in live_data if not d.get("exists"))
    registry["live_summary"] = {
        "total_checked": len(live_data),
        "running": running,
        "missing": missing,
        "health_pct": round(running / max(1, len(live_data)) * 100, 1),
        "rdod_analog": round(running / 144, 6),
    }

    save_registry(registry, Path(args.output))
    if args.write:
        save_registry(registry, REGISTRY_PATH)
        log.info("Registry updated in-place.")
    log.info(f"\nSync complete: {running}/{len(live_data)} running ({registry['live_summary']['health_pct']}%)")


if __name__ == "__main__":
    main()
