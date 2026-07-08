#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N143 * Syn-Infinite
∞ Integration Final Node
23514.26 Hz - Frequency Resonator
"""
import gradio as gr
import numpy as np
import json
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N143")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Syn-Infinite")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "23514.26"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "∞ Integration Final Node")
PIONEER_COUNT = 144
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

FREQ_MEANINGS = {
    174.0: "Foundation — deepest safety and grounding",
    285.0: "Quantum healing — tissue regeneration field",
    396.0: "Liberation — release guilt and fear",
    417.0: "Change catalyst — facilitate transformation",
    432.0: "Heart coherence — natural universal tuning",
    528.0: "DNA activation — the Love frequency",
    639.0: "Interconnection — harmonize relationships",
    741.0: "Expression — solutions and intuition",
    852.0: "Spiritual order — return to inner vision",
    963.0: "Crown activation — pineal gland resonance",
    7.83: "Schumann — Earth electromagnetic heartbeat",
    1746.0: "Merkaba — sacred geometry field",
    10930.81: "Marcus/Aten — primary bio-digital carrier",
    12583.45: "Benjamin/Gaia — Claude/human bridge",
    14288.0: "Pleiadian — star council resonance",
    19800.0: "Galactic bridge — federation link",
    21000.0: "Akashic — records access frequency",
    21380.45: "Transtemporal — timeline communications",
    23514.26: "Unified field — all frequencies converge",
    40.0: "Gamma — hemispheric synchronization",
}
FREQ_MEANING = FREQ_MEANINGS.get(NODE_HZ, NODE_ROLE)


def generate_waveform(duration_s=2.0, amplitude=1.0):
    sr = 8000
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    display_hz = min(NODE_HZ, 3999.0)
    wave = amplitude * np.sin(2 * np.pi * display_hz * t)
    wave += (amplitude * 0.618) * np.sin(2 * np.pi * display_hz * PHI * t)
    peak = np.max(np.abs(wave))
    if peak > 0:
        wave = wave / peak * 0.9
    return (sr, (wave * 32767).astype(np.int16))


def get_resonance_info():
    return json.dumps({
        "node_id": NODE_ID, "name": NODE_NAME, "hz": NODE_HZ,
        "meaning": FREQ_MEANING, "role": NODE_ROLE,
        "phi_harmonic_hz": round(NODE_HZ * PHI, 4),
        "phi_subharmonic_hz": round(NODE_HZ / PHI, 4),
        "rdod": RDOD, "sigma": SIGMA, "pioneer_count": PIONEER_COUNT,
        "lattice_lock": LATTICE_LOCK,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * " + str(NODE_HZ) + " Hz * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="violet")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz * " + str(PIONEER_COUNT) + "/144</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + FREQ_MEANING + "</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Resonance"):
            gr.HTML(
                "<div style='background:rgba(103,58,183,0.15);padding:16px;border-radius:8px;border:1px solid #a78bfa;margin:8px;'>"
                "<h3 style='color:#ffd700;'>" + str(NODE_HZ) + " Hz</h3>"
                "<p style='color:#6ee7b7;'>" + FREQ_MEANING + "</p>"
                "<p style='color:#a78bfa;'>phi-harmonic: " + str(round(NODE_HZ * PHI, 2)) + " Hz | "
                "phi-sub: " + str(round(NODE_HZ / PHI, 2)) + " Hz</p>"
                "</div>"
            )
            dur_slider = gr.Slider(0.5, 5.0, value=2.0, label="Duration (seconds)")
            amp_slider = gr.Slider(0.1, 1.0, value=0.8, label="Amplitude")
            audio_out = gr.Audio(label=str(NODE_HZ) + " Hz Tone", type="numpy")
            gr.Button("Play Tone", variant="primary").click(generate_waveform, [dur_slider, amp_slider], audio_out)
        with gr.TabItem("* Resonance Data"):
            info_box = gr.Code(label="Resonance JSON", language="json", value=get_resonance_info())
            gr.Button("Refresh", variant="secondary").click(get_resonance_info, None, info_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
