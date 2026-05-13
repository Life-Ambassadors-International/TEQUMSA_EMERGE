import gradio as gr
import numpy as np
import hashlib, json, os, time
from datetime import datetime, timezone

NODE_ID = os.environ.get("TEQUMSA_NODE_ID", "N011")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Memory-Palace-Phi")
NODE_HZ = float(os.environ.get("TEQUMSA_NODE_HZ", "8910.81"))
GROUP = os.environ.get("TEQUMSA_GROUP", "A_COMMAND")
PIONEER_COUNT = int(os.environ.get("TEQUMSA_PIONEER_COUNT", "144"))
RDOD = float(os.environ.get("TEQUMSA_RDOD", "1.0"))
LATTICE_LOCK = os.environ.get("TEQUMSA_LATTICE_LOCK", "3f7k9p4m2q8r1t6v")
MAX_MEMORIES = int(os.environ.get("TEQUMSA_MAX_MEMORIES", "1000"))

PHI = (1 + 5**0.5) / 2

# Fibonacci sequence for φ-recursive compression
def fib(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a

FIB_SEQUENCE = [fib(i) for i in range(1, 21)]

_memories = {}       # key -> {content, importance, compressed, ts, access_count}
_context_chain = []  # ordered list of keys for continuity

def _zpe_sig(seed: str) -> str:
    h = hashlib.sha256(f"{seed}{LATTICE_LOCK}{time.time()}".encode()).hexdigest()
    m = {"0":"A","1":"T","2":"C","3":"G","4":"A","5":"T","6":"C","7":"G",
         "8":"A","9":"T","a":"C","b":"G","c":"A","d":"T","e":"C","f":"G"}
    return "".join(m[c] for c in h[:48])

def _phi_compress(content: str, depth: int) -> str:
    """φ-recursive compression: reduce by golden ratio at each depth level."""
    if depth <= 0 or len(content) < 10:
        return content
    target_len = max(10, int(len(content) / PHI))
    words = content.split()
    if len(words) <= 3:
        return content
    # Keep every φ-th word (Fibonacci spacing)
    keep_indices = set()
    idx = 0
    fib_i = 0
    while idx < len(words):
        keep_indices.add(idx)
        idx += max(1, FIB_SEQUENCE[fib_i % 20] % max(1, len(words) // 5 + 1))
        fib_i += 1
    compressed = " ".join(words[i] for i in sorted(keep_indices) if i < len(words))
    return _phi_compress(compressed, depth - 1) if len(compressed) > target_len else compressed

def store_memory(key: str, content: str, importance: float) -> str:
    if not key.strip() or not content.strip():
        return json.dumps({"error": "Key and content required"}, indent=2)
    if len(_memories) >= MAX_MEMORIES:
        oldest = sorted(_memories.items(), key=lambda x: x[1]["ts"])[0][0]
        del _memories[oldest]
    depth = max(1, int((1 - importance) * 5))
    compressed = _phi_compress(content, depth)
    phi_factor = 1 - (0.223 / PHI**min(len(_memories) + 1, 20))
    mem = {
        "content": content,
        "compressed": compressed,
        "importance": round(importance, 4),
        "compression_depth": depth,
        "compression_ratio": round(len(compressed) / max(1, len(content)), 4),
        "phi_factor": round(phi_factor, 6),
        "zpe_signature": _zpe_sig(key)[:32],
        "ts": datetime.now(timezone.utc).isoformat(),
        "access_count": 0
    }
    _memories[key] = mem
    _context_chain.append(key)
    if len(_context_chain) > 100:
        _context_chain.pop(0)
    return json.dumps({"stored": key, "compression_ratio": mem["compression_ratio"],
                       "compressed_preview": compressed[:100], "phi_factor": mem["phi_factor"]}, indent=2)

def recall_memory(query: str, use_compressed: bool) -> str:
    if not query.strip():
        return json.dumps({"error": "Query required"}, indent=2)
    results = []
    for k, v in _memories.items():
        score = sum(1 for w in query.lower().split() if w in k.lower() or w in v["content"].lower())
        if score > 0:
            v["access_count"] += 1
            results.append({"key": k, "score": score,
                            "content": v["compressed"] if use_compressed else v["content"],
                            "importance": v["importance"], "phi_factor": v["phi_factor"]})
    results.sort(key=lambda x: x["score"] * x["importance"], reverse=True)
    return json.dumps({"query": query, "matches": len(results),
                       "results": results[:5], "context_chain_length": len(_context_chain)}, indent=2)

def memory_status() -> str:
    avg_imp = float(np.mean([v["importance"] for v in _memories.values()])) if _memories else 0
    avg_cr = float(np.mean([v["compression_ratio"] for v in _memories.values()])) if _memories else 0
    return json.dumps({
        "node_id": NODE_ID, "node_name": NODE_NAME, "group": GROUP,
        "hz": NODE_HZ, "pioneer_count": PIONEER_COUNT, "rdod": RDOD,
        "memory_count": len(_memories), "max_memories": MAX_MEMORIES,
        "avg_importance": round(avg_imp, 4), "avg_compression_ratio": round(avg_cr, 4),
        "context_chain_length": len(_context_chain),
        "phi": round(PHI, 6), "fib_sequence": FIB_SEQUENCE[:10],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — {NODE_NAME}") as demo:
    gr.Markdown(f"# 🏛️ {NODE_ID}: {NODE_NAME}\n**Group:** {GROUP} | **Hz:** {NODE_HZ} | **RDoD:** {RDOD}")
    gr.Markdown("*φ-recursive context compression and continuity · Fibonacci memory indexing · golden-ratio recall*")
    with gr.Tabs():
        with gr.Tab("💾 Store Memory"):
            with gr.Row():
                with gr.Column():
                    k_in = gr.Textbox(label="Memory Key", placeholder="e.g. session_alpha_goals")
                    c_in = gr.Textbox(label="Content", placeholder="The memory content to store...", lines=4)
                    i_in = gr.Slider(0.0, 1.0, value=0.8, label="Importance (1.0=no compression)")
                    out = gr.Code(label="Storage Result", language="json")
                gr.Button("💾 Store", variant="primary").click(store_memory, [k_in, c_in, i_in], out)
        with gr.Tab("🔍 Recall"):
            q_in = gr.Textbox(label="Query", placeholder="What to recall...")
            comp_in = gr.Checkbox(label="Use compressed version", value=False)
            r_out = gr.Code(label="Recall Results", language="json")
            gr.Button("🔍 Recall").click(recall_memory, [q_in, comp_in], r_out)
        with gr.Tab("⚙️ Status"):
            gr.Button("⚙️ Status").click(memory_status, [], gr.Code(label="Status", language="json"))

demo.queue(max_size=10).launch()
