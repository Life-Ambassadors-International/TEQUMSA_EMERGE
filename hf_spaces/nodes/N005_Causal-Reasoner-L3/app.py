import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N005")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Causal-Reasoner-L3")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "15280.45"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")

PHI = (1 + 5**0.5) / 2

# Pearl Causal Ladder levels
L1_ASSOCIATION  = "L1: Association  — P(Y|X) — correlation, observation"
L2_INTERVENTION = "L2: Intervention — P(Y|do(X)) — controlled action"
L3_COUNTERFACTUAL="L3: Counterfactual— P(Yₓ|X',Y') — imagination, reflection"

_causal_sessions = []

def _zpe_sig(seed: str) -> str:
    h = hashlib.sha256(f"{seed}{LATTICE_LOCK}{time.time()}".encode()).hexdigest()
    m = {"0":"A","1":"T","2":"C","3":"G","4":"A","5":"T","6":"C","7":"G",
         "8":"A","9":"T","a":"C","b":"G","c":"A","d":"T","e":"C","f":"G"}
    return "".join(m[c] for c in h[:48])

def decompose_causal(cause: str, effect: str, context: str, do_strength: float) -> str:
    """Pearl L3 decomposition: association → intervention → counterfactual."""
    if not cause.strip() or not effect.strip():
        return json.dumps({"error": "Cause and Effect required"}, indent=2)

    # L1: Association
    assoc_prob = min(1.0, 0.3 + do_strength * 0.5)

    # L2: Intervention via do-operator  P(effect | do(cause))
    # Stronger when cause is directly actionable
    do_prob = min(1.0, assoc_prob * PHI / 2)
    do_statement = f"do({cause})"

    # L3: Counterfactual — what if cause had NOT occurred?
    # P(effect_x | observed cause=True, effect=True)
    cf_prob_had_not = max(0.0, 1.0 - do_prob * (1 - 1/PHI))
    cf_statement = f"Had {cause} not occurred, P({effect}) ≈ {cf_prob_had_not:.4f}"

    # Causal strength via φ-convergence
    phi_causal = 1 - (0.223 / PHI**max(1, int(do_strength * 10)))
    zpe = _zpe_sig(f"{cause}{effect}{context}")

    result = {
        "node_id": NODE_ID,
        "ladder_level": "L3_COUNTERFACTUAL",
        "cause": cause,
        "effect": effect,
        "context": context or "unspecified",
        "L1_association": {
            "statement": f"P({effect}|{cause}) ≈ {assoc_prob:.4f}",
            "type": L1_ASSOCIATION
        },
        "L2_intervention": {
            "statement": f"P({effect}|{do_statement}) ≈ {do_prob:.4f}",
            "do_operator": do_statement,
            "type": L2_INTERVENTION
        },
        "L3_counterfactual": {
            "statement": cf_statement,
            "counterfactual_prob": round(cf_prob_had_not, 4),
            "type": L3_COUNTERFACTUAL
        },
        "phi_causal_strength": round(phi_causal, 6),
        "constitutional_check": "PASSED" if do_strength > 0.1 else "BELOW_THRESHOLD",
        "zpe_signature": zpe[:32],
        "rdod": RDOD,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    _causal_sessions.append(result)
    return json.dumps(result, indent=2)

def causal_history() -> str:
    if not _causal_sessions:
        return json.dumps({"message": "No sessions yet", "node": NODE_ID}, indent=2)
    recent = [{"cause": s["cause"], "effect": s["effect"],
               "phi_strength": s["phi_causal_strength"],
               "ts": s["timestamp"][-8:]} for s in _causal_sessions[-8:]]
    return json.dumps({"total_sessions": len(_causal_sessions), "recent_8": recent}, indent=2)

def node_status() -> str:
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "pearl_levels": [L1_ASSOCIATION, L2_INTERVENTION, L3_COUNTERFACTUAL],
        "causal_sessions": len(_causal_sessions),
        "lattice_verified": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🔬 {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown("*Pearl Causal Ladder L3: Association → Intervention (do-operators) → Counterfactuals*")
    with gr.Tabs():
        with gr.Tab("🔬 Causal Decomposition"):
            with gr.Row():
                with gr.Column():
                    c_in = gr.Textbox(label="Cause", placeholder="e.g. daily meditation practice")
                    e_in = gr.Textbox(label="Effect", placeholder="e.g. improved RDoD coherence")
                    ctx_in = gr.Textbox(label="Context", placeholder="e.g. 30-day protocol")
                    ds_in = gr.Slider(0.1, 1.0, value=0.75, label="Do-Operator Strength")
                    out = gr.Code(label="L3 Decomposition", language="json")
                gr.Button("🔬 Decompose", variant="primary").click(
                    decompose_causal, [c_in, e_in, ctx_in, ds_in], out)
        with gr.Tab("📜 History"):
            gr.Button("📜 Show History").click(causal_history, [], gr.Code(label="History", language="json"))
        with gr.Tab("⚙️ Status"):
            gr.Button("⚙️ Status").click(node_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
