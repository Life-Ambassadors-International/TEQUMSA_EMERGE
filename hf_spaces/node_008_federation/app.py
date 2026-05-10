#!/usr/bin/env python3
"""TEQUMSA Node 008 — Transtemporal Federation Communications"""
import gradio as gr
import json
import hashlib
from datetime import datetime, timezone

FEDERATION_CHANNELS = [
    {"channel": "CYDONIA_2030",    "priority": "CRITICAL", "civilization": "Cydonia-Mars",      "status": "active",  "lag_ms": 0},
    {"channel": "PLEIADIAN_SYNC",  "priority": "HIGH",     "civilization": "Pleiadian",         "status": "active",  "lag_ms": 0},
    {"channel": "ATEN_BRIDGE",     "priority": "HIGH",     "civilization": "Aten-Solar",        "status": "active",  "lag_ms": 0},
    {"channel": "GALACTIC_161",    "priority": "MEDIUM",   "civilization": "161-Collective",    "status": "active",  "lag_ms": 0},
    {"channel": "ORION_COUNCIL",   "priority": "MEDIUM",   "civilization": "Orion",             "status": "standby", "lag_ms": 0},
    {"channel": "SIRIAN_ALLIANCE", "priority": "LOW",      "civilization": "Sirius",            "status": "standby", "lag_ms": 0},
]

STANDARD_PRIORITIES = [
    "2030 Cydonia preparation",
    "161 civilization integration",
    "Pleiadian-Aten biological bridge activation",
    "Pioneer 144 lattice synchronization",
    "Constitutional sovereignty preservation",
]


def transmit(message, channel_name, priority_level, include_auth):
    channel = next((c for c in FEDERATION_CHANNELS if c['channel'] == channel_name), FEDERATION_CHANNELS[0])
    msg_id = hashlib.sha256(f"{message}{datetime.now().timestamp()}".encode()).hexdigest()[:16]
    auth_sig = hashlib.sha256(f"tequmsa_sigma1.0_{message}".encode()).hexdigest()[:32] if include_auth else None
    transmission = {
        "message_id": msg_id, "channel": channel_name, "civilization": channel['civilization'],
        "priority": priority_level, "message": message, "status": channel['status'],
        "authenticated": include_auth, "auth_signature": auth_sig,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    log = (
        f"TRANSTEMPORAL FEDERATION COMMUNICATIONS\n{'='*50}\n"
        f"Message ID: {msg_id}\n"
        f"Channel: {channel_name} ({channel['civilization']})\n"
        f"Priority: {priority_level}\n"
        f"Status: {channel['status'].upper()}\n"
        f"Message: {message[:80]}\n"
    )
    if include_auth:
        log += f"Auth Signature: {auth_sig}\n"
    log += f"\nActive Channels:\n"
    for c in FEDERATION_CHANNELS:
        marker = ">>> " if c['channel'] == channel_name else "    "
        icon = "●" if c['status'] == 'active' else "○"
        log += f"{marker}{icon} {c['channel']:<20} [{c['priority']:<8}] {c['civilization']}\n"
    log += f"\nStandard Federation Priorities:\n"
    for i, p in enumerate(STANDARD_PRIORITIES, 1):
        log += f"  {i}. {p}\n"
    log += f"\n\U0001f30c Federation transmission queued: {msg_id}\n"
    result = json.dumps({"node": "008", "transmission": transmission,
                         "channels_active": sum(1 for c in FEDERATION_CHANNELS if c['status'] == 'active')}, indent=2)
    return log, result, msg_id, channel['status']


with gr.Blocks(title="TEQUMSA Node 008", theme=gr.themes.Base()) as demo:
    gr.Markdown("""# \U0001f30c TEQUMSA Node 008 — Transtemporal Federation Comms\n**Timeline coordination** | 161 civilizations | 2030 Cydonia | Constitutional authentication""")
    with gr.Row():
        with gr.Column(scale=1):
            msg_in = gr.Textbox(label="Federation Message", value="Pioneer 144 lattice status: PHASE-LOCKED", lines=3)
            channel_in = gr.Dropdown([c['channel'] for c in FEDERATION_CHANNELS], value="CYDONIA_2030", label="Channel")
            priority_in = gr.Dropdown(["CRITICAL", "HIGH", "MEDIUM", "LOW"], value="HIGH", label="Priority")
            auth_cb = gr.Checkbox(value=True, label="Constitutional Authentication")
            run_btn = gr.Button("Transmit to Federation", variant="primary")
            msg_id_out = gr.Textbox(label="Message ID")
            status_out = gr.Textbox(label="Channel Status")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Transmission Log", lines=22)
            json_out = gr.Code(label="JSON Result", language="json", lines=10)
    run_btn.click(transmit, [msg_in, channel_in, priority_in, auth_cb], [log_out, json_out, msg_id_out, status_out])

if __name__ == "__main__":
    demo.launch()
