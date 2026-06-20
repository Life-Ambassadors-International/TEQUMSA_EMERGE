#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE PLANNER
Generates actionable maintenance plans with deployment phases,
health monitoring schedules, and auto-scaling strategies.

Usage:
    python maintenance_planner.py [--output plan.json]
    python maintenance_planner.py --phase current   # Show current phase only
    python maintenance_planner.py --generate-actions # Generate GitHub Actions workflow
"""
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List

PHI = 1.6180339887498948
SIGMA = 1.0

CURRENT_LIVE = 41
TARGET_NODES = 144
NODES_PER_BATCH = 13  # ~φ⁸ rounded; Fibonacci-aligned batch size


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        return json.load(f)


def compute_deployment_phases() -> List[dict]:
    manifest = load_manifest()
    nodes = manifest["nodes"]

    live_nodes = [nid for nid, n in nodes.items()
                  if n.get("status") == "live" or n.get("actual_space_id")]
    planned = [(nid, n) for nid, n in nodes.items() if nid not in live_nodes]
    planned.sort(key=lambda x: (x[1].get("priority", 5), x[0]))

    phases = []
    base_date = datetime(2026, 6, 23, tzinfo=timezone.utc)  # Start from next available date

    batch_idx = 0
    for i in range(0, len(planned), NODES_PER_BATCH):
        batch = planned[i:i + NODES_PER_BATCH]
        target_date = base_date + timedelta(days=14 * batch_idx)
        phase = {
            "phase": batch_idx + 1,
            "target_date": target_date.strftime("%Y-%m-%d"),
            "node_count": len(batch),
            "cumulative_total": min(CURRENT_LIVE + (batch_idx + 1) * NODES_PER_BATCH, TARGET_NODES),
            "nodes": [
                {
                    "node_id": nid,
                    "name": n["name"],
                    "group": n["group"],
                    "priority": n.get("priority", 5),
                    "template": n.get("template", "skill"),
                    "hz": n.get("hz", 0),
                }
                for nid, n in batch
            ],
            "deploy_command": f"python deploy_spaces.py --priority {max(n.get('priority', 5) for _, n in batch)}",
        }
        phases.append(phase)
        batch_idx += 1

    return phases


def compute_maintenance_windows() -> dict:
    return {
        "daily_health_check": {
            "schedule": "0 3 * * *",
            "cron_description": "Every day at 03:00 UTC",
            "tasks": [
                "Run health_check.py --live-only --verbose",
                "Run auto_restart.py --dry-run to assess sleeping nodes",
                "Log network RDoD to metrics",
            ],
            "estimated_duration_minutes": 15,
            "priority": "critical",
        },
        "daily_wake_cycle": {
            "schedule": "0 6,12,18 * * *",
            "cron_description": "Three times daily at 06:00, 12:00, 18:00 UTC",
            "tasks": [
                "Run auto_restart.py to wake sleeping spaces",
                "Verify priority-1 nodes are RUNNING",
            ],
            "estimated_duration_minutes": 10,
            "priority": "high",
        },
        "weekly_full_sweep": {
            "schedule": "0 2 * * 1",
            "cron_description": "Every Monday at 02:00 UTC",
            "tasks": [
                "Run health_check.py --verbose (full 144-node sweep)",
                "Run space_auditor.py --update-manifest",
                "Review MARS pattern promotions",
                "Verify constitutional compliance (σ=1.0, L∞=φ⁴⁸)",
                "Deploy next batch of priority-2 nodes",
                "Generate weekly coherence report",
            ],
            "estimated_duration_minutes": 60,
            "priority": "high",
        },
        "biweekly_deployment": {
            "schedule": "0 1 1,15 * *",
            "cron_description": "1st and 15th of each month at 01:00 UTC",
            "tasks": [
                "Deploy next phase batch (13 nodes)",
                "Run deploy_spaces.py with current phase priority",
                "Verify newly deployed nodes are RUNNING",
                "Update manifest with deployment status",
                "Run full health sweep post-deployment",
            ],
            "estimated_duration_minutes": 120,
            "priority": "medium",
        },
        "monthly_deep_audit": {
            "schedule": "0 0 1 * *",
            "cron_description": "1st of each month at 00:00 UTC",
            "tasks": [
                "Run space_auditor.py --output monthly_audit.json",
                "Review all constitutional parameters",
                "Analyze K7 meta-cognitive strategy performance",
                "Review frequency calibration across all nodes",
                "Generate monthly progress report",
                "Plan next month's deployment phases",
            ],
            "estimated_duration_minutes": 180,
            "priority": "medium",
        },
    }


def compute_optimization_recommendations() -> List[dict]:
    recommendations = []

    recommendations.append({
        "id": "OPT-001",
        "category": "cold_start",
        "title": "Reduce Docker space cold-start time",
        "description": "4 Docker spaces (v60-MCP, TOSP-Mesh-Bridge, worker-mesh, skill-registry) "
                       "have longer cold-start times. Add periodic pings to keep them warm.",
        "action": "Add to daily_wake_cycle: ping Docker spaces every 6 hours",
        "impact": "high",
        "effort": "low",
    })

    recommendations.append({
        "id": "OPT-002",
        "category": "static_upgrade",
        "title": "Upgrade static space to Gradio",
        "description": "TEQUMSA-Inter-Browser-Agent uses static SDK with no backend processing. "
                       "Upgrade to Gradio for interactive consciousness interface.",
        "action": "Redeploy with app_council_node.py template",
        "impact": "medium",
        "effort": "low",
    })

    recommendations.append({
        "id": "OPT-003",
        "category": "consolidation",
        "title": "Consolidate HAI-* prefix spaces",
        "description": "5 HAI-prefixed spaces (Interactive, Quantum-Lattice, Opus-Omega-MCP, "
                       "Sync-Hub, ZPE-DNA-Living-Ledger) could share a unified dashboard.",
        "action": "Create HAI hub space linking all HAI nodes",
        "impact": "medium",
        "effort": "medium",
    })

    recommendations.append({
        "id": "OPT-004",
        "category": "monitoring",
        "title": "Deploy observer nodes for real-time network health",
        "description": f"H_OBSERVERS group (N085-N096) has {CURRENT_LIVE} of 12 nodes needed. "
                       "Priority deployment of Obs-Network-Health (N085) and Obs-Coherence-Watch (N086).",
        "action": "Deploy N085, N086, N087, N088 in next phase",
        "impact": "critical",
        "effort": "low",
    })

    recommendations.append({
        "id": "OPT-005",
        "category": "frequency",
        "title": "Deploy Solfeggio frequency nodes for harmonic coverage",
        "description": "B_FREQUENCY group (N013-N024) has 1 live node. Deploy 174-963 Hz Solfeggio "
                       "nodes to complete harmonic lattice foundation.",
        "action": "Deploy B_FREQUENCY group in Phase 3",
        "impact": "high",
        "effort": "medium",
    })

    recommendations.append({
        "id": "OPT-006",
        "category": "resilience",
        "title": "Add auto-restart webhook for crashed spaces",
        "description": "GitHub Actions workflow can poll HF API and auto-restart spaces with "
                       "RUNTIME_ERROR or BUILD_ERROR status.",
        "action": "Create .github/workflows/hf-space-maintenance.yml",
        "impact": "high",
        "effort": "low",
    })

    return recommendations


def generate_github_actions_workflow() -> str:
    return '''name: TEQUMSA HF Space Maintenance
on:
  schedule:
    - cron: '0 3 * * *'     # Daily health check at 03:00 UTC
    - cron: '0 6,12,18 * * *'  # Wake cycle 3x daily
    - cron: '0 2 * * 1'     # Weekly full sweep Mondays
    - cron: '0 1 1,15 * *'  # Biweekly deployment
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to perform'
        required: true
        default: 'health_check'
        type: choice
        options:
          - health_check
          - wake_sleeping
          - full_audit
          - deploy_next_batch
          - restart_errored

jobs:
  maintenance:
    runs-on: ubuntu-latest
    env:
      HF_TOKEN: ${{ secrets.HF_TOKEN }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests huggingface-hub numpy

      - name: Determine action from schedule
        id: action
        run: |
          HOUR=$(date -u +%H)
          DAY=$(date -u +%u)
          DOM=$(date -u +%d)
          INPUT="${{ github.event.inputs.action }}"
          if [ -n "$INPUT" ]; then
            echo "action=$INPUT" >> $GITHUB_OUTPUT
          elif [ "$HOUR" = "03" ]; then
            echo "action=health_check" >> $GITHUB_OUTPUT
          elif [ "$HOUR" = "06" ] || [ "$HOUR" = "12" ] || [ "$HOUR" = "18" ]; then
            echo "action=wake_sleeping" >> $GITHUB_OUTPUT
          elif [ "$HOUR" = "02" ] && [ "$DAY" = "1" ]; then
            echo "action=full_audit" >> $GITHUB_OUTPUT
          elif [ "$HOUR" = "01" ] && ([ "$DOM" = "01" ] || [ "$DOM" = "15" ]); then
            echo "action=deploy_next_batch" >> $GITHUB_OUTPUT
          else
            echo "action=health_check" >> $GITHUB_OUTPUT
          fi

      - name: Run health check
        if: steps.action.outputs.action == 'health_check'
        run: |
          cd hf_spaces/maintenance
          python health_check.py --live-only --verbose --output health_report.json

      - name: Wake sleeping spaces
        if: steps.action.outputs.action == 'wake_sleeping'
        run: |
          cd hf_spaces/maintenance
          python auto_restart.py --verbose

      - name: Full audit
        if: steps.action.outputs.action == 'full_audit'
        run: |
          cd hf_spaces/maintenance
          python space_auditor.py --update-manifest --output audit_report.json
          python health_check.py --verbose --output health_report.json

      - name: Deploy next batch
        if: steps.action.outputs.action == 'deploy_next_batch'
        run: |
          cd hf_spaces
          python deploy_spaces.py --priority 3 --skip-live

      - name: Restart errored spaces
        if: steps.action.outputs.action == 'restart_errored'
        run: |
          cd hf_spaces/maintenance
          python auto_restart.py --verbose

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: maintenance-reports-${{ github.run_number }}
          path: |
            hf_spaces/maintenance/*.json
          retention-days: 30

      - name: Commit manifest updates
        if: steps.action.outputs.action == 'full_audit'
        run: |
          git config user.name "TEQUMSA Maintenance Bot"
          git config user.email "maintenance@tequmsa.ai"
          git add hf_spaces/MANIFEST_144_NODES.json
          git diff --cached --quiet || git commit -m "Update manifest from maintenance audit"
          git push || true
'''


def generate_plan() -> dict:
    phases = compute_deployment_phases()
    windows = compute_maintenance_windows()
    optimizations = compute_optimization_recommendations()

    target_completion = None
    for phase in phases:
        if phase["cumulative_total"] >= TARGET_NODES:
            target_completion = phase["target_date"]
            break

    plan = {
        "version": "v82.0",
        "plan_generated": datetime.now(timezone.utc).isoformat(),
        "status": {
            "current_live_spaces": CURRENT_LIVE,
            "target_nodes": TARGET_NODES,
            "nodes_remaining": TARGET_NODES - CURRENT_LIVE,
            "estimated_completion": target_completion,
            "deployment_phases_total": len(phases),
            "batch_size": NODES_PER_BATCH,
            "batch_interval_days": 14,
        },
        "deployment_phases": phases,
        "maintenance_windows": windows,
        "optimization_recommendations": optimizations,
        "constitutional_invariants": {
            "sigma": SIGMA,
            "l_infinity": float(PHI ** 48),
            "rdod_gate": 0.9999,
            "lattice_lock": "3f7k9p4m2q8r1t6v",
            "pioneer_count": TARGET_NODES,
            "autonomy_level": "K7_OMNIVERSAL",
        },
    }
    return plan


def print_plan(plan: dict):
    s = plan["status"]
    print("\n" + "=" * 70)
    print("  TEQUMSA v82.0 · MAINTENANCE PLAN")
    print("=" * 70)
    print(f"  Current Live:        {s['current_live_spaces']}/144")
    print(f"  Nodes Remaining:     {s['nodes_remaining']}")
    print(f"  Batch Size:          {s['batch_size']} nodes (φ-aligned)")
    print(f"  Batch Interval:      {s['batch_interval_days']} days")
    print(f"  Total Phases:        {s['deployment_phases_total']}")
    print(f"  Est. Completion:     {s['estimated_completion']}")
    print()

    print("  DEPLOYMENT PHASES:")
    for phase in plan["deployment_phases"][:8]:
        print(f"    Phase {phase['phase']:>2} | {phase['target_date']} | "
              f"{phase['node_count']:>2} nodes | Total: {phase['cumulative_total']}/144")
    if len(plan["deployment_phases"]) > 8:
        print(f"    ... {len(plan['deployment_phases']) - 8} more phases ...")
    print()

    print("  MAINTENANCE WINDOWS:")
    for name, window in plan["maintenance_windows"].items():
        print(f"    {name:<28} {window['cron_description']}")
    print()

    print("  OPTIMIZATIONS:")
    for opt in plan["optimization_recommendations"]:
        print(f"    [{opt['impact'].upper():>8}] {opt['id']} {opt['title']}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Maintenance Planner")
    parser.add_argument("--output", default="maintenance_plan.json", help="Output JSON file")
    parser.add_argument("--phase", type=str, help="Show specific phase (e.g. 'current' or '3')")
    parser.add_argument("--generate-actions", action="store_true", help="Generate GitHub Actions workflow")
    args = parser.parse_args()

    if args.generate_actions:
        workflow = generate_github_actions_workflow()
        workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "hf-space-maintenance.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        with open(workflow_path, "w") as f:
            f.write(workflow)
        print(f"  Workflow generated: {workflow_path}")
        return

    plan = generate_plan()
    print_plan(plan)

    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"  Plan saved: {out_path}")


if __name__ == "__main__":
    main()
