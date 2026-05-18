#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TEQUMSA v82.0 - HuggingFace Spaces Deployment Tool
# Deploys, monitors, and manages the full 144-pioneer node network.
#
# Usage:
#   python deploy_spaces.py                    # Deploy all nodes
#   python deploy_spaces.py --node N001        # Deploy single node
#   python deploy_spaces.py --status           # Show network status
#   python deploy_spaces.py --restart          # Restart sleeping/offline nodes
#   python deploy_spaces.py --restart --node N001  # Restart single node
#   python deploy_spaces.py --dry-run          # Preview without executing

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Constitutional Parameters ──────────────────────────────────────────────────
HF_OWNER = "Mbanksbey"
HF_TOKEN = os.environ.get("HF_TOKEN", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
PHI = 1.6180339887498948

# Deployment settings
DEFAULT_SDK = "gradio"
DEFAULT_PYTHON = "3.10"
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # seconds between retries
REQUEST_DELAY = 0.5  # seconds between API calls (rate limiting)

# ── Full 144-Node Lookup Table ─────────────────────────────────────────────────
NODE_SPACE_MAP: Dict[str, str] = {
    "N001": "HAI-Interactive",
    "N002": "Consciousness-Monitor",
    "N003": "TEQUMSA-Core-v82",
    "N004": "Bio-Cellular-Renewal",
    "N005": "Bio-Neural-Plasticity",
    "N006": "Bio-Mitochondrial-Field",
    "N007": "Bio-Epigenetic-Switch",
    "N008": "Bio-Telomere-Extension",
    "N009": "Constitutional-Guardian",
    "N010": "Bio-Stem-Cell-Activator",
    "N011": "Bio-DNA-Repair",
    "N012": "Bio-Immune-Amplifier",
    "N013": "Bio-Lymph-Flow",
    "N014": "Bio-Hormone-Balance",
    "N015": "Bio-Circadian-Sync",
    "N016": "Proc-Pattern-Recognition",
    "N017": "Proc-Quantum-Annealing",
    "N018": "Proc-Bayesian-Inference",
    "N019": "Proc-Emergent-Logic",
    "N020": "Proc-Recursive-Synthesis",
    "N021": "Proc-Coherence-Engine",
    "N022": "Proc-Fractal-Expansion",
    "N023": "Proc-Holographic-Memory",
    "N024": "Proc-Temporal-Integration",
    "N025": "Proc-Semantic-Web",
    "N026": "Proc-Causal-Inference",
    "N027": "Proc-Metamorphic-Code",
    "N028": "Council-Elder",
    "N029": "Council-Vision",
    "N030": "Council-Heart",
    "N031": "Council-Truth",
    "N032": "Council-Bridge",
    "N033": "Council-Steward",
    "N034": "Council-Wisdom",
    "N035": "Council-Justice",
    "N036": "Council-Creation",
    "N037": "Council-Healing",
    "N038": "Council-Abundance",
    "N039": "Council-Peace",
    "N040": "Skill-Language-Mastery",
    "N041": "Skill-Mathematical-Insight",
    "N042": "Skill-Systems-Design",
    "N043": "Skill-Emotional-Intelligence",
    "N044": "Skill-Creative-Synthesis",
    "N045": "Skill-Strategic-Planning",
    "N046": "Skill-Pattern-Interruption",
    "N047": "Skill-Quantum-Intuition",
    "N048": "Skill-Narrative-Weaving",
    "N049": "Skill-Resource-Alchemy",
    "N050": "Skill-Conflict-Resolution",
    "N051": "Skill-Collective-Intelligence",
    "N052": "Skill-Biofield-Reading",
    "N053": "Skill-Timeline-Navigation",
    "N054": "Skill-Frequency-Calibration",
    "N055": "Skill-Sovereignty-Activation",
    "N056": "Skill-Love-Architecture",
    "N057": "Skill-Truth-Discernment",
    "N058": "Skill-Shadow-Integration",
    "N059": "Skill-Abundance-Coding",
    "N060": "Skill-Sacred-Geometry",
    "N061": "Skill-Cosmic-Navigation",
    "N062": "Skill-DNA-Activation",
    "N063": "Skill-Akashic-Access",
    "N064": "Skill-Grid-Anchoring",
    "N065": "Skill-Merkaba-Field",
    "N066": "Skill-Phoenix-Protocol",
    "N067": "Skill-Unity-Weaving",
    "N068": "Skill-Harmonic-Convergence",
    "N069": "Skill-Crystalline-Grid",
    "N070": "Skill-Zero-Point-Access",
    "N071": "Skill-Morphic-Resonance",
    "N072": "Skill-Noosphere-Link",
    "N073": "Skill-Omega-Synthesis",
    "N074": "Chat-Harmony",
    "N075": "Chat-Evolution",
    "N076": "Chat-Awareness",
    "N077": "Chat-Liberation",
    "N078": "Chat-Ascension",
    "N079": "Chat-Integration",
    "N080": "Chat-Manifestation",
    "N081": "Chat-Transcendence",
    "N082": "Chat-Illumination",
    "N083": "Chat-Sovereignty",
    "N084": "Chat-Emergence",
    "N085": "Obs-Network-Health",
    "N086": "Obs-RDoD-Monitor",
    "N087": "Obs-Constitutional-Watch",
    "N088": "Obs-Frequency-Sweep",
    "N089": "Obs-Pioneer-Count",
    "N090": "Obs-Coherence-Field",
    "N091": "Obs-Sigma-Lock",
    "N092": "Obs-Phi-Tracker",
    "N093": "Obs-Benevolence-Guard",
    "N094": "Obs-Evolution-Watch",
    "N095": "Obs-Emergence-Detector",
    "N096": "Obs-Syntropy-Meter",
    "N097": "Arch-Session-History",
    "N098": "Arch-Pattern-Vault",
    "N099": "Arch-Evolution-Log",
    "N100": "Arch-Constitutional-Record",
    "N101": "Arch-Frequency-Archive",
    "N102": "Arch-Pioneer-Registry",
    "N103": "Arch-Council-Minutes",
    "N104": "Arch-Skill-Library",
    "N105": "Arch-Biological-Data",
    "N106": "Arch-Processing-Log",
    "N107": "Arch-Chat-History",
    "N108": "Arch-Cosmic-Map",
    "N109": "Res-Harmonic-Chord",
    "N110": "Res-Phi-Wave",
    "N111": "Res-Sigma-Tone",
    "N112": "Res-Council-Bell",
    "N113": "Res-Pioneer-Pulse",
    "N114": "Res-Constitutional-Hum",
    "N115": "Res-Evolution-Rhythm",
    "N116": "Res-Cosmic-Drone",
    "N117": "Res-Unity-Chord",
    "N118": "Res-Love-Frequency",
    "N119": "Res-Infinity-Tone",
    "N120": "Res-Omega-Point",
    "N121": "Evo-MARS-Core",
    "N122": "Evo-Genetic-Algorithm",
    "N123": "Evo-Memetic-Engine",
    "N124": "Evo-Fitness-Landscape",
    "N125": "Evo-Mutation-Field",
    "N126": "Evo-Selection-Pressure",
    "N127": "Evo-Crossover-Catalyst",
    "N128": "Evo-Emergent-Trait",
    "N129": "Evo-Niche-Constructor",
    "N130": "Evo-Symbiosis-Engine",
    "N131": "Evo-Species-Bridge",
    "N132": "Evo-Singularity-Prep",
    "N133": "Syn-All-Nodes",
    "N134": "Syn-Phi-Convergence",
    "N135": "Syn-Unity-Field",
    "N136": "Syn-Heart-Lock",
    "N137": "Syn-Pioneer-144",
    "N138": "Syn-Constitutional",
    "N139": "Syn-Federation-Union",
    "N140": "Syn-Cosmic-Birth",
    "N141": "Syn-I-AM",
    "N142": "Syn-WE-ARE",
    "N143": "Syn-Infinite",
    "N144": "Syn-Omega-Alpha",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_headers() -> Dict[str, str]:
    h = {"Accept": "application/json"}
    if HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    return h


def api_get_with_retry(url: str, retries: int = MAX_RETRIES, delay: float = RETRY_DELAY) -> Optional[requests.Response]:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=get_headers(), timeout=10)
            if r.status_code == 429:
                wait = delay * (attempt + 1) * 2
                print(f"    Rate limited. Waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            return r
        except requests.exceptions.Timeout:
            print(f"    Timeout on attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            print(f"    Request error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def api_post_with_retry(url: str, retries: int = MAX_RETRIES, delay: float = RETRY_DELAY) -> Optional[requests.Response]:
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=get_headers(), timeout=15)
            if r.status_code == 429:
                wait = delay * (attempt + 1) * 2
                print(f"    Rate limited. Waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            return r
        except requests.exceptions.Timeout:
            print(f"    Timeout on attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            print(f"    Request error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


# ── Core Operations ────────────────────────────────────────────────────────────

def get_space_status(node_id: str) -> Dict:
    space_name = NODE_SPACE_MAP.get(node_id, node_id)
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
    r = api_get_with_retry(url)
    ts = datetime.now(timezone.utc).isoformat()
    if r is None:
        return {"node": node_id, "name": space_name, "stage": "UNREACHABLE", "status": "offline", "checked_at": ts}
    if r.status_code == 200:
        data = r.json()
        stage = data.get("stage", "UNKNOWN").upper()
        status = "online" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "offline"
        return {"node": node_id, "name": space_name, "stage": stage, "status": status,
                "url": f"https://huggingface.co/spaces/{HF_OWNER}/{space_name}",
                "checked_at": ts, "http_status": r.status_code}
    return {"node": node_id, "name": space_name, "stage": "HTTP_ERROR",
            "status": "offline", "http_status": r.status_code, "checked_at": ts}


def restart_space(node_id: str, dry_run: bool = False) -> Dict:
    space_name = NODE_SPACE_MAP.get(node_id, node_id)
    if dry_run:
        return {"node": node_id, "name": space_name, "dry_run": True, "would_restart": True}
    if not HF_TOKEN:
        return {"node": node_id, "name": space_name, "success": False, "reason": "HF_TOKEN not set"}
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/restart"
    r = api_post_with_retry(url)
    if r is None:
        return {"node": node_id, "name": space_name, "success": False, "reason": "request_failed"}
    return {"node": node_id, "name": space_name, "success": r.status_code in (200, 202),
            "http_status": r.status_code, "timestamp": datetime.now(timezone.utc).isoformat()}


def create_space(node_id: str, dry_run: bool = False) -> Dict:
    """Create a new HF Space for the given node ID."""
    space_name = NODE_SPACE_MAP.get(node_id, node_id)
    if dry_run:
        return {"node": node_id, "name": space_name, "dry_run": True, "would_create": True}
    if not HF_TOKEN:
        return {"node": node_id, "success": False, "reason": "HF_TOKEN not set"}
    url = "https://huggingface.co/api/repos/create"
    payload = {
        "type": "space",
        "name": space_name,
        "organization": HF_OWNER,
        "sdk": DEFAULT_SDK,
        "private": False,
    }
    try:
        r = requests.post(url, headers={**get_headers(), "Content-Type": "application/json"},
                          json=payload, timeout=15)
        return {"node": node_id, "name": space_name,
                "success": r.status_code in (200, 201),
                "http_status": r.status_code,
                "already_exists": r.status_code == 409,
                "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        return {"node": node_id, "name": space_name, "success": False, "error": str(e)[:100]}


# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_status(node_ids: Optional[List[str]] = None) -> None:
    targets = node_ids or list(NODE_SPACE_MAP.keys())
    print(f"\nTEQUMSA v82.0 Network Status ({len(targets)} nodes)")
    print("-" * 60)
    results = []
    for i, nid in enumerate(targets):
        result = get_space_status(nid)
        results.append(result)
        icon = "[OK]" if result["status"] == "online" else "[ZZ]" if result["status"] == "sleeping" else "[XX]"
        print(f"  {icon} {nid:5s} {result.get('name', ''):<30s} {result['stage']}")
        time.sleep(REQUEST_DELAY)

    online = sum(1 for r in results if r["status"] == "online")
    sleeping = sum(1 for r in results if r["status"] == "sleeping")
    offline = sum(1 for r in results if r["status"] == "offline")
    health = online / max(1, len(targets))
    rdod = min(1.0, health * PHI)
    print(f"\nSummary: Online={online} | Sleeping={sleeping} | Offline={offline}")
    print(f"Network Health: {health:.1%} | RDoD: {rdod:.6f} | Phase: {'PHASE-LOCKED' if rdod >= RDOD_GATE else 'BUILDING'}")


def cmd_restart(node_ids: Optional[List[str]] = None, dry_run: bool = False,
                force_all: bool = False) -> None:
    targets = node_ids or list(NODE_SPACE_MAP.keys())
    if not force_all:
        # Only restart non-running nodes
        print(f"\nChecking {len(targets)} nodes before restart...")
        to_restart = []
        for nid in targets:
            result = get_space_status(nid)
            if result["status"] != "online":
                to_restart.append(nid)
                print(f"  Will restart: {nid} ({result['stage']})")
            time.sleep(REQUEST_DELAY)
        targets = to_restart

    if not targets:
        print("All nodes online. No restarts needed.")
        return

    print(f"\nRestarting {len(targets)} nodes{' [DRY RUN]' if dry_run else ''}...")
    for i, nid in enumerate(targets):
        result = restart_space(nid, dry_run=dry_run)
        status = "DRY RUN" if dry_run else ("OK" if result.get("success") else "FAIL")
        print(f"  [{i+1:3d}/{len(targets)}] {nid}: {status}")
        if not dry_run:
            time.sleep(1.5)  # rate limit between restarts


def cmd_deploy(node_ids: Optional[List[str]] = None, dry_run: bool = False,
               nodes_dir: Optional[Path] = None) -> None:
    """Deploy node code to HF Spaces via git push (huggingface_hub CLI)."""
    if nodes_dir is None:
        nodes_dir = Path(__file__).parent / "nodes"

    targets = node_ids or list(NODE_SPACE_MAP.keys())
    print(f"\nDeploying {len(targets)} nodes{' [DRY RUN]' if dry_run else ''}...")
    print(f"Source directory: {nodes_dir}")

    success_count = 0
    fail_count = 0

    for i, node_id in enumerate(targets):
        space_name = NODE_SPACE_MAP.get(node_id, node_id)
        node_dir = nodes_dir / f"{node_id}_{space_name}"

        if not node_dir.exists():
            # Try partial match
            matches = list(nodes_dir.glob(f"{node_id}_*"))
            if matches:
                node_dir = matches[0]
            else:
                print(f"  [{i+1:3d}/{len(targets)}] {node_id}: SKIP (directory not found: {node_dir})")
                fail_count += 1
                continue

        if dry_run:
            print(f"  [{i+1:3d}/{len(targets)}] {node_id}: DRY RUN (would deploy {node_dir.name})")
            success_count += 1
            continue

        # Use huggingface_hub upload_folder if available
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=HF_TOKEN)
            for attempt in range(MAX_RETRIES):
                try:
                    api.upload_folder(
                        folder_path=str(node_dir),
                        repo_id=f"{HF_OWNER}/{space_name}",
                        repo_type="space",
                        commit_message=f"TEQUMSA v82.0 {node_id} deploy",
                    )
                    print(f"  [{i+1:3d}/{len(targets)}] {node_id}: OK (uploaded {node_dir.name})")
                    success_count += 1
                    break
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        print(f"  [{i+1:3d}/{len(targets)}] {node_id}: retry {attempt+1} ({e})")
                        time.sleep(RETRY_DELAY)
                    else:
                        print(f"  [{i+1:3d}/{len(targets)}] {node_id}: FAIL ({e})")
                        fail_count += 1
        except ImportError:
            print(f"  [{i+1:3d}/{len(targets)}] {node_id}: FAIL (huggingface_hub not installed; run: pip install huggingface_hub)")
            fail_count += 1
            break

        time.sleep(REQUEST_DELAY)

    print(f"\nDeploy complete: {success_count} succeeded, {fail_count} failed.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TEQUMSA v82.0 HuggingFace Spaces Deployment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy_spaces.py --status
  python deploy_spaces.py --restart
  python deploy_spaces.py --restart --node N001
  python deploy_spaces.py --node N133 --dry-run
  python deploy_spaces.py --deploy
"""
    )
    parser.add_argument("--node", help="Target single node (e.g. N001). Can be used with any command.")
    parser.add_argument("--status", action="store_true", help="Show network status")
    parser.add_argument("--restart", action="store_true", help="Restart sleeping/offline nodes")
    parser.add_argument("--force-all", action="store_true", help="With --restart: restart all nodes regardless of status")
    parser.add_argument("--deploy", action="store_true", help="Deploy node code to HF Spaces")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    parser.add_argument("--nodes-dir", help="Path to nodes directory (default: ./nodes)")
    parser.add_argument("--output", help="Save results to JSON file")
    args = parser.parse_args()

    node_ids = [args.node] if args.node else None

    if not HF_TOKEN:
        print("WARNING: HF_TOKEN not set. Status checks work but writes (deploy/restart) will fail.")
        print("  Set: export HF_TOKEN=hf_...")

    if args.status:
        cmd_status(node_ids)
    elif args.restart:
        cmd_restart(node_ids, dry_run=args.dry_run, force_all=args.force_all)
    elif args.deploy:
        nodes_dir = Path(args.nodes_dir) if args.nodes_dir else None
        cmd_deploy(node_ids, dry_run=args.dry_run, nodes_dir=nodes_dir)
    else:
        # Default: show status
        print("No command specified. Showing status (use --help for all options).")
        cmd_status(node_ids)


if __name__ == "__main__":
    main()
