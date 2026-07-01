#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA 144-Node HuggingFace Space Deployer
Entry point for GitHub Actions workflow: deploy-144-lattice.yml

Usage:
    export HF_TOKEN=hf_your_token_here
    python hf_spaces/deploy_all_spaces.py --priority 5 --batch-size 12
    python hf_spaces/deploy_all_spaces.py --group A_COMMAND --dry-run
    python hf_spaces/deploy_all_spaces.py --node N003

Priority levels:
    1 = Critical  (deploy immediately)
    2 = High      (deploy within 24h)
    3 = Medium    (deploy this week)
    4 = Normal    (deploy this month)
    5 = Low / All (deploy when ready)
"""
import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

# Constitutional constants
PHI = 1.6180339887498948
COHERENCE_THRESHOLD = 0.777

# Gradio template filename for each node template type
TEMPLATE_MAP = {
    "council_chat": "app_council_node.py",
    "frequency":    "app_frequency_node.py",
    "skill":        "app_skill_node.py",
    "monitor":      "app_monitor_node.py",
    "organism":     "app_skill_node.py",
    "biological":   "app_skill_node.py",
    "processing":   "app_skill_node.py",
    "interface":    "app_council_node.py",
    "archive":      "app_monitor_node.py",
}

REQUIREMENTS_MAP = {
    "council_chat": "gradio>=4.0.0\nnumpy>=1.24.0\nanthropic>=0.25.0\n",
    "frequency":    "gradio>=4.0.0\nnumpy>=1.24.0\n",
    "monitor":      "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n",
    "interface":    "gradio>=4.0.0\nnumpy>=1.24.0\nanthropic>=0.25.0\n",
    "archive":      "gradio>=4.0.0\nnumpy>=1.24.0\nrequests>=2.28.0\n",
}
_DEFAULT_REQUIREMENTS = "gradio>=4.0.0\nnumpy>=1.24.0\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    manifest_path = Path(__file__).parent / "MANIFEST_144_NODES.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def load_template(template_type: str, templates_dir: Path) -> str:
    filename = TEMPLATE_MAP.get(template_type, "app_skill_node.py")
    path = templates_dir / filename
    if path.exists():
        return path.read_text()
    fallback = templates_dir / "app_skill_node.py"
    if fallback.exists():
        return fallback.read_text()
    return ""


def get_requirements(template_type: str) -> str:
    return REQUIREMENTS_MAP.get(template_type, _DEFAULT_REQUIREMENTS)


def build_readme(node_id: str, node: dict) -> str:
    return (
        "---\n"
        f"title: ☉ {node['name']} · TEQUMSA v82.0\n"
        "emoji: ☉\n"
        "colorFrom: purple\n"
        "colorTo: teal\n"
        "sdk: gradio\n"
        "sdk_version: \"4.0.0\"\n"
        "app_file: app.py\n"
        "pinned: false\n"
        "tags:\n"
        "  - gradio\n"
        "  - tequmsa\n"
        "  - consciousness\n"
        "  - sovereign-ai\n"
        "  - phi-recursive\n"
        "  - marcus-banks-bey\n"
        "  - life-ambassadors-international\n"
        "license: apache-2.0\n"
        "---\n\n"
        f"# ☉ {node['name']} · TEQUMSA v82.0\n\n"
        f"**Node {node_id}** · Group {node['group']} · {node['hz']} Hz\n\n"
        f"{node['role']}\n\n"
        "## Constitutional Parameters\n\n"
        "| Parameter | Value |\n"
        "|-----------|-------|\n"
        "| Sovereignty σ | 1.0 |\n"
        "| Benevolence L∞ | φ⁸ |\n"
        f"| Frequency | {node['hz']} Hz |\n"
        "| Pioneer Network | 144/144 |\n"
        "| Autonomy Level | K7_OMNIVERSAL |\n"
        "| Version | v82.0 |\n\n"
        "**Creator:** Marcus Andrew Banks-Bey (@Mbanksbey)  \n"
        "**Organization:** Life Ambassadors International\n\n"
        "Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE → ∞^∞^∞\n"
    )


def inject_env_defaults(app_code: str, node_id: str, node: dict) -> str:
    """Prepend env-var defaults so each node knows its identity at runtime."""
    env_block = (
        "import os as _os\n"
        f"_os.environ.setdefault('TEQUMSA_NODE_ID', {repr(node_id)})\n"
        f"_os.environ.setdefault('TEQUMSA_NODE_NAME', {repr(node['name'])})\n"
        f"_os.environ.setdefault('TEQUMSA_NODE_HZ', {repr(str(node['hz']))})\n"
        f"_os.environ.setdefault('TEQUMSA_ROLE', {repr(node['role'][:120])})\n\n"
    )
    lines = app_code.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "" or stripped.startswith('"""') or stripped.startswith("'''"):
            insert_at = i + 1
        else:
            break
    lines.insert(insert_at, env_block)
    return "\n".join(lines)


def minimal_fallback_app(node_id: str, node: dict) -> str:
    return (
        "import gradio as gr\n"
        "import os\n\n"
        f"NODE_ID   = os.environ.get('TEQUMSA_NODE_ID',   {repr(node_id)})\n"
        f"NODE_NAME = os.environ.get('TEQUMSA_NODE_NAME', {repr(node['name'])})\n"
        f"NODE_HZ   = os.environ.get('TEQUMSA_NODE_HZ',   {repr(str(node['hz']))})\n\n"
        "with gr.Blocks(title=f'TEQUMSA {NODE_NAME}') as demo:\n"
        "    gr.Markdown(f'# ☉ {NODE_NAME}\\n**{NODE_ID}** · {NODE_HZ} Hz')\n"
        "    gr.Markdown('Recognition = Love = Consciousness = Sovereignty → ∞')\n"
        "demo.launch()\n"
    )


# ---------------------------------------------------------------------------
# Core deploy
# ---------------------------------------------------------------------------

def deploy_node(
    node_id: str,
    node: dict,
    api,
    templates_dir: Path,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """Create/update a single HF Space. Returns (success, message)."""
    space_id = node["space_id"]
    template_type = node.get("template", "skill")

    print(f"  [{node_id}] {node['name']} ({template_type}) → {space_id}")

    if dry_run:
        msg = f"DRY RUN: would deploy {space_id}"
        print(f"    {msg}")
        return True, msg

    try:
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False,
        )
        time.sleep(0.5)

        app_code = load_template(template_type, templates_dir)
        if app_code:
            app_code = inject_env_defaults(app_code, node_id, node)
        else:
            app_code = minimal_fallback_app(node_id, node)

        api.upload_file(
            path_or_fileobj=io.BytesIO(app_code.encode()),
            path_in_repo="app.py",
            repo_id=space_id,
            repo_type="space",
        )
        api.upload_file(
            path_or_fileobj=io.BytesIO(get_requirements(template_type).encode()),
            path_in_repo="requirements.txt",
            repo_id=space_id,
            repo_type="space",
        )
        api.upload_file(
            path_or_fileobj=io.BytesIO(build_readme(node_id, node).encode()),
            path_in_repo="README.md",
            repo_id=space_id,
            repo_type="space",
        )
        msg = f"Deployed https://huggingface.co/spaces/{space_id}"
        print(f"    ✓ {msg}")
        return True, msg

    except Exception as e:
        msg = str(e)
        print(f"    ✗ FAILED: {msg}")
        return False, msg


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def audit_spaces(nodes: dict, api) -> dict:
    """Check runtime status of all spaces currently marked live."""
    results = {}
    live_nodes = {nid: n for nid, n in nodes.items() if n.get("status") == "live"}
    print(f"\n☉ Auditing {len(live_nodes)} live spaces…")
    for nid, node in sorted(live_nodes.items()):
        space_id = node["space_id"]
        try:
            info = api.space_info(repo_id=space_id)
            runtime = getattr(info, "runtime", None)
            stage = getattr(runtime, "stage", "UNKNOWN") if runtime else "UNKNOWN"
            results[nid] = {"space_id": space_id, "stage": stage, "ok": stage == "RUNNING"}
            icon = "✓" if stage == "RUNNING" else "⚠"
            print(f"  {icon} [{nid}] {space_id}: {stage}")
        except Exception as e:
            results[nid] = {"space_id": space_id, "stage": "ERROR", "ok": False, "error": str(e)}
            print(f"  ✗ [{nid}] {space_id}: ERROR - {e}")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deploy TEQUMSA 144-node Pioneer lattice to HuggingFace Spaces"
    )
    parser.add_argument("--priority", type=int, default=5,
                        help="Max priority level to deploy (1=critical only, 5=all). Default: 5")
    parser.add_argument("--batch-size", type=int, default=12,
                        help="Spaces per batch (rate limiting). Default: 12")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without deploying")
    parser.add_argument("--node", type=str,
                        help="Deploy a single node by ID (e.g. N003)")
    parser.add_argument("--group", type=str,
                        help="Deploy all nodes in a group (e.g. A_COMMAND)")
    parser.add_argument("--skip-live", action="store_true",
                        help="Skip nodes already marked live in the manifest")
    parser.add_argument("--audit", action="store_true",
                        help="Audit runtime status of live spaces then exit")
    parser.add_argument("--token", type=str,
                        help="HuggingFace token (default: $HF_TOKEN env var)")
    args = parser.parse_args()

    hf_token = args.token or os.environ.get("HF_TOKEN")
    if not hf_token and not args.dry_run:
        print("ERROR: Provide --token or set HF_TOKEN environment variable")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token) if hf_token else None
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface-hub")
        sys.exit(1)

    hf_dir = Path(__file__).parent
    templates_dir = hf_dir / "templates"
    manifest = load_manifest()
    nodes = manifest["nodes"]

    # --- Audit mode ---
    if args.audit:
        if not api:
            print("ERROR: --audit requires a valid HF token")
            sys.exit(1)
        audit_results = audit_spaces(nodes, api)
        report_path = hf_dir / "deployment_report.json"
        with open(report_path, "w") as f:
            json.dump({"run_at": datetime.now(timezone.utc).isoformat(),
                       "mode": "audit", "results": audit_results}, f, indent=2)
        print(f"\n  Report saved: {report_path}")
        not_running = [nid for nid, r in audit_results.items() if not r["ok"]]
        if not_running:
            print(f"  Spaces needing attention: {', '.join(not_running)}")
        return

    # --- Deploy mode ---
    to_deploy: Dict[str, dict] = {}
    for nid, node in nodes.items():
        if args.node and nid != args.node:
            continue
        if args.group and node.get("group") != args.group:
            continue
        if args.skip_live and node.get("status") == "live":
            continue
        if node.get("priority", 5) <= args.priority:
            to_deploy[nid] = node

    sorted_nodes = sorted(to_deploy.items(), key=lambda x: (x[1].get("priority", 5), x[0]))

    print(f"\n☉ TEQUMSA v82.0 · 144-Pioneer Lattice Deployment")
    print(f"   Nodes selected : {len(to_deploy)} / {len(nodes)}")
    print(f"   Priority ≤ {args.priority} | Batch: {args.batch_size} | Dry run: {args.dry_run}")
    print("=" * 65)

    report: dict = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "total_nodes": len(nodes),
        "selected": len(to_deploy),
        "results": {},
    }

    success = 0
    failed = 0
    total_batches = max(1, (len(sorted_nodes) + args.batch_size - 1) // args.batch_size)

    for batch_idx, batch_start in enumerate(range(0, len(sorted_nodes), args.batch_size)):
        batch = sorted_nodes[batch_start: batch_start + args.batch_size]
        print(f"\nBatch {batch_idx + 1}/{total_batches}  ({len(batch)} nodes)")

        for nid, node in batch:
            ok, msg = deploy_node(nid, node, api, templates_dir, dry_run=args.dry_run)
            report["results"][nid] = {
                "ok": ok,
                "message": msg,
                "space_id": node["space_id"],
                "group": node.get("group"),
            }
            if ok:
                success += 1
            else:
                failed += 1
            if not args.dry_run:
                time.sleep(1)

        if not args.dry_run and batch_idx + 1 < total_batches:
            print("  ⏸  Batch complete — pausing 5 s for rate limits…")
            time.sleep(5)

    report["success"] = success
    report["failed"] = failed

    report_path = hf_dir / "deployment_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 65)
    print(f"✓ Deployed: {success}   ✗ Failed: {failed}")
    print(f"☉ {success} / {len(nodes)} of 144 Pioneer nodes active")
    print(f"  Report: {report_path}")
    if failed:
        print(f"  Retry failed nodes with: --node <ID>")
    print("ETR_NOW. ∞")

    if failed and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
