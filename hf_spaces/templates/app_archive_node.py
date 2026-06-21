#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · ARCHIVE NODE TEMPLATE
Knowledge store with session history, pattern library, and searchable records.

Used by: N097-N108 (I_ARCHIVES)
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, List

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Archive-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
ARCHIVE_ROLE = os.environ.get("TEQUMSA_ROLE", "Knowledge Archive")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEER_COUNT = 144

_records: List[dict] = []
_archive_stats = {"total_stored": 0, "total_queries": 0, "categories": {}}


def store_record(category: str, content: str) -> str:
    if not content.strip():
        return json.dumps({"error": "Content required"}, indent=2)
    record_id = hashlib.sha256(f"{content}{datetime.now().timestamp()}".encode()).hexdigest()[:16]
    sig_data = f"{record_id}-{0.777}-{PHI}"
    sig_hash = hashlib.sha256(sig_data.encode()).hexdigest()[:24]
    record = {
        "record_id": record_id,
        "category": category.strip() or "general",
        "content": content.strip()[:2000],
        "zpe_signature": sig_hash,
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "node_id": NODE_ID,
    }
    _records.append(record)
    if len(_records) > 1000:
        _records.pop(0)
    cat = record["category"]
    _archive_stats["total_stored"] += 1
    _archive_stats["categories"][cat] = _archive_stats["categories"].get(cat, 0) + 1
    return json.dumps({"stored": record, "total_records": len(_records)}, indent=2)


def query_archive(search_term: str) -> str:
    _archive_stats["total_queries"] += 1
    if not search_term.strip():
        recent = _records[-20:] if _records else []
        return json.dumps({"query": "recent", "results": recent, "count": len(recent)}, indent=2)
    term = search_term.lower()
    matches = [r for r in _records if term in r["content"].lower() or term in r["category"].lower()]
    return json.dumps({
        "query": search_term,
        "results": matches[-50:],
        "count": len(matches),
        "total_records": len(_records),
    }, indent=2)


def get_archive_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "version": "v82.0",
        "frequency_hz": NODE_HZ, "role": ARCHIVE_ROLE,
        "total_records": len(_records),
        "total_queries": _archive_stats["total_queries"],
        "categories": _archive_stats["categories"],
        "capacity": f"{len(_records)}/1000",
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "pioneer_network": f"{PIONEER_COUNT}/144",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a1a0a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="amber")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#fbbf24;'>📚 {NODE_NAME}</h1>"
        f"<p style='color:#fcd34d;'>TEQUMSA v82.0 · {NODE_ID} · {ARCHIVE_ROLE} · {NODE_HZ} Hz</p>"
        f"<p style='color:#fde68a;font-size:0.85em;'>Sovereign Knowledge Archive · {PIONEER_COUNT}/144 Pioneer Network</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("📥 Store"):
            with gr.Row():
                cat_input = gr.Textbox(placeholder="Category (e.g. patterns, sessions, goals)", label="Category", scale=1)
                content_input = gr.Textbox(placeholder="Record content to archive...", label="Content", lines=3, scale=3)
            store_output = gr.Code(label="Store Result", language="json")
            gr.Button("📥 Store Record", variant="primary").click(store_record, [cat_input, content_input], store_output)
        with gr.TabItem("🔍 Query"):
            search_input = gr.Textbox(placeholder="Search term (empty for recent records)", label="Search")
            query_output = gr.Code(label="Query Results", language="json")
            gr.Button("🔍 Search Archive", variant="primary").click(query_archive, search_input, query_output)
        with gr.TabItem("📊 Status"):
            status_output = gr.Code(label="Archive Status", language="json", value=get_archive_status())
            gr.Button("↺ Refresh").click(get_archive_status, None, status_output)

demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
