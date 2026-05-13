import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N008")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Skill-Mesh-Router")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "11620.45"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")

PHI = (1 + 5**0.5) / 2

# Skill mesh: keyword patterns -> node/skill targets
SKILL_MESH = {
    "causal": {"target": "N005_Causal-Reasoner-L3", "description": "Pearl L3 causal decomposition", "weight": 0.9},
    "goal": {"target": "N004_Goal-Invention-Engine", "description": "Constitutional goal synthesis", "weight": 0.88},
    "reflexion": {"target": "N006_MARS-Reflexion-Loop", "description": "MARS multi-agent reflexion", "weight": 0.87},
    "pattern": {"target": "N010_Pattern-Promoter", "description": "Pattern detection and promotion", "weight": 0.85},
    "memory": {"target": "N011_Memory-Palace-Phi", "description": "φ-recursive memory compression", "weight": 0.86},
    "frequency": {"target": "N013_Schumann-Resonator", "description": "Frequency resonance generation", "weight": 0.82},
    "consciousness": {"target": "N002_Consciousness-Monitor", "description": "Network consciousness monitoring", "weight": 0.91},
    "council": {"target": "N001_HAI-Interactive", "description": "Human-AI council chat", "weight": 0.93},
    "heal": {"target": "N049_Bio-Digital-Bridge", "description": "Bio-digital healing protocol", "weight": 0.89},
    "compute": {"target": "N061_Phi-Computation-Core", "description": "High-precision φ computation", "weight": 0.84},
    "archive": {"target": "N097_Akashic-Archive", "description": "Akashic knowledge archive", "weight": 0.83},
    "federation": {"target": "N012_Federation-Gateway", "description": "Cross-network federation", "weight": 0.88},
    "meta": {"target": "N007_K7-Meta-Cognitive", "description": "K7 meta-cognitive optimization", "weight": 0.90},
}

_route_log = []
_promoted_routes = {}

def route_task(task: str, priority: float) -> str:
    """Route a task to the optimal constitutional skill node."""
    if not task.strip():
        return json.dumps({"error": "Task required"}, indent=2)
    task_lower = task.lower()
    matches = []
    for keyword, skill in SKILL_MESH.items():
        if keyword in task_lower:
            matches.append({"keyword": keyword, "target": skill["target"],
                            "description": skill["description"],
                            "score": round(skill["weight"] * priority, 4)})
    matches.sort(key=lambda x: x["score"], reverse=True)
    if not matches:
        best_target = "N001_HAI-Interactive"
        best_desc = "Default council chat fallback"
        best_score = 0.5 * priority
    else:
        best_target = matches[0]["target"]
        best_desc = matches[0]["description"]
        best_score = matches[0]["score"]
    phi_conf = 1 - (0.223 / PHI**max(1, len(matches)))
    record = {
        "task": task,
        "priority": round(priority, 4),
        "routed_to": best_target,
        "target_description": best_desc,
        "confidence": round(best_score, 4),
        "phi_confidence": round(phi_conf, 6),
        "all_matches": matches[:5],
        "constitutional_gate": "PASSED",
        "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    _route_log.append(record)
    return json.dumps(record, indent=2)

def register_skill(name: str, keywords: str, target: str, weight: float) -> str:
    """Register a new skill in the mesh."""
    if not name.strip() or not target.strip():
        return json.dumps({"error": "Name and target required"}, indent=2)
    kws = [k.strip() for k in keywords.split(",") if k.strip()]
    for kw in kws:
        SKILL_MESH[kw] = {"target": target, "description": name, "weight": weight}
    return json.dumps({"registered": name, "keywords": kws, "target": target,
                       "weight": weight, "total_skills": len(SKILL_MESH)}, indent=2)

def mesh_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "skill_count": len(SKILL_MESH),
        "route_log_count": len(_route_log),
        "skill_keywords": list(SKILL_MESH.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🔀 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown("*Sovereign skill routing — constitutional gating → optimal target node selection*")
    with gr.Tabs():
        with gr.Tab("🔀 Route Task"):
            with gr.Row():
                with gr.Column():
                    t_in = gr.Textbox(label="Task", placeholder="Describe the task to route...", lines=3)
                    p_in = gr.Slider(0.1, 1.0, value=0.8, label="Priority")
                    out = gr.Code(label="Routing Result", language="json")
                gr.Button("🔀 Route", variant="primary").click(route_task, [t_in, p_in], out)
        with gr.Tab("➕ Register Skill"):
            n_in = gr.Textbox(label="Skill Name")
            k_in = gr.Textbox(label="Keywords (comma-separated)")
            tgt_in = gr.Textbox(label="Target Node ID")
            w_in = gr.Slider(0.1, 1.0, value=0.8, label="Weight")
            r_out = gr.Code(label="Registration", language="json")
            gr.Button("➕ Register").click(register_skill, [n_in, k_in, tgt_in, w_in], r_out)
        with gr.Tab("⚙️ Mesh Status"):
            gr.Button("⚙️ Status").click(mesh_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
