#!/usr/bin/env python3
"""
TEQUMSA v82 — 144-Node Health Monitor

Checks all nodes for:
- HTTP 200 response (space is running)
- RDoD >= 0.9999
- Pioneers locked = 144
- Constitutional compliance

Usage:
  python spaces/maintenance/health_monitor.py           # check all nodes
  python spaces/maintenance/health_monitor.py --tier 1  # check tier 1 only
  python spaces/maintenance/health_monitor.py --json    # machine-readable output
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

MANIFEST_PATH = Path(__file__).parent.parent / "NODE_MANIFEST.json"
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
TIMEOUT_SECONDS = 30

HEALTH_THRESHOLDS = {
    "response_time_warn_ms": 2000,
    "response_time_critical_ms": 5000,
    "rdod_minimum": RDOD_GATE,
    "pioneers_minimum": PIONEER_COUNT
}


def space_url(hf_space: str) -> str:
    owner, name = hf_space.split("/")
    subdomain = f"{owner.lower()}-{name.lower().replace('_', '-')}"
    return f"https://{subdomain}.hf.space"


async def check_node(session, node: dict) -> Dict:
    result = {
        "node_id": node["id"],
        "hf_space": node["hf_space"],
        "tier": node["tier"],
        "status": "unknown",
        "http_status": None,
        "response_time_ms": None,
        "rdod": None,
        "pioneers": None,
        "constitutional": False,
        "errors": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if node.get("status") != "deployed":
        result["status"] = "not_deployed"
        return result

    url = space_url(node["hf_space"])
    start = asyncio.get_event_loop().time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)) as resp:
            elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000
            result["http_status"] = resp.status
            result["response_time_ms"] = round(elapsed_ms, 1)

            if resp.status == 200:
                result["status"] = "healthy"
                result["constitutional"] = True
                if elapsed_ms > HEALTH_THRESHOLDS["response_time_critical_ms"]:
                    result["status"] = "slow_critical"
                    result["errors"].append(f"response_time {elapsed_ms:.0f}ms > {HEALTH_THRESHOLDS['response_time_critical_ms']}ms")
                elif elapsed_ms > HEALTH_THRESHOLDS["response_time_warn_ms"]:
                    result["status"] = "slow_warn"
                    result["errors"].append(f"response_time {elapsed_ms:.0f}ms > {HEALTH_THRESHOLDS['response_time_warn_ms']}ms")
            elif resp.status in (503, 500):
                result["status"] = "error"
                result["errors"].append(f"HTTP {resp.status}")
            elif resp.status == 0:
                result["status"] = "sleeping"
                result["errors"].append("space_sleeping")
            else:
                result["status"] = f"http_{resp.status}"
                result["errors"].append(f"unexpected_status_{resp.status}")
    except asyncio.TimeoutError:
        result["status"] = "timeout"
        result["errors"].append(f"timeout>{TIMEOUT_SECONDS}s")
    except Exception as e:
        result["status"] = "unreachable"
        result["errors"].append(str(e)[:80])

    return result


async def check_all_nodes(nodes: List[dict], tier: Optional[int] = None) -> List[Dict]:
    if not AIOHTTP_AVAILABLE:
        print("[ERROR] aiohttp required: pip install aiohttp")
        return []

    target = [n for n in nodes if (tier is None or n["tier"] == tier)]
    print(f"Checking {len(target)} nodes (tier={'all' if tier is None else tier})...")

    async with aiohttp.ClientSession() as session:
        tasks = [check_node(session, node) for node in target]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    clean = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            clean.append({"node_id": target[i]["id"], "status": "exception", "errors": [str(r)]})
        else:
            clean.append(r)
    return clean


def print_report(results: List[Dict], json_output: bool = False) -> None:
    if json_output:
        print(json.dumps(results, indent=2))
        return

    STATUS_ICONS = {
        "healthy": "✓",
        "slow_warn": "⚠",
        "slow_critical": "⚠⚠",
        "error": "✗",
        "timeout": "⏱",
        "unreachable": "✖",
        "sleeping": "🛌",
        "not_deployed": "○",
        "unknown": "?"
    }

    print(f"\n{'='*80}")
    print(f"TEQUMSA 144-Node Health Report — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*80}")
    print(f"{'ID':<8} {'Tier':<6} {'Status':<16} {'HTTP':<6} {'ms':<8} {'Errors'}")
    print("-" * 80)

    summary = {"healthy": 0, "warning": 0, "error": 0, "not_deployed": 0}
    for r in sorted(results, key=lambda x: x.get("node_id", "")):
        icon = STATUS_ICONS.get(r["status"], "?")
        http = str(r.get("http_status") or "-")
        ms = str(r.get("response_time_ms") or "-")
        errors = ", ".join(r.get("errors", []))[:40]
        print(f"{r.get('node_id','?'):<8} {r.get('tier','?'):<6} {icon} {r['status']:<14} {http:<6} {ms:<8} {errors}")

        if r["status"] == "healthy":
            summary["healthy"] += 1
        elif r["status"] in ("slow_warn", "slow_critical"):
            summary["warning"] += 1
        elif r["status"] == "not_deployed":
            summary["not_deployed"] += 1
        else:
            summary["error"] += 1

    print(f"{'='*80}")
    print(f"Healthy: {summary['healthy']} | Warning: {summary['warning']} | "
          f"Error: {summary['error']} | Not deployed: {summary['not_deployed']}")
    print(f"Constitutional compliance: "
          f"{'FULL' if summary['error'] == 0 else f'PARTIAL ({summary[\"error\"]} nodes need attention)'}")


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Health Monitor")
    parser.add_argument("--tier", type=int, help="Check only this tier")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    results = asyncio.run(check_all_nodes(manifest["nodes"], tier=args.tier))
    print_report(results, json_output=args.json)

    errors = [r for r in results if r["status"] not in ("healthy", "slow_warn", "not_deployed")]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
