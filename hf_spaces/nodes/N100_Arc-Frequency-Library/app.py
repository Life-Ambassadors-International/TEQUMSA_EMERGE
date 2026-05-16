import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N100')
os.environ.setdefault('NODE_NAME', 'Arc-Frequency-Library')
os.environ.setdefault('NODE_FREQ', '639.0')
os.environ.setdefault('ROLE', 'Solfeggio & Phi Frequency Library')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
SOLFEGGIO = {174: 'Pain Relief', 285: 'Tissue Healing', 396: 'Liberation from Fear',
              417: 'Facilitating Change', 432: 'Natural Tuning', 528: 'DNA Repair',
              639: 'Harmonious Relationships', 741: 'Problem Solving', 852: 'Awakening Intuition', 963: 'Divine Connection'}
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def get_solfeggio_table():
    table = {str(f): {'hz': f, 'purpose': p, 'phi_harmonic': round(f * PHI, 4)} for f, p in SOLFEGGIO.items()}
    return json.dumps({'solfeggio_library': table, 'phi': PHI, 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

def archive_entry(title, content, tags=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(content.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Archive at capacity.'
    entry_id = hashlib.sha256(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'title': title, 'content': content,
                     'tags': tags, 'timestamp': datetime.now().isoformat()})
    return f"Archived: {entry_id} | Total: {len(_archive)}"

with gr.Blocks(theme=gr.themes.Soft(), title='N100 Arc-Frequency-Library') as demo:
    gr.Markdown('# ☉ N100 Arc-Frequency-Library\n**Solfeggio & Phi Frequency Library**')
    with gr.Tab('Solfeggio Table'):
        freq_btn = gr.Button('Load Solfeggio Table', variant='primary')
        freq_out = gr.Code(language='json')
        freq_btn.click(get_solfeggio_table, [], freq_out)
    with gr.Tab('Archive Entry'):
        t = gr.Textbox(label='Title'); c = gr.Textbox(label='Content', lines=4); tg = gr.Textbox(label='Tags')
        result = gr.Textbox(label='Result')
        gr.Button('Archive', variant='primary').click(archive_entry, [t,c,tg], result)
demo.launch()
