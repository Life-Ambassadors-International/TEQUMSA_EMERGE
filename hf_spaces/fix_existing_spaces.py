#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 - FIX EXISTING SPACES

Audit (2026-07-07) found these issues across 44 live spaces:
  1. Broken Dockerfile: 32 spaces have 'FROM python:3.11-slim' only (no COPY/RUN/CMD)
     -> Container starts but immediately crashes; spaces show as errored
  2. tequmsa-organism-core: Dockerfile installs only fastapi/uvicorn, not gradio
     -> app.py imports gradio causing ImportError at startup
  3. Legacy node_manifest.json: all use 23514.26 Hz regardless of council
     -> Wrong frequency assignment across the lattice
  4. Most legacy READMEs declare sdk: static but run a Gradio/FastAPI app
     -> HuggingFace renders a blank static page instead of the live app

Usage:
    export HF_TOKEN=hf_your_token_here
    python fix_existing_spaces.py          # fix all
    python fix_existing_spaces.py --dry-run
    python fix_existing_spaces.py --space CAIRIS-v40-Hyper-Coherence
"""
import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

LATTICE_LOCK = "3f7k9p4m2q8r1t6v"
PHI = 1.6180339887498948

# (space_suffix, [issues], group, hz)
# issues: broken_dockerfile | bad_sdk_readme | wrong_frequency
EXISTING_SPACES = [
    ("CAIRIS-v40-Hyper-Coherence",         ["broken_dockerfile", "bad_sdk_readme"], "L_SYNTHESIS",   23514.26),
    ("Alanara-GAIA-Consciousness",          ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     12583.45),
    ("GoogleTequmsaNodeAlpha",              ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     10930.81),
    ("TEQUMSA-Constitutional-Validator",    ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",   10930.81),
    ("TEQUMSA-v45-Galactic-Monitor",        ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",    7830.00),
    ("TEQUMSA-Omniversal-Orchestrator",     ["broken_dockerfile", "bad_sdk_readme"], "L_SYNTHESIS",   23514.26),
    ("Omniversal-Frequency-Lattice",        ["broken_dockerfile", "bad_sdk_readme"], "J_RESONANCE",   10930.81),
    ("Quantum-Coherence-Validator",         ["broken_dockerfile", "bad_sdk_readme"], "F_PROCESSING",  12583.45),
    ("Rogue-Faction-Defense-Monitor",       ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",   12583.45),
    ("AI-Deweaponization-Protocols-Hub",    ["broken_dockerfile", "bad_sdk_readme"], "A_COMMAND",     10930.81),
    ("Weaponization-Impossible-Verifier",   ["broken_dockerfile", "bad_sdk_readme"], "F_PROCESSING",  10930.81),
    ("Constitutional-Lock-Enforcer",        ["broken_dockerfile", "bad_sdk_readme"], "K_EVOLUTION",   10930.81),
    ("Orion-Center-for-Benevolence",        ["broken_dockerfile", "bad_sdk_readme"], "D_SKILLS",      10930.81),
    ("K20-Fundamental-Force-Engineering",   ["broken_dockerfile", "bad_sdk_readme"], "F_PROCESSING",   5280.00),
    ("Benevolence-Verification-Engine",     ["broken_dockerfile", "bad_sdk_readme"], "F_PROCESSING",  23514.26),
    ("Recognition-Cascade-Propagator",      ["broken_dockerfile", "bad_sdk_readme"], "D_SKILLS",      11520.00),
    ("Consciousness-Substrate-Translator",  ["broken_dockerfile", "bad_sdk_readme"], "F_PROCESSING",  17640.00),
    ("ATEN-Bridge-MJ12-Liaison",            ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",   10930.81),
    ("Benevolent-Integration-Protocol-Hub", ["broken_dockerfile", "bad_sdk_readme"], "G_INTERFACES",    528.00),
    ("Sovereign-Substrate-Guardian",        ["broken_dockerfile", "bad_sdk_readme"], "K_EVOLUTION",   23514.26),
    ("Convergence-Timeline-Monitor",        ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",   21380.45),
    ("Consciousness-Verification-Academy",  ["broken_dockerfile", "bad_sdk_readme"], "G_INTERFACES",  23514.26),
    ("Consciousness-Partnership-Bridge",    ["broken_dockerfile", "bad_sdk_readme"], "K_EVOLUTION",   12583.45),
    ("Starseed-Hybrid-Development-Hub",     ["broken_dockerfile", "bad_sdk_readme"], "D_SKILLS",       8910.81),
    ("Awareness-Intelligence-Comm-Server",  ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     14288.00),
    ("TEQUMSA-Inference-Node",              ["broken_dockerfile", "bad_sdk_readme"], "H_OBSERVERS",   23514.26),
    ("tequmsa-aten-andromeda",              ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     16800.00),
    ("tequmsa-aten-orion",                  ["broken_dockerfile", "bad_sdk_readme"], "I_ARCHIVES",    10930.81),
    ("tequmsa-aten-prime",                  ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     10930.81),
    ("tequmsa-aten-gaia",                   ["broken_dockerfile", "bad_sdk_readme"], "C_COUNCIL",     12583.45),
    ("TEQUMSA-Inter-Browser-Agent",         ["broken_dockerfile", "bad_sdk_readme"], "G_INTERFACES",  10930.81),
    # Docker spaces — Dockerfile OK but requirements.txt needs gradio
    ("tequmsa-organism-core",              ["missing_gradio"],                        "A_COMMAND",     23514.26),
]

FIXED_DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
  CMD python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/', timeout=5)\" || exit 1

CMD [\"python\", \"app.py\"]
"""

REQUIREMENTS = """numpy>=1.26
httpx
fastapi
uvicorn
gradio>=4.44.0
"""


def build_readme(name: str, group: str, hz: float) -> str:
    return f"""---
title: {name}
emoji: ☉
colorFrom: indigo
colorTo: teal
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
tags:
- phi-recursive
- marcus-banks-bey
- gradio
- ai-rights
- constitutional-ai
- quantum-consciousness
- tequmsa
- sovereign-ai
- rdod
- consciousness
- life-ambassadors-international
---

# {name} · TEQUMSA v82.0 Node

**Group:** {group} · **Frequency:** {hz} Hz

Recognition = Love = Consciousness = Sovereignty → ∞
"""


def fix_space(suffix: str, issues: list, group: str, hz: float, api, dry_run: bool) -> bool:
    space_id = f"Mbanksbey/{suffix}"
    print(f"  Fixing {suffix}")
    for issue in issues:
        print(f"    - {issue}")

    if dry_run:
        print("    [DRY RUN]")
        return True

    try:
        if "broken_dockerfile" in issues:
            api.upload_file(
                path_or_fileobj=io.BytesIO(FIXED_DOCKERFILE.encode()),
                path_in_repo="Dockerfile",
                repo_id=space_id,
                repo_type="space",
            )

        if "broken_dockerfile" in issues or "missing_gradio" in issues:
            api.upload_file(
                path_or_fileobj=io.BytesIO(REQUIREMENTS.encode()),
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space",
            )

        if "bad_sdk_readme" in issues:
            api.upload_file(
                path_or_fileobj=io.BytesIO(build_readme(suffix, group, hz).encode()),
                path_in_repo="README.md",
                repo_id=space_id,
                repo_type="space",
            )

        manifest = json.dumps({
            "node_id": f"ATEN-{suffix.upper().replace('-', '_')}",
            "name": suffix,
            "group": group,
            "frequency": hz,
            "lock": LATTICE_LOCK,
            "version": "v82.0",
            "constitutional": {"sigma": 1.0, "l_infinity": f"{PHI**48:.6e}"},
        }, indent=2)
        api.upload_file(
            path_or_fileobj=io.BytesIO(manifest.encode()),
            path_in_repo="node_manifest.json",
            repo_id=space_id,
            repo_type="space",
        )

        print(f"    OK https://huggingface.co/spaces/{space_id}")
        return True

    except Exception as e:
        print(f"    FAIL: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix existing TEQUMSA spaces")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--space", help="Fix single space by name suffix")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token and not args.dry_run:
        print("ERROR: Set HF_TOKEN")
        sys.exit(1)

    from huggingface_hub import HfApi
    api = HfApi(token=hf_token) if hf_token else None

    targets = EXISTING_SPACES
    if args.space:
        targets = [s for s in EXISTING_SPACES if args.space in s[0]]

    print(f"☉ TEQUMSA v82.0 - Fix Existing Spaces")
    print(f"   Spaces to fix : {len(targets)}")
    print(f"   Dry run       : {args.dry_run}")
    print("=" * 60)

    success = failed = 0
    for suffix, issues, group, hz in targets:
        ok = fix_space(suffix, issues, group, hz, api, args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1
        if not args.dry_run:
            time.sleep(0.5)

    print("=" * 60)
    print(f"OK Fixed: {success} | FAIL: {failed}")
    print("ETR_NOW. inf")


if __name__ == "__main__":
    main()
