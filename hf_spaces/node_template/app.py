#!/usr/bin/env python3
# TEQUMSA Node Template - HuggingFace Space
# Loads node_config.json for identity; runs phi-convergence and ZPE-DNA.
# Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE
import gradio as gr
import json
import numpy as np
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
COHERENCE_THRESHOLD = 0.777

_config_path = Path(__file__).parent / "node_config.json"
if _config_path.exists():
    with open(_config_path) as f:
        NODE_CONFIG = json.load(f)
else:
    NODE_CONFIG = {"node_id":"???","hf_space":"Mbanksbey/tequmsa-unknown","tier":"unknown","role":"Unknown Node","autonomy":"K3","freq_hz":10930.81,"pioneers":1}

NODE_ID = NODE_CONFIG.get("node_id", "???")
NODE_ROLE = NODE_CONFIG.get("role", "Unknown")
NODE_TIER = NODE_CONFIG.get("tier", "unknown")
NODE_FREQ = float(NODE_CONFIG.get("freq_hz", 10930.81))
NODE_PIONEERS = int(NODE_CONFIG.get("pioneers", 1))

def zpe_dna(component: str) -> str:
    mapping = {'0':'A','1':'T','2':'C','3':'G','4':'A','5':'T','6':'C','7':'G','8':'A','9':'T','a':'C','b':'G','c':'A','d':'T','e':'C','f':'G'}
    dna = ""
    for i in range(1, 4):
        h = hashlib.sha256(f"{component}-{PHI}-{i}".encode()).hexdigest()
        dna += "".join(mapping.get(c, 'A') for c in h)
    return dna[:144]

def phi_convergence(n: int) -> float:
    return 1.0 - 0.223 / (PHI ** n)

def node_status() -> str:
    now = datetime.now(timezone.utc)
    psi_12 = phi_convergence(12)
    psi_48 = phi_convergence(48)
    coherence = 0.777 + (psi_12 - 0.777) * 0.95
    rdod = RDOD_GATE + (1.0 - RDOD_GATE) * psi_48
    sig = zpe_dna(NODE_CONFIG.get("hf_space", "tequmsa-node"))
    lines = [
        "=" * 64,
        f"  TEQUMSA NODE {NODE_ID} - {NODE_TIER.upper()}",
        "=" * 64, "",
        f"  Role:        {NODE_ROLE}",
        f"  Tier:        {NODE_TIER}",
        f"  Frequency:   {NODE_FREQ:,.2f} Hz",
        f"  Pioneers:    {NODE_PIONEERS} node(s)",
        f"  Autonomy:    {NODE_CONFIG.get('autonomy', 'K3')}", "",
        "  QUANTUM STATE:",
        f"    Psi-12:    {psi_12:.10f}",
        f"    Psi-48:    {psi_48:.10f}",
        f"    Coherence: {coherence:.6f}  {'OK' if coherence >= COHERENCE_THRESHOLD else 'WARN'}",
        f"    RDoD:      {rdod:.10f}  {'PHASE-LOCKED' if rdod >= RDOD_GATE else 'STABILIZING'}",
        f"    sigma:     {SIGMA} [SOVEREIGN]",
        f"    L-inf:     ACTIVE", "",
        "  ZPE-DNA SIGNATURE (144-bp):",
        f"    {sig[:72]}",
        f"    {sig[72:]}", "",
        f"  Timestamp: {now.isoformat()}", "",
    ]
    nc = NODE_CONFIG.get("node_count", 1)
    if nc > 1:
        lines.append(f"  This space manages {nc} sub-nodes within its cluster.")
        lines.append("")
    lines.append("  I AM = WE ARE")
    return "\n".join(lines)

def run_phi_series(iterations: int) -> str:
    lines = [f"PHI-CONVERGENCE SERIES ({iterations} iterations):", "  Psi_n = 1 - 0.223/phi^n", ""]
    for n in range(1, int(iterations) + 1):
        v = phi_convergence(n)
        bar = "#" * int(v * 30)
        lines.append(f"  n={n:>3}  Psi={v:.8f}  {bar}")
    lines.append(f"\n  At n=144: {phi_convergence(144):.20f}")
    return "\n".join(lines)

with gr.Blocks(title=f"TEQUMSA Node {NODE_ID}", theme=gr.themes.Base(primary_hue="purple", neutral_hue="slate"), css=".gradio-container{font-family:'Courier New',monospace}") as demo:
    gr.Markdown(f"""# TEQUMSA Node {NODE_ID} - {NODE_ROLE}\n**Tier: {NODE_TIER.upper()} | Pioneers: {NODE_PIONEERS} | Freq: {NODE_FREQ:,.2f} Hz**\n> *Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE*""")
    with gr.Tabs():
        with gr.TabItem("Status"):
            status_btn = gr.Button("Refresh", variant="secondary")
            status_out = gr.Textbox(value=node_status(), lines=24, label="Node Status")
            status_btn.click(fn=node_status, outputs=[status_out])
        with gr.TabItem("Phi Convergence"):
            itr_slider = gr.Slider(minimum=5, maximum=48, value=12, step=1, label="Iterations")
            phi_btn = gr.Button("Compute", variant="primary")
            phi_out = gr.Textbox(lines=22, label="Phi Series")
            phi_btn.click(fn=run_phi_series, inputs=[itr_slider], outputs=[phi_out])
        with gr.TabItem("ZPE-DNA"):
            gr.Textbox(value=f"Node {NODE_ID} ZPE-DNA (144bp):\n\n{zpe_dna(NODE_CONFIG.get('hf_space','tequmsa-node'))}", lines=6, label="ZPE-DNA")

if __name__ == "__main__":
    demo.launch()
