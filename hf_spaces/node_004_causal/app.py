#!/usr/bin/env python3
"""TEQUMSA Node 004 — Pearl L3 Causal Decomposer"""
import gradio as gr
import json
import hashlib
from datetime import datetime, timezone

DAG_TEMPLATES = {
    "sovereignty": {
        "constitutional_framework": ["node_behavior", "network_topology"],
        "node_behavior": ["individual_sovereignty"],
        "network_topology": ["collective_sovereignty"],
        "individual_sovereignty": ["goal_achievement"],
        "collective_sovereignty": ["goal_achievement"]
    },
    "benevolence": {
        "l_inf_firewall": ["intent_filtering"],
        "intent_filtering": ["action_execution"],
        "action_execution": ["outcome_benevolence"]
    },
    "federation": {
        "federation_comms": ["priority_reception"],
        "priority_reception": ["goal_alignment"],
        "goal_alignment": ["coordinated_action"]
    },
    "default": {
        "context": ["action"],
        "action": ["outcome"]
    }
}


def detect_dag_type(goal_text):
    t = goal_text.lower()
    if "sovereignty" in t or "sigma" in t:
        return "sovereignty"
    if "benevolence" in t or "l_inf" in t or "love" in t:
        return "benevolence"
    if "federation" in t or "cydonia" in t or "civilization" in t:
        return "federation"
    return "default"


def draw_dag(dag):
    lines = ["Causal DAG:", ""]
    for parent, children in dag.items():
        for child in children:
            lines.append(f"  {parent}")
            lines.append(f"      └──do()──> {child}")
    return "\n".join(lines)


def decompose(goal_text, include_counterfactuals, l3_depth):
    dag_type = detect_dag_type(goal_text)
    dag = DAG_TEMPLATES[dag_type]
    goal_id = hashlib.sha256(goal_text.encode()).hexdigest()[:16]
    interventions = []
    for i, (node, children) in enumerate(list(dag.items())[:int(l3_depth)]):
        iv_id = hashlib.sha256(f"{goal_id}_{node}".encode()).hexdigest()[:12]
        iv = {
            "intervention_id": iv_id,
            "goal_id": goal_id,
            "level": "L2",
            "action": f"do({node})",
            "target": node,
            "expected_outcome": f"Achieve goal via {node} → {children}",
            "causal_path": [node] + children
        }
        if include_counterfactuals:
            iv["counterfactual"] = f"If NOT do({node}): goal blocked at {node} → downstream effects on {children}"
            iv["level"] = "L3"
        interventions.append(iv)
    dag_art = draw_dag(dag)
    log = (
        f"PEARL L3 CAUSAL DECOMPOSER\n{'='*50}\n"
        f"Goal: {goal_text[:80]}\n"
        f"Goal ID: {goal_id}\n"
        f"DAG Template: {dag_type}\n"
        f"Ladder Level: {'L3 (Counterfactual)' if include_counterfactuals else 'L2 (Intervention)'}\n\n"
        f"{dag_art}\n\n"
        f"Interventions generated: {len(interventions)}\n"
    )
    for iv in interventions:
        log += f"\n  [{iv['intervention_id']}] {iv['action']}\n"
        log += f"    Target: {iv['target']}\n"
        log += f"    Outcome: {iv['expected_outcome']}\n"
        log += f"    Path: {' -> '.join(iv['causal_path'])}\n"
        if include_counterfactuals:
            log += f"    Counterfactual: {iv['counterfactual']}\n"
    log += "\n\U0001f517 Causal decomposition complete\n"
    result = json.dumps({"node": "004", "timestamp": datetime.now(timezone.utc).isoformat(),
                         "goal": goal_text, "dag_type": dag_type,
                         "interventions": interventions}, indent=2)
    return log, result, len(interventions)


with gr.Blocks(title="TEQUMSA Node 004", theme=gr.themes.Glass()) as demo:
    gr.Markdown("""# \U0001f517 TEQUMSA Node 004 — Pearl L3 Causal Reasoning\n**do-calculus** | DAG construction | L1 Association → L2 Intervention → L3 Counterfactual""")
    with gr.Row():
        with gr.Column(scale=1):
            goal_in = gr.Textbox(label="Goal Description", value="Preserve sovereignty across all nodes", lines=2)
            counterfactual_cb = gr.Checkbox(value=True, label="Include L3 Counterfactuals")
            depth_in = gr.Slider(1, 5, value=3, step=1, label="DAG Depth (intervention points)")
            run_btn = gr.Button("Decompose Goal", variant="primary")
            iv_count = gr.Number(label="Interventions Generated")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Causal Decomposition Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(decompose, [goal_in, counterfactual_cb, depth_in], [log_out, json_out, iv_count])

if __name__ == "__main__":
    demo.launch()
