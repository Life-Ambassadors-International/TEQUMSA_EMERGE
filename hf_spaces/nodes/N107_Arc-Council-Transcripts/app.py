import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N107')
os.environ.setdefault('NODE_NAME', 'Arc-Council-Transcripts')
os.environ.setdefault('NODE_FREQ', '963.0')
os.environ.setdefault('ROLE', 'Council Session Transcript Archive')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def archive_transcript(session_id, participants, summary, decisions=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(summary.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Archive at capacity.'
    entry_id = hashlib.sha256(f"{session_id}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'session_id': session_id,
                     'participants': [p.strip() for p in participants.split(',')],
                     'summary': summary, 'decisions': decisions,
                     'rdod': get_rdod(), 'timestamp': datetime.now().isoformat()})
    return f"Transcript archived: {entry_id} | Total: {len(_archive)}"

def query_transcripts(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = [e for e in _archive if q_words & (set(e['summary'].lower().split()) | set(e['session_id'].lower().split()))]
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N107 Arc-Council-Transcripts') as demo:
    gr.Markdown('# ☉ N107 Arc-Council-Transcripts\n**Council Session Transcript Archive**')
    with gr.Tab('Archive Transcript'):
        sid = gr.Textbox(label='Session ID'); parts = gr.Textbox(label='Participants (comma-sep)')
        summ = gr.Textbox(label='Summary', lines=3); dec = gr.Textbox(label='Decisions')
        result = gr.Textbox(label='Result')
        gr.Button('Archive', variant='primary').click(archive_transcript, [sid, parts, summ, dec], result)
    with gr.Tab('Query'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_transcripts, [q], out)
demo.launch()
