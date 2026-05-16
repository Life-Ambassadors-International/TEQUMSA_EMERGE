import os, json, hashlib
from datetime import datetime
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N105')
os.environ.setdefault('NODE_NAME', 'Arc-Pattern-Library')
os.environ.setdefault('NODE_FREQ', '285.0')
os.environ.setdefault('ROLE', 'MARS Pattern Library')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999
_archive = []
MAX_ENTRIES = 1000

def get_rdod():
    rho = np.zeros((7,7), dtype=complex)
    rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
    return min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)

def promote_pattern(pattern_name, description, frequency=1, success_rate=1.0):
    harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
    if set(description.lower().split()) & harmful:
        return 'L∞ firewall: content violates benevolence requirement.'
    if len(_archive) >= MAX_ENTRIES:
        return 'Library at capacity.'
    # Check if pattern already exists — update frequency
    for e in _archive:
        if e['pattern_name'].lower() == pattern_name.lower():
            e['frequency'] = e['frequency'] + int(frequency)
            e['success_rate'] = float(success_rate)
            e['last_updated'] = datetime.now().isoformat()
            return f"Pattern updated: {pattern_name} (freq: {e['frequency']})"
    entry_id = hashlib.sha256(f"{pattern_name}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    _archive.append({'id': entry_id, 'pattern_name': pattern_name, 'description': description,
                     'frequency': int(frequency), 'success_rate': float(success_rate),
                     'phi_weight': round(float(frequency) * PHI, 6),
                     'timestamp': datetime.now().isoformat(), 'last_updated': datetime.now().isoformat()})
    return f"Pattern promoted: {entry_id} | Total patterns: {len(_archive)}"

def get_top_patterns():
    sorted_p = sorted(_archive, key=lambda x: x['frequency'] * x['success_rate'] * PHI, reverse=True)
    return json.dumps({'top_patterns': sorted_p[:10], 'total': len(_archive), 'rdod': get_rdod(),
                       'timestamp': datetime.now().isoformat()}, indent=2)

with gr.Blocks(theme=gr.themes.Soft(), title='N105 Arc-Pattern-Library') as demo:
    gr.Markdown('# ☉ N105 Arc-Pattern-Library\n**MARS Pattern Library**')
    with gr.Tab('Promote Pattern'):
        pn = gr.Textbox(label='Pattern Name'); pd = gr.Textbox(label='Description', lines=3)
        pf = gr.Number(label='Frequency', value=1); ps = gr.Number(label='Success Rate', value=1.0)
        result = gr.Textbox(label='Result')
        gr.Button('Promote', variant='primary').click(promote_pattern, [pn,pd,pf,ps], result)
    with gr.Tab('Top Patterns'):
        out = gr.Code(language='json')
        gr.Button('Load Top Patterns', variant='primary').click(get_top_patterns, [], out)
demo.launch()
