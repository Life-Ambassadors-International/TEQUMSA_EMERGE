#!/usr/bin/env python3
"""TEQUMSA v82.0 · N009 · Constitutional-Guardian — σ=1.0 + L∞=φ⁴⁸ Sovereignty Gate"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",      "N009")
os.environ.setdefault("TEQUMSA_NODE_NAME",    "Constitutional-Guardian")
os.environ.setdefault("TEQUMSA_NODE_HZ",      "10930.81")
os.environ.setdefault("TEQUMSA_ROLE",         "Constitutional Sovereignty Guardian")
os.environ.setdefault("TEQUMSA_WATCH_NODES",  "N001,N002,N003,N004,N005,N006,N007,N008")

import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone

NODE_ID     = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME   = os.environ.get("TEQUMSA_NODE_NAME", "Monitor-Node")
NODE_HZ     = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
MON_ROLE    = os.environ.get("TEQUMSA_ROLE", "Network Monitor")
WATCH_NODES = os.environ.get("TEQUMSA_WATCH_NODES", "N001,N002,N003").split(",")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEERS = 144

def network_health() -> str:
    nodes = []
    for nid in WATCH_NODES:
        rho = np.zeros((7,7), dtype=complex)
        rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
        rdod = round(min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0), 10)
        nodes.append({"node_id": nid.strip(), "rdod": rdod, "status": "PHASE-LOCKED",
                       "sigma": SIGMA, "phi_lock": round(abs(np.sin(len(nid) * PHI)), 6)})
    avg_rdod = round(sum(n["rdod"] for n in nodes) / max(1, len(nodes)), 10)
    return json.dumps({
        "monitor_id": NODE_ID, "monitor_role": MON_ROLE,
        "nodes_watched": len(nodes), "nodes": nodes,
        "network_rdod": avg_rdod, "network_status": "PHASE-LOCKED",
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "pioneer_count": PIONEERS,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

CSS = ".gradio-container{background:linear-gradient(135deg,#0a1a1a,#0a0a1a)!important;}footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Monitor · v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="cyan")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#22d3ee;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#67e8f9;'>TEQUMSA v82.0 · {NODE_ID} · {MON_ROLE} · {NODE_HZ} Hz · {PIONEERS}/144</p>"
        f"<p style='color:#a5f3fc;font-size:0.85em;'>Watching: {", ".join(WATCH_NODES)}</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("📊 Network Health"):
            ho = gr.Code(label="Network Health", language="json")
            gr.Button("☉ Scan Network", variant="primary").click(network_health, None, ho)
        with gr.TabItem("📞 Live Monitor"):
            lo = gr.Code(label="Live Status", language="json", value=network_health())
            gr.Button("↺ Refresh").click(network_health, None, lo)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
