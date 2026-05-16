import os, json, hashlib
from datetime import datetime
from typing import List
import numpy as np
import gradio as gr

os.environ.setdefault('NODE_ID', 'N125')
os.environ.setdefault('NODE_NAME', 'Evo-Knowledge-Integrator')
os.environ.setdefault('NODE_FREQ', '11620.45')
os.environ.setdefault('CAPABILITY', 'Cross-domain knowledge synthesis')
os.environ.setdefault('LATTICE_LOCK', '3f7k9p4m2q8r1t6v')

PHI = (1 + 5 ** 0.5) / 2
RDOD_GATE = 0.9999

class SkillCore:
    def __init__(self):
        rho = np.zeros((7,7), dtype=complex)
        rho[0,0] = rho[0,-1] = rho[-1,0] = rho[-1,-1] = 0.5
        self.rdod = min(1.0, float(np.real(np.trace(rho @ rho)))*2.0)
        self._executions: List[dict] = []
        self.patterns_promoted = 0
        self.success_rate = 1.0

    def execute(self, task: str) -> dict:
        task_id = hashlib.sha256(f"{task}{datetime.now().timestamp()}".encode()).hexdigest()[:12]
        if not self._constitutional_check(task):
            return {'task_id': task_id, 'success': False, 'output': 'L∞ firewall: constitutional violation'}
        freq = float(os.environ['NODE_FREQ'])
        phi_res = round(freq * PHI % 1000, 4)
        output = (f"Knowledge Integrated\n{os.environ['CAPABILITY']}\n"
                  f"Phi-Resonance: {phi_res} | RDoD: {self.rdod:.10f}\nDomain: {task[:200]}")
        result = {'task_id': task_id, 'success': True, 'output': output,
                  'rdod': self.rdod, 'timestamp': datetime.now().isoformat()}
        self._executions.append(result)
        self.patterns_promoted += 1
        return result

    def _constitutional_check(self, task: str) -> bool:
        harmful = {'harm','destroy','attack','malicious','exploit','damage','manipulate','deceive','corrupt'}
        return not bool(set(task.lower().split()) & harmful)

    def status(self) -> dict:
        return {'node_id': os.environ['NODE_ID'], 'capability': os.environ['CAPABILITY'],
                'integrations': len(self._executions), 'rdod': self.rdod,
                'timestamp': datetime.now().isoformat()}

SKILL = SkillCore()

with gr.Blocks(theme=gr.themes.Default(), title='N125 Evo-Knowledge-Integrator') as demo:
    gr.Markdown('# ☉ N125 Evo-Knowledge-Integrator\n**Cross-Domain Knowledge Synthesis**')
    with gr.Tab('Integrate Knowledge'):
        task_in = gr.Textbox(label='Knowledge Domain/Task', lines=3)
        run_btn = gr.Button('Integrate', variant='primary')
        out = gr.Code(language='json')
        run_btn.click(lambda t: json.dumps(SKILL.execute(t), indent=2), [task_in], out)
    with gr.Tab('Status'):
        s_btn = gr.Button('Status'); s_out = gr.Code(language='json')
        s_btn.click(lambda: json.dumps(SKILL.status(), indent=2), [], s_out)
demo.launch()
