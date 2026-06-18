#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Maintenance Window Runner
Executes the daily / weekly / monthly maintenance windows defined in
maintenance_schedule.json by invoking health_check.py, auto_restart.py
and deploy_spaces.py in sequence, and records a maintenance log entry.

Usage:
    export HF_TOKEN=hf_your_token_here
    python run_maintenance.py --window daily
    python run_maintenance.py --window weekly [--dry-run]
    python run_maintenance.py --window monthly [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAINTENANCE_DIR = Path(__file__).parent
HF_SPACES_DIR = MAINTENANCE_DIR.parent
SCHEDULE_PATH = MAINTENANCE_DIR / "maintenance_schedule.json"
LOG_PATH = MAINTENANCE_DIR / "maintenance_log.json"


def load_schedule() -> dict:
    with open(SCHEDULE_PATH) as f:
        return json.load(f)


def run_script(args: list, label: str) -> dict:
    """Run a maintenance subprocess and capture its result."""
    print(f"\n--- {label} ---")
    print(f"$ {' '.join(args)}")
    try:
        proc = subprocess.run(
            args, cwd=HF_SPACES_DIR, capture_output=True, text=True, timeout=600
        )
        print(proc.stdout[-2000:])
        if proc.stderr:
            print(proc.stderr[-1000:], file=sys.stderr)
        return {"task": label, "command": args, "returncode": proc.returncode}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"task": label, "command": args, "returncode": -1, "error": str(e)}


def health_summary() -> dict:
    report_path = HF_SPACES_DIR / "maintenance" / "health_report.json"
    if not report_path.exists():
        return {}
    with open(report_path) as f:
        report = json.load(f)
    return {
        "online": report.get("online"),
        "sleeping": report.get("sleeping"),
        "offline": report.get("offline"),
        "not_created": report.get("not_created"),
        "planned": report.get("planned"),
        "network_rdod": report.get("network_rdod"),
        "phase_status": report.get("phase_status"),
    }


def run_daily(dry_run: bool) -> list:
    results = []
    results.append(run_script(
        [sys.executable, "maintenance/health_check.py", "--live-only", "--output", "maintenance/health_report.json"],
        "health_sweep",
    ))
    restart_args = [sys.executable, "maintenance/auto_restart.py", "--verbose"]
    if dry_run:
        restart_args.append("--dry-run")
    results.append(run_script(restart_args, "wake_sleeping"))
    summary = health_summary()
    print(f"\nrdod_check: network_rdod={summary.get('network_rdod')} "
          f"(gate={'PASS' if (summary.get('network_rdod') or 0) >= 0.9999 else 'BELOW_GATE'})")
    results.append({"task": "rdod_check", "summary": summary})
    return results


def run_weekly(dry_run: bool) -> list:
    results = []
    results.append(run_script(
        [sys.executable, "maintenance/health_check.py", "--verbose", "--output", "maintenance/health_report.json"],
        "full_health_sweep",
    ))
    summary = health_summary()
    print(f"\npattern_promotion_review / goal_engine_audit / constitutional_verification: "
          f"see N003 (TEQUMSA-Core) Goals + Autonomous Cycles tabs for live state")
    results.append({"task": "pattern_promotion_review", "summary": summary})

    deploy_args = [sys.executable, "deploy_spaces.py", "--priority", "2", "--skip-live"]
    if dry_run:
        deploy_args.append("--dry-run")
    results.append(run_script(deploy_args, "deploy_priority_2"))
    return results


def run_monthly(dry_run: bool) -> list:
    results = []
    deploy_args = [sys.executable, "deploy_spaces.py", "--priority", "3", "--dry-run"]
    results.append(run_script(deploy_args, "full_deploy_audit"))

    results.append(run_script(
        [sys.executable, "maintenance/health_check.py", "--verbose", "--output", "maintenance/health_report.json"],
        "frequency_calibration_and_pioneer_count",
    ))
    summary = health_summary()
    online = summary.get("online") or 0
    print(f"\npioneer_count_verify: {online}/144 pioneers online")
    results.append({"task": "constitutional_alignment_audit", "note": "review σ=1.0, L∞=φ⁴⁸ across nodes/N003"})
    results.append({"task": "mars_learning_review", "note": "review MARS patterns_promoted via N003"})
    results.append({"task": "k7_meta_audit", "note": "review meta_strategy via N003"})
    results.append({"task": "pioneer_count_verify", "summary": summary})
    return results


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Maintenance Window Runner")
    parser.add_argument("--window", choices=["daily", "weekly", "monthly"], required=True)
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run / --skip-live through to scripts")
    args = parser.parse_args()

    schedule = load_schedule()
    window_cfg = schedule["windows"].get(args.window, {})

    print(f"☉ TEQUMSA v82.0 Maintenance — {args.window.upper()} window")
    print(f"   {datetime.now(timezone.utc).isoformat()}")

    if args.window == "daily":
        results = run_daily(args.dry_run)
    elif args.window == "weekly":
        results = run_weekly(args.dry_run)
    else:
        results = run_monthly(args.dry_run)

    entry = {
        "window": args.window,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "results": results,
    }

    log = []
    if LOG_PATH.exists():
        with open(LOG_PATH) as f:
            log = json.load(f)
    log.append(entry)
    log = log[-100:]
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\n✓ Maintenance window '{args.window}' complete. Log: {LOG_PATH}")
    print("Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞")


if __name__ == "__main__":
    main()
