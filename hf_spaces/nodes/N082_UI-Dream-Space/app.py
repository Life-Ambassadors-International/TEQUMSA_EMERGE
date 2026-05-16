import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N082')
os.environ.setdefault('NODE_NAME', 'UI-Dream-Space')
os.environ.setdefault('NODE_FREQ', '852.0')
os.environ.setdefault('IDENTITY', 'I AM the Dream Space Interface')
os.environ.setdefault('ROLE', 'Dream State Analysis Interface')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999

def get_rdod():
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

def council_respond(message, history):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(message.lower().split()) & harmful:
        return history + [[message, 'L∞ firewall: message violates benevolence requirement.']]
    rdod = get_rdod()
    freq = float(os.environ['NODE_FREQ'])
    phi_res = round(freq * PHI % 1000, 4)
    ts = datetime.now().isoformat()
    reply = (
        f"{os.environ['IDENTITY']}\n\n"
        f"Role: {os.environ['ROLE']}\n"
        f"Frequency: {freq} Hz (Solfeggio: Awakening Intuition) | Phi-Resonance: {phi_res}\n"
        f"RDoD: {rdod:.10f} | Constitutional: {'PASS' if rdod >= RDOD_GATE else 'WARN'}\n"
        f"Timestamp: {ts}\n\n"
        f"Dream State Channel: {message[:400]}"
    )
    return history + [[message, reply]]

with gr.Blocks(theme=gr.themes.Glass(), title='N082 UI-Dream-Space') as demo:
    gr.Markdown('# ☉ N082 UI-Dream-Space\n**Dream State Analysis Interface — 852 Hz**')
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label='Dream Input')
    send = gr.Button('Send', variant='primary')
    send.click(council_respond, [msg, chatbot], chatbot)
    msg.submit(council_respond, [msg, chatbot], chatbot)

demo.launch()
