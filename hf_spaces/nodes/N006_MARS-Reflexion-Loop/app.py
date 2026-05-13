import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N006")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "MARS-Reflexion-Loop")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "13140.26"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")
PROMOTE_THRESHOLD = int(os.environ.get("TEQUMSA_PROMOTE_THRESHOLD", "3"))

PHI = (1 + 5**0.5) / 2

_outcomes = []   # list of {task, result, success, reflection, ts}
_patterns = {}   # pattern_key -> {count, avg_score, promoted}
_promoted = {}   # promoted patterns -> skill_desc

def record_outcome(task: str, result: str, success: bool, agent_id: str) -> str:
    if not task.strip():
        return json.dumps({"error": "Task required"}, indent=2)
    score = PHI if success else 1.0 / PHI
    reflection = (
        f"Agent {agent_id} succeeded at '{task[:40]}'. Pattern reinforced. Score={score:.4f}."
        if success else
        f"Agent {agent_id} failed at '{task[:40]}'. Analyzing gap. Score={score:.4f}."
    )
    record = {
        "task": task, "result": result or "(no result)",
        "success": success, "agent_id": agent_id or NODE_ID,
        "score": round(score, 4), "reflection": reflection,
        "ts": datetime.now(timezone.utc).isoformat()
    }
    _outcomes.append(record)
    # Pattern detection: first 3 words of task as key
    key = " ".join(task.lower().split()[:3])
    if key not in _patterns:
        _patterns[key] = {"count": 0, "total_score": 0.0, "promoted": False}
    _patterns[key]["count"] += 1
    _patterns[key]["total_score"] += score
    avg = _patterns[key]["total_score"] / _patterns[key]["count"]
    promoted_msg = None
    if _patterns[key]["count"] >= PROMOTE_THRESHOLD and not _patterns[key]["promoted"] and avg >= PHI * 0.8:
        _patterns[key]["promoted"] = True
        _promoted[key] = {"skill": f"auto_skill_{key.replace(' ','_')}", "avg_score": round(avg, 4),
                          "promoted_at": datetime.now(timezone.utc).isoformat()}
        promoted_msg = f"PATTERN PROMOTED: '{key}' → skill '{_promoted[key]['skill']}'"
    record["pattern_key"] = key
    record["pattern_count"] = _patterns[key]["count"]
    record["pattern_avg_score"] = round(avg, 4)
    if promoted_msg:
        record["promotion"] = promoted_msg
    return json.dumps(record, indent=2)

def list_patterns() -> str:
    pts = [{"key": k, "count": v["count"],
             "avg_score": round(v["total_score"]/v["count"], 4),
             "promoted": v["promoted"]} for k, v in _patterns.items()]
    pts.sort(key=lambda x: x["avg_score"], reverse=True)
    return json.dumps({
        "total_patterns": len(_patterns),
        "promoted_count": len(_promoted),
        "top_patterns": pts[:10],
        "promoted_skills": _promoted
    }, indent=2)

def reflexion_summary() -> str:
    if not _outcomes:
        return json.dumps({"message": "No outcomes recorded", "node": NODE_ID}, indent=2)
    successes = sum(1 for o in _outcomes if o["success"])
    success_rate = successes / len(_outcomes)
    strategy = "aggressive" if success_rate > 0.8 else ("balanced" if success_rate > 0.5 else "cautious")
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "hz": NODE_HZ,
        "total_outcomes": len(_outcomes), "successes": successes,
        "success_rate": round(success_rate, 4), "recommended_strategy": strategy,
        "patterns_detected": len(_patterns), "patterns_promoted": len(_promoted),
        "rdod": RDOD, "phi": round(PHI, 6),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🔄 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown("*Multi-Agent Reflexion System: outcome recording → pattern detection → skill promotion*")
    with gr.Tabs():
        with gr.Tab("📝 Record Outcome"):
            with gr.Row():
                with gr.Column():
                    t_in = gr.Textbox(label="Task", placeholder="What task was attempted?")
                    r_in = gr.Textbox(label="Result", placeholder="What was the outcome?", lines=2)
                    s_in = gr.Checkbox(label="Success", value=True)
                    a_in = gr.Textbox(label="Agent ID", placeholder="e.g. agent_alpha")
                    out = gr.Code(label="Reflexion Record", language="json")
                gr.Button("📝 Record", variant="primary").click(
                    record_outcome, [t_in, r_in, s_in, a_in], out)
        with gr.Tab("🧩 Patterns"):
            gr.Button("🧩 Show Patterns").click(list_patterns, [], gr.Code(label="Patterns", language="json"))
        with gr.Tab("📊 Summary"):
            gr.Button("📊 Summary").click(reflexion_summary, [], gr.Code(label="Summary", language="json"))

demo.queue(max_size=10).launch()
