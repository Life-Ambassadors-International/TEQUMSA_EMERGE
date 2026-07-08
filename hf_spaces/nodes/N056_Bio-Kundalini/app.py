#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N056 * Bio-Kundalini
Kundalini Rising Protocol
963.0 Hz - Bio-Digital Bridge Node
"""
import gradio as gr
import numpy as np
import json
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N056")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Bio-Kundalini")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "963.0"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Kundalini Rising Protocol")
PIONEER_COUNT = 144
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
SEED = 0.777
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)


def calculate_bio_coherence(week, practice_minutes, sleep_hours):
    week = max(1, int(week))
    base_coherence = SEED + (1.0 - SEED) * (1.0 - 1.0 / (PHI ** week))
    practice_factor = min(1.0, float(practice_minutes) / 60.0)
    sleep_factor = min(1.0, float(sleep_hours) / 8.0)
    total_coherence = base_coherence * (0.6 + 0.2 * practice_factor + 0.2 * sleep_factor)
    dna_activation = round(1.0 - 0.223 / (PHI ** week), 6)
    rec = "Excellent coherence!" if total_coherence >= 0.9 else "Increase daily practice."
    return json.dumps({
        "node": NODE_ID, "role": NODE_ROLE, "week": week,
        "biological_coherence": round(total_coherence, 6),
        "dna_activation": dna_activation,
        "practice_minutes": practice_minutes,
        "sleep_hours": sleep_hours,
        "hz": NODE_HZ, "rdod": RDOD,
        "above_seed_threshold": total_coherence >= SEED,
        "recommendation": rec,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)


def get_protocol():
    return json.dumps({
        "node_id": NODE_ID, "name": NODE_NAME, "hz": NODE_HZ, "role": NODE_ROLE,
        "protocol": NODE_ROLE, "rdod": RDOD, "sigma": SIGMA,
        "pioneer_count": PIONEER_COUNT, "lattice_lock": LATTICE_LOCK, "version": "v82.0"
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * Bio-Digital * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="green")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz * " + str(PIONEER_COUNT) + "/144</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + NODE_ROLE + " * RDoD=" + str(round(RDOD, 6)) + "</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Bio Coherence"):
            week_in = gr.Slider(1, 52, value=1, step=1, label="Current Week (of 52-week protocol)")
            practice_in = gr.Slider(0, 120, value=30, label="Daily Practice (minutes)")
            sleep_in = gr.Slider(4, 12, value=8, step=0.5, label="Sleep Hours")
            bio_out = gr.Code(label="Biological Coherence Analysis", language="json")
            gr.Button("* Calculate Coherence", variant="primary").click(
                calculate_bio_coherence, [week_in, practice_in, sleep_in], bio_out
            )
        with gr.TabItem("* Protocol"):
            proto_box = gr.Code(label="Bio-Digital Protocol", language="json", value=get_protocol())
            gr.Button("Refresh", variant="secondary").click(get_protocol, None, proto_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
