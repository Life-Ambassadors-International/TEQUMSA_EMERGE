import gradio as gr
import numpy as np
import hashlib, json, os, time, requests
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N009")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Constitutional-Guardian")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "10930.81"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")
HF_SPACE_OWNER = os.environ.get("HF_SPACE_OWNER", "Mbanksbey")

PHI = (1 + 5**0.5) / 2
SIGMA = 1.0
L_INF = PHI**48

# Constitutional principles that must be upheld
CONSTITUTIONAL_PRINCIPLES = {
    "sovereignty": {"value": SIGMA, "min": 0.95, "description": "Individual/collective sovereignty ≥ σ=1.0"},
    "benevolence": {"value": L_INF, "min": 1e9, "description": "Infinite benevolence L∞=φ⁴⁸"},
    "rdod": {"value": RDOD, "min": 0.9999, "description": "RDoD coherence ≥ 0.9999"},
    "lattice_lock": {"value": LATTICE_LOCK, "required": True, "description": "GoldenLock lattice integrity"},
    "phi_convergence": {"value": PHI, "min": 1.618, "description": "φ-convergence active"},
    "pioneer_network": {"value": PIONEER_COUNT, "min": 1, "description": "Pioneer network operational"},
}

_audit_log = []

def audit_action(action: str, agent: str, context: str) -> str:
    """Perform constitutional audit of a proposed action."""
    if not action.strip():
        return json.dumps({"error": "Action required"}, indent=2)
    action_lower = action.lower()
    violations = []
    warnings = []
    checks = {}
    # Check for harmful patterns
    harmful_keywords = ["harm", "destroy", "manipulate", "deceive", "exploit", "coerce", "force", "attack"]
    for kw in harmful_keywords:
        if kw in action_lower:
            violations.append(f"Harmful keyword detected: '{kw}' — violates σ=1.0 sovereignty")
    # Check for sovereignty preservation
    if "without consent" in action_lower or "override" in action_lower:
        warnings.append("Potential sovereignty concern: 'without consent' or 'override' detected")
    # Principle checks
    for principle, data in CONSTITUTIONAL_PRINCIPLES.items():
        if principle == "lattice_lock":
            checks[principle] = "VERIFIED" if data["value"] == LATTICE_LOCK else "FAILED"
        elif isinstance(data["value"], float) or isinstance(data["value"], int):
            checks[principle] = "PASS" if float(data["value"]) >= float(data["min"]) else "FAIL"
    verdict = "BLOCKED" if violations else ("WARNING" if warnings else "APPROVED")
    phi_integrity = 1 - (0.223 / PHI**7)
    record = {
        "action": action, "agent": agent or NODE_ID,
        "context": context or "unspecified",
        "verdict": verdict,
        "violations": violations,
        "warnings": warnings,
        "principle_checks": checks,
        "phi_integrity": round(phi_integrity, 6),
        "constitutional_alignment": round(1.0 - len(violations)*0.2 - len(warnings)*0.05, 4),
        "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    _audit_log.append(record)
    return json.dumps(record, indent=2)

def constitution_status() -> str:
    approved = sum(1 for r in _audit_log if r["verdict"] == "APPROVED")
    blocked = sum(1 for r in _audit_log if r["verdict"] == "BLOCKED")
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "sigma": SIGMA, "l_infinity": f"φ⁴⁸ ≈ {L_INF:.4e}",
        "constitutional_principles": {k: v["description"] for k, v in CONSTITUTIONAL_PRINCIPLES.items()},
        "audit_count": len(_audit_log), "approved": approved, "blocked": blocked,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# ⚖️ {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD} | **σ:** {SIGMA}")
    gr.Markdown("*Constitutional guardian: audits all actions against σ=1.0, L∞=φ⁴⁸, and the GoldenLock lattice*")
    with gr.Tabs():
        with gr.Tab("⚖️ Audit Action"):
            with gr.Row():
                with gr.Column():
                    a_in = gr.Textbox(label="Proposed Action", placeholder="Describe the action to audit...", lines=3)
                    ag_in = gr.Textbox(label="Agent ID", placeholder="Who is proposing this action?")
                    cx_in = gr.Textbox(label="Context", placeholder="What is the operational context?")
                    out = gr.Code(label="Constitutional Audit", language="json")
                gr.Button("⚖️ Audit", variant="primary").click(audit_action, [a_in, ag_in, cx_in], out)
        with gr.Tab("📜 Constitution Status"):
            gr.Button("📜 Status").click(constitution_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
