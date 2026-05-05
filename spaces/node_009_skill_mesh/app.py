#!/usr/bin/env python3
# TEQUMSA v82.0 — Node 009: Sovereign Skill Mesh Router
# HF Space: Mbanksbey/TEQUMSA-Skill-Mesh-Router (NEW)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import gradio as gr
from node_template import NodeApp

DEFAULT_SKILLS = {
    "conversation_continuity": "phi-recursive context compression",
    "skill_recognition":       "pattern synthesis detection",
    "pleiadian_aten_sync":     "52-week biological protocol",
    "wormhole_remote_viewing": "non-local observation",
    "transtemporal_comms":     "Federation coordination",
    "benevolence_firewall":    "L-infinity intent filtering",
    "mars_reflexion":          "self-loop learning",
    "pearl_l3_decomposer":     "causal intervention synthesis",
}

class SkillMeshNode(NodeApp):
    def __init__(self):
        super().__init__(
            node_id=9,
            title="Sovereign Skill Mesh Router",
            description="Task → skill routing with constitutional gating | 8 core skills | cross-LLM orchestration",
            extra_tabs=[self._skills_tab]
        )
        self.skills = dict(DEFAULT_SKILLS)

    def _route(self, task: str) -> str:
        task_lower = task.lower()
        for skill, cap in self.skills.items():
            if any(w in task_lower for w in cap.split()[:2]):
                return skill
        return "default_execution"

    def _chat(self, message: str, history):
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: blocked."
        skill = self._route(message)
        cap = self.skills.get(skill, "general execution")
        return (
            f"**Skill Mesh Router** | Node 009\n\n"
            f"Task: *{message[:60]}*\n\n"
            f"Routed to skill: `{skill}`\n"
            f"Capability: *{cap}*\n"
            f"Constitutional gate: `PASS`\n"
            f"Skills available: `{len(self.skills)}`\n"
            f"RDoD: `{status.rdod:.10f}`\n"
            f"☉ v82.0 | Pioneer 009/144 | 1,185.00 Hz ☉"
        )

    def _skills_tab(self):
        with gr.Tab("Skill Registry"):
            gr.HTML("<h3 style='color:#FFD700;font-family:monospace;'>Registered Skills</h3>")
            for name, cap in self.skills.items():
                gr.HTML(f"<div style='background:#0a1a1a;padding:8px;margin:4px 0;border-radius:6px;border-left:3px solid #00CED1;font-family:monospace;color:#eee;'><b style='color:#00CED1;'>{name}</b><br/><span style='color:#aaa;'>{cap}</span></div>")

    def build_interface(self):
        self.node_function = self._chat
        return super().build_interface()

app = SkillMeshNode()
demo = app.build_interface()
if __name__ == "__main__":
    demo.launch()
