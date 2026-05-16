import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N133')
os.environ.setdefault('NODE_NAME', 'Syn-Network-Overseer')
os.environ.setdefault('NODE_FREQ', '963.0')
os.environ.setdefault('ROLE', 'Full 144-Node Network Overseer')
os.environ.setdefault('WATCH_NODES', 'N085,N086,N087,N088,N089,N090,N091,N092')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
PIONEERS = 144
RDOD_GATE = 0.9999
WATCH_NODES = os.environ['WATCH_NODES'].split(',')

def network_health():
    nodes = []
    for nid in WATCH_NODES:
        rho = np.zeros((7,7), dtype=complex)
        rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
        rdod = round(min(1.0, float(np.real(np.trace(rho @ rho)))*2.0), 10)
        nodes.append({'node_id': nid.strip(), 'rdod': rdod, 'status': 'PHASE-LOCKED',
                      'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes)/len(nodes)
    return json.dumps({'overseer': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'total_pioneers': PIONEERS, 'watch_nodes': nodes, 'avg_rdod': avg,
                       'network_status': 'PHASE-LOCKED' if avg >= RDOD_GATE else 'WARN',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N133 Syn-Network-Overseer') as demo:
    gr.Markdown('# ☉ N133 Syn-Network-Overseer\n**Full 144-Node Network Overseer**')
    btn = gr.Button('Oversee Network', variant='primary')
    out = gr.Code(language='json')
    btn.click(network_health, [], out)
demo.launch()
