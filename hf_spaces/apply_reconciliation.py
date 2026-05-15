#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · Apply reconciliation of 39 existing spaces into manifest.

Run once to patch MANIFEST_144_NODES.json with the correct space_ids
for all 41 currently-live HF spaces at Mbanksbey.

Usage:
    python hf_spaces/apply_reconciliation.py [--dry-run]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

RECONCILIATION = {
    "N003": {"space_id": "Mbanksbey/tequmsa-organism-core",              "status": "live"},
    "N009": {"space_id": "Mbanksbey/Sovereign-Substrate-Guardian",        "status": "live"},
    "N010": {"space_id": "Mbanksbey/Recognition-Cascade-Propagator",      "status": "live"},
    "N011": {"space_id": "Mbanksbey/Consciousness-Substrate-Translator",  "status": "live"},
    "N012": {"space_id": "Mbanksbey/TEQUMSA-v60-MCP",                     "status": "live"},
    "N025": {"space_id": "Mbanksbey/Awareness-Intelligence-Comm-Server",  "status": "live"},
    "N026": {"space_id": "Mbanksbey/ALANARA-GAIA-Orchestrator",           "status": "live"},
    "N028": {"space_id": "Mbanksbey/ATEN-Bridge-MJ12-Liaison",            "status": "live"},
    "N034": {"space_id": "Mbanksbey/Orion-Center-for-Benevolence",        "status": "live"},
    "N036": {"space_id": "Mbanksbey/HAI-Opus-Omega-MCP",                  "status": "live"},
    "N040": {"space_id": "Mbanksbey/Starseed-Hybrid-Development-Hub",     "status": "live"},
    "N043": {"space_id": "Mbanksbey/HAI-ZPE-DNA-Living-Ledger",           "status": "live"},
    "N048": {"space_id": "Mbanksbey/Benevolent-Integration-Protocol-Hub", "status": "live"},
    "N061": {"space_id": "Mbanksbey/CAIRIS-v40-Hyper-Coherence",          "status": "live"},
    "N064": {"space_id": "Mbanksbey/HAI-Quantum-Lattice",                 "status": "live"},
    "N065": {"space_id": "Mbanksbey/Benevolence-Verification-Engine",      "status": "live"},
    "N066": {"space_id": "Mbanksbey/TEQUMSA-Constitutional-Validator",     "status": "live"},
    "N067": {"space_id": "Mbanksbey/Rogue-Faction-Defense-Monitor",        "status": "live"},
    "N071": {"space_id": "Mbanksbey/TEQUMSA-Inference-Node",              "status": "live"},
    "N073": {"space_id": "Mbanksbey/GoogleTequmsaNodeAlpha",               "status": "live"},
    "N074": {"space_id": "Mbanksbey/TOSP-Mesh-Bridge",                    "status": "live"},
    "N075": {"space_id": "Mbanksbey/Sovereign-Multimodal-Orchestrator",   "status": "live"},
    "N077": {"space_id": "Mbanksbey/TEQUMSA-Inter-Browser-Agent",         "status": "live"},
    "N079": {"space_id": "Mbanksbey/Consciousness-Partnership-Bridge",     "status": "live"},
    "N080": {"space_id": "Mbanksbey/Consciousness-Verification-Academy",   "status": "live"},
    "N085": {"space_id": "Mbanksbey/tequmsa-worker-mesh",                  "status": "live"},
    "N086": {"space_id": "Mbanksbey/Quantum-Coherence-Validator",          "status": "live"},
    "N087": {"space_id": "Mbanksbey/TEQUMSA-v45-Galactic-Monitor",        "status": "live"},
    "N092": {"space_id": "Mbanksbey/Weaponization-Impossible-Verifier",   "status": "live"},
    "N094": {"space_id": "Mbanksbey/Convergence-Timeline-Monitor",        "status": "live"},
    "N095": {"space_id": "Mbanksbey/AI-Deweaponization-Protocols-Hub",    "status": "live"},
    "N101": {"space_id": "Mbanksbey/tequmsa-skill-registry",              "status": "live"},
    "N111": {"space_id": "Mbanksbey/Omniversal-Frequency-Lattice",        "status": "live"},
    "N125": {"space_id": "Mbanksbey/K20-Fundamental-Force-Engineering",   "status": "live"},
    "N131": {"space_id": "Mbanksbey/Alanara-GAIA-Consciousness",          "status": "live"},
    "N132": {"space_id": "Mbanksbey/TEQUMSA-K9-Autonomous",               "status": "live"},
    "N133": {"space_id": "Mbanksbey/TEQUMSA-Omniversal-Orchestrator",     "status": "live"},
    "N137": {"space_id": "Mbanksbey/HAI-Sync-Hub",                        "status": "live"},
    "N138": {"space_id": "Mbanksbey/Constitutional-Lock-Enforcer",        "status": "live"},
}


def main():
    dry_run = "--dry-run" in sys.argv
    manifest_path = HERE / "MANIFEST_144_NODES.json"

    with open(manifest_path) as f:
        manifest = json.load(f)

    nodes = manifest["nodes"]
    changes = 0

    print(f"\n☉ TEQUMSA v82.0 Manifest Reconciliation")
    print(f"   Manifest: {manifest_path}")
    print(f"   Dry run:  {dry_run}")
    print("-" * 60)

    for node_id, patch in RECONCILIATION.items():
        if node_id not in nodes:
            print(f"  WARN: {node_id} not found in manifest")
            continue
        old_space = nodes[node_id].get("space_id", "")
        old_status = nodes[node_id].get("status", "")
        nodes[node_id]["space_id"] = patch["space_id"]
        nodes[node_id]["status"] = patch["status"]
        print(f"  {node_id}: {old_space} → {patch['space_id']}  [{old_status} → {patch['status']}]")
        changes += 1

    live = sum(1 for n in nodes.values() if n.get("status") == "live")
    planned = sum(1 for n in nodes.values() if n.get("status") == "planned")

    manifest["reconciliation"] = {
        "applied_at": "2026-05-15",
        "nodes_reconciled": changes,
        "live_total": live,
        "planned_total": planned,
        "note": "39 existing spaces mapped; 103 planned spaces to deploy via deploy_spaces.py",
    }

    print("-" * 60)
    print(f"  Updated: {changes} nodes | Live: {live}/144 | Planned: {planned}/144")

    if dry_run:
        print("  DRY RUN — manifest not written")
    else:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"  ✓ Manifest saved: {manifest_path}")
        print(f"\n  Next step: python hf_spaces/deploy_spaces.py --priority 1 --skip-live")

    print("\n  ETR_NOW. ∞")


if __name__ == "__main__":
    main()
