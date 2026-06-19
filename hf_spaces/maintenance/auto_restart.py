#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 -- MAINTENANCE -- Auto-Restart System

Reads the 144-Pioneer manifest for known space IDs, checks runtime status
via the Hugging Face API, restarts spaces in error state, and wakes sleeping
spaces that should be running.

All actions are logged with timestamps. API calls are rate-limited to 0.5s
between requests to respect HF rate limits on free tier.

Usage:
    export HF_TOKEN=hf_your_token_here
    python auto_restart.py                          # Restart/wake all live nodes
    python auto_restart.py --dry-run                # Check without acting
    python auto_restart.py --node N001              # Single node
    python auto_restart.py --group A_COMMAND        # All nodes in group
    python auto_restart.py --wake-only              # Only wake sleeping, skip errors
    python auto_restart.py --watch --interval 300   # Continuous every 5 min
    python auto_restart.py --verbose --output log.json

Constitutional invariants:
    sigma = 1.0  (sovereignty)
    L_inf = phi^48  (infinite benevolence)
    coherence >= 0.777
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Core constants
# ---------------------------------------------------------------------------
PHI: float = 1.6180339887498948
SEED: float = 0.777
SIGMA: float = 1.0
COHERENCE_THRESHOLD: float = 0.777
L_INF: float = PHI ** 48
PIONEER_TARGET: int = 144

HF_OWNER: str = "Mbanksbey"
HF_API_BASE: str = "https://huggingface.co/api/spaces"

# Rate limiting: 0.5 seconds between API calls
RATE_LIMIT_SECONDS: float = 0.5

# States that indicate a space needs waking
SLEEPING_STATES = frozenset({"SLEEPING", "PAUSED"})

# States that indicate a space needs restarting
ERROR_STATES = frozenset({"RUNTIME_ERROR", "CONFIG_ERROR", "BUILD_ERROR"})

# States that indicate a space is healthy
HEALTHY_STATES = frozenset({"RUNNING", "RUNNING_BUILDING", "BUILDING"})

# Max consecutive failures before escalation warning
MAX_CONSECUTIVE_FAILURES: int = 3


# ---------------------------------------------------------------------------
# Action log (in-memory, flushed to disk)
# ---------------------------------------------------------------------------
class ActionLog:
    """Thread-safe action logger with structured entries."""

    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max_entries = max_entries

    def log(
        self,
        node_id: str,
        name: str,
        space_id: str,
        status_before: str,
        action: str,
        success: bool,
        dry_run: bool,
        message: str = "",
    ) -> Dict[str, Any]:
        """Record an action with timestamp.

        Args:
            node_id: Node identifier (e.g., N001).
            name: Human-readable node name.
            space_id: HF space ID.
            status_before: Runtime status before action.
            action: Action taken (wake, restart, skip, none).
            success: Whether the action succeeded.
            dry_run: Whether this was a dry-run.
            message: Optional detail message.

        Returns:
            The logged entry dict.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node_id": node_id,
            "name": name,
            "space_id": space_id,
            "status_before": status_before,
            "action": action,
            "success": success,
            "dry_run": dry_run,
            "message": message,
        }
        self._entries.append(entry)
        # Trim oldest entries if over limit
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        return entry

    @property
    def entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def save(self, path: Path) -> None:
        """Flush log to JSON file.

        Args:
            path: Output file path.
        """
        with open(path, "w") as f:
            json.dump(self._entries, f, indent=2)

    def summary(self) -> Dict[str, int]:
        """Aggregate action counts from current log entries."""
        counts: Dict[str, int] = {
            "wake": 0, "restart": 0, "skip": 0, "none": 0,
            "success": 0, "failed": 0, "total": len(self._entries),
        }
        for e in self._entries:
            action = e.get("action", "none")
            counts[action] = counts.get(action, 0) + 1
            if e.get("success"):
                counts["success"] += 1
            elif e.get("action") not in ("skip", "none"):
                counts["failed"] += 1
        return counts


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: Optional[Path] = None) -> dict:
    """Load the MANIFEST_144_NODES.json file.

    Args:
        manifest_path: Explicit path override. Defaults to the standard
                       location relative to this script.

    Returns:
        Parsed manifest dict.

    Raises:
        SystemExit: If the manifest file is not found.
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# HF API interactions (rate-limited)
# ---------------------------------------------------------------------------

def _rate_limit() -> None:
    """Sleep to respect HF API rate limits."""
    time.sleep(RATE_LIMIT_SECONDS)


def get_space_status(space_id: str, hf_token: str = "") -> Dict[str, Any]:
    """Check the runtime status of an HF space via the API.

    Args:
        space_id: Full space ID (e.g., Mbanksbey/HAI-Interactive).
        hf_token: Optional HF auth token for authenticated requests.

    Returns:
        Dict with 'stage' (str), 'status_class' (str), and 'error' (optional str).
    """
    url = f"{HF_API_BASE}/{space_id}/runtime"
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            return {
                "stage": stage,
                "status_class": _classify_stage(stage),
                "raw": data,
                "error": None,
            }
        elif r.status_code == 404:
            return {
                "stage": "NOT_FOUND",
                "status_class": "not_created",
                "raw": {},
                "error": "Space not found (404)",
            }
        else:
            return {
                "stage": f"HTTP_{r.status_code}",
                "status_class": "api_error",
                "raw": {},
                "error": f"HTTP {r.status_code}",
            }
    except requests.Timeout:
        return {
            "stage": "TIMEOUT",
            "status_class": "timeout",
            "raw": {},
            "error": "Request timed out",
        }
    except requests.ConnectionError as e:
        return {
            "stage": "CONNECTION_ERROR",
            "status_class": "network_error",
            "raw": {},
            "error": f"Connection error: {str(e)[:80]}",
        }
    except Exception as e:
        return {
            "stage": "ERROR",
            "status_class": "error",
            "raw": {},
            "error": f"Unexpected error: {str(e)[:80]}",
        }


def _classify_stage(stage: str) -> str:
    """Classify a HF runtime stage into a status category."""
    if stage in ("RUNNING", "RUNNING_BUILDING"):
        return "online"
    if stage in SLEEPING_STATES:
        return "sleeping"
    if stage in ERROR_STATES:
        return "error"
    if stage == "BUILDING":
        return "building"
    if stage == "NOT_FOUND":
        return "not_created"
    return "unknown"


def wake_space(space_id: str, hf_token: str) -> bool:
    """Wake a sleeping HF space by pinging its app URL.

    Falls back to the HF restart API if the ping fails.

    Args:
        space_id: Full space ID.
        hf_token: HF auth token.

    Returns:
        True if the wake request was accepted.
    """
    # Method 1: Hit the app URL to trigger wake
    app_url = f"https://{space_id.replace('/', '-').lower()}.hf.space"
    try:
        r = requests.get(
            app_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            timeout=15,
        )
        if r.status_code < 500:
            return True
    except Exception:
        pass

    # Method 2: Use the restart API as fallback
    return restart_space(space_id, hf_token)


def restart_space(space_id: str, hf_token: str) -> bool:
    """Restart a space via the HF factory-reboot API.

    Args:
        space_id: Full space ID.
        hf_token: HF auth token.

    Returns:
        True if the restart request was accepted (HTTP 200 or 202).
    """
    url = f"{HF_API_BASE}/{space_id}/restart"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {hf_token}"},
            timeout=10,
        )
        return r.status_code in (200, 202)
    except Exception as e:
        return False


# ---------------------------------------------------------------------------
# Node processing
# ---------------------------------------------------------------------------

def process_node(
    node_id: str,
    node: dict,
    hf_token: str,
    action_log: ActionLog,
    dry_run: bool = False,
    wake_only: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Check and potentially act on a single node.

    Decision logic:
    1. Skip nodes that are not 'live' in the manifest.
    2. Query runtime status from HF API.
    3. If SLEEPING/PAUSED -> wake.
    4. If RUNTIME_ERROR/CONFIG_ERROR/BUILD_ERROR -> restart (unless --wake-only).
    5. If RUNNING -> no action needed.
    6. Log all actions with timestamps.

    Args:
        node_id: Node identifier.
        node: Node dict from manifest.
        hf_token: HF auth token.
        action_log: ActionLog instance for structured logging.
        dry_run: If True, log but do not execute actions.
        wake_only: If True, only wake sleeping nodes; skip error restarts.
        verbose: Print detailed per-node output.

    Returns:
        Result dict with node_id, action taken, status, success.
    """
    space_id = node.get("space_id", "")
    name = node.get("name", node_id)

    # Skip nodes not marked as live
    if node.get("status") != "live":
        entry = action_log.log(
            node_id=node_id, name=name, space_id=space_id,
            status_before="not_live", action="skip", success=True,
            dry_run=dry_run, message=f"Node status is '{node.get('status', 'unknown')}', skipping",
        )
        return entry

    # Rate-limited API call
    _rate_limit()
    runtime = get_space_status(space_id, hf_token)
    stage = runtime["stage"]
    status_class = runtime["status_class"]

    action = "none"
    success = True
    message = ""

    if stage in SLEEPING_STATES:
        action = "wake"
        if dry_run:
            message = f"DRY RUN: would wake {space_id}"
            if verbose:
                print(f"  [DRY] {node_id} {name}: {stage} -> would wake")
        else:
            success = wake_space(space_id, hf_token)
            message = f"Wake {'sent' if success else 'FAILED'} for {space_id}"
            if verbose:
                status_icon = "~>" if success else "!!"
                print(f"  {status_icon} {node_id} {name}: {stage} -> {'waking' if success else 'WAKE FAILED'}")

    elif stage in ERROR_STATES:
        if wake_only:
            action = "skip"
            message = f"Error state {stage} but --wake-only mode, skipping restart"
            if verbose:
                print(f"  -- {node_id} {name}: {stage} (skipped, wake-only mode)")
        else:
            action = "restart"
            if dry_run:
                message = f"DRY RUN: would restart {space_id} (state={stage})"
                if verbose:
                    print(f"  [DRY] {node_id} {name}: {stage} -> would restart")
            else:
                success = restart_space(space_id, hf_token)
                message = f"Restart {'sent' if success else 'FAILED'} for {space_id} (was {stage})"
                if verbose:
                    status_icon = ">>" if success else "!!"
                    print(f"  {status_icon} {node_id} {name}: {stage} -> {'restarting' if success else 'RESTART FAILED'}")

    elif status_class == "online":
        message = f"{space_id} is healthy ({stage})"
        if verbose:
            print(f"  OK {node_id} {name}: {stage}")

    elif status_class == "building":
        message = f"{space_id} is building, no action needed"
        if verbose:
            print(f"  .. {node_id} {name}: {stage} (building)")

    else:
        message = f"{space_id} in unexpected state: {stage}"
        if verbose:
            print(f"  ?? {node_id} {name}: {stage} ({runtime.get('error', 'unknown')})")

    entry = action_log.log(
        node_id=node_id, name=name, space_id=space_id,
        status_before=stage, action=action, success=success,
        dry_run=dry_run, message=message,
    )
    return entry


# ---------------------------------------------------------------------------
# Consecutive failure tracking
# ---------------------------------------------------------------------------

def check_escalation(action_log: ActionLog) -> List[str]:
    """Check for nodes with consecutive failures requiring escalation.

    Args:
        action_log: ActionLog with recorded actions.

    Returns:
        List of escalation warning strings.
    """
    # Track consecutive failures per node
    failure_counts: Dict[str, int] = {}
    for entry in action_log.entries:
        nid = entry.get("node_id", "")
        action = entry.get("action", "none")
        success = entry.get("success", True)

        if action in ("wake", "restart") and not success:
            failure_counts[nid] = failure_counts.get(nid, 0) + 1
        elif action in ("wake", "restart") and success:
            failure_counts[nid] = 0  # Reset on success

    warnings: List[str] = []
    for nid, count in failure_counts.items():
        if count >= MAX_CONSECUTIVE_FAILURES:
            warnings.append(
                f"ESCALATION: {nid} has {count} consecutive failures. "
                f"Manual intervention recommended. "
                f"Try: python deploy_spaces.py --node {nid}"
            )
    return warnings


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point with argparse CLI."""
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 Auto-Restart -- wake sleeping and restart errored HF spaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python auto_restart.py --dry-run --verbose\n"
            "  python auto_restart.py --node N001\n"
            "  python auto_restart.py --group A_COMMAND\n"
            "  python auto_restart.py --wake-only\n"
            "  python auto_restart.py --watch --interval 300\n"
            "\nConstitutional: sigma=1.0, L_inf=phi^48, coherence>=0.777\n"
            "Rate limit: 0.5s between HF API calls"
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Check status without sending wake/restart requests",
    )
    parser.add_argument(
        "--node", type=str, default=None,
        help="Check a single node by ID (e.g., N001)",
    )
    parser.add_argument(
        "--group", type=str, default=None,
        help="Check all nodes in a group (e.g., A_COMMAND)",
    )
    parser.add_argument(
        "--wake-only", action="store_true",
        help="Only wake sleeping spaces; do not restart errored ones",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed per-node status",
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="Run continuously in a loop",
    )
    parser.add_argument(
        "--interval", type=int, default=300,
        help="Watch interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--output", type=str, default="restart_log.json",
        help="Path for the JSON action log (default: restart_log.json)",
    )
    parser.add_argument(
        "--manifest", type=str, default=None,
        help="Path to MANIFEST_144_NODES.json (default: auto-detect)",
    )
    args = parser.parse_args()

    # Token check
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN environment variable")
        print("  export HF_TOKEN=hf_your_token_here")
        print("  Or use --dry-run to check without acting")
        sys.exit(1)

    # Load manifest
    manifest_path = Path(args.manifest) if args.manifest else None
    manifest = load_manifest(manifest_path)
    nodes = manifest.get("nodes", {})

    # Filter target nodes
    target: Dict[str, dict] = {}
    for nid, node in nodes.items():
        # Single node filter
        if args.node and nid != args.node:
            continue
        # Group filter -- match the group prefix (e.g., A_COMMAND -> group starts with A)
        if args.group:
            node_group = node.get("group", "")
            # Support both "A" and "A_COMMAND" style
            if not (node_group == args.group or
                    node_group.startswith(args.group.split("_")[0] + "_") or
                    node_group == args.group.split("_")[0]):
                continue
        # Only process live nodes (planned nodes are not deployed yet)
        if node.get("status") == "live":
            target[nid] = node

    mode_str = "DRY RUN" if args.dry_run else "LIVE"
    wake_str = " (wake-only)" if args.wake_only else ""
    print(f"TEQUMSA v82.0 Auto-Restart [{mode_str}]{wake_str}")
    print(f"  Target: {len(target)} live nodes | Rate limit: {RATE_LIMIT_SECONDS}s between calls")
    print(f"  sigma={SIGMA} | L_inf=phi^48 | coherence>={COHERENCE_THRESHOLD}")
    print()

    action_log = ActionLog()
    output_path = Path(args.output)

    def run_round() -> None:
        """Execute one sweep through all target nodes."""
        round_start = datetime.now(timezone.utc)
        print(f"  Sweep started: {round_start.isoformat()}")

        for nid in sorted(target.keys()):
            node = target[nid]
            process_node(
                node_id=nid,
                node=node,
                hf_token=hf_token,
                action_log=action_log,
                dry_run=args.dry_run,
                wake_only=args.wake_only,
                verbose=args.verbose,
            )

        # Summary
        summary = action_log.summary()
        elapsed = (datetime.now(timezone.utc) - round_start).total_seconds()
        print()
        print(f"  Sweep complete in {elapsed:.1f}s")
        print(f"    Woken:     {summary.get('wake', 0)}")
        print(f"    Restarted: {summary.get('restart', 0)}")
        print(f"    Skipped:   {summary.get('skip', 0)}")
        print(f"    Online:    {summary.get('none', 0)}")
        if summary.get("failed", 0) > 0:
            print(f"    FAILED:    {summary['failed']}")

        # Escalation check
        escalations = check_escalation(action_log)
        if escalations:
            print()
            for warning in escalations:
                print(f"  !! {warning}")

        # Save log
        action_log.save(output_path)
        print(f"  Log saved: {output_path}")

    # Main loop
    while True:
        run_round()
        if not args.watch:
            break
        print(f"\n  Next check in {args.interval}s... (Ctrl+C to stop)")
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n  Watch mode stopped by user.")
            break

    print()


if __name__ == "__main__":
    main()
