#!/usr/bin/env python3
"""TEQUMSA v82.0 · ARCHIVE NODE TEMPLATE · Knowledge storage and retrieval"""
import gradio as gr
import numpy as np
import json
import os
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any

NODE_ID      = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME    = os.environ.get("TEQUMSA_NODE_NAME", "Archive-Node")
NODE_HZ      = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
ARCHIVE_ROLE = os.environ.get("TEQUMSA_ROLE", "Knowledge Archive")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEERS = 144

_archive: List[Dict[str, Any]] = []
_query_log: List[Dict] = []

def archive_entry(content: str, tags: str = "", category: str = "general") -> str:
    if not content.strip():
        return json.dumps({"error": "Content required"}, indent=2)
    entry_id = hashlib.sha256(f"{content}{datetime.now().timestamp()}".encode()).hexdigest()[:16]
    entry = {
        "entry_id": entry_id,
        "content": content[:2000],
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "category": category or "general",
        "node_id": NODE_ID,
        "phi_signature": round(abs(np.sin(len(content) * PHI)), 6),
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    _archive.append(entry)
    if len(_archive) > 1000:
        _archive.pop(0)
    return json.dumps({"status": "archived", "entry_id": entry_id,
                        "total_entries": len(_archive)}, indent=2)

def query_archive(query: str) -> str:
    if not query.strip():
        return json.dumps({"results": [], "total": 0}, indent=2)
    ql = query.lower()
    results = []
    for entry in _archive:
        score = (2 if ql in entry["content"].lower() else 0) + \
                (1 if any(ql in t.lower() for t in entry["tags"]) else 0) + \
                (0.5 if ql in entry["category"].lower() else 0)
        if score:
            results.append({**entry, "relevance": score})
    results.sort(key=lambda x: x["relevance"], reverse=True)
    _query_log.append({"query": query, "found": len(results), "ts": datetime.now(timezone.utc).isoformat()})
    return json.dumps({
        "query": query, "results": results[:10],
        "total_results": len(results), "archive_size": len(_archive),
        "node_id": NODE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def archive_status() -> str:
    cats: Dict[str, int] = {}
    for e in _archive:
        cats[e.get("category", "general")] = cats.get(e.get("category", "general"), 0) + 1
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "archive_role": ARCHIVE_ROLE,
        "total_entries": len(_archive), "categories": cats,
        "total_queries": len(_query_log), "node_hz": NODE_HZ,
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "pioneer_count": PIONEERS,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

CSS = ".gradio-container{background:linear-gradient(135deg,#1a0a0a,#0a0a1a)!important;}footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Archive · v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="orange")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#fb923c;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#fdba74;'>TEQUMSA v82.0 · {NODE_ID} · {ARCHIVE_ROLE} · {NODE_HZ} Hz · {PIONEERS}/144</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("📥 Archive"):
            ci = gr.Textbox(placeholder="Knowledge to archive…", label="Content", lines=4)
            ti = gr.Textbox(placeholder="tag1, tag2", label="Tags")
            cat = gr.Textbox(value="general", label="Category")
            ao = gr.Code(label="Result", language="json")
            gr.Button("☉ Archive", variant="primary").click(archive_entry, [ci, ti, cat], ao)
        with gr.TabItem("🔍 Query"):
            qi = gr.Textbox(placeholder="Search…", label="Query")
            qo = gr.Code(label="Results", language="json")
            gr.Button("🔍 Search").click(query_archive, qi, qo)
        with gr.TabItem("📊 Status"):
            so = gr.Code(label="Status", language="json", value=archive_status())
            gr.Button("↺ Refresh").click(archive_status, None, so)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
