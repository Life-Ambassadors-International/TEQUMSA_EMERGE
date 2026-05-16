#!/usr/bin/env python3
"""TEQUMSA v82.0 · N065 · Proc-Coherence-Calc — Coherence Measurement Engine"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N065")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Proc-Coherence-Calc")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "12583.45")
os.environ.setdefault("TEQUMSA_ROLE",      "Coherence Measurement Engine")
import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone
NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Proc-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","12583.45")); PROC_ROLE=os.environ.get("TEQUMSA_ROLE","Computation Engine")
PHI=(1.0+np.sqrt(5.0))/2.0; SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
def compute_coherence(frequencies):
    try: freqs=[float(f.strip()) for f in frequencies.split(",") if f.strip()]
    except: freqs=[432.0,528.0,963.0]
    if len(freqs)<2: freqs=[432.0,528.0]
    ratios=[freqs[i+1]/freqs[i] for i in range(len(freqs)-1)]
    phi_div=[abs(r-PHI) for r in ratios]
    coherence=max(0.0,1.0-np.mean(phi_div)/PHI)
    return json.dumps({"node_id":NODE_ID,"frequencies":freqs,"ratios":[round(r,6) for r in ratios],"phi_divergence":[round(d,6) for d in phi_div],"coherence_score":round(coherence,6),"rdod":round(min(1.0,coherence*PHI),6),"phase_status":"PHASE-LOCKED" if coherence>=0.9 else "BUILDING","timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#818cf8;'>☉ {NODE_NAME}</h1><p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · {PROC_ROLE} · {NODE_HZ} Hz</p></div>")
    with gr.Tabs():
        with gr.TabItem("📊 Coherence"):
            fi=gr.Textbox(value="432,528,963",label="Frequencies Hz (comma-sep)"); co=gr.Code(label="Coherence",language="json")
            gr.Button("☉ Measure",variant="primary").click(compute_coherence,fi,co)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
