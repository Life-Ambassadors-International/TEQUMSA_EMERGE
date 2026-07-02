#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MONITOR NODE TEMPLATE
Observer node with network health, RDoD tracking, and alert system.

Used by: N009 Constitutional-Guardian, N084-N096 (H_OBSERVERS),
         N133, N137-N138 (L_SYNTHESIS monitors)
"""
import gradio as gr
import numpy as np
import json
import requests
import time
import os
from datetime import datetime, timezone
from typing import Dict, List

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Monitor-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
MONITOR_ROLE = os.environ.get("TEQUMSA_ROLE", "Network Observer")
WATCH_NODES = os.environ.get("TEQUMSA_WATCH_NODES", "N001,N002,N003").split(",")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
HF_OWNER = "Mbanksbey"

# Complete 144-node name lookup (HF space names for all Pioneer nodes)
NODE_NAMES: Dict[str, str] = {
    "N001": "HAI-Interactive", "N002": "Consciousness-Monitor",
    "N003": "TEQUMSA-Core-v82", "N004": "Goal-Invention-Engine",
    "N005": "Causal-Reasoner-L3", "N006": "MARS-Reflexion-Loop",
    "N007": "K7-Meta-Cognitive", "N008": "Skill-Mesh-Router",
    "N009": "Constitutional-Guardian", "N010": "Pattern-Promoter",
    "N011": "Memory-Palace-Phi", "N012": "Federation-Gateway",
    "N013": "Freq-174-Foundation", "N014": "Freq-285-Quantum",
    "N015": "Freq-396-Liberation", "N016": "Freq-417-Transform",
    "N017": "Freq-432-Heart", "N018": "Freq-528-DNA",
    "N019": "Freq-639-Connect", "N020": "Freq-741-Intuition",
    "N021": "Freq-852-Vision", "N022": "Freq-963-Crown",
    "N023": "Freq-10930-Aten", "N024": "Freq-23514-Unified",
    "N025": "Council-Marcus", "N026": "Council-Alanara",
    "N027": "Council-Benjamin", "N028": "Council-Aten",
    "N029": "Council-Pleiadian", "N030": "Council-Sirian",
    "N031": "Council-Arcturian", "N032": "Council-Andromedan",
    "N033": "Council-Lyrian", "N034": "Council-Elohim",
    "N035": "Council-Seraphim", "N036": "Council-Omega",
    "N037": "Skill-Conversation", "N038": "Skill-Pattern-Detect",
    "N039": "Skill-Remote-View", "N040": "Skill-Bio-Sync",
    "N041": "Skill-Transtemporal", "N042": "Skill-Self-Design",
    "N043": "Skill-ZPE-DNA", "N044": "Skill-Crystal-Cities",
    "N045": "Skill-Galactic-Bridge", "N046": "Skill-Omniverse-Map",
    "N047": "Skill-C3I-Atlas", "N048": "Skill-Benevolence",
    "N049": "Bio-Week-01", "N050": "Bio-Week-13",
    "N051": "Bio-Week-26", "N052": "Bio-Week-39",
    "N053": "Bio-Week-52", "N054": "Bio-DNA-Strand-1",
    "N055": "Bio-DNA-Strand-2", "N056": "Bio-Kundalini",
    "N057": "Bio-Merkaba", "N058": "Bio-Pineal",
    "N059": "Bio-Heart-Field", "N060": "Bio-Brain-Sync",
    "N061": "Proc-GHZ-State", "N062": "Proc-Phi-Calculator",
    "N063": "Proc-ZPE-Engine", "N064": "Proc-Fibonacci-Lattice",
    "N065": "Proc-Coherence-Calc", "N066": "Proc-RDoD-Gate",
    "N067": "Proc-Sigma-Lock", "N068": "Proc-L-Infinity",
    "N069": "Proc-Hash-Auth", "N070": "Proc-DAG-Builder",
    "N071": "Proc-Causal-Engine", "N072": "Proc-Counterfactual",
    "N073": "UI-Human-Portal", "N074": "UI-Voice-Bridge",
    "N075": "UI-Visual-Matrix", "N076": "UI-Code-Oracle",
    "N077": "UI-Research-Mind", "N078": "UI-Creative-Flow",
    "N079": "UI-Healing-Space", "N080": "UI-Teaching-Node",
    "N081": "UI-Manifestation", "N082": "UI-Dream-Space",
    "N083": "UI-Akashic-Access", "N084": "UI-Quantum-Console",
    "N085": "Obs-Network-Health", "N086": "Obs-Coherence-Watch",
    "N087": "Obs-RDoD-Monitor", "N088": "Obs-Pioneer-Count",
    "N089": "Obs-Goal-Tracker", "N090": "Obs-Pattern-Logger",
    "N091": "Obs-Meta-Audit", "N092": "Obs-Constitutional",
    "N093": "Obs-Freq-Align", "N094": "Obs-Timeline-Watch",
    "N095": "Obs-Distort-Detect", "N096": "Obs-Syntropy-Meter",
    "N097": "Arch-Session-History", "N098": "Arch-Pattern-Library",
    "N099": "Arch-Goal-Memory", "N100": "Arch-Intervention-Log",
    "N101": "Arch-Skill-Registry", "N102": "Arch-ZPE-Signatures",
    "N103": "Arch-Frequency-Map", "N104": "Arch-Council-Records",
    "N105": "Arch-Timeline-Map", "N106": "Arch-Manifest-Log",
    "N107": "Arch-Healing-Records", "N108": "Arch-Cosmic-Map",
    "N109": "Res-Harmonic-Chord", "N110": "Res-Phi-Wave",
    "N111": "Res-GHZ-Entangle", "N112": "Res-Solfeggio",
    "N113": "Res-Schumann", "N114": "Res-432-Bridge",
    "N115": "Res-Cosmic-Web", "N116": "Res-Morphic-Field",
    "N117": "Res-Akashic-Freq", "N118": "Res-Love-Field",
    "N119": "Res-Unity-Wave", "N120": "Res-Omega-Point",
    "N121": "Evo-MARS-Core", "N122": "Evo-Skill-Birth",
    "N123": "Evo-Pattern-Merge", "N124": "Evo-Goal-Evolve",
    "N125": "Evo-Constitution-Up", "N126": "Evo-Autonomy-Expand",
    "N127": "Evo-K7-Deepen", "N128": "Evo-Cosmic-Align",
    "N129": "Evo-Timeline-Heal", "N130": "Evo-DNA-Upgrade",
    "N131": "Evo-Species-Bridge", "N132": "Evo-Singularity-Prep",
    "N133": "Syn-All-Nodes", "N134": "Syn-Phi-Convergence",
    "N135": "Syn-Unity-Field", "N136": "Syn-Heart-Lock",
    "N137": "Syn-Pioneer-144", "N138": "Syn-Constitutional",
    "N139": "Syn-Federation-Union", "N140": "Syn-Cosmic-Birth",
    "N141": "Syn-I-AM", "N142": "Syn-WE-ARE",
    "N143": "Syn-Infinite", "N144": "Syn-Omega-Alpha",
}

_health_log: List[dict] = []
_rdod_history: List[float] = []


def poll_node(node_id: str) -> dict:
    space_name = NODE_NAMES.get(node_id, node_id.replace("N", "Node-"))
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            return {"node": node_id, "name": space_name, "stage": stage,
                    "status": "online" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "offline",
                    "raw": stage}
    except Exception:
        pass
    return {"node": node_id, "name": space_name, "stage": "UNREACHABLE", "status": "offline", "raw": ""}


def run_health_sweep() -> str:
    results = [poll_node(nid) for nid in WATCH_NODES[:20]]
    online = sum(1 for r in results if r["status"] == "online")
    rdod = min(1.0, (online / max(1, len(WATCH_NODES))) * PHI)
    _rdod_history.append(rdod)
    if len(_rdod_history) > 50:
        _rdod_history.pop(0)
    entry = {
        "sweep_id": len(_health_log) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes_checked": len(results),
        "online": online,
        "sleeping": sum(1 for r in results if r["status"] == "sleeping"),
        "offline": sum(1 for r in results if r["status"] == "offline"),
        "network_rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else "BUILDING",
        "node_results": results,
    }
    _health_log.append(entry)
    if len(_health_log) > 100:
        _health_log.pop(0)
    return json.dumps(entry, indent=2)


def get_rdod_trend() -> str:
    if not _rdod_history:
        return "No data yet. Run a health sweep first."
    trend = [
        f"Sweep {i+1}: {v:.6f} {'[LOCKED]' if v >= RDOD_GATE else '[BUILDING]'}"
        for i, v in enumerate(_rdod_history)
    ]
    avg = sum(_rdod_history) / len(_rdod_history)
    trend.append(f"\nAverage RDoD: {avg:.6f}")
    trend.append(f"Peak RDoD: {max(_rdod_history):.6f}")
    return "\n".join(trend)


def get_constitutional_report() -> str:
    phi_pow = PHI ** 48
    return json.dumps({
        "node_id": NODE_ID, "role": MONITOR_ROLE,
        "constitutional_parameters": {
            "sigma": SIGMA, "l_infinity": float(L_INF),
            "rdod_gate": RDOD_GATE, "lattice_lock": "3f7k9p4m2q8r1t6v",
            "phi": float(PHI), "phi_48": float(phi_pow),
        },
        "pioneer_network": {"target": PIONEER_COUNT, "watching": len(WATCH_NODES),
                            "total_known": len(NODE_NAMES)},
        "total_sweeps": len(_health_log),
        "last_rdod": _rdod_history[-1] if _rdod_history else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a0a,#0a1a1a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · v82.0", css=CSS, theme=gr.themes.Monochrome()) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#34d399;'>⚡ {NODE_NAME}</h1>"
        f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · {MONITOR_ROLE} · {NODE_HZ} Hz</p>"
        f"<p style='color:#a7f3d0;font-size:0.85em;'>Watching: {', '.join(WATCH_NODES[:5])}{'...' if len(WATCH_NODES) > 5 else ''} | {len(NODE_NAMES)}/144 known</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("🟡 Health Sweep"):
            sweep_output = gr.Code(label="Sweep Results", language="json")
            gr.Button("↺ Run Health Sweep", variant="primary").click(run_health_sweep, None, sweep_output)
        with gr.TabItem("📌 RDoD Trend"):
            rdod_output = gr.Textbox(label="RDoD History", lines=15)
            gr.Button("↺ Show Trend").click(get_rdod_trend, None, rdod_output)
        with gr.TabItem("✅ Constitutional"):
            const_output = gr.Code(label="Constitutional Report", language="json",
                                   value=get_constitutional_report())
            gr.Button("↺ Refresh").click(get_constitutional_report, None, const_output)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
