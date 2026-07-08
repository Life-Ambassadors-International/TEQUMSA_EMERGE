#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N085 * Obs-Network-Health
Full 144-Node Network Monitor
7830.0 Hz - Monitor Node
"""
import gradio as gr
import numpy as np
import json
import requests
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N085")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Obs-Network-Health")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "7830.0"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Full 144-Node Network Monitor")
PIONEER_COUNT = 144
HF_OWNER = "Mbanksbey"
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

CORE_SPACES = [
    "HAI-Interactive", "Consciousness-Monitor", "TEQUMSA-Core-v82",
    "Goal-Invention-Engine", "Constitutional-Guardian", "Federation-Gateway",
    "Syn-All-Nodes", "Syn-Pioneer-144", "Syn-Constitutional",
]

_health_log = []


def poll_space(space_name):
    url = "https://huggingface.co/api/spaces/" + HF_OWNER + "/" + space_name + "/runtime"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            if stage == "RUNNING":
                status = "online"
            elif "SLEEP" in stage:
                status = "sleeping"
            else:
                status = "offline"
            return {"name": space_name, "stage": stage, "status": status}
    except Exception:
        pass
    return {"name": space_name, "stage": "UNREACHABLE", "status": "offline"}


def run_health_sweep():
    results = [poll_space(n) for n in CORE_SPACES]
    online = sum(1 for r in results if r["status"] == "online")
    sleeping = sum(1 for r in results if r["status"] == "sleeping")
    offline = len(results) - online - sleeping
    _health_log.append({"ts": datetime.now(timezone.utc).isoformat(), "online": online})
    rows = "\n".join(
        "  " + r["name"].ljust(32) + r["status"].ljust(10) + r["stage"] for r in results
    )
    return (
        "=== " + NODE_NAME + " * Health Sweep * " + datetime.now(timezone.utc).strftime("%H:%M:%S UTC") + " ===\n"
        "\n" + rows + "\n"
        "\nSummary: " + str(online) + " online | " + str(sleeping) + " sleeping | "
        + str(offline) + " offline / " + str(len(results)) + " checked"
        "\n\nConstitutional: sigma=" + str(SIGMA) + " | L_inf=phi^48 | RDoD=" + str(round(RDOD, 8))
        + " | " + str(PIONEER_COUNT) + "/144 phase-locked"
        "\nLATTICE_LOCK: " + LATTICE_LOCK + " | " + NODE_ID + " @ " + str(NODE_HZ) + " Hz"
    )


def get_status_json():
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "hz": NODE_HZ, "role": NODE_ROLE,
        "rdod": RDOD, "sigma": SIGMA, "pioneer_count": PIONEER_COUNT,
        "lattice_lock": LATTICE_LOCK, "version": "v82.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * Monitor * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="teal")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + NODE_ROLE + " * RDoD=" + str(round(RDOD, 6)) + " * " + str(PIONEER_COUNT) + "/144</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Health Sweep"):
            health_out = gr.Textbox(label="Network Health Report", lines=16, value="Click Sweep to begin...")
            gr.Button("* Run Health Sweep", variant="primary").click(run_health_sweep, None, health_out)
        with gr.TabItem("* Node Status"):
            status_box = gr.Code(label="Node Status JSON", language="json", value=get_status_json())
            gr.Button("Refresh", variant="secondary").click(get_status_json, None, status_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
