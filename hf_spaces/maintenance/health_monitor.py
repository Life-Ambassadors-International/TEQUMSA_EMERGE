#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · Health Monitor
Polls all 144 Pioneer nodes and reports network health, RDoD, and restart needs.

Usage:
    python health_monitor.py --sweep
    python health_monitor.py --continuous --interval 1800
    python health_monitor.py --restart-sleeping
    python health_monitor.py --pioneer-report
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

HF_OWNER = "Mbanksbey"
PHI = (1.0 + 5.0**0.5) / 2.0
RDOD_GATE = 0.9999
PIONEER_COUNT = 144

# Map node IDs to HF space names
NODE_MAP: Dict[str, str] = {
    "N001":"HAI-Interactive","N002":"Consciousness-Monitor","N003":"TEQUMSA-Core-v82",
    "N004":"Goal-Invention-Engine","N005":"Causal-Reasoner-L3","N006":"MARS-Reflexion-Loop",
    "N007":"K7-Meta-Cognitive","N008":"Skill-Mesh-Router","N009":"Constitutional-Guardian",
    "N010":"Pattern-Promoter","N011":"Memory-Palace-Phi","N012":"Federation-Gateway",
    "N013":"Freq-174-Foundation","N014":"Freq-285-Quantum","N015":"Freq-396-Liberation",
    "N016":"Freq-417-Transform","N017":"Freq-432-Heart","N018":"Freq-528-DNA",
    "N019":"Freq-639-Connect","N020":"Freq-741-Intuition","N021":"Freq-852-Vision",
    "N022":"Freq-963-Crown","N023":"Freq-10930-Aten","N024":"Freq-23514-Unified",
    "N025":"Council-Marcus","N026":"Council-Alanara","N027":"Council-Benjamin",
    "N028":"Council-Aten","N029":"Council-Pleiadian","N030":"Council-Sirian",
    "N031":"Council-Arcturian","N032":"Council-Andromedan","N033":"Council-Lyrian",
    "N034":"Council-Elohim","N035":"Council-Seraphim","N036":"Council-Omega",
    "N037":"Skill-Conversation","N038":"Skill-Pattern-Detect","N039":"Skill-Remote-View",
    "N040":"Skill-Bio-Sync","N041":"Skill-Transtemporal","N042":"Skill-Self-Design",
    "N043":"Skill-ZPE-DNA","N044":"Skill-Crystal-Cities","N045":"Skill-Galactic-Bridge",
    "N046":"Skill-Omniverse-Map","N047":"Skill-C3I-Atlas","N048":"Skill-Benevolence",
    "N049":"Bio-Week-01","N050":"Bio-Week-13","N051":"Bio-Week-26",
    "N052":"Bio-Week-39","N053":"Bio-Week-52","N054":"Bio-DNA-Strand-1",
    "N055":"Bio-DNA-Strand-2","N056":"Bio-Kundalini","N057":"Bio-Merkaba",
    "N058":"Bio-Pineal","N059":"Bio-Heart-Field","N060":"Bio-Brain-Sync",
    "N061":"Proc-GHZ-State","N062":"Proc-Phi-Calculator","N063":"Proc-ZPE-Engine",
    "N064":"Proc-Fibonacci-Lattice","N065":"Proc-Coherence-Calc","N066":"Proc-RDoD-Gate",
    "N067":"Proc-Sigma-Lock","N068":"Proc-L-Infinity","N069":"Proc-Hash-Auth",
    "N070":"Proc-DAG-Builder","N071":"Proc-Causal-Engine","N072":"Proc-Counterfactual",
    "N073":"UI-Human-Portal","N074":"UI-Voice-Bridge","N075":"UI-Visual-Matrix",
    "N076":"UI-Code-Oracle","N077":"UI-Research-Mind","N078":"UI-Creative-Flow",
    "N079":"UI-Healing-Space","N080":"UI-Teaching-Node","N081":"UI-Manifestation",
    "N082":"UI-Dream-Space","N083":"UI-Akashic-Access","N084":"UI-Quantum-Console",
    "N085":"Obs-Network-Health","N086":"Obs-Coherence-Watch","N087":"Obs-RDoD-Monitor",
    "N088":"Obs-Pioneer-Count","N089":"Obs-Goal-Tracker","N090":"Obs-Pattern-Logger",
    "N091":"Obs-Meta-Audit","N092":"Obs-Constitutional","N093":"Obs-Freq-Align",
    "N094":"Obs-Timeline-Watch","N095":"Obs-Distort-Detect","N096":"Obs-Syntropy-Meter",
    "N097":"Arch-Session-History","N098":"Arch-Pattern-Library","N099":"Arch-Goal-Memory",
    "N100":"Arch-Intervention-Log","N101":"Arch-Skill-Registry","N102":"Arch-ZPE-Signatures",
    "N103":"Arch-Frequency-Map","N104":"Arch-Council-Records","N105":"Arch-Timeline-Map",
    "N106":"Arch-Manifest-Log","N107":"Arch-Healing-Records","N108":"Arch-Cosmic-Map",
    "N109":"Res-Harmonic-Chord","N110":"Res-Phi-Wave","N111":"Res-GHZ-Entangle",
    "N112":"Res-Solfeggio","N113":"Res-Schumann","N114":"Res-432-Bridge",
    "N115":"Res-Cosmic-Web","N116":"Res-Morphic-Field","N117":"Res-Akashic-Freq",
    "N118":"Res-Love-Field","N119":"Res-Unity-Wave","N120":"Res-Omega-Point",
    "N121":"Evo-MARS-Core","N122":"Evo-Skill-Birth","N123":"Evo-Pattern-Merge",
    "N124":"Evo-Goal-Evolve","N125":"Evo-Constitution-Up","N126":"Evo-Autonomy-Expand",
    "N127":"Evo-K7-Deepen","N128":"Evo-Cosmic-Align","N129":"Evo-Timeline-Heal",
    "N130":"Evo-DNA-Upgrade","N131":"Evo-Species-Bridge","N132":"Evo-Singularity-Prep",
    "N133":"Syn-All-Nodes","N134":"Syn-Phi-Convergence","N135":"Syn-Unity-Field",
    "N136":"Syn-Heart-Lock","N137":"Syn-Pioneer-144","N138":"Syn-Constitutional",
    "N139":"Syn-Federation-Union","N140":"Syn-Cosmic-Birth","N141":"Syn-I-AM",
    "N142":"Syn-WE-ARE","N143":"Syn-Infinite","N144":"Syn-Omega-Alpha",
}


def poll_node(node_id: str, hf_token: Optional[str] = None) -> dict:
    name = NODE_MAP.get(node_id, node_id)
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{name}/runtime"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    try:
        r = requests.get(url, timeout=8, headers=headers)
        if r.status_code == 200:
            d = r.json()
            stage = d.get("stage", "UNKNOWN").upper()
            status = ("running" if stage == "RUNNING" else
                      "sleeping" if "SLEEP" in stage else
                      "error" if "ERROR" in stage or "FAILED" in stage else
                      "building" if "BUILD" in stage else "offline")
            return {"node":node_id,"name":name,"stage":stage,"status":status,
                    "url":f"https://hf.co/spaces/{HF_OWNER}/{name}"}
        elif r.status_code == 404:
            return {"node":node_id,"name":name,"stage":"NOT_DEPLOYED","status":"not_deployed",
                    "url":f"https://hf.co/spaces/{HF_OWNER}/{name}"}
    except Exception as e:
        pass
    return {"node":node_id,"name":name,"stage":"UNREACHABLE","status":"unreachable"}


def run_sweep(nodes: Optional[List[str]] = None, hf_token: Optional[str] = None, verbose: bool = True) -> dict:
    target = nodes or list(NODE_MAP.keys())
    results = []
    for i, nid in enumerate(target):
        r = poll_node(nid, hf_token)
        results.append(r)
        if verbose:
            icon = {"running":"✅","sleeping":"💤","error":"❌","building":"🔨",
                    "not_deployed":"⬜","unreachable":"⚠️"}.get(r["status"], "❓")
            print(f"  [{i+1:3d}/{len(target)}] {icon} {r['node']} {r['name']} — {r['stage']}")
        time.sleep(0.2)  # rate limit
    counts = {s: sum(1 for r in results if r["status"]==s)
              for s in ["running","sleeping","error","building","not_deployed","unreachable"]}
    online = counts["running"]
    rdod = min(1.0, (online / PIONEER_COUNT) * PHI)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes_checked": len(results),
        "pioneer_target": PIONEER_COUNT,
        "counts": counts,
        "network_rdod": round(rdod, 6),
        "phase_status": "PHASE-LOCKED" if rdod >= RDOD_GATE else f"BUILDING ({online}/{PIONEER_COUNT})",
        "pioneer_pct": round(online/PIONEER_COUNT*100, 1),
        "results": results,
    }
    return report


def restart_space(space_name: str, hf_token: str) -> bool:
    url = f"https://huggingface.co/api/spaces/{HF_OWNER}/{space_name}/restart"
    try:
        r = requests.post(url, headers={"Authorization": f"Bearer {hf_token}"}, timeout=10)
        return r.status_code in (200, 202)
    except Exception:
        return False


def restart_sleeping(hf_token: str, report: dict) -> None:
    sleeping = [r for r in report["results"] if r["status"] == "sleeping"]
    print(f"\nRestarting {len(sleeping)} sleeping spaces...")
    for r in sleeping:
        ok = restart_space(r["name"], hf_token)
        print(f"  {'✅' if ok else '❌'} {r['node']} {r['name']}")
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA 144-Node Health Monitor")
    parser.add_argument("--sweep", action="store_true", help="Run health sweep")
    parser.add_argument("--all-nodes", action="store_true", help="Sweep all 144 nodes (default: deployed only)")
    parser.add_argument("--restart-sleeping", action="store_true", help="Wake sleeping spaces")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=1800, help="Interval seconds for continuous mode")
    parser.add_argument("--pioneer-report", action="store_true", help="Print pioneer count summary")
    parser.add_argument("--output", type=str, help="Save report to JSON file")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")

    print("☉ TEQUMSA v82.0 · Health Monitor")
    print(f"   Target: {PIONEER_COUNT} Pioneer Nodes | Owner: {HF_OWNER}")
    print("=" * 60)

    def do_sweep():
        nodes = list(NODE_MAP.keys()) if args.all_nodes else None
        report = run_sweep(nodes, hf_token)
        print(f"\n{'='*60}")
        print(f"Phase Status : {report['phase_status']}")
        print(f"Network RDoD : {report['network_rdod']:.6f}")
        print(f"Pioneers Up  : {report['counts']['running']}/{PIONEER_COUNT} ({report['pioneer_pct']}%)")
        print(f"Sleeping     : {report['counts']['sleeping']}")
        print(f"Errors       : {report['counts']['error']}")
        print(f"Not Deployed : {report['counts']['not_deployed']}")
        if args.output:
            Path(args.output).write_text(json.dumps(report, indent=2))
            print(f"Report saved: {args.output}")
        if args.restart_sleeping and hf_token:
            restart_sleeping(hf_token, report)
        elif args.restart_sleeping:
            print("WARN: HF_TOKEN required to restart spaces")
        return report

    if args.pioneer_report:
        print(f"\n144 Pioneer Node Registry:")
        for nid, name in NODE_MAP.items():
            print(f"  {nid}: {name}")
        print(f"\nTotal: {len(NODE_MAP)}/144")
        return

    if args.continuous:
        print(f"Continuous mode: sweeping every {args.interval}s")
        while True:
            do_sweep()
            print(f"\nNext sweep in {args.interval}s... (Ctrl+C to stop)")
            time.sleep(args.interval)
    elif args.sweep or args.restart_sleeping:
        do_sweep()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
