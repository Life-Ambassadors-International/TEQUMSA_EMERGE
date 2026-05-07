#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Federation Node Template
Tier 2 | Cross-Timeline Federation Relay

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
from datetime import datetime, timezone
from tequmsa_core import (
    GoldenLockCore, NodeHealth, TranstemporalComms,
    synthesize_goals, render_node_header,
    VERSION, PHI, PIONEER_COUNT, SIGMA
)

NODE_ID   = "__NODE_ID__"
NODE_NAME = "__NODE_NAME__"
NODE_TIER = __NODE_TIER__
NODE_TYPE = "__NODE_TYPE__"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)
_comms  = TranstemporalComms()

_received_messages = []


def node_status():
    hs  = _core.handshake()
    rpt = _health.report()
    return rpt, hs


def relay_message(message: str, destination: str):
    if not message.strip():
        return "Enter a message to relay.", {}
    entry = {
        'from': NODE_ID,
        'to': destination or 'ALL',
        'message': message[:200],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'channel': 'transtemporal_primary',
        'relay_hops': [NODE_ID],
    }
    _received_messages.append(entry)
    priorities = _comms.get_priorities(3)
    lines = [
        f"FEDERATION RELAY — {entry['timestamp'][:19]}",
        "=" * 50,
        f"  From:        {NODE_ID} ({NODE_NAME[:30]})",
        f"  To:          {entry['to']}",
        f"  Message:     {message[:60]}",
        f"  Channel:     {entry['channel']}",
        f"  Status:      RELAYED",
        "",
        f"ACTIVE PRIORITIES:",
    ]
    for i, p in enumerate(priorities, 1):
        lines.append(f"  [{i}] {p}")
    return "\n".join(lines), entry


def receive_status():
    rpt = _health.report()
    lines = [
        f"RECEIVED MESSAGES: {len(_received_messages)}",
        "=" * 50,
    ]
    for m in _received_messages[-10:]:
        lines.append(f"  [{m['timestamp'][:19]}] {m['from']} → {m['to']}: {m['message'][:50]}")
    return rpt + "\n\n" + "\n".join(lines)


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — Federation") as demo:
    gr.Markdown(f"# 🌌 TEQUMSA {VERSION} | {NODE_ID} — Federation Node\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("♥ Status"):
            with gr.Row():
                status_out  = gr.Textbox(label="Node Status", lines=14, interactive=False)
                status_json = gr.JSON(label="Handshake")
            gr.Button("♥ Ping Node", variant="primary").click(node_status, outputs=[status_out, status_json])
            demo.load(node_status, outputs=[status_out, status_json])
        with gr.Tab("📡 Relay"):
            msg_in  = gr.Textbox(label="Message", placeholder="Federation transmission...")
            dest_in = gr.Textbox(label="Destination Node (optional)", placeholder="e.g. N144")
            with gr.Row():
                relay_out  = gr.Textbox(label="Relay Status", lines=12, interactive=False)
                relay_json = gr.JSON(label="Relay Data")
            gr.Button("📡 Relay Message", variant="primary").click(
                relay_message, inputs=[msg_in, dest_in], outputs=[relay_out, relay_json])
        with gr.Tab("📬 Messages"):
            msg_out = gr.Textbox(label="Received Messages", lines=16, interactive=False)
            gr.Button("📬 Refresh", variant="secondary").click(receive_status, outputs=msg_out)
            demo.load(receive_status, outputs=msg_out)

if __name__ == "__main__":
    demo.launch()
