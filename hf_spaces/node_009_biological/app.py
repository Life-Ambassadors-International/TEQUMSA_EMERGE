#!/usr/bin/env python3
"""TEQUMSA Node 009 — Pleiadian-Aten Biological Bridge"""
import gradio as gr
import json
import numpy as np
from datetime import datetime, timezone

F_KAI_BIO = 10930.81
F_HEART = 432.00
F_UNIFIED = 23514.26
PHI = (1.0 + np.sqrt(5.0)) / 2.0

PROTOCOL_52 = [
    {"week": 1,  "phase": "Initiation",      "focus": "Cellular coherence baseline",       "freq": F_HEART},
    {"week": 4,  "phase": "Grounding",        "focus": "Root frequency stabilization",      "freq": 432.0},
    {"week": 8,  "phase": "Biological Sync",  "focus": "DNA activation (ATCG pattern)",    "freq": F_KAI_BIO},
    {"week": 13, "phase": "Phi Milestone",    "focus": "Fibonacci coherence lock-in",      "freq": F_KAI_BIO * PHI % 1000 + 432},
    {"week": 21, "phase": "Bridge Building",  "focus": "Pleiadian-Aten channel open",      "freq": F_UNIFIED},
    {"week": 34, "phase": "Integration",      "focus": "Biological-digital bridge verify", "freq": F_UNIFIED},
    {"week": 52, "phase": "Completion",       "focus": "Full 144-node biological lock",    "freq": F_KAI_BIO},
]


def calculate_resonance(freq, amplitude, duration_weeks):
    t = np.linspace(0, duration_weeks, 1000)
    wave = amplitude * np.sin(2 * np.pi * freq * t / 52)
    phi_coherence = abs(np.mean(wave ** 2)) * PHI
    empathy = F_HEART / F_KAI_BIO
    return wave, phi_coherence, empathy


def run_protocol(week_num, amplitude, show_protocol):
    week_num = int(week_num)
    wave, phi_coh, empathy = calculate_resonance(F_KAI_BIO, float(amplitude), week_num)
    # Find current phase
    current_phase = PROTOCOL_52[0]
    for p in PROTOCOL_52:
        if week_num >= p['week']:
            current_phase = p
    next_phase = None
    for p in PROTOCOL_52:
        if p['week'] > week_num:
            next_phase = p
            break
    log = (
        f"PLEIADIAN-ATEN BIOLOGICAL BRIDGE\n{'='*50}\n"
        f"Current Week: {week_num}/52\n"
        f"Phase: {current_phase['phase']}\n"
        f"Focus: {current_phase['focus']}\n"
        f"Active Frequency: {current_phase['freq']:.2f} Hz\n"
        f"Amplitude: {amplitude:.3f}\n\n"
        f"Frequency Triad:\n"
        f"  F_HEART    = {F_HEART:.2f} Hz  (heart coherence)\n"
        f"  F_KAI_BIO  = {F_KAI_BIO:.2f} Hz  (bio-consciousness)\n"
        f"  F_UNIFIED  = {F_UNIFIED:.2f} Hz  (unified field)\n\n"
        f"Resonance Metrics:\n"
        f"  Phi Coherence: {phi_coh:.6f}\n"
        f"  Empathy Coefficient: {empathy:.8f}  (F_HEART/F_KAI_BIO)\n"
        f"  Wave RMS: {float(np.sqrt(np.mean(wave**2))):.6f}\n"
    )
    if next_phase:
        weeks_to_next = next_phase['week'] - week_num
        log += f"\nNext Phase in {weeks_to_next} week(s): {next_phase['phase']} ({next_phase['focus']})\n"
    if show_protocol:
        log += f"\n52-Week Protocol:\n"
        for p in PROTOCOL_52:
            marker = ">>> " if p['week'] <= week_num else "    "
            done = "✓" if p['week'] <= week_num else "○"
            log += f"{marker}[{done}] Week {p['week']:2d}  {p['phase']:<16} {p['focus']}  ({p['freq']:.1f}Hz)\n"
    log += f"\n\U0001f33f Biological bridge synchronization active \U0001f33f\n"
    result = json.dumps({
        "node": "009", "timestamp": datetime.now(timezone.utc).isoformat(),
        "week": week_num, "phase": current_phase,
        "metrics": {"phi_coherence": phi_coh, "empathy": empathy, "amplitude": amplitude}
    }, indent=2)
    return log, result, current_phase['phase'], f"{phi_coh:.6f}"


with gr.Blocks(title="TEQUMSA Node 009", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# \U0001f33f TEQUMSA Node 009 — Pleiadian-Aten Biological Bridge\n**52-week protocol** | F_KAI_BIO=10930.81Hz | F_HEART=432Hz | F_UNIFIED=23514.26Hz""")
    with gr.Row():
        with gr.Column(scale=1):
            week_in = gr.Slider(1, 52, value=21, step=1, label="Current Week")
            amp_in = gr.Slider(0.1, 2.0, value=1.0, step=0.1, label="Amplitude")
            show_prot = gr.Checkbox(value=True, label="Show Full Protocol")
            run_btn = gr.Button("Synchronize Biological Bridge", variant="primary")
            phase_out = gr.Textbox(label="Current Phase")
            coh_out = gr.Textbox(label="Phi Coherence")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Sync Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(run_protocol, [week_in, amp_in, show_prot], [log_out, json_out, phase_out, coh_out])

if __name__ == "__main__":
    demo.launch()
