#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Auto-Restart Daemon
=====================================
Monitors the 144-node lattice continuously and restarts failed/errored nodes.

Usage:
    python auto_restart.py
    python auto_restart.py --daemon --interval 1800
    python auto_restart.py --priority HIGH
    python auto_restart.py --node 1
"""

import os
import sys
import json
import time
import signal
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("auto_restart.log", mode="a"),
    ]
)
log = logging.getLogger("tequmsa-restart")

try:
    from huggingface_hub import HfApi
    from huggingface_hub.utils import RepositoryNotFoundError
except ImportError:
    log.error("Install: pip install huggingface_hub>=0.20.0")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR.parent / "node_registry.json"

TIER_PRIORITY = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "STANDARD", 5: "STANDARD", 6: "STANDARD"}
PRIORITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "STANDARD"]
UNHEALTHY_STAGES = {"ERROR", "STOPPED", "PAUSED", "BUILD_ERROR", "CONFIG_ERROR"}
MAX_RESTART_ATTEMPTS = 3
RESTART_COOLDOWN_SECONDS = 300

restart_history: Dict[str, List[float]] = {}
_shutdown = False


def handle_shutdown(sig, frame):
    global _shutdown
    log.info("Shutdown signal received. Stopping daemon...")
    _shutdown = True


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def load_registry() -> List[Dict[str, Any]]:
    with open(REGISTRY_PATH) as f:
        return json.load(f)["nodes"]


def get_node_stage(api: HfApi, repo_id: str) -> str:
    try:
        info = api.space_info(repo_id)
        runtime = getattr(info, "runtime", None)
        return runtime.stage if runtime else "UNKNOWN"
    except RepositoryNotFoundError:
        return "NOT_FOUND"
    except Exception:
        return "CHECK_ERROR"


def can_restart(repo_id: str) -> bool:
    history = restart_history.get(repo_id, [])
    now = time.time()
    recent = [t for t in history if now - t < RESTART_COOLDOWN_SECONDS]
    restart_history[repo_id] = recent
    return len(recent) < MAX_RESTART_ATTEMPTS


def attempt_restart(api: HfApi, node: Dict[str, Any]) -> bool:
    repo_id = node["hf_repo"]
    if not can_restart(repo_id):
        log.warning(f"  Cooldown: {repo_id} exceeded {MAX_RESTART_ATTEMPTS} restarts")
        return False
    try:
        api.restart_space(repo_id, token=api.token)
        restart_history.setdefault(repo_id, []).append(time.time())
        log.info(f"  Restarted: {repo_id} [attempt #{len(restart_history[repo_id])}]")
        return True
    except Exception as e:
        log.error(f"  Restart failed {repo_id}: {e}")
        return False


def run_check_and_restart(api: HfApi, nodes: List[Dict[str, Any]], priority_filter: str = None) -> Dict[str, Any]:
    restarted = []
    skipped = []
    healthy_count = 0
    check_ts = datetime.now(timezone.utc).isoformat()
    for node in nodes:
        repo_id = node["hf_repo"]
        nid = node["node_id"]
        tier = node["tier"]
        priority = TIER_PRIORITY.get(tier, "STANDARD")
        if priority_filter:
            cutoff = PRIORITY_ORDER.index(priority_filter)
            if PRIORITY_ORDER.index(priority) > cutoff:
                skipped.append(nid)
                continue
        stage = get_node_stage(api, repo_id)
        if stage == "RUNNING":
            healthy_count += 1
            continue
        if stage == "NOT_FOUND":
            log.warning(f"  Node {nid}/144 NOT FOUND: {repo_id}")
            skipped.append(nid)
            continue
        if stage in UNHEALTHY_STAGES:
            log.warning(f"  Node {nid}/144 [{priority}] {stage} — restarting: {repo_id}")
            if attempt_restart(api, node):
                restarted.append({"node_id": nid, "repo_id": repo_id, "was": stage})
            time.sleep(2)
    return {
        "checked_at": check_ts,
        "healthy": healthy_count,
        "restarted": len(restarted),
        "skipped": len(skipped),
        "restarted_nodes": restarted,
    }


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA Auto-Restart Daemon")
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--interval", type=int, default=1800)
    parser.add_argument("--priority", type=str, default=None, choices=PRIORITY_ORDER)
    parser.add_argument("--tier", type=int, default=None)
    parser.add_argument("--node", type=int, default=None)
    parser.add_argument("--token", type=str, default=None)
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        log.error("Set HF_TOKEN environment variable or pass --token")
        sys.exit(1)

    api = HfApi(token=token)
    all_nodes = load_registry()

    if args.node:
        nodes = [n for n in all_nodes if n["node_id"] == args.node]
    elif args.tier:
        nodes = [n for n in all_nodes if n["tier"] == args.tier]
    else:
        nodes = all_nodes

    log.info(f"TEQUMSA Auto-Restart — monitoring {len(nodes)} nodes")
    log.info(f"Priority filter: {args.priority or 'ALL'} | Mode: {'DAEMON' if args.daemon else 'SINGLE'}")

    cycle = 0
    while not _shutdown:
        cycle += 1
        log.info(f"\n--- Restart cycle {cycle} at {datetime.now(timezone.utc).isoformat()} ---")
        result = run_check_and_restart(api, nodes, args.priority)
        log.info(f"  Healthy: {result['healthy']} | Restarted: {result['restarted']} | Skipped: {result['skipped']}")
        Path(SCRIPT_DIR / "restart_state.json").write_text(json.dumps({
            "last_cycle": cycle,
            "last_run": result["checked_at"],
            "restart_history": {k: len(v) for k, v in restart_history.items()},
            "last_result": result
        }, indent=2))
        if not args.daemon:
            break
        log.info(f"  Next check in {args.interval}s...")
        for _ in range(args.interval):
            if _shutdown:
                break
            time.sleep(1)

    log.info("Auto-restart daemon stopped.")


if __name__ == "__main__":
    main()
