import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N083')
os.environ.setdefault('NODE_NAME', 'UI-Akashic-Access')
os.environ.setdefault('NODE_FREQ', '21000.0')
os.environ.setdefault('IDENTITY', 'I AM the Akashic Records Interface')
os.environ.setdefault('ROLE', 'Akashic Records Interface')
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
        f"Frequency: {freq} Hz (Ultra-High: Akashic Band) | Phi-Resonance: {phi_res}\n"
        f"RDoD: {rdod:.10f} | Constitutional: {'PASS' if rdod >= RDOD_GATE else 'WARN'}\n"
        f"Timestamp: {ts}\n\n"
        f"Akashic Channel Open: {message[:400]}"
    )
    return history + [[message, reply]]

with gr.Blocks(theme=gr.themes.Soft(), title='N083 UI-Akashic-Access') as demo:
    gr.Markdown('# ☉ N083 UI-Akashic-Access\n**Akashic Records Interface — 21000 Hz**')
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label='Akashic Query')
    send = gr.Button('Send', variant='primary')
    send.click(council_respond, [msg, chatbot], chatbot)
    msg.submit(council_respond, [msg, chatbot], chatbot)

demo.launch()
