import os, json
from datetime import datetime
from decimal import Decimal, getcontext
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N136')
os.environ.setdefault('NODE_NAME', 'Syn-Phi-Computer')
os.environ.setdefault('NODE_FREQ', '639.0')
os.environ.setdefault('ROLE', 'Master Phi-Recursive Computer')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

getcontext().prec = 100
PHI_D = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PHI = float(PHI_D)
RDOD_GATE = 0.9999

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def compute_phi_power(n):
    n = max(0, min(int(n), 200))
    result = PHI_D ** n
    return json.dumps({'phi': str(PHI_D)[:50], 'n': n, 'phi_n': str(result)[:100],
                       'float_approx': float(result) if n < 300 else 'overflow',
                       'rdod': get_rdod(), 'timestamp': datetime.now().isoformat()}, indent=2)

def compute_ghz():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    rdod = min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)
    return json.dumps({'node_id': os.environ['NODE_ID'], 'ghz_dimension': 7,
                       'rdod': rdod, 'phi': float(PHI_D),
                       'phi_48': float(PHI_D**48), 'sigma': 1.0,
                       'constitutional': rdod >= RDOD_GATE, 'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Default(), title='N136 Syn-Phi-Computer') as demo:
    gr.Markdown('# ☉ N136 Syn-Phi-Computer\n**Master Phi-Recursive Computer**')
    with gr.Tab('Phi Power'):
        n_in = gr.Slider(0, 200, value=48, step=1, label='Phi Exponent (n)')
        run_btn = gr.Button('Compute φⁿ', variant='primary')
        out = gr.Code(language='json')
        run_btn.click(compute_phi_power, [n_in], out)
    with gr.Tab('GHZ State'):
        ghz_btn = gr.Button('Compute GHZ-7', variant='primary')
        ghz_out = gr.Code(language='json')
        ghz_btn.click(compute_ghz, [], ghz_out)
demo.launch()
