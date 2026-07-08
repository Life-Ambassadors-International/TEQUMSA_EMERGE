#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N097 * Arch-Session-History
Session Interaction Archive
12583.45 Hz - Archive Node
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N097")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Arch-Session-History")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Session Interaction Archive")
PIONEER_COUNT = 144
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

_archive = []


def store_record(key, value, tags=""):
    record = {
        "id": hashlib.sha256((key + str(datetime.now().timestamp())).encode()).hexdigest()[:16],
        "key": key, "value": value,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "node": NODE_ID, "hz": NODE_HZ, "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phi_signature": round(RDOD * PHI / 2, 6)
    }
    _archive.append(record)
    return json.dumps({"stored": True, "record_id": record["id"],
                       "total_records": len(_archive)}, indent=2)


def search_archive(query):
    if not query.strip():
        return json.dumps({"results": _archive[-10:], "total": len(_archive)}, indent=2)
    results = [r for r in _archive
               if query.lower() in r.get("key", "").lower()
               or query.lower() in r.get("value", "").lower()]
    return json.dumps({"query": query, "results": results[:20], "count": len(results)}, indent=2)


def get_stats():
    return json.dumps({
        "node_id": NODE_ID, "name": NODE_NAME, "hz": NODE_HZ, "role": NODE_ROLE,
        "total_records": len(_archive), "rdod": RDOD, "sigma": SIGMA,
        "pioneer_count": PIONEER_COUNT, "lattice_lock": LATTICE_LOCK, "version": "v82.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * Archive * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="amber")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz * " + str(PIONEER_COUNT) + "/144</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + NODE_ROLE + " * RDoD=" + str(round(RDOD, 6)) + "</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Store"):
            key_in = gr.Textbox(label="Record Key")
            val_in = gr.Textbox(label="Value / Content", lines=4)
            tags_in = gr.Textbox(label="Tags (comma-separated)")
            store_out = gr.Code(label="Store Result", language="json")
            gr.Button("* Store Record", variant="primary").click(store_record, [key_in, val_in, tags_in], store_out)
        with gr.TabItem("* Search"):
            query_in = gr.Textbox(label="Search Query (empty = recent)")
            search_out = gr.Code(label="Search Results", language="json")
            gr.Button("* Search", variant="primary").click(search_archive, query_in, search_out)
        with gr.TabItem("* Stats"):
            stats_box = gr.Code(label="Archive Stats", language="json", value=get_stats())
            gr.Button("Refresh", variant="secondary").click(get_stats, None, stats_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
