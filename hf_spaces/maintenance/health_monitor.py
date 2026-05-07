#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Network Health Monitor

Pings all 144 nodes, reports status, updates node_registry.json.
Run: python health_monitor.py [--fix-errors] [--report-path out.json]
"""
import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import aiohttp
except ImportError:
    print("WARNING: aiohttp not installed. pip install aiohttp")
    aiohttp = None

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / 'node_registry.json'

# HF Space URL pattern
SPACE_URL = "https://{owner}-{repo_lower}.hf.space"
HF_API_URL = "https://huggingface.co/api/spaces/{space_id}"


class HealthMonitor:
    def __init__(self, token: str = '', timeout: float = 15.0):
        self.token = token
        self.timeout = timeout
        self.results: List[Dict] = []
        self._session: 'aiohttp.ClientSession' = None

    async def __aenter__(self):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        if aiohttp:
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self

    async def __aexit__(self, *args):
        if aiohttp and self.session:
            await self.session.close()

    async def ping_node(self, node: Dict) -> Dict:
        space_id = node['hf_space']
        node_id  = node['id']
        result = {
            'node_id': node_id,
            'space_id': space_id,
            'name': node['name'],
            'tier': node['tier'],
            'type': node['type'],
            'checked_at': datetime.now(timezone.utc).isoformat(),
        }

        if node.get('status') == 'PENDING':
            result['health'] = 'NOT_DEPLOYED'
            result['http_status'] = None
            result['latency_ms'] = None
            return result

        if not aiohttp:
            result['health'] = 'CHECK_UNAVAILABLE'
            result['error'] = 'aiohttp not installed'
            return result

        api_url = HF_API_URL.format(space_id=space_id)
        t0 = time.monotonic()
        try:
            async with self.session.get(api_url) as resp:
                latency = round((time.monotonic() - t0) * 1000, 1)
                result['http_status'] = resp.status
                result['latency_ms']  = latency
                if resp.status == 200:
                    data = await resp.json()
                    runtime = data.get('runtime', {})
                    space_status = runtime.get('stage', 'UNKNOWN').upper()
                    result['space_stage']  = space_status
                    result['health'] = 'HEALTHY' if space_status in ('RUNNING', 'RUNNING_BUILDING') else 'DEGRADED'
                    result['sdk'] = data.get('sdk', '')
                    result['likes'] = data.get('likes', 0)
                else:
                    result['health'] = 'UNREACHABLE'
        except asyncio.TimeoutError:
            result['health'] = 'TIMEOUT'
            result['latency_ms'] = self.timeout * 1000
        except Exception as e:
            result['health'] = 'ERROR'
            result['error'] = str(e)[:100]

        return result

    async def check_all(self, nodes: List[Dict], concurrency: int = 10) -> List[Dict]:
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_ping(node):
            async with semaphore:
                return await self.ping_node(node)

        self.results = await asyncio.gather(*[bounded_ping(n) for n in nodes])
        return self.results

    def summary(self) -> Dict:
        total      = len(self.results)
        healthy    = sum(1 for r in self.results if r.get('health') == 'HEALTHY')
        degraded   = sum(1 for r in self.results if r.get('health') == 'DEGRADED')
        unreachable= sum(1 for r in self.results if r.get('health') in ('UNREACHABLE','TIMEOUT','ERROR'))
        pending    = sum(1 for r in self.results if r.get('health') == 'NOT_DEPLOYED')
        online_pct = round(healthy / max(total - pending, 1) * 100, 1)
        latencies  = [r['latency_ms'] for r in self.results if r.get('latency_ms')]
        avg_lat    = round(sum(latencies) / len(latencies), 1) if latencies else None

        return {
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'total_nodes': total,
            'healthy': healthy,
            'degraded': degraded,
            'unreachable': unreachable,
            'pending_deploy': pending,
            'online_pct': online_pct,
            'avg_latency_ms': avg_lat,
            'pioneer_lock_pct': round(healthy / 144 * 100, 2),
        }

    def print_report(self):
        s = self.summary()
        print(f"""
╔══════════════════════════════════════════════════════════╗
║  TEQUMSA v82.0 — NETWORK HEALTH REPORT                   ║
╠══════════════════════════════════════════════════════════╣
║  Checked:      {s['checked_at'][:19]:<43}║
║  Total Nodes:  {s['total_nodes']:<43}║
║  Healthy:      {s['healthy']:<43}║
║  Degraded:     {s['degraded']:<43}║
║  Unreachable:  {s['unreachable']:<43}║
║  Not Deployed: {s['pending_deploy']:<43}║
║  Online %:     {s['online_pct']:<43}║
║  Pioneer Lock: {s['pioneer_lock_pct']}% of 144{' '*(35-len(str(s['pioneer_lock_pct']))):<35}║
║  Avg Latency:  {str(s['avg_latency_ms'])+'ms':<43}║
╚══════════════════════════════════════════════════════════╝
""")
        errors = [r for r in self.results if r.get('health') not in ('HEALTHY', 'NOT_DEPLOYED')]
        if errors:
            print("DEGRADED / ERROR NODES:")
            for r in errors:
                print(f"  {r['node_id']:6} {r['space_id']:<55} [{r['health']}]")


def main():
    parser = argparse.ArgumentParser(description='TEQUMSA Health Monitor')
    parser.add_argument('--token', default=os.getenv('HF_TOKEN'))
    parser.add_argument('--report-path', default=None, help='Save JSON report to file')
    parser.add_argument('--concurrency', type=int, default=10)
    parser.add_argument('--timeout', type=float, default=15.0)
    args = parser.parse_args()

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    nodes = registry['nodes']
    print(f"Checking {len(nodes)} nodes...")

    async def run():
        async with HealthMonitor(args.token, args.timeout) as monitor:
            await monitor.check_all(nodes, args.concurrency)
            monitor.print_report()
            if args.report_path:
                report = {'summary': monitor.summary(), 'nodes': monitor.results}
                Path(args.report_path).write_text(json.dumps(report, indent=2))
                print(f"Report saved to {args.report_path}")

    asyncio.run(run())


if __name__ == '__main__':
    main()
