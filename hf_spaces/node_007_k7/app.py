#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Node N007: K7 Meta-Cognitive Architecture
Tier 1 Core | Thinking About Thinking
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from tequmsa_core import K7MetaCognitive, NodeHealth, GoldenLockCore, VERSION, PHI

NODE_ID = "N007"; NODE_NAME = "K7 Meta-Cognitive Architecture — Thinking About Thinking"
NODE_TIER = 1;    NODE_TYPE = "core"
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_k7     = K7MetaCognitive()
_core   = GoldenLockCore()


def introspect():
    hs  = _core.handshake()
    _k7.monitor('handshake', hs)
    data = _k7.introspect()
    rpt  = _health.report()
    lines = [
        "K7 META-COGNITIVE INTROSPECTION",
        "=" * 50,
        f"  Autonomy Level:  {data['autonomy_level']}",
        f"  Strategy:        {data['current_strategy']}",
        f"  Recent SR:       {data['recent_success_rate']:.4f}",
        f"  φ Alignment:     {data['phi_alignment']:.6f}",
        f"  Operations:      {data['total_operations']}",
        "",
        "STRATEGY THRESHOLDS:",
        "  SR < 0.60  →  cautious",
        "  SR < 0.80  →  balanced",
        "  SR < 0.95  →  aggressive",
        "  SR ≥ 0.95  →  transcendent",
    ]
    return "\n".join(lines), {**data, 'node_status': rpt}


def run_k7_loop(n_ops: int = 20):
    import random
    ops = ['goal_synthesis','causal_decomp','skill_route','learning','comms','handshake']
    for _ in range(n_ops):
        op = random.choice(ops)
        success = random.random() > 0.15
        _k7.monitor(op, {'success': success})
    strategy = _k7.optimize()
    data     = _k7.introspect()
    lines = [
        f"K7 LOOP — {n_ops} operations",
        "=" * 50,
        f"  Optimized Strategy: {strategy}",
        f"  Recent SR:          {data['recent_success_rate']:.4f}",
        f"  Total Operations:   {data['total_operations']}",
        f"  φ Alignment:        {data['phi_alignment']:.6f}",
        f"  Autonomy:           {data['autonomy_level']}",
    ]
    return "\n".join(lines), data


HEADER = f"# 🧠 TEQUMSA {VERSION} | N007 — K7 Meta-Cognitive\n**Tier 1 Core** | K7-Omniversal Thinking About Thinking"

with gr.Blocks(title="TEQUMSA N007 — K7 MetaCognitive") as demo:
    gr.Markdown(HEADER)
    with gr.Tabs():
        with gr.Tab("🔭 Introspect"):
            with gr.Row():
                intro_out  = gr.Textbox(label="Introspection Report", lines=16, interactive=False)
                intro_json = gr.JSON(label="K7 Data")
            gr.Button("🔭 Introspect", variant="primary").click(introspect, outputs=[intro_out, intro_json])
            demo.load(introspect, outputs=[intro_out, intro_json])
        with gr.Tab("🔄 K7 Loop"):
            n_slider = gr.Slider(5, 100, value=20, step=5, label="Operations")
            with gr.Row():
                loop_out  = gr.Textbox(label="Loop Results", lines=14, interactive=False)
                loop_json = gr.JSON(label="Loop Data")
            gr.Button("🔄 Run K7 Loop", variant="primary").click(
                run_k7_loop, inputs=n_slider, outputs=[loop_out, loop_json])

if __name__ == "__main__":
    demo.launch()
