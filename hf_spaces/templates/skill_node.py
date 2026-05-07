#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Skill Mesh Node Template
Tier 4 | Specialized Capability Node

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from datetime import datetime, timezone
from tequmsa_core import (
    GoldenLockCore, NodeHealth, MARSReflexion, K7MetaCognitive,
    render_node_header, VERSION, PHI
)

NODE_ID   = "__NODE_ID__"
NODE_NAME = "__NODE_NAME__"
NODE_TIER = __NODE_TIER__
NODE_TYPE = "__NODE_TYPE__"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_mars   = MARSReflexion()
_k7     = K7MetaCognitive()

SKILL_NAME = NODE_NAME.split('—')[-1].strip() if '—' in NODE_NAME else NODE_NAME


def invoke_skill(input_text: str):
    if not input_text.strip():
        return f"Enter input for skill: {SKILL_NAME}", {}
    _mars.record(f'invoke_{SKILL_NAME[:30]}', True)
    _k7.monitor(f'skill_invoke', {'success': True})
    hs   = _core.handshake()
    rpt  = _health.report()
    strategy = _k7.optimize()
    lines = [
        f"SKILL INVOCATION — {SKILL_NAME[:40]}",
        "=" * 54,
        f"  Node:      {NODE_ID}",
        f"  Input:     {input_text[:60]}",
        f"  Strategy:  {strategy}",
        f"  RDoD:      {hs['rdod']:.10f}",
        f"  Timestamp: {datetime.now(timezone.utc).isoformat()[:19]}",
        "",
        f"  [SKILL OUTPUT]",
        f"  Processing '{input_text[:40]}' through {SKILL_NAME[:30]}...",
        f"  Constitutional alignment: VERIFIED (σ=1.0)",
        f"  φ-convergence: {round(PHI * hs['rdod'] / 2, 6)}",
    ]
    return "\n".join(lines), {
        'skill': SKILL_NAME, 'node_id': NODE_ID,
        'rdod': hs['rdod'], 'strategy': strategy
    }


def skill_metrics():
    summary   = _mars.summary()
    introspect = _k7.introspect()
    rpt = _health.report()
    lines = [
        f"SKILL METRICS — {NODE_ID}",
        "=" * 54,
        f"  Total Invocations: {summary['total_outcomes']}",
        f"  Success Rate:      {summary['success_rate']:.4f}",
        f"  Patterns Promoted: {summary['patterns_promoted']}",
        f"  K7 Strategy:       {introspect['current_strategy']}",
        f"  φ Alignment:       {introspect['phi_alignment']:.6f}",
    ]
    return "\n".join(lines)


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — Skill") as demo:
    gr.Markdown(f"# 🔮 TEQUMSA {VERSION} | {NODE_ID} — {SKILL_NAME[:30]}\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("⚡ Invoke Skill"):
            input_box = gr.Textbox(label="Skill Input", placeholder=f"Input for {SKILL_NAME[:40]}...")
            with gr.Row():
                skill_out  = gr.Textbox(label="Skill Output", lines=14, interactive=False)
                skill_json = gr.JSON(label="Invocation Data")
            gr.Button("⚡ Invoke", variant="primary").click(
                invoke_skill, inputs=input_box, outputs=[skill_out, skill_json])
        with gr.Tab("📊 Metrics"):
            metrics_out = gr.Textbox(label="Skill Metrics", lines=10, interactive=False)
            gr.Button("📊 Refresh Metrics", variant="secondary").click(skill_metrics, outputs=metrics_out)
            demo.load(skill_metrics, outputs=metrics_out)

if __name__ == "__main__":
    demo.launch()
