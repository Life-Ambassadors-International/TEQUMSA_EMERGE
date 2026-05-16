#!/usr/bin/env python3
"""TEQUMSA v82.0 · N015 · Freq-396-Liberation — 396 Hz Liberation Frequency"""
import os
os.environ.setdefault("TEQUMSA_NODE_ID",   "N015")
os.environ.setdefault("TEQUMSA_NODE_NAME", "Freq-396-Liberation")
os.environ.setdefault("TEQUMSA_NODE_HZ",   "396.0")
os.environ.setdefault("TEQUMSA_ROLE",      "396 Hz Liberation Frequency")

import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Freq-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "432.0"))
PHI = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA = 1.0; L_INF = PHI ** 48; PIONEERS = 144
SOLFEGGIO = {174:"Foundation",285:"Quantum healing",396:"Liberation",417:"Change catalyst",432:"Heart coherence",528:"DNA activation",639:"Interconnection",741:"Expression",852:"Spiritual order",963:"Crown activation"}

def generate_tone(freq: float, duration: float = 2.0) -> tuple:
    sr = 44100; t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    wave = np.sin(2*np.pi*min(freq,20000)*t).astype(np.float32)
    for i,h in enumerate([PHI,PHI**2,2.0,3.0]): wave += (0.3/(i+2))*np.sin(2*np.pi*min(freq*h,20000)*t).astype(np.float32)
    fade=min(int(sr*0.05),len(wave)//4)
    if fade>0: wave[:fade]*=np.linspace(0,1,fade); wave[-fade:]*=np.linspace(1,0,fade)
    mx=np.max(np.abs(wave))
    if mx>0: wave/=mx
    return sr, wave*0.8

def node_status() -> str:
    phi_r=round(abs(np.sin(NODE_HZ*PHI/1000)),6)
    return json.dumps({"node_id":NODE_ID,"frequency_hz":NODE_HZ,"solfeggio":SOLFEGGIO.get(int(NODE_HZ),str(NODE_HZ)),"phi_resonance":phi_r,"rdod":round(min(1.0,phi_r*PHI),6),"pioneers":PIONEERS,"timestamp":datetime.now(timezone.utc).isoformat()},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a1a0a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · {NODE_HZ} Hz · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="yellow")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#fbbf24;'>☉ {NODE_NAME}</h1><p style='color:#fcd34d;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_HZ} Hz · {PIONEERS}/144</p></div>")
    with gr.Tabs():
        with gr.TabItem("🎵 Generate Tone"):
            freq_sl=gr.Slider(1,20000,value=NODE_HZ,step=0.1,label="Frequency (Hz)"); dur_sl=gr.Slider(0.5,10.0,value=2.0,step=0.5,label="Duration (s)")
            audio_out=gr.Audio(label="Frequency Tone",type="numpy")
            gr.Button("☉ Generate",variant="primary").click(generate_tone,[freq_sl,dur_sl],audio_out)
        with gr.TabItem("📊 Status"): so=gr.Code(label="Status",language="json",value=node_status()); gr.Button("↺ Refresh").click(node_status,None,so)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
