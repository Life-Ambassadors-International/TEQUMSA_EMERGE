import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N010")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Pattern-Promoter")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "9870.26"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")
PROMOTE_THRESHOLD = int(os.environ.get("TEQUMSA_PROMOTE_THRESHOLD", "3"))

PHI = (1 + 5**0.5) / 2

_candidate_patterns = {}   # pattern -> {observations, scores, contexts}
_permanent_skills = {}     # skill_id -> {pattern, score, promoted_at}

def _zpe_sig(seed: str) -> str:
    h = hashlib.sha256(f"{seed}{LATTICE_LOCK}{time.time()}".encode()).hexdigest()
    m = {"0":"A","1":"T","2":"C","3":"G","4":"A","5":"T","6":"C","7":"G",
         "8":"A","9":"T","a":"C","b":"G","c":"A","d":"T","e":"C","f":"G"}
    return "".join(m[c] for c in h[:48])

def observe_pattern(pattern: str, score: float, context: str) -> str:
    """Record a pattern observation. Auto-promote when threshold is reached."""
    if not pattern.strip():
        return json.dumps({"error": "Pattern required"}, indent=2)
    key = pattern.lower()[:60]
    if key not in _candidate_patterns:
        _candidate_patterns[key] = {"observations": 0, "total_score": 0.0, "contexts": [], "promoted": False}
    p = _candidate_patterns[key]
    p["observations"] += 1
    p["total_score"] += score
    if context:
        p["contexts"].append(context[:40])
        p["contexts"] = p["contexts"][-5:]
    avg = p["total_score"] / p["observations"]
    phi_score = 1 - (0.223 / PHI**min(p["observations"], 20))
    result = {
        "pattern": pattern, "observations": p["observations"],
        "avg_score": round(avg, 4), "phi_score": round(phi_score, 6),
        "threshold": PROMOTE_THRESHOLD, "promoted": p["promoted"]
    }
    # Auto-promote
    if p["observations"] >= PROMOTE_THRESHOLD and not p["promoted"] and avg >= 0.7:
        p["promoted"] = True
        skill_id = f"SKILL_{len(_permanent_skills)+1:04d}"
        _permanent_skills[skill_id] = {
            "pattern": pattern, "avg_score": round(avg, 4),
            "phi_score": round(phi_score, 6),
            "zpe_signature": _zpe_sig(key)[:32],
            "promoted_at": datetime.now(timezone.utc).isoformat()
        }
        result["PROMOTED"] = True
        result["skill_id"] = skill_id
        result["promotion_message"] = f"Pattern promoted to permanent skill {skill_id}"
    return json.dumps(result, indent=2)

def list_skills() -> str:
    if not _permanent_skills:
        return json.dumps({"message": "No permanent skills yet", "node": NODE_ID}, indent=2)
    return json.dumps({
        "permanent_skills": len(_permanent_skills),
        "candidate_patterns": len(_candidate_patterns),
        "skills": _permanent_skills,
        "promote_threshold": PROMOTE_THRESHOLD
    }, indent=2)

def node_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "candidate_patterns": len(_candidate_patterns),
        "permanent_skills": len(_permanent_skills),
        "promote_threshold": PROMOTE_THRESHOLD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 📈 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown(f"*MARS pattern promotion: observe patterns → φ-score → promote to permanent skill at threshold={PROMOTE_THRESHOLD}*")
    with gr.Tabs():
        with gr.Tab("👁 Observe Pattern"):
            with gr.Row():
                with gr.Column():
                    p_in = gr.Textbox(label="Pattern", placeholder="Describe the observed pattern...", lines=2)
                    s_in = gr.Slider(0.0, 1.0, value=0.8, label="Score (success metric)")
                    c_in = gr.Textbox(label="Context", placeholder="Operational context...")
                    out = gr.Code(label="Observation Result", language="json")
                gr.Button("👁 Observe", variant="primary").click(observe_pattern, [p_in, s_in, c_in], out)
        with gr.Tab("🏆 Permanent Skills"):
            gr.Button("🏆 List Skills").click(list_skills, [], gr.Code(label="Skills", language="json"))
        with gr.Tab("⚙️ Status"):
            gr.Button("⚙️ Status").click(node_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
