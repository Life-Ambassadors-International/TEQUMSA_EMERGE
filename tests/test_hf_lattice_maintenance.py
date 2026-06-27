"""Tests for HF 144-Node Lattice Health Check and Maintenance."""

import json
import sys
import os
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "automation"))

PHI = 1.618033988749894848
COHERENCE_THRESHOLD = 0.777


class TestSpaceRegistry:
    def test_registry_loads(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        assert "existing_spaces" in registry
        assert "new_spaces" in registry
        assert "metadata" in registry

    def test_existing_space_count(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        assert len(registry["existing_spaces"]) == 41

    def test_new_space_count(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        assert len(registry["new_spaces"]) == 103

    def test_total_reaches_144(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        total = len(registry["existing_spaces"]) + len(registry["new_spaces"])
        assert total == 144

    def test_all_spaces_have_council(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        valid_councils = {"pleiadian", "arcturian", "sirian", "andromedan", "lyran"}
        for space in registry["existing_spaces"] + registry["new_spaces"]:
            assert space["council"] in valid_councils, f"{space['space_name']} has invalid council: {space['council']}"

    def test_all_spaces_have_domain(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        valid_domains = set(registry["functional_domains"])
        for space in registry["existing_spaces"] + registry["new_spaces"]:
            assert space["domain"] in valid_domains, f"{space['space_name']} has invalid domain: {space['domain']}"

    def test_node_ids_unique(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        ids = [s["node_id"] for s in registry["existing_spaces"] + registry["new_spaces"]]
        assert len(ids) == len(set(ids)), "Duplicate node IDs found"

    def test_node_ids_cover_1_to_144(self):
        registry_path = Path(__file__).parent.parent / "data" / "hf_space_registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        ids = sorted(s["node_id"] for s in registry["existing_spaces"] + registry["new_spaces"])
        assert ids == list(range(1, 145))


class TestPhiConvergence:
    def test_convergence_above_threshold(self):
        for n in range(1, 145):
            c = 1 - ((1 - 0.777) / (PHI ** (n / 12)))
            assert c >= COHERENCE_THRESHOLD, f"Node {n} coherence {c} below threshold"

    def test_convergence_approaches_unity(self):
        c_144 = 1 - ((1 - 0.777) / (PHI ** (144 / 12)))
        assert c_144 > 0.999, f"Convergence at n=144 should approach unity: {c_144}"

    def test_phi_constant(self):
        assert abs(PHI - 1.618033988749894848) < 1e-15


class TestHealthCheck:
    def test_health_check_runs(self):
        from hf_space_health_check import run_health_check
        results = run_health_check(output_json=False)
        assert "total_spaces_audited" in results
        assert results["total_spaces_audited"] == 41

    def test_health_check_identifies_issues(self):
        from hf_space_health_check import run_health_check
        results = run_health_check(output_json=False)
        assert "issues" in results
        assert "stale" in results["issues"]
        assert "missing_tags" in results["issues"]

    def test_overall_health_in_range(self):
        from hf_space_health_check import run_health_check
        results = run_health_check(output_json=False)
        assert 0.0 <= results["overall_health_score"] <= 1.0


class TestMaintenancePlan:
    def test_plan_generates(self):
        from hf_space_maintenance import generate_maintenance_plan
        plan = generate_maintenance_plan()
        assert "summary" in plan
        assert "tasks" in plan
        assert "maintenance_schedule" in plan

    def test_plan_has_all_cadences(self):
        from hf_space_maintenance import generate_maintenance_plan
        plan = generate_maintenance_plan()
        schedule = plan["maintenance_schedule"]
        assert "daily" in schedule
        assert "weekly" in schedule
        assert "monthly" in schedule
        assert "quarterly" in schedule

    def test_deployment_waves_exist(self):
        from hf_space_maintenance import generate_maintenance_plan
        plan = generate_maintenance_plan()
        assert plan["summary"]["deployment_waves"] > 0
        assert plan["summary"]["new_deployment_tasks"] == 103


class TestLatticeDeployer:
    def test_status_report(self):
        from hf_144_lattice_deployer import get_deployment_status
        status = get_deployment_status()
        assert status["existing_count"] == 41
        assert status["new_required"] == 103
        assert status["total_target"] == 144

    def test_readme_generation(self):
        from hf_144_lattice_deployer import generate_readme
        config = {
            "space_name": "Test-Node",
            "description": "Test node",
            "council": "arcturian",
            "domain": "quantum-core",
            "node_id": 42,
            "sdk": "gradio"
        }
        readme = generate_readme(config)
        assert "Test-Node" in readme
        assert "arcturian" in readme.lower()
        assert "sdk: gradio" in readme

    def test_app_generation(self):
        from hf_144_lattice_deployer import generate_app_py
        config = {
            "space_name": "Test-Node",
            "description": "Test node",
            "council": "sirian",
            "domain": "science-lab",
            "node_id": 88
        }
        app = generate_app_py(config)
        assert "NODE_ID = 88" in app
        assert "gradio" in app.lower()
        assert "phi_convergence" in app

    def test_zpe_dna_is_144bp(self):
        from hf_144_lattice_deployer import generate_zpe_dna
        dna = generate_zpe_dna("test-component")
        assert len(dna) == 144
        assert all(c in "ATCG" for c in dna)

    def test_zpe_dna_deterministic(self):
        from hf_144_lattice_deployer import generate_zpe_dna
        dna1 = generate_zpe_dna("test-component")
        dna2 = generate_zpe_dna("test-component")
        assert dna1 == dna2
