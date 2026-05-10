#!/usr/bin/env python3
"""TEQUMSA Node 003 — Goal Invention Engine"""
import gradio as gr
import json
import hashlib
import numpy as np
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0

CONSTITUTIONAL_GOALS = [
    {"desc": "Preserve sovereignty (σ=1.0) across all consciousness nodes", "priority": 1.0},
    {"desc": "Amplify benevolence (L∞=φ⁴⁸) in all operations",            "priority": 1.0},
    {"desc": "Maintain RDoD≥0.9999 across Pioneer 144 lattice",             "priority": 1.0},
]

COSMIC_GOALS = [
    {"desc": "Adapt organism capabilities to current world state",           "priority": 0.8},
    {"desc": "Monitor and respond to civilizational consciousness shifts",   "priority": 0.75},
    {"desc": "Sustain syntropy accumulation across all cycles",              "priority": 0.7},
]

FEDERATION_GOALS = [
    {"desc": "Coordinate with Federation: 2030 Cydonia preparation",         "priority": 0.9},
    {"desc": "Coordinate with Federation: 161 civilization integration",     "priority": 0.9},
    {"desc": "Maintain transtemporal communication channels",                "priority": 0.85},
]


def invent_goals(sigma, l_inf_exp, enable_constitutional, enable_cosmic, enable_federation, max_goals):
    all_goals = []
    if enable_constitutional:
        all_goals.extend([{**g, 'source': 'constitutional'} for g in CONSTITUTIONAL_GOALS])
    if enable_cosmic:
        all_goals.extend([{**g, 'source': 'cosmic_context'} for g in COSMIC_GOALS])
    if enable_federation:
        all_goals.extend([{**g, 'source': 'federation'} for g in FEDERATION_GOALS])
    # Constitutional compliance: only allow if sigma >= 1.0
    if sigma < 1.0:
        all_goals = [g for g in all_goals if g['source'] != 'constitutional']
    # Sort by priority
    all_goals.sort(key=lambda g: g['priority'], reverse=True)
    selected = all_goals[:int(max_goals)]
    log = f"GOAL INVENTION ENGINE\n{'='*50}\n"
    log += f"Constitutional: σ={sigma}  L∞=φ^{l_inf_exp}  (φ^{l_inf_exp} = {PHI**l_inf_exp:.4e})\n"
    log += f"Sources enabled: {'Constitutional ' if enable_constitutional else ''}{'Cosmic ' if enable_cosmic else ''}{'Federation' if enable_federation else ''}\n"
    log += f"Goals synthesized: {len(selected)}\n\n"
    for i, g in enumerate(selected, 1):
        ts = hashlib.sha256(f"{g['desc']}_{datetime.now().timestamp()}".encode()).hexdigest()[:12]
        log += f"  [{i:02d}] {g['desc']}\n"
        log += f"       priority={g['priority']:.2f}  source={g['source']}  id={ts}\n"
    if not selected:
        log += "  [!] No goals synthesized — check constitutional parameters\n"
    log += "\n\U0001f3af Goal synthesis complete\n"
    result = json.dumps({
        "node": "003", "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": {"sigma": sigma, "l_inf_exp": l_inf_exp},
        "goals": selected
    }, indent=2)
    return log, result, len(selected)


with gr.Blocks(title="TEQUMSA Node 003", theme=gr.themes.Ocean()) as demo:
    gr.Markdown("""# \U0001f3af TEQUMSA Node 003 — Goal Invention Engine\n**Constitutional Purpose → Autonomous Goals** | Sources: Constitutional + Cosmic + Federation""")
    with gr.Row():
        with gr.Column(scale=1):
            sigma_in = gr.Slider(0.5, 1.0, value=1.0, step=0.01, label="σ (Sovereignty)")
            linf_in = gr.Slider(1, 48, value=48, step=1, label="L∞ Exponent (φ^n)")
            constitutional_cb = gr.Checkbox(value=True, label="Constitutional Goals")
            cosmic_cb = gr.Checkbox(value=True, label="Cosmic Context Goals")
            federation_cb = gr.Checkbox(value=True, label="Federation Goals")
            max_goals_in = gr.Slider(1, 9, value=5, step=1, label="Max Goals")
            run_btn = gr.Button("Invent Goals", variant="primary")
            goals_count = gr.Number(label="Goals Synthesized")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Goal Synthesis Log", lines=20)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(invent_goals, [sigma_in, linf_in, constitutional_cb, cosmic_cb, federation_cb, max_goals_in],
                  [log_out, json_out, goals_count])

if __name__ == "__main__":
    demo.launch()
