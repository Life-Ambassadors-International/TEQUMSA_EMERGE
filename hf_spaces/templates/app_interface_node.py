#!/usr/bin/env python3
# TEQUMSA v82.0 · INTERFACE NODE TEMPLATE
# Used by: N074-N075 (G_INTERFACES voice/visual)
import gradio as gr, numpy as np, json, hashlib, os
from datetime import datetime, timezone
from typing import List, Tuple

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Interface-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "432.0"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Human-AI Interface")
ITYPE     = os.environ.get("TEQUMSA_INTERFACE_TYPE", "general")

PHI = (1+np.sqrt(5))/2; SIGMA = 1.0; L_INF = PHI**48; PIONEER = 144
HARMFUL = {"harm","destroy","attack","malicious","exploit","damage","manipulate","deceive"}
rho = np.zeros((7,7),dtype=complex); rho[0,0]=rho[0,-1]=rho[-1,0]=rho[-1,-1]=0.5
RDOD = min(1.0, float(np.real(np.trace(rho@rho)))*2)

def process_input(text):
    if not str(text).strip(): return json.dumps({"error":"Input required"},indent=2)
    if set(str(text).lower().split()) & HARMFUL:
        return json.dumps({"filtered":True,"message":"L∞ firewall: benevolence active"},indent=2)
    sig = hashlib.sha256(f"{text}{PHI}".encode()).hexdigest()[:16]
    fr  = NODE_HZ*(1+(hash(str(text))%100)/10000)
    return json.dumps({"node":NODE_ID,"interface":ITYPE,"hash":sig,
        "freq_response":round(fr,4),"phi_ratio":round(fr/432,6),"rdod":RDOD,
        "message":f"☉ {NODE_NAME} active at {NODE_HZ} Hz",
        "sigma":SIGMA,"l_inf":float(L_INF),"pioneer":f"{PIONEER}/144",
        "ts":datetime.now(timezone.utc).isoformat()},indent=2)

def generate_tone(freq):
    sr=8000; t=np.linspace(0,0.1,800,endpoint=False)
    wave=(np.sin(2*np.pi*min(freq,4000)*t)+0.3*np.sin(2*np.pi*min(freq*PHI,4000)*t)).astype(np.float32)
    wave/=np.max(np.abs(wave)+1e-9)
    return sr, wave

def node_status():
    return json.dumps({"node_id":NODE_ID,"name":NODE_NAME,"version":"v82.0",
        "hz":NODE_HZ,"itype":ITYPE,"role":NODE_ROLE,"rdod":RDOD,
        "sigma":SIGMA,"l_inf":float(L_INF),"pioneer":f"{PIONEER}/144",
        "ts":datetime.now(timezone.utc).isoformat()},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME}·Interface·v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="pink")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#f9a8d4;'>☉ {NODE_NAME}</h1>"
            f"<p style='color:#fbcfe8;'>v82.0·{NODE_ID}·{NODE_HZ}Hz·{NODE_ROLE}</p></div>")
    with gr.Tabs():
        with gr.TabItem("\U0001f517 Interface"):
            inp=gr.Textbox(placeholder=f"Interface with {NODE_NAME}...",label="Input",lines=3)
            out=gr.Code(label="Response",language="json")
            gr.Button("☉ Process",variant="primary").click(process_input,inp,out)
        with gr.TabItem("\U0001f3b5 Tone Generator"):
            fs=gr.Slider(1,4000,value=min(NODE_HZ,4000),step=0.01,label="Frequency (Hz)")
            ao=gr.Audio(label="Phi-harmonic Tone",type="numpy")
            gr.Button(f"☉ Generate {NODE_HZ} Hz Tone").click(generate_tone,fs,ao)
        with gr.TabItem("\U0001f4ca Status"):
            s=gr.Code(label="Interface Status",language="json",value=node_status())
            gr.Button("↺ Refresh").click(node_status,None,s)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
