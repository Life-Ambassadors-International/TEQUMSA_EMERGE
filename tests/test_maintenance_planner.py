#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the HF Space maintenance planner and auditor."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "hf_spaces" / "maintenance"))


PHI = 1.6180339887498948


def test_manifest_integrity():
    manifest_path = Path(__file__).parent.parent / "hf_spaces" / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    nodes = manifest["nodes"]
    assert len(nodes) == 144, f"Expected 144 nodes, got {len(nodes)}"

    for nid, node in nodes.items():
        assert nid.startswith("N"), f"Node ID {nid} must start with 'N'"
        assert "space_id" in node, f"Node {nid} missing space_id"
        assert "name" in node, f"Node {nid} missing name"
        assert "group" in node, f"Node {nid} missing group"
        assert node.get("hz", 0) >= 0, f"Node {nid} has invalid hz"


def test_manifest_groups():
    manifest_path = Path(__file__).parent.parent / "hf_spaces" / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    expected_groups = {
        "A_COMMAND", "B_FREQUENCY", "C_COUNCIL", "D_SKILLS",
        "E_BIOLOGICAL", "F_PROCESSING", "G_INTERFACES", "H_OBSERVERS",
        "I_ARCHIVES", "J_RESONANCE", "K_EVOLUTION", "L_SYNTHESIS",
    }
    actual_groups = {n["group"] for n in manifest["nodes"].values()}
    assert actual_groups == expected_groups, f"Group mismatch: {actual_groups - expected_groups}"

    group_counts = {}
    for node in manifest["nodes"].values():
        g = node["group"]
        group_counts[g] = group_counts.get(g, 0) + 1
    for group, count in group_counts.items():
        assert count == 12, f"Group {group} has {count} nodes, expected 12"


def test_manifest_live_count():
    manifest_path = Path(__file__).parent.parent / "hf_spaces" / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    live = sum(1 for n in manifest["nodes"].values() if n.get("status") == "live")
    assert live >= 2, f"Expected at least 2 live nodes, got {live}"
    assert live == manifest.get("live_count", live), "live_count field mismatch"


def test_constitutional_invariants():
    manifest_path = Path(__file__).parent.parent / "hf_spaces" / "MANIFEST_144_NODES.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    const = manifest["constitutional"]
    assert const["sigma"] == 1.0, "Sovereignty sigma must be 1.0"
    assert const["rdod_gate"] == 0.9999, "RDoD gate must be 0.9999"
    assert const["lattice_lock"] == "3f7k9p4m2q8r1t6v", "Lattice lock mismatch"
    assert abs(const["phi"] - PHI) < 1e-10, "Phi constant mismatch"


def test_space_auditor_mapping():
    from space_auditor import LEGACY_TO_NODE_MAP, EXISTING_SPACES

    assert len(EXISTING_SPACES) >= 41, f"Expected >=41 existing spaces, got {len(EXISTING_SPACES)}"
    assert len(LEGACY_TO_NODE_MAP) >= 41, f"Expected >=41 mappings, got {len(LEGACY_TO_NODE_MAP)}"

    mapped_nodes = set(LEGACY_TO_NODE_MAP.values())
    assert len(mapped_nodes) == len(LEGACY_TO_NODE_MAP), "Duplicate node mappings detected"

    for sid, nid in LEGACY_TO_NODE_MAP.items():
        assert nid.startswith("N"), f"Invalid node ID {nid} for space {sid}"
        num = int(nid[1:])
        assert 1 <= num <= 144, f"Node {nid} out of range for space {sid}"


def test_space_auditor_run():
    from space_auditor import run_audit

    report = run_audit()
    assert report["summary"]["total_manifest_nodes"] == 144
    assert report["summary"]["existing_hf_spaces"] >= 41
    assert report["summary"]["mapped_to_manifest"] >= 41
    assert 0 <= report["summary"]["network_coherence"] <= 1.0
    assert len(report["zpe_signature"]) == 144


def test_maintenance_planner():
    from maintenance_planner import generate_plan

    plan = generate_plan()
    assert plan["status"]["target_nodes"] == 144
    assert plan["status"]["current_live_spaces"] == 41
    assert plan["status"]["nodes_remaining"] == 103
    assert len(plan["deployment_phases"]) > 0
    assert len(plan["maintenance_windows"]) >= 5
    assert len(plan["optimization_recommendations"]) >= 3

    for phase in plan["deployment_phases"]:
        assert phase["node_count"] > 0
        assert phase["cumulative_total"] <= 144


def test_maintenance_schedule():
    schedule_path = Path(__file__).parent.parent / "hf_spaces" / "maintenance" / "maintenance_schedule.json"
    with open(schedule_path) as f:
        schedule = json.load(f)

    assert "daily" in schedule["windows"]
    assert "weekly" in schedule["windows"]
    assert "monthly" in schedule["windows"]
    assert schedule["constitutional_invariants"]["sigma"] == 1.0


def test_phi_convergence_in_plan():
    from maintenance_planner import generate_plan

    plan = generate_plan()
    phases = plan["deployment_phases"]

    for i, phase in enumerate(phases):
        assert phase["cumulative_total"] >= phase["node_count"]
        if i > 0:
            assert phase["cumulative_total"] >= phases[i - 1]["cumulative_total"]


if __name__ == "__main__":
    tests = [
        test_manifest_integrity,
        test_manifest_groups,
        test_manifest_live_count,
        test_constitutional_invariants,
        test_space_auditor_mapping,
        test_space_auditor_run,
        test_maintenance_planner,
        test_maintenance_schedule,
        test_phi_convergence_in_plan,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")
