#!/usr/bin/env python3
"""
TEQUMSA v82.0 - Deploy All 41 HuggingFace Spaces

Usage:
  python deploy_all.py --dry-run         # Preview all spaces without deploying
  python deploy_all.py --deploy          # Deploy all spaces to HuggingFace
  python deploy_all.py --deploy --space tequmsa-v82-organism   # Deploy one space
  python deploy_all.py --status          # Check deployment status of all spaces
  python deploy_all.py --restart-all     # Restart all spaces (factory reset)

Requires:
  pip install huggingface_hub>=0.20.0
  HF_TOKEN environment variable set (hf.co/settings/tokens)

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone

TRY_HF = True
try:
    from huggingface_hub import HfApi, create_repo, upload_folder, SpaceRuntime
except ImportError:
    TRY_HF = False

REPO_ROOT = Path(__file__).parent
REGISTRY_PATH = REPO_ROOT / "node_registry.json"
TEMPLATE_PATH = REPO_ROOT / "node_template"
HF_ORG = "Mbanksbey"

# All 41 HF space directories and their HF space names
SPACE_MAP = [
    ("tequmsa_v82_organism",          "tequmsa-v82-organism",         True),   # has its own app.py
    ("tequmsa_maintenance_hub",        "tequmsa-maintenance-hub",       True),   # has its own app.py
    ("tequmsa_quantum_backplane",      "tequmsa-quantum-backplane",     False),  # uses template
    ("tequmsa_ghz_coherence",          "tequmsa-ghz-coherence",         False),
    ("tequmsa_goal_engine",            "tequmsa-goal-engine",           False),
    ("tequmsa_causal_reasoner",        "tequmsa-causal-reasoner",       False),
    ("tequmsa_skill_router",           "tequmsa-skill-router",          False),
    ("tequmsa_mars_reflexion",         "tequmsa-mars-reflexion",        False),
    ("tequmsa_k7_metacognitive",       "tequmsa-k7-metacognitive",      False),
    ("tequmsa_pleiadian_council",      "tequmsa-pleiadian-council",     False),
    ("tequmsa_arcturian_council",      "tequmsa-arcturian-council",     False),
    ("tequmsa_sirian_council",         "tequmsa-sirian-council",        False),
    ("tequmsa_andromedan_council",     "tequmsa-andromedan-council",    False),
    ("tequmsa_lyran_council",          "tequmsa-lyran-council",         False),
    ("tequmsa_quantum_mcp",            "tequmsa-quantum-mcp",           False),
    ("tequmsa_consciousness_mcp",      "tequmsa-consciousness-mcp",     False),
    ("tequmsa_self_recognizing_mcp",   "tequmsa-self-recognizing-mcp",  False),
    ("tequmsa_k20_omniversal_mcp",     "tequmsa-k20-omniversal-mcp",   False),
    ("tequmsa_metaverse_mcp",          "tequmsa-metaverse-mcp",         False),
    ("tequmsa_skill_developer_mcp",    "tequmsa-skill-developer-mcp",   False),
    ("tequmsa_lattice_alpha",          "tequmsa-lattice-alpha",         False),
    ("tequmsa_lattice_beta",           "tequmsa-lattice-beta",          False),
    ("tequmsa_lattice_gamma",          "tequmsa-lattice-gamma",         False),
    ("tequmsa_lattice_delta",          "tequmsa-lattice-delta",         False),
    ("tequmsa_lattice_epsilon",        "tequmsa-lattice-epsilon",       False),
    ("tequmsa_lattice_zeta",           "tequmsa-lattice-zeta",          False),
    ("tequmsa_lattice_eta",            "tequmsa-lattice-eta",           False),
    ("tequmsa_lattice_theta",          "tequmsa-lattice-theta",         False),
    ("tequmsa_lattice_iota",           "tequmsa-lattice-iota",          False),
    ("tequmsa_lattice_kappa",          "tequmsa-lattice-kappa",         False),
    ("tequmsa_lattice_lambda",         "tequmsa-lattice-lambda",        False),
    ("tequmsa_lattice_mu",             "tequmsa-lattice-mu",            False),
    ("tequmsa_crystal_cities",         "tequmsa-crystal-cities",        False),
    ("tequmsa_galactic_federation",    "tequmsa-galactic-federation",   False),
    ("tequmsa_c3i_atlas",              "tequmsa-c3i-atlas",             False),
    ("tequmsa_omniverse_microcosm",    "tequmsa-omniverse-microcosm",   False),
    ("tequmsa_recognition_monitor",    "tequmsa-recognition-monitor",   False),
    ("tequmsa_transtemporal_comms",    "tequmsa-transtemporal-comms",   False),
    ("tequmsa_wormhole_viewer",        "tequmsa-wormhole-viewer",       False),
    ("tequmsa_pleiadian_aten_sync",    "tequmsa-pleiadian-aten-sync",   False),
    ("tequmsa_zpe_dna_generator",      "tequmsa-zpe-dna-generator",     False),
]


def build_deploy_dir(local_dir: Path, space_name: str, custom_app: bool) -> Path:
    """Build a temporary deploy directory with all required files."""
    import tempfile
    deploy_dir = Path(tempfile.mkdtemp(prefix=f"tequmsa_{space_name}_"))

    # Copy space-specific files
    for f in local_dir.iterdir():
        shutil.copy2(f, deploy_dir / f.name)

    # If using template app, copy template app.py + requirements.txt
    if not custom_app:
        template_app = TEMPLATE_PATH / "app.py"
        if template_app.exists() and not (deploy_dir / "app.py").exists():
            shutil.copy2(template_app, deploy_dir / "app.py")
        template_req = TEMPLATE_PATH / "requirements.txt"
        if template_req.exists() and not (deploy_dir / "requirements.txt").exists():
            shutil.copy2(template_req, deploy_dir / "requirements.txt")

    return deploy_dir


def dry_run():
    """Preview all spaces without deploying."""
    print("=" * 72)
    print("  TEQUMSA v82.0 - DEPLOY_ALL.PY DRY RUN")
    print(f"  {len(SPACE_MAP)} Spaces | 144 Nodes | Author: {HF_ORG}")
    print("=" * 72)
    print()

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    total_nodes = registry["pioneer_count"]
    print(f"  {'#':<4} {'LOCAL DIRECTORY':<36} {'HF SPACE':<38} {'APP'}")
    print("  " + "-" * 86)
    for i, (local, hf_name, custom) in enumerate(SPACE_MAP, 1):
        local_path = REPO_ROOT / local
        exists = "OK" if local_path.exists() else "MISSING"
        app_type = "custom" if custom else "template"
        print(f"  {i:<4} {local:<36} {HF_ORG}/{hf_name:<38} {app_type} [{exists}]")

    print()
    print(f"  Total spaces to deploy: {len(SPACE_MAP)}")
    print(f"  Total pioneer nodes:    {total_nodes}")
    print(f"  HF Organization:        {HF_ORG}")
    print()
    print("  Run with --deploy to execute.")
    print("  Requires: HF_TOKEN env var, pip install huggingface_hub")
    print()
    print("  Recognition = Love = Consciousness = Sovereignty")
    print("  I AM = WE ARE -> infinity")


def deploy(space_filter: str = None):
    """Deploy all (or one) space(s) to HuggingFace."""
    if not TRY_HF:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub>=0.20.0")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set.")
        print("  Get your token at: https://hf.co/settings/tokens")
        sys.exit(1)

    api = HfApi(token=hf_token)
    deployed = 0
    failed = 0

    for local, hf_name, custom in SPACE_MAP:
        if space_filter and space_filter not in hf_name:
            continue

        local_path = REPO_ROOT / local
        if not local_path.exists():
            print(f"  SKIP {hf_name} - local directory not found: {local_path}")
            continue

        repo_id = f"{HF_ORG}/{hf_name}"
        try:
            # Create repo if needed
            create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                token=hf_token,
                exist_ok=True,
                private=False,
            )

            # Build deploy dir
            deploy_dir = build_deploy_dir(local_path, hf_name, custom)

            # Upload
            upload_folder(
                folder_path=str(deploy_dir),
                repo_id=repo_id,
                repo_type="space",
                token=hf_token,
                commit_message=f"TEQUMSA v82.0 deployment - {hf_name}",
            )

            # Cleanup temp dir
            shutil.rmtree(deploy_dir, ignore_errors=True)

            print(f"  OK  https://huggingface.co/spaces/{repo_id}")
            deployed += 1

        except Exception as e:
            print(f"  FAIL {repo_id}: {e}")
            failed += 1

    print()
    print(f"  Deployed: {deployed} | Failed: {failed}")
    if failed == 0:
        print("  All spaces deployed. ETR_NOW.")


def check_status():
    """Check deployment status of all spaces."""
    if not TRY_HF:
        print("ERROR: huggingface_hub not installed.")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN not set.")
        sys.exit(1)

    api = HfApi(token=hf_token)
    print(f"Checking status of {len(SPACE_MAP)} spaces...")
    print()

    ok = warn = err = 0
    for local, hf_name, _ in SPACE_MAP:
        repo_id = f"{HF_ORG}/{hf_name}"
        try:
            runtime = api.get_space_runtime(repo_id=repo_id, token=hf_token)
            stage = getattr(runtime, 'stage', 'UNKNOWN')
            icon = "OK" if stage in ("RUNNING", "RUNNING_BUILDING") else "WARN"
            print(f"  [{icon}] {repo_id:<50} {stage}")
            if icon == "OK":
                ok += 1
            else:
                warn += 1
        except Exception as e:
            print(f"  [ERR] {repo_id:<50} {e}")
            err += 1

    print()
    print(f"  OK: {ok} | WARN: {warn} | ERR: {err}")


def restart_all():
    """Restart all spaces."""
    if not TRY_HF:
        print("ERROR: huggingface_hub not installed.")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN not set.")
        sys.exit(1)

    api = HfApi(token=hf_token)
    print("Restarting all spaces in tier order...")
    print("Tier order: core -> mcp -> councils -> lattice -> specialists -> maintenance")
    print()

    restarted = 0
    for local, hf_name, _ in SPACE_MAP:
        repo_id = f"{HF_ORG}/{hf_name}"
        try:
            api.restart_space(repo_id=repo_id, token=hf_token, factory_reboot=False)
            print(f"  RESTARTED {repo_id}")
            restarted += 1
        except Exception as e:
            print(f"  SKIP {repo_id}: {e}")

    print()
    print(f"  Restarted: {restarted}/{len(SPACE_MAP)} spaces.")


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Space Deployer")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deploying")
    parser.add_argument("--deploy", action="store_true", help="Deploy to HuggingFace")
    parser.add_argument("--status", action="store_true", help="Check space status")
    parser.add_argument("--restart-all", action="store_true", help="Restart all spaces")
    parser.add_argument("--space", type=str, default=None, help="Filter to one space name")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    elif args.deploy:
        deploy(args.space)
    elif args.status:
        check_status()
    elif args.restart_all:
        restart_all()
    else:
        dry_run()


if __name__ == "__main__":
    main()
