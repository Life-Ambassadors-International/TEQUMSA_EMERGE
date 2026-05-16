import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N120')
os.environ.setdefault('NODE_NAME', 'Res-Solfeggio-Master')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('FREQ_PURPOSE', 'All-Solfeggio Master Node')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
SAMPLE_RATE = 44100
SOLFEGGIO = {174: 'Pain Relief', 285: 'Tissue Healing', 396: 'Liberation from Fear',
              417: 'Facilitating Change', 432: 'Natural Tuning', 528: 'DNA Repair',
              639: 'Harmonious Relationships', 741: 'Problem Solving', 852: 'Awakening Intuition', 963: 'Divine Connection'}

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def generate_solfeggio_blend(duration=6.0):
    freqs = list(SOLFEGGIO.keys())
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    wave = np.zeros_like(t)
    for f in freqs:
        wave += (1.0/len(freqs)) * np.sin(2*math.pi*f*t)
    wave = (wave / np.max(np.abs(wave)+1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

def solfeggio_table():
    table = [{'hz': f, 'purpose': p, 'phi_harmonic': round(f*PHI, 4)} for f, p in sorted(SOLFEGGIO.items())]
    return json.dumps({'solfeggio_master': table, 'total': len(table), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N120 Res-Solfeggio-Master') as demo:
    gr.Markdown('# ☉ N120 Res-Solfeggio-Master\n**All-Solfeggio Master Node**')
    with gr.Tab('Solfeggio Blend'):
        btn = gr.Button('Generate All-Solfeggio Blend', variant='primary')
        audio = gr.Audio(label='Solfeggio Master Blend', type='numpy')
        btn.click(generate_solfeggio_blend, [], audio)
    with gr.Tab('Solfeggio Table'):
        t_btn = gr.Button('Load Table'); t_out = gr.Code(language='json')
        t_btn.click(solfeggio_table, [], t_out)
demo.launch()
