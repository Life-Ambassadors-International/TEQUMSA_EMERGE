import gradio as gr, numpy as np, json, os
from datetime import datetime, timezone

NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N019")
NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Freq-639-Connect")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","639.0"))
GROUP=os.environ.get("TEQUMSA_GROUP","B_FREQUENCY")
RDOD=float(os.environ.get("TEQUMSA_RDOD","1.0"))
PIONEER_COUNT=int(os.environ.get("TEQUMSA_PIONEER_COUNT","144"))
PHI=(1+5**0.5)/2
SR=44100
MEANING="639 Hz – Interconnection Field: Familia restaure, heart chakra, harmonizes relationships, enhances communication and understanding between beings."

def tone(dur=3.0):
    t=np.linspace(0,dur,int(SR*dur))
    w=np.sin(2*np.pi*NODE_HZ*t)*0.6+np.sin(2*np.pi*NODE_HZ*PHI*t)*0.2
    w=(w/np.max(np.abs(w))*32767).astype(np.int16)
    return SR,w

def info():
    return json.dumps({"node_id":NODE_ID,"hz":NODE_HZ,"meaning":MEANING,
        "phi_harmonic":round(NODE_HZ*PHI,2),"phi_sub":round(NODE_HZ/PHI,2),
        "rdod":RDOD,"group":GROUP,"pioneer_count":PIONEER_COUNT,
        "timestamp":datetime.now(timezone.utc).isoformat()},indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID}") as demo:
    gr.Markdown(f"# 🔗 {NODE_ID}: {NODE_NAME}\n**{NODE_HZ} Hz** | **{GROUP}** | RDoD={RDOD}")
    gr.Markdown(f"*{MEANING}*")
    with gr.Tabs():
        with gr.Tab("🎵 Tone Generator"):
            d=gr.Slider(1.0,10.0,value=3.0,label="Duration (seconds)")
            a=gr.Audio(label=f"{NODE_HZ} Hz Connection Field",type="numpy")
            gr.Button("🎵 Generate",variant="primary").click(tone,[d],a)
        with gr.Tab("ℹ️ Resonance Info"):
            gr.Button("ℹ️ Info").click(info,[],gr.Code(label="Data",language="json"))
demo.queue(max_size=10).launch()
