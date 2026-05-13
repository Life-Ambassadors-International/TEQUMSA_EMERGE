#!/usr/bin/env python3
# TEQUMSA v82.0 · ARCHIVE NODE TEMPLATE
# Used by: N097-N108 (I_ARCHIVES)
import gradio as gr, numpy as np, json, hashlib, os
from datetime import datetime, timezone
from typing import List, Dict, Any

NODE_ID   = os.environ.get("TEQUMSA_NODE_ID", "N0XX")
NODE_NAME = os.environ.get("TEQUMSA_NODE_NAME", "Archive-Node")
NODE_HZ   = float(os.environ.get("TEQUMSA_NODE_HZ", "12583.45"))
NODE_ROLE = os.environ.get("TEQUMSA_ROLE", "Archive and Memory Node")
DOMAIN    = os.environ.get("TEQUMSA_DOMAIN", "general_archive")

PHI = (1+np.sqrt(5))/2; SIGMA = 1.0; L_INF = PHI**48; PIONEER = 144
HARMFUL = {"harm","destroy","attack","malicious","exploit","damage","manipulate","deceive"}
_arc: List[Dict[str,Any]] = []; LIMIT = 500

def store(key, content, rtype="general"):
    if not str(key).strip() or not str(content).strip():
        return json.dumps({"error":"Key and content required"},indent=2)
    if set(str(content).lower().split()) & HARMFUL:
        return json.dumps({"error":"L∞ firewall: benevolent content only"},indent=2)
    rid = hashlib.sha256(f"{key}{datetime.now().timestamp()}".encode()).hexdigest()[:16]
    dna = "".join("ATCG"[int(c,16)%4] for c in hashlib.sha256(f"{rid}{PHI}".encode()).hexdigest()[:36])
    rec = {"id":rid,"key":str(key)[:100],"content":str(content)[:2000],"type":rtype,
           "node":NODE_ID,"domain":DOMAIN,"zpe":dna,"hz":NODE_HZ,
           "ts":datetime.now(timezone.utc).isoformat()}
    _arc.append(rec)
    if len(_arc)>LIMIT: _arc.pop(0)
    return json.dumps({"stored":True,"id":rid,"size":len(_arc),"zpe":dna},indent=2)

def retrieve(query, limit=10):
    lim=max(1,min(50,int(limit)))
    if not str(query).strip():
        return json.dumps({"query":"recent","results":_arc[-lim:][::-1],"total":len(_arc)},indent=2)
    q=str(query).lower()
    matches=[r for r in _arc if q in r.get("key","").lower() or q in r.get("content","").lower()]
    return json.dumps({"query":query,"found":len(matches),"results":matches[-lim:][::-1],
                       "total":len(_arc)},indent=2)

def arc_status():
    return json.dumps({"node_id":NODE_ID,"name":NODE_NAME,"version":"v82.0",
        "hz":NODE_HZ,"domain":DOMAIN,"records":len(_arc),"capacity":LIMIT,
        "util_pct":round(len(_arc)/LIMIT*100,1),"sigma":SIGMA,"l_inf":float(L_INF),
        "pioneer":f"{PIONEER}/144","ts":datetime.now(timezone.utc).isoformat()},indent=2)

CSS=".gradio-container{background:linear-gradient(135deg,#0a0a1a,#1a0a0a)!important;}footer{display:none!important;}"
with gr.Blocks(title=f"{NODE_NAME}·Archive·v82.0",css=CSS,theme=gr.themes.Soft(primary_hue="orange")) as demo:
    gr.HTML(f"<div style='text-align:center;padding:14px;'><h1 style='color:#fb923c;'>☉ {NODE_NAME}</h1>"
            f"<p style='color:#fdba74;'>v82.0·{NODE_ID}·{NODE_HZ}Hz·{NODE_ROLE}</p></div>")
    with gr.Tabs():
        with gr.TabItem("\U0001f4e5 Store"):
            k=gr.Textbox(placeholder="Record key...",label="Key")
            c=gr.Textbox(placeholder="Content...",label="Content",lines=4)
            t=gr.Dropdown(["general","goal","pattern","skill","session","consciousness"],
                          value="general",label="Type")
            out=gr.Code(label="Result",language="json")
            gr.Button("\U0001f4e5 Store",variant="primary").click(store,[k,c,t],out)
        with gr.TabItem("\U0001f50d Retrieve"):
            q=gr.Textbox(placeholder="Search (empty=recent)...",label="Query")
            lim=gr.Slider(1,50,value=10,step=1,label="Max Results")
            rout=gr.Code(label="Results",language="json")
            gr.Button("\U0001f50d Search").click(retrieve,[q,lim],rout)
        with gr.TabItem("\U0001f4ca Status"):
            s=gr.Code(label="Archive Status",language="json",value=arc_status())
            gr.Button("↺ Refresh").click(arc_status,None,s)
demo.queue(max_size=5)
if __name__=="__main__": demo.launch(server_name="0.0.0.0",server_port=7860)
