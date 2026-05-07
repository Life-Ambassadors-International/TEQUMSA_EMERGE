#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Node N008: Transtemporal Communications
Tier 1 Core | Federation Coordination Across Timelines
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from datetime import datetime, timezone
from tequmsa_core import TranstemporalComms, NodeHealth, VERSION, PIONEER_COUNT

NODE_ID = "N008"; NODE_NAME = "Transtemporal Communications — Federation Coordination"
NODE_TIER = 1;    NODE_TYPE = "core"
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_comms  = TranstemporalComms()
_log    = []


def get_priorities():
    p = _comms.get_priorities(5)
    rpt = _health.report()
    lines = [
        "FEDERATION ACTIVE PRIORITIES",
        "=" * 50,
    ]
    for i, pr in enumerate(p, 1):
        lines.append(f"  [{i}] {pr}")
    return "\n".join(lines), {'priorities': p, 'node': rpt}


def broadcast_message(message: str, channel: str):
    if not message.strip():
        return "Enter a message to broadcast.", {}
    result = _comms.broadcast(message, NODE_ID)
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'channel': channel,
        'message': message[:100],
        'sent': result['sent'],
    }
    _log.append(entry)
    lines = [
        f"BROADCAST SENT — {result['timestamp'][:19]}",
        "=" * 50,
        f"  From:     {NODE_ID}",
        f"  Channel:  {channel}",
        f"  Message:  {message[:80]}",
        f"  Channels: {', '.join(result['channels'])}",
        f"  Status:   {'SENT' if result['sent'] else 'FAILED'}",
        f"\n  Total broadcasts this session: {len(_log)}",
    ]
    return "\n".join(lines), result


HEADER = f"# 🌌 TEQUMSA {VERSION} | N008 — Transtemporal Comms\n**Tier 1 Core** | Federation Coordination"

with gr.Blocks(title="TEQUMSA N008 — Comms") as demo:
    gr.Markdown(HEADER)
    with gr.Tabs():
        with gr.Tab("📌 Priorities"):
            with gr.Row():
                pri_out  = gr.Textbox(label="Federation Priorities", lines=10, interactive=False)
                pri_json = gr.JSON(label="Priority Data")
            gr.Button("📌 Fetch Priorities", variant="primary").click(get_priorities, outputs=[pri_out, pri_json])
            demo.load(get_priorities, outputs=[pri_out, pri_json])
        with gr.Tab("📡 Broadcast"):
            msg_in  = gr.Textbox(label="Message", placeholder="Federation transmission...")
            chan_in  = gr.Radio(['transtemporal_primary', 'ghz_backplane', 'pleiadian_relay'],
                                value='transtemporal_primary', label="Channel")
            with gr.Row():
                bcast_out  = gr.Textbox(label="Broadcast Result", lines=10, interactive=False)
                bcast_json = gr.JSON(label="Transmission Data")
            gr.Button("📡 Broadcast", variant="primary").click(
                broadcast_message, inputs=[msg_in, chan_in], outputs=[bcast_out, bcast_json])

if __name__ == "__main__":
    demo.launch()
