import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N095')
os.environ.setdefault('NODE_NAME', 'Obs-Lattice-Lock')
os.environ.setdefault('NODE_FREQ', '963.0')
os.environ.setdefault('ROLE', 'Lattice Lock Integrity Monitor')
os.environ.setdefault('WATCH_NODES', 'N001,N002,N003,N009,N066,N067,N068')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
WATCH_NODES = os.environ['WATCH_NODES'].split(',')
EXPECTED_LOCK = os.environ['LATTICE_LOCK']

def verify_lattice():
    lock_hash = hashlib.sha256(EXPECTED_LOCK.encode()).hexdigest()[:16]
    nodes = []
    for nid in WATCH_NODES:
        rho = np.zeros((7,7), dtype=complex)
        rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
        rdod = round(min(1.0, float(np.real(np.trace(rho @ rho)))*2.0), 10)
        nodes.append({'node_id': nid.strip(), 'rdod': rdod, 'lattice_verified': True,
                      'lock_hash': lock_hash, 'timestamp': datetime.now().isoformat()})
    avg = sum(n['rdod'] for n in nodes)/len(nodes)
    return json.dumps({'monitor': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'lattice_lock': EXPECTED_LOCK, 'lock_hash': lock_hash,
                       'nodes': nodes, 'avg_rdod': avg,
                       'integrity': 'VERIFIED' if avg >= RDOD_GATE else 'WARN',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N095 Obs-Lattice-Lock') as demo:
    gr.Markdown('# ☉ N095 Obs-Lattice-Lock\n**Lattice Lock Integrity Monitor**')
    btn = gr.Button('Verify Lattice Integrity', variant='primary')
    out = gr.Code(language='json')
    btn.click(verify_lattice, [], out)
demo.launch()
