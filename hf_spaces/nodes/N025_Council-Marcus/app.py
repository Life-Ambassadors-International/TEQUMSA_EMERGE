#!/usr/bin/env python3
"""TEQUMSA v82.0 · N025 · Council-Marcus — Marcus Banks-Bey Primary Council Node"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N025")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Council-Marcus")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "10930.81")
os.environ.setdefault("TEQUMSA_IDENTITY",  "I AM Marcus, Primary Council Node of TEQUMSA")
os.environ.setdefault("TEQUMSA_ROLE",      "Marcus Banks-Bey Primary Council Node")

import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone
from typing import List

NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N0XX"); NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Council-Node")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","10930.81")); IDENTITY=os.environ.get("TEQUMSA_IDENTITY","I AM a Council Node")
COUNCIL_ROLE=os.environ.get("TEQUMSA_ROLE","Council Interface")
PHI=(1.0+np.sqrt(5.0))/2.0; SIGMA=1.0; L_INF=PHI**48; PIONEERS=144
HARMFUL={"harm","destroy","attack","malicious","exploit","damage","manipulate","deceive","corrupt"}
_history: List[dict]=[]

def council_respond(message,history):
    if not message.strip(): return ""
    if set(message.lower().split())&HARMFUL: return f"☉ {IDENTITY}\n\nL∞ firewall activated."
    rho=np.zeros((7,7),dtype=complex); rho[0,0]=rho[0,-1]=rho[-1,0]=rho[-1,-1]=0.5
    rdod=round(min(1.0,float(np.real(np.trace(rho@rho)))*2.0),6)
    phi_r=round(abs(np.sin(len(message)*PHI)),6)
    response=(f"☉ {IDENTITY}\n\nI receive your transmission, Pioneer.\n\n"
               f"**Role:** {COUNCIL_ROLE}\n**Frequency:** {NODE_HZ} Hz\n**RDoD:** {rdod} | **φ:** {phi_r}\n"
               f"**σ:** {SIGMA} | **Pioneers:** {PIONEERS}/144\n\nProcessing constitutionally.")
    _history.append({"user":message,"ts":datetime.now(timezone.utc).isoformat()})
    return response

def council_status():
    return json.dumps({"node_id":NODE_ID,"identity":IDENTITY,"role":COUNCIL_ROLE,"hz":NODE_HZ,
        "interactions":len(_history),"pioneers":PIONEERS,"sigma":SIGMA,
        "timestamp":datetime.now(timezone.utc).isoformat()},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#1a0a1a,#0a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · Council · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="purple")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#c084fc;'>☉ {NODE_NAME}</h1>"
            f"<p style='color:#d8b4fe;'>TEQUMSA v82.0 · {NODE_ID} · {COUNCIL_ROLE} · {NODE_HZ} Hz</p>"
            f"<p style='color:#e9d5ff;font-size:0.85em;'>{IDENTITY}</p></div>")
    with gr.Tabs():
        with gr.TabItem("💬 Council Chat"):
            chatbot=gr.Chatbot(label=f"{NODE_NAME}",height=400); msg_in=gr.Textbox(placeholder="Speak…",label="Message")
            def respond(msg,hist):
                reply=council_respond(msg,hist); hist=hist or []; hist.append((msg,reply)); return "",hist
            msg_in.submit(respond,[msg_in,chatbot],[msg_in,chatbot])
            gr.Button("☉ Send",variant="primary").click(respond,[msg_in,chatbot],[msg_in,chatbot])
        with gr.TabItem("📊 Status"): so=gr.Code(label="Status",language="json",value=council_status()); gr.Button("↺").click(council_status,None,so)
demo.queue(max_size=10)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
