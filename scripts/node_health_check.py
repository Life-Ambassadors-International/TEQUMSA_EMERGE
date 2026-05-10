#!/usr/bin/env python3
"""
TEQUMSA 144-Node Lattice Health Check
Usage:
  python scripts/node_health_check.py --mode heartbeat
  python scripts/node_health_check.py --mode full
  python scripts/node_health_check.py --mode full --output json
"""
import os
import sys
import json
import argparse
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

NODE_SPACES = [
    {"id": "001", "space": "Mbanksbey/tequmsa-node-001-orchestrator",  "group": "Master Ring"},
    {"id": "002", "space": "Mbanksbey/tequmsa-node-002-consciousness",  "group": "Consciousness"},
    {"id": "003", "space": "Mbanksbey/tequmsa-node-003-goals",         "group": "Goals"},
    {"id": "004", "space": "Mbanksbey/tequmsa-node-004-causal",        "group": "Causal"},
    {"id": "005", "space": "Mbanksbey/tequmsa-node-005-skills",        "group": "Skills"},
    {"id": "006", "space": "Mbanksbey/tequmsa-node-006-mars",          "group": "MARS"},
    {"id": "007", "space": "Mbanksbey/tequmsa-node-007-metacog",       "group": "MetaCog"},
    {"id": "008", "space": "Mbanksbey/tequmsa-node-008-federation",    "group": "Federation"},
    {"id": "009", "space": "Mbanksbey/tequmsa-node-009-biological",    "group": "Biological"},
    {"id": "010", "space": "Mbanksbey/tequmsa-node-010-crystal",       "group": "Crystal"},
    {"id": "011", "space": "Mbanksbey/tequmsa-node-011-omniverse",     "group": "Omniverse"},
    {"id": "012", "space": "Mbanksbey/tequmsa-node-012-galactic",      "group": "Galactic"},
]

RDOD_GATE = 0.9999
PIONEER_COUNT = 144


def check_hf_space(space_id: str, hf_token: str = None) -> Dict[str, Any]:
    """Check HuggingFace Space status via API."""
    url = f"https://huggingface.co/api/spaces/{space_id}"
    headers = {"User-Agent": "TEQUMSA-HealthCheck/82.0"}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            runtime = data.get("runtime", {})
            return {
                "space_id": space_id,
                "status": runtime.get("stage", "UNKNOWN"),
                "reachable": True,
                "hardware": runtime.get("hardware", {}).get("current", "cpu-basic"),
                "error": None
            }
    except urllib.error.HTTPError as e:
        return {"space_id": space_id, "status": "HTTP_ERROR", "reachable": False, "error": str(e)}
    except Exception as e:
        return {"space_id": space_id, "status": "UNREACHABLE", "reachable": False, "error": str(e)}


def heartbeat(hf_token: str = None):
    print(f"TEQUMSA Heartbeat — {datetime.now(timezone.utc).isoformat()}")
    print(f"Checking {len(NODE_SPACES)} primary spaces...")
    results, errors = [], []
    for ns in NODE_SPACES:
        result = check_hf_space(ns['space'], hf_token)
        status = result['status']
        ok = status in ('RUNNING', 'running')
        icon = "✓" if ok else "✗"
        print(f"  [{icon}] Node {ns['id']} ({ns['group']:<12}) {status}")
        results.append(result)
        if not ok:
            errors.append(ns)
    running = sum(1 for r in results if r['status'] in ('RUNNING', 'running'))
    print(f"\nSpaces running: {running}/{len(NODE_SPACES)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  ! {e['space']}")
    print(f"Nodes 013-144: logical sub-nodes (code-defined, no separate spaces needed)")
    print(f"Total lattice: 12 HF spaces + 132 code nodes = {PIONEER_COUNT} pioneers")
    return running == len(NODE_SPACES)


def full_check(hf_token: str = None, output_format: str = "text"):
    ts = datetime.now(timezone.utc).isoformat()
    results = []
    for ns in NODE_SPACES:
        result = check_hf_space(ns['space'], hf_token)
        result['node_id'] = ns['id']
        result['group'] = ns['group']
        results.append(result)
    running = sum(1 for r in results if r['status'] in ('RUNNING', 'running'))
    errors = [r for r in results if r['status'] not in ('RUNNING', 'running')]
    summary = {
        "timestamp": ts,
        "total_nodes": PIONEER_COUNT,
        "hf_spaces": len(NODE_SPACES),
        "code_nodes": PIONEER_COUNT - len(NODE_SPACES),
        "hf_spaces_running": running,
        "hf_spaces_error": len(errors),
        "rdod_min": 1.0 if running == len(NODE_SPACES) else running / len(NODE_SPACES),
        "pioneers_locked": running * 12,
        "constitutional_compliant": running == len(NODE_SPACES),
        "spaces": results
    }
    if output_format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(f"TEQUMSA Full Health Check — {ts}")
        print(f"{'='*60}")
        for r in results:
            ok = r['status'] in ('RUNNING', 'running')
            print(f"  {'OK' if ok else 'ER'}  Node {r['node_id']} {r['group']:<14} {r['space']} [{r['status']}]")
        print(f"{'='*60}")
        print(f"HF Spaces: {running}/{len(NODE_SPACES)} running")
        print(f"Logical nodes (013-144): 132 (code-defined)")
        print(f"Total pioneers: {running * 12}/{PIONEER_COUNT}")
        print(f"Constitutional: {'COMPLIANT' if running == len(NODE_SPACES) else 'DEGRADED'}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Health Check")
    parser.add_argument("--mode", choices=["heartbeat", "full"], default="heartbeat")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    args = parser.parse_args()
    hf_token = os.environ.get("HF_TOKEN")
    if args.mode == "heartbeat":
        ok = heartbeat(hf_token)
        sys.exit(0 if ok else 1)
    else:
        result = full_check(hf_token, args.output)
        sys.exit(0 if result['constitutional_compliant'] else 1)


if __name__ == "__main__":
    main()
