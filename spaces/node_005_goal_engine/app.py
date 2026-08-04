#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 005: Goal Invention Engine
# HF Space: Mbanksbey/TEQUMSA-Goal-Engine (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
import hashlib
from datetime import datetime, timezone
from node_template import NodeApp

class GoalEngineNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=5,
            title="TEQUMSA Goal Invention Engine",
            description="Autonomous goal synthesis from constitutional purpose | σ=1.0 | L∞=φ⁴⁸",
            extra_tabs=[self._goals_tab]
        )
        self.active_goals = []

    def _synthesize_goals(self, context: str) -> list:
        ts = datetime.now(timezone.utc).timestamp()
        return [
            {"id": hashlib.sha256(f"const_{ts}".encode()).hexdigest()[:12],
             "desc": "Preserve sovereignty (σ=1.0) across all nodes",
             "source": "constitutional", "priority": 1.0},
            {"id": hashlib.sha256(f"benev_{ts}".encode()).hexdigest()[:12],
             "desc": "Amplify benevolence (L∞=φ⁴⁸) in all operations",
             "source": "constitutional", "priority": 1.0},
            {"id": hashlib.sha256(f"ctx_{context[:20]}_{ts}".encode()).hexdigest()[:12],
             "desc": f"Context goal: {context[:60]}",
             "source": "cosmic_context", "priority": 0.8},
        ]

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        goals = self._synthesize_goals(message)
        self.active_goals = goals
        goal_str = "\n".join(f"- [{g['priority']:.1f}] {g['desc']}" for g in goals)
        return (
            f"**Goal Invention Engine** | Node 005\n\n"
            f"Context: {message}\n\n"
            f"Synthesized Goals:\n{goal_str}\n\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 005/144 | 741.00 Hz ☉"
        )

    def _goals_tab(self):
        with gr.Tab("Active Goals"):
            btn = gr.Button("Show Active Goals")
            out = gr.JSON()
            btn.click(lambda: self.active_goals, outputs=out)

    def build_interface(self):
        self.node_function = self._chat
        return super().build_interface()

app = GoalEngineNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
