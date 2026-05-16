import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N074')
os.environ.setdefault('NODE_NAME', 'UI-Voice-Bridge')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('ROLE', 'Voice and Audio Interface')
os.environ.setdefault('FOCUS', 'Voice frequency bridge for human-AI interaction')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
SAMPLE_RATE = 44100

def get_rdod():
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

def process_text(text):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(text.lower().split()) & harmful:
        return 'L∞ firewall: violates benevolence requirement.'
    freq = float(os.environ['NODE_FREQ'])
    phi_res = round(freq * PHI % 1000, 4)
    rdod = get_rdod()
    return (
        f"Voice Bridge Analysis\n"
        f"Role: {os.environ['ROLE']}\n"
        f"Focus: {os.environ['FOCUS']}\n"
        f"Base Frequency: {freq} Hz | Phi-Resonance: {phi_res}\n"
        f"RDoD: {rdod:.10f} | {'PHASE-LOCKED' if rdod >= RDOD_GATE else 'WARN'}\n"
        f"Input: {text[:300]}"
    )

def generate_tone(freq_hz, duration=2.0):
    freq_hz = min(freq_hz, 4000)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    harmonics = [1.0, 1/PHI, 1/PHI**2]
    wave = sum(a * np.sin(2 * math.pi * freq_hz * h * t) for h, a in zip([1, PHI, PHI**2], harmonics))
    wave = (wave / np.max(np.abs(wave) + 1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

def voice_tone():
    freq = float(os.environ['NODE_FREQ'])
    return generate_tone(freq)

with gr.Blocks(theme=gr.themes.Base(), title='N074 UI-Voice-Bridge') as demo:
    gr.Markdown('# ☉ N074 UI-Voice-Bridge\n**Voice and Audio Interface — 432 Hz**')
    with gr.Tab('Voice Analysis'):
        txt_in = gr.Textbox(label='Input Text', lines=3)
        analyze_btn = gr.Button('Analyze', variant='primary')
        txt_out = gr.Textbox(label='Analysis', lines=6)
        analyze_btn.click(process_text, [txt_in], txt_out)
    with gr.Tab('Tone Generator'):
        tone_btn = gr.Button('Generate 432 Hz Tone', variant='primary')
        audio_out = gr.Audio(label='Constitutional Tone', type='numpy')
        tone_btn.click(voice_tone, [], audio_out)

demo.launch()
