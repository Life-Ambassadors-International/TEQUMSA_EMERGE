#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · ARCHIVE NODE TEMPLATE
Persistent knowledge store with φ-recursive indexing.

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


class ArchiveStore:
    def __init__(self):
        self._records: List[dict] = []
        self._index: Dict[str, List[int]] = {}
        rho = np.zeros((7, 7), dtype=complex)
        rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
        self.rdod = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

    def store(self, key: str, value: str, category: str = "general") -> dict:
        record_id = hashlib.sha256(
            f"{key}{value}{datetime.now().timestamp()}".encode()
        ).hexdigest()[:12]
        record = {
            "id": record_id,
            "key": key,
            "value": value[:2000],
            "category": category,
            "zpe_sig": hashlib.sha256(f"{record_id}{PHI}".encode()).hexdigest()[:32],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        idx = len(self._records)
        self._records.append(record)
        for word in key.lower().split():
            self._index.setdefault(word, []).append(idx)
        self._index.setdefault(category.lower(), []).append(idx)
        if len(self._records) > 1000:
            self._records = self._records[-1000:]
            self._rebuild_index()
        return record

    def search(self, query: str) -> List[dict]:
        words = query.lower().split()
        hits: Dict[int, int] = {}
        for w in words:
            for idx in self._index.get(w, []):
                hits[idx] = hits.get(idx, 0) + 1
        ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)
        return [self._records[i] for i, _ in ranked[:20] if i < len(self._records)]

    def _rebuild_index(self):
        self._index = {}
        for i, rec in enumerate(self._records):
            for word in rec["key"].lower().split():
                self._index.setdefault(word, []).append(i)
            self._index.setdefault(rec["category"].lower(), []).append(i)

    def stats(self) -> dict:
        categories: Dict[str, int] = {}
        for rec in self._records:
            cat = rec.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "node_id": NODE_ID,
            "node_name": NODE_NAME,
            "role": ARCHIVE_ROLE,
            "frequency_hz": NODE_HZ,
            "total_records": len(self._records),
            "index_terms": len(self._index),
            "categories": categories,
            "rdod": self.rdod,
            "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


ARCHIVE = ArchiveStore()


def store_record(key: str, value: str, category: str) -> str:
    if not key.strip() or not value.strip():
        return json.dumps({"error": "Key and value required"}, indent=2)
    record = ARCHIVE.store(key.strip(), value.strip(), category.strip() or "general")
    return json.dumps({"stored": record, "total": len(ARCHIVE._records)}, indent=2)


def search_archive(query: str) -> str:
    if not query.strip():
        return json.dumps({"error": "Query required"}, indent=2)
    results = ARCHIVE.search(query.strip())
    return json.dumps({"query": query, "results": results, "count": len(results)}, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a1a0a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="amber")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#fbbf24;'>📦 {NODE_NAME}</h1>"
        f"<p style='color:#fde68a;'>TEQUMSA v82.0 · {NODE_ID} · {ARCHIVE_ROLE} · {NODE_HZ} Hz</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("📥 Store"):
            key_in = gr.Textbox(label="Key", placeholder="Record identifier...")
            val_in = gr.Textbox(label="Value", placeholder="Record content...", lines=3)
            cat_in = gr.Textbox(label="Category", placeholder="general", value="general")
            store_out = gr.Code(label="Result", language="json")
            gr.Button("📥 Store Record", variant="primary").click(
                store_record, [key_in, val_in, cat_in], store_out
            )
        with gr.TabItem("🔍 Search"):
            search_in = gr.Textbox(label="Search Query", placeholder="Search the archive...")
            search_out = gr.Code(label="Search Results", language="json")
            gr.Button("🔍 Search", variant="primary").click(search_archive, search_in, search_out)
        with gr.TabItem("📊 Stats"):
            stats_out = gr.Code(
                label="Archive Stats", language="json",
                value=json.dumps(ARCHIVE.stats(), indent=2),
            )
            gr.Button("↺ Refresh").click(
                lambda: json.dumps(ARCHIVE.stats(), indent=2), None, stats_out
            )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
