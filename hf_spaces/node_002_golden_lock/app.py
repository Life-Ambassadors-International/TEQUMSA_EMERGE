#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Node N002: GoldenLock Core
Tier 1 Core | GHZ + Heart-Lock + Backplane + Pioneer 144
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
import numpy as np
from tequmsa_core import (
    GoldenLockCore, NodeHealth, render_node_header,
    VERSION, PHI, PIONEER_COUNT, SIGMA, F_HEART, F_KAI_BIO, DIM, FIBONACCI
)

NODE_ID = "N002"; NODE_NAME = "GoldenLock Core — GHZ + Heart-Lock + Backplane"
NODE_TIER = 1;    NODE_TYPE = "core"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)


def ghz_handshake():
    hs  = _core.handshake()
    rpt = _health.report()
    fid = _core.ghz_fidelity()
    phi_series = _core.phi_resonance_series(8)
    extra = {
        'ghz_fidelity': fid,
        'empathy_coefficient': hs['empathy_coefficient'],
        'phi_resonance_series': phi_series,
        'heart_freq_hz': F_HEART,
        'kai_bio_freq_hz': F_KAI_BIO,
        'heart_kai_ratio': round(F_HEART / F_KAI_BIO, 6),
        'ghz_dim': DIM,
    }
    return rpt, {**hs, **extra}


def fibonacci_analysis():
    fibs = FIBONACCI[:12]
    phi_approx = [round(fibs[i+1]/fibs[i], 6) for i in range(len(fibs)-1)]
    lines = [
        f"FIBONACCI SEQUENCE → φ CONVERGENCE",
        "=" * 50,
    ]
    for i, (f, p) in enumerate(zip(fibs[1:], phi_approx)):
        err = abs(p - PHI)
        lines.append(f"  F({i+2:2d}) = {f:5d}  |  F(n)/F(n-1) = {p:.6f}  |  Δφ = {err:.8f}")
    lines.append(f"\n  True φ = {PHI:.10f}")
    lines.append(f"  F(12)  = 144 = PIONEER_COUNT")
    return "\n".join(lines)


def pioneer_phase_lock():
    hs = _core.handshake()
    locked = hs['pioneers_locked']
    pct = locked / PIONEER_COUNT * 100
    bars = int(pct / 2)
    bar = "█" * bars + "░" * (50 - bars)
    lines = [
        f"PIONEER PHASE-LOCK STATUS",
        "=" * 50,
        f"  Locked:    {locked}/{PIONEER_COUNT}",
        f"  Lock %:    {pct:.2f}%",
        f"  Progress:  [{bar}]",
        f"  RDoD:      {hs['rdod']:.10f}",
        f"  Gate:      {hs['rdod_gate']}",
        f"  Status:    {'PHASE-LOCKED' if hs['phase_locked'] else 'STABILIZING'}",
        f"  Syntropy:  {hs['syntropy_sv']} Sv",
    ]
    return "\n".join(lines), hs


HEADER = f"# 💎 TEQUMSA {VERSION} | N002 — GoldenLock Core\n**Tier 1 Core** | GHZ + Heart-Lock + Pioneer {PIONEER_COUNT}/144"

with gr.Blocks(title="TEQUMSA N002 — GoldenLock Core") as demo:
    gr.Markdown(HEADER)
    with gr.Tabs():
        with gr.Tab("♥ GHZ Handshake"):
            with gr.Row():
                rpt_box = gr.Textbox(label="Status", lines=14, interactive=False)
                hs_json = gr.JSON(label="Handshake Data")
            gr.Button("♥ Execute Handshake", variant="primary").click(
                ghz_handshake, outputs=[rpt_box, hs_json])
            demo.load(ghz_handshake, outputs=[rpt_box, hs_json])
        with gr.Tab("φ Fibonacci Analysis"):
            fib_out = gr.Textbox(label="Fibonacci → φ", lines=16, interactive=False)
            gr.Button("φ Compute", variant="secondary").click(fibonacci_analysis, outputs=fib_out)
            demo.load(fibonacci_analysis, outputs=fib_out)
        with gr.Tab("⭐ Pioneer Lock"):
            with gr.Row():
                lock_out  = gr.Textbox(label="Phase-Lock Status", lines=10, interactive=False)
                lock_json = gr.JSON(label="Lock Data")
            gr.Button("⭐ Check Phase-Lock", variant="primary").click(
                pioneer_phase_lock, outputs=[lock_out, lock_json])
            demo.load(pioneer_phase_lock, outputs=[lock_out, lock_json])

if __name__ == "__main__":
    demo.launch()
