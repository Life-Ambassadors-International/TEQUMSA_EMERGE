#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · PROCESSING NODE TEMPLATE
Computational engine with phi-recursive math, coherence calculation, and ZPE-DNA generation.

Used by: N061-N072 (F_PROCESSING), N134 (Syn-Phi-Convergence)
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, List

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Proc-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
PROC_ROLE = os.environ.get("TEQUMSA_ROLE", "Processing Engine")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
PIONEER_COUNT = 144
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]

_computation_log: List[dict] = []


def phi_recursive_convergence(iterations: int = 144) -> dict:
    iterations = max(1, min(iterations, 100000))
    values = []
    for n in range(1, iterations + 1):
        psi_n = 1 - 0.223 / (PHI ** n)
        values.append(psi_n)
    return {
        "function": "psi_n = 1 - 0.223 / phi^n",
        "iterations": iterations,
        "initial_value": round(values[0], 10),
        "final_value": round(values[-1], 15),
        "converged_to_unity": values[-1] >= 0.9999999,
        "convergence_at_iteration": next((i + 1 for i, v in enumerate(values) if v >= 0.9999999), None),
        "phi": PHI,
    }


def coherence_calculation(n_cycles: int = 144, p0: float = 0.777) -> dict:
    n_cycles = max(1, min(n_cycles, 10000))
    p0 = max(0.0, min(p0, 1.0))
    values = []
    for n in range(1, n_cycles + 1):
        c_n = 1 - ((1 - p0) / (PHI ** n))
        values.append(c_n)
    return {
        "function": "C(n;p0) = 1 - ((1-p0) / phi^n)",
        "p0": p0,
        "n_cycles": n_cycles,
        "initial_coherence": round(values[0], 10),
        "final_coherence": round(values[-1], 15),
        "above_threshold": values[-1] >= 0.777,
        "threshold": 0.777,
    }


def generate_zpe_dna(component: str = "", seed: float = 0.777) -> dict:
    if not component.strip():
        component = f"{NODE_ID}-{NODE_NAME}"
    data = f"{component}-{seed}-{PHI}"
    mapping = {
        '0': 'A', '1': 'T', '2': 'C', '3': 'G',
        '4': 'A', '5': 'T', '6': 'C', '7': 'G',
        '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
        'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G',
    }
    dna = ""
    for i in range(3):
        h = hashlib.sha256(f"{data}-{i}".encode()).hexdigest()
        dna += "".join(mapping.get(c, 'A') for c in h[:64])
    dna = dna[:144]
    gc = sum(1 for b in dna if b in ('G', 'C'))
    return {
        "component": component,
        "seed": seed,
        "sequence_length": len(dna),
        "sequence": dna,
        "gc_content": round(gc / len(dna), 4),
        "at_content": round(1 - gc / len(dna), 4),
    }


def run_computation(calc_type: str, param1: float, param2: float) -> str:
    if calc_type == "phi_convergence":
        result = phi_recursive_convergence(int(param1))
    elif calc_type == "coherence":
        result = coherence_calculation(int(param1), param2)
    elif calc_type == "zpe_dna":
        result = generate_zpe_dna(f"user-{param1}", param2)
    elif calc_type == "l_infinity":
        power = max(1, min(int(param1), 100))
        result = {"function": f"L_inf = phi^{power}", "value": float(PHI ** power), "phi": PHI, "power": power}
    elif calc_type == "recognition_cascade":
        r0 = 1717524
        t = max(0, min(param1, 1000))
        cascade = r0 * (PHI ** (t / 12)) * 143127
        result = {"function": "R(t) = R0 * phi^(t/12) * 143127", "R0": r0, "t": t, "cascade_value": cascade}
    else:
        result = {"error": f"Unknown calc_type: {calc_type}"}

    entry = {"type": calc_type, "params": [param1, param2], "ts": datetime.now(timezone.utc).isoformat()}
    _computation_log.append(entry)
    if len(_computation_log) > 200:
        _computation_log.pop(0)

    result["node_id"] = NODE_ID
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(result, indent=2, default=str)


def get_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "version": "v82.0",
        "frequency_hz": NODE_HZ, "role": PROC_ROLE,
        "computations_run": len(_computation_log),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF), "rdod_gate": RDOD_GATE},
        "fibonacci_sequence": FIBONACCI[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#0a1a2e) !important;} footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#60a5fa;'>⚙ {NODE_NAME}</h1>"
        f"<p style='color:#93c5fd;'>TEQUMSA v82.0 · {NODE_ID} · Processing Node · {NODE_HZ} Hz</p>"
        f"<p style='color:#bfdbfe;font-size:0.85em;'>{PROC_ROLE}</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("⚙ Compute"):
            calc_type = gr.Dropdown(
                choices=["phi_convergence", "coherence", "zpe_dna", "l_infinity", "recognition_cascade"],
                value="phi_convergence", label="Calculation Type"
            )
            with gr.Row():
                p1 = gr.Number(value=144, label="Parameter 1 (iterations/cycles/power/t)")
                p2 = gr.Number(value=0.777, label="Parameter 2 (p0/seed)")
            result_out = gr.Code(label="Result", language="json")
            gr.Button("▶ Compute", variant="primary").click(run_computation, [calc_type, p1, p2], result_out)
        with gr.TabItem("📊 Status"):
            status_out = gr.Code(label="Node Status", language="json", value=get_status())
            gr.Button("↺ Refresh").click(get_status, None, status_out)

demo.queue(max_size=10)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
