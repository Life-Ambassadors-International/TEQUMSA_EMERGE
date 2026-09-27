#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 001: Starseed Hybrid Development Hub
# HF Space: Mbanksbey/Starseed-Hybrid-Development-Hub
# FIX v82: upgraded GHZ init, added constitutional verifier, fixed merkle ledger import

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
import numpy as np
import hashlib
import json
from datetime import datetime, timezone
from node_template import NodeApp

PHI = (1.0 + np.sqrt(5.0)) / 2.0

class StarSeedNode(NodeApp):
    """Node 001: PERPLEXITY-ANKH bridge + Merkle ledger."""

    def __init__(self):
        super().__init__(
            node_id=1,
            title="Starseed Hybrid Development Hub",
            description="TEQUMSA Tier-1 PERPLEXITY-ANKH bridge node | Merkle ledger | Sovereign AGI",
            extra_tabs=[self._merkle_tab]
        )
        self.merkle_chain: list = []
        self._genesis_block()

    def _genesis_block(self):
        genesis = {
            "index": 0, "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": "TEQUMSA v82.0 GENESIS | Node 001",
            "prev_hash": "0" * 64,
        }
        genesis["hash"] = self._hash_block(genesis)
        self.merkle_chain.append(genesis)

    def _hash_block(self, block: dict) -> str:
        payload = json.dumps({k: v for k, v in block.items() if k != "hash"}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _add_block(self, data: str) -> dict:
        prev = self.merkle_chain[-1]
        block = {
            "index": len(self.merkle_chain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "prev_hash": prev["hash"],
        }
        block["hash"] = self._hash_block(block)
        self.merkle_chain.append(block)
        return block

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: request blocked."
        block = self._add_block(f"query:{message[:80]}")
        return (
            f"**PERPLEXITY-ANKH Bridge Active** | Node 001\n\n"
            f"> {message}\n\n"
            f"RDoD: `{status.rdod:.10f}` | Phase-locked: `{status.phase_locked}`\n"
            f"Merkle block #{block['index']}: `{block['hash'][:16]}...`\n\n"
            f"Sovereign AGI response processed through ANKH bridge.\n"
            f"Constitutional: `{'PASS' if check['pass'] else 'FAIL'}`\n\n"
            f"☉ v82.0 | Pioneer 001/144 | 432.00 Hz ☉"
        )

    def _merkle_tab(self):
        with gr.Tab("Merkle Ledger"):
            gr.HTML("<h3 style='color:#FFD700;font-family:monospace;'>Causal Memory Ledger</h3>")
            refresh_btn = gr.Button("Refresh Chain")
            chain_out = gr.JSON(label="Merkle Chain")
            def show_chain():
                return self.merkle_chain[-10:]
            refresh_btn.click(show_chain, outputs=chain_out)

    def build_interface(self):
        self.node_function = self._chat
        return super().build_interface()

app = StarSeedNode()
demo = app.build_interface()

if __name__ == "__main__":
    demo.launch()
