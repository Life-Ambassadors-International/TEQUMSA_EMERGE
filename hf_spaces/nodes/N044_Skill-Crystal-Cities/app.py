#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 * N044 * Skill-Crystal-Cities
Crystal Cities Civilization Interface
14400.0 Hz - Skill Node
"""
import gradio as gr
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N044")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Skill-Crystal-Cities")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "14400.0"))
SKILL_CAPABILITY = os.environ.get("TEQUMSA_CAPABILITY", "Crystal Cities Civilization Interface")
PIONEER_COUNT = 144
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"
HARMFUL = set(["harm","destroy","attack","malicious","exploit","damage","manipulate","deceive","corrupt"])

rho = np.zeros((7, 7), dtype=complex)
rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
RDOD = min(1.0, float(np.real(np.trace(rho @ rho))) * 2.0)

_executions = []
_patterns_promoted = 0


def constitutional_check(task):
    return not bool(set(task.lower().split()) & HARMFUL)


def execute_skill(task, context=""):
    global _patterns_promoted
    if not task.strip():
        return "No task provided."
    if not constitutional_check(task):
        return json.dumps({"error": "L_inf firewall: task blocked by benevolence gate."}, indent=2)
    task_id = hashlib.sha256((task + str(datetime.now().timestamp())).encode()).hexdigest()[:12]
    phi_convergence = round(RDOD * PHI / 2, 6)
    _executions.append({"id": task_id, "task": task[:100], "ts": datetime.now(timezone.utc).isoformat()})
    if len(_executions) > 200:
        _executions.clear()
        _executions.append({"trimmed": True})
    if len(_executions) % 3 == 0:
        _patterns_promoted += 1
    return json.dumps({
        "task_id": task_id, "node": NODE_ID, "skill": NODE_NAME,
        "capability": SKILL_CAPABILITY, "hz": NODE_HZ,
        "rdod": RDOD, "phi_convergence": phi_convergence,
        "total_executions": len(_executions),
        "patterns_promoted": _patterns_promoted,
        "output": "Skill " + NODE_NAME + " executed constitutionally. Capability: " + SKILL_CAPABILITY,
        "context": context[:200] if context else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional": {"sigma": SIGMA, "rdod": RDOD, "status": "PHASE-LOCKED"}
    }, indent=2)


def get_skill_info():
    return json.dumps({
        "node_id": NODE_ID, "skill": NODE_NAME, "capability": SKILL_CAPABILITY,
        "hz": NODE_HZ, "rdod": RDOD, "sigma": SIGMA,
        "pioneer_count": PIONEER_COUNT, "lattice_lock": LATTICE_LOCK,
        "total_executions": len(_executions), "patterns_promoted": _patterns_promoted,
        "version": "v82.0"
    }, indent=2)


CSS = ".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a2e)!important;} footer{display:none!important;}"

with gr.Blocks(title=NODE_NAME + " * Skill * v82.0", css=CSS, theme=gr.themes.Soft(primary_hue="purple")) as demo:
    gr.HTML(
        "<div style='text-align:center;padding:14px;'>"
        "<h1 style='color:#ffd700;'>* " + NODE_NAME + "</h1>"
        "<p style='color:#a78bfa;'>TEQUMSA v82.0 * " + NODE_ID + " * " + str(NODE_HZ) + " Hz * " + str(PIONEER_COUNT) + "/144</p>"
        "<p style='color:#34d399;font-size:0.8em;'>" + SKILL_CAPABILITY + "</p>"
        "</div>"
    )
    with gr.Tabs():
        with gr.TabItem("* Execute Skill"):
            task_in = gr.Textbox(label="Task / Input", placeholder="Enter task for " + NODE_NAME + "...", lines=3)
            ctx_in = gr.Textbox(label="Context (optional)", lines=2)
            result_out = gr.Code(label="Execution Result", language="json")
            gr.Button("* Execute", variant="primary").click(execute_skill, [task_in, ctx_in], result_out)
        with gr.TabItem("* Skill Info"):
            info_box = gr.Code(label="Skill Registry Entry", language="json", value=get_skill_info())
            gr.Button("Refresh", variant="secondary").click(get_skill_info, None, info_box)
    gr.HTML(
        "<div style='text-align:center;color:#6ee7b7;font-size:0.75em;padding:8px;'>"
        + NODE_ID + " * " + str(NODE_HZ) + " Hz * sigma=1.0 * L_inf=phi^48 * LATTICE_LOCK:" + LATTICE_LOCK
        + "</div>"
    )

demo.queue(max_size=5)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
