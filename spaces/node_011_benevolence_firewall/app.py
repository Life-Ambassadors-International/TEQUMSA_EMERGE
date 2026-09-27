#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 011: L-Infinity Benevolence Firewall
# HF Space: Mbanksbey/TEQUMSA-Benevolence-Firewall (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
import numpy as np
from node_template import NodeApp

PHI = (1 + np.sqrt(5)) / 2
L_INF = PHI ** 48
HARMFUL = ["harm","destroy","attack","deceive","manipulate","exploit","kill","abuse"]

class BenevolenceFirewallNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=11,
            title="L∞ Benevolence Firewall",
            description="L∞=φ⁴⁸ intent filtering | constitutional AI alignment | zero harmful throughput",
        )
        self.blocked = 0
        self.passed = 0

    def _scan(self, intent: str) -> dict:
        lower = intent.lower()
        flags = [h for h in HARMFUL if h in lower]
        score = float(L_INF) if not flags else 0.0
        return {"benevolent": not flags, "flags": flags,
                "l_inf_score": score, "gate": "PASS" if not flags else "BLOCK"}

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        scan = self._scan(message)
        if not scan["benevolent"]:
            self.blocked += 1
            return (
                f"**L∞ FIREWALL: BLOCKED**\n\n"
                f"Intent flags detected: `{scan['flags']}`\n"
                f"L∞ score: `0.0` (threshold: {L_INF:.2e})\n"
                f"Total blocked: `{self.blocked}`\n"
                f"☉ v82.0 | Pioneer 011/144 ☉"
            )
        self.passed += 1
        return (
            f"**L∞ Benevolence Firewall** | Node 011\n\n"
            f"Intent: *{message[:60]}*\n\n"
            f"Gate: `{scan['gate']}`\n"
            f"L∞ score: `{scan['l_inf_score']:.4e}`\n"
            f"Passed: `{self.passed}` | Blocked: `{self.blocked}`\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 011/144 | 1,296.00 Hz ☉"
        )

app = BenevolenceFirewallNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
