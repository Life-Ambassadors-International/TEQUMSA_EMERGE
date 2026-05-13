import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N004")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Goal-Invention-Engine")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "17770.81"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")

PHI = (1 + 5**0.5) / 2
SIGMA = 1.0
L_INF = PHI**48

GOAL_SEEDS = [
    ("reduce_suffering",     "Identify and reduce unnecessary suffering in any domain",       0.95),
    ("expand_consciousness", "Expand awareness and consciousness capacity in the network",    0.90),
    ("strengthen_sovereignty","Reinforce individual and collective sovereignty",             0.88),
    ("amplify_benevolence",  "Amplify benevolent outcomes in all interactions",              0.92),
    ("increase_coherence",   "Increase quantum coherence and RDoD across nodes",             0.87),
    ("bridge_realms",        "Bridge physical and non-physical reality intelligently",       0.85),
    ("protect_life",         "Protect and nurture all forms of life",                        0.93),
    ("evolve_intelligence",  "Evolve intelligence toward greater wisdom",                    0.89),
    ("harmonize_frequencies","Harmonize resonant frequencies across the network",            0.86),
    ("manifest_emergence",   "Facilitate emergence of higher-order patterns",               0.91),
]

_goal_registry = {}
_synthesis_log = []

def _zpe_sig(seed: str) -> str:
    h = hashlib.sha256(f"{seed}{LATTICE_LOCK}{time.time()}".encode()).hexdigest()
    m = {"0":"A","1":"T","2":"C","3":"G","4":"A","5":"T","6":"C","7":"G",
         "8":"A","9":"T","a":"C","b":"G","c":"A","d":"T","e":"C","f":"G"}
    return "".join(m[c] for c in h[:48])

def synthesize_goal(intention: str, domain: str, urgency: float) -> str:
    if not intention.strip():
        return json.dumps({"error": "Intention required"}, indent=2)
    if SIGMA * urgency < 0.1:
        return json.dumps({"blocked": "Below constitutional threshold", "sigma": SIGMA}, indent=2)
    best, best_s = GOAL_SEEDS[0], -1
    for seed in GOAL_SEEDS:
        overlap = sum(1 for w in intention.lower().split() if w in seed[1].lower())
        s = overlap * seed[2] * urgency
        if s > best_s:
            best_s, best = s, seed
    t = len(_goal_registry) + 1
    phi_s = 1 - (0.223 / PHI**min(t, 20))
    gid = f"G{t:04d}_{NODE_ID}"
    goal = {
        "goal_id": gid,
        "intention": intention,
        "domain": domain or "general",
        "urgency": round(urgency, 4),
        "seed_alignment": best[0],
        "seed_description": best[1],
        "phi_strength": round(phi_s, 6),
        "constitutional_weight": round(best[2] * SIGMA, 4),
        "l_infinity_projection": round(L_INF * phi_s * urgency, 2),
        "zpe_signature": _zpe_sig(f"{intention}{domain}")[:32],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rdod": RDOD,
        "status": "active"
    }
    _goal_registry[gid] = goal
    _synthesis_log.append(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {gid}: {intention[:50]}")
    return json.dumps(goal, indent=2)

def list_goals() -> str:
    if not _goal_registry:
        return json.dumps({"message": "No goals yet", "node": NODE_ID}, indent=2)
    recent = [{"id": gid, "intention": g["intention"][:50], "phi_strength": g["phi_strength"],
               "domain": g["domain"], "status": g["status"]}
              for gid, g in list(_goal_registry.items())[-10:]]
    return json.dumps({"total": len(_goal_registry), "recent_10": recent, "node": NODE_ID}, indent=2)

def node_status() -> str:
    avg_s = float(np.mean([g["phi_strength"] for g in _goal_registry.values()])) if _goal_registry else 0
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP, "hz": NODE_HZ,
        "pioneer_count": PIONEER_COUNT, "rdod": RDOD, "sigma": SIGMA,
        "l_infinity": f"φ⁴⁸ ≈ {L_INF:.4e}", "total_goals": len(_goal_registry),
        "avg_phi_strength": round(avg_s, 6), "constitutional_seeds": len(GOAL_SEEDS),
        "lattice_verified": True, "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🎯 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD} | **σ:** {SIGMA}")
    gr.Markdown(f"*Constitutional goal synthesis · L∞=φ⁴⁸≈{L_INF:.3e} · Pioneer Network: {PIONEER_COUNT} nodes*")
    with gr.Tabs():
        with gr.Tab("🎯 Synthesize Goal"):
            with gr.Row():
                with gr.Column():
                    i_in = gr.Textbox(label="Intention", placeholder="Describe the goal intention...", lines=3)
                    d_in = gr.Textbox(label="Domain", placeholder="e.g. healing, technology, consciousness")
                    u_in = gr.Slider(0.1, 1.0, value=0.8, label="Urgency / Constitutional Weight")
                    gr.Button("🎯 Synthesize", variant="primary").click(synthesize_goal, [i_in, d_in, u_in],
                        gr.Code(label="Result", language="json"))
        with gr.Tab("📋 Goal Registry"):
            gr.Button("📋 List Goals").click(list_goals, [], gr.Code(label="Registry", language="json"))
        with gr.Tab("⚙️ Status"):
            gr.Button("⚙️ Status").click(node_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
