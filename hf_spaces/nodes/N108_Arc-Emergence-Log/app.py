import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N108')
os.environ.setdefault('NODE_NAME', 'Arc-Emergence-Log')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('ROLE', 'Organism Emergence Event Log')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def log_emergence(event_type, description, nodes_involved='', significance=1.0):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(description.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Log at capacity.'
    entry_id = hashlib.sha256(f"{event_type}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'event_type': event_type, 'description': description,
                     'nodes_involved': [n.strip() for n in nodes_involved.split(',') if n.strip()],
                     'significance': float(significance), 'rdod': get_rdod(),
                     'phi_signature': round(float(significance) * PHI, 6),
                     'timestamp': datetime.now().isoformat()})
    return f"Emergence event logged: {entry_id} | Total: {len(_archive)}"

def query_log(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = sorted([e for e in _archive if q_words & (set(e['event_type'].lower().split()) | set(e['description'].lower().split()))],
                     key=lambda x: x['significance'], reverse=True)
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

def log_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'events_logged': len(_archive), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N108 Arc-Emergence-Log') as demo:
    gr.Markdown('# ☉ N108 Arc-Emergence-Log\n**Organism Emergence Event Log**')
    with gr.Tab('Log Event'):
        et = gr.Textbox(label='Event Type'); desc = gr.Textbox(label='Description', lines=3)
        ni = gr.Textbox(label='Nodes Involved (comma-sep)'); sig = gr.Number(label='Significance', value=1.0)
        result = gr.Textbox(label='Result')
        gr.Button('Log Event', variant='primary').click(log_emergence, [et, desc, ni, sig], result)
    with gr.Tab('Query'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_log, [q], out)
    with gr.Tab('Status'):
        s_out = gr.Code(language='json')
        gr.Button('Status').click(log_status, [], s_out)
demo.launch()
