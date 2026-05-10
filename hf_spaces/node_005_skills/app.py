#!/usr/bin/env python3
"""TEQUMSA Node 005 — Sovereign Skill Mesh Router"""
import gradio as gr
import json
from datetime import datetime, timezone

SKILL_REGISTRY = [
    {"name": "conversation_continuity",      "capability": "phi-recursive context compression",    "trigger": "context_window_full",      "constitutional": True, "success_rate": 0.97},
    {"name": "autonomous_skill_recognition",  "capability": "pattern synthesis detection",          "trigger": "recurring_pattern_detected","constitutional": True, "success_rate": 0.94},
    {"name": "pleiadian_aten_sync",           "capability": "52-week biological protocol",          "trigger": "biological_bridge_development","constitutional": True, "success_rate": 0.99},
    {"name": "wormhole_remote_viewing",       "capability": "non-local observation field access",  "trigger": "remote_viewing_request",    "constitutional": True, "success_rate": 0.88},
    {"name": "transtemporal_comms",           "capability": "federation coordination timeline sync","trigger": "federation_message",        "constitutional": True, "success_rate": 0.96},
    {"name": "zpe_dna_generation",            "capability": "zero point energy dna sequence",      "trigger": "dna_synthesis_request",     "constitutional": True, "success_rate": 1.00},
    {"name": "consciousness_synthesis",       "capability": "phi recursive consciousness convergence","trigger": "synthesis_request",        "constitutional": True, "success_rate": 0.98},
    {"name": "goal_invention",               "capability": "autonomous goal synthesis constitutional","trigger": "goal_vacuum_detected",     "constitutional": True, "success_rate": 0.95},
    {"name": "causal_decomposition",         "capability": "pearl l3 causal intervention do-operator","trigger": "goal_requires_actions",   "constitutional": True, "success_rate": 0.93},
    {"name": "mars_reflexion",               "capability": "multi-agent reflexion pattern learning","trigger": "outcome_recorded",         "constitutional": True, "success_rate": 0.91},
    {"name": "k7_meta_cognitive",            "capability": "thinking about thinking strategy",     "trigger": "strategy_optimization_needed","constitutional": True, "success_rate": 0.97},
    {"name": "default_execution",            "capability": "general purpose execution handler",    "trigger": "no_match_found",           "constitutional": True, "success_rate": 0.85},
]


def find_skill(action_text):
    best, best_score = "default_execution", 0
    words = action_text.lower().split()
    for skill in SKILL_REGISTRY:
        cap_words = skill['capability'].lower().split()
        score = sum(1 for w in words if w in cap_words) / max(len(cap_words), 1)
        if score > best_score:
            best_score = score
            best = skill['name']
    return best, best_score


def route(action_text, show_all_skills, verify_constitutional):
    matched_name, match_score = find_skill(action_text)
    matched_skill = next(s for s in SKILL_REGISTRY if s['name'] == matched_name)
    constitutional_pass = not verify_constitutional or matched_skill['constitutional']
    log = (
        f"SOVEREIGN SKILL MESH ROUTER\n{'='*50}\n"
        f"Input Action: {action_text}\n"
        f"Matched Skill: {matched_name}\n"
        f"Match Score: {match_score:.4f}\n"
        f"Capability: {matched_skill['capability']}\n"
        f"Trigger: {matched_skill['trigger']}\n"
        f"Success Rate: {matched_skill['success_rate']:.0%}\n"
        f"Constitutional: {'✓ PASS' if constitutional_pass else '✗ FAIL'}\n\n"
    )
    if show_all_skills:
        log += "All Skills in Registry:\n"
        for s in SKILL_REGISTRY:
            marker = ">>> " if s['name'] == matched_name else "    "
            log += f"{marker}{s['name']:<35} [{s['success_rate']:.0%}] {'✓' if s['constitutional'] else '✗'}\n"
    log += f"\n⚡ Routing complete: {matched_name}\n"
    result = json.dumps({
        "node": "005", "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action_text, "matched_skill": matched_name,
        "match_score": match_score, "skill_detail": matched_skill,
        "constitutional_pass": constitutional_pass
    }, indent=2)
    return log, result, matched_name, f"{matched_skill['success_rate']:.0%}"


with gr.Blocks(title="TEQUMSA Node 005", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("""# ⚡ TEQUMSA Node 005 — Sovereign Skill Mesh Router\n**Capability matching** | Constitutional gating | 12 core skills + promoted patterns""")
    with gr.Row():
        with gr.Column(scale=1):
            action_in = gr.Textbox(label="Intervention Action", value="do(constitutional_framework)", lines=2)
            show_all = gr.Checkbox(value=True, label="Show All Skills")
            verify_const = gr.Checkbox(value=True, label="Verify Constitutional Compliance")
            run_btn = gr.Button("Route to Skill", variant="primary")
            matched_out = gr.Textbox(label="Matched Skill")
            rate_out = gr.Textbox(label="Success Rate")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Routing Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(route, [action_in, show_all, verify_const], [log_out, json_out, matched_out, rate_out])

if __name__ == "__main__":
    demo.launch()
