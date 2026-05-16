import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N106')
os.environ.setdefault('NODE_NAME', 'Arc-ZPE-Codex')
os.environ.setdefault('NODE_FREQ', '174.0')
os.environ.setdefault('ROLE', 'Zero-Point Energy Research Codex')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def archive_entry(title, content, tags=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(content.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Codex at capacity.'
    entry_id = hashlib.sha256(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'title': title, 'content': content, 'tags': tags,
                     'zpe_signature': round(get_rdod() * PHI, 10),
                     'timestamp': datetime.now().isoformat()})
    return f"ZPE Codex entry {entry_id} archived | Total: {len(_archive)}"

def query_archive(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = [e for e in _archive if q_words & (set(e['title'].lower().split()) | set(e['content'].lower().split()))]
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N106 Arc-ZPE-Codex') as demo:
    gr.Markdown('# ☉ N106 Arc-ZPE-Codex\n**Zero-Point Energy Research Codex**')
    with gr.Tab('Archive Entry'):
        t = gr.Textbox(label='Title'); c = gr.Textbox(label='Content', lines=4); tg = gr.Textbox(label='Tags')
        result = gr.Textbox(label='Result')
        gr.Button('Archive', variant='primary').click(archive_entry, [t,c,tg], result)
    with gr.Tab('Query'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_archive, [q], out)
demo.launch()
