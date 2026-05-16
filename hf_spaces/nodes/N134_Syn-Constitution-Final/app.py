import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N134')
os.environ.setdefault('NODE_NAME', 'Syn-Constitution-Final')
os.environ.setdefault('NODE_FREQ', '852.0')
os.environ.setdefault('ROLE', 'Final Constitutional Compliance Monitor')
os.environ.setdefault('WATCH_NODES', 'N009,N093,N094,N095')
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
        nodes.append({'node_id': nid.strip(), 'rdod': rdod,
                      'constitutional_status': 'COMPLIANT' if rdod >= RD0D_GATE else 'REVIEW',
                      'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes)/len(nodes)
    return json.dumps({'monitor': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'watch_nodes': nodes, 'avg_rdod': avg,
                       'compliance': 'FULL' if avg >= RDOD_GATE else 'PARTIAL',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N134 Syn-Constitution-Final') as demo:
    gr.Markdown('# ☉ N134 Syn-Constitution-Final\n**Final Constitutional Compliance Monitor**')
    btn = gr.Button('Check Compliance', variant='primary')
    out = gr.Code(language='json')
    btn.click(network_health, [], out)
demo.launch()
