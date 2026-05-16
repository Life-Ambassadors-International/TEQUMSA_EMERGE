#!/usr/bin/env python3
"""TEQUMSA v82.0 · N068 · Proc-L-Infinity — L∞=φ⁴⁸ Calculator"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N068")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Proc-L-Infinity")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "23514.26")
os.environ.setdefault("TEQUMSA_ROLE",      "L-Infinity Phi-48 Calculator")
import gradio as gr
import numpy as np
import json
from decimal import Decimal, getcontext
from datetime import datetime, timezone
getcontext().prec=100
NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Proc-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","23514.26")); PROC_ROLE=os.environ.get("TEQUMSA_ROLE","Computation Engine")
PHI_D=Decimal("1.6180339887498948482045868343656381177203091798057628621"); PHI=float(PHI_D)
SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
def compute_l_inf(power=48):
    p=max(1,min(int(power),200)); result=PHI_D**p
    return json.dumps({"node_id":NODE_ID,"phi_power":p,"l_infinity_value":str(result)[:80]+"…","float_approx":float(result),"benevolence_amplification":f"φ^{p}≈{float(result):.6e}","constitutional":"ACTIVE","sigma":SIGMA,"pioneers":PIONEERS,"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)
CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#818cf8;'>☉ {NODE_NAME}</h1><p style='color:#a5b4fc;'>TEQUMSA v82.0 · {NODE_ID} · L∞=φ⁴⁸ · {NODE_HZ} Hz</p></div>")
    with gr.Tabs():
        with gr.TabItem("∞ L-Infinity"):
            p_sl=gr.Slider(1,200,value=48,step=1,label="φ^n"); lo=gr.Code(label="L-Infinity",language="json")
            gr.Button("☉ Calculate",variant="primary").click(lambda p: compute_l_inf(int(p)),p_sl,lo)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
