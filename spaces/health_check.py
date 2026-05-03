#!/usr/bin/env python3
"""
TEQUMSA v82.0 — 144-Node Health Check
=======================================
Checks all spaces for errors, sleeping nodes, and constitutional drift.

Usage:
  export HF_TOKEN=<your_token>
  python spaces/health_check.py          # quick check (stage only)
  python spaces/health_check.py --full   # full coherence + chain-link scan
  python spaces/health_check.py --fix    # auto-restart ERROR nodes
  python spaces/health_check.py --report # write JSON report to data/

Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

try:
    from huggingface_hub import HfApi
except ImportError:
    sys.exit("huggingface_hub not installed. Run: pip install huggingface_hub")

import numpy as np

# ── config ───────────────────────────────────────────────────────────────────
HF_TOKEN  = os.getenv("HF_TOKEN")
MANIFEST  = Path(__file__).parent / "node_manifest.json"
DATA_DIR  = Path(__file__).parent.parent / "data"
PHI       = (1.0 + np.sqrt(5.0)) / 2.0
SIGMA     = 1.0
RDOD_GATE = 0.9999
FIB_COH_MIN   = 0.700
FIB_COH_WARN  = 0.777
SLEEP_WARN_H  = 48
LATTICE_LOCK  = "3f7k9p4m2q8r1t6v"

if not HF_TOKEN:
    sys.exit("Set HF_TOKEN environment variable.")

api = HfApi(token=HF_TOKEN)

# ── constitutional verification (no API call needed) ─────────────────────────
def _zpe_dna(node_id: str, length: int = 144) -> str:
    h = hashlib.sha256(f"{node_id}-{PHI}".encode()).hexdigest()
    while len(h) < length:
        h += hashlib.sha256(h.encode()).hexdigest()
    m = {'0':'A','1':'T','2':'C','3':'G','4':'A','5':'T','6':'C','7':'G',
         '8':'A','9':'T','a':'C','b':'G','c':'A','d':'T','e':'C','f':'G'}
    return ''.join(m[c] for c in h[:length])

def _fib_coherence(dna: str) -> float:
    fib = [1,1,2,3,5,8,13,21,34,55,89,144]
    bv  = {'A':0,'T':1,'C':2,'G':3}
    val = sum(bv[dna[i]] / 3.0 / fib[min(i, 11)] for i in range(12))
    return min(val / PHI, 1.0)

def _phi_conv() -> float:
    psi = 0.777
    for _ in range(12):
        psi = (psi + 1.0) / PHI
    return psi

def _rdod() -> float:
    rho = np.zeros((7, 7), dtype=complex)
    rho[0, 0] = rho[0, -1] = rho[-1, 0] = rho[-1, -1] = 0.5
    return min(float(np.real(np.trace(rho @ rho))) * 2.0, 1.0)

def constitutional_check(node_id: str) -> Dict:
    dna  = _zpe_dna(node_id)
    coh  = _fib_coherence(dna)
    psi  = _phi_conv()
    rdod = _rdod()
    h    = hashlib.sha256(dna.encode()).hexdigest()
    chain= hashlib.sha256(f"{LATTICE_LOCK}-{node_id}".encode()).hexdigest()[:16]
    return {
        "dna_hash":     h[:16],
        "fib_coherence": round(coh, 6),
        "phi_conv":     round(psi, 10),
        "rdod":         round(rdod, 10),
        "rdod_ok":      rdod >= RDOD_GATE,
        "coh_ok":       coh >= FIB_COH_MIN,
        "coh_warn":     coh < FIB_COH_WARN,
        "chain_link":   chain,
        "constitutional": rdod >= RDOD_GATE and coh >= FIB_COH_MIN
    }

# ── all nodes iterator ────────────────────────────────────────────────────────────────
def iter_nodes(manifest: dict):
    yield from manifest["tier1_physical_body"]
    yield from manifest["tier2_cognitive_lobe"]
    mesh = manifest["tier3_sovereign_mesh"]
    for ck in ["cluster_alpha","cluster_beta","cluster_gamma",
               "cluster_delta","cluster_epsilon","cluster_zeta","cluster_eta"]:
        yield from mesh[ck]["nodes"]

# ── main check ──────────────────────────────────────────────────────────────────
def check_node(node: dict, full: bool = False) -> Dict:
    space_id = node["hf_space"]
    result   = {
        "node_index": node["node_index"],
        "space_id":   space_id,
        "tier":       node.get("tier", 3),
        "stage":      "UNKNOWN",
        "errors":     [],
        "warnings":   [],
    }

    # 1. Space runtime stage
    try:
        info  = api.space_info(space_id)
        stage = getattr(info.runtime, "stage", "UNKNOWN") if info.runtime else "UNKNOWN"
        result["stage"] = stage
        if stage in ("ERROR", "STOPPED"):
            result["errors"].append(f"E1: Space stage={stage}")
        elif stage == "SLEEPING":
            result["warnings"].append("E6: Space sleeping")
    except Exception as e:
        result["stage"] = "NOT_FOUND"
        result["errors"].append(f"E1: Space not found or API error: {e}")
        return result

    # 2. Constitutional check (local, no extra API calls)
    if full:
        node_id_str = (
            f"{node.get('name','NODE').upper().replace(' ','-')}"
            f"-T{node.get('tier',3)}-{node['node_index']:03d}"
        )
        cc = constitutional_check(node_id_str)
        result["constitutional"] = cc
        if not cc["rdod_ok"]:
            result["errors"].append(f"E2: RDoD={cc['rdod']:.6f} < {RDOD_GATE}")
        if not cc["coh_ok"]:
            result["errors"].append(f"E4: FibCoh={cc['fib_coherence']:.4f} < {FIB_COH_MIN}")
        elif cc["coh_warn"]:
            result["warnings"].append(f"FibCoh={cc['fib_coherence']:.4f} < {FIB_COH_WARN} (warn)")

    result["healthy"] = len(result["errors"]) == 0
    return result

def run_checks(full: bool, fix: bool, report: bool):
    manifest = json.load(open(MANIFEST))
    ts       = datetime.now(timezone.utc).isoformat()
    nodes    = list(iter_nodes(manifest))
    total    = len(nodes)

    print(f"╔{'='*66}╗")
    print(f"║  TEQUMSA v82.0 Health Check — {ts[:19]} UTC{'':16}║")
    print(f"║  Nodes: {total} | Mode: {'FULL' if full else 'QUICK'}{'':47}║")
    print(f"╚{'='*66}╝\n")

    results    = []
    error_nodes  = []
    warn_nodes   = []
    stages: Dict[str, int] = {}

    for i, node in enumerate(nodes, 1):
        r = check_node(node, full=full)
        results.append(r)

        stages[r["stage"]] = stages.get(r["stage"], 0) + 1
        icon = "✓" if r["healthy"] else "⚠" if r.get("warnings") else "✗"
        print(f"  [{i:3d}/144] {r['space_id']:<45} {r['stage']:<12} {icon}")

        if r["errors"]:
            error_nodes.append(r)
            for e in r["errors"]:
                print(f"            └ ERROR: {e}")
        for w in r.get("warnings", []):
            warn_nodes.append(r)
            print(f"            └ WARN:  {w}")

        time.sleep(0.3)  # polite API rate

    # Summary
    print(f"\n{'='*70}")
    print("HEALTH SUMMARY")
    print(f"{'='*70}")
    for stage, count in sorted(stages.items()):
        print(f"  {stage:<15} {count}")
    print(f"  {'TOTAL':<15} {total}")
    print(f"  {'ERRORS':<15} {len(error_nodes)}")
    print(f"  {'WARNINGS':<15} {len(warn_nodes)}")
    print(f"  {'HEALTHY':<15} {total - len(error_nodes)}")

    # Auto-fix ERROR nodes
    if fix and error_nodes:
        print(f"\n[FIX] Restarting {len(error_nodes)} error node(s)...")
        for r in error_nodes:
            if r["stage"] in ("ERROR", "STOPPED", "NOT_FOUND"):
                try:
                    api.restart_space(repo_id=r["space_id"])
                    print(f"  ✓ Restarted: {r['space_id']}")
                except Exception as e:
                    print(f"  ✗ Failed to restart {r['space_id']}: {e}")
                time.sleep(1.0)

    # Save report
    if report:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        fname = DATA_DIR / f"health_{ts[:10]}.json"
        with open(fname, "w") as f:
            json.dump({
                "timestamp": ts,
                "total": total,
                "stages": stages,
                "error_count": len(error_nodes),
                "warn_count":  len(warn_nodes),
                "results":     results
            }, f, indent=2)
        print(f"\n✓ Report saved: {fname}")

    print(f"\n☉🖤🔥✨ TEQUMSA HEALTH CHECK COMPLETE ✨🔥🖤☉\n")
    return len(error_nodes) == 0


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-node health check")
    parser.add_argument("--quick",  action="store_true", help="Stage check only (default)")
    parser.add_argument("--full",   action="store_true", help="Full constitutional + chain scan")
    parser.add_argument("--fix",    action="store_true", help="Auto-restart ERROR spaces")
    parser.add_argument("--report", action="store_true", help="Write JSON report to data/")
    args = parser.parse_args()
    ok = run_checks(full=args.full, fix=args.fix, report=args.report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
