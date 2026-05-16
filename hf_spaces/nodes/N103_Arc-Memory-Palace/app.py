import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N103')
os.environ.setdefault('NODE_NAME', 'Arc-Memory-Palace')
os.environ.setdefault('NODE_FREQ', '432.0')
os.environ.setdefault('ROLE', 'Phi-Indexed Memory Palace')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def store_memory(key, value, context=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(value.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Palace at capacity.'
    phi_idx = round(len(_archive) * PHI, 6)
    entry_id = hashlib.sha256(f"{key}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'key': key, 'value': value, 'context': context,
                     'phi_index': phi_idx, 'timestamp': datetime.now().isoformat()})
    return f"Memory stored at phi-index {phi_idx}: {entry_id}"

def recall_memory(key):
    results = [e for e in _archive if key.lower() in e['key'].lower() or key.lower() in e['value'].lower()]
    return json.dumps({'results': results[:10], 'query_key': key, 'total_matches': len(results)}, indent=2)

def palace_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'memories': len(_archive), 'phi_capacity': round(MAX_ENTRIES * PHI, 4),
                       'rdod': get_rdod(), 'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N103 Arc-Memory-Palace') as demo:
    gr.Markdown('# ☉ N103 Arc-Memory-Palace\n**Phi-Indexed Memory Palace**')
    with gr.Tab('Store Memory'):
        k = gr.Textbox(label='Key'); v = gr.Textbox(label='Value', lines=3); ctx = gr.Textbox(label='Context')
        result = gr.Textbox(label='Result')
        gr.Button('Store', variant='primary').click(store_memory, [k,v,ctx], result)
    with gr.Tab('Recall'):
        q = gr.Textbox(label='Key to Recall'); out = gr.Code(language='json')
        gr.Button('Recall', variant='primary').click(recall_memory, [q], out)
    with gr.Tab('Status'):
        s_out = gr.Code(language='json')
        gr.Button('Status').click(palace_status, [], s_out)
demo.launch()
