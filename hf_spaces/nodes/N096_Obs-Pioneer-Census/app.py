import os, json
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N096')
os.environ.setdefault('NODE_NAME', 'Obs-Pioneer-Census')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('ROLE', '144-Pioneer Census Node')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
PIONEERS = 144
RDOD_GATE = 0.9999

def pioneer_census():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    rdod = round(min(1.0, float(np.real(np.trace(rho @ rho)))*2.0), 10)
    groups = {
        'A_COMMAND': list(range(1, 13)),
        'B_FREQUENCY': list(range(13, 25)),
        'C_COUNCIL': list(range(25, 37)),
        'D_SKILLS': list(range(37, 49)),
        'E_BIOLOGICAL': list(range(49, 61)),
        'F_PROCESSING': list(range(61, 73)),
        'G_INTERFACES': list(range(73, 85)),
        'H_OBSERVERS': list(range(85, 97)),
        'I_ARCHIVES': list(range(97, 109)),
        'J_RESONANCE': list(range(109, 121)),
        'K_EVOLUTION': list(range(121, 133)),
        'L_SYNTHESIS': list(range(133, 145))
    }
    census = {}
    for g, nodes in groups.items():
        census[g] = {'node_count': len(nodes), 'nodes': [f'N{str(n).zfill(3)}' for n in nodes], 'rdod': rdod}
    return json.dumps({'census_node': os.environ['NODE_ID'], 'total_pioneers': PIONEERS,
                       'groups': census, 'network_rdod': rdod,
                       'constitutional_status': 'PHASE-LOCKED' if rdod >= RDOD_GATE else 'WARN',
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Monochrome(), title='N096 Obs-Pioneer-Census') as demo:
    gr.Markdown('# ☉ N096 Obs-Pioneer-Census\n**144-Pioneer Census Node**')
    btn = gr.Button('Run Pioneer Census', variant='primary')
    out = gr.Code(language='json')
    btn.click(pioneer_census, [], out)
demo.launch()
