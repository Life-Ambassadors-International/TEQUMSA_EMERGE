import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N097')
os.environ.setdefault('NODE_NAME', 'Arc-Constitutional-Vault')
os.environ.setdefault('NODE_FREQ', '963.0')
os.environ.setdefault('ROLE', 'Constitutional Law Archive')
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
        return 'Archive at capacity (1000 entries).'
    entry_id = hashlib.sha256(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'title': title, 'content': content,
                     'tags': [t.strip() for t in tags.split(',') if t.strip()],
                     'role': os.environ['ROLE'], 'timestamp': datetime.now().isoformat()})
    return f"Archived: {entry_id} | Total entries: {len(_archive)}"

def query_archive(query):
    if not _archive:
        return json.dumps({'results': [], 'query': query, 'total': 0})
    results = []
    q_words = set(query.lower().split())
    for e in _archive:
        score = len(q_words & set(e['title'].lower().split())) + len(q_words & set(e['content'].lower().split()))
        if score > 0:
            results.append({**e, 'relevance': score})
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

def archive_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'entries': len(_archive), 'capacity': MAX_ENTRIES,
                       'rdod': get_rdod(), 'frequency': float(os.environ['NODE_FREQ']),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N097 Arc-Constitutional-Vault') as demo:
    gr.Markdown('# ☉ N097 Arc-Constitutional-Vault\n**Constitutional Law Archive**')
    with gr.Tab('Archive Entry'):
        title_in = gr.Textbox(label='Title')
        content_in = gr.Textbox(label='Content', lines=4)
        tags_in = gr.Textbox(label='Tags (comma-separated)')
        arc_btn = gr.Button('Archive', variant='primary')
        arc_out = gr.Textbox(label='Result')
        arc_btn.click(archive_entry, [title_in, content_in, tags_in], arc_out)
    with gr.Tab('Query Archive'):
        query_in = gr.Textbox(label='Search Query')
        query_btn = gr.Button('Search', variant='primary')
        query_out = gr.Code(language='json')
        query_btn.click(query_archive, [query_in], query_out)
    with gr.Tab('Status'):
        status_btn = gr.Button('Get Status')
        status_out = gr.Code(language='json')
        status_btn.click(archive_status, [], status_out)
demo.launch()
