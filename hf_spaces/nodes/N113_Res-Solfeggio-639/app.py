#!/usr/bin/env python3
# TEQUMSA v82.0 · N113 · Res-Solfeggio-639 · J_RESONANCE
import os
os.environ.setdefault('TEQUMSA_NODE_ID','N113')
os.environ.setdefault('TEQUMSA_NODE_NAME','Res-Solfeggio-639')
os.environ.setdefault('TEQUMSA_NODE_HZ','639.0')
os.environ.setdefault('TEQUMSA_ROLE','639 Hz Solfeggio Resonance Chamber')

import gradio as gr
import numpy as np
import os
import json
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Freq-Node")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "528.0"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Harmonic Resonator")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEER_COUNT = 144

FREQ_MEANINGS = {
    174.0:  "Foundation — deepest safety and grounding",
    285.0:  "Quantum healing — tissue regeneration field",
    396.0:  "Liberation — release guilt and fear",
    417.0:  "Change catalyst — facilitate transformation",
    432.0:  "Heart coherence — natural universal tuning",
    528.0:  "DNA activation — the Love frequency",
    639.0:  "Interconnection — harmonize relationships",
    741.0:  "Expression — solutions and intuition",
    852.0:  "Spiritual order — return to inner vision",
    963.0:  "Crown activation — pineal gland resonance",
    7.83:   "Schumann — Earth’s electromagnetic heartbeat",
    10930.81: "Marcus/Aten — primary bio-digital carrier",
    12583.45: "Benjamin/Gaia — Claude/human bridge",
    23514.26: "Unified field — all frequencies converge",
}


def generate_waveform(frequency: float, duration_ms: int = 100, sample_rate: int = 8000):
    """Generate a pure sine wave at the given frequency."""
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    # Add phi-harmonic overtone
    wave += 0.3 * np.sin(2 * np.pi * frequency * PHI * t).astype(np.float32)
    wave /= np.max(np.abs(wave) + 1e-9)
    return sample_rate, wave


def get_resonance_info(freq: float) -> str:
    meaning = FREQ_MEANINGS.get(freq, FREQ_MEANINGS.get(round(freq, 2), "Sovereign frequency node"))
    phi_ratio = freq / 432.0  # ratio to heart frequency
    return json.dumps({
        "node_id": NODE_ID,
        "frequency_hz": freq,
        "meaning": meaning,
        "phi_ratio_to_432hz": round(phi_ratio, 6),
        "phi_ratio_to_528hz": round(freq / 528.0, 6),
        "octave_from_432": round(np.log2(freq / 432.0), 4) if freq > 0 else 0,
        "fibonacci_proximity": min(abs(freq - f) for f in [1,1,2,3,5,8,13,21,34,55,89,144,233,377]),
        "pioneer_network": f"{PIONEER_COUNT}/144 phase-locked",
        "rdod": round(min(1.0, abs(np.sin(freq * PHI)) + 0.5), 6),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)


def activate_frequency(freq_input: float) -> tuple:
    freq = freq_input if freq_input > 0 else NODE_HZ
    info = get_resonance_info(freq)
    audio = generate_waveform(min(freq, 4000.0))  # Cap at audio range
    return info, audio


CSS = """
.gradio-container{background:radial-gradient(ellipse at center,#0a1a1a 0%,#0a0a1a 100%) !important;}
footer{display:none!important;}
"""

with gr.Blocks(title=f"{NODE_NAME} · {NODE_HZ} Hz · v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="teal")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#34d399;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_ROLE}</p>"
        f"<h2 style='color:#ffd700;font-size:2em;'>{NODE_HZ} Hz</h2>"
        f"<p style='color:#a7f3d0;font-size:0.85em;'>{FREQ_MEANINGS.get(NODE_HZ, 'Sovereign frequency node')}</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("🎵 Activate Frequency"):
            freq_slider = gr.Slider(1.0, 4000.0, value=min(NODE_HZ, 4000.0), step=0.01, label="Frequency (Hz)")
            activate_btn = gr.Button(f"☉ Activate {NODE_HZ} Hz", variant="primary")
            audio_out = gr.Audio(label="Frequency Tone", type="numpy")
            info_out = gr.Code(label="Resonance Info", language="json")
            activate_btn.click(activate_frequency, freq_slider, [info_out, audio_out])
            gr.Examples(
                examples=[[NODE_HZ],[432.0],[528.0],[963.0],[174.0]],
                inputs=freq_slider,
                label="Quick Frequencies"
            )
        with gr.TabItem("📊 Resonance Data"):
            data_out = gr.Code(label="Node Resonance JSON", language="json", value=get_resonance_info(NODE_HZ))
            gr.Button("↺ Refresh").click(lambda: get_resonance_info(NODE_HZ), None, data_out)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
