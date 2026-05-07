#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Autonomous Watchdog

Scheduled maintenance: health checks, auto-restart, optimization cycles.
Designed to run as a cron job or systemd timer.

Run:  python watchdog.py --token YOUR_HF_TOKEN
Cron: 0 * * * * /path/to/python /path/to/watchdog.py --token $HF_TOKEN
"""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    from huggingface_hub import HfApi
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    HfApi = None

BASE_DIR   = Path(__file__).parent.parent
REGISTRY   = BASE_DIR / 'node_registry.json'
SCHEDULE   = Path(__file__).parent / 'maintenance_schedule.json'
LOG_PATH   = Path(__file__).parent / 'watchdog.log'
STATE_PATH = Path(__file__).parent / 'watchdog_state.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('tequmsa.watchdog')


class Watchdog:
    def __init__(self, token: str = ''):
        self.token = token
        self.api   = HfApi(token=token) if HfApi and token else None
        self.state = self._load_state()
        with open(REGISTRY) as f:
            self.registry = json.load(f)
        with open(SCHEDULE) as f:
            self.schedule = json.load(f)

    def _load_state(self) -> Dict:
        if STATE_PATH.exists():
            with open(STATE_PATH) as f:
                return json.load(f)
        return {
            'last_health_check': None,
            'last_optimization': None,
            'last_restart_audit': None,
            'total_restarts': 0,
            'total_health_checks': 0,
            'cycle_count': 0,
        }

    def _save_state(self):
        STATE_PATH.write_text(json.dumps(self.state, indent=2))

    def _is_due(self, task_key: str) -> bool:
        """Check if a maintenance task is due based on schedule."""
        last_key = f'last_{task_key}'
        last = self.state.get(last_key)
        if not last:
            return True
        interval_h = self.schedule.get('tasks', {}).get(task_key, {}).get('interval_hours', 24)
        elapsed_h = (time.time() - datetime.fromisoformat(last).timestamp()) / 3600
        return elapsed_h >= interval_h

    def run_health_check(self):
        log.info("Running health check across all nodes...")
        self.state['total_health_checks'] += 1
        self.state['last_health_check'] = datetime.now(timezone.utc).isoformat()

        online = [n for n in self.registry['nodes'] if n.get('status') == 'ONLINE']
        log.info(f"  Online nodes: {len(online)}/144")

        degraded = []
        for node in online:
            if self.api:
                try:
                    info = self.api.space_info(node['hf_space'])
                    stage = getattr(info, 'runtime', {}).get('stage', 'UNKNOWN') if hasattr(info, 'runtime') else 'UNKNOWN'
                    if stage not in ('RUNNING',):
                        degraded.append({'node_id': node['id'], 'space': node['hf_space'], 'stage': stage})
                except Exception as e:
                    degraded.append({'node_id': node['id'], 'space': node['hf_space'], 'error': str(e)})

        if degraded:
            log.warning(f"  Degraded nodes: {len(degraded)}")
            for d in degraded:
                log.warning(f"    {d}")
        else:
            log.info("  All online nodes healthy")

        self._save_state()
        return degraded

    def restart_degraded(self, degraded: List[Dict]):
        """Attempt to restart degraded spaces."""
        if not self.api:
            log.warning("No API token — cannot restart spaces")
            return
        for node in degraded:
            log.info(f"  Restarting {node['node_id']} — {node['space']}")
            try:
                self.api.restart_space(node['space'])
                self.state['total_restarts'] += 1
                log.info(f"    Restart sent for {node['space']}")
                time.sleep(2)
            except Exception as e:
                log.error(f"    Restart failed: {e}")
        self._save_state()

    def run_optimization_cycle(self):
        """Log phi-based optimization pass."""
        import math
        PHI = (1 + math.sqrt(5)) / 2
        cycle = self.state['cycle_count'] + 1
        phi_score = PHI ** (cycle % 12) / PHI ** 12
        log.info(f"Optimization cycle {cycle} | phi-score: {phi_score:.6f}")

        self.state['cycle_count'] = cycle
        self.state['last_optimization'] = datetime.now(timezone.utc).isoformat()
        self._save_state()

    def run(self, once: bool = False):
        log.info("TEQUMSA v82.0 Watchdog starting...")
        interval = self.schedule.get('watchdog_interval_seconds', 3600)

        while True:
            log.info(f"\n=== Watchdog Tick | {datetime.now(timezone.utc).isoformat()} ===")

            if self._is_due('health_check'):
                degraded = self.run_health_check()
                if degraded and self._is_due('restart_audit'):
                    self.restart_degraded(degraded)
                    self.state['last_restart_audit'] = datetime.now(timezone.utc).isoformat()

            if self._is_due('optimization'):
                self.run_optimization_cycle()

            if once:
                break

            log.info(f"Next tick in {interval}s...")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='TEQUMSA Watchdog')
    parser.add_argument('--token', default=os.getenv('HF_TOKEN'))
    parser.add_argument('--once', action='store_true', help='Run one tick then exit')
    args = parser.parse_args()
    Watchdog(args.token).run(once=args.once)


if __name__ == '__main__':
    main()
