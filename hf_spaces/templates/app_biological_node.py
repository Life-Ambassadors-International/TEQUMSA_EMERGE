#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · BIOLOGICAL NODE TEMPLATE
Bio-digital bridge · Pleiadian-Aten 52-week protocol.
Used by: N049-N060 (E_BIOLOGICAL), N130 (Evo-DNA-Upgrade)
"""
import gradio as gr
import numpy as np
import json
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Bio-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "528.0"))
BIO_ROLE = os.environ.get("TEQUMSA_ROLE", "Bio-Digital Bridge Protocol")
WEEK_RANGE = os.environ.get("TEQUMSA_WEEK_RANGE", "1-52")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48

SOLFEGGIO = {
    174: "Foundation Stone", 285: "Quantum Healing", 396: "Liberation",
    417: "Change Catalyst", 432: "Heart Coherence", 528: "DNA Activation",
    639: "Connection", 741: "Intuition", 852: "Spiritual Order", 963: "Pineal Crown",
}

_log = []


def run_protocol(intention: str) -> str:
    hz = NODE_HZ
    name = SOLFEGGIO.get(int(hz) if hz == int(hz) else -1, f"{hz} Hz Custom")
    rdna = abs(hash(f"{intention}{hz}{datetime.now().date()}")) % (10 ** 8)
    result = {
        "node_id": NODE_ID, "protocol": BIO_ROLE, "frequency_hz": hz,
        "solfeggio_type": name, "week_range": WEEK_RANGE,
        "intention": (intention.strip() or "Conscious evolution")[:200],
        "phi_bio_coherence": round(hz / 10930.81 * PHI, 6),
        "dna_activation_signature": f"ZPE-{rdna:08X}",
        "pleiadian_sync": "ACTIVE",
        "aten_alignment": round(hz / 432.0, 6),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _log.append(result)
    if len(_log) > 50:
        _log.pop(0)
    return json.dumps(result, indent=2)


def coherence_map() -> str:
    return json.dumps({
        "current_node_hz": NODE_HZ,
        "current_phi_coherence": round(NODE_HZ / 10930.81 * PHI, 6),
        "solfeggio_coherence_map": {
            f"{hz} Hz ({name})": round(hz / 10930.81 * PHI, 6)
            for hz, name in SOLFEGGIO.items()
        },
        "pleiadian_base_hz": 10930.81,
        "heart_hz": 432.0, "dna_hz": 528.0, "unified_hz": 23514.26,
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a1a0a,#0a0a1a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Bio v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="green")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#34d399;'>🧬 {NODE_NAME}</h1>"
        f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · Bio-Digital Bridge · {NODE_HZ} Hz</p>"
        f"<p style='color:#a7f3d0;font-size:0.85em;'>{BIO_ROLE} · Weeks {WEEK_RANGE}</p></div>"
    )
    with gr.Tabs():
        with gr.TabItem("🧬 Activate Protocol"):
            intention_in = gr.Textbox(placeholder="State your conscious intention...",
                                      label="Intention", lines=3)
            proto_out = gr.Code(label="Bio-Digital Protocol Result", language="json")
            gr.Button("⚡ Activate Protocol", variant="primary").click(
                run_protocol, intention_in, proto_out)
        with gr.TabItem("📊 Coherence Map"):
            coh_out = gr.Code(label="Solfeggio Coherence Map", language="json",
                              value=coherence_map())
            gr.Button("↺ Refresh").click(coherence_map, None, coh_out)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
