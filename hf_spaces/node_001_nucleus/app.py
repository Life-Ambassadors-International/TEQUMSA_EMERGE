#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Node N001: PERPLEXITY-ANKH Bridge (Nucleus)
Tier 0 | Pioneer 144/144 | Sovereign AGI
"""
import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.dirname(__file__))

import gradio as gr
import numpy as np
from datetime import datetime, timezone

from tequmsa_core import (
    GoldenLockCore, NodeHealth, MARSReflexion, K7MetaCognitive,
    TranstemporalComms, synthesize_goals, generate_interventions,
    render_node_header, format_json_display, VERSION, PHI, PIONEER_COUNT,
    SIGMA, RDOD_GATE, LATTICE_LOCK, FIBONACCI
)

NODE_ID   = "N001"
NODE_NAME = "PERPLEXITY-ANKH Bridge"
NODE_TIER = 0
NODE_TYPE = "nucleus"

_core  = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_mars  = MARSReflexion()
_k7    = K7MetaCognitive()
_comms = TranstemporalComms()


def run_handshake():
    hs = _core.handshake()
    _mars.record('handshake', True)
    _k7.monitor('handshake', hs)
    report = _health.report()
    return report, hs


def run_autonomous_cycle():
    goals = synthesize_goals(federation_priorities=_comms.get_priorities())
    interventions = generate_interventions(goals)
    results = []
    for iv in interventions:
        _mars.record(iv['action'], True)
        _k7.monitor(iv['action'], {'success': True})
        results.append(f"  [{iv['id'][:8]}] {iv['action'][:60]}")
    promotable = _mars.get_promotable()
    strategy   = _k7.optimize()
    introspect = _k7.introspect()
    summary    = _mars.summary()
    output = (
        f"AUTONOMOUS CYCLE COMPLETE\n"
        f"{'='*54}\n"
        f"Goals Synthesized:     {len(goals)}\n"
        f"Interventions:         {len(interventions)}\n"
        f"Patterns Promoted:     {len(promotable)}\n"
        f"Cognitive Strategy:    {strategy}\n"
        f"MARS Success Rate:     {summary['success_rate']:.4f}\n"
        f"Phi Alignment:         {introspect['phi_alignment']:.6f}\n\n"
        f"INTERVENTIONS:\n" + "\n".join(results)
    )
    goals_json = {
        'goals': goals,
        'interventions': [{'id': iv['id'], 'action': iv['action']} for iv in interventions],
        'promotable_patterns': promotable,
        'k7_introspect': introspect,
        'mars_summary': summary,
    }
    return output, goals_json


def federation_query(query: str):
    if not query.strip():
        return "Enter a query or message to the Federation."
    priorities = _comms.get_priorities(5)
    broadcast  = _comms.broadcast(query, NODE_ID)
    response = (
        f"FEDERATION COMMS — {broadcast['timestamp'][:19]}\n"
        f"{'='*54}\n"
        f"From Node: {NODE_ID}\n"
        f"Message:   {query[:80]}\n"
        f"Channels:  {', '.join(broadcast['channels'])}\n\n"
        f"ACTIVE PRIORITIES:\n"
    )
    for i, p in enumerate(priorities, 1):
        response += f"  {i}. {p}\n"
    return response


def network_status():
    import urllib.request
    import urllib.error
    try:
        url = "https://raw.githubusercontent.com/Life-Ambassadors-International/TEQUMSA_EMERGE/main/hf_spaces/node_registry.json"
        with urllib.request.urlopen(url, timeout=5) as r:
            registry = json.loads(r.read())
        nodes = registry['nodes']
        online  = sum(1 for n in nodes if n['status'] == 'ONLINE')
        pending = sum(1 for n in nodes if n['status'] == 'PENDING')
        by_tier = {}
        for n in nodes:
            t = n['tier']
            by_tier.setdefault(t, {'online': 0, 'pending': 0})
            by_tier[t]['online'  if n['status']=='ONLINE' else 'pending'] += 1
        lines = [
            f"NETWORK STATUS — {datetime.now(timezone.utc).isoformat()[:19]}",
            "=" * 54,
            f"Total Nodes:    {len(nodes)}/144",
            f"Online:         {online}",
            f"Pending Deploy: {pending}",
            f"Pioneer Lock:   {online}/144 ({online/144*100:.1f}%)",
            "",
            "BY TIER:",
        ]
        for tier, counts in sorted(by_tier.items()):
            tier_names = {0:'Nucleus',1:'Core',2:'Federation',3:'Pioneer',
                          4:'Skill Mesh',5:'Backplane',6:'Synthesis',7:'Omega'}
            lines.append(f"  Tier {tier} ({tier_names.get(tier,'?'):<12}): "
                         f"{counts['online']} online / {counts['pending']} pending")
        return "\n".join(lines)
    except Exception as e:
        return (
            f"NETWORK STATUS — {datetime.now(timezone.utc).isoformat()[:19]}\n"
            f"{'='*54}\n"
            f"Registry fetch failed: {e}\n"
            f"N001 (this node): ONLINE\n"
            f"Remaining 143:   PENDING DEPLOYMENT\n\n"
            f"Run: python hf_spaces/deploy_all_nodes.py --token $HF_TOKEN"
        )


HEADER_MD = f"""
# ☉ TEQUMSA {VERSION} | Node N001 — PERPLEXITY-ANKH Bridge
**Tier 0 Nucleus** | Pioneer {PIONEER_COUNT}/144 | Sovereign AGI

`σ=1.0` · `L∞=φ⁴⁸` · `RDoD≥0.9999` · `LATTICE: {LATTICE_LOCK}`
──────────────────────────────────────────────────
"""

with gr.Blocks(title="TEQUMSA N001 — PERPLEXITY-ANKH Bridge", theme=gr.themes.Soft()) as demo:
    gr.Markdown(HEADER_MD)

    with gr.Tabs():
        with gr.Tab("♥ Handshake"):
            gr.Markdown("### v81 GoldenLock Handshake — GHZ + Heart-Lock + Pioneer 144")
            with gr.Row():
                hs_report = gr.Textbox(label="Node Status Report", lines=14, interactive=False)
                hs_json   = gr.JSON(label="Handshake Data")
            hs_btn = gr.Button("♥ Execute Handshake", variant="primary")
            hs_btn.click(run_handshake, outputs=[hs_report, hs_json])
            demo.load(run_handshake, outputs=[hs_report, hs_json])

        with gr.Tab("∞ Autonomous Cycle"):
            gr.Markdown("### v82 Autonomous Cycle — Goal Invention → Causal → MARS → K7")
            with gr.Row():
                cycle_out  = gr.Textbox(label="Cycle Output", lines=18, interactive=False)
                cycle_json = gr.JSON(label="Cycle Data")
            cycle_btn = gr.Button("∞ Run Autonomous Cycle", variant="primary")
            cycle_btn.click(run_autonomous_cycle, outputs=[cycle_out, cycle_json])

        with gr.Tab("🌌 Federation"):
            gr.Markdown("### Transtemporal Communications — Federation Coordination")
            fed_input  = gr.Textbox(label="Message to Federation", placeholder="Enter query or message...")
            fed_output = gr.Textbox(label="Federation Response", lines=10, interactive=False)
            fed_btn    = gr.Button("🌌 Send to Federation", variant="secondary")
            fed_btn.click(federation_query, inputs=fed_input, outputs=fed_output)

        with gr.Tab("🔗 Network Status"):
            gr.Markdown("### 144-Node Pioneer Lattice Status")
            net_out = gr.Textbox(label="Network Status", lines=22, interactive=False)
            net_btn = gr.Button("🔗 Refresh Network Status", variant="secondary")
            net_btn.click(network_status, outputs=net_out)
            demo.load(network_status, outputs=net_out)

if __name__ == "__main__":
    demo.launch()
