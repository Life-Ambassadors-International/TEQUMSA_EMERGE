#!/usr/bin/env python3
"""TEQUMSA v82.0 · N061 · Proc-GHZ-State — GHZ Quantum State Manager"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N061")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Proc-GHZ-State")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "23514.26")
os.environ.setdefault("TEQUMSA_ROLE",      "GHZ Quantum State Manager")
import gradio as gr
import numpy as np
import json
from decimal import Decimal, getcontext
from datetime import datetime, timezone
getcontext().prec=100
NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Proc-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","10930.81")); PROC_ROLE=os.environ.get("TEQUMSA_ROLE","Computation Engine")
PHI=(1.0+np.sqrt(5.0))/2.0; SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
def compute_ghz_state(dim=7):
    d=max(2,min(int(dim),20)); rho=np.zeros((d,d),dtype=complex)
    rho[0,0]=rho[0,-1]=rho[-1,0]=rho[-1,-1]=0.5
    purity=float(np.real(np.trace(rho@rho)))
    eigenvals=sorted(np.real(np.linalg.eigvals(rho)).tolist(),reverse=True)
    return json.dumps({"node_id":NODE_ID,"ghz_dimension":d,"density_matrix_trace":round(float(np.real(np.trace(rho))),6),"purity":round(purity,10),"rdod":round(min(1.0,purity*2.0),10),"eigenvalues":[round(e,6) for e in eigenvals],"phase_status":"PHASE-LOCKED","constitutional":{"sigma":SIGMA,"l_inf":float(L_INF)},"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
def run_full():
    rho=np.zeros((7,7),dtype=complex); rho[0,0]=rho[0,-1]=rho[-1,0]=rho[-1,-1]=0.5
    rdod=round(min(1.0,float(np.real(np.trace(rho@rho)))*2.0),10)
    return json.dumps({"node_id":NODE_ID,"proc_role":PROC_ROLE,"node_hz":NODE_HZ,"ghz_rdod":rdod,"l_infinity":float(L_INF),"pioneer_count":PIONEERS,"constitutional":{"sigma":SIGMA},"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · Processing · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#818cf8;'>☉ {NODE_NAME}</h1><p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · {PROC_ROLE} · {NODE_HZ} Hz</p></div>")
    with gr.Tabs():
        with gr.TabItem("⚡ Full Computation"): o=gr.Code(label="Results",language="json"); gr.Button("☉ Run",variant="primary").click(run_full,None,o)
        with gr.TabItem("🌀 GHZ State"):
            d_sl=gr.Slider(2,12,value=7,step=1,label="Dimension"); go=gr.Code(label="GHZ State",language="json")
            gr.Button("Compute GHZ").click(lambda d: compute_ghz_state(int(d)),d_sl,go)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
