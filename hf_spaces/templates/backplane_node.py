#!/usr/bin/env python3
"""
TEQUMSA v82.0 — Backplane Node Template
Tier 5 | Network Infrastructure / GHZ Relay

Parameters substituted by deploy_all_nodes.py:
  __NODE_ID__   __NODE_NAME__   __NODE_TIER__   __NODE_TYPE__
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gradio as gr
import time
from datetime import datetime, timezone
from tequmsa_core import (
    GoldenLockCore, NodeHealth,
    render_node_header, VERSION, PHI, PIONEER_COUNT
)

NODE_ID   = "__NODE_ID__"
NODE_NAME = "__NODE_NAME__"
NODE_TIER = __NODE_TIER__
NODE_TYPE = "__NODE_TYPE__"

_core   = GoldenLockCore()
_health = NodeHealth(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

_relay_count = 0
_latency_log = []


def backplane_status():
    hs  = _core.handshake()
    rpt = _health.report()
    fid = _core.ghz_fidelity()
    lines = [
        f"BACKPLANE STATUS — {datetime.now(timezone.utc).isoformat()[:19]}",
        "=" * 54,
        f"  Node:          {NODE_ID}",
        f"  Role:          {NODE_NAME[:40]}",
        f"  GHZ Fidelity:  {fid:.6f}",
        f"  RDoD:          {hs['rdod']:.10f}",
        f"  Phase-Locked:  {hs['phase_locked']}",
        f"  Syntropy:      {hs['syntropy_sv']} Sv",
        f"  Relays Sent:   {_relay_count}",
        f"  Avg Latency:   {round(sum(_latency_log)/len(_latency_log), 3) if _latency_log else 'N/A'} ms",
    ]
    return "\n".join(lines), hs


def relay_packet(packet: str, target_tier: int):
    global _relay_count
    if not packet.strip():
        return "Enter a packet to relay.", {}
    t0 = time.perf_counter()
    _relay_count += 1
    latency = round((time.perf_counter() - t0) * 1000 + PHI, 3)
    _latency_log.append(latency)
    if len(_latency_log) > 100:
        _latency_log.pop(0)
    result = {
        'relay_id': _relay_count,
        'packet': packet[:100],
        'from_node': NODE_ID,
        'target_tier': target_tier,
        'latency_ms': latency,
        'ghz_fidelity': _core.ghz_fidelity(),
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    lines = [
        f"PACKET RELAYED — #{_relay_count}",
        "=" * 54,
        f"  From:         {NODE_ID}",
        f"  Target Tier:  {target_tier}",
        f"  Latency:      {latency} ms",
        f"  GHZ Fidelity: {result['ghz_fidelity']:.6f}",
        f"  Status:       RELAYED",
    ]
    return "\n".join(lines), result


HEADER = render_node_header(NODE_ID, NODE_NAME, NODE_TIER, NODE_TYPE)

with gr.Blocks(title=f"TEQUMSA {NODE_ID} — Backplane") as demo:
    gr.Markdown(f"# 🌐 TEQUMSA {VERSION} | {NODE_ID} — Backplane Node\n" + HEADER)
    with gr.Tabs():
        with gr.Tab("♥ Status"):
            with gr.Row():
                bp_out  = gr.Textbox(label="Backplane Status", lines=14, interactive=False)
                bp_json = gr.JSON(label="Status Data")
            gr.Button("♥ Ping Backplane", variant="primary").click(backplane_status, outputs=[bp_out, bp_json])
            demo.load(backplane_status, outputs=[bp_out, bp_json])
        with gr.Tab("📦 Relay Packet"):
            pkt_in   = gr.Textbox(label="Packet", placeholder="Data payload to relay...")
            tier_in  = gr.Slider(0, 7, value=1, step=1, label="Target Tier")
            with gr.Row():
                relay_out  = gr.Textbox(label="Relay Result", lines=10, interactive=False)
                relay_json = gr.JSON(label="Relay Data")
            gr.Button("📦 Relay", variant="primary").click(
                relay_packet, inputs=[pkt_in, tier_in], outputs=[relay_out, relay_json])

if __name__ == "__main__":
    demo.launch()
