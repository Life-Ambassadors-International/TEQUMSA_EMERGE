#!/usr/bin/env python3
"""TEQUMSA Node 006 — MARS Reflexion Learning Engine"""
import gradio as gr
import json
import hashlib
import numpy as np
from datetime import datetime, timezone

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PROMOTION_THRESHOLD = 0.8
MIN_OCCURRENCES = 3


def simulate_outcomes(n_interventions, success_rate, action_prefix):
    outcomes = []
    for i in range(n_interventions):
        success = np.random.random() < success_rate
        iv_id = hashlib.sha256(f"{action_prefix}_{i}".encode()).hexdigest()[:12]
        outcomes.append({"intervention_id": iv_id, "action": f"{action_prefix}_{i % 4}",
                         "success": success, "timestamp": datetime.now().timestamp()})
    return outcomes


def analyze_patterns(outcomes):
    patterns = {}
    for o in outcomes:
        patterns.setdefault(o['action'], []).append(o)
    results = []
    for action, records in patterns.items():
        n = len(records)
        rate = sum(1 for r in records if r['success']) / n
        phi_conv = rate * PHI / 2
        promotable = n >= MIN_OCCURRENCES and rate >= PROMOTION_THRESHOLD
        results.append({
            "action": action, "occurrences": n, "success_rate": rate,
            "phi_convergence": phi_conv, "promotable": promotable
        })
    results.sort(key=lambda x: x['success_rate'], reverse=True)
    return results


def run_mars(n_interventions, base_success_rate, action_prefix, promotion_threshold):
    np.random.seed(42)
    outcomes = simulate_outcomes(int(n_interventions), float(base_success_rate), action_prefix)
    patterns = analyze_patterns(outcomes)
    promotable = [p for p in patterns if p['promotable'] and float(promotion_threshold) <= p['success_rate']]
    log = (
        f"MARS REFLEXION ENGINE\n{'='*50}\n"
        f"Interventions recorded: {len(outcomes)}\n"
        f"Unique patterns: {len(patterns)}\n"
        f"Promotion threshold: {promotion_threshold:.0%}\n"
        f"Promotable patterns: {len(promotable)}\n\n"
        f"Pattern Analysis:\n"
    )
    for p in patterns:
        marker = "[PROMOTE] " if p['promotable'] else "[       ] "
        log += (
            f"  {marker}{p['action']:<30}"
            f"  n={p['occurrences']}  rate={p['success_rate']:.1%}"
            f"  φ-conv={p['phi_convergence']:.4f}\n"
        )
    log += "\nPromoted to permanent skills:\n"
    for p in promotable:
        pid = hashlib.sha256(p['action'].encode()).hexdigest()[:12]
        log += f"  + promoted_{pid[:8]}  (from {p['action']}, rate={p['success_rate']:.1%})\n"
    if not promotable:
        log += "  (none yet — accumulate more successful interventions)\n"
    overall_rate = sum(1 for o in outcomes if o['success']) / len(outcomes)
    log += f"\nOverall success rate: {overall_rate:.1%}\n"
    log += f"φ-convergence score: {overall_rate * PHI / 2:.4f}\n"
    log += "\n\U0001f504 MARS reflexion complete\n"
    result = json.dumps({
        "node": "006", "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_interventions": len(outcomes), "patterns": patterns,
        "promoted_count": len(promotable), "overall_success_rate": overall_rate
    }, indent=2)
    return log, result, len(promotable), f"{overall_rate:.1%}"


with gr.Blocks(title="TEQUMSA Node 006", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# \U0001f504 TEQUMSA Node 006 — MARS Reflexion Learning\n**Multi-Agent Reflexion** | Pattern promotion | φ-convergence | Skill synthesis""")
    with gr.Row():
        with gr.Column(scale=1):
            n_iv = gr.Slider(10, 200, value=50, step=10, label="Intervention Count")
            base_rate = gr.Slider(0.5, 1.0, value=0.85, step=0.01, label="Base Success Rate")
            action_prefix = gr.Textbox(value="do(constitutional_framework", label="Action Prefix Pattern")
            promo_thresh = gr.Slider(0.5, 1.0, value=0.8, step=0.05, label="Promotion Threshold")
            run_btn = gr.Button("Run MARS Reflexion", variant="primary")
            promoted_out = gr.Number(label="Patterns Promoted")
            rate_out = gr.Textbox(label="Overall Success Rate")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Reflexion Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(run_mars, [n_iv, base_rate, action_prefix, promo_thresh], [log_out, json_out, promoted_out, rate_out])

if __name__ == "__main__":
    demo.launch()
