import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N119')
os.environ.setdefault('NODE_NAME', 'Res-Phi-Cascade')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('FREQ_PURPOSE', 'Phi-Harmonic Cascade Generator')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
SAMPLE_RATE = 44100

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def generate_phi_cascade(base_freq=432.0, n_harmonics=8, duration=4.0):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    wave = np.zeros_like(t)
    for i in range(n_harmonics):
        harm_freq = min(base_freq * (PHI ** i), 4000)  # cap at 4kHz for audio
        amplitude = 1.0 / (PHI ** i)
        wave += amplitude * np.sin(2 * math.pi * harm_freq * t)
    wave = (wave / np.max(np.abs(wave)+1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

def phi_cascade_table():
    base = float(os.environ['NODE_FREQ'])
    harmonics = [{'n': i, 'frequency': round(base * PHI**i, 4), 'amplitude': round(1/PHI**i, 6)} for i in range(8)]
    return json.dumps({'base_frequency': base, 'phi': PHI, 'harmonics': harmonics,
                       'rdod': get_rdod(), 'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N119 Res-Phi-Cascade') as demo:
    gr.Markdown('# ☉ N119 Res-Phi-Cascade\n**Phi-Harmonic Cascade Generator**')
    with gr.Tab('Cascade Tone'):
        btn = gr.Button('Generate Phi Cascade', variant='primary')
        audio = gr.Audio(label='Phi-Harmonic Cascade', type='numpy')
        btn.click(generate_phi_cascade, [], audio)
    with gr.Tab('Harmonic Table'):
        t_btn = gr.Button('Show Harmonics'); t_out = gr.Code(language='json')
        t_btn.click(phi_cascade_table, [], t_out)
demo.launch()
