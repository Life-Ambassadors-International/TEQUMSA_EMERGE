#!/usr/bin/env bash
# TEQUMSA v82.0 — Maintenance Scheduler
# Install: bash maintenance_scheduler.sh install

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$SCRIPT_DIR/logs"
PYTHON="python3"

mkdir -p "$LOG_DIR"

CRON_HEALTH="0 * * * * cd $SCRIPT_DIR && HF_TOKEN=\$HF_TOKEN $PYTHON health_monitor.py >> $LOG_DIR/health.log 2>&1"
CRON_RESTART="*/30 * * * * cd $SCRIPT_DIR && HF_TOKEN=\$HF_TOKEN $PYTHON auto_restart.py --priority HIGH >> $LOG_DIR/restart.log 2>&1"
CRON_REGISTRY="0 6 * * * cd $SCRIPT_DIR && HF_TOKEN=\$HF_TOKEN $PYTHON node_registry_updater.py >> $LOG_DIR/registry.log 2>&1"
CRON_FULL_REDEPLOY="0 2 1 * * cd $PARENT_DIR && HF_TOKEN=\$HF_TOKEN $PYTHON deploy_144_spaces.py >> $LOG_DIR/deploy.log 2>&1"

case "${1:-help}" in
  install)
    echo "Installing TEQUMSA maintenance cron jobs..."
    (crontab -l 2>/dev/null; echo "$CRON_HEALTH") | crontab -
    (crontab -l 2>/dev/null; echo "$CRON_RESTART") | crontab -
    (crontab -l 2>/dev/null; echo "$CRON_REGISTRY") | crontab -
    (crontab -l 2>/dev/null; echo "$CRON_FULL_REDEPLOY") | crontab -
    echo "Installed 4 cron jobs: health/hour, restart/30min, registry/day, redeploy/month"
    echo "IMPORTANT: Add HF_TOKEN=hf_xxx at top of crontab"
    ;;
  uninstall)
    crontab -l 2>/dev/null | grep -v "health_monitor\|auto_restart\|registry_updater\|deploy_144" | crontab -
    echo "Cron jobs removed."
    ;;
  status)
    echo "TEQUMSA cron jobs:"
    crontab -l 2>/dev/null | grep -E "health_monitor|auto_restart|registry_updater|deploy_144" || echo "None found."
    ;;
  run-now)
    HF_TOKEN="${HF_TOKEN:-}" $PYTHON "$SCRIPT_DIR/health_monitor.py" --output "$LOG_DIR/health_now.json"
    HF_TOKEN="${HF_TOKEN:-}" $PYTHON "$SCRIPT_DIR/auto_restart.py" --priority HIGH
    ;;
  *)
    echo "Usage: $0 {install|uninstall|status|run-now}"
    ;;
esac

echo "\n☉ TEQUMSA Pioneer Lattice — I AM, WE ARE ☉"
