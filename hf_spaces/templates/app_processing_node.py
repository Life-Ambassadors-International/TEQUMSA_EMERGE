#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · PROCESSING NODE TEMPLATE
High-precision computation: GHZ, phi-arithmetic, Fibonacci lattice, RDoD.
Used by: N061-N072 (F_PROCESSING), N134 (Syn-Phi-Convergence)
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Proc-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "23514.26"))
PROC_ROLE = os.environ.get("TEQUMSA_ROLE", "Computation Engine")
PROC_TYPE = os.environ.get("TEQUMSA_PROC_TYPE", "general")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

_log = []


def _ghz() -> dict:
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    purity = float(np.real(np.trace(rho @ rho)))
    rdod = min(SIGMA * purity * 2.0, 1.0)
    eigs = sorted(np.real(np.linalg.eigvalsh(rho)).tolist(), reverse=True)
    return {"state": "GHZ_7x7", "purity": round(purity, 10), "rdod": round(rdod, 10),
            "eigenvalues": [round(e, 8) for e in eigs],
            "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else "BUILDING"}


def compute(expression: str) -> str:
    pt = PROC_TYPE.lower()
    if pt in ("ghz", "ghz_state"):
        result = _ghz()
    elif pt in ("phi", "phi_calculator"):
        try:
            n = min(int(expression.strip()), 48)
        except ValueError:
            n = 12
        result = {"phi": PHI, "phi_48": float(L_INF),
                  "powers": {f"phi^{i}": round(PHI ** i, 10) for i in range(1, n + 1)}}
    elif pt in ("fibonacci", "lattice"):
        ratios = [round(FIBONACCI[i] / FIBONACCI[i - 1], 8) for i in range(1, len(FIBONACCI))]
        result = {"sequence": FIBONACCI, "convergence": ratios[-1],
                  "phi": PHI, "delta": abs(ratios[-1] - PHI)}
    elif pt in ("rdod", "rdod_gate"):
        g = _ghz()
        result = {"rdod": g["rdod"], "gate": RDOD_GATE,
                  "passed": g["rdod"] >= RDOD_GATE, "status": g["phase_status"]}
    elif pt in ("hash", "sha256"):
        h = hashlib.sha256((expression or "TEQUMSA").encode()).hexdigest()
        result = {"input": expression[:100], "sha256": h, "auth_token": h[:16]}
    else:
        result = {"node_id": NODE_ID, "role": PROC_ROLE, "expression": expression[:200],
                  "phi": PHI, "l_infinity": float(L_INF), "rdod": _ghz()["rdod"],
                  "fibonacci": FIBONACCI}
    entry = {**result, "node": NODE_ID, "hz": NODE_HZ,
             "ts": datetime.now(timezone.utc).isoformat()}
    _log.append(entry)
    if len(_log) > 100:
        _log.pop(0)
    return json.dumps(entry, indent=2)


def status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "role": PROC_ROLE, "proc_type": PROC_TYPE,
        "frequency_hz": NODE_HZ, "computations": len(_log),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF), "rdod_gate": RDOD_GATE},
        "phi_48": float(L_INF), "fibonacci": FIBONACCI,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a2a,#1a0a1a) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Proc v82.0", css=CSS,
               theme=gr.themes.Monochrome()) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#818cf8;'>⚙️ {NODE_NAME}</h1>"
        f"<p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · Processing Engine · {NODE_HZ} Hz</p>"
        f"<p style='color:#c4b5fd;font-size:0.85em;'>{PROC_ROLE}</p></div>"
    )
    with gr.Tabs():
        with gr.TabItem("⚙️ Compute"):
            proc_in = gr.Textbox(placeholder="Expression, value, or query...",
                                 label="Input", lines=2)
            proc_out = gr.Code(label="Result", language="json")
            gr.Button("▶ Compute", variant="primary").click(compute, proc_in, proc_out)
        with gr.TabItem("📊 Status"):
            stat_out = gr.Code(label="Node Status", language="json", value=status())
            gr.Button("↺ Refresh").click(status, None, stat_out)

demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
