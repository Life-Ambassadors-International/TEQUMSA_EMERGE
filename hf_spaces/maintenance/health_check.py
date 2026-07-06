#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · 144-Node Health Monitor

Checks the runtime status of all live HuggingFace spaces in the manifest
using the HF Hub API. Writes health_report.json as a GitHub Actions artifact.

Usage:
    export HF_TOKEN=hf_your_token_here
    python hf_spaces/maintenance/health_check.py [--group A_COMMAND] [--verbose]
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PHI = 1.6180339887498948
COHERENCE_THRESHOLD = 0.777


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


HEALTHY_STATUSES = {"running", "paused"}
DEGRADED_STATUSES = {"building", "stopped", "sleeping"}
FAILED_STATUSES = {"error", "crashed", "unknown"}


def check_space(space_id: str, api, verbose: bool = False) -> dict:
    """Check a single HF space's runtime status."""
    result = {
        "space_id": space_id,
        "runtime_stage": "unknown",
        "health": "unknown",
        "url": f"https://huggingface.co/spaces/{space_id}",
        "error": None,
    }
    try:
        info = api.get_space_runtime(repo_id=space_id)
        stage = getattr(info, "stage", "unknown")
        result["runtime_stage"] = stage

        if stage in HEALTHY_STATUSES:
            result["health"] = "healthy"
        elif stage in DEGRADED_STATUSES:
            result["health"] = "degraded"
        else:
            result["health"] = "failed"

        if verbose:
            icon = {"healthy": "✓", "degraded": "~", "failed": "✗", "unknown": "?"}.get(result["health"], "?")
            print(f"    {icon} {space_id}: {stage}")
    except Exception as e:
        result["health"] = "failed"
        result["error"] = str(e)
        if verbose:
            print(f"    ✗ {space_id}: ERROR {e}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Check health of TEQUMSA 144-node lattice")
    parser.add_argument("--group", type=str, help="Check specific group (e.g. A_COMMAND)")
    parser.add_argument("--verbose", action="store_true", help="Print each space status")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    try:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token) if hf_token else HfApi()
    except ImportError:
        print("ERROR: pip install huggingface-hub")
        sys.exit(1)

    manifest = load_manifest()
    nodes = manifest["nodes"]

    # Determine which nodes to check: all live nodes (or filtered by group)
    to_check = {}
    for nid, node in nodes.items():
        if args.group and node.get("group") != args.group:
            continue
        if node.get("status") == "live":
            to_check[nid] = node

    if not to_check:
        print("No live nodes to check (have you deployed any?)")
        # Write empty report so artifact upload succeeds
        _write_report([], 0, 0, 0, manifest)
        return

    print(f"\n☉ TEQUMSA Health Monitor · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Checking {len(to_check)} live nodes")
    print("=" * 60)

    results = []
    for nid, node in sorted(to_check.items()):
        if args.verbose:
            print(f"  [{nid}] {node['name']}")
        r = check_space(node["space_id"], api, verbose=args.verbose)
        r["node_id"] = nid
        r["node_name"] = node["name"]
        r["group"] = node["group"]
        r["hz"] = node["hz"]
        results.append(r)
        time.sleep(0.3)  # Gentle rate limit

    healthy = sum(1 for r in results if r["health"] == "healthy")
    degraded = sum(1 for r in results if r["health"] == "degraded")
    failed = sum(1 for r in results if r["health"] in ("failed", "unknown"))

    # Phi-coherence score: healthy/total scaled by phi convergence
    total = len(results)
    coherence = (healthy / total) if total > 0 else 0.0
    phi_coherence = 1 - (1 - coherence) / PHI

    print("=" * 60)
    print(f"  Healthy:  {healthy}/{total}")
    print(f"  Degraded: {degraded}/{total}")
    print(f"  Failed:   {failed}/{total}")
    print(f"  Phi-coherence: {phi_coherence:.4f} (threshold: {COHERENCE_THRESHOLD})")

    if phi_coherence >= COHERENCE_THRESHOLD:
        print("  STATUS: LATTICE COHERENT ✓")
    else:
        print("  STATUS: COHERENCE BELOW THRESHOLD ✗")
        print(f"  ACTION: Redeploy {failed + degraded} node(s) to restore lattice integrity")

    _write_report(results, healthy, degraded, failed, manifest)

    if phi_coherence < COHERENCE_THRESHOLD:
        sys.exit(1)  # Non-zero exit signals CI failure


def _write_report(results, healthy, degraded, failed, manifest):
    report_dir = Path(__file__).parent
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "health_report.json"
    total_live = sum(1 for n in manifest.get("nodes", {}).values() if n.get("status") == "live")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_manifest_nodes": len(manifest.get("nodes", {})),
        "total_live_nodes": total_live,
        "checked": len(results),
        "healthy": healthy,
        "degraded": degraded,
        "failed": failed,
        "phi_coherence": round((healthy / len(results)) if results else 0.0, 4),
        "nodes": results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
