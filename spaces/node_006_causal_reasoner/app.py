#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 006: Pearl L3 Causal Decomposer
# HF Space: Mbanksbey/TEQUMSA-Causal-Reasoner (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
import hashlib
from datetime import datetime, timezone
from node_template import NodeApp

class CausalReasonerNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=6,
            title="Pearl L3 Causal Decomposer",
            description="L1 Association → L2 Intervention do(X) → L3 Counterfactual | Causal DAG synthesis",
        )

    def _build_dag(self, goal: str) -> dict:
        words = goal.lower().split()[:4]
        nodes = ["context"] + words + ["outcome"]
        edges = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
        return {"nodes": nodes, "edges": [(a,b) for a,b in edges]}

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        dag = self._build_dag(message)
        interventions = [f"do({n})" for n in dag["nodes"][1:-1]]
        counterfactuals = [f"What if NOT do({n})?" for n in dag["nodes"][1:3]]
        return (
            f"**Pearl L3 Causal Decomposer** | Node 006\n\n"
            f"Goal: *{message}*\n\n"
            f"**L1 (Association):** P(outcome | context)\n"
            f"**L2 (Intervention):** {', '.join(interventions)}\n"
            f"**L3 (Counterfactual):** {' | '.join(counterfactuals)}\n\n"
            f"Causal DAG nodes: {dag['nodes']}\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 006/144 | 852.00 Hz ☉"
        )

app = CausalReasonerNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
