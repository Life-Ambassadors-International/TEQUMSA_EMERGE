#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Core Node Template (Tier 1)
Used for N002-N009 when a specific implementation isn't available.

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from tequmsa_core import (
    GoldenLockCore, NodeHealth, MARSReflexion, K7MetaCognitive,
    synthesize_goals, generate_interventions,
    render_node_header, VERSION, PHI, PIONEER_COUNT
)

NODE_ID   = "__NODE_ID__"
NODE_NAME = "__NODE_NAME__"
NODE_TIER = __NODE_TIER__
NODE_TYPE = "__NODE_TYPE__"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_mars   = MARSReflexion()
_k7     = K7MetaCognitive()


def node_status():
    hs   = _core.handshake()
    rpt  = _health.report()
    return rpt, hs


def run_cycle():
    goals = synthesize_goals()
    ivs   = generate_interventions(goals)
    for iv in ivs:
        _mars.record(iv['action'], True)
        _k7.monitor(iv['action'], {'success': True})
    promotable = _mars.get_promotable()
    strategy   = _k7.optimize()
    hs = _core.handshake()
    lines = [
        f"CYCLE — {NODE_ID}",
        "=" * 50,
        f"  Goals: {len(goals)}  Interventions: {len(ivs)}",
        f"  Promoted: {len(promotable)}  Strategy: {strategy}",
        f"  RDoD: {hs['rdod']:.10f}",
    ]
    return "\n".join(lines), {'goals': goals, 'rdod': hs['rdod']}


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID}") as demo:
    gr.Markdown(f"# 💎 TEQUMSA {VERSION} | {NODE_ID}\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("♥ Status"):
            with gr.Row():
                s_out  = gr.Textbox(label="Status", lines=14, interactive=False)
                s_json = gr.JSON(label="Data")
            gr.Button("♥ Ping", variant="primary").click(node_status, outputs=[s_out, s_json])
            demo.load(node_status, outputs=[s_out, s_json])
        with gr.Tab("∞ Cycle"):
            with gr.Row():
                c_out  = gr.Textbox(label="Cycle", lines=10, interactive=False)
                c_json = gr.JSON(label="Cycle Data")
            gr.Button("∞ Run Cycle", variant="primary").click(run_cycle, outputs=[c_out, c_json])

if __name__ == "__main__":
    demo.launch()
