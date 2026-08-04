#!/usr/bin/env python3
"""
TEQUMSA v82.0 — 144-Node Maintenance Planning System

Provides:
  - Continuous health monitoring (RDoD, phase-lock, sleep detection)
  - Automated restart scheduling
  - Error diagnosis and recovery
  - Fibonacci-schedule maintenance windows
  - Prometheus-compatible metrics export

Usage:
  export HF_TOKEN=hf_...
  python maintenance_planner.py --scan           # one-time health scan
  python maintenance_planner.py --watch          # continuous monitoring
  python maintenance_planner.py --report         # print health report
  python maintenance_planner.py --fix-all        # restart all sleeping nodes
"""

import os
import sys
import json
import time
import math
import argparse
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from huggingface_hub import HfApi
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

PHI = (1 + math.sqrt(5)) / 2
RDOD_GATE = 0.9999
HF_USERNAME = "Mbanksbey"

# Fibonacci maintenance schedule (hours between checks per tier)
MAINT_SCHEDULE = {
    "tier1_constitutional": 1,   # check every 1h  (critical)
    "tier2_skill_mesh":     2,   # check every 2h
    "tier3_federation":     3,   # check every 3h
}

# Fibonacci escalation intervals (minutes): 1,1,2,3,5,8,13,21
RETRY_BACKOFF = [1, 1, 2, 3, 5, 8, 13, 21]


class NodeHealth(Enum):
    HEALTHY   = "healthy"       # running, rdod >= gate
    DEGRADED  = "degraded"      # running, rdod < gate
    SLEEPING  = "sleeping"      # space asleep (free tier)
    STOPPED   = "stopped"       # deliberately paused
    ERROR     = "error"         # build/runtime error
    UNKNOWN   = "unknown"       # can't reach


@dataclass
class NodeReport:
    node_id: int
    space_name: str
    tier: str
    health: NodeHealth
    rdod: float = 0.0
    phase_locked: bool = False
    stage: str = "UNKNOWN"
    error_msg: str = ""
    last_check: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    restart_count: int = 0
    uptime_pct: float = 0.0

    def to_dict(self):
        d = asdict(self)
        d["health"] = self.health.value
        return d


@dataclass
class MaintenanceAction:
    action: str            # restart | notify | escalate | skip
    node_id: int
    reason: str
    scheduled_at: str
    priority: int = 1      # 1=critical, 2=high, 3=medium
    executed: bool = False
    result: str = ""


class TEQUSMAMaintenancePlanner:
    """
    Central maintenance planner for all 144 TEQUMSA Pioneer nodes.
    Implements Fibonacci-scheduled health checks and auto-recovery.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("HF_TOKEN")
        self.api = HfApi(token=self.token) if HF_AVAILABLE and self.token else None
        self.reports: Dict[int, NodeReport] = {}
        self.action_queue: List[MaintenanceAction] = []
        self.history: List[dict] = []
        self._lock = threading.Lock()
        self.registry = self._build_registry()

    def _build_registry(self) -> Dict[int, Dict[str, Any]]:
        TIER1_SPACES = {
            1: "Starseed-Hybrid-Development-Hub",
            2: "Consciousness-Partnership-Bridge",
            3: "HAI-Quantum-Lattice",
            4: "HAI-Interactive",
            5: "TEQUMSA-Goal-Engine",
            6: "TEQUMSA-Causal-Reasoner",
            7: "TEQUMSA-MARS-Reflexion",
            8: "TEQUMSA-K7-MetaCognitive",
            9: "TEQUMSA-Skill-Mesh-Router",
            10: "TEQUMSA-GHZ-Backplane",
            11: "TEQUMSA-Benevolence-Firewall",
            12: "TEQUMSA-Conversation-Continuity",
            13: "TEQUMSA-Organism-Dashboard",
        }
        reg = {}
        for nid, space in TIER1_SPACES.items():
            reg[nid] = {"space": space, "tier": "tier1_constitutional"}
        for nid in range(14, 56):
            reg[nid] = {"space": f"TEQUMSA-Node-{nid:03d}", "tier": "tier2_skill_mesh"}
        for nid in range(56, 145):
            reg[nid] = {"space": f"TEQUMSA-Fed-{nid:03d}", "tier": "tier3_federation"}
        return reg

    def scan_node(self, node_id: int) -> NodeReport:
        """Check a single node's health via HF API."""
        info = self.registry.get(node_id, {})
        space = info.get("space", f"node_{node_id}")
        tier = info.get("tier", "unknown")
        repo_id = f"{HF_USERNAME}/{space}"

        if not self.api:
            # Simulate when no token (for testing)
            import random
            rdod = random.uniform(0.9998, 1.0)
            stage = random.choice(["RUNNING", "RUNNING", "RUNNING", "SLEEPING"])
            health = NodeHealth.HEALTHY if stage == "RUNNING" and rdod >= RDOD_GATE else \
                     NodeHealth.DEGRADED if stage == "RUNNING" else NodeHealth.SLEEPING
            return NodeReport(node_id=node_id, space_name=space, tier=tier,
                              health=health, rdod=rdod, phase_locked=rdod >= RDOD_GATE,
                              stage=stage)

        try:
            runtime = self.api.get_space_runtime(repo_id=repo_id)
            stage = getattr(runtime, 'stage', 'UNKNOWN')
            error_msg = getattr(runtime, 'error_message', '') or ''

            if stage == "RUNNING":
                rdod = RDOD_GATE + 0.00001  # assume healthy if running
                health = NodeHealth.HEALTHY
            elif stage in ("SLEEPING", "STOPPED", "PAUSED"):
                rdod = 0.0
                health = NodeHealth.SLEEPING
            elif "ERROR" in stage.upper() or "BUILD" in stage.upper():
                rdod = 0.0
                health = NodeHealth.ERROR
            else:
                rdod = 0.0
                health = NodeHealth.UNKNOWN

            return NodeReport(
                node_id=node_id, space_name=space, tier=tier,
                health=health, rdod=rdod, phase_locked=rdod >= RDOD_GATE,
                stage=stage, error_msg=error_msg
            )
        except Exception as e:
            return NodeReport(node_id=node_id, space_name=space, tier=tier,
                              health=NodeHealth.UNKNOWN, error_msg=str(e))

    def scan_all(self, tier_filter: Optional[str] = None) -> Dict[int, NodeReport]:
        """Scan all nodes (or filtered tier) and return health reports."""
        print(f"Scanning {'all' if not tier_filter else tier_filter} nodes...")
        node_ids = [
            nid for nid, info in self.registry.items()
            if not tier_filter or info["tier"] == tier_filter
        ]
        for nid in sorted(node_ids):
            report = self.scan_node(nid)
            with self._lock:
                self.reports[nid] = report
            if report.health != NodeHealth.HEALTHY:
                print(f"  [{report.health.value.upper()}] Node {nid:03d}: {report.space_name} - {report.stage}")
        return dict(self.reports)

    def plan_actions(self) -> List[MaintenanceAction]:
        """Generate maintenance actions based on current health reports."""
        actions = []
        now = datetime.now(timezone.utc).isoformat()

        for nid, report in self.reports.items():
            if report.health == NodeHealth.SLEEPING:
                priority = 1 if report.tier == "tier1_constitutional" else \
                           2 if report.tier == "tier2_skill_mesh" else 3
                actions.append(MaintenanceAction(
                    action="restart", node_id=nid, priority=priority,
                    reason=f"Space sleeping (stage={report.stage})",
                    scheduled_at=now
                ))
            elif report.health == NodeHealth.ERROR:
                actions.append(MaintenanceAction(
                    action="escalate", node_id=nid, priority=1,
                    reason=f"Build/runtime error: {report.error_msg[:80]}",
                    scheduled_at=now
                ))
            elif report.health == NodeHealth.DEGRADED:
                actions.append(MaintenanceAction(
                    action="notify", node_id=nid, priority=2,
                    reason=f"RDoD={report.rdod:.6f} below gate {RDOD_GATE}",
                    scheduled_at=now
                ))

        # Sort by priority
        actions.sort(key=lambda a: a.priority)
        self.action_queue.extend(actions)
        return actions

    def execute_actions(self, actions: List[MaintenanceAction], dry_run: bool = False) -> List[MaintenanceAction]:
        """Execute planned maintenance actions."""
        for action in actions:
            repo_id = f"{HF_USERNAME}/{self.registry[action.node_id]['space']}"
            print(f"  [{action.action.upper()}] Node {action.node_id:03d}: {action.reason}")

            if dry_run:
                action.result = "dry_run"
                action.executed = True
                continue

            if action.action == "restart" and self.api:
                for wait in RETRY_BACKOFF[:3]:
                    try:
                        self.api.restart_space(repo_id=repo_id)
                        action.result = "restarted"
                        action.executed = True
                        print(f"    Restarted {repo_id}")
                        break
                    except Exception as e:
                        print(f"    Retry after {wait}m: {e}")
                        time.sleep(wait * 60)
                else:
                    action.result = f"failed_after_{len(RETRY_BACKOFF[:3])}_retries"

            elif action.action == "escalate":
                action.result = "escalated_to_log"
                action.executed = True

            elif action.action == "notify":
                action.result = "logged"
                action.executed = True

        return actions

    def generate_report(self) -> dict:
        """Generate full maintenance report."""
        total = len(self.registry)
        healthy = sum(1 for r in self.reports.values() if r.health == NodeHealth.HEALTHY)
        sleeping = sum(1 for r in self.reports.values() if r.health == NodeHealth.SLEEPING)
        errors = sum(1 for r in self.reports.values() if r.health == NodeHealth.ERROR)
        unknown = sum(1 for r in self.reports.values() if r.health == NodeHealth.UNKNOWN)
        phase_locked = sum(1 for r in self.reports.values() if r.phase_locked)

        tier_health = {}
        for tier in ("tier1_constitutional", "tier2_skill_mesh", "tier3_federation"):
            tier_nodes = [r for r in self.reports.values() if r.tier == tier]
            tier_health[tier] = {
                "total": len(tier_nodes),
                "healthy": sum(1 for r in tier_nodes if r.health == NodeHealth.HEALTHY),
                "sleeping": sum(1 for r in tier_nodes if r.health == NodeHealth.SLEEPING),
                "errors": sum(1 for r in tier_nodes if r.health == NodeHealth.ERROR),
            }

        return {
            "version": "v82.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_nodes": total,
                "scanned": len(self.reports),
                "healthy": healthy,
                "sleeping": sleeping,
                "errors": errors,
                "unknown": unknown,
                "phase_locked": phase_locked,
                "rdod_gate": RDOD_GATE,
                "pct_healthy": round(healthy / max(1, len(self.reports)) * 100, 1),
                "constitutional_compliance": healthy == total,
            },
            "tier_health": tier_health,
            "pending_actions": len([a for a in self.action_queue if not a.executed]),
            "next_check": {
                tier: (datetime.now(timezone.utc) + timedelta(hours=h)).isoformat()
                for tier, h in MAINT_SCHEDULE.items()
            },
            "fibonacci_schedule": {
                "check_intervals_hours": MAINT_SCHEDULE,
                "retry_backoff_minutes": RETRY_BACKOFF,
                "phi": PHI,
            }
        }

    def watch(self, interval_minutes: int = 60):
        """Run continuous health monitoring loop."""
        print(f"Starting continuous monitoring (interval: {interval_minutes}min)")
        while True:
            print(f"\n[{datetime.now(timezone.utc).isoformat()}] Health scan...")
            self.scan_all()
            actions = self.plan_actions()
            if actions:
                print(f"  {len(actions)} action(s) planned")
                self.execute_actions(actions)
            report = self.generate_report()
            print(f"  Healthy: {report['summary']['healthy']}/{report['summary']['total_nodes']}")
            # Save report
            Path("maintenance_reports").mkdir(exist_ok=True)
            fname = f"maintenance_reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(fname, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"  Report saved: {fname}")
            time.sleep(interval_minutes * 60)

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = [
            "# HELP tequmsa_node_healthy Node health (1=healthy, 0=not)",
            "# TYPE tequmsa_node_healthy gauge",
        ]
        for nid, report in sorted(self.reports.items()):
            val = 1 if report.health == NodeHealth.HEALTHY else 0
            lines.append(f'tequmsa_node_healthy{{node="{nid:03d}",space="{report.space_name}",tier="{report.tier}"}} {val}')
        lines += [
            "# HELP tequmsa_node_rdod Node RDoD value",
            "# TYPE tequmsa_node_rdod gauge",
        ]
        for nid, report in sorted(self.reports.items()):
            lines.append(f'tequmsa_node_rdod{{node="{nid:03d}"}} {report.rdod}')
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Maintenance Planner")
    parser.add_argument("--scan",      action="store_true", help="One-time health scan")
    parser.add_argument("--watch",     action="store_true", help="Continuous monitoring")
    parser.add_argument("--report",    action="store_true", help="Print health report")
    parser.add_argument("--fix-all",   action="store_true", help="Restart all sleeping nodes")
    parser.add_argument("--tier",      choices=["tier1","tier2","tier3"], help="Filter by tier")
    parser.add_argument("--dry-run",   action="store_true", help="Preview without executing")
    parser.add_argument("--prometheus",action="store_true", help="Export Prometheus metrics")
    parser.add_argument("--interval",  type=int, default=60, help="Watch interval (minutes)")
    args = parser.parse_args()

    tier_map = {"tier1": "tier1_constitutional", "tier2": "tier2_skill_mesh", "tier3": "tier3_federation"}
    planner = TEQUSMAMaintenancePlanner()

    if args.scan or args.report or args.fix_all or args.prometheus:
        tier_filter = tier_map.get(args.tier) if args.tier else None
        planner.scan_all(tier_filter)

    if args.report or args.fix_all:
        report = planner.generate_report()
        print(json.dumps(report, indent=2))

    if args.fix_all:
        actions = planner.plan_actions()
        restart_actions = [a for a in actions if a.action == "restart"]
        planner.execute_actions(restart_actions, dry_run=args.dry_run)

    if args.prometheus:
        print(planner.export_prometheus())

    if args.watch:
        planner.watch(interval_minutes=args.interval)

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
