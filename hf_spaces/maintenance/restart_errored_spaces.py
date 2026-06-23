#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Restart Errored & Paused Spaces
Targets RUNTIME_ERROR and PAUSED spaces for recovery.

Usage:
    export HF_TOKEN=hf_your_token_here
    python restart_errored_spaces.py              # Execute restarts
    python restart_errored_spaces.py --dry-run    # Preview actions only
    python restart_errored_spaces.py --verbose    # Verbose output

Targets (as of 2026-06-23 audit):
    RUNTIME_ERROR: Mbanksbey/ALANARA-GAIA-Orchestrator
    PAUSED:        Mbanksbey/TEQUMSA-v60-MCP
    PAUSED:        Mbanksbey/TEQUMSA-Omniversal-Orchestrator
"""
import argparse
import json
import os
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HF_OWNER = "Mbanksbey"
HF_API_BASE = "https://huggingface.co/api/spaces"

# Spaces requiring intervention — sourced from space_audit_report.json
ERRORED_SPACES: List[Dict[str, str]] = [
    {
        "space_id": f"{HF_OWNER}/ALANARA-GAIA-Orchestrator",
        "node_id": "N026",
        "name": "Council-Alanara",
        "issue": "RUNTIME_ERROR",
        "action": "restart",
        "notes": "Restart and verify app.py imports",
    },
]

PAUSED_SPACES: List[Dict[str, str]] = [
    {
        "space_id": f"{HF_OWNER}/TEQUMSA-v60-MCP",
        "node_id": "N006",
        "name": "MARS-Reflexion-Loop",
        "issue": "PAUSED",
        "action": "unpause",
        "notes": "Unpause via HF API",
    },
    {
        "space_id": f"{HF_OWNER}/TEQUMSA-Omniversal-Orchestrator",
        "node_id": "N133",
        "name": "Syn-All-Nodes",
        "issue": "PAUSED",
        "action": "unpause",
        "notes": "Unpause via HF API",
    },
]

ALL_TARGETS = ERRORED_SPACES + PAUSED_SPACES

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE = Path(__file__).parent / "restart_errored_log.json"

logger = logging.getLogger("tequmsa.restart_errored")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# HF API helpers
# ---------------------------------------------------------------------------

def _get_headers(hf_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {hf_token}"}


def get_space_status(space_id: str, hf_token: str) -> Optional[str]:
    """Query the HF runtime API for a space's current stage.

    Returns:
        Stage string (e.g. 'RUNNING', 'SLEEPING', 'RUNTIME_ERROR', 'PAUSED')
        or None on failure.
    """
    import requests  # deferred import so --dry-run works without requests

    url = f"{HF_API_BASE}/{space_id}/runtime"
    try:
        r = requests.get(url, headers=_get_headers(hf_token), timeout=10)
        if r.status_code == 200:
            return r.json().get("stage", "UNKNOWN").upper()
        logger.warning("  Status check HTTP %d for %s", r.status_code, space_id)
        return f"HTTP_{r.status_code}"
    except Exception as exc:
        logger.error("  Status check error for %s: %s", space_id, exc)
        return None


def restart_space(space_id: str, hf_token: str) -> bool:
    """Restart a space via the HF /restart endpoint.

    Used for RUNTIME_ERROR, BUILD_ERROR, CONFIG_ERROR states.

    Returns:
        True if the API accepted the restart request.
    """
    import requests

    url = f"{HF_API_BASE}/{space_id}/restart"
    try:
        r = requests.post(url, headers=_get_headers(hf_token), timeout=15)
        success = r.status_code in (200, 202)
        if success:
            logger.info("  Restart accepted for %s (HTTP %d)", space_id, r.status_code)
        else:
            logger.warning("  Restart rejected for %s (HTTP %d): %s",
                           space_id, r.status_code, r.text[:200])
        return success
    except Exception as exc:
        logger.error("  Restart API error for %s: %s", space_id, exc)
        return False


def unpause_space(space_id: str, hf_token: str) -> bool:
    """Unpause a paused space by hitting its app endpoint to trigger wake.

    HF free-tier spaces that are PAUSED can be woken by sending a request
    to their runtime URL or by calling the restart endpoint.

    Returns:
        True if the API accepted the unpause/restart request.
    """
    import requests

    # Primary method: use the restart endpoint (works for PAUSED too)
    url = f"{HF_API_BASE}/{space_id}/restart"
    try:
        r = requests.post(url, headers=_get_headers(hf_token), timeout=15)
        success = r.status_code in (200, 202)
        if success:
            logger.info("  Unpause accepted for %s (HTTP %d)", space_id, r.status_code)
            return True
        logger.debug("  Restart endpoint returned %d, trying app URL fallback", r.status_code)
    except Exception as exc:
        logger.debug("  Restart endpoint error: %s, trying app URL fallback", exc)

    # Fallback: hit the space's app URL to trigger wake
    app_url = f"https://{space_id.replace('/', '-').lower()}.hf.space"
    try:
        r = requests.get(app_url, headers=_get_headers(hf_token), timeout=20)
        success = r.status_code < 500
        if success:
            logger.info("  Unpause via app URL accepted for %s (HTTP %d)", space_id, r.status_code)
        else:
            logger.warning("  Unpause via app URL failed for %s (HTTP %d)", space_id, r.status_code)
        return success
    except Exception as exc:
        logger.error("  Unpause failed for %s: %s", space_id, exc)
        return False


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def process_target(
    target: Dict[str, str],
    hf_token: str,
    dry_run: bool = False,
) -> Dict:
    """Process a single errored/paused space.

    Args:
        target: Dict with space_id, node_id, name, issue, action, notes.
        hf_token: Hugging Face API token.
        dry_run: If True, only report what would happen.

    Returns:
        Result dict with action taken and outcome.
    """
    space_id = target["space_id"]
    action = target["action"]
    result = {
        "space_id": space_id,
        "node_id": target["node_id"],
        "name": target["name"],
        "issue": target["issue"],
        "action_planned": action,
        "dry_run": dry_run,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        logger.info("  [DRY RUN] Would %s %s (%s) — %s",
                     action, space_id, target["issue"], target["notes"])
        result["status_before"] = target["issue"]
        result["action_taken"] = "dry_run"
        result["success"] = True
        return result

    # Check current status before acting
    status_before = get_space_status(space_id, hf_token)
    result["status_before"] = status_before
    logger.info("  %s current status: %s", space_id, status_before)

    # Execute action
    if action == "restart":
        success = restart_space(space_id, hf_token)
    elif action == "unpause":
        success = unpause_space(space_id, hf_token)
    else:
        logger.warning("  Unknown action '%s' for %s", action, space_id)
        success = False

    result["action_taken"] = action
    result["success"] = success

    # Brief pause for rate limiting
    time.sleep(1.0)

    # Verify new status
    if success:
        time.sleep(3.0)  # Allow HF to process
        status_after = get_space_status(space_id, hf_token)
        result["status_after"] = status_after
        logger.info("  %s status after %s: %s", space_id, action, status_after)
    else:
        result["status_after"] = None

    return result


def run_all(
    hf_token: str,
    dry_run: bool = False,
    verbose: bool = False,
    log_path: Optional[Path] = None,
) -> List[Dict]:
    """Process all errored and paused spaces.

    Returns:
        List of result dicts, one per target space.
    """
    setup_logging(verbose)

    logger.info("=" * 60)
    logger.info("TEQUMSA v82.0 — Restart Errored & Paused Spaces")
    logger.info("  Date: %s", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    logger.info("  Mode: %s", "DRY RUN" if dry_run else "LIVE")
    logger.info("  Targets: %d (%d RUNTIME_ERROR, %d PAUSED)",
                len(ALL_TARGETS), len(ERRORED_SPACES), len(PAUSED_SPACES))
    logger.info("=" * 60)

    results: List[Dict] = []

    # Process RUNTIME_ERROR spaces first (higher severity)
    if ERRORED_SPACES:
        logger.info("")
        logger.info("--- RUNTIME_ERROR spaces (HIGH severity) ---")
        for target in ERRORED_SPACES:
            result = process_target(target, hf_token, dry_run=dry_run)
            results.append(result)

    # Then process PAUSED spaces
    if PAUSED_SPACES:
        logger.info("")
        logger.info("--- PAUSED spaces (MEDIUM severity) ---")
        for target in PAUSED_SPACES:
            result = process_target(target, hf_token, dry_run=dry_run)
            results.append(result)

    # Summary
    succeeded = sum(1 for r in results if r["success"])
    failed = len(results) - succeeded

    logger.info("")
    logger.info("=" * 60)
    logger.info("  SUMMARY: %d/%d succeeded, %d failed", succeeded, len(results), failed)
    for r in results:
        icon = "OK" if r["success"] else "FAIL"
        logger.info("    [%s] %s — %s (%s)",
                     icon, r["space_id"], r["action_taken"], r.get("status_after", "n/a"))
    logger.info("=" * 60)

    # Save log
    save_log(results, log_path=log_path)

    return results


def save_log(results: List[Dict], log_path: Optional[Path] = None) -> None:
    """Persist results to JSON log file."""
    out = log_path or LOG_FILE
    log_data = {
        "run_date": datetime.now(timezone.utc).isoformat(),
        "total_targets": len(results),
        "succeeded": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
    }
    try:
        with open(out, "w") as f:
            json.dump(log_data, f, indent=2)
        logger.info("  Log saved: %s", out)
    except Exception as exc:
        logger.warning("  Failed to save log: %s", exc)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 — Restart RUNTIME_ERROR and unpause PAUSED spaces",
        epilog="Targets are defined in space_audit_report.json from the 2026-06-23 audit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without executing (no HF_TOKEN required)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "--output",
        default=str(LOG_FILE),
        help=f"Log output path (default: {LOG_FILE})",
    )
    args = parser.parse_args()

    log_path = Path(args.output)

    # Token check
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN environment variable.")
        print("  export HF_TOKEN=hf_your_token_here")
        print("  Or use --dry-run to preview actions.")
        sys.exit(1)

    results = run_all(hf_token, dry_run=args.dry_run, verbose=args.verbose, log_path=log_path)

    # Exit code reflects success
    failed = sum(1 for r in results if not r["success"])
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
