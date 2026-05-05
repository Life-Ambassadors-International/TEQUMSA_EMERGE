#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 013: Central Organism Dashboard
# HF Space: Mbanksbey/TEQUMSA-Organism-Dashboard (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
import numpy as np
from datetime import datetime, timezone
from node_template import NodeApp, NODE_REGISTRY, NODE_TIERS

PHI = (1 + np.sqrt(5)) / 2
RDOD_GATE = 0.9999

class OrganismDashboardNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=13,
            title="TEQUMSA Organism Dashboard",
            description="Central orchestrator | 144-node health monitor | v82.0 autonomous cycle control",
            extra_tabs=[self._network_tab, self._cycle_tab]
        )

    def _simulate_network_health(self) -> dict:
        locked = 0
        nodes_status = {}
        for tier, ids in NODE_TIERS.items():
            for nid in ids:
                rdod = min(1.0, 0.9998 + np.random.uniform(0, 0.0003))
                locked += int(rdod >= RDOD_GATE)
                nodes_status[nid] = {"rdod": round(rdod, 8), "locked": rdod >= RDOD_GATE}
        return {
            "total_nodes": 144,
            "phase_locked": locked,
            "pct": round(locked / 144 * 100, 2),
            "sigma": 1.0,
            "l_inf": float(PHI**48),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        net = self._simulate_network_health()
        return (
            f"**TEQUMSA Organism Dashboard** | Node 013\n\n"
            f"Query: *{message[:60]}*\n\n"
            f"Network: `{net['phase_locked']}/144` phase-locked ({net['pct']}%)\n"
            f"σ: `{net['sigma']}` | L∞: `{net['l_inf']:.4e}`\n"
            f"Autonomous cycles: `ACTIVE`\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 013/144 | 23,514.26 Hz ☉"
        )

    def _network_tab(self):
        with gr.Tab("Network Health"):
            btn = gr.Button("Scan Network", variant="primary")
            out = gr.JSON(label="144-Node Network Status")
            btn.click(self._simulate_network_health, outputs=out)

    def _cycle_tab(self):
        with gr.Tab("Autonomous Cycles"):
            gr.HTML("""
            <div style='background:#0a0a1a;padding:16px;border-radius:8px;border:1px solid #FFD700;font-family:monospace;color:#eee;'>
              <h3 style='color:#FFD700;'>v82.0 Autonomous Cycle</h3>
              <ol style='color:#ccc;'>
                <li>v81 GHZ handshake (quantum coherence)</li>
                <li>Goal synthesis (constitutional + context)</li>
                <li>Pearl L3 causal decomposition</li>
                <li>Skill mesh routing</li>
                <li>Constitutional gating + execution</li>
                <li>MARS reflexion (learning)</li>
                <li>Pattern promotion to permanent skills</li>
                <li>K7 meta-cognitive optimization</li>
              </ol>
            </div>
            """)

    def build_interface(self):
        self.node_function = self._chat
        return super().build_interface()

app = OrganismDashboardNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
