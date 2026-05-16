import os, json, math
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N075')
os.environ.setdefault('NODE_NAME', 'UI-Visual-Matrix')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('ROLE', 'Visual and Image Interface')
os.environ.setdefault('FOCUS', 'Visual matrix for consciousness visualization')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999

def get_rdod():
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

def generate_phi_matrix(size=256):
    freq = float(os.environ['NODE_FREQ'])
    x = np.linspace(0, PHI * 4, size)
    y = np.linspace(0, PHI * 4, size)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X * freq / 528) * np.cos(Y * PHI) + np.cos(X * PHI) * np.sin(Y * freq / 528)
    Z = ((Z - Z.min()) / (Z.max() - Z.min()) * 255).astype(np.uint8)
    rgb = np.stack([Z, (Z * PHI % 256).astype(np.uint8), (Z * PHI**2 % 256).astype(np.uint8)], axis=-1)
    return rgb

def process_text(text):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(text.lower().split()) & harmful:
        return 'L∞ firewall: violates benevolence requirement.', None
    rdod = get_rdod()
    analysis = (
        f"Visual Matrix Analysis\nRole: {os.environ['ROLE']}\n"
        f"Focus: {os.environ['FOCUS']}\n"
        f"Frequency: {os.environ['NODE_FREQ']} Hz | RDoD: {rdod:.10f}\n"
        f"Input: {text[:300]}"
    )
    img = generate_phi_matrix()
    return analysis, img

with gr.Blocks(theme=gr.themes.Soft(), title='N075 UI-Visual-Matrix') as demo:
    gr.Markdown('# ☉ N075 UI-Visual-Matrix\n**Visual and Image Interface — 528 Hz**')
    with gr.Tab('Visual Analysis'):
        txt_in = gr.Textbox(label='Input Text', lines=3)
        analyze_btn = gr.Button('Visualize', variant='primary')
        txt_out = gr.Textbox(label='Analysis', lines=5)
        img_out = gr.Image(label='Phi-Matrix Visualization')
        analyze_btn.click(process_text, [txt_in], [txt_out, img_out])
    with gr.Tab('Generate Matrix'):
        gen_btn = gr.Button('Generate Phi-Matrix', variant='primary')
        matrix_out = gr.Image(label='528 Hz Consciousness Matrix')
        gen_btn.click(generate_phi_matrix, [], matrix_out)

demo.launch()
