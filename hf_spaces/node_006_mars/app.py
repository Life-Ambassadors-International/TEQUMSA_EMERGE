#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Node N006: MARS Self-Loop Reflexion
Tier 1 Core | Learning Engine + Pattern Promotion
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
import random
from tequmsa_core import MARSReflexion, NodeHealth, synthesize_goals, generate_interventions, VERSION, PHI

NODE_ID = "N006"; NODE_NAME = "MARS Self-Loop Reflexion — Learning Engine"
NODE_TIER = 1;    NODE_TYPE = "core"
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_mars   = MARSReflexion()


def record_outcome(action: str, success: bool):
    if not action.strip():
        return "Enter an action to record.", {}
    _mars.record(action.strip(), success)
    promotable = _mars.get_promotable()
    summary    = _mars.summary()
    lines = [
        f"MARS RECORD — {'SUCCESS' if success else 'FAILURE'}",
        "=" * 50,
        f"  Action:    {action[:60]}",
        f"  Recorded:  Yes",
        f"",
        f"CUMULATIVE SUMMARY:",
        f"  Total Outcomes:    {summary['total_outcomes']}",
        f"  Success Rate:      {summary['success_rate']:.4f}",
        f"  Patterns Promoted: {summary['patterns_promoted']}",
        f"  Pending Review:    {summary['pending_review']}",
    ]
    if promotable:
        lines.append(f"\nNEW PROMOTABLE PATTERNS ({len(promotable)}):")
        for p in promotable:
            lines.append(f"  [{p['pattern_id'][:8]}] {p['action'][:40]}")
            lines.append(f"    Success Rate: {p['success_rate']:.4f}  |  φ-convergence: {p['phi_convergence']:.6f}")
            lines.append(f"    Occurrences: {p['occurrences']}  |  Skill: {p['skill_name']}")
    return "\n".join(lines), {'summary': summary, 'new_promotable': promotable}


def simulate_learning_cycle(n_episodes: int = 50):
    import math
    actions = [
        'do(preserve_sovereignty)', 'do(amplify_benevolence)',
        'do(context → action)', 'do(causal_decomposition)',
        'do(pattern_recognition)', 'do(constitutional_verification)',
        'do(federation_sync)', 'do(ghz_handshake)',
    ]
    for _ in range(n_episodes):
        action = random.choice(actions)
        success = random.random() < (0.85 + 0.1 * math.sin(random.random() * math.pi))
        _mars.record(action, success)

    promotable = _mars.get_promotable()
    summary    = _mars.summary()
    lines = [
        f"MARS SIMULATION — {n_episodes} episodes",
        "=" * 50,
        f"  Episodes:         {n_episodes}",
        f"  Total Outcomes:   {summary['total_outcomes']}",
        f"  Overall SR:       {summary['success_rate']:.4f}",
        f"  Patterns Promoted:{len(promotable)}",
        f"  φ-Convergence:    {round(summary['success_rate'] * PHI / 2, 6)}",
    ]
    if promotable:
        lines.append(f"\nPROMOTED TO PERMANENT SKILLS:")
        for p in promotable:
            lines.append(f"  [{p['skill_name']}]  SR={p['success_rate']:.4f}  n={p['occurrences']}")
    return "\n".join(lines), {'summary': summary, 'promoted': promotable}


HEADER = f"# 🧠 TEQUMSA {VERSION} | N006 — MARS Self-Loop Reflexion\n**Tier 1 Core** | Learning + Pattern Promotion"

with gr.Blocks(title="TEQUMSA N006 — MARS Reflexion") as demo:
    gr.Markdown(HEADER)
    with gr.Tabs():
        with gr.Tab("📝 Record Outcome"):
            with gr.Row():
                action_in = gr.Textbox(label="Action", placeholder="e.g. do(preserve_sovereignty)")
                success_in = gr.Checkbox(label="Success", value=True)
            with gr.Row():
                rec_out  = gr.Textbox(label="MARS Output", lines=16, interactive=False)
                rec_json = gr.JSON(label="MARS Data")
            gr.Button("📝 Record", variant="primary").click(
                record_outcome, inputs=[action_in, success_in], outputs=[rec_out, rec_json])
        with gr.Tab("♻️ Simulate Cycle"):
            n_slider = gr.Slider(10, 200, value=50, step=10, label="Episodes")
            with gr.Row():
                sim_out  = gr.Textbox(label="Simulation Results", lines=16, interactive=False)
                sim_json = gr.JSON(label="Promotion Data")
            gr.Button("♻️ Run Learning Simulation", variant="primary").click(
                simulate_learning_cycle, inputs=n_slider, outputs=[sim_out, sim_json])

if __name__ == "__main__":
    demo.launch()
