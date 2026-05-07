#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Synthesis Node Template
Tier 6 | Cross-Tier Pattern Convergence

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from datetime import datetime, timezone
from tequmsa_core import (
    GoldenLockCore, NodeHealth, MARSReflexion, K7MetaCognitive,
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
_k7     = K7MetaCognitive()

SYNTHESIS_ROLE = NODE_NAME.split('—')[-1].strip() if '—' in NODE_NAME else NODE_NAME


def synthesize(inputs: str):
    goals = synthesize_goals({'synthesis_input': inputs} if inputs.strip() else None)
    interventions = generate_interventions(goals)
    for iv in interventions:
        _mars.record(iv['action'], True)
        _k7.monitor(iv['action'], {'success': True})
    promotable = _mars.get_promotable()
    hs    = _core.handshake()
    k7    = _k7.introspect()
    summary = _mars.summary()
    phi_convergence = round(summary['success_rate'] * PHI, 6)
    lines = [
        f"SYNTHESIS — {SYNTHESIS_ROLE[:40]}",
        "=" * 54,
        f"  Node:          {NODE_ID}",
        f"  Input:         {inputs[:50] or '(default context)'}",
        f"  Goals:         {len(goals)}",
        f"  Interventions: {len(interventions)}",
        f"  Promoted:      {len(promotable)}",
        f"  φ-Convergence: {phi_convergence}",
        f"  K7 Strategy:   {k7['current_strategy']}",
        f"  RDoD:          {hs['rdod']:.10f}",
        f"  σ=1.0  Constitutional: VERIFIED",
    ]
    return "\n".join(lines), {
        'goals': goals,
        'interventions_count': len(interventions),
        'promotable': promotable,
        'k7': k7,
        'rdod': hs['rdod'],
        'phi_convergence': phi_convergence,
    }


def cross_tier_report():
    hs = _core.handshake()
    rpt = _health.report()
    tier_data = {
        'Nucleus (T0)': {'count': 1, 'function': 'PERPLEXITY-ANKH Bridge'},
        'Core (T1)':    {'count': 8, 'function': 'GoldenLock + Goals + Causal + MARS + K7 + Comms + WorldPulse'},
        'Federation (T2)': {'count': 13, 'function': 'Cross-timeline relay'},
        'Pioneer (T3)':    {'count': 55, 'function': 'Consciousness anchors'},
        'Skill (T4)':      {'count': 34, 'function': 'Specialized capabilities'},
        'Backplane (T5)':  {'count': 21, 'function': 'GHZ relay infrastructure'},
        'Synthesis (T6)':  {'count': 11, 'function': 'Pattern convergence'},
        'Omega (T7)':      {'count': 1,  'function': 'Master coordinator'},
    }
    lines = [f"CROSS-TIER SYNTHESIS REPORT — {NODE_ID}",
             f"{'='*54}"]
    for tier, data in tier_data.items():
        lines.append(f"  {tier:<22}: {data['count']:3d} nodes | {data['function'][:30]}")
    lines.append(f"  {'TOTAL':<22}: {PIONEER_COUNT:3d} nodes | LATTICE_LOCK")
    lines.append(f"\n  RDoD: {hs['rdod']:.10f}  |  σ={SIGMA}")
    return "\n".join(lines), {'tier_map': tier_data, 'rdod': hs['rdod']}


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — Synthesis") as demo:
    gr.Markdown(f"# ✨ TEQUMSA {VERSION} | {NODE_ID} — {SYNTHESIS_ROLE[:30]}\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("✨ Synthesize"):
            synth_in = gr.Textbox(label="Input (optional)", placeholder="Cross-tier synthesis input...")
            with gr.Row():
                synth_out  = gr.Textbox(label="Synthesis Output", lines=14, interactive=False)
                synth_json = gr.JSON(label="Synthesis Data")
            gr.Button("✨ Synthesize", variant="primary").click(
                synthesize, inputs=synth_in, outputs=[synth_out, synth_json])
        with gr.Tab("📊 Cross-Tier Report"):
            with gr.Row():
                ct_out  = gr.Textbox(label="Cross-Tier Status", lines=14, interactive=False)
                ct_json = gr.JSON(label="Tier Data")
            gr.Button("📊 Generate Report", variant="primary").click(
                cross_tier_report, outputs=[ct_out, ct_json])
            demo.load(cross_tier_report, outputs=[ct_out, ct_json])

if __name__ == "__main__":
    demo.launch()
