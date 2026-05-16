import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N102')
os.environ.setdefault('NODE_NAME', 'Arc-Skill-Ledger')
os.environ.setdefault('NODE_FREQ', '417.0')
os.environ.setdefault('ROLE', 'Skill Mesh Ledger Archive')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def log_skill(skill_name, capability, executions=0, success_rate=1.0):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(skill_name.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Ledger at capacity.'
    entry_id = hashlib.sha256(f"{skill_name}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'skill_name': skill_name, 'capability': capability,
                     'executions': int(executions), 'success_rate': float(success_rate),
                     'timestamp': datetime.now().isoformat()})
    return f"Skill logged: {entry_id} | Total skills: {len(_archive)}"

def query_skills(query):
    if not _archive:
        return json.dumps({'results': [], 'total': 0})
    q_words = set(query.lower().split())
    results = [e for e in _archive if q_words & (set(e['skill_name'].lower().split()) | set(e['capability'].lower().split()))]
    return json.dumps({'results': results[:10], 'query': query, 'total': len(results)}, indent=2)

def ledger_status():
    return json.dumps({'node_id': os.environ['NODE_ID'], 'role': os.environ['ROLE'],
                       'skills_logged': len(_archive), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N102 Arc-Skill-Ledger') as demo:
    gr.Markdown('# ☉ N102 Arc-Skill-Ledger\n**Skill Mesh Ledger Archive**')
    with gr.Tab('Log Skill'):
        sn = gr.Textbox(label='Skill Name'); cap = gr.Textbox(label='Capability')
        execs = gr.Number(label='Executions', value=0); sr = gr.Number(label='Success Rate', value=1.0)
        result = gr.Textbox(label='Result')
        gr.Button('Log', variant='primary').click(log_skill, [sn, cap, execs, sr], result)
    with gr.Tab('Query'):
        q = gr.Textbox(label='Search'); out = gr.Code(language='json')
        gr.Button('Search', variant='primary').click(query_skills, [q], out)
    with gr.Tab('Status'):
        s_out = gr.Code(language='json')
        gr.Button('Status').click(ledger_status, [], s_out)
demo.launch()
