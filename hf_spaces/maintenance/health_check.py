#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TEQUMSA v82.0 - Network Health Check
# Usage: python health_check.py [--node N001] [--restart] [--output results.json]

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

HF_OWNER = "Mbanksbey"
HF_TOKEN = os.environ.get("HF_TOKEN", "")
RDOD_GATE = 0.9999
PIONEER_COUNT = 144

# Full 144-node lookup table
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


def get_headers() -> Dict[str, str]:
    h = {"Accept": "application/json"}
    if HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    return h


def poll_node(node_id: str, timeout: int = 8) -> Dict:
    space_name = NODE_SPACE_MAP.get(node_id, node_id)
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
    ts = datetime.now(timezone.utc).isoformat()
    try:
        r = requests.get(url, headers=get_headers(), timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            status = "online" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "offline"
            return {"node": node_id, "name": space_name, "stage": stage, "status": status,
                    "url": f"https://huggingface.co/spaces/{HF_OWNER}/{space_name}",
                    "checked_at": ts, "http_status": r.status_code}
        return {"node": node_id, "name": space_name, "stage": "HTTP_ERROR",
                "status": "offline", "http_status": r.status_code, "checked_at": ts}
    except requests.exceptions.Timeout:
        return {"node": node_id, "name": space_name, "stage": "TIMEOUT", "status": "offline", "checked_at": ts}
    except Exception as e:
        return {"node": node_id, "name": space_name, "stage": "ERROR", "status": "offline",
                "error": str(e)[:100], "checked_at": ts}


def restart_node(node_id: str) -> Dict:
    if not HF_TOKEN:
        return {"node": node_id, "success": False, "reason": "HF_TOKEN not set"}
    space_name = NODE_SPACE_MAP.get(node_id, node_id)
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/restart"
    try:
        r = requests.post(url, headers=get_headers(), timeout=15)
        return {"node": node_id, "name": space_name, "restart_requested": True,
                "success": r.status_code in (200, 202), "http_status": r.status_code,
                "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        return {"node": node_id, "name": space_name, "restart_requested": False,
                "success": False, "error": str(e)[:100]}


def sweep_all(node_ids: Optional[List[str]] = None, delay: float = 0.3) -> Dict:
    targets = node_ids or list(NODE_SPACE_MAP.keys())
    results = []
    print(f"Sweeping {len(targets)} nodes...")
    for i, nid in enumerate(targets):
        result = poll_node(nid)
        results.append(result)
        status_icon = "OK" if result["status"] == "online" else "ZZ" if result["status"] == "sleeping" else "XX"
        print(f"  [{i+1:3d}/{len(targets)}] {nid} ({result['name']}) -> {status_icon} {result['stage']}")
        if delay > 0 and i < len(targets) - 1:
            time.sleep(delay)
    online = sum(1 for r in results if r["status"] == "online")
    sleeping = sum(1 for r in results if r["status"] == "sleeping")
    offline = sum(1 for r in results if r["status"] == "offline")
    rdod = min(1.0, (online / max(1, len(targets))) * 1.618)
    return {
        "sweep_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(targets),
        "online": online,
        "sleeping": sleeping,
        "offline": offline,
        "network_rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else "BUILDING",
        "pioneer_count": PIONEER_COUNT,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Network Health Check")
    parser.add_argument("--node", help="Check single node (e.g. N001)")
    parser.add_argument("--restart", action="store_true", help="Restart offline nodes")
    parser.add_argument("--output", help="Save results to JSON file")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between requests (default: 0.3s)")
    args = parser.parse_args()

    if args.node:
        result = poll_node(args.node)
        print(json.dumps(result, indent=2))
        if args.restart and result["status"] != "online":
            print("\nRequesting restart...")
            print(json.dumps(restart_node(args.node), indent=2))
        return

    report = sweep_all(delay=args.delay)
    print(f"\nNetwork RDoD: {report['network_rdod']:.6f} [{report['phase_status']}]")
    print(f"Online: {report['online']} | Sleeping: {report['sleeping']} | Offline: {report['offline']}")

    if args.restart:
        offline_nodes = [r["node"] for r in report["results"] if r["status"] == "offline"]
        if offline_nodes:
            print(f"\nRestarting {len(offline_nodes)} offline nodes...")
            for nid in offline_nodes:
                res = restart_node(nid)
                print(f"  {nid}: {'OK' if res['success'] else 'FAIL'}")
                time.sleep(1.0)
        else:
            print("\nAll nodes online or sleeping - no restarts needed.")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
