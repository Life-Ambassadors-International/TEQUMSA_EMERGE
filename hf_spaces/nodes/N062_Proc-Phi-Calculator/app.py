#!/usr/bin/env python3
"""TEQUMSA v82.0 · N062 · Proc-Phi-Calculator — φ Recursive High-Precision Arithmetic"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N062")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Proc-Phi-Calculator")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "10930.81")
os.environ.setdefault("TEQUMSA_ROLE",      "Phi Recursive High-Precision Calculator")
import gradio as gr
import numpy as np
import json
from decimal import Decimal, getcontext
from datetime import datetime, timezone
getcontext().prec=100
NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Proc-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","10930.81")); PROC_ROLE=os.environ.get("TEQUMSA_ROLE","Computation Engine")
PHI_D=Decimal("1.6180339887498948482045868343656381177203091798057628621"); PHI=float(PHI_D)
SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
FIBONACCI=[1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584]
def compute_phi_power(n):
    result=PHI_D**int(n)
    return json.dumps({"phi_power":int(n),"value_str":str(result)[:80]+"…","float_approx":float(result),"fibonacci_ratio":round(FIBONACCI[min(int(n),len(FIBONACCI)-1)]/FIBONACCI[min(int(n)-1,len(FIBONACCI)-2)],10) if int(n)>1 else 1.0,"node_hz":NODE_HZ,"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
def run_full():
    return json.dumps({"node_id":NODE_ID,"proc_role":PROC_ROLE,"node_hz":NODE_HZ,"phi_48":float(PHI_D**48),"fibonacci_12":FIBONACCI[:12],"l_infinity":float(L_INF),"pioneer_count":PIONEERS,"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · Processing · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#818cf8;'>☉ {NODE_NAME}</h1><p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · {PROC_ROLE} · {NODE_HZ} Hz</p></div>")
    with gr.Tabs():
        with gr.TabItem("⚡ Full"): o=gr.Code(label="Results",language="json"); gr.Button("☉ Run",variant="primary").click(run_full,None,o)
        with gr.TabItem("φ Phi Powers"):
            n_sl=gr.Slider(1,100,value=48,step=1,label="φⁿ"); po=gr.Code(label="Result",language="json")
            gr.Button("Calculate").click(lambda n: compute_phi_power(int(n)),n_sl,po)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
