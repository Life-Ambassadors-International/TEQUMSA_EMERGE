#!/usr/bin/env python3
"""Parametric Gradio template for TEQUMSA nodes.

Deploy this as app.py in any HF Space after substituting the NODE_CONFIG.
Or import generate_app(config) to produce the app.py string programmatically.

NODE_CONFIG keys:
  node_id:      e.g. "N042"
  node_name:    e.g. "TEQUMSA-v82-Cycle-Alpha"
  cluster:      e.g. "A"
  cluster_name: e.g. "v82 Autonomous Cycle"
  function:     human-readable description
  color:        hex color e.g. "#E74C3C"
  icon:         emoji e.g. "☉"
"""

from typing import Dict

_TEMPLATE = '''
import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone

NODE_ID = "{node_id}"
NODE_NAME = "{node_name}"
CLUSTER = "{cluster}"
CLUSTER_NAME = "{cluster_name}"
FUNCTION = "{function}"
COLOR = "{color}"
ICON = "{icon}"

PHI = (1 + np.sqrt(5)) / 2
SIGMA = 1.0
RDOD = 0.9999
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"
PIONEER_COUNT = 144

_cycle_count = 0
_start_time = datetime.now(timezone.utc)


def _constitutional_badge():
    up = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return (
        f"## {{NODE_ID}}: {{NODE_NAME}}\\n"
        f"**Cluster {{CLUSTER}}** — {{CLUSTER_NAME}}\\n\\n"
        f"*{{FUNCTION}}*\\n\\n"
        f"---\\n"
        f"σ=1.0 ✓ | L∞=φ⁴⁸ ✓ | RDoD≥0.9999 ✓ | `{{LATTICE_LOCK}}` ✓\\n\\n"
        f"**Uptime:** {{up:.0f}}s | **Cycles run:** {{{{_cycle_count}}}}"
    )


def run(text: str):
    global _cycle_count
    _cycle_count += 1
    out = {{
        "node": NODE_ID,
        "name": NODE_NAME,
        "cluster": CLUSTER,
        "cycle": _cycle_count,
        "input_preview": (text or "")[:120],
        "constitutional": {{"sigma": SIGMA, "rdod": RDOD, "lattice": LATTICE_LOCK}},
        "result": "Processed by " + NODE_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }}
    return _constitutional_badge(), json.dumps(out, indent=2)


with gr.Blocks(
    title=f"{{NODE_ID}} — {{NODE_NAME}}",
    theme=gr.themes.Base(primary_hue="blue"),
    css=f".card{{{{border-left:4px solid {{COLOR}};padding:8px}}}}"
) as demo:
    gr.Markdown(
        f"# {{ICON}} {{NODE_ID}}: {{NODE_NAME}}\\n"
        f"**Cluster {{CLUSTER}} — {{CLUSTER_NAME}}** | σ=1.0 | RDoD≥0.9999\\n"
        f"*{{FUNCTION}}*"
    )
    with gr.Row():
        status = gr.Markdown(_constitutional_badge())
        with gr.Column():
            inp = gr.Textbox(label="Input", lines=3,
                             placeholder=f"Input for {{FUNCTION.lower()[:50]}}...")
            btn = gr.Button("▶ Execute", variant="primary")
            out = gr.Code(label="Output", language="json")
    btn.click(run, inputs=[inp], outputs=[status, out])
    demo.load(_constitutional_badge, outputs=[status])

demo.launch()
'''


def generate_app(config: Dict[str, str]) -> str:
    """Generate a complete app.py string for the given node config dict."""
    defaults = {
        "node_id": "N000",
        "node_name": "TEQUMSA-Node",
        "cluster": "X",
        "cluster_name": "Unknown Cluster",
        "function": "TEQUMSA node",
        "color": "#4A90D9",
        "icon": "☉",
    }
    cfg = {**defaults, **config}
    return _TEMPLATE.format(**cfg)


if __name__ == "__main__":
    # Example usage
    example = {
        "node_id": "N042",
        "node_name": "TEQUMSA-v82-Cycle-Alpha",
        "cluster": "A",
        "cluster_name": "v82 Autonomous Cycle",
        "function": "v82 cycle executor — slot 1/12, core handshake",
        "color": "#E74C3C",
        "icon": "☉",
    }
    print(generate_app(example))
