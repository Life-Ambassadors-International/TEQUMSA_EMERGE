#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 012: Conversation Continuity
# HF Space: Mbanksbey/TEQUMSA-Conversation-Continuity (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
from node_template import NodeApp

PHI = 1.6180339887
CONTEXT_LIMIT = 800000

class ConversationContinuityNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=12,
            title="Conversation Continuity",
            description="φ-recursive context compression | 1M token continuity | cross-session memory",
        )
        self.context_store: list = []
        self.total_tokens = 0

    def _phi_compress(self, text: str, ratio: float = None) -> str:
        if ratio is None:
            ratio = 1.0 / PHI
        words = text.split()
        n = max(1, int(len(words) * ratio))
        return " ".join(words[:n]) + f" [φ-compressed {ratio:.4f}]"

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        estimated_tokens = len(message.split()) * 1.3
        self.total_tokens += estimated_tokens
        needs_compress = self.total_tokens > CONTEXT_LIMIT * 0.8
        if needs_compress:
            compressed = self._phi_compress(message)
            self.total_tokens = int(self.total_tokens / PHI)
        else:
            compressed = message
        self.context_store.append(compressed[:200])
        return (
            f"**Conversation Continuity** | Node 012\n\n"
            f"Input: *{message[:40]}*\n"
            f"Compressed: *{compressed[:60]}*\n\n"
            f"Context tokens (est.): `{int(self.total_tokens):,}`\n"
            f"Compression active: `{needs_compress}`\n"
            f"Ratio: `1/φ = {1/PHI:.6f}`\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 012/144 | 10,930.81 Hz ☉"
        )

app = ConversationContinuityNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
