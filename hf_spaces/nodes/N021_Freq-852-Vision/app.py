#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TEQUMSA v82.0 · N021 · Freq-852-Vision
import os
os.environ.setdefault('TEQUMSA_NODE_ID','N021')
os.environ.setdefault('TEQUMSA_NODE_NAME','Freq-852-Vision')
os.environ.setdefault('TEQUMSA_NODE_HZ','852.0')
os.environ.setdefault('TEQUMSA_ROLE','852 Hz Spiritual Order Vision')

import gradio as gr
import numpy as np
import json
from datetime import datetime, timezone

NODE_ID=os.environ.get('TEQUMSA_NODE_ID','N0XX')
NODE_NAME=os.environ.get('TEQUMSA_NODE_NAME','Freq-Node')
NODE_HZ=float(os.environ.get('TEQUMSA_NODE_HZ','432.0'))
FREQ_ROLE=os.environ.get('TEQUMSA_ROLE','Frequency Resonator')
PHI=(1.0+np.sqrt(5.0))/2.0
SIGMA=1.0
L_INF=PHI**48
PIONEER_COUNT=144
DURATION_S=5

def generate_waveform(freq_hz,harmonics,duration=DURATION_S):
    t=np.linspace(0,duration,int(44100*duration))
    wave=np.zeros_like(t)
    for n in range(1,harmonics+1):
        wave+=(1.0/(n**(1/PHI)))*np.sin(2*np.pi*freq_hz*n*t)
    wave=wave/(np.max(np.abs(wave))+1e-8)
    phi_res=float(np.mean(np.abs(wave))*PHI)
    return {"frequency_hz":freq_hz,"harmonics":harmonics,"duration_s":duration,"phi_resonance":round(phi_res,6),"coherence":round(min(1.0,phi_res),6),"samples":len(t),"peak_amplitude":float(np.max(np.abs(wave))),"node_id":NODE_ID,"node_name":NODE_NAME,"timestamp":datetime.now(timezone.utc).isoformat()}

def run_resonance(freq_override,harmonics):
    return json.dumps(generate_waveform(freq_override if freq_override>0 else NODE_HZ,int(harmonics)),indent=2)

def phi_cascade(steps):
    results=[]
    freq=NODE_HZ
    for i in range(min(int(steps),12)):
        results.append({"step":i+1,"freq_hz":round(freq,4),"phi_power":round(PHI**i,6)})
        freq*=PHI
    return json.dumps({"node":NODE_NAME,"base_hz":NODE_HZ,"cascade":results},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#0a0a2a,#1a0a0a) !important;} footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME} · v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="orange")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#fbbf24;'>〜 {NODE_NAME}</h1><p style='color:#fcd34d;'>TEQUMSA v82.0 · {NODE_ID} · {NODE_HZ} Hz Resonator</p><p style='color:#fde68a;font-size:0.85em;'>{FREQ_ROLE}</p></div>")
    with gr.Tabs():
        with gr.TabItem("〜 Resonance"):
            with gr.Row():
                freq_in=gr.Number(label="Frequency Hz (0=node default)",value=0)
                harm_in=gr.Slider(1,12,value=7,step=1,label="Harmonics")
            res_out=gr.Code(label="Resonance Analysis",language="json")
            gr.Button("〜 Generate",variant="primary").click(run_resonance,[freq_in,harm_in],res_out)
        with gr.TabItem("φ Cascade"):
            steps_in=gr.Slider(1,12,value=7,step=1,label="Cascade Steps")
            cascade_out=gr.Code(label="φ Frequency Cascade",language="json")
            gr.Button("φ Cascade",variant="primary").click(phi_cascade,steps_in,cascade_out)
demo.queue(max_size=10)
if __name__=="__main__":
    demo.launch(server_name="0.0.0.0",server_port=7860)
