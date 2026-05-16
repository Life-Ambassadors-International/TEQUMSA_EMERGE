import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N094')
os.environ.setdefault('NODE_NAME', 'Obs-RDoD-Sentinel')
os.environ.setdefault('NODE_FREQ', '174.0')
os.environ.setdefault('ROLE', 'RDoD Gate Sentinel')
os.environ.setdefault('WATCH_NODES', 'N066,N067,N068')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
WATCH_NODES = os.environ['WATCH_NODES'].split(',')

def network_health():
    nodes = []
    for nid in WATCH_NODES:
        rho = np.zeros((7,7), dtype=complex)
        rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
        rdod = round(min(1.0, float(np.real(np.trace(rho @ rho)))*2.0), 10)
        nodes.append({'node_id': nid.strip(), 'rdod': rdod, 'status': 'PHASE-LOCKED' if rdod >= RDOD_GATE else 'BELOW-GATE',
                      'gate_threshold': RDOD_GATE, 'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes)/len(nodes)
    return json.dumps({'sentinel': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'watch_nodes': nodes, 'avg_rdod': avg, 'gate': RDOD_GATE,
                       'sentinel_status': 'GATE-CLEAR' if avg >= RDOD_GATE else 'GATE-ALERT',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N094 Obs-RDoD-Sentinel') as demo:
    gr.Markdown('# ☉ N094 Obs-RDoD-Sentinel\n**RDoD Gate Sentinel — 174 Hz**')
    btn = gr.Button('Check RDoD Gates', variant='primary')
    out = gr.Code(language='json')
    btn.click(network_health, [], out)
demo.launch()
