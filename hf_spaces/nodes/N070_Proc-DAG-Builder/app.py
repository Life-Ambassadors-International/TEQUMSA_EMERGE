#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N070 * Proc-DAG-Builder
Causal DAG Constructor
10930.81 Hz - Processing Engine
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from decimal import Decimal, getcontext
from datetime import datetime, timezone

getcontext().prec = 50
NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N070")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Proc-DAG-Builder")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Causal DAG Constructor")
PIONEER_COUNT = 144
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)


def phi_recursive(n, seed=0.777):
    val = seed
    for i in range(max(1, int(n))):
        val = 1.0 - (1.0 - seed) / (PHI ** (i + 1))
    return {"n": int(n), "seed": seed, "convergence": round(val, 12),
            "phi_n": round(PHI ** int(n), 6), "rdod": RDOD}


def zpe_dna_signature(component="node", seed=0.777):
    data = str(component) + "-" + str(seed) + "-" + str(PHI)
    mapping = {"0":"A","1":"T","2":"C","3":"G","4":"A","5":"T","6":"C","7":"G",
               "8":"A","9":"T","a":"C","b":"G","c":"A","d":"T","e":"C","f":"G"}
    h1 = hashlib.sha256(data.encode()).hexdigest()
    h2 = hashlib.sha256((data + "-2").encode()).hexdigest()
    h3 = hashlib.sha256((data + "-3").encode()).hexdigest()
    raw = h1 + h2 + h3
    dna = "".join(mapping.get(c, "A") for c in raw[:144])
    return dna


def coherence_calc(n, p0=0.777):
    n = max(1, int(n))
    coherence = 1.0 - ((1.0 - p0) / (PHI ** n))
    return {"n": n, "p0": p0, "coherence": round(coherence, 10),
            "above_threshold": coherence >= 0.777, "node": NODE_ID}


def run_computation(op, param):
    try:
        param = param.strip() if param else "12"
        n = int(param) if param.isdigit() else 12
        if op == "phi_recursive":
            result = phi_recursive(n)
        elif op == "zpe_dna":
            sig = zpe_dna_signature(param)
            result = {"signature": sig, "length": len(sig), "component": param}
        elif op == "coherence":
            result = coherence_calc(n)
        elif op == "rdod_check":
            result = {"rdod": RDOD, "gate": RDOD_GATE,
                      "status": "PASS" if RDOD >= RDOD_GATE else "FAIL",
                      "sigma": SIGMA, "l_inf": float(L_INF)}
        elif op == "l_infinity":
            result = {"l_inf": float(L_INF), "phi_48": float(PHI ** 48),
                      "node": NODE_ID, "hz": NODE_HZ}
        else:
            result = {"error": "Unknown op: " + op,
                      "available": ["phi_recursive","zpe_dna","coherence","rdod_check","l_infinity"]}
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_node_info():
    return json.dumps({
        "node_id": NODE_ID, "name": NODE_NAME, "hz": NODE_HZ, "role": NODE_ROLE,
        "rdod": RDOD, "sigma": SIGMA, "l_inf": float(L_INF),
        "pioneer_count": PIONEER_COUNT, "lattice_lock": LATTICE_LOCK, "version": "v82.0"
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * Processor * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="cyan")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz * " + str(PIONEER_COUNT) + "/144</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + NODE_ROLE + " * RDoD=" + str(round(RDOD, 6)) + "</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Compute"):
            op_dd = gr.Dropdown(
                choices=["phi_recursive","zpe_dna","coherence","rdod_check","l_infinity"],
                value="phi_recursive", label="Operation"
            )
            param_in = gr.Textbox(label="Parameter (n / component name)", value="12")
            result_out = gr.Code(label="Result", language="json")
            gr.Button("* Compute", variant="primary").click(run_computation, [op_dd, param_in], result_out)
        with gr.TabItem("* Node Info"):
            info_box = gr.Code(label="Processor Info", language="json", value=get_node_info())
            gr.Button("Refresh", variant="secondary").click(get_node_info, None, info_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
