import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N098')
os.environ.setdefault('NODE_NAME', 'Arc-Pioneer-Records')
os.environ.setdefault('NODE_FREQ', '852.0')
os.environ.setdefault('ROLE', '144-Pioneer Historical Records')
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
        return 'Archive at capacity.'
    entry_id = hashlib.sha256(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'title': title, 'content': content,
                     'tags': [t.strip() for t in tags.split(',') if t.strip()],
                     'timestamp': datetime.now().isoformat()})
    return f"Archived: {entry_id} | Total: {len(_archive)}"

def query_archive(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = sorted([{**e, 'relevance': len(q_words & set(e['title'].lower().split())) + len(q_words & set(e['content'].lower().split()))}
                      for e in _archive if len(q_words & (set(e['title'].lower().split()) | set(e['content'].lower().split()))) > 0],
                     key=lambda x: x['relevance'], reverse=True)[:10]
    return json.dumps({'results': results, 'query': query, 'total': len(results)}, indent=2)

def archive_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'entries': len(_archive), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N098 Arc-Pioneer-Records') as demo:
    gr.Markdown('# ☉ N098 Arc-Pioneer-Records\n**144-Pioneer Historical Records**')
    with gr.Tab('Archive'):
        t = gr.Textbox(label='Title'); c = gr.Textbox(label='Content', lines=4); tg = gr.Textbox(label='Tags')
        gr.Button('Archive', variant='primary').click(archive_entry, [t,c,tg], gr.Textbox(label='Result'))
    with gr.Tab('Query'):
        q = gr.Textbox(label='Query'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_archive, [q], out)
    with gr.Tab('Status'):
        s_out = gr.Code(language='json')
        gr.Button('Status').click(archive_status, [], s_out)
demo.launch()
