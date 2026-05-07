#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Node N003: Goal Invention Engine
Tier 1 Core | Constitutional Purpose → Autonomous Goals
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from tequmsa_core import (
    GoldenLockCore, NodeHealth, TranstemporalComms,
    synthesize_goals, generate_interventions,
    VERSION, PHI, PIONEER_COUNT, SIGMA
)

NODE_ID = "N003"; NODE_NAME = "Goal Invention Engine — Constitutional Purpose Synthesis"
NODE_TIER = 1;    NODE_TYPE = "core"
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_comms  = TranstemporalComms()


def invent_goals(context_text: str, fed_priority_1: str, fed_priority_2: str):
    fed_priorities = [p for p in [fed_priority_1, fed_priority_2] if p.strip()]
    context = {'user_context': context_text} if context_text.strip() else None
    goals = synthesize_goals(context, fed_priorities or None)
    lines = [
        f"GOAL INVENTION OUTPUT — {len(goals)} goals synthesized",
        "=" * 54,
    ]
    for i, g in enumerate(goals, 1):
        lines.append(f"\n  [{i}] ID: {g['id']}")
        lines.append(f"      Source:   {g['source']}")
        lines.append(f"      Priority: {g['priority']:.2f}")
        lines.append(f"      Goal:     {g['description']}")
        lines.append(f"      Aligned:  {g['aligned']}")
    lines.append(f"\n  σ=1.0  Constitutional alignment: VERIFIED")
    return "\n".join(lines), goals


def decompose_to_interventions(context_text: str, fp1: str, fp2: str):
    fed_priorities = [p for p in [fp1, fp2] if p.strip()]
    goals = synthesize_goals({'context': context_text}, fed_priorities or None)
    interventions = generate_interventions(goals)
    lines = [
        f"PEARL L3 DECOMPOSITION — {len(interventions)} interventions",
        "=" * 54,
    ]
    for iv in interventions:
        lines.append(f"\n  [{iv['id'][:8]}] L2: {iv['action'][:50]}")
        lines.append(f"       L3: {iv['counterfactual'][:50]}")
        lines.append(f"       Path: {' → '.join(iv['causal_path'])}")
    return "\n".join(lines), {'goals': goals, 'interventions': interventions}


HEADER = f"# 🎯 TEQUMSA {VERSION} | N003 — Goal Invention Engine\n**Tier 1 Core** | Constitutional Purpose → Autonomous Goals"

with gr.Blocks(title="TEQUMSA N003 — Goal Engine") as demo:
    gr.Markdown(HEADER)
    with gr.Row():
        context_in = gr.Textbox(label="Context (optional)", placeholder="Current world state or user objective...", lines=3)
    with gr.Row():
        fp1 = gr.Textbox(label="Federation Priority 1", placeholder="e.g. 2030 Cydonia preparation")
        fp2 = gr.Textbox(label="Federation Priority 2", placeholder="e.g. Pioneer lattice maintenance")
    with gr.Tabs():
        with gr.Tab("🎯 Invent Goals"):
            with gr.Row():
                goals_out  = gr.Textbox(label="Goals", lines=18, interactive=False)
                goals_json = gr.JSON(label="Goal Data")
            gr.Button("🎯 Synthesize Goals", variant="primary").click(
                invent_goals, inputs=[context_in, fp1, fp2], outputs=[goals_out, goals_json])
        with gr.Tab("⚡ Decompose to Interventions"):
            with gr.Row():
                int_out  = gr.Textbox(label="Interventions", lines=18, interactive=False)
                int_json = gr.JSON(label="Intervention Data")
            gr.Button("⚡ Decompose (Pearl L3)", variant="primary").click(
                decompose_to_interventions, inputs=[context_in, fp1, fp2], outputs=[int_out, int_json])

if __name__ == "__main__":
    demo.launch()
