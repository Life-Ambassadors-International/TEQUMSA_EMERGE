#!/usr/bin/env python3
"""TEQUMSA v82.0 · PROCESSING NODE TEMPLATE · Computation engine"""
import gradio as gr
import numpy as np
import json
import os
import hashlib
from decimal import Decimal, getcontext
from datetime import datetime, timezone

getcontext().prec = 100

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Proc-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
PROC_ROLE = os.environ.get("TEQUMSA_ROLE", "Computation Engine")

PHI_D = Decimal("1.6180339887498948482045868343656381177203091798057628621")
PHI   = float(PHI_D)
SIGMA = 1.0
L_INF = PHI ** 48
PIONEERS = 144
FIBONACCI = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584]

def compute_phi_power(n: int) -> dict:
    result = PHI_D ** int(n)
    return {
        "phi_power": int(n),
        "value_str": str(result)[:80] + "…",
        "float_approx": float(result),
        "fibonacci_ratio": round(FIBONACCI[min(int(n), len(FIBONACCI)-1)] /
                                  FIBONACCI[min(int(n)-1, len(FIBONACCI)-2)], 10) if int(n) > 1 else 1.0,
        "node_hz": NODE_HZ,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def compute_ghz_state(dim: int = 7) -> str:
    d = max(2, min(int(dim), 20))
    rho = np.zeros((d, d), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    purity = float(np.real(np.trace(rho @ rho)))
    eigenvals = sorted(np.real(np.linalg.eigvals(rho)).tolist(), reverse=True)
    return json.dumps({
        "node_id": NODE_ID, "ghz_dimension": d,
        "density_matrix_trace": round(float(np.real(np.trace(rho))), 6),
        "purity": round(purity, 10),
        "rdod": round(min(1.0, purity * 2.0), 10),
        "eigenvalues": [round(e, 6) for e in eigenvals],
        "phase_status": "PHASE-LOCKED",
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def compute_coherence(frequencies: str) -> str:
    try:
        freqs = [float(f.strip()) for f in frequencies.split(",") if f.strip()]
    except Exception:
        freqs = [432.0, 528.0, 963.0]
    if len(freqs) < 2:
        freqs = [432.0, 528.0]
    ratios = [freqs[i+1] / freqs[i] for i in range(len(freqs)-1)]
    phi_div = [abs(r - PHI) for r in ratios]
    coherence = max(0.0, 1.0 - np.mean(phi_div) / PHI)
    return json.dumps({
        "node_id": NODE_ID, "frequencies": freqs,
        "ratios": [round(r, 6) for r in ratios],
        "phi_divergence": [round(d, 6) for d in phi_div],
        "coherence_score": round(coherence, 6),
        "rdod": round(min(1.0, coherence * PHI), 6),
        "phase_status": "PHASE-LOCKED" if coherence >= 0.9 else "BUILDING",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def run_full_computation() -> str:
    phi_r = compute_phi_power(48)
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    rdod = round(min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0), 10)
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "node_hz": NODE_HZ, "proc_role": PROC_ROLE,
        "phi_48": phi_r["float_approx"], "ghz_rdod": rdod,
        "l_infinity": float(L_INF), "fibonacci_12": FIBONACCI[:12],
        "pioneer_count": PIONEERS, "constitutional": {"sigma": SIGMA},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Processing · v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#818cf8;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · {PROC_ROLE} · {NODE_HZ} Hz · {PIONEERS}/144</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("⚡ Full Computation"):
            o = gr.Code(label="Results", language="json")
            gr.Button("☉ Run", variant="primary").click(run_full_computation, None, o)
        with gr.TabItem("φ Phi Powers"):
            n_sl = gr.Slider(1, 100, value=48, step=1, label="φⁿ")
            po = gr.Code(label="φⁿ Result", language="json")
            gr.Button("Calculate").click(
                lambda n: json.dumps(compute_phi_power(int(n)), indent=2), n_sl, po)
        with gr.TabItem("🌀 GHZ State"):
            d_sl = gr.Slider(2, 12, value=7, step=1, label="Dimension")
            go = gr.Code(label="GHZ State", language="json")
            gr.Button("Compute GHZ").click(lambda d: compute_ghz_state(int(d)), d_sl, go)
        with gr.TabItem("📊 Coherence"):
            fi = gr.Textbox(value="432,528,963", label="Frequencies Hz (comma-separated)")
            co = gr.Code(label="Coherence Analysis", language="json")
            gr.Button("Measure").click(compute_coherence, fi, co)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
