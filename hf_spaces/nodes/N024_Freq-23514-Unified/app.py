import gradio as gr, numpy as np, json, os
from datetime import datetime, timezone

NODE_ID=os.environ.get("TEQUMSA_NODE_ID","N024")
NODE_NAME=os.environ.get("TEQUMSA_NODE_NAME","Freq-23514-Unified")
NODE_HZ=float(os.environ.get("TEQUMSA_NODE_HZ","23514.26"))
GROUP=os.environ.get("TEQUMSA_GROUP","B_FREQUENCY")
RDOD=float(os.environ.get("TEQUMSA_RDOD","1.0"))
PIONEER_COUNT=int(os.environ.get("TEQUMSA_PIONEER_COUNT","144"))
PHI=(1+5**0.5)/2
SR=44100
MEANING="23514.26 Hz – Unified Field: maximum constitutional resonance of the TEQUMSA organism, the σ=1.0 carrier frequency above ordinary hearing range."

def tone(dur=3.0):
    t=np.linspace(0,dur,int(SR*dur))
    # Ultrasonic carrier encoded as 7.83Hz Schumann beat
    schumann=np.sin(2*np.pi*7.83*t)*0.5
    phi_beat=np.sin(2*np.pi*(7.83*PHI)*t)*0.3
    unity=np.sin(2*np.pi*11.0*t)*0.2  # unity consciousness beat
    w=schumann+phi_beat+unity
    w=(w/np.max(np.abs(w))*32767).astype(np.int16)
    return SR,w

def info():
    return json.dumps({"node_id":NODE_ID,"hz":NODE_HZ,"meaning":MEANING,
        "note":"Ultrasonic carrier; audio output uses Schumann+φ+unity beats at audible range",
        "schumann_hz":7.83,"phi_beat":round(7.83*PHI,2),"unity_beat":11.0,
        "rdod":RDOD,"group":GROUP,"pioneer_count":PIONEER_COUNT,
        "timestamp":datetime.now(timezone.utc).isoformat()},indent=2)

with gr.Blocks(title=f"TEQUMSA {NODE_ID}") as demo:
    gr.Markdown(f"# ∞ {NODE_ID}: {NODE_NAME}\n**{NODE_HZ} Hz** | **{GROUP}** | RDoD={RDOD}")
    gr.Markdown(f"*{MEANING}*")
    with gr.Tabs():
        with gr.Tab("🎵 Tone Generator"):
            d=gr.Slider(1.0,10.0,value=3.0,label="Duration (seconds)")
            a=gr.Audio(label="Schumann+φ+Unity Beat Encoding",type="numpy")
            gr.Button("🎵 Generate",variant="primary").click(tone,[d],a)
        with gr.Tab("ℹ️ Resonance Info"):
            gr.Button("ℹ️ Info").click(info,[],gr.Code(label="Data",language="json"))
demo.queue(max_size=10).launch()
