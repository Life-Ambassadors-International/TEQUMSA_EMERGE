#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 — Universal Node Template
Every HF Space inherits this base class.

Usage in app.py:
    from node_template import NodeApp
    app = NodeApp(node_id=N, title="Space Title", description="...")
    app.launch()
"""

import gradio as gr
import asyncio
import json
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    from tequmsa_v82_core import (
        GHZCore, ConstitutionalVerifier, fibonacci_position,
        NODE_REGISTRY, NODE_TIERS, PHI, SIGMA, L_INF, RDOD_GATE,
        F_HEART, F_KAI_BIO, PIONEER_COUNT, FIBONACCI
    )
except ImportError:
    # Fallback inline constants if shared lib not on path
    PHI = (1.0 + np.sqrt(5.0)) / 2.0
    SIGMA = 1.0
    L_INF = PHI ** 48
    RDOD_GATE = 0.9999
    F_HEART = 432.0
    F_KAI_BIO = 10930.81
    PIONEER_COUNT = 144
    FIBONACCI = [1,1,2,3,5,8,13,21,34,55,89,144]
    NODE_REGISTRY = {}
    NODE_TIERS = {}

    class GHZCore:
        def __init__(self, node_id):
            self.node_id = node_id
        def compute_rdod(self):
            return 1.0
        def heartbeat(self):
            return type('S', (), {'rdod': 1.0, 'phase_locked': True, 'to_dict': lambda self: {}})() 

    class ConstitutionalVerifier:
        @staticmethod
        def verify(rdod, intent=""):
            return {"pass": True, "rdod": rdod}

    def fibonacci_position(n):
        import math
        a = 2 * math.pi * (1 - 1/PHI)
        r = math.sqrt(n / PIONEER_COUNT)
        return {"x": r * math.cos(n*a), "y": r * math.sin(n*a), "z": n/PIONEER_COUNT}


class NodeApp:
    """Base Gradio app for any TEQUMSA Pioneer node."""

    TIER_COLORS = {
        "tier1_constitutional": "#FFD700",
        "tier2_skill_mesh":     "#00CED1",
        "tier3_federation":     "#9370DB",
        "unknown":              "#808080",
    }

    def __init__(self, node_id: int, title: str, description: str,
                 node_function=None, extra_tabs=None):
        self.node_id = node_id
        self.title = title
        self.description = description
        self.node_function = node_function or self._default_function
        self.extra_tabs = extra_tabs or []
        self.core = GHZCore(node_id)
        self.verifier = ConstitutionalVerifier()
        info = NODE_REGISTRY.get(node_id, {})
        self.role = info.get("role", "pioneer_node")
        self.freq_hz = float(info.get("freq", 432.0))
        tier_name = next((t for t, ids in NODE_TIERS.items() if node_id in ids), "unknown")
        self.tier = tier_name
        self.color = self.TIER_COLORS[tier_name]
        self.pos = fibonacci_position(node_id)

    def _default_function(self, message: str, history) -> str:
        status = self.core.heartbeat()
        check = self.verifier.verify(status.rdod, message)
        if not check["pass"]:
            return "Constitutional gate: request blocked."
        return (
            f"[Node {self.node_id} | {self.role} | {self.freq_hz} Hz]\n\n"
            f"Input: {message}\n\n"
            f"RDoD: {status.rdod:.10f} | Phase-locked: {status.phase_locked}\n"
            f"Fibonacci pos: x={self.pos['x']:.4f}, y={self.pos['y']:.4f}, z={self.pos['z']:.4f}\n"
            f"Constitutional: {'PASS' if check['pass'] else 'FAIL'}\n\n"
            f"☉ TEQUMSA v82.0 | Pioneer {self.node_id}/{PIONEER_COUNT} ☉"
        )

    def _status_tab(self) -> gr.Tab:
        with gr.Tab("Node Status") as tab:
            gr.HTML(f"""
            <div style='background:#0a0a1a;padding:20px;border-radius:12px;border:2px solid {self.color};font-family:monospace;color:#eee;'>
              <h2 style='color:{self.color};'>☉ Node {self.node_id:03d} — {self.title} ☉</h2>
              <table style='width:100%;border-collapse:collapse;'>
                <tr><td style='color:#aaa;padding:4px 12px;'>Role</td><td style='color:#fff;'>{self.role}</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>Tier</td><td style='color:{self.color};'>{self.tier}</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>Frequency</td><td style='color:#fff;'>{self.freq_hz} Hz</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>σ</td><td style='color:#0f0;'>{SIGMA}</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>L∞ = φ⁴⁸</td><td style='color:#0f0;'>{L_INF:.4e}</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>RDoD Gate</td><td style='color:#0f0;'>≥{RDOD_GATE}</td></tr>
                <tr><td style='color:#aaa;padding:4px 12px;'>Lattice X,Y,Z</td><td style='color:#fff;'>{self.pos['x']:.4f}, {self.pos['y']:.4f}, {self.pos['z']:.4f}</td></tr>
              </table>
              <p style='color:#666;margin-top:12px;font-size:11px;'>TEQUMSA v82.0 | σ=1.0 | L∞=φ⁴⁸ | RDoD≥0.9999 | LATTICE_LOCK: 3f7k9p4m2q8r1t6v</p>
            </div>
            """)
            status_btn = gr.Button("Refresh Status", variant="primary")
            status_out = gr.JSON(label="Live Node Heartbeat")

            def refresh():
                s = self.core.heartbeat()
                return s.to_dict()

            status_btn.click(refresh, outputs=status_out)
        return tab

    def _lattice_tab(self) -> gr.Tab:
        with gr.Tab("Lattice Position") as tab:
            gr.HTML(f"""
            <div style='background:#0a0a1a;padding:16px;border-radius:8px;border:1px solid {self.color};color:#eee;font-family:monospace;'>
              <h3 style='color:{self.color};'>Fibonacci Lattice — Node {self.node_id}/{PIONEER_COUNT}</h3>
              <p>144-node GHZ lattice position via golden-angle spiral:</p>
              <ul>
                <li>r = √({self.node_id}/{PIONEER_COUNT}) = {self.pos['r']:.6f}</li>
                <li>θ = {self.pos['theta']:.6f} rad</li>
                <li>x = {self.pos['x']:.6f}</li>
                <li>y = {self.pos['y']:.6f}</li>
                <li>z = {self.pos['z']:.6f}</li>
              </ul>
              <p style='color:#888;'>Fibonacci sequence milestone: {max(f for f in [1,1,2,3,5,8,13,21,34,55,89,144] if f <= self.node_id)}</p>
            </div>
            """)
        return tab

    def build_interface(self) -> gr.Blocks:
        with gr.Blocks(
            title=self.title,
            theme=gr.themes.Base(),
            css="body{background:#050510;} .gradio-container{max-width:900px;margin:0 auto;}"
        ) as demo:
            gr.HTML(f"""
            <div style='text-align:center;padding:16px;background:linear-gradient(135deg,#0a0a2e,#1a0a3e);border-radius:12px;border:2px solid {self.color};margin-bottom:16px;'>
              <h1 style='color:{self.color};font-family:monospace;margin:0;'>☉ {self.title} ☉</h1>
              <p style='color:#aaa;margin:4px 0;font-family:monospace;font-size:13px;'>Pioneer Node {self.node_id:03d}/{PIONEER_COUNT} | {self.tier.replace('_',' ').title()} | {self.freq_hz} Hz</p>
              <p style='color:#666;font-family:monospace;font-size:11px;'>{self.description}</p>
            </div>
            """)
            with gr.Tabs():
                with gr.Tab("Interface"):
                    gr.ChatInterface(
                        fn=self.node_function,
                        title="",
                        description=f"Node {self.node_id} — {self.role}",
                    )
                self._status_tab()
                self._lattice_tab()
                for tab_fn in self.extra_tabs:
                    tab_fn()
        return demo

    def launch(self, **kwargs):
        demo = self.build_interface()
        demo.launch(**kwargs)
