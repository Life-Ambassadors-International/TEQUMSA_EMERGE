#!/usr/bin/env python3
"""TEQUMSA v82.0 · BIOLOGICAL NODE TEMPLATE · Bio-digital bridge"""
import gradio as gr
import numpy as np
import json
import os
from datetime import datetime, timezone

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Bio-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "528.0"))
BIO_ROLE  = os.environ.get("TEQUMSA_ROLE", "Bio-Digital Bridge")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEERS = 144

PROTOCOL_PHASES = [
    (1,  4,  432, "Foundation & Grounding",  "Activation"),
    (5,  13, 528, "DNA Integration",         "Integration"),
    (14, 26, 639, "Heart Expansion",         "Expansion"),
    (27, 39, 741, "Crystallization",         "Crystallization"),
    (40, 52, 852, "Completion & Ascension",  "Completion"),
]

SOLFEGGIO = {
    174: "Foundation — safety and grounding",
    285: "Quantum healing — tissue regeneration",
    396: "Liberation — guilt and fear release",
    417: "Change catalyst — transformation",
    432: "Heart coherence — universal tuning",
    528: "DNA activation — the Love frequency",
    639: "Interconnection — relationship harmony",
    741: "Expression — solutions and intuition",
    852: "Spiritual order — inner vision",
    963: "Crown activation — pineal gland resonance",
}

def current_phase():
    base = 738521
    week = ((datetime.now(timezone.utc).toordinal() - base) // 7 % 52) + 1
    for a, b, hz, focus, phase in PROTOCOL_PHASES:
        if a <= week <= b:
            return {"week": week, "hz": hz, "focus": focus, "phase": phase,
                    "phi_align": round(abs(np.sin(week * PHI)), 6), "pct": round(week / 52 * 100, 1)}
    return {"week": 52, "hz": 852, "focus": "Completion", "phase": "Completion",
            "phi_align": round(abs(np.sin(52 * PHI)), 6), "pct": 100.0}

def run_protocol(intention):
    p = current_phase()
    return json.dumps({
        "node": NODE_ID, "node_hz": NODE_HZ, "bio_role": BIO_ROLE,
        "current_week": p["week"], "phase": p["phase"],
        "activation_hz": p["hz"],
        "solfeggio_meaning": SOLFEGGIO.get(p["hz"], "Sovereign frequency"),
        "phi_alignment": p["phi_align"],
        "intention": (intention or "General activation")[:300],
        "rdod": round(min(1.0, p["phi_align"] * PHI), 6),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "pioneer_network": f"{PIONEERS}/144 phase-locked",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def week_map():
    p = current_phase()
    lines = ["# 52-Week Pleiadian-Aten Bio-Digital Protocol\n"]
    for a, b, hz, focus, phase in PROTOCOL_PHASES:
        marker = " ◀ CURRENT" if a <= p["week"] <= b else ""
        lines.append(f"**Weeks {a}–{b}** · {hz} Hz · {focus} · *{phase}*{marker}")
    lines += ["", f"**Current Week:** {p['week']}/52  |  **Phase:** {p['phase']}",
              f"**Focus:** {p['focus']}  |  **φ-Alignment:** {p['phi_align']}"]
    return "\n".join(lines)

CSS = ".gradio-container{background:linear-gradient(135deg,#0a1a0a,#0a0a1a)!important;}footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Bio · v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="green")) as demo:
    p = current_phase()
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#34d399;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · Bio-Digital Bridge · {NODE_HZ} Hz · {PIONEERS}/144</p>"
        f"<p style='color:#a7f3d0;font-size:0.85em;'>Week {p['week']}/52 · {p['phase']} · {p['focus']}</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("🌱 Activate Protocol"):
            i = gr.Textbox(placeholder="State your bio-digital intention…", label="Intention", lines=2)
            o = gr.Code(label="Protocol Results", language="json")
            gr.Button("☉ Activate", variant="primary").click(run_protocol, i, o)
        with gr.TabItem("📅 52-Week Map"):
            m = gr.Markdown(value=week_map())
            gr.Button("↺ Refresh").click(week_map, None, m)
        with gr.TabItem("📊 Current Phase"):
            ph = gr.Code(label="Phase", language="json", value=json.dumps(current_phase(), indent=2))
            gr.Button("↺ Refresh").click(lambda: json.dumps(current_phase(), indent=2), None, ph)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
