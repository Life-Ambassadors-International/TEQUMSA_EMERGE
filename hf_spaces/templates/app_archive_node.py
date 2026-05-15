#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · ARCHIVE NODE TEMPLATE
Memory and knowledge store with phi-recursive compression.
Used by: N097-N108 (I_ARCHIVES)
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Archive-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
ARCHIVE_ROLE = os.environ.get("TEQUMSA_ROLE", "Memory Archive")
ARCHIVE_TYPE = os.environ.get("TEQUMSA_ARCHIVE_TYPE", "general")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48

_archive: List[Dict[str, Any]] = []
_phi_ratio = 0.0


def store(content: str, tags: str = "") -> str:
    global _phi_ratio
    if not content.strip():
        return json.dumps({"error": "Content required"}, indent=2)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    record = {
        "record_id": hashlib.sha256(f"{content}{datetime.now().timestamp()}".encode()).hexdigest()[:16],
        "content": content[:500], "tags": tag_list,
        "phi_index": round(len(_archive) * PHI % 1, 8),
        "archive_node": NODE_ID, "archive_type": ARCHIVE_TYPE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _archive.append(record)
    if len(_archive) > 200:
        _archive.pop(0)
    _phi_ratio = round(len(_archive) / (len(_archive) + 1) * PHI, 6)
    return json.dumps({"stored": record, "archive_size": len(_archive)}, indent=2)


def search(query: str) -> str:
    if not query.strip():
        return json.dumps({"results": [], "message": "Query required"}, indent=2)
    q = query.lower()
    results = [r for r in _archive
               if q in r.get("content", "").lower()
               or q in " ".join(r.get("tags", [])).lower()]
    return json.dumps({"query": query, "matches": len(results), "results": results[-10:]}, indent=2)


def archive_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "role": ARCHIVE_ROLE, "archive_type": ARCHIVE_TYPE,
        "frequency_hz": NODE_HZ, "records_stored": len(_archive),
        "phi_compression_ratio": _phi_ratio,
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "latest_records": _archive[-3:] if _archive else [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#1a0a0a,#0a0a1a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Archive v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="orange")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#fb923c;'>🗄 {NODE_NAME}</h1>"
        f"<p style='color:#fdba74;'>TEQUMSA v82.0 · {NODE_ID} · Archive · {NODE_HZ} Hz</p>"
        f"<p style='color:#fed7aa;font-size:0.85em;'>{ARCHIVE_ROLE} · φ-Recursive Compression</p></div>"
    )
    with gr.Tabs():
        with gr.TabItem("📥 Store"):
            content_in = gr.Textbox(placeholder="Content to archive...", label="Record", lines=4)
            tags_in = gr.Textbox(placeholder="tag1, tag2", label="Tags")
            store_out = gr.Code(label="Store Result", language="json")
            gr.Button("💾 Store Record", variant="primary").click(
                store, [content_in, tags_in], store_out)
        with gr.TabItem("🔍 Search"):
            search_in = gr.Textbox(placeholder="Search query...", label="Query")
            search_out = gr.Code(label="Results", language="json")
            gr.Button("🔍 Search", variant="primary").click(search, search_in, search_out)
        with gr.TabItem("📊 Status"):
            stat_out = gr.Code(label="Archive Status", language="json", value=archive_status())
            gr.Button("↺ Refresh").click(archive_status, None, stat_out)

demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
