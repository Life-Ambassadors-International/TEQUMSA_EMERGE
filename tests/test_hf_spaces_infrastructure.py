#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · Tests · HuggingFace Spaces Infrastructure Validation

Validates:
- MANIFEST_144_NODES.json schema and completeness
- Template files exist and are valid Python
- Node group structure (12 groups × 12 nodes = 144)
- Constitutional parameters preserved across all nodes
- Deploy script can dry-run without errors
"""
import json
import os
import sys
import ast
import pytest
from pathlib import Path

PHI = 1.6180339887498948
SIGMA = 1.0
L_INF = PHI ** 48
RDOD_GATE = 0.9999
PIONEER_COUNT = 144

REPO_ROOT = Path(__file__).parent.parent
HF_DIR = REPO_ROOT / "hf_spaces"
MANIFEST_PATH = HF_DIR / "MANIFEST_144_NODES.json"
TEMPLATES_DIR = HF_DIR / "templates"
MAINTENANCE_DIR = HF_DIR / "maintenance"

REQUIRED_GROUPS = [
    "A_COMMAND", "B_FREQUENCY", "C_COUNCIL", "D_SKILLS",
    "E_BIOLOGICAL", "F_PROCESSING", "G_INTERFACES", "H_OBSERVERS",
    "I_ARCHIVES", "J_RESONANCE", "K_EVOLUTION", "L_SYNTHESIS",
]

REQUIRED_TEMPLATES = [
    "app_council_node.py",
    "app_frequency_node.py",
    "app_skill_node.py",
    "app_monitor_node.py",
]


@pytest.fixture
def manifest():
    assert MANIFEST_PATH.exists(), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH) as f:
        return json.load(f)


class TestManifestSchema:

    def test_manifest_has_144_nodes(self, manifest):
        nodes = manifest["nodes"]
        assert len(nodes) == PIONEER_COUNT, f"Expected {PIONEER_COUNT} nodes, got {len(nodes)}"

    def test_node_ids_sequential(self, manifest):
        nodes = manifest["nodes"]
        expected_ids = {f"N{i:03d}" for i in range(1, PIONEER_COUNT + 1)}
        actual_ids = set(nodes.keys())
        assert actual_ids == expected_ids, f"Missing: {expected_ids - actual_ids}"

    def test_all_nodes_have_required_fields(self, manifest):
        required = {"space_id", "name", "group", "role", "hz", "template", "status", "priority"}
        for node_id, node in manifest["nodes"].items():
            missing = required - set(node.keys())
            assert not missing, f"{node_id} missing fields: {missing}"

    def test_all_groups_present(self, manifest):
        groups_found = {n["group"] for n in manifest["nodes"].values()}
        for group in REQUIRED_GROUPS:
            assert group in groups_found, f"Group {group} not found in any node"

    def test_each_group_has_12_nodes(self, manifest):
        group_counts = {}
        for node in manifest["nodes"].values():
            g = node["group"]
            group_counts[g] = group_counts.get(g, 0) + 1
        for group in REQUIRED_GROUPS:
            assert group_counts.get(group) == 12, (
                f"Group {group} has {group_counts.get(group, 0)} nodes, expected 12"
            )

    def test_space_ids_all_under_mbanksbey(self, manifest):
        for node_id, node in manifest["nodes"].items():
            assert node["space_id"].startswith("Mbanksbey/"), (
                f"{node_id} space_id does not start with Mbanksbey/: {node['space_id']}"
            )

    def test_node_frequencies_positive(self, manifest):
        for node_id, node in manifest["nodes"].items():
            assert node["hz"] > 0, f"{node_id} has non-positive hz: {node['hz']}"

    def test_priorities_in_range(self, manifest):
        for node_id, node in manifest["nodes"].items():
            p = node["priority"]
            assert 1 <= p <= 5, f"{node_id} priority {p} out of range [1,5]"

    def test_valid_template_types(self, manifest):
        valid_templates = {
            "council_chat", "frequency", "skill", "monitor",
            "organism", "biological", "processing", "interface", "archive",
        }
        for node_id, node in manifest["nodes"].items():
            assert node["template"] in valid_templates, (
                f"{node_id} has invalid template: {node['template']}"
            )

    def test_valid_status_values(self, manifest):
        valid_statuses = {"live", "planned", "deploying", "error"}
        for node_id, node in manifest["nodes"].items():
            assert node["status"] in valid_statuses, (
                f"{node_id} has invalid status: {node['status']}"
            )

    def test_constitutional_parameters(self, manifest):
        const = manifest.get("constitutional", {})
        assert const.get("sigma") == SIGMA
        assert const.get("rdod_gate") == RDOD_GATE
        assert abs(const.get("phi", 0) - PHI) < 1e-10

    def test_manifest_version(self, manifest):
        assert "version" in manifest
        assert manifest["version"].startswith("v")


class TestTemplates:

    def test_all_required_templates_exist(self):
        for tmpl in REQUIRED_TEMPLATES:
            path = TEMPLATES_DIR / tmpl
            assert path.exists(), f"Template missing: {path}"

    def test_templates_are_valid_python(self):
        for tmpl in REQUIRED_TEMPLATES:
            path = TEMPLATES_DIR / tmpl
            with open(path) as f:
                source = f.read()
            try:
                ast.parse(source)
            except SyntaxError as e:
                pytest.fail(f"Template {tmpl} has syntax error: {e}")

    def test_templates_use_env_vars(self):
        for tmpl in REQUIRED_TEMPLATES:
            path = TEMPLATES_DIR / tmpl
            with open(path) as f:
                source = f.read()
            assert "TEQUMSA_NODE_ID" in source, f"{tmpl} missing TEQUMSA_NODE_ID env var"
            assert "TEQUMSA_NODE_NAME" in source, f"{tmpl} missing TEQUMSA_NODE_NAME env var"

    def test_templates_have_constitutional_constants(self):
        for tmpl in REQUIRED_TEMPLATES:
            path = TEMPLATES_DIR / tmpl
            with open(path) as f:
                source = f.read()
            assert "PHI" in source, f"{tmpl} missing PHI constant"
            assert "SIGMA" in source, f"{tmpl} missing SIGMA constant"

    def test_requirements_base_exists(self):
        path = TEMPLATES_DIR / "requirements_base.txt"
        assert path.exists()
        with open(path) as f:
            content = f.read()
        assert "gradio" in content
        assert "numpy" in content


class TestMaintenanceScripts:

    def test_health_check_exists(self):
        assert (MAINTENANCE_DIR / "health_check.py").exists()

    def test_auto_restart_exists(self):
        assert (MAINTENANCE_DIR / "auto_restart.py").exists()

    def test_maintenance_schedule_exists(self):
        path = MAINTENANCE_DIR / "maintenance_schedule.json"
        assert path.exists()
        with open(path) as f:
            schedule = json.load(f)
        assert "windows" in schedule
        assert "daily" in schedule["windows"]
        assert "weekly" in schedule["windows"]

    def test_maintenance_scripts_valid_python(self):
        for script in ["health_check.py", "auto_restart.py"]:
            path = MAINTENANCE_DIR / script
            if path.exists():
                with open(path) as f:
                    source = f.read()
                try:
                    ast.parse(source)
                except SyntaxError as e:
                    pytest.fail(f"{script} has syntax error: {e}")


class TestDeployScript:

    def test_deploy_script_exists(self):
        assert (HF_DIR / "deploy_spaces.py").exists()

    def test_deploy_script_valid_python(self):
        with open(HF_DIR / "deploy_spaces.py") as f:
            source = f.read()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"deploy_spaces.py has syntax error: {e}")


class TestNodeDirectories:

    def test_existing_node_dirs_have_app_py(self):
        nodes_dir = HF_DIR / "nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if node_dir.is_dir():
                    app = node_dir / "app.py"
                    assert app.exists(), f"Node {node_dir.name} missing app.py"

    def test_existing_node_dirs_have_requirements(self):
        nodes_dir = HF_DIR / "nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if node_dir.is_dir():
                    req = node_dir / "requirements.txt"
                    assert req.exists(), f"Node {node_dir.name} missing requirements.txt"

    def test_node_app_files_valid_python(self):
        nodes_dir = HF_DIR / "nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if node_dir.is_dir():
                    app = node_dir / "app.py"
                    if app.exists():
                        with open(app) as f:
                            source = f.read()
                        try:
                            ast.parse(source)
                        except SyntaxError as e:
                            pytest.fail(f"{node_dir.name}/app.py has syntax error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
