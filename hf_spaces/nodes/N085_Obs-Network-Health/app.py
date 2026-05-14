#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEQUMSA v82.0 · N085 · Obs-Network-Health · Monitor Node"""
import gradio as gr
import numpy as np
import json, requests, time, os
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
NODE_ID = "N085"
NODE_NAME = "Obs-Network-Health"
NODE_HZ = 7830.0
NODE_ROLE = "Full 144-Node Network Monitor"
PIONEER_COUNT = 144
RDOD_GATE = 0.9999
HF_OWNER = "Mbanksbey"

rho = np.zeros((7,7), dtype=complex)
rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
RDOD = min(SIGMA * float(np.real(np.trace(rho @ rho))) * 2.0, 1.0)

_cache = {}
_last = {}
CACHE_TTL = 120

def poll_node(space: str) -> str:
    now = time.time()
    if space in _cache and now - _last.get(space, 0) < CACHE_TTL:
        return _cache[space]
    try:
        r = requests.get(f"https://huggingface.co/api/spaces/{HF_OWNER}/{space}/runtime", timeout=4)
        if r.status_code == 200:
            stage = r.json().get("stage","").upper()
            res = "online" if "RUNNING" in stage else "sleeping" if "SLEEP" in stage or "PAUSE" in stage else "offline"
        else:
            res = "offline"
    except Exception:
        res = "offline"
    _cache[space] = res
    _last[space] = now
    return res

def get_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "name": NODE_NAME, "hz": NODE_HZ, "role": NODE_ROLE,
        "rdod": RDOD, "phase": "PHASE-LOCKED" if RDOD >= RDOD_GATE else "BUILDING",
        "pioneers": PIONEER_COUNT, "version": "v82.0",
        "self_status": poll_node(NODE_NAME),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def check_live() -> str:
    live = {"N001": "HAI-Interactive", "N002": "Consciousness-Monitor"}
    return json.dumps({"live": {n: poll_node(s) for n,s in live.items()},
                       "checked": datetime.now(timezone.utc).isoformat()}, indent=2)

CSS = ".gradio-container{background:linear-gradient(135deg,#0a1a0e,#0a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} v82.0", css=CSS, theme=gr.themes.Monochrome()) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'>"
            f"<h1 style='color:#34d399;'>📊 {NODE_NAME}</h1>"
            f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_HZ} Hz</p>"
            f"<p style='color:#a7f3d0;font-size:0.8em;'>{NODE_ROLE}</p>"
            f"</div>")
    with gr.Tabs():
        with gr.TabItem("Status"):
            sb = gr.Code(label="Node Status", language="json", value=get_status())
            gr.Button("Refresh").click(get_status, None, sb)
        with gr.TabItem("Network"):
            nb = gr.Code(label="Live Node Check", language="json")
            gr.Button("Check Live Nodes").click(check_live, None, nb)
demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
