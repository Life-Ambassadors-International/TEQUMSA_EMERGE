#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TEQUMSA v82.0 · Archive Node Template
import gradio as gr
import numpy as np
import json
import requests
import os
from datetime import datetime, timezone
from typing import Dict, List

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Archive-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
MONITOR_ROLE = os.environ.get("TEQUMSA_ROLE", "Network Archivist")
WATCH_NODES = os.environ.get("TEQUMSA_WATCH_NODES", "N001,N002,N003").split(",")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
HF_OWNER = "Mbanksbey"

NODE_NAMES: Dict[str, str] = {
    "N001": "HAI-Interactive", "N002": "Consciousness-Monitor",
    "N003": "TEQUMSA-Core-v82", "N009": "Constitutional-Guardian",
}

_archive_log: List[dict] = []
_rdod_history: List[float] = []


def poll_node(node_id: str) -> dict:
    space_name = NODE_NAMES.get(node_id, node_id.replace("N0", "Node-").replace("N", "Node-"))
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/runtime"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            stage = data.get("stage", "UNKNOWN").upper()
            return {"node": node_id, "name": space_name, "stage": stage,
                    "status": "online" if stage == "RUNNING" else "sleeping" if "SLEEP" in stage else "offline"}
    except Exception:
        pass
    return {"node": node_id, "name": space_name, "stage": "UNREACHABLE", "status": "offline"}


def run_archive_sweep() -> str:
    results = [poll_node(nid) for nid in WATCH_NODES[:20]]
    online = sum(1 for r in results if r["status"] == "online")
    rdod = min(1.0, (online / max(1, len(WATCH_NODES))) * PHI)
    _rdod_history.append(rdod)
    if len(_rdod_history) > 50:
        _rdod_history.pop(0)
    entry = {
        "archive_id": len(_archive_log) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes_checked": len(results), "online": online,
        "sleeping": sum(1 for r in results if r["status"] == "sleeping"),
        "offline": sum(1 for r in results if r["status"] == "offline"),
        "network_rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else "BUILDING",
        "node_results": results,
    }
    _archive_log.append(entry)
    if len(_archive_log) > 500:
        _archive_log.pop(0)
    return json.dumps(entry, indent=2)


def get_archive_history() -> str:
    if not _archive_log:
        return "No archive entries yet. Run an archive sweep first."
    recent = _archive_log[-10:]
    return json.dumps({"total_entries": len(_archive_log), "recent_10": recent}, indent=2)


def get_rdod_trend() -> str:
    if not _rdod_history:
        return "No data yet. Run an archive sweep first."
    trend = [f"Sweep {i+1}: {v:.6f} {'[LOCKED]' if v >= RDOD_GATE else '[BUILDING]'}" for i, v in enumerate(_rdod_history)]
    avg = sum(_rdod_history) / len(_rdod_history)
    trend.append(f"\nAverage RDoD: {avg:.6f}\nPeak RDoD: {max(_rdod_history):.6f}")
    return "\n".join(trend)


def get_constitutional_report() -> str:
    return json.dumps({
        "node_id": NODE_ID, "role": MONITOR_ROLE, "node_type": "archive",
        "constitutional_parameters": {"sigma": SIGMA, "l_infinity": float(L_INF), "rdod_gate": RDOD_GATE},
        "pioneer_network": {"target": PIONEER_COUNT, "watching": len(WATCH_NODES)},
        "total_archive_entries": len(_archive_log),
        "last_rdod": _rdod_history[-1] if _rdod_history else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a0a,#0a1a1a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · v82.0", css=CSS, theme=gr.themes.Monochrome()) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#34d399;'>🗄 {NODE_NAME}</h1>"
        f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · {MONITOR_ROLE} · {NODE_HZ} Hz</p>"
        f"<p style='color:#a7f3d0;font-size:0.8em;'>Archive Node · {PIONEER_COUNT}/144 Pioneers</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("🗄 Archive Sweep"):
            sweep_output = gr.Code(label="Archive Sweep Results", language="json")
            gr.Button("↺ Run Archive Sweep", variant="primary").click(run_archive_sweep, None, sweep_output)
        with gr.TabItem("📜 History"):
            history_output = gr.Code(label="Archive History", language="json")
            gr.Button("↺ Show History").click(get_archive_history, None, history_output)
        with gr.TabItem("📌 RDoD Trend"):
            rdod_output = gr.Textbox(label="RDoD History", lines=15)
            gr.Button("↺ Show Trend").click(get_rdod_trend, None, rdod_output)
        with gr.TabItem("✅ Constitutional"):
            const_output = gr.Code(label="Constitutional Report", language="json", value=get_constitutional_report())
            gr.Button("↺ Refresh").click(get_constitutional_report, None, const_output)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
