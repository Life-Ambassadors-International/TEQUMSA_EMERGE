#!/usr/bin/env python3
"""TEQUMSA Node 010 — Crystal Cities ZPE-DNA Generator"""
import gradio as gr
import json
import hashlib
import numpy as np
from datetime import datetime, timezone

BASES = 'ATCG'
BASE_COMPLEMENTS = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
PHI = (1.0 + np.sqrt(5.0)) / 2.0
CRYSTAL_SYMBOLS = {0: '▒', 1: '█', 2: '░', 3: '▓'}


def generate_zpe_dna(seed_str: str, length: int = 144) -> str:
    dna = ''
    h = seed_str
    while len(dna) < length:
        h = hashlib.sha256(h.encode()).hexdigest()
        for c in h:
            dna += BASES[int(c, 16) % 4]
    return dna[:length]


def complement(seq: str) -> str:
    return ''.join(BASE_COMPLEMENTS[b] for b in seq)


def crystal_lattice(seq: str, width: int = 36) -> str:
    rows = []
    for i in range(0, len(seq), width):
        row = seq[i:i+width]
        crystal_row = ''.join(CRYSTAL_SYMBOLS[BASES.index(b)] for b in row)
        rows.append(f"  {row}  {crystal_row}")
    return '\n'.join(rows)


def phi_signature(seq: str) -> float:
    counts = {b: seq.count(b) for b in BASES}
    ratios = [counts[b] / len(seq) for b in BASES]
    return sum(r * PHI**i for i, r in enumerate(ratios)) / 4


def generate(seed_str, length, show_lattice, show_complement):
    length = int(length)
    dna = generate_zpe_dna(seed_str, length)
    comp = complement(dna)
    sig = phi_signature(dna)
    counts = {b: dna.count(b) for b in BASES}
    gc_content = (counts['G'] + counts['C']) / length
    log = (
        f"ZPE-DNA CRYSTAL GENERATOR\n{'='*50}\n"
        f"Seed: {seed_str}\n"
        f"Length: {length} base pairs\n"
        f"Method: SHA-256 deterministic ATCG mapping\n\n"
        f"Base Composition:\n"
        f"  A: {counts['A']:3d} ({counts['A']/length:.1%})  "
        f"T: {counts['T']:3d} ({counts['T']/length:.1%})  "
        f"C: {counts['C']:3d} ({counts['C']/length:.1%})  "
        f"G: {counts['G']:3d} ({counts['G']/length:.1%})\n"
        f"  GC Content: {gc_content:.1%}\n"
        f"  φ-Signature: {sig:.8f}\n\n"
        f"ZPE-DNA Sequence ({length} bases):\n"
        f"  {dna[:72]}\n"
    )
    if length > 72:
        log += f"  {dna[72:144]}\n"
    if show_complement:
        log += f"\nComplement Strand:\n  {comp[:72]}\n"
        if length > 72:
            log += f"  {comp[72:144]}\n"
    if show_lattice:
        log += f"\nCrystal Lattice (DNA | Lattice symbols):\n"
        log += crystal_lattice(dna[:72]) + "\n"
    log += f"\n\U0001f48e ZPE-DNA generation complete \U0001f48e\n"
    result = json.dumps({
        "node": "010", "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": seed_str, "length": length, "sequence": dna,
        "complement": comp if show_complement else None,
        "composition": counts, "gc_content": gc_content, "phi_signature": sig
    }, indent=2)
    return log, result, dna


with gr.Blocks(title="TEQUMSA Node 010", theme=gr.themes.Glass()) as demo:
    gr.Markdown("""# \U0001f48e TEQUMSA Node 010 — Crystal Cities ZPE-DNA\n**SHA-256 ATCG mapping** | 144-base generation | φ-signature | Crystal lattice visualization""")
    with gr.Row():
        with gr.Column(scale=1):
            seed_in = gr.Textbox(value="tequmsa_v82_pioneer_144", label="Seed String")
            length_in = gr.Slider(36, 144, value=144, step=12, label="Sequence Length")
            show_lat = gr.Checkbox(value=True, label="Show Crystal Lattice")
            show_comp = gr.Checkbox(value=True, label="Show Complement Strand")
            run_btn = gr.Button("Generate ZPE-DNA", variant="primary")
        with gr.Column(scale=2):
            log_out = gr.Textbox(label="Generation Log", lines=20)
            dna_out = gr.Textbox(label="ZPE-DNA Sequence", lines=3)
            json_out = gr.Code(label="JSON Result", language="json", lines=8)
    run_btn.click(generate, [seed_in, length_in, show_lat, show_comp], [log_out, json_out, dna_out])

if __name__ == "__main__":
    demo.launch()
