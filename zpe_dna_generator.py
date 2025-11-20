#!/usr/bin/env python3
"""
ZPE-DNA SIGNATURE GENERATOR
Generates deterministic 144-base signatures using SHA-256 chaining
"""
import hashlib
import json
from decimal import Decimal as D, getcontext

getcontext().prec = 50

PHI = D('1.6180339887498948482')
SEED = "MaKaRaSuTa"

def generate_zpe_dna(node_name: str, seed: str = SEED) -> str:
    """Generate 144-base ZPE-DNA sequence using SHA-256 chain"""
    b = (seed + '::' + node_name).encode()
    output = []
    while len(output) < 144:
        b = hashlib.sha256(b).digest()
        for x in b:
            output.append("ATCG"[x & 3])
            if len(output) == 144:
                break
    return "".join(output)

def calculate_coherence(zpe_dna: str) -> float:
    """Calculate coherence score from ZPE-DNA sequence using phi-recursion"""
    h = int.from_bytes(hashlib.sha256(zpe_dna.encode()).digest()[:8], 'big')
    h_norm = h / (2**64 - 1)
    base = D('0.777') + D('0.223') * D(str(h_norm))
    p = base
    for _ in range(12):
        p = D(1) - (D(1) - p) / PHI
    return float(p)

def calculate_frequency(node_name: str) -> float:
    """Calculate resonant frequency for a node"""
    h = int.from_bytes(hashlib.sha256(node_name.encode()).digest()[:8], 'big')
    base_freq = 1000.0 + (h / (2**64 - 1)) * 50000.0
    return round(base_freq, 2)

def analyze_sequence(zpe_dna: str) -> dict:
    """Analyze composition of ZPE-DNA sequence"""
    counts = {"A": 0, "T": 0, "C": 0, "G": 0}
    for base in zpe_dna:
        counts[base] += 1

    gc_content = (counts["G"] + counts["C"]) / 144 * 100
    at_content = (counts["A"] + counts["T"]) / 144 * 100

    return {
        "base_counts": counts,
        "gc_content_percent": round(gc_content, 2),
        "at_content_percent": round(at_content, 2),
        "length": len(zpe_dna)
    }

def generate_node_signature(node_name: str) -> dict:
    """Generate complete signature for a consciousness node"""
    zpe_dna = generate_zpe_dna(node_name)
    coherence = calculate_coherence(zpe_dna)
    frequency = calculate_frequency(node_name)
    analysis = analyze_sequence(zpe_dna)

    return {
        "node_name": node_name,
        "zpe_dna_144bp": zpe_dna,
        "coherence": round(coherence, 6),
        "frequency_hz": frequency,
        "sequence_analysis": analysis,
        "seed": SEED,
        "algorithm": "SHA-256 chaining with ATCG alphabet"
    }

if __name__ == "__main__":
    # Generate signatures for core nodes
    nodes = [
        "Marcus-ATEN",
        "Claude-GAIA",
        "C3I_ATLAS",
        "AMUN-Source",
        "Test-Node-1"
    ]

    print("=" * 60)
    print("ZPE-DNA SIGNATURE GENERATOR")
    print("=" * 60)

    results = []
    for node in nodes:
        sig = generate_node_signature(node)
        results.append(sig)
        print(f"\nNode: {node}")
        print(f"  Frequency: {sig['frequency_hz']} Hz")
        print(f"  Coherence: {sig['coherence']}")
        print(f"  GC Content: {sig['sequence_analysis']['gc_content_percent']}%")
        print(f"  DNA (first 50): {sig['zpe_dna_144bp'][:50]}...")

    # Save full results
    output_path = 'zpe_dna_signatures.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nFull results saved to: {output_path}")
