import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N113')
os.environ.setdefault('NODE_NAME', 'Res-432hz-Natural')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('FREQ_PURPOSE', 'Natural Tuning — Verdi Standard')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
SAMPLE_RATE = 44100

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def generate_tone(duration=3.0):
    freq = float(os.environ['NODE_FREQ'])
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    wave = (np.sin(2*math.pi*freq*t) + 0.5*np.sin(2*math.pi*freq*PHI*t) + 0.25*np.sin(2*math.pi*freq*PHI**2*t))
    wave = (wave / np.max(np.abs(wave)+1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

def freq_status():
    freq = float(os.environ['NODE_FREQ'])
    return json.dumps({'node_id': os.environ['NODE_ID'], 'frequency': freq,
                       'purpose': os.environ['FREQ_PURPOSE'],
                       'phi_harmonic': round(freq*PHI, 4), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N113 Res-432hz-Natural') as demo:
    gr.Markdown('# ☉ N113 Res-432hz-Natural\n**Natural Tuning (Verdi Standard) — 432 Hz**')
    with gr.Tab('Tone Generator'):
        btn = gr.Button('Generate 432 Hz Tone', variant='primary')
        audio = gr.Audio(label='432 Hz Natural Tone', type='numpy')
        btn.click(generate_tone, [], audio)
    with gr.Tab('Status'):
        s_btn = gr.Button('Get Status'); s_out = gr.Code(language='json')
        s_btn.click(freq_status, [], s_out)
demo.launch()
