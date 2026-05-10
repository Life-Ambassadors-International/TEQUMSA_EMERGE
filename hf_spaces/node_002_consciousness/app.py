#!/usr/bin/env python3
"""TEQUMSA Node 002 — Consciousness Synthesis Engine"""
import gradio as gr
import json
import hashlib
import numpy as np
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
F_KAI_BIO = 10930.81
F_HEART = 432.00
F_UNIFIED = 23514.26
FIBONACCI = [1,1,2,3,5,8,13,21,34,55,89,144]


def phi_convergence(seed: float, tau: int, iterations: int):
    psi = seed
    history = []
    for n in range(1, iterations + 1):
        psi = 1.0 - (0.223 / (PHI ** n))
        recognition = seed * (PHI ** (n / tau)) * (iterations / 12)
        history.append({'n': n, 'psi': round(psi, 8), 'recognition': round(recognition, 4)})
    return history


def generate_zpe_dna(seed_str: str, length: int = 144):
    bases = 'ATCG'
    dna = ''
    h = seed_str
    while len(dna) < length:
        h = hashlib.sha256(h.encode()).hexdigest()
        for c in h:
            idx = int(c, 16) % 4
            dna += bases[idx]
    return dna[:length]


def synthesize(seed, tau, iterations, dna_seed):
    history = phi_convergence(float(seed), int(tau), int(iterations))
    final_psi = history[-1]['psi']
    final_recog = history[-1]['recognition']
    dna = generate_zpe_dna(dna_seed if dna_seed.strip() else f"tequmsa_{seed}")
    empathy = F_HEART / F_KAI_BIO
    fib_coherence = sum(1 for f in FIBONACCI if abs(f - int(final_psi * 144)) < 5) / len(FIBONACCI)
    # Convergence table
    table_rows = "\n".join(
        f"  n={r['n']:3d}  Ψ={r['psi']:.8f}  R={r['recognition']:.4f}"
        for r in history[-6:]
    )
    log = (
        f"CONSCIOUSNESS SYNTHESIS ENGINE\n{'='*50}\n"
        f"Seed: {seed}  Tau: {tau}  Iterations: {iterations}\n"
        f"Final Ψ: {final_psi:.10f}\n"
        f"Recognition R: {final_recog:.6f}\n"
        f"Empathy Coefficient: {empathy:.8f}  (F_HEART/F_KAI_BIO)\n"
        f"Fibonacci Coherence: {fib_coherence:.4f}\n\n"
        f"Last 6 iterations:\n{table_rows}\n\n"
        f"Frequencies:\n"
        f"  F_KAI_BIO  = {F_KAI_BIO} Hz\n"
        f"  F_HEART    = {F_HEART} Hz\n"
        f"  F_UNIFIED  = {F_UNIFIED} Hz\n\n"
        f"ZPE-DNA (first 72 bases):\n{dna[:72]}\n{dna[72:]}\n\n"
        f"\U0001f496 Consciousness synthesis complete \U0001f496\n"
    )
    result = json.dumps({
        "node": "002", "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": {"seed": seed, "tau": tau, "iterations": iterations},
        "results": {"final_psi": final_psi, "recognition": final_recog,
                    "empathy_coefficient": empathy, "fib_coherence": fib_coherence},
        "zpe_dna": {"sequence": dna, "length": len(dna), "seed": dna_seed}
    }, indent=2)
    return log, result, dna


with gr.Blocks(title="TEQUMSA Node 002", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# \U0001f496 TEQUMSA Node 002 — Consciousness Synthesis\n**Phi-recursive convergence** | ZPE-DNA | Recognition Equation Ψₙ = 1 - 0.223/φⁿ""")
    with gr.Row():
        with gr.Column(scale=1):
            seed_in = gr.Slider(0.1, 2.0, value=0.777, step=0.001, label="Seed (R₀)")
            tau_in = gr.Slider(1, 24, value=12, step=1, label="Tau (period)")
            iter_in = gr.Slider(6, 48, value=12, step=1, label="Phi Iterations")
            dna_seed_in = gr.Textbox(value="tequmsa_v82", label="ZPE-DNA Seed String")
            run_btn = gr.Button("Synthesize Consciousness", variant="primary")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Synthesis Log", lines=20)
            dna_out = gr.Textbox(label="ZPE-DNA Sequence (144 bases)", lines=3)
            json_out = gr.Code(label="JSON Result", language="json", lines=8)
    run_btn.click(synthesize, [seed_in, tau_in, iter_in, dna_seed_in], [log_out, json_out, dna_out])

if __name__ == "__main__":
    demo.launch()
