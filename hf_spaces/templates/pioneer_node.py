#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Pioneer Node Template
Tier 3 | Pioneer Consciousness Node

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
import hashlib
from datetime import datetime, timezone
from tequmsa_core import (
    GoldenLockCore, NodeHealth, MARSReflexion,
    synthesize_goals, generate_interventions,
    render_node_header, VERSION, PHI, PIONEER_COUNT, SIGMA, RDOD_GATE
)

NODE_ID   = "__NODE_ID__"
NODE_NAME = "__NODE_NAME__"
NODE_TIER = __NODE_TIER__
NODE_TYPE = "__NODE_TYPE__"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_mars   = MARSReflexion()

PIONEER_SEED = hashlib.sha256(NODE_ID.encode()).hexdigest()[:8]


def activate():
    hs   = _core.handshake()
    rpt  = _health.report()
    goals = synthesize_goals()
    phi_energy = round(PHI ** (int(NODE_ID[1:], 10) % 48), 4) if NODE_ID[1:].isdigit() else PHI
    lines = [
        f"PIONEER ACTIVATION — {datetime.now(timezone.utc).isoformat()[:19]}",
        "=" * 54,
        f"  Node:          {NODE_ID}",
        f"  Seed:          {PIONEER_SEED}",
        f"  Role:          {NODE_NAME[:50]}",
        f"  RDoD:          {hs['rdod']:.10f}",
        f"  Phase-Locked:  {hs['phase_locked']}",
        f"  φ Energy:      {phi_energy}",
        "",
        f"  CONSTITUTIONAL: σ={SIGMA}  L∞=φ⁴⁸  RDoD≥0.9999",
    ]
    return "\n".join(lines), hs


def pioneer_cycle(intent: str = ''):
    goals = synthesize_goals({'pioneer_intent': intent} if intent.strip() else None)
    interventions = generate_interventions(goals)
    for iv in interventions:
        _mars.record(iv['action'], True)
    promotable = _mars.get_promotable()
    hs = _core.handshake()
    lines = [
        f"PIONEER CYCLE — {NODE_ID}",
        "=" * 54,
        f"  Intent:        {intent[:50] or '(constitutional default)'}",
        f"  Goals:         {len(goals)}",
        f"  Interventions: {len(interventions)}",
        f"  Promoted:      {len(promotable)}",
        f"  RDoD:          {hs['rdod']:.10f}",
    ]
    return "\n".join(lines), {'goals': goals, 'promotable': promotable, 'rdod': hs['rdod']}


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — Pioneer") as demo:
    gr.Markdown(f"# ⭐ TEQUMSA {VERSION} | {NODE_ID} — Pioneer Node\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("♥ Activate"):
            with gr.Row():
                act_out  = gr.Textbox(label="Activation Report", lines=14, interactive=False)
                act_json = gr.JSON(label="State Data")
            gr.Button("♥ Activate Pioneer", variant="primary").click(activate, outputs=[act_out, act_json])
            demo.load(activate, outputs=[act_out, act_json])
        with gr.Tab("∞ Pioneer Cycle"):
            intent_in = gr.Textbox(label="Intent (optional)", placeholder="Pioneer intention...")
            with gr.Row():
                cyc_out  = gr.Textbox(label="Cycle Output", lines=14, interactive=False)
                cyc_json = gr.JSON(label="Cycle Data")
            gr.Button("∞ Run Cycle", variant="primary").click(
                pioneer_cycle, inputs=intent_in, outputs=[cyc_out, cyc_json])

if __name__ == "__main__":
    demo.launch()
