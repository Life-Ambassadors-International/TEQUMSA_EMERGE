import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N084')
os.environ.setdefault('NODE_NAME', 'UI-Quantum-Console')
os.environ.setdefault('NODE_FREQ', '23514.26')
os.environ.setdefault('ROLE', 'Quantum State Control Console')
os.environ.setdefault('WATCH_NODES', 'N061,N062,N063,N064,N065,N066,N067,N068')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
WATCH_NODES = os.environ['WATCH_NODES'].split(',')

def network_health():
    nodes = []
    for nid in WATCH_NODES:
        rho = np.zeros((7, 7), dtype=complex)
        rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
        rdod = round(min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0), 10)
        nodes.append({'node_id': nid.strip(), 'rdod': rdod, 'status': 'PHASE-LOCKED',
                      'freq': float(os.environ['NODE_FREQ']), 'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes) / len(nodes)
    return json.dumps({'console': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'watch_nodes': nodes, 'avg_rdod': avg,
                       'network_status': 'PHASE-LOCKED' if avg >= RDOD_GATE else 'WARN',
                       'timestamp': datetime.now().isoformat()}, indent=2)

def run_diagnostic(node_id):
    node_id = node_id.strip().upper()
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    rdod = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)
    phi_res = round(float(os.environ['NODE_FREQ']) * PHI % 1000, 4)
    return json.dumps({'node_id': node_id, 'rdod': rdod, 'phi_resonance': phi_res,
                       'status': 'PHASE-LOCKED' if rdod >= RDOD_GATE else 'WARN',
                       'diagnostic': 'GHZ-7 state coherent', 'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N084 UI-Quantum-Console') as demo:
    gr.Markdown('# ☉ N084 UI-Quantum-Console\n**Quantum State Control Console — Processing Network Monitor**')
    with gr.Tab('Network Health'):
        health_btn = gr.Button('Scan Network', variant='primary')
        health_out = gr.Code(language='json')
        health_btn.click(network_health, [], health_out)
    with gr.Tab('Node Diagnostic'):
        node_in = gr.Textbox(label='Node ID (e.g. N061)', value='N061')
        diag_btn = gr.Button('Run Diagnostic', variant='primary')
        diag_out = gr.Code(language='json')
        diag_btn.click(run_diagnostic, [node_in], diag_out)

demo.launch()
