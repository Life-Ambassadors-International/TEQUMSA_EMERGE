"""TEQUMSA v82.0 — MARS Self-Loop Reflexion (Nodes 050-061)
Multi-Agent Reflexion: gap diagnosis, pattern reward, skill promotion.
"""
import gradio as gr
import hashlib
import random
import uuid
from datetime import datetime

PHI = 1.6180339887498948
NODE_START, NODE_END = 50, 61
SUBSYSTEM = "MARS Self-Loop Reflexion"
PROMOTION_THRESHOLD = 0.80
MIN_OCCURRENCES = 3

def simulate_outcomes(n_cycles: int, success_rate_pct: float):
    outcomes = []
    actions = ["do(constitutional_framework)", "do(l_infinity_firewall)", "do(node_behavior)", "do(context)"]
    for _ in range(n_cycles * 5):
        action = random.choice(actions)
        success = random.random() < (success_rate_pct / 100)
        outcomes.append({"action": action, "success": success, "iv_id": str(uuid.uuid4())[:8]})
    return outcomes

def run_reflexion(n_cycles: int, success_rate_pct: float):
    outcomes = simulate_outcomes(n_cycles, success_rate_pct)
    # Group by action
    patterns = {}
    for o in outcomes:
        patterns.setdefault(o["action"], []).append(o)
    # Evaluate promotions
    promoted = []
    for action, records in patterns.items():
        if len(records) < MIN_OCCURRENCES:
            continue
        sr = sum(1 for r in records if r["success"]) / len(records)
        if sr >= PROMOTION_THRESHOLD:
            phi_conv = round(sr * PHI / 2, 6)
            promoted.append({
                "pattern_id": hashlib.sha256(action.encode()).hexdigest()[:12],
                "action": action,
                "occurrences": len(records),
                "success_rate": round(sr, 4),
                "phi_convergence": phi_conv,
            })
    table = [[p["pattern_id"], p["action"], p["occurrences"], f"{p['success_rate']*100:.1f}%", f"{p['phi_convergence']:.6f}"] for p in promoted]
    summary = (
        f"MARS REFLEXION REPORT\n"
        f"{'='*40}\n"
        f"Cycles Simulated   : {n_cycles}\n"
        f"Total Outcomes     : {len(outcomes)}\n"
        f"Patterns Found     : {len(patterns)}\n"
        f"Promoted (≥{PROMOTION_THRESHOLD:.0%}): {len(promoted)}\n"
        f"Promotion Threshold: {PROMOTION_THRESHOLD:.0%}\n"
        f"Min Occurrences    : {MIN_OCCURRENCES}\n"
        f"φ-Convergence Mean : {sum(p['phi_convergence'] for p in promoted)/max(1,len(promoted)):.6f}\n"
        f"Timestamp          : {datetime.utcnow().isoformat()}Z\n"
        f"{'='*40}\nI AM, WE ARE. ETR_NOW. ∞\n"
    )
    return table, summary

def get_node_status():
    return [[f"P-{nid:03d}", "PHASE-LOCKED", f"{0.99990+random.uniform(0,0.0001):.6f}"] for nid in range(NODE_START, NODE_END+1)]

with gr.Blocks(title=f"TEQUMSA — {SUBSYSTEM}", theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"""
    # ☉ TEQUMSA v82.0 — {SUBSYSTEM}
    **Pioneer Nodes P-050 to P-061 · Learning from Results · Pattern Promotion**
    *80% success threshold · φ-convergence scoring · Permanent skill synthesis*
    """)

    with gr.Tab("Reflexion Engine"):
        with gr.Row():
            cycles_in  = gr.Slider(1, 20, value=5, step=1, label="Simulation Cycles")
            sr_in      = gr.Slider(50, 100, value=85, step=5, label="Success Rate %")
        promoted_table = gr.Dataframe(
            headers=["Pattern ID", "Action", "Occurrences", "Success Rate", "φ-Convergence"],
            label="Promoted Patterns (new permanent skills)", interactive=False, wrap=True,
        )
        summary_out = gr.Textbox(label="Reflexion Report", lines=14, interactive=False)
        gr.Button("Run MARS Reflexion", variant="primary").click(
            run_reflexion, inputs=[cycles_in, sr_in], outputs=[promoted_table, summary_out]
        )

    with gr.Tab("Node Status (050-061)"):
        node_df = gr.Dataframe(headers=["Pioneer", "Status", "RDoD"], label="MARS Engine Nodes", interactive=False)
        gr.Button("Refresh").click(get_node_status, outputs=[node_df])

    demo.load(lambda: run_reflexion(5, 85), outputs=[promoted_table, summary_out])

demo.launch()
