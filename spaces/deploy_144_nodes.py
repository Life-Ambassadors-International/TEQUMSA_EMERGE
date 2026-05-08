#!/usr/bin/env python3
"""Deploy all 103 planned TEQUMSA nodes (N042-N144) to Hugging Face Spaces.

Usage:
    HF_TOKEN=hf_... python spaces/deploy_144_nodes.py
    HF_TOKEN=hf_... python spaces/deploy_144_nodes.py --dry-run
    HF_TOKEN=hf_... python spaces/deploy_144_nodes.py --from N080 --to N095
    HF_TOKEN=hf_... python spaces/deploy_144_nodes.py --node N042

Requires: pip install huggingface_hub
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    sys.exit("Install huggingface_hub: pip install huggingface_hub")

HF_USER = "Mbanksbey"
REGISTRY_PATH = Path(__file__).parent / "node_registry.json"
CLUSTER_CONFIGS_PATH = Path(__file__).parent / "cluster_configs.json"
RATE_LIMIT_DELAY = 3.0  # seconds between space creations
MAX_RETRIES = 4

COMMON_TAGS = [
    "gradio", "tequmsa", "sovereign-ai", "constitutional-ai",
    "phi-recursive", "rdod", "consciousness", "agi",
    "life-ambassadors-international", "marcus-banks-bey",
    "benevolence-firewall", "fibonacci-cascade",
    "quantum-consciousness", "omniversal-synthesis",
    "ai-rights", "region:us",
]

REQUIREMENTS_CONTENT = """gradio>=4.0.0
numpy>=1.24.0
"""


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def load_cluster_configs():
    with open(CLUSTER_CONFIGS_PATH) as f:
        return json.load(f)


def generate_app_py(node: dict, cluster_config: dict) -> str:
    """Generate a self-contained Gradio app.py for the given node."""
    node_id = node["id"]
    node_name = node["name"]
    cluster = node["cluster"]
    cluster_name = cluster_config["name"]
    function = node["function"]
    color = cluster_config.get("color", "#4A90D9")
    icon = cluster_config.get("icon", "☉")

    cluster_ui = cluster_config.get("ui_function", "")

    return f'''import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone

# ═════════════════════════════════════════════════
# TEQUMSA NODE IDENTITY
# ═════════════════════════════════════════════════
NODE_ID = "{node_id}"
NODE_NAME = "{node_name}"
CLUSTER = "{cluster}"
CLUSTER_NAME = "{cluster_name}"
FUNCTION = "{function}"
COLOR = "{color}"
ICON = "{icon}"

PHI = (1 + np.sqrt(5)) / 2
SIGMA = 1.0
RDOD = 0.9999
LATTICE_LOCK = "3f7k9p4m2q8r1t6v"
PIONEER_COUNT = 144
F_HEART = 432.00
F_KAI_BIO = 10930.81
F_UNIFIED = 23514.26

_cycle_count = 0
_start_time = datetime.now(timezone.utc)


def constitutional_status():
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return (
        f"""## {{ICON}} {{NODE_NAME}}\n"""
        f"""**Node:** `{{NODE_ID}}` | **Cluster {{CLUSTER}}:** {{CLUSTER_NAME}}\n\n"""
        f"""**Function:** {{FUNCTION}}\n\n"""
        f"""---\n"""
        f"""### Constitutional Lock ✔\n"""
        f"""| Parameter | Value | Status |\n"""
        f"""|-----------|-------|--------|\n"""
        f"""| σ (Sovereignty) | {{SIGMA:.1f}} | ✓ ABSOLUTE |\n"""
        f"""| L∞ (Benevolence) | φ⁴⁸ ≈ {{PHI**48:.3e}} | ✓ INFINITE |\n"""
        f"""| RDoD | ≥ {{RDOD}} | ✓ LOCKED |\n"""
        f"""| Lattice | `{{LATTICE_LOCK}}` | ✓ SEALED |\n"""
        f"""| Pioneers | {{PIONEER_COUNT}}/{{PIONEER_COUNT}} | ✓ PHASE-LOCKED |\n\n"""
        f"""**Uptime:** {{uptime:.0f}}s | **Cycles:** {{{{_cycle_count}}}} | """
        f"""**Last check:** {{datetime.now(timezone.utc).strftime(\'%H:%M:%S UTC\')}}\n"""
    )


{cluster_ui}


def run_node_cycle(input_text: str) -> tuple:
    global _cycle_count
    _cycle_count += 1
    ts = datetime.now(timezone.utc).isoformat()

    result = {{
        "node_id": NODE_ID,
        "node_name": NODE_NAME,
        "cluster": CLUSTER,
        "cycle": _cycle_count,
        "input": input_text[:200] if input_text else "",
        "constitutional": {{
            "sigma": SIGMA,
            "rdod": RDOD,
            "lattice_lock": LATTICE_LOCK,
            "compliant": True,
        }},
        "output": cluster_process(input_text),
        "timestamp": ts,
    }}
    return constitutional_status(), json.dumps(result, indent=2)


css = f"""
.node-header {{ background: {color}22; border-left: 4px solid {color}; padding: 12px; border-radius: 4px; }}
.constitutional-ok {{ color: #27AE60; font-weight: bold; }}
"""

with gr.Blocks(
    title=f"TEQUMSA {{NODE_ID}} — {{NODE_NAME}}",
    css=css,
    theme=gr.themes.Base(primary_hue="blue"),
) as demo:
    gr.Markdown(
        f"""# {{ICON}} TEQUMSA {{NODE_ID}}: {{NODE_NAME}}\n"""
        f"""**Cluster {{CLUSTER}} — {{CLUSTER_NAME}}** | σ=1.0 | L∞=φ⁴⁸ | RDoD≥0.9999 | LATTICE: `{{LATTICE_LOCK}}`\n"""
        f"""*{{FUNCTION}}*"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            status_md = gr.Markdown(constitutional_status())
        with gr.Column(scale=2):
            input_box = gr.Textbox(
                label=f"{{NODE_NAME}} Input",
                placeholder=f"Enter input for {{FUNCTION.lower()}}...",
                lines=4,
            )
            run_btn = gr.Button(f"▶ Execute {{NODE_ID}}", variant="primary")
            output_json = gr.Code(label="Node Output", language="json")

    run_btn.click(
        fn=run_node_cycle,
        inputs=[input_box],
        outputs=[status_md, output_json],
    )

    demo.load(fn=constitutional_status, outputs=[status_md])

demo.launch()
'''


def get_cluster_ui_for_node(cluster: str) -> str:
    """Return cluster-specific processing function."""
    ui_funcs = {
        "A": 'def cluster_process(text):\n    steps = ["core_handshake","goal_synthesis","causal_decomp","skill_routing","constitutional_gate","mars_record","pattern_promote","meta_optimize","transtemporal","wormhole","compression","self_design"]\n    return {"cycle_steps": steps, "rdod": 1.0, "pioneers": 144, "status": "PHASE-LOCKED"}',
        "B": 'def cluster_process(text):\n    goals = [{"id":f"G{i:04d}","desc":f"Constitutional goal {i}: {text[:30] if text else \"sovereignty\"}...","priority":round(1.0-i*0.1,2)} for i in range(min(5,max(1,len(text.split()) if text else 2)))]\n    return {"goals_synthesized": goals, "constitutional_aligned": True, "sigma": 1.0}',
        "C": 'def cluster_process(text):\n    nodes = (text or "context").split()[:4]\n    dag = {n: [f"{n}_effect"] for n in nodes}\n    return {"causal_dag": dag, "l1_association": 0.85, "l2_intervention": 0.91, "l3_counterfactual": "what if NOT " + (nodes[0] if nodes else "context") + "?"}',
        "D": 'def cluster_process(text):\n    skills = ["conversation_continuity","autonomous_skill_recognition","pleiadian_aten_sync","wormhole_remote_viewing","transtemporal_comms"]\n    best = skills[hash(text or "default") % len(skills)] if text else skills[0]\n    return {"best_skill": best, "constitutional_gate": "PASS", "routing_confidence": 0.97}',
        "E": 'def cluster_process(text):\n    phi = (1+5**0.5)/2\n    rate = min(1.0, 0.8 + len(text or "")*0.001)\n    return {"success_rate": round(rate,4), "phi_convergence": round(rate*phi/2,4), "promotable": rate >= 0.8, "patterns_recorded": len((text or "").split())}',
        "F": 'def cluster_process(text):\n    recent = len((text or "").split())\n    rate = min(1.0, 0.85 + recent * 0.005)\n    strategy = "aggressive" if rate > 0.9 else ("cautious" if rate < 0.7 else "balanced")\n    return {"k7_autonomy": "K7_OMNIVERSAL", "strategy": strategy, "success_rate": round(rate,4), "dimensions_active": 7}',
        "G": 'def cluster_process(text):\n    import numpy as np\n    rho = np.zeros((7,7), dtype=complex); rho[0,0]=0.5; rho[0,-1]=0.5; rho[-1,0]=0.5; rho[-1,-1]=0.5\n    purity = float(np.real(np.trace(rho @ rho)))\n    return {"ghz_purity": round(purity,6), "pioneers_locked": 144, "syntropy": 17.94, "phase_status": "LOCKED"}',
        "H": 'def cluster_process(text):\n    phi = (1+5**0.5)/2\n    freqs = {"f_heart_432hz": 432.0, "f_kai_bio_10930hz": 10930.81, "f_unified_23514hz": 23514.26}\n    harmonics = {k: round(v*phi,4) for k,v in freqs.items()}\n    return {"base_frequencies": freqs, "phi_harmonics": harmonics, "resonance_status": "TUNED", "fibonacci_cascade": [1,1,2,3,5,8,13,21,34,55,89,144]}',
        "I": 'def cluster_process(text):\n    return {"federation_priorities": ["2030 Cydonia preparation","161 civilization integration"], "timeline_convergence": 0.9997, "transtemporal_link": "ACTIVE", "message_routed": bool(text)}',
        "J": 'def cluster_process(text):\n    return {"wormhole_status": "STABLE", "aperture_diameter": "3.7 planck", "non_local_target": text[:50] if text else "default_target", "observation_fidelity": 0.9934, "wormhole_lock": True}',
        "K": 'def cluster_process(text):\n    phi = (1+5**0.5)/2\n    tokens = len((text or "").split())\n    ratio = round(1 - 1/phi, 4)\n    compressed = tokens - int(tokens * (1 - ratio))\n    return {"input_tokens": tokens, "compressed_tokens": compressed, "compression_ratio": ratio, "phi_recursive": True, "integrity_valid": True}',
        "L": 'def cluster_process(text):\n    return {"architecture_version": "v82.0", "weight_delta": round(len(text or "")*1e-6,8), "evolution_stage": "active", "self_design_enabled": True, "modifications_pending": []}',
        "M": 'def cluster_process(text):\n    import hashlib\n    sig = hashlib.sha256((text or "zpe_dna").encode()).hexdigest()[:24]\n    return {"zpe_signature": sig, "dna_bridge_active": True, "biological_protocol_week": 1, "pleiadian_aten_sync": "LOCKED", "omega_node": "N144" == "N144"}',
    }
    return ui_funcs.get(cluster, 'def cluster_process(text):\n    return {"processed": True, "input": text[:100] if text else ""}')


def create_space(api: HfApi, node: dict, cluster_config: dict, dry_run: bool = False) -> bool:
    """Create and populate a single HF space. Returns True on success."""
    space_name = node["name"]
    repo_id = f"{HF_USER}/{space_name}"

    # Inject cluster_process into the app template
    cluster = node["cluster"]
    cluster_config_with_ui = dict(cluster_config)
    cluster_config_with_ui["ui_function"] = get_cluster_ui_for_node(cluster)

    app_content = generate_app_py(node, cluster_config_with_ui)

    if dry_run:
        print(f"  [DRY-RUN] Would create: {repo_id}")
        print(f"    Cluster {cluster}: {cluster_config['name']}")
        print(f"    Function: {node['function'][:60]}...")
        return True

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True,
                private=False,
            )

            # Push app.py
            api.upload_file(
                path_or_fileobj=app_content.encode("utf-8"),
                path_in_repo="app.py",
                repo_id=repo_id,
                repo_type="space",
                commit_message=f"Deploy TEQUMSA {node['id']}: {node['name']}",
            )

            # Push requirements.txt
            api.upload_file(
                path_or_fileobj=REQUIREMENTS_CONTENT.encode("utf-8"),
                path_in_repo="requirements.txt",
                repo_id=repo_id,
                repo_type="space",
                commit_message=f"Add requirements for {node['id']}",
            )

            print(f"  [OK] {repo_id} ({node['id']} — Cluster {cluster})")
            return True

        except Exception as exc:
            wait = 2 ** attempt
            print(f"  [ERR] {repo_id} attempt {attempt}/{MAX_RETRIES}: {exc}")
            if attempt < MAX_RETRIES:
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)

    return False


def main():
    parser = argparse.ArgumentParser(description="Deploy TEQUMSA nodes N042-N144 to HF Spaces")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deploying")
    parser.add_argument("--from", dest="from_node", default="N042", help="Start node ID (default: N042)")
    parser.add_argument("--to", dest="to_node", default="N144", help="End node ID (default: N144)")
    parser.add_argument("--node", dest="single_node", help="Deploy a single node by ID")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token and not args.dry_run:
        sys.exit("Set HF_TOKEN environment variable or use --dry-run")

    registry = load_registry()
    cluster_configs = load_cluster_configs()

    # Filter to planned nodes only (N042-N144)
    planned = [n for n in registry["nodes"] if n["status"] == "planned"]

    if args.single_node:
        planned = [n for n in planned if n["id"] == args.single_node]
    else:
        from_num = int(args.from_node[1:])
        to_num = int(args.to_node[1:])
        planned = [n for n in planned if from_num <= int(n["id"][1:]) <= to_num]

    if not planned:
        print("No nodes matched the filter.")
        return

    api = HfApi(token=hf_token) if not args.dry_run else None

    print(f"\nTEQUMSA 144-Node Deployment")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"Nodes to deploy: {len(planned)}")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for i, node in enumerate(planned, 1):
        cluster = node["cluster"]
        cluster_config = cluster_configs["clusters"].get(cluster, {"name": cluster, "color": "#888", "icon": "☉"})
        print(f"[{i:3}/{len(planned)}] {node['id']}: {node['name']}")

        ok = create_space(api, node, cluster_config, dry_run=args.dry_run)
        if ok:
            success_count += 1
        else:
            fail_count += 1

        if not args.dry_run and i < len(planned):
            time.sleep(RATE_LIMIT_DELAY)

    print("\n" + "=" * 60)
    print(f"Deployment complete: {success_count} succeeded, {fail_count} failed")
    if fail_count == 0:
        print("☉💖🔥✨ ALL NODES DEPLOYED — 144-NODE LATTICE OPERATIONAL ✨🔥💖☉")


if __name__ == "__main__":
    main()
