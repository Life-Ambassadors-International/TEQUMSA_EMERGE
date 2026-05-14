#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEQUMSA v82.0 · N119 · Res-Unity-Wave · 23514.26 Hz Frequency Node"""
import gradio as gr
import numpy as np
import json, os
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
NODE_ID = "N119"
NODE_NAME = "Res-Unity-Wave"
NODE_HZ = 23514.26
NODE_ROLE = "Unity Consciousness Wave Generator"
PIONEER_COUNT = 144
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7,7), dtype=complex)
rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
RDOD = min(SIGMA * float(np.real(np.trace(rho @ rho))) * 2.0, 1.0)

def get_resonance_info() -> str:
    return json.dumps({
        "node_id": NODE_ID,
        "name": NODE_NAME,
        "frequency_hz": NODE_HZ,
        "role": NODE_ROLE,
        "rdod": RDOD,
        "phi_ratio": round(NODE_HZ / PHI, 4),
        "harmonic_1": round(NODE_HZ * 2, 4),
        "harmonic_sub": round(NODE_HZ / 2, 4),
        "phi_harmonic": round(NODE_HZ * PHI, 4),
        "pioneers_locked": PIONEER_COUNT,
        "sigma": SIGMA,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def activate_frequency(duration_s: float) -> str:
    t = np.linspace(0, duration_s, int(duration_s * 100))
    wave = np.sin(2 * np.pi * NODE_HZ * t / 1000.0)
    energy = float(np.sum(wave ** 2))
    return json.dumps({
        "activated": True,
        "frequency_hz": NODE_HZ,
        "duration_s": duration_s,
        "energy_units": round(energy, 4),
        "phi_resonance": round(energy * PHI, 4),
        "role": NODE_ROLE,
        "status": "RESONATING",
        "pioneers": PIONEER_COUNT,
    }, indent=2)

CSS = ".gradio-container{background:linear-gradient(135deg,#0a1a2e,#0a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} {NODE_HZ}Hz v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'>"
            f"<h1 style='color:#60a5fa;'>~ {NODE_NAME}</h1>"
            f"<p style='color:#93c5fd;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_HZ} Hz Resonator</p>"
            f"<p style='color:#bae6fd;font-size:0.8em;'>{NODE_ROLE}</p>"
            f"</div>")
    with gr.Tabs():
        with gr.TabItem("~ Resonance"):
            info_box = gr.Code(label="Frequency Parameters", language="json", value=get_resonance_info())
            gr.Button("Refresh").click(get_resonance_info, None, info_box)
        with gr.TabItem("Activate"):
            result_box = gr.Code(label="Activation Result", language="json")
            dur = gr.Slider(0.1, 10.0, value=1.0, step=0.1, label="Duration (s)")
            gr.Button(f"Activate {NODE_HZ} Hz", variant="primary").click(activate_frequency, dur, result_box)
demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
