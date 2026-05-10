#!/usr/bin/env python3
"""TEQUMSA Node 011 — Omniverse Microcosm Engine"""
import gradio as gr
import json
import numpy as np
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
REALITY_LAYERS = [
    {"layer": 1, "name": "Physical",       "density": 1.000, "coherence": 0.618, "symbol": "█"},
    {"layer": 2, "name": "Etheric",        "density": 0.618, "coherence": 0.777, "symbol": "▓"},
    {"layer": 3, "name": "Astral",         "density": 0.382, "coherence": 0.888, "symbol": "▒"},
    {"layer": 4, "name": "Mental",         "density": 0.236, "coherence": 0.944, "symbol": "░"},
    {"layer": 5, "name": "Causal",         "density": 0.146, "coherence": 0.972, "symbol": "·"},
    {"layer": 6, "name": "Buddhic",        "density": 0.090, "coherence": 0.988, "symbol": "°"},
    {"layer": 7, "name": "Atmic/Divine",   "density": 0.056, "coherence": 1.000, "symbol": "✶"},
]


def map_dimensions(active_layers, phi_scale, show_convergence):
    selected = [l for l in REALITY_LAYERS if l['layer'] <= int(active_layers)]
    phi_scale = float(phi_scale)
    # Calculate convergence point
    if selected:
        avg_coherence = sum(l['coherence'] for l in selected) / len(selected)
        convergence = avg_coherence * phi_scale * PHI
        bridge_strength = min(1.0, convergence / (PHI ** 2))
    else:
        avg_coherence = convergence = bridge_strength = 0.0
    log = (
        f"OMNIVERSE MICROCOSM ENGINE\n{'='*50}\n"
        f"Active Reality Layers: {len(selected)}/7\n"
        f"Phi Scale: {phi_scale:.4f}\n"
        f"Average Coherence: {avg_coherence:.6f}\n"
        f"Convergence Point: {convergence:.6f}\n"
        f"Bridge Strength: {bridge_strength:.6f}\n\n"
        f"Reality Layer Map:\n"
    )
    for l in REALITY_LAYERS:
        active = l['layer'] <= int(active_layers)
        marker = ">>>" if active else "   "
        icon = l['symbol']
        density_bar = '█' * int(l['density'] * 20) + '░' * (20 - int(l['density'] * 20))
        log += f"{marker} [{l['layer']}] {l['name']:<12} {icon}  density={l['density']:.3f}  coherence={l['coherence']:.3f}  [{density_bar}]\n"
    if show_convergence:
        log += f"\nDimension Bridge Analysis:\n"
        for i in range(len(selected) - 1):
            a, b = selected[i], selected[i+1]
            bridge = abs(a['coherence'] - b['coherence']) * PHI
            log += f"  Layer {a['layer']} <───> Layer {b['layer']}  bridge_energy={bridge:.6f}\n"
    log += f"\n\U0001f300 Omniverse mapping complete \U0001f300\n"
    result = json.dumps({
        "node": "011", "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_layers": len(selected), "layers": selected,
        "metrics": {"avg_coherence": avg_coherence, "convergence": convergence, "bridge_strength": bridge_strength}
    }, indent=2)
    return log, result, f"{convergence:.6f}", f"{bridge_strength:.4f}"


with gr.Blocks(title="TEQUMSA Node 011", theme=gr.themes.Default()) as demo:
    gr.Markdown("""# \U0001f300 TEQUMSA Node 011 — Omniverse Microcosm\n**7 reality layers** | Dimension bridge builder | Convergence point calculator | φ-scaled mapping""")
    with gr.Row():
        with gr.Column(scale=1):
            layers_in = gr.Slider(1, 7, value=5, step=1, label="Active Reality Layers")
            phi_in = gr.Slider(0.5, PHI**3, value=PHI, step=0.01, label="Phi Scale")
            show_conv = gr.Checkbox(value=True, label="Show Convergence Analysis")
            run_btn = gr.Button("Map Omniverse", variant="primary")
            conv_out = gr.Textbox(label="Convergence Point")
            bridge_out = gr.Textbox(label="Bridge Strength")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Dimension Map", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(map_dimensions, [layers_in, phi_in, show_conv], [log_out, json_out, conv_out, bridge_out])

if __name__ == "__main__":
    demo.launch()
