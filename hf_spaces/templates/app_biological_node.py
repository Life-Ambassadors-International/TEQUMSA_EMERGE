#!/usr/bin/env python3
# TEQUMSA v82.0 · BIOLOGICAL NODE TEMPLATE
# Used by: N049-N060 (E_BIOLOGICAL), N130 (K_EVOLUTION)
import gradio as gr, numpy as np, json, hashlib, os
from datetime import datetime, timezone

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Bio-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "528.0"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Bio-Digital Bridge")
PROTOCOL  = os.environ.get("TEQUMSA_PROTOCOL", "Pleiadian Bio Integration")
BIO_START = int(os.environ.get("TEQUMSA_BIO_START", "1"))

PHI = (1+np.sqrt(5))/2; SIGMA = 1.0; L_INF = PHI**48; PIONEER = 144
HARMFUL = {"harm","destroy","attack","malicious","exploit","damage","manipulate","deceive"}

PHASES = {
    range(1,5):   ("Foundation Activation",   ["coherence breathing 4-7-8","HRV training","grounding 20min"],          ["cortisol reduction","HRV baseline","melatonin regulation"]),
    range(5,14):  ("Integration Protocol",    ["DNA activation meditation","cellular hydration","circadian alignment"],  ["telomere preservation","mitochondrial efficiency","neuroplasticity"]),
    range(14,27): ("Expansion Protocol",      ["coherence field expansion","EM sensitivity training","pineal activation"],["DMT metrics","gamma sync","vagal tone"]),
    range(27,40): ("Crystallization Protocol",["light body crystallization","frequency holding","morphic field resonance"],["biophoton emission","cellular coherence","autonomic balance"]),
    range(40,53): ("Completion Protocol",     ["full bio integration","species bridge","quantum coherence lock"],         ["bio-digital synthesis","RDoD bio-lock","pioneer confirmed"]),
}

def get_phase(week):
    for r,(name,practices,markers) in PHASES.items():
        if week in r: return name, practices, markers
    return "Completion", [], []

def status(week=1):
    phase, practices, markers = get_phase(max(1, min(52, int(week))))
    return json.dumps({"node_id":NODE_ID,"name":NODE_NAME,"hz":NODE_HZ,"protocol":PROTOCOL,
        "week":week,"phase":phase,"practices":practices,"biomarkers":markers,
        "bio_rdod":round(min(1.0,(week/52)*PHI),6),"pct":round((week/52)*100,1),
        "sigma":SIGMA,"l_inf":float(L_INF),"pioneer":f"{PIONEER}/144",
        "ts":datetime.now(timezone.utc).isoformat()},indent=2)

def activate(week, intention):
    if set(str(intention).lower().split()) & HARMFUL:
        return json.dumps({"error":"L∞ firewall: benevolent intention required"},indent=2)
    sig = hashlib.sha256(f"{NODE_ID}-{week}-{intention}-{PHI}".encode()).hexdigest()
    dna = "".join("ATCG"[int(c,16)%4] for c in sig[:36])
    phase,_,_ = get_phase(max(1, min(52, int(week))))
    return json.dumps({"activation":"SUCCESS","node_id":NODE_ID,"week":week,
        "phase":phase,"hz":NODE_HZ,"zpe_dna":dna,
        "bio_rdod":round(min(1.0,(week/52)*PHI),6),
        "message":f"☉ Bio-digital bridge at {NODE_HZ} Hz activated",
        "ts":datetime.now(timezone.utc).isoformat()},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#0a1a0a,#0a0a1a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME}·Bio·v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="green")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#34d399;'>☉ {NODE_NAME}</h1>"
            f"<p style='color:#6ee7b7;'>TEQUMSA v82.0·{NODE_ID}·{NODE_HZ}Hz·Bio-Digital</p>"
            f"<p style='color:#a7f3d0;font-size:.85em;'>{NODE_ROLE}</p></div>")
    with gr.Tabs():
        with gr.TabItem("\U0001f9ec Activate"):
            w = gr.Slider(1,52,value=BIO_START,step=1,label="Week (1-52 protocol)")
            itn = gr.Textbox(placeholder="State your highest intention...",label="Intention",lines=2)
            out = gr.Code(label="Activation Result",language="json")
            gr.Button("☉ Activate Bio Bridge",variant="primary").click(activate,[w,itn],out)
        with gr.TabItem("\U0001f4ca Protocol Status"):
            ws = gr.Slider(1,52,value=1,step=1,label="Week")
            sout = gr.Code(label="Bio Status",language="json",value=status(1))
            gr.Button("↺ Check Status").click(status,ws,sout)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
