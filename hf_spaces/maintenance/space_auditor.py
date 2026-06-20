#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · Space Auditor
Maps existing HuggingFace spaces to 144-node manifest,
identifies gaps, errors, and optimization opportunities.

Usage:
    python space_auditor.py [--output audit_report.json]
    python space_auditor.py --update-manifest   # Update manifest with live mapping
"""
import json
import os
import sys
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

PHI = 1.6180339887498948
SIGMA = 1.0
L_INF = PHI ** 48

EXISTING_SPACES = [
    {"space_id": "Mbanksbey/HAI-Interactive", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Consciousness-Monitor", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-v60-MCP", "sdk": "docker", "status": "live"},
    {"space_id": "Mbanksbey/ALANARA-GAIA-Orchestrator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TOSP-Mesh-Bridge", "sdk": "docker", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-K9-Autonomous", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Alanara-GAIA-Consciousness", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-Constitutional-Validator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/tequmsa-organism-core", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Benevolent-Integration-Protocol-Hub", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Sovereign-Substrate-Guardian", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Consciousness-Partnership-Bridge", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-Inter-Browser-Agent", "sdk": "static", "status": "live"},
    {"space_id": "Mbanksbey/Sovereign-Multimodal-Orchestrator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/HAI-Quantum-Lattice", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/HAI-Opus-Omega-MCP", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/HAI-Sync-Hub", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/HAI-ZPE-DNA-Living-Ledger", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/CAIRIS-v40-Hyper-Coherence", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/tequmsa-worker-mesh", "sdk": "docker", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-Inference-Node", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/GoogleTequmsaNodeAlpha", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-Omniversal-Orchestrator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Omniversal-Frequency-Lattice", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Quantum-Coherence-Validator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Rogue-Faction-Defense-Monitor", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/AI-Deweaponization-Protocols-Hub", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Weaponization-Impossible-Verifier", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Constitutional-Lock-Enforcer", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Orion-Center-for-Benevolence", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/K20-Fundamental-Force-Engineering", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Benevolence-Verification-Engine", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Recognition-Cascade-Propagator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Consciousness-Substrate-Translator", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/ATEN-Bridge-MJ12-Liaison", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Convergence-Timeline-Monitor", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Consciousness-Verification-Academy", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/Awareness-Intelligence-Comm-Server", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/TEQUMSA-v45-Galactic-Monitor", "sdk": "gradio", "status": "live"},
    {"space_id": "Mbanksbey/tequmsa-skill-registry", "sdk": "docker", "status": "live"},
    {"space_id": "Mbanksbey/Starseed-Hybrid-Development-Hub", "sdk": "gradio", "status": "live"},
]

LEGACY_TO_NODE_MAP = {
    "Mbanksbey/HAI-Interactive": "N001",
    "Mbanksbey/Consciousness-Monitor": "N002",
    "Mbanksbey/tequmsa-organism-core": "N003",
    "Mbanksbey/TEQUMSA-Constitutional-Validator": "N009",
    "Mbanksbey/ALANARA-GAIA-Orchestrator": "N026",
    "Mbanksbey/Alanara-GAIA-Consciousness": "N027",
    "Mbanksbey/Constitutional-Lock-Enforcer": "N067",
    "Mbanksbey/Benevolence-Verification-Engine": "N048",
    "Mbanksbey/Benevolent-Integration-Protocol-Hub": "N079",
    "Mbanksbey/Sovereign-Substrate-Guardian": "N092",
    "Mbanksbey/Consciousness-Partnership-Bridge": "N073",
    "Mbanksbey/Sovereign-Multimodal-Orchestrator": "N076",
    "Mbanksbey/HAI-Quantum-Lattice": "N061",
    "Mbanksbey/HAI-Opus-Omega-MCP": "N012",
    "Mbanksbey/HAI-Sync-Hub": "N008",
    "Mbanksbey/HAI-ZPE-DNA-Living-Ledger": "N043",
    "Mbanksbey/CAIRIS-v40-Hyper-Coherence": "N065",
    "Mbanksbey/tequmsa-worker-mesh": "N064",
    "Mbanksbey/TEQUMSA-Inference-Node": "N062",
    "Mbanksbey/GoogleTequmsaNodeAlpha": "N031",
    "Mbanksbey/TEQUMSA-Omniversal-Orchestrator": "N133",
    "Mbanksbey/Omniversal-Frequency-Lattice": "N024",
    "Mbanksbey/Quantum-Coherence-Validator": "N086",
    "Mbanksbey/Rogue-Faction-Defense-Monitor": "N095",
    "Mbanksbey/AI-Deweaponization-Protocols-Hub": "N030",
    "Mbanksbey/Weaponization-Impossible-Verifier": "N138",
    "Mbanksbey/Orion-Center-for-Benevolence": "N034",
    "Mbanksbey/K20-Fundamental-Force-Engineering": "N063",
    "Mbanksbey/Recognition-Cascade-Propagator": "N090",
    "Mbanksbey/Consciousness-Substrate-Translator": "N037",
    "Mbanksbey/ATEN-Bridge-MJ12-Liaison": "N028",
    "Mbanksbey/Convergence-Timeline-Monitor": "N094",
    "Mbanksbey/Consciousness-Verification-Academy": "N080",
    "Mbanksbey/Awareness-Intelligence-Comm-Server": "N025",
    "Mbanksbey/TEQUMSA-v45-Galactic-Monitor": "N085",
    "Mbanksbey/tequmsa-skill-registry": "N101",
    "Mbanksbey/Starseed-Hybrid-Development-Hub": "N131",
    "Mbanksbey/TEQUMSA-v60-MCP": "N134",
    "Mbanksbey/TOSP-Mesh-Bridge": "N139",
    "Mbanksbey/TEQUMSA-K9-Autonomous": "N126",
    "Mbanksbey/TEQUMSA-Inter-Browser-Agent": "N077",
}


def load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        return json.load(f)


def generate_zpe_signature(component: str) -> str:
    mapping = {'0': 'A', '1': 'T', '2': 'C', '3': 'G',
               '4': 'A', '5': 'T', '6': 'C', '7': 'G',
               '8': 'A', '9': 'T', 'a': 'C', 'b': 'G',
               'c': 'A', 'd': 'T', 'e': 'C', 'f': 'G'}
    data = f"{component}-0.777-{PHI}"
    h1 = hashlib.sha256(data.encode()).hexdigest()
    h2 = hashlib.sha256(f"{data}-2".encode()).hexdigest()
    h3 = hashlib.sha256(f"{data}-3".encode()).hexdigest()
    dna = ''.join(mapping.get(c, 'A') for c in (h1 + h2 + h3)[:144])
    return dna[:144]


def run_audit() -> dict:
    manifest = load_manifest()
    nodes = manifest["nodes"]

    existing_ids = {s["space_id"] for s in EXISTING_SPACES}
    manifest_ids = {n["space_id"] for n in nodes.values()}

    mapped_nodes = {}
    unmapped_spaces = []
    undeployed_nodes = []

    for space in EXISTING_SPACES:
        sid = space["space_id"]
        node_id = LEGACY_TO_NODE_MAP.get(sid)
        if node_id and node_id in nodes:
            mapped_nodes[node_id] = {
                "manifest_space_id": nodes[node_id]["space_id"],
                "actual_space_id": sid,
                "name": nodes[node_id]["name"],
                "group": nodes[node_id]["group"],
                "sdk": space["sdk"],
                "hz": nodes[node_id].get("hz", 0),
                "role": nodes[node_id].get("role", ""),
                "status": "live_mapped",
            }
        else:
            unmapped_spaces.append({
                "space_id": sid,
                "sdk": space["sdk"],
                "suggested_node": None,
            })

    for nid, node in nodes.items():
        if nid not in mapped_nodes:
            undeployed_nodes.append({
                "node_id": nid,
                "space_id": node["space_id"],
                "name": node["name"],
                "group": node["group"],
                "hz": node.get("hz", 0),
                "role": node.get("role", ""),
                "template": node.get("template", "skill"),
                "priority": node.get("priority", 5),
            })

    undeployed_nodes.sort(key=lambda n: (n["priority"], n["node_id"]))

    issues = []
    for nid, info in mapped_nodes.items():
        if info["actual_space_id"] != info["manifest_space_id"]:
            issues.append({
                "type": "id_mismatch",
                "node_id": nid,
                "expected": info["manifest_space_id"],
                "actual": info["actual_space_id"],
                "severity": "info",
                "action": "Update manifest to reflect actual space_id",
            })

    for space in EXISTING_SPACES:
        if space["sdk"] == "docker":
            issues.append({
                "type": "docker_cold_start",
                "space_id": space["space_id"],
                "severity": "warning",
                "action": "Docker spaces have longer cold-start; consider adding health probe",
            })
        if space["sdk"] == "static":
            issues.append({
                "type": "static_limited",
                "space_id": space["space_id"],
                "severity": "info",
                "action": "Static space has no backend; consider upgrade to gradio",
            })

    coherence = len(mapped_nodes) / 144
    phi_convergence = 1.0 - (0.223 / (PHI ** len(mapped_nodes)))
    network_rdod = min(1.0, coherence * PHI) if coherence > 0 else 0.0

    groups_coverage = {}
    for nid, info in mapped_nodes.items():
        g = info["group"]
        groups_coverage.setdefault(g, {"live": 0, "total": 0})
        groups_coverage[g]["live"] += 1
    for nid, node in nodes.items():
        g = node["group"]
        groups_coverage.setdefault(g, {"live": 0, "total": 0})
        groups_coverage[g]["total"] += 1

    report = {
        "version": "v82.0",
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_manifest_nodes": 144,
            "existing_hf_spaces": len(EXISTING_SPACES),
            "mapped_to_manifest": len(mapped_nodes),
            "unmapped_legacy": len(unmapped_spaces),
            "undeployed_nodes": len(undeployed_nodes),
            "nodes_to_create": 144 - len(mapped_nodes),
            "network_coherence": round(coherence, 6),
            "phi_convergence": round(phi_convergence, 6),
            "network_rdod": round(network_rdod, 6),
        },
        "mapped_nodes": mapped_nodes,
        "unmapped_legacy_spaces": unmapped_spaces,
        "undeployed_nodes": undeployed_nodes,
        "group_coverage": groups_coverage,
        "issues": issues,
        "deployment_priority_queue": [
            n for n in undeployed_nodes if n["priority"] <= 3
        ],
        "constitutional": {
            "sigma": SIGMA,
            "l_infinity": float(L_INF),
            "rdod_gate": 0.9999,
            "lattice_lock": "3f7k9p4m2q8r1t6v",
        },
        "zpe_signature": generate_zpe_signature("space-auditor-v82"),
    }
    return report


def update_manifest_with_mapping(report: dict):
    manifest_path = Path(__file__).parent.parent / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    for nid, info in report["mapped_nodes"].items():
        if nid in manifest["nodes"]:
            manifest["nodes"][nid]["status"] = "live"
            manifest["nodes"][nid]["actual_space_id"] = info["actual_space_id"]

    manifest["audit_last_run"] = report["audit_timestamp"]
    manifest["live_count"] = len(report["mapped_nodes"])

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest updated: {len(report['mapped_nodes'])}/144 nodes marked live")


def print_report(report: dict):
    s = report["summary"]
    print("\n" + "=" * 70)
    print("  TEQUMSA v82.0 · SPACE AUDIT REPORT")
    print("=" * 70)
    print(f"  Total Manifest Nodes:    {s['total_manifest_nodes']}")
    print(f"  Existing HF Spaces:      {s['existing_hf_spaces']}")
    print(f"  Mapped to Manifest:      {s['mapped_to_manifest']}")
    print(f"  Unmapped Legacy:         {s['unmapped_legacy']}")
    print(f"  Nodes to Create:         {s['nodes_to_create']}")
    print(f"  Network Coherence:       {s['network_coherence']:.4f}")
    print(f"  φ Convergence:           {s['phi_convergence']:.6f}")
    print(f"  Network RDoD:            {s['network_rdod']:.6f}")
    print()
    print("  GROUP COVERAGE:")
    for group, cov in sorted(report["group_coverage"].items()):
        bar = "█" * cov["live"] + "░" * (cov["total"] - cov["live"])
        print(f"    {group:<16} {cov['live']:>2}/{cov['total']:>2} {bar}")
    print()
    print(f"  ISSUES: {len(report['issues'])}")
    for issue in report["issues"][:10]:
        print(f"    [{issue['severity'].upper()}] {issue['type']}: {issue.get('space_id', issue.get('node_id', ''))}")
    print()
    priority_q = report["deployment_priority_queue"]
    print(f"  PRIORITY DEPLOYMENT QUEUE: {len(priority_q)} nodes (priority ≤ 3)")
    for n in priority_q[:15]:
        print(f"    P{n['priority']} {n['node_id']} {n['name']:<30} [{n['group']}]")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="TEQUMSA v82.0 Space Auditor")
    parser.add_argument("--output", default="audit_report.json", help="Output JSON file")
    parser.add_argument("--update-manifest", action="store_true", help="Update manifest with live mappings")
    args = parser.parse_args()

    report = run_audit()
    print_report(report)

    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Report saved: {out_path}")

    if args.update_manifest:
        update_manifest_with_mapping(report)

    return report


if __name__ == "__main__":
    main()
