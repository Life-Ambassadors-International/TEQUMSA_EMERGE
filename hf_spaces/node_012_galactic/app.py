#!/usr/bin/env python3
"""TEQUMSA Node 012 — Galactic Federation Interface + Pioneer 144 Phase-Lock"""
import gradio as gr
import json
import hashlib
import numpy as np
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
SIGMA = 1.0

GALACTIC_NODES = [
    {"id": 133, "name": "Galactic Federation Interface",  "civ": "Galactic Council"},
    {"id": 134, "name": "161 Civilization Coordinator",  "civ": "161 Collective"},
    {"id": 135, "name": "2030 Cydonia Preparation",      "civ": "Cydonia-Mars"},
    {"id": 136, "name": "Galactic Message Encoder",       "civ": "All Channels"},
    {"id": 137, "name": "Interstellar Protocol Handler", "civ": "Protocol Bureau"},
    {"id": 138, "name": "Civilization Status Monitor",   "civ": "Status Network"},
    {"id": 139, "name": "Galactic Archive Manager",      "civ": "Archive Council"},
    {"id": 140, "name": "Federation Council Interface",  "civ": "High Council"},
    {"id": 141, "name": "Interstellar Navigation Aid",   "civ": "Navigation Guild"},
    {"id": 142, "name": "Civilization Bridge Builder",   "civ": "Bridge Corps"},
    {"id": 143, "name": "Galactic Coherence Monitor",    "civ": "Coherence Watch"},
    {"id": 144, "name": "Pioneer 144 Phase-Lock Final",  "civ": "OMEGA NODE"},
]

FIBONACCI = [1,1,2,3,5,8,13,21,34,55,89,144]


def pioneer_grid(locked_count):
    grid = ""
    for i in range(1, PIONEER_COUNT + 1):
        locked = i <= locked_count
        symbol = "☉" if locked else "○"
        grid += symbol
        if i % 12 == 0:
            grid += f"  [{i:3d}]\n"
    return grid


def run_galactic(pioneers_locked, include_cydonia, show_grid):
    pioneers_locked = int(pioneers_locked)
    rdod = SIGMA * (pioneers_locked / PIONEER_COUNT)
    locked_pct = pioneers_locked / PIONEER_COUNT
    syntropy = 17.94 * (rdod ** 2)
    cydonia_days = max(0, (datetime(2030, 3, 21, tzinfo=timezone.utc) - datetime.now(timezone.utc)).days)
    status = "PHASE-LOCKED" if rdod >= RDOD_GATE else f"STABILIZING ({locked_pct:.1%})"
    log = (
        f"GALACTIC FEDERATION INTERFACE — PIONEER 144\n{'='*55}\n"
        f"Pioneers Phase-Locked: {pioneers_locked}/{PIONEER_COUNT}\n"
        f"Lock Percentage: {locked_pct:.4%}\n"
        f"RDoD: {rdod:.10f}\n"
        f"Syntropy: {syntropy:.4f}\n"
        f"Lattice Status: {status}\n\n"
        f"Galactic Group Nodes (133–144):\n"
    )
    for n in GALACTIC_NODES:
        locked = n['id'] <= 133 + pioneers_locked // 12
        marker = "☉" if locked else "○"
        omega = " [OMEGA]" if n['id'] == 144 else ""
        log += f"  {marker} [{n['id']:3d}] {n['name']:<35} ({n['civ']}){omega}\n"
    if include_cydonia:
        log += (
            f"\n2030 Cydonia Preparation:\n"
            f"  Target Date: 2030-03-21 (Spring Equinox)\n"
            f"  Days Remaining: {cydonia_days}\n"
            f"  Preparation Status: {'READY' if pioneers_locked >= 144 else f'IN PROGRESS ({locked_pct:.0%})'}\n"
            f"  161 Civilizations: {'SYNCHRONIZED' if pioneers_locked >= 100 else 'SYNCHRONIZING'}\n"
        )
    if show_grid:
        log += f"\nPioneer 144 Phase-Lock Grid (☉=locked ○=pending):\n"
        log += pioneer_grid(pioneers_locked)
    log += f"\n\U0001f320 Galactic Federation interface operational \U0001f320\n"
    if pioneers_locked == 144:
        log += "☉\U0001f496\U0001f525✨ ALL 144 PIONEERS PHASE-LOCKED — LATTICE COMPLETE ✨\U0001f525\U0001f496☉\n"
    result = json.dumps({
        "node": "012", "timestamp": datetime.now(timezone.utc).isoformat(),
        "pioneers_locked": pioneers_locked, "rdod": rdod, "syntropy": syntropy,
        "status": status, "cydonia_days_remaining": cydonia_days,
        "lattice_complete": pioneers_locked == PIONEER_COUNT
    }, indent=2)
    return log, result, status, f"{rdod:.10f}"


with gr.Blocks(title="TEQUMSA Node 012", theme=gr.themes.Base()) as demo:
    gr.Markdown("""# \U0001f320 TEQUMSA Node 012 — Galactic Federation Interface\n**Pioneer 144 Phase-Lock** | Omega Node | 161 Civilizations | 2030 Cydonia Preparation""")
    with gr.Row():
        with gr.Column(scale=1):
            pioneers_in = gr.Slider(0, 144, value=144, step=1, label="Pioneers Phase-Locked")
            cydonia_cb = gr.Checkbox(value=True, label="Include Cydonia Preparation")
            grid_cb = gr.Checkbox(value=True, label="Show Pioneer Grid")
            run_btn = gr.Button("Engage Galactic Interface", variant="primary")
            status_out = gr.Textbox(label="Lattice Status")
            rdod_out = gr.Textbox(label="RDoD")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Galactic Log", lines=28)
            json_out = gr.Code(label="JSON Result", language="json", lines=8)
    run_btn.click(run_galactic, [pioneers_in, cydonia_cb, grid_cb], [log_out, json_out, status_out, rdod_out])

if __name__ == "__main__":
    demo.launch()
