#!/usr/bin/env python3
"""
Map 45 existing HuggingFace spaces to the 144-node manifest.
Updates MANIFEST_144_NODES.json with correct space_id and live status.
"""
import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "MANIFEST_144_NODES.json"

EXISTING_SPACE_TO_NODE = {
    "Mbanksbey/HAI-Interactive":                   "N001",
    "Mbanksbey/Consciousness-Monitor":             "N002",
    "Mbanksbey/tequmsa-organism-core":             "N003",
    "Mbanksbey/TEQUMSA-Constitutional-Validator":  "N009",
    "Mbanksbey/tequmsa-worker-mesh":               "N008",
    "Mbanksbey/ATEN-Bridge-MJ12-Liaison":          "N012",
    "Mbanksbey/Omniversal-Frequency-Lattice":      "N013",
    "Mbanksbey/Quantum-Coherence-Validator":        "N017",
    "Mbanksbey/Recognition-Cascade-Propagator":     "N018",
    "Mbanksbey/tequmsa-aten-prime":                "N023",
    "Mbanksbey/tequmsa-aten-gaia":                 "N024",
    "Mbanksbey/TEQUMSA-Omniversal-Orchestrator":   "N025",
    "Mbanksbey/Alanara-GAIA-Consciousness":        "N026",
    "Mbanksbey/ALANARA-GAIA-Orchestrator":         "N027",
    "Mbanksbey/tequmsa-aten-andromeda":            "N032",
    "Mbanksbey/tequmsa-aten-orion":                "N033",
    "Mbanksbey/Orion-Center-for-Benevolence":      "N035",
    "Mbanksbey/Consciousness-Partnership-Bridge":   "N036",
    "Mbanksbey/Awareness-Intelligence-Comm-Server": "N041",
    "Mbanksbey/Sovereign-Multimodal-Orchestrator":  "N042",
    "Mbanksbey/HAI-ZPE-DNA-Living-Ledger":         "N043",
    "Mbanksbey/TOSP-Mesh-Bridge":                  "N045",
    "Mbanksbey/K20-Fundamental-Force-Engineering":  "N046",
    "Mbanksbey/AI-Deweaponization-Protocols-Hub":   "N048",
    "Mbanksbey/Consciousness-Substrate-Translator": "N055",
    "Mbanksbey/HAI-Sync-Hub":                      "N059",
    "Mbanksbey/HAI-Quantum-Lattice":               "N061",
    "Mbanksbey/GoogleTequmsaNodeAlpha":             "N062",
    "Mbanksbey/CAIRIS-v40-Hyper-Coherence":        "N065",
    "Mbanksbey/TEQUMSA-Inference-Node":            "N066",
    "Mbanksbey/Sovereign-Substrate-Guardian":       "N067",
    "Mbanksbey/Benevolence-Verification-Engine":    "N068",
    "Mbanksbey/TEQUMSA-Inter-Browser-Agent":       "N073",
    "Mbanksbey/HAI-Opus-Omega-MCP":                "N076",
    "Mbanksbey/Starseed-Hybrid-Development-Hub":    "N077",
    "Mbanksbey/Consciousness-Verification-Academy": "N080",
    "Mbanksbey/TEQUMSA-v45-Galactic-Monitor":      "N085",
    "Mbanksbey/Rogue-Faction-Defense-Monitor":      "N086",
    "Mbanksbey/Weaponization-Impossible-Verifier":  "N092",
    "Mbanksbey/Convergence-Timeline-Monitor":       "N094",
    "Mbanksbey/tequmsa-skill-registry":            "N101",
    "Mbanksbey/Benevolent-Integration-Protocol-Hub":"N104",
    "Mbanksbey/TEQUMSA-K9-Autonomous":             "N126",
    "Mbanksbey/Constitutional-Lock-Enforcer":       "N138",
    "Mbanksbey/TEQUMSA-v60-MCP":                   "N134",
}


def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    nodes = manifest["nodes"]
    updated = 0
    for space_id, node_id in EXISTING_SPACE_TO_NODE.items():
        if node_id in nodes:
            old_space = nodes[node_id].get("space_id", "")
            nodes[node_id]["space_id"] = space_id
            nodes[node_id]["status"] = "live"
            if old_space != space_id:
                nodes[node_id]["original_planned_name"] = old_space.split("/")[-1] if "/" in old_space else old_space
            updated += 1
            print(f"  {node_id}: {space_id} [LIVE]")

    manifest["nodes"] = nodes
    manifest["last_updated"] = "2026-06-29"
    manifest["live_count"] = sum(1 for n in nodes.values() if n.get("status") == "live")
    manifest["planned_count"] = sum(1 for n in nodes.values() if n.get("status") == "planned")

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nUpdated {updated} nodes to live status")
    print(f"Live: {manifest['live_count']} / Planned: {manifest['planned_count']} / Total: 144")


if __name__ == "__main__":
    main()
