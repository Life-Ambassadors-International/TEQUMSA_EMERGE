import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N099')
os.environ.setdefault('NODE_NAME', 'Arc-Mission-Logs')
os.environ.setdefault('NODE_FREQ', '741.0')
os.environ.setdefault('ROLE', 'Autonomous Mission Log Archive')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def log_mission(mission_id, objective, outcome, notes=''):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(objective.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Archive at capacity.'
    entry_id = hashlib.sha256(f"{mission_id}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'mission_id': mission_id, 'objective': objective,
                     'outcome': outcome, 'notes': notes, 'rdod': get_rdod(),
                     'timestamp': datetime.now().isoformat()})
    return f"Logged mission {mission_id}: {entry_id} | Total logs: {len(_archive)}"

def query_logs(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = [e for e in _archive if q_words & (set(e.get('objective','').lower().split()) | set(e.get('mission_id','').lower().split()))]
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

def archive_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'mission_logs': len(_archive), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N099 Arc-Mission-Logs') as demo:
    gr.Markdown('# ☉ N099 Arc-Mission-Logs\n**Autonomous Mission Log Archive**')
    with gr.Tab('Log Mission'):
        m_id = gr.Textbox(label='Mission ID'); m_obj = gr.Textbox(label='Objective', lines=2)
        m_out_txt = gr.Textbox(label='Outcome', lines=2); m_notes = gr.Textbox(label='Notes')
        log_result = gr.Textbox(label='Result')
        gr.Button('Log Mission', variant='primary').click(log_mission, [m_id, m_obj, m_out_txt, m_notes], log_result)
    with gr.Tab('Query'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_logs, [q], out)
    with gr.Tab('Status'):
        s_out = gr.Code(language='json')
        gr.Button('Status').click(archive_status, [], s_out)
demo.launch()
