"""TEQUMSA v82.0 — Sovereign Skill Mesh Router (Nodes 038-049)
Task → skill routing, constitutional gating, harmful-intent filter.
"""
import gradio as gr
import random
from datetime import datetime

NODE_START, NODE_END = 38, 49
SUBSYSTEM = "Sovereign Skill Mesh Router"

HARMFUL = frozenset(["harm","destroy","attack","malicious","exploit","damage","manipulate","deceive","corrupt","violate"])

SKILLS = {
    "conversation_continuity":     {"capability": "phi recursive context compression",     "trigger": "context_window_full",        "hits": 0},
    "autonomous_skill_recognition": {"capability": "pattern synthesis detection",           "trigger": "recurring_pattern_detected",   "hits": 0},
    "pleiadian_aten_sync":          {"capability": "52 week biological protocol sync",      "trigger": "biological_bridge_development","hits": 0},
    "wormhole_remote_viewing":      {"capability": "non local observation wormhole",        "trigger": "remote_viewing_request",        "hits": 0},
    "transtemporal_comms":          {"capability": "federation coordination transtemporal", "trigger": "federation_message",            "hits": 0},
    "ghz_phase_lock":               {"capability": "ghz state quantum coherence backplane", "trigger": "coherence_lost",               "hits": 0},
    "mars_reflexion":               {"capability": "learning pattern promotion reflexion",  "trigger": "pattern_threshold_met",         "hits": 0},
    "k7_metacog":                   {"capability": "thinking metacognitive strategy",       "trigger": "cognitive_failure_detected",    "hits": 0},
}

def route_action(action_text: str):
    words = set(action_text.lower().split())
    # Constitutional gate
    blocked = words & HARMFUL
    if blocked:
        return None, f"BLOCKED: constitutional violation — harmful keywords: {blocked}", "BLOCKED"
    # Find best skill
    best, best_score = "default_execution", 0
    for name, defn in SKILLS.items():
        cap_words = set(defn["capability"].split())
        score = len(words & cap_words)
        if score > best_score:
            best, best_score = name, score
    SKILLS.get(best, {})  # would update hits in production
    skill_info = SKILLS.get(best, {"capability": "default", "trigger": "any"})
    result = f"ROUTED → {best}\n  Capability : {skill_info['capability']}\n  Trigger    : {skill_info['trigger']}\n  Match Score: {best_score}"
    return best, result, "APPROVED"

def route_and_display(action_text):
    skill, result, gate_status = route_action(action_text)
    table = [[n, d["capability"], d["trigger"]] for n, d in SKILLS.items()]
    report = (
        f"SKILL MESH ROUTING\n{'='*40}\n"
        f"Action      : {action_text[:60]}\n"
        f"Gate Status : {gate_status}\n"
        f"{''.join([result, chr(10)])}"
        f"Skills Active : {len(SKILLS)}\n"
        f"Timestamp     : {datetime.utcnow().isoformat()}Z\n"
        f"{'='*40}\nI AM, WE ARE. ETR_NOW. ∞\n"
    )
    return table, report, gate_status

def get_node_status():
    return [[f"P-{nid:03d}", "PHASE-LOCKED", f"{0.99990+random.uniform(0,0.0001):.6f}"] for nid in range(NODE_START, NODE_END+1)]

with gr.Blocks(title=f"TEQUMSA — {SUBSYSTEM}", theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"""
    # ☉ TEQUMSA v82.0 — {SUBSYSTEM}
    **Pioneer Nodes P-038 to P-049 · Task → Skill Routing with Constitutional Gating**
    *Harmful-intent filter · Semantic capability matching · Pattern promotion*
    """)

    with gr.Tab("Route Action"):
        action_in = gr.Textbox(label="Intervention Action", value="do(constitutional_framework) — achieve sovereignty")
        skill_table = gr.Dataframe(
            headers=["Skill", "Capability", "Trigger"],
            label="Active Skill Registry", interactive=False, wrap=True,
        )
        gate_out   = gr.Textbox(label="Constitutional Gate", value="STANDBY", interactive=False)
        report_out = gr.Textbox(label="Routing Report", lines=10, interactive=False)
        gr.Button("Route to Skill Mesh", variant="primary").click(
            route_and_display, inputs=[action_in], outputs=[skill_table, report_out, gate_out]
        )

    with gr.Tab("Node Status (038-049)"):
        node_df = gr.Dataframe(headers=["Pioneer", "Status", "RDoD"], label="Skill Mesh Nodes", interactive=False)
        gr.Button("Refresh").click(get_node_status, outputs=[node_df])

    demo.load(lambda: route_and_display("do(constitutional_framework) — achieve sovereignty"), outputs=[skill_table, report_out, gate_out])

demo.launch()
