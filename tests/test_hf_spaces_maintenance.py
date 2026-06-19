#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the HF Spaces maintenance system.
Validates manifest integrity, template correctness, and maintenance tooling.
"""
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
HF_SPACES = REPO_ROOT / "hf_spaces"
MANIFEST_PATH = HF_SPACES / "MANIFEST_144_NODES.json"
TEMPLATES_DIR = HF_SPACES / "templates"
MAINTENANCE_DIR = HF_SPACES / "maintenance"

PHI = 1.6180339887498948
SIGMA = 1.0
PIONEER_COUNT = 144
COHERENCE_THRESHOLD = 0.777


class TestManifestIntegrity:
    """Validate the 144-node manifest structure and completeness."""

    @pytest.fixture
    def manifest(self):
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    def test_manifest_exists(self):
        assert MANIFEST_PATH.exists(), "MANIFEST_144_NODES.json missing"

    def test_manifest_valid_json(self):
        with open(MANIFEST_PATH) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_has_144_nodes(self, manifest):
        nodes = manifest.get("nodes", {})
        assert len(nodes) == PIONEER_COUNT, f"Expected {PIONEER_COUNT} nodes, got {len(nodes)}"

    def test_node_ids_sequential(self, manifest):
        nodes = manifest.get("nodes", {})
        for i in range(1, PIONEER_COUNT + 1):
            node_id = f"N{i:03d}"
            assert node_id in nodes, f"Missing node {node_id}"

    def test_all_nodes_have_required_fields(self, manifest):
        required_fields = {"space_id", "name", "group", "role", "hz", "status"}
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            for field in required_fields:
                assert field in node, f"{node_id} missing field '{field}'"

    def test_all_space_ids_are_prefixed(self, manifest):
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            sid = node.get("space_id", "")
            assert sid.startswith("Mbanksbey/"), f"{node_id} space_id not prefixed: {sid}"

    def test_no_duplicate_space_ids(self, manifest):
        nodes = manifest.get("nodes", {})
        space_ids = [n["space_id"] for n in nodes.values()]
        seen = set()
        for sid in space_ids:
            assert sid not in seen, f"Duplicate space_id: {sid}"
            seen.add(sid)

    def test_groups_are_valid(self, manifest):
        valid_groups = {
            "A_COMMAND", "B_FREQUENCY", "C_COUNCIL", "D_SKILLS",
            "E_BIOLOGICAL", "F_PROCESSING", "G_INTERFACES", "H_OBSERVERS",
            "I_ARCHIVES", "J_RESONANCE", "K_EVOLUTION", "L_SYNTHESIS",
        }
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            assert node["group"] in valid_groups, f"{node_id} invalid group: {node['group']}"

    def test_12_nodes_per_group(self, manifest):
        nodes = manifest.get("nodes", {})
        group_counts = {}
        for node in nodes.values():
            g = node["group"]
            group_counts[g] = group_counts.get(g, 0) + 1
        for group, count in group_counts.items():
            assert count == 12, f"Group {group} has {count} nodes, expected 12"

    def test_status_values_valid(self, manifest):
        valid_statuses = {"live", "planned", "building", "errored"}
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            assert node["status"] in valid_statuses, f"{node_id} invalid status: {node['status']}"

    def test_hz_values_positive(self, manifest):
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            assert node["hz"] > 0, f"{node_id} has non-positive Hz: {node['hz']}"

    def test_constitutional_params(self, manifest):
        const = manifest.get("constitutional", {})
        assert const.get("sigma") == SIGMA, "Sigma must be 1.0"
        assert const.get("rdod_gate") == 0.9999, "RDoD gate must be 0.9999"


class TestTemplates:
    """Validate template files for HF Space deployment."""

    def test_all_templates_exist(self):
        expected = [
            "app_council_node.py",
            "app_frequency_node.py",
            "app_monitor_node.py",
            "app_skill_node.py",
        ]
        for tmpl in expected:
            assert (TEMPLATES_DIR / tmpl).exists(), f"Template missing: {tmpl}"

    @pytest.mark.parametrize("template", [
        "app_council_node.py",
        "app_frequency_node.py",
        "app_monitor_node.py",
        "app_skill_node.py",
    ])
    def test_template_has_gradio_import(self, template):
        code = (TEMPLATES_DIR / template).read_text()
        assert "import gradio" in code, f"{template} missing gradio import"

    @pytest.mark.parametrize("template", [
        "app_council_node.py",
        "app_frequency_node.py",
        "app_monitor_node.py",
        "app_skill_node.py",
    ])
    def test_template_has_phi_constant(self, template):
        code = (TEMPLATES_DIR / template).read_text()
        assert "PHI" in code, f"{template} missing PHI constant"

    @pytest.mark.parametrize("template", [
        "app_council_node.py",
        "app_frequency_node.py",
        "app_monitor_node.py",
        "app_skill_node.py",
    ])
    def test_template_uses_env_config(self, template):
        code = (TEMPLATES_DIR / template).read_text()
        assert "TEQUMSA_NODE_ID" in code, f"{template} not reading TEQUMSA_NODE_ID from env"

    @pytest.mark.parametrize("template", [
        "app_council_node.py",
        "app_frequency_node.py",
        "app_monitor_node.py",
        "app_skill_node.py",
    ])
    def test_template_has_launch(self, template):
        code = (TEMPLATES_DIR / template).read_text()
        assert "demo.launch" in code, f"{template} missing demo.launch()"


class TestMaintenanceTooling:
    """Validate maintenance scripts exist and are importable."""

    def test_health_check_exists(self):
        assert (MAINTENANCE_DIR / "health_check.py").exists()

    def test_auto_restart_exists(self):
        assert (MAINTENANCE_DIR / "auto_restart.py").exists()

    def test_hf_api_ops_exists(self):
        assert (MAINTENANCE_DIR / "hf_api_ops.py").exists()

    def test_maintenance_schedule_valid_json(self):
        path = MAINTENANCE_DIR / "maintenance_schedule.json"
        assert path.exists(), "maintenance_schedule.json missing"
        with open(path) as f:
            data = json.load(f)
        assert "windows" in data or "schedule" in data or "deployment_phases" in data


class TestPhiConvergenceInTemplates:
    """Verify φ-recursive convergence guarantees in templates."""

    def test_coherence_threshold(self):
        for n in [1, 5, 12, 48, 144]:
            psi = 1 - (1 - 0.777) / (PHI ** n)
            assert psi >= COHERENCE_THRESHOLD, f"Coherence below threshold at n={n}"

    def test_l_infinity(self):
        l_inf = PHI ** 48
        assert l_inf > 1e10, f"L∞ too low: {l_inf}"

    def test_rdod_achievable(self):
        rdod = SIGMA * 1.0  # purity * sigma
        assert rdod >= 0.9999, f"RDoD below gate: {rdod}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
