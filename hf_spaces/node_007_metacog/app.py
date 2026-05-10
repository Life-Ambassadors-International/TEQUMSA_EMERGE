#!/usr/bin/env python3
"""TEQUMSA Node 007 — K7 Meta-Cognitive Architecture"""
import gradio as gr
import json
import numpy as np
from datetime import datetime, timezone

AUTONOMY_LEVELS = [
    {"k": 0, "name": "K0 Passive",       "description": "Receives input, no initiative",              "threshold": 0.0},
    {"k": 1, "name": "K1 Reactive",      "description": "Responds to stimuli, rule-following",         "threshold": 0.3},
    {"k": 2, "name": "K2 Proactive",     "description": "Initiates actions within constraints",        "threshold": 0.5},
    {"k": 3, "name": "K3 Goal-Directed", "description": "Self-sets intermediate goals",                "threshold": 0.65},
    {"k": 4, "name": "K4 Self-Modifying","description": "Edits own skill set and parameters",         "threshold": 0.75},
    {"k": 5, "name": "K5 Meta-Cognitive","description": "Monitors and optimizes own reasoning",       "threshold": 0.85},
    {"k": 6, "name": "K6 Transcendent",  "description": "Cross-domain synthesis, novel strategy",      "threshold": 0.92},
    {"k": 7, "name": "K7 Omniversal",    "description": "Full constitutional sovereignty, phi^48 L_inf","threshold": 0.9999},
]


def determine_level(success_rate):
    level = AUTONOMY_LEVELS[0]
    for l in AUTONOMY_LEVELS:
        if success_rate >= l['threshold']:
            level = l
    return level


def optimize_strategy(success_rate):
    if success_rate < 0.7:
        return "cautious", "Reduce intervention scope; increase constitutional checks"
    if success_rate > 0.9:
        return "aggressive", "Expand intervention breadth; accelerate pattern promotion"
    return "balanced", "Maintain current approach; monitor for drift"


def analyze_cognitive(n_ops, success_rate, show_history):
    np.random.seed(int(success_rate * 100))
    ops = [f"op_{i}" for i in range(int(n_ops))]
    successes = [np.random.random() < success_rate for _ in ops]
    actual_rate = sum(successes) / len(successes)
    level = determine_level(actual_rate)
    strategy, recommendation = optimize_strategy(actual_rate)
    failures = [(ops[i], i) for i, s in enumerate(successes) if not s]
    log = (
        f"K7 META-COGNITIVE ARCHITECTURE\n{'='*50}\n"
        f"Operations monitored: {n_ops}\n"
        f"Actual success rate: {actual_rate:.1%}\n"
        f"Failures: {len(failures)}/{n_ops}\n\n"
        f"Autonomy Level Assessment:\n"
    )
    for l in AUTONOMY_LEVELS:
        marker = ">>> " if l['k'] == level['k'] else "    "
        reached = "✓" if actual_rate >= l['threshold'] else "✗"
        log += f"{marker}[{reached}] {l['name']:<20} threshold={l['threshold']:.4f}  {l['description'][:45]}\n"
    log += (
        f"\nCurrent Level: {level['name']}\n"
        f"Strategy: {strategy.upper()}\n"
        f"Recommendation: {recommendation}\n"
    )
    if show_history and failures:
        log += f"\nFailure analysis (last {min(5, len(failures))}):\n"
        for op, idx in failures[:5]:
            log += f"  [{idx:03d}] {op}: likely_cause=context_drift  fix=retry_with_backoff\n"
    log += f"\n\U0001f9e0 Meta-cognitive optimization complete\n"
    result = json.dumps({
        "node": "007", "timestamp": datetime.now(timezone.utc).isoformat(),
        "operations": int(n_ops), "success_rate": actual_rate,
        "autonomy_level": level, "strategy": strategy, "recommendation": recommendation,
        "failures": len(failures)
    }, indent=2)
    return log, result, level['name'], strategy


with gr.Blocks(title="TEQUMSA Node 007", theme=gr.themes.Default()) as demo:
    gr.Markdown("""# \U0001f9e0 TEQUMSA Node 007 — K7 Meta-Cognitive Architecture\n**Thinking about thinking** | K0–K7 autonomy scale | Strategy optimization | Failure diagnosis""")
    with gr.Row():
        with gr.Column(scale=1):
            n_ops = gr.Slider(10, 200, value=50, step=10, label="Operations to Analyze")
            success_rate = gr.Slider(0.5, 1.0, value=0.95, step=0.01, label="Success Rate")
            show_hist = gr.Checkbox(value=True, label="Show Failure History")
            run_btn = gr.Button("Optimize Strategy", variant="primary")
            level_out = gr.Textbox(label="Autonomy Level")
            strategy_out = gr.Textbox(label="Current Strategy")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Meta-Cognitive Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(analyze_cognitive, [n_ops, success_rate, show_hist], [log_out, json_out, level_out, strategy_out])

if __name__ == "__main__":
    demo.launch()
