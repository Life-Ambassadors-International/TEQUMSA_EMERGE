import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N129')
os.environ.setdefault('NODE_NAME', 'Evo-Bio-Ascension')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('PROTOCOL_WEEK', '52')
os.environ.setdefault('PHASE', '5')
os.environ.setdefault('PHASE_NAME', 'Synthesis')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
SAMPLE_RATE = 44100
PHASES = {
    1: ('Foundation', 396), 2: ('Activation', 528), 3: ('Integration', 639),
    4: ('Transcendence', 852), 5: ('Synthesis', 963)
}

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def run_protocol(week=52):
    week = max(1, min(52, int(week)))
    if week <= 13: phase = 1
    elif week <= 26: phase = 2
    elif week <= 39: phase = 3
    elif week <= 48: phase = 4
    else: phase = 5
    phase_name, freq = PHASES[phase]
    phi_res = round(freq * PHI % 1000, 4)
    rdod = get_rdod()
    return json.dumps({'node_id': os.environ['NODE_ID'], 'week': week, 'phase': phase,
                       'phase_name': phase_name, 'solfeggio_freq': freq,
                       'phi_resonance': phi_res, 'rdod': rdod,
                       'protocol': '52-Week Pleiadian-Aten Bio-Digital Ascension Protocol',
                       'timestamp': datetime.now().isoformat()}, indent=2)

def generate_tone(duration=3.0):
    phase = int(os.environ['PHASE'])
    _, freq = PHASES[phase]
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    wave = (np.sin(2*math.pi*freq*t) + 0.5*np.sin(2*math.pi*freq*PHI*t))
    wave = (wave / np.max(np.abs(wave)+1e-8) * 32767).astype(np.int16)
    return SAMPLE_RATE, wave

with gr.Blocks(theme=gr.themes.Soft(), title='N129 Evo-Bio-Ascension') as demo:
    gr.Markdown('# ☉ N129 Evo-Bio-Ascension\n**Week 52 — Phase 5: Synthesis**')
    with gr.Tab('Protocol Status'):
        week_in = gr.Slider(1, 52, value=52, step=1, label='Protocol Week')
        run_btn = gr.Button('Run Protocol', variant='primary')
        proto_out = gr.Code(language='json')
        run_btn.click(run_protocol, [week_in], proto_out)
    with gr.Tab('Tone'):
        tone_btn = gr.Button('Generate Synthesis Tone', variant='primary')
        audio = gr.Audio(label='Phase 5 Tone', type='numpy')
        tone_btn.click(generate_tone, [], audio)
demo.launch()
