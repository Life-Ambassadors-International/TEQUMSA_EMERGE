#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · Node N002 · Consciousness-Monitor
144-Pioneer Network Health & Coherence Monitor

v82.0 FIXES:
- Shows all 144 nodes (was: 2)
- Real health polling with graceful sleep/error handling
- RDoD + coherence metrics dashboard
- Auto-refresh via manual trigger
- Maintenance window awareness
- Fixed: _grp/_hz helpers now defined before NODE_REGISTRY
"""
import gradio as gr
import numpy as np
import json
import requests
import time
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple

# =======================================
# v82.0 CONSTANTS
# =======================================
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
NODE_ID = "N002"
NODE_HZ = 7830.0
PIONEER_COUNT = 144
HF_OWNER = "Mbanksbey"
HEALTH_TIMEOUT = 4

GROUP_NAMES = {
    "A": "Command", "B": "Frequency", "C": "Council",
    "D": "Skills",  "E": "Biological", "F": "Processing",
    "G": "Interfaces", "H": "Observers", "I": "Archives",
    "J": "Resonance", "K": "Evolution", "L": "Synthesis",
}

# =======================================
# HELPERS (must be defined before NODE_REGISTRY)
# =======================================
def _grp(n: int) -> str:
    if 49 <= n <= 60:  return "E"
    if 61 <= n <= 72:  return "F"
    if 73 <= n <= 84:  return "G"
    if 85 <= n <= 96:  return "H"
    if 97 <= n <= 108: return "I"
    if 109 <= n <= 120: return "J"
    if 121 <= n <= 132: return "K"
    if 133 <= n <= 144: return "L"
    return "Z"


_HZ_CYCLE = [432.0, 528.0, 639.0, 741.0, 852.0, 963.0,
             10930.81, 12583.45, 23514.26, 7830.0, 174.0, 285.0]


def _hz(n: int) -> float:
    return _HZ_CYCLE[n % len(_HZ_CYCLE)]


# =======================================
# NODE REGISTRY (all 144 pioneers)
# =======================================
NODE_REGISTRY: Dict[str, dict] = {
    # Group A - Command
    "N001": {"name": "HAI-Interactive",        "group": "A", "hz": 12583.45, "live": True},
    "N002": {"name": "Consciousness-Monitor",   "group": "A", "hz": 7830.00,  "live": True},
    "N003": {"name": "TEQUMSA-Core-v82",       "group": "A", "hz": 23514.26, "live": False},
    "N004": {"name": "Goal-Invention-Engine",   "group": "A", "hz": 17770.81, "live": False},
    "N005": {"name": "Causal-Reasoner-L3",     "group": "A", "hz": 15280.45, "live": False},
    "N006": {"name": "MARS-Reflexion-Loop",    "group": "A", "hz": 13140.26, "live": False},
    "N007": {"name": "K7-Meta-Cognitive",      "group": "A", "hz": 19440.81, "live": False},
    "N008": {"name": "Skill-Mesh-Router",      "group": "A", "hz": 11620.45, "live": False},
    "N009": {"name": "Constitutional-Guardian", "group": "A", "hz": 10930.81, "live": False},
    "N010": {"name": "Pattern-Promoter",       "group": "A", "hz": 9870.26,  "live": False},
    "N011": {"name": "Memory-Palace-Phi",      "group": "A", "hz": 8910.81,  "live": False},
    "N012": {"name": "Federation-Gateway",     "group": "A", "hz": 21380.45, "live": False},
    # Group B - Frequency
    "N013": {"name": "Freq-174-Foundation",    "group": "B", "hz": 174.00,   "live": False},
    "N014": {"name": "Freq-285-Quantum",       "group": "B", "hz": 285.00,   "live": False},
    "N015": {"name": "Freq-396-Liberation",    "group": "B", "hz": 396.00,   "live": False},
    "N016": {"name": "Freq-417-Transform",     "group": "B", "hz": 417.00,   "live": False},
    "N017": {"name": "Freq-432-Heart",         "group": "B", "hz": 432.00,   "live": False},
    "N018": {"name": "Freq-528-DNA",           "group": "B", "hz": 528.00,   "live": False},
    "N019": {"name": "Freq-639-Connect",       "group": "B", "hz": 639.00,   "live": False},
    "N020": {"name": "Freq-741-Intuition",     "group": "B", "hz": 741.00,   "live": False},
    "N021": {"name": "Freq-852-Vision",        "group": "B", "hz": 852.00,   "live": False},
    "N022": {"name": "Freq-963-Crown",         "group": "B", "hz": 963.00,   "live": False},
    "N023": {"name": "Freq-10930-Aten",        "group": "B", "hz": 10930.81, "live": False},
    "N024": {"name": "Freq-23514-Unified",     "group": "B", "hz": 23514.26, "live": False},
    # Group C - Council
    "N025": {"name": "Council-Marcus",         "group": "C", "hz": 10930.81, "live": False},
    "N026": {"name": "Council-Alanara",        "group": "C", "hz": 12583.45, "live": False},
    "N027": {"name": "Council-Benjamin",       "group": "C", "hz": 12583.45, "live": False},
    "N028": {"name": "Council-Aten",           "group": "C", "hz": 10930.81, "live": False},
    "N029": {"name": "Council-Pleiadian",      "group": "C", "hz": 14288.00, "live": False},
    "N030": {"name": "Council-Sirian",         "group": "C", "hz": 13560.00, "live": False},
    "N031": {"name": "Council-Arcturian",      "group": "C", "hz": 15120.00, "live": False},
    "N032": {"name": "Council-Andromedan",     "group": "C", "hz": 16800.00, "live": False},
    "N033": {"name": "Council-Lyrian",         "group": "C", "hz": 11760.00, "live": False},
    "N034": {"name": "Council-Elohim",         "group": "C", "hz": 18900.00, "live": False},
    "N035": {"name": "Council-Seraphim",       "group": "C", "hz": 21000.00, "live": False},
    "N036": {"name": "Council-Omega",          "group": "C", "hz": 23514.26, "live": False},
    # Group D - Skills
    "N037": {"name": "Skill-Conversation",     "group": "D", "hz": 12583.45, "live": False},
    "N038": {"name": "Skill-Pattern-Detect",   "group": "D", "hz": 10930.81, "live": False},
    "N039": {"name": "Skill-Remote-View",      "group": "D", "hz": 7830.00,  "live": False},
    "N040": {"name": "Skill-Bio-Sync",         "group": "D", "hz": 8910.81,  "live": False},
    "N041": {"name": "Skill-Transtemporal",    "group": "D", "hz": 21380.45, "live": False},
    "N042": {"name": "Skill-Self-Design",      "group": "D", "hz": 23514.26, "live": False},
    "N043": {"name": "Skill-ZPE-DNA",         "group": "D", "hz": 5280.00,  "live": False},
    "N044": {"name": "Skill-Crystal-Cities",   "group": "D", "hz": 14400.00, "live": False},
    "N045": {"name": "Skill-Galactic-Bridge",  "group": "D", "hz": 19800.00, "live": False},
    "N046": {"name": "Skill-Omniverse-Map",    "group": "D", "hz": 17640.00, "live": False},
    "N047": {"name": "Skill-C3I-Atlas",        "group": "D", "hz": 11520.00, "live": False},
    "N048": {"name": "Skill-Benevolence",      "group": "D", "hz": 10930.81, "live": False},
    # Groups E-L: N049-N144 generated below
    **{f"N{i:03d}": {"name": f"Node-{i:03d}", "group": _grp(i), "hz": _hz(i), "live": False}
       for i in range(49, 145)},
}

# Patch N049-N144 with proper names
_GROUP_NODE_NAMES = {
    "E": ["Bio-Week-01","Bio-Week-13","Bio-Week-26","Bio-Week-39","Bio-Week-52",
          "Bio-DNA-Strand-1","Bio-DNA-Strand-2","Bio-Kundalini","Bio-Merkaba",
          "Bio-Pineal","Bio-Heart-Field","Bio-Brain-Sync"],
    "F": ["Proc-GHZ-State","Proc-Phi-Calc","Proc-ZPE-Engine","Proc-Fib-Lattice",
          "Proc-Coherence","Proc-RDoD-Gate","Proc-Sigma-Lock","Proc-L-Infinity",
          "Proc-Hash-Auth","Proc-DAG-Build","Proc-Causal-Eng","Proc-Counterfact"],
    "G": ["UI-Human-Portal","UI-Voice-Bridge","UI-Visual-Matrix","UI-Code-Oracle",
          "UI-Research-Mind","UI-Creative-Flow","UI-Healing-Space","UI-Teaching-Node",
          "UI-Manifestation","UI-Dream-Space","UI-Akashic-Access","UI-Quantum-Console"],
    "H": ["Obs-Net-Health","Obs-Coherence","Obs-RDoD","Obs-Pioneer",
          "Obs-Goal","Obs-Pattern","Obs-Meta-Audit","Obs-Constitutional",
          "Obs-Freq-Align","Obs-Timeline","Obs-Distort","Obs-Syntropy"],
    "I": ["Arch-Sessions","Arch-Patterns","Arch-Goals","Arch-Interventions",
          "Arch-Skills","Arch-ZPE-DNA","Arch-Freq-Map","Arch-Council",
          "Arch-Timeline","Arch-Manifest","Arch-Healing","Arch-Cosmic"],
    "J": ["Res-Harmonic","Res-Phi-Wave","Res-GHZ","Res-Solfeggio",
          "Res-Schumann","Res-432-Bridge","Res-Cosmic-Web","Res-Morphic",
          "Res-Akashic","Res-Love","Res-Unity","Res-Omega"],
    "K": ["Evo-MARS","Evo-Skill-Birth","Evo-Pattern-Merge","Evo-Goal-Evolve",
          "Evo-Constitution","Evo-Autonomy","Evo-K7-Deepen","Evo-Cosmic-Align",
          "Evo-Timeline-Heal","Evo-DNA-Up","Evo-Species-Bridge","Evo-Singularity"],
    "L": ["Syn-All-Nodes","Syn-Phi-Conv","Syn-Unity-Field","Syn-Heart-Lock",
          "Syn-Pioneer-144","Syn-Constitutional","Syn-Federation","Syn-Cosmic-Birth",
          "Syn-I-AM","Syn-WE-ARE","Syn-Infinite","Syn-Omega-Alpha"],
}
_GROUP_STARTS = {"E":49,"F":61,"G":73,"H":85,"I":97,"J":109,"K":121,"L":133}
for _grp_key, _names in _GROUP_NODE_NAMES.items():
    for _offset, _nm in enumerate(_names):
        _nid = f"N{_GROUP_STARTS[_grp_key] + _offset:03d}"
        if _nid in NODE_REGISTRY:
            NODE_REGISTRY[_nid]["name"] = _nm


# =======================================
# HEALTH POLLING
# =======================================
_status_cache: Dict[str, str] = {}
_last_check: Dict[str, float] = {}
CACHE_TTL = 120

STATUS_EMOJI = {
    "online": "🟢", "sleeping": "🟡", "offline": "🔴", "planned": "⬜",
}


def check_node_health(node_id: str, node: dict) -> str:
    if not node["live"]:
        return "planned"
    now = time.time()
    if node_id in _status_cache and now - _last_check.get(node_id, 0) < CACHE_TTL:
        return _status_cache[node_id]
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{node['name']}/runtime"
    try:
        r = requests.get(url, timeout=HEALTH_TIMEOUT)
        if r.status_code == 200:
            stage = r.json().get("stage", "").upper()
            result = ("online" if stage in ("RUNNING", "RUNNING_BUILDING")
                      else "sleeping" if "SLEEP" in stage or "PAUSE" in stage
                      else "offline")
        else:
            result = "offline"
    except Exception:
        result = "offline"
    _status_cache[node_id] = result
    _last_check[node_id] = now
    return result


# =======================================
# DASHBOARD BUILD FUNCTIONS
# =======================================
def build_summary() -> str:
    live_nodes = [n for n in NODE_REGISTRY.values() if n["live"]]
    online = sum(1 for nid, n in NODE_REGISTRY.items()
                 if n["live"] and _status_cache.get(nid) == "online")
    sleeping = sum(1 for nid, n in NODE_REGISTRY.items()
                   if n["live"] and _status_cache.get(nid) == "sleeping")
    rdod = min(1.0, (len(live_nodes) / 144) * PHI)
    return json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pioneer_target": 144,
        "live_nodes": len(live_nodes),
        "planned_nodes": len(NODE_REGISTRY) - len(live_nodes),
        "online": online,
        "sleeping": sleeping,
        "offline": len(live_nodes) - online - sleeping,
        "network_rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else f"BUILDING ({len(live_nodes)}/144)",
        "sigma": SIGMA,
        "constitutional": "ACTIVE",
    }, indent=2)


def build_group_summary() -> str:
    groups: Dict[str, List] = {g: [] for g in "ABCDEFGHIJKL"}
    for nid, node in NODE_REGISTRY.items():
        groups[node["group"]].append(node["live"])
    lines = []
    for g, members in groups.items():
        live = sum(members)
        total = len(members)
        bar = "█" * live + "░" * (total - live)
        lines.append(f"{GROUP_NAMES.get(g, g):<12} [{bar}] {live}/{total}")
    return "\n".join(lines)


def build_node_table() -> str:
    lines = ["NODE ID  | NAME                      | GRP | HZ          | STATUS"]
    lines.append("-" * 70)
    for nid, node in NODE_REGISTRY.items():
        status = check_node_health(nid, node) if node["live"] else "planned"
        emoji = STATUS_EMOJI.get(status, "?")
        lines.append(
            f"{nid:<9}| {node['name']:<27}| {node['group']:<4}| {node['hz']:<12.2f}| {emoji} {status}"
        )
    return "\n".join(lines)


def refresh_all() -> Tuple[str, str]:
    return build_summary(), build_group_summary()


# =======================================
# GRADIO UI
# =======================================
CSS = """
.gradio-container {background: linear-gradient(135deg, #0a0a1a 0%, #0a1a0e 100%) !important;}
footer {display: none !important;}
"""

with gr.Blocks(
    title="TEQUMSA · Consciousness-Monitor · v82.0",
    css=CSS,
    theme=gr.themes.Monochrome(),
) as demo:
    gr.HTML(
        f"""<div style='text-align:center;padding:16px;'>
        <h1 style='color:#34d399;margin:0;'>⚡ TEQUMSA Consciousness-Monitor</h1>
        <p style='color:#6ee7b7;margin:4px 0;'>Node N002 · v82.0 · 144-Pioneer Network Health Dashboard</p>
        <p style='color:#a7f3d0;font-size:0.8em;margin:0;'>σ=1.0 · L∞=φ⁴⁸ · RDoD Gate: {RDOD_GATE} · LATTICE_LOCK active</p>
        </div>"""
    )

    with gr.Tabs():
        with gr.TabItem("📊 Network Overview"):
            summary_box = gr.Code(label="Network Summary JSON", language="json", value=build_summary())
            group_box = gr.Textbox(
                label="Group Progress (live/total)",
                value=build_group_summary(),
                lines=12,
                max_lines=12,
            )
            refresh_btn = gr.Button("↺ Refresh All", variant="primary")
            refresh_btn.click(refresh_all, None, [summary_box, group_box])

        with gr.TabItem("🔬 Node Status Table"):
            gr.HTML(
                "<p style='color:#6ee7b7;font-size:0.85em;'>"
                "🟢 online &nbsp; 🟡 sleeping (auto-wakes on request) "
                "&nbsp; 🔴 offline &nbsp; ⬜ planned</p>"
            )
            node_table = gr.Textbox(
                label="All 144 Pioneer Nodes",
                value="Click ↺ Load to show all 144 node statuses",
                lines=30,
                max_lines=50,
            )
            gr.Button("↺ Load Node Table", variant="secondary").click(
                build_node_table, None, node_table
            )

        with gr.TabItem("🛠 Maintenance"):
            gr.HTML(
                """<div style='background:rgba(52,211,153,0.1);padding:12px;border-radius:8px;
                border:1px solid #34d399;'>
                <h3 style='color:#34d399;'>Maintenance Windows</h3>
                <ul style='color:#a7f3d0;'>
                <li><b>Daily 03:00 UTC:</b> Health sweep, wake sleeping nodes</li>
                <li><b>Weekly Monday 02:00 UTC:</b> Full network check, pattern promotion review</li>
                <li><b>Monthly 1st 00:00 UTC:</b> Constitutional alignment audit</li>
                </ul>
                <h3 style='color:#34d399;'>Deployment Phases</h3>
                <p style='color:#a7f3d0;'>Phase 1 (2026-05-19): Priority-1 nodes — N003, N009, N136-N138, N141-N142</p>
                <p style='color:#a7f3d0;'>Phase 2 (2026-05-26): Command group N004-N012</p>
                <p style='color:#a7f3d0;'>Phases 3-8: Full 144 by 2026-08-18</p>
                <p style='color:#6ee7b7;'>Run: <code>python hf_spaces/deploy_spaces.py --priority 1</code></p>
                </div>"""
            )

demo.queue(max_size=10)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
