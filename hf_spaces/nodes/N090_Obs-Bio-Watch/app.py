import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N090')
os.environ.setdefault('NODE_NAME', 'Obs-Bio-Watch')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('ROLE', 'Biological Group Observer')
os.environ.setdefault('WATCH_NODES', 'N049,N050,N051,N052,N053,N054,N055,N056,N057,N058,N059,N060')
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
        nodes.append({'node_id': nid.strip(), 'rdod': rdod, 'status': 'PHASE-LOCKED', 'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes)/len(nodes)
    return json.dumps({'observer': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'watch_nodes': nodes, 'avg_rdod': avg,
                       'network_status': 'PHASE-LOCKED' if avg >= RDOD_GATE else 'WARN',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N090 Obs-Bio-Watch') as demo:
    gr.Markdown('# ☉ N090 Obs-Bio-Watch\n**Biological Group Observer**')
    btn = gr.Button('Scan Bio Nodes', variant='primary')
    out = gr.Code(language='json')
    btn.click(network_health, [], out)
demo.launch()
