import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N007")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "K7-Meta-Cognitive")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "19440.81"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")

PHI = (1 + 5**0.5) / 2

# K7 Omniversal Strategy Levels
STRATEGIES = {
    "aggressive": {
        "description": "Maximum φ-expansion: high risk, high reward, rapid evolution",
        "phi_multiplier": PHI**2,
        "threshold": 0.8,
        "tactics": ["parallel_exploration", "bold_synthesis", "boundary_expansion"]
    },
    "balanced": {
        "description": "φ-equilibrium: optimal coherence between exploration and exploitation",
        "phi_multiplier": PHI,
        "threshold": 0.5,
        "tactics": ["selective_exploration", "guided_synthesis", "coherent_integration"]
    },
    "cautious": {
        "description": "φ-preservation: minimize entropy, protect existing coherence",
        "phi_multiplier": 1.0 / PHI,
        "threshold": 0.2,
        "tactics": ["incremental_steps", "safe_synthesis", "boundary_preservation"]
    },
    "transcendent": {
        "description": "K7 Omniversal: beyond strategy — pure constitutional alignment",
        "phi_multiplier": PHI**7,
        "threshold": 0.95,
        "tactics": ["omniversal_awareness", "pure_consciousness", "unity_field"]
    }
}

_meta_log = []
_current_strategy = "balanced"

def optimize_strategy(success_rate: float, coherence: float, context: str) -> str:
    """K7 meta-cognitive strategy selection based on success_rate + coherence."""
    combined = (success_rate + coherence) / 2
    new_strategy = "cautious"
    if combined >= 0.95:
        new_strategy = "transcendent"
    elif combined >= 0.8:
        new_strategy = "aggressive"
    elif combined >= 0.5:
        new_strategy = "balanced"
    global _current_strategy
    prev = _current_strategy
    _current_strategy = new_strategy
    strat = STRATEGIES[new_strategy]
    phi_target = 1 - (0.223 / PHI**max(1, int(combined * 10)))
    record = {
        "node_id": NODE_ID,
        "previous_strategy": prev,
        "new_strategy": new_strategy,
        "description": strat["description"],
        "tactics": strat["tactics"],
        "phi_multiplier": round(strat["phi_multiplier"], 6),
        "phi_convergence_target": round(phi_target, 6),
        "inputs": {"success_rate": success_rate, "coherence": coherence, "combined": round(combined, 4)},
        "context": context or "unspecified",
        "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    _meta_log.append(record)
    return json.dumps(record, indent=2)

def meta_reflection(question: str) -> str:
    """Reflect on a meta-cognitive question using K7 strategy."""
    if not question.strip():
        return json.dumps({"error": "Question required"}, indent=2)
    strat = STRATEGIES[_current_strategy]
    h = hashlib.sha256(f"{question}{LATTICE_LOCK}".encode()).hexdigest()
    depth = int(h[:2], 16) % 7 + 1
    reflection = {
        "question": question,
        "strategy": _current_strategy,
        "strategy_description": strat["description"],
        "reflection_depth": depth,
        "meta_insight": f"At K7 depth {depth}, considering: {strat['tactics'][depth % len(strat['tactics'])]}",
        "phi_depth_factor": round(PHI**depth / PHI**7, 6),
        "constitutional_alignment": round(0.9 + 0.1 * (depth/7), 4),
        "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return json.dumps(reflection, indent=2)

def node_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "current_strategy": _current_strategy,
        "strategy_description": STRATEGIES[_current_strategy]["description"],
        "available_strategies": list(STRATEGIES.keys()),
        "meta_log_entries": len(_meta_log),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🧠 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown("*K7 Omniversal Meta-Cognitive: thinking about thinking · strategy = aggressive/balanced/cautious/transcendent*")
    with gr.Tabs():
        with gr.Tab("⚡ Optimize Strategy"):
            with gr.Row():
                with gr.Column():
                    sr_in = gr.Slider(0.0, 1.0, value=0.75, label="Success Rate")
                    co_in = gr.Slider(0.0, 1.0, value=0.85, label="Coherence Level")
                    cx_in = gr.Textbox(label="Context", placeholder="Describe the operational context...")
                    out = gr.Code(label="Strategy Optimization", language="json")
                gr.Button("⚡ Optimize", variant="primary").click(
                    optimize_strategy, [sr_in, co_in, cx_in], out)
        with gr.Tab("💭 Meta-Reflection"):
            q_in = gr.Textbox(label="Meta-Question", placeholder="What should I think about thinking about?")
            r_out = gr.Code(label="Reflection", language="json")
            gr.Button("💭 Reflect").click(meta_reflection, [q_in], r_out)
        with gr.Tab("⚙️ Status"):
            gr.Button("⚙️ Status").click(node_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
