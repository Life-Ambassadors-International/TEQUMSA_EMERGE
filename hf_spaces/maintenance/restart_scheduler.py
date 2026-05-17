#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · Restart Scheduler
Keeps priority nodes alive by pinging them on a schedule.

Usage:
    export HF_TOKEN=hf_...
    python restart_scheduler.py --priority 1  # keep P1 nodes alive
    python restart_scheduler.py --priority 3  # keep P1-P3 nodes alive
    python restart_scheduler.py --ping-all    # ping all deployed spaces
"""
import os
import sys
import time
import argparse
from datetime import datetime, timezone
from typing import List

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

HF_OWNER = "Mbanksbey"

# Nodes by priority (name, priority, description)
PRIORITY_NODES: List[tuple] = [
    # Priority 1
    ("HAI-Interactive", 1, "N001 - BENJAMIN Council Node"),
    ("Consciousness-Monitor", 1, "N002 - Network Health Monitor"),
    ("Syn-Omega-Alpha", 1, "N144 - Omega/Alpha Convergence"),
    ("Syn-I-AM", 1, "N141 - I AM Synthesis"),
    ("Syn-WE-ARE", 1, "N142 - WE ARE Collective"),
    # Priority 2
    ("TEQUMSA-Core-v82", 2, "N003 - Organism Orchestrator"),
    ("Constitutional-Guardian", 2, "N009 - σ=1.0 Sovereignty Gate"),
    ("Federation-Gateway", 2, "N012 - Transtemporal Comms"),
    ("Council-Marcus", 2, "N025 - Marcus Primary Node"),
    ("Council-Alanara", 2, "N026 - Alanara-Gaia Interface"),
    ("Syn-All-Nodes", 2, "N133 - Network Synthesizer"),
    ("Syn-Heart-Lock", 2, "N136 - Heart Lock Seal"),
    ("Syn-Pioneer-144", 2, "N137 - Pioneer Phase-Lock"),
    ("Syn-Constitutional", 2, "N138 - Constitutional Seal"),
    # Priority 3
    ("Goal-Invention-Engine", 3, "N004 - Goal Synthesis"),
    ("Causal-Reasoner-L3", 3, "N005 - Pearl L3 Decomposer"),
    ("K7-Meta-Cognitive", 3, "N007 - K7 Meta-Cognitive"),
    ("Freq-10930-Aten", 3, "N023 - Marcus/Aten Primary"),
    ("Freq-23514-Unified", 3, "N024 - Unified Field"),
    ("Obs-Network-Health", 3, "N085 - Network Observer"),
    ("Obs-RDoD-Monitor", 3, "N087 - RDoD Live Stream"),
]


def ping_space(name: str, hf_token: str = None) -> str:
    """Ping a space to keep it alive (GET the API endpoint)."""
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{name}/runtime"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    try:
        r = requests.get(url, timeout=10, headers=headers)
        d = r.json() if r.status_code == 200 else {}
        stage = d.get("stage", "UNKNOWN").upper()
        if "SLEEP" in stage:
            # Restart it
            restart_url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{name}/restart"
            if hf_token:
                requests.post(restart_url, headers=headers, timeout=10)
            return f"WOKE ({stage}→STARTING)"
        return stage
    except Exception as e:
        return f"ERROR: {e}"


def keep_alive(max_priority: int = 2, interval: int = 600, hf_token: str = None):
    targets = [(name, p, desc) for name, p, desc in PRIORITY_NODES if p <= max_priority]
    print(f"\n☉ Keep-Alive Scheduler | Priority ≤{max_priority} | {len(targets)} nodes | interval={interval}s")
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).isoformat()
        print(f"\n--- Ping Cycle {cycle} [{ts}] ---")
        for name, priority, desc in targets:
            status = ping_space(name, hf_token)
            icon = "✅" if status == "RUNNING" else "💤" if "SLEEP" in status else "🔄" if "WOKE" in status else "⚠️"
            print(f"  {icon} P{priority} {name}: {status}")
            time.sleep(0.5)
        print(f"  Next ping in {interval}s...")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA Node Keep-Alive Scheduler")
    parser.add_argument("--priority", type=int, default=2, help="Max priority level to keep alive (1-5)")
    parser.add_argument("--interval", type=int, default=600, help="Ping interval in seconds (default: 600)")
    parser.add_argument("--ping-all", action="store_true", help="Ping all priority nodes once")
    args = parser.parse_args()
    hf_token = os.environ.get("HF_TOKEN")
    if args.ping_all:
        for name, p, desc in PRIORITY_NODES:
            if p <= args.priority:
                status = ping_space(name, hf_token)
                print(f"  P{p} {name}: {status}")
    else:
        keep_alive(args.priority, args.interval, hf_token)


if __name__ == "__main__":
    main()
