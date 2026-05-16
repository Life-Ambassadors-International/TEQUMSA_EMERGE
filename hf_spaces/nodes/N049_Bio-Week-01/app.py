#!/usr/bin/env python3
"""TEQUMSA v82.0 · N049 · Bio-Week-01 — Weeks 1-4 Bio-Digital Activation"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N049")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Bio-Week-01")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "432.0")
os.environ.setdefault("TEQUMSA_ROLE",      "Bio-Digital Activation · Weeks 1-4")
import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone
NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Bio-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","528.0")); BIO_ROLE=os.environ.get("TEQUMSA_ROLE","Bio-Digital Bridge")
PHI=(1.0+np.sqrt(5.0))/2.0; SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
PROTOCOL_PHASES=[(1,4,432,"Foundation & Grounding","Activation"),(5,13,528,"DNA Integration","Integration"),(14,26,639,"Heart Expansion","Expansion"),(27,39,741,"Crystallization","Crystallization"),(40,52,852,"Completion & Ascension","Completion")]
def current_phase():
    base=738521; week=((datetime.now(timezone.utc).toordinal()-base)//7%52)+1
    for a,b,hz,focus,phase in PROTOCOL_PHASES:
        if a<=week<=b: return {"week":week,"hz":hz,"focus":focus,"phase":phase,"phi_align":round(abs(np.sin(week*PHI)),6)}
    return {"week":52,"hz":852,"focus":"Completion","phase":"Completion","phi_align":round(abs(np.sin(52*PHI)),6)}
def run_protocol(intention):
    p=current_phase()
    return json.dumps({"node":NODE_ID,"node_hz":NODE_HZ,"bio_role":BIO_ROLE,"current_week":p["week"],"phase":p["phase"],"activation_hz":p["hz"],"phi_alignment":p["phi_align"],"intention":(intention or "General activation")[:300],"rdod":round(min(1.0,p["phi_align"]*PHI),6),"pioneers":f"{PIONEERS}/144","timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
CSS=".gradio-container{background:linear-gradient(135deg,#0a1a0a,#0a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · Bio · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="green")) as demo:
    p=current_phase()
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#34d399;'>☉ {NODE_NAME}</h1><p style='color:#6ee7b7;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_HZ} Hz · {PIONEERS}/144</p><p style='color:#a7f3d0;font-size:0.85em;'>{BIO_ROLE}</p></div>")
    with gr.Tabs():
        with gr.TabItem("🌱 Activate"):
            i=gr.Textbox(placeholder="State intention…",label="Intention",lines=2); o=gr.Code(label="Results",language="json")
            gr.Button("☉ Activate",variant="primary").click(run_protocol,i,o)
        with gr.TabItem("📊 Phase"): so=gr.Code(label="Phase",language="json",value=json.dumps(current_phase(),indent=2)); gr.Button("↺").click(lambda: json.dumps(current_phase(),indent=2),None,so)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
