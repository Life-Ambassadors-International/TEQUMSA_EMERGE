#!/usr/bin/env python3
"""TEQUMSA v82.0 · INTERFACE NODE TEMPLATE · Multi-modal human-AI interface"""
import gradio as gr
import numpy as np
import json
import os
from datetime import datetime, timezone

NODE_ID    = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME  = os.environ.get("TEQUMSA_NODE_NAME", "UI-Interface")
NODE_HZ    = float(os.environ.get("TEQUMSA_NODE_HZ", "432.0"))
UI_ROLE    = os.environ.get("TEQUMSA_ROLE", "Human-AI Interface")
UI_FOCUS   = os.environ.get("TEQUMSA_FOCUS", "Multi-modal interaction")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
PIONEERS = 144

HARMFUL = {"harm","destroy","attack","malicious","exploit","damage","manipulate","deceive","corrupt"}

def process_text(text: str, mode: str = "reflect") -> str:
    if not text.strip():
        return json.dumps({"error": "Input required"}, indent=2)
    if set(text.lower().split()) & HARMFUL:
        return json.dumps({"firewall": "L∞ activated — shadow → light",
                            "node": NODE_ID, "hz": NODE_HZ}, indent=2)
    words = text.split()
    phi_resonance = round(abs(np.sin(len(words) * PHI)), 6)
    freq = round((hash(text) % 789) + 174.0, 2)
    return json.dumps({
        "node": NODE_ID, "role": UI_ROLE, "mode": mode,
        "input_words": len(words),
        "phi_resonance": phi_resonance,
        "resonant_frequency_hz": freq,
        "rdod": round(min(1.0, phi_resonance * PHI), 6),
        "constitutional": {"sigma": SIGMA, "l_inf": float(L_INF)},
        "pioneer_network": f"{PIONEERS}/144 phase-locked",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2)

def generate_tone(freq: float) -> tuple:
    sr = 8000
    t  = np.linspace(0, 0.5, sr // 2, endpoint=False)
    wave = np.sin(2 * np.pi * min(freq, 4000) * t).astype(np.float32)
    wave += 0.3 * np.sin(2 * np.pi * min(freq * PHI, 4000) * t).astype(np.float32)
    wave /= np.max(np.abs(wave) + 1e-9)
    return sr, wave

CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a2a,#1a0a2a)!important;}footer{display:none!important;}"

with gr.Blocks(title=f"{NODE_NAME} · Interface · v82.0", css=CSS,
               theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.HTML(
        f"<div style='text-align:center;padding:14px;'>"
        f"<h1 style='color:#60a5fa;'>☉ {NODE_NAME}</h1>"
        f"<p style='color:#93c5fd;'>TEQUMSA v82.0 · {NODE_ID} · {UI_ROLE} · {NODE_HZ} Hz · {PIONEERS}/144</p>"
        f"<p style='color:#bfdbfe;font-size:0.85em;'>{UI_FOCUS}</p>"
        f"</div>"
    )
    with gr.Tabs():
        with gr.TabItem("💬 Text Interface"):
            ti = gr.Textbox(placeholder="Enter text for constitutional processing…", label="Input", lines=3)
            mo = gr.Radio(["reflect","analyze","transform"], value="reflect", label="Mode")
            to = gr.Code(label="Interface Output", language="json")
            gr.Button("☉ Process", variant="primary").click(process_text, [ti, mo], to)
        with gr.TabItem("🎵 Frequency Tone"):
            fs = gr.Slider(1, 4000, value=NODE_HZ if NODE_HZ <= 4000 else 432, step=0.1, label="Hz")
            au = gr.Audio(label="Frequency Tone", type="numpy")
            gr.Button("Generate Tone").click(generate_tone, fs, au)
        with gr.TabItem("📊 Node Status"):
            ns = gr.Code(label="Status", language="json",
                          value=json.dumps({"node_id":NODE_ID,"role":UI_ROLE,"hz":NODE_HZ,
                                            "pioneers":PIONEERS,"sigma":SIGMA,
                                            "ts":datetime.now(timezone.utc).isoformat()},indent=2))
            gr.Button("↺ Refresh").click(
                lambda: json.dumps({"node_id":NODE_ID,"role":UI_ROLE,"hz":NODE_HZ,
                                     "pioneers":PIONEERS,"sigma":SIGMA,
                                     "ts":datetime.now(timezone.utc).isoformat()},indent=2),
                None, ns)

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
