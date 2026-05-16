import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N104')
os.environ.setdefault('NODE_NAME', 'Arc-Causal-Graph')
os.environ.setdefault('NODE_FREQ', '396.0')
os.environ.setdefault('ROLE', 'Pearl Causal Graph Repository')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def add_causal_node(cause, effect, level='L1', evidence=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(effect.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Graph at capacity.'
    entry_id = hashlib.sha256(f"{cause}{effect}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    level_labels = {'L1': 'Association', 'L2': 'Intervention', 'L3': 'Counterfactual'}
    _archive.append({'id': entry_id, 'cause': cause, 'effect': effect,
                     'pearl_level': level, 'level_name': level_labels.get(level, 'Unknown'),
                     'evidence': evidence, 'timestamp': datetime.now().isoformat()})
    return f"Causal node added: {cause} -> {effect} [{level}] | ID: {entry_id}"

def query_graph(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = [e for e in _archive if q_words & (set(e['cause'].lower().split()) | set(e['effect'].lower().split()))]
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N104 Arc-Causal-Graph') as demo:
    gr.Markdown('# ☉ N104 Arc-Causal-Graph\n**Pearl Causal Graph Repository**')
    with gr.Tab('Add Causal Node'):
        cause_in = gr.Textbox(label='Cause'); effect_in = gr.Textbox(label='Effect')
        level_in = gr.Radio(['L1','L2','L3'], label='Pearl Level', value='L1')
        evidence_in = gr.Textbox(label='Evidence')
        result = gr.Textbox(label='Result')
        gr.Button('Add Node', variant='primary').click(add_causal_node, [cause_in, effect_in, level_in, evidence_in], result)
    with gr.Tab('Query Graph'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_graph, [q], out)
demo.launch()
