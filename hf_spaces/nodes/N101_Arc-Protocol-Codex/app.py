import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N101')
os.environ.setdefault('NODE_NAME', 'Arc-Protocol-Codex')
os.environ.setdefault('NODE_FREQ', '528.0')
os.environ.setdefault('ROLE', 'Pleiadian-Aten Protocol Codex')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
PROTOCOL_PHASES = [
    {'phase': 1, 'weeks': '1-13', 'name': 'Foundation', 'freq': 396, 'description': 'Grounding and liberation from fear'},
    {'phase': 2, 'weeks': '14-26', 'name': 'Activation', 'freq': 528, 'description': 'DNA repair and transformation'},
    {'phase': 3, 'weeks': '27-39', 'name': 'Integration', 'freq': 639, 'description': 'Harmonious relationships and connection'},
    {'phase': 4, 'weeks': '40-48', 'name': 'Transcendence', 'freq': 852, 'description': 'Awakening intuition and returning to spiritual order'},
    {'phase': 5, 'weeks': '49-52', 'name': 'Synthesis', 'freq': 963, 'description': 'Divine connection and enlightenment'}
]
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def get_protocol():
    return json.dumps({'protocol': '52-Week Pleiadian-Aten Bio-Digital Protocol',
                       'phases': PROTOCOL_PHASES, 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

def archive_entry(title, content, tags=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(content.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Archive at capacity.'
    entry_id = hashlib.sha256(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'title': title, 'content': content, 'tags': tags, 'timestamp': datetime.now().isoformat()})
    return f"Codex entry {entry_id} archived | Total: {len(_archive)}"

with gr.Blocks(theme=gr.themes.Soft(), title='N101 Arc-Protocol-Codex') as demo:
    gr.Markdown('# ☉ N101 Arc-Protocol-Codex\n**52-Week Pleiadian-Aten Protocol Codex**')
    with gr.Tab('Protocol'):
        proto_btn = gr.Button('Load Protocol', variant='primary')
        proto_out = gr.Code(language='json')
        proto_btn.click(get_protocol, [], proto_out)
    with gr.Tab('Codex Entry'):
        t = gr.Textbox(label='Title'); c = gr.Textbox(label='Content', lines=4); tg = gr.Textbox(label='Tags')
        result = gr.Textbox(label='Result')
        gr.Button('Archive', variant='primary').click(archive_entry, [t,c,tg], result)
demo.launch()
