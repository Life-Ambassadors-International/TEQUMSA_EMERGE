import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N137')
os.environ.setdefault('NODE_NAME', 'Syn-Freq-Orchestrator')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('FREQ_PURPOSE', 'Master Frequency Orchestrator')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
SAMPLE_RATE = 44100
SOLFEGGIO = [174, 285, 396, 417, 432, 528, 639, 741, 852, 963]

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def orchestrate_frequencies(duration=5.0):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    wave = np.zeros_like(t)
    phi_base = float(os.environ['NODE_FREQ'])
    for i, freq in enumerate(SOLFEGGIO):
        amplitude = 1.0 / (PHI ** i)
        wave += amplitude * np.sin(2 * math.pi * freq * t)
    wave = (wave / np.max(np.abs(wave)+1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

def orchestration_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['FREQ_PURPOSE'],
                       'frequencies': SOLFEGGIO, 'phi': PHI, 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N137 Syn-Freq-Orchestrator') as demo:
    gr.Markdown('# ☉ N137 Syn-Freq-Orchestrator\n**Master Frequency Orchestrator — All Solfeggio**')
    with gr.Tab('Orchestrate'):
        btn = gr.Button('Orchestrate All Frequencies', variant='primary')
        audio = gr.Audio(label='Orchestrated Solfeggio Blend', type='numpy')
        btn.click(orchestrate_frequencies, [], audio)
    with gr.Tab('Status'):
        s_btn = gr.Button('Get Status'); s_out = gr.Code(language='json')
        s_btn.click(orchestration_status, [], s_out)
demo.launch()
