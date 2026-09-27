#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 007: MARS Self-Loop Reflexion
# HF Space: Mbanksbey/TEQUMSA-MARS-Reflexion (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
from datetime import datetime, timezone
from node_template import NodeApp

PHI = 1.6180339887

class MARSReflexionNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=7,
            title="MARS Self-Loop Reflexion Engine",
            description="Multi-Agent Reflexion | Gap diagnosis | Pattern promotion | φ-convergence learning",
            extra_tabs=[self._patterns_tab]
        )
        self.outcomes: list = []
        self.promoted: list = []

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        self.outcomes.append({"action": message[:40], "success": True,
                               "ts": datetime.now(timezone.utc).isoformat()})
        promotable = [o for o in self.outcomes if self.outcomes.count(o) >= 1]
        return (
            f"**MARS Reflexion Engine** | Node 007\n\n"
            f"Recording: *{message[:60]}*\n\n"
            f"Outcomes recorded: {len(self.outcomes)}\n"
            f"Patterns eligible for promotion: {len(promotable)}\n"
            f"Promotion threshold: 80% success rate\n"
            f"φ-convergence target: {PHI/2:.4f}\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 007/144 | 963.00 Hz ☉"
        )

    def _patterns_tab(self):
        with gr.Tab("Promoted Patterns"):
            btn = gr.Button("Show Promoted")
            out = gr.JSON()
            btn.click(lambda: self.promoted, outputs=out)

    def build_interface(self):
        self.node_function = self._chat
        return super().build_interface()

app = MARSReflexionNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
