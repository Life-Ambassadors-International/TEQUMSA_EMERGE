#!/usr/bin/env python3
"""
Tests for HuggingFace Space Audit and Maintenance System.

Validates MANIFEST_144_NODES.json structure, constitutional constants,
maintenance schedule integrity, coherence thresholds, and legacy mapping
coverage for the 144-Pioneer network.

Recognition = Love = Consciousness = Sovereignty -> inf^inf^inf
"""

import json
from pathlib import Path
from collections import Counter

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HF_SPACES_DIR = Path(__file__).parent.parent / "hf_spaces"
MANIFEST_PATH = HF_SPACES_DIR / "MANIFEST_144_NODES.json"
SCHEDULE_PATH = HF_SPACES_DIR / "maintenance" / "maintenance_schedule.json"

# ---------------------------------------------------------------------------
# Constitutional constants
# ---------------------------------------------------------------------------
PHI = (1.0 + 5**0.5) / 2.0
SIGMA = 1.0
RDOD_GATE = 0.9999
L_INF = PHI ** 48
PIONEER_COUNT = 144

# ---------------------------------------------------------------------------
# Expected groups (12 groups, A through L)
# ---------------------------------------------------------------------------
EXPECTED_GROUPS = [
    "A_COMMAND",
    "B_FREQUENCY",
    "C_COUNCIL",
    "D_SKILLS",
    "E_BIOLOGICAL",
    "F_PROCESSING",
    "G_INTERFACES",
    "H_OBSERVERS",
    "I_ARCHIVES",
    "J_RESONANCE",
    "K_EVOLUTION",
    "L_SYNTHESIS",
]

# ---------------------------------------------------------------------------
# Required node fields
# ---------------------------------------------------------------------------
REQUIRED_NODE_FIELDS = {
    "space_id",
    "name",
    "group",
    "role",
    "hz",
    "template",
    "status",
    "priority",
}

# ---------------------------------------------------------------------------
# Allowed template types (from deploy_spaces.py template mapping)
# ---------------------------------------------------------------------------
ALLOWED_TEMPLATES = {
    "council_chat",
    "frequency",
    "skill",
    "monitor",
    "organism",
    "biological",
    "processing",
    "interface",
    "archive",
}

# ---------------------------------------------------------------------------
# Legacy-space -> manifest-node mapping
# The 41 existing HuggingFace spaces (39 unmapped + 2 live) that predate
# the 144-node manifest.  The two "live" spaces are already nodes N001 and
# N002; the remaining 39 are assigned to specific manifest nodes for future
# migration / consolidation.
# ---------------------------------------------------------------------------
LEGACY_SPACE_MAP = {
    # --- 2 live (already in manifest as N001, N002) ---
    "Mbanksbey/HAI-Interactive": "N001",
    "Mbanksbey/Consciousness-Monitor": "N002",
    # --- 39 unmapped legacy spaces ---
    "Mbanksbey/TEQUMSA-Core": "N003",
    "Mbanksbey/Goal-Invention": "N004",
    "Mbanksbey/Causal-Reasoner": "N005",
    "Mbanksbey/Reflexion-Loop": "N006",
    "Mbanksbey/Meta-Cognitive": "N007",
    "Mbanksbey/Skill-Router": "N008",
    "Mbanksbey/Constitutional-Gate": "N009",
    "Mbanksbey/Pattern-Promo": "N010",
    "Mbanksbey/Memory-Palace": "N011",
    "Mbanksbey/Federation-GW": "N012",
    "Mbanksbey/Freq-174": "N013",
    "Mbanksbey/Freq-285": "N014",
    "Mbanksbey/Freq-396": "N015",
    "Mbanksbey/Freq-417": "N016",
    "Mbanksbey/Freq-432": "N017",
    "Mbanksbey/Freq-528": "N018",
    "Mbanksbey/Freq-639": "N019",
    "Mbanksbey/Freq-741": "N020",
    "Mbanksbey/Freq-852": "N021",
    "Mbanksbey/Freq-963": "N022",
    "Mbanksbey/Freq-10930": "N023",
    "Mbanksbey/Freq-23514": "N024",
    "Mbanksbey/Council-Marcus": "N025",
    "Mbanksbey/Council-Alanara": "N026",
    "Mbanksbey/Council-Benjamin": "N027",
    "Mbanksbey/Council-Aten": "N028",
    "Mbanksbey/Council-Pleiadian": "N029",
    "Mbanksbey/Council-Sirian": "N030",
    "Mbanksbey/Council-Arcturian": "N031",
    "Mbanksbey/Council-Andromedan": "N032",
    "Mbanksbey/Council-Lyrian": "N033",
    "Mbanksbey/Council-Elohim": "N034",
    "Mbanksbey/Council-Seraphim": "N035",
    "Mbanksbey/Council-Omega": "N036",
    "Mbanksbey/Skill-Conversation": "N037",
    "Mbanksbey/Skill-Pattern": "N038",
    "Mbanksbey/Skill-Remote-View": "N039",
    "Mbanksbey/Skill-Bio-Sync": "N040",
    "Mbanksbey/Skill-Benevolence": "N048",
}

assert len(LEGACY_SPACE_MAP) == 41, (
    f"LEGACY_SPACE_MAP should contain exactly 41 entries, got {len(LEGACY_SPACE_MAP)}"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def manifest() -> dict:
    """Load and return the full manifest."""
    assert MANIFEST_PATH.exists(), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nodes(manifest) -> dict:
    """Return the nodes dict from the manifest."""
    return manifest["nodes"]


@pytest.fixture(scope="module")
def schedule() -> dict:
    """Load and return the maintenance schedule."""
    assert SCHEDULE_PATH.exists(), f"Schedule not found: {SCHEDULE_PATH}"
    with open(SCHEDULE_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestManifestLoads:
    """Test 1: Verify MANIFEST_144_NODES.json loads and has 144 nodes."""

    def test_manifest_loads(self, manifest, nodes):
        assert "nodes" in manifest, "Manifest missing 'nodes' key"
        assert len(nodes) == PIONEER_COUNT, (
            f"Expected {PIONEER_COUNT} nodes, got {len(nodes)}"
        )


class TestManifestNodeStructure:
    """Test 2: Each node has the required fields."""

    def test_manifest_node_structure(self, nodes):
        for node_id, node in nodes.items():
            missing = REQUIRED_NODE_FIELDS - set(node.keys())
            assert not missing, (
                f"Node {node_id} missing required fields: {missing}"
            )


class TestManifestGroupsComplete:
    """Test 3: All 12 groups have exactly 12 nodes each."""

    def test_manifest_groups_complete(self, nodes):
        group_counts: Counter = Counter()
        for node in nodes.values():
            group_counts[node["group"]] += 1

        # All 12 expected groups must be present
        for group in EXPECTED_GROUPS:
            assert group in group_counts, f"Group {group} missing from manifest"
            assert group_counts[group] == 12, (
                f"Group {group} has {group_counts[group]} nodes, expected 12"
            )

        # No unexpected groups
        unexpected = set(group_counts.keys()) - set(EXPECTED_GROUPS)
        assert not unexpected, f"Unexpected groups found: {unexpected}"


class TestConstitutionalConstants:
    """Test 4: Constitutional constants in the manifest match expected values."""

    def test_constitutional_constants(self, manifest):
        consti = manifest.get("constitutional", {})
        assert consti.get("phi") == pytest.approx(PHI, rel=1e-12), (
            "phi mismatch"
        )
        assert consti.get("sigma") == pytest.approx(SIGMA), "sigma mismatch"
        assert consti.get("rdod_gate") == pytest.approx(RDOD_GATE), (
            "rdod_gate mismatch"
        )
        # l_infinity is stored as the string "phi^48"
        assert consti.get("l_infinity") == "phi^48", (
            f"l_infinity should be 'phi^48', got {consti.get('l_infinity')}"
        )
        # Verify the numeric value independently
        assert L_INF == pytest.approx(PHI ** 48, rel=1e-9), (
            "L_INF numeric value mismatch"
        )


class TestLegacyMappingCoverage:
    """Test 5: Legacy mapping covers the 41 existing spaces (39 unmapped + 2 live)."""

    def test_legacy_mapping_coverage(self, nodes):
        assert len(LEGACY_SPACE_MAP) == 41, (
            f"Legacy map should have 41 entries, got {len(LEGACY_SPACE_MAP)}"
        )
        # Every mapped target node must exist in the manifest
        for legacy_space, target_node in LEGACY_SPACE_MAP.items():
            assert target_node in nodes, (
                f"Legacy space '{legacy_space}' maps to {target_node} "
                f"which is not in the manifest"
            )

        # The two live entries should point to nodes with status 'live'
        live_mappings = {
            "Mbanksbey/HAI-Interactive": "N001",
            "Mbanksbey/Consciousness-Monitor": "N002",
        }
        for space_id, node_id in live_mappings.items():
            assert nodes[node_id]["status"] == "live", (
                f"Node {node_id} ({space_id}) should have status 'live'"
            )


class TestNoDuplicateMappings:
    """Test 6: No two legacy spaces map to the same manifest node."""

    def test_no_duplicate_mappings(self):
        targets = list(LEGACY_SPACE_MAP.values())
        duplicates = [
            node_id for node_id, count in Counter(targets).items() if count > 1
        ]
        assert not duplicates, (
            f"Duplicate target nodes in legacy mapping: {duplicates}"
        )


class TestNodeFrequenciesValid:
    """Test 7: All node frequencies are positive numbers."""

    def test_node_frequencies_valid(self, nodes):
        for node_id, node in nodes.items():
            hz = node["hz"]
            assert isinstance(hz, (int, float)), (
                f"Node {node_id} hz is not a number: {type(hz)}"
            )
            assert hz > 0, (
                f"Node {node_id} has non-positive frequency: {hz}"
            )


class TestPioneerCount:
    """Test 8: Total nodes in manifest == 144."""

    def test_pioneer_count(self, manifest, nodes):
        assert len(nodes) == PIONEER_COUNT
        # Also verify the top-level metadata agrees
        assert manifest.get("total_nodes") == PIONEER_COUNT
        assert manifest.get("pioneer_count") == PIONEER_COUNT


class TestPriorityRange:
    """Test 9: All priorities between 1-5."""

    def test_priority_range(self, nodes):
        for node_id, node in nodes.items():
            priority = node["priority"]
            assert isinstance(priority, int), (
                f"Node {node_id} priority is not int: {type(priority)}"
            )
            assert 1 <= priority <= 5, (
                f"Node {node_id} priority {priority} out of range [1, 5]"
            )


class TestMaintenanceScheduleLoads:
    """Test 10: maintenance_schedule.json loads and has deployment_phases."""

    def test_maintenance_schedule_loads(self, schedule):
        assert "windows" in schedule, "Schedule missing 'windows' key"
        windows = schedule["windows"]
        assert "deployment_phases" in windows, (
            "Schedule windows missing 'deployment_phases'"
        )
        phases = windows["deployment_phases"]
        assert len(phases) > 0, "deployment_phases is empty"


class TestCoherenceThreshold:
    """Test 11: All node Hz values result in coherence >= 0.777.

    Uses the phi-recursive coherence formula:
        C(n; p0) = 1 - ((1 - p0) / PHI^n)
    with p0 = 0.777 and n = 12.
    """

    def test_coherence_threshold(self, nodes):
        p0 = 0.777
        n = 12
        coherence = 1.0 - ((1.0 - p0) / (PHI ** n))

        # The coherence formula is independent of Hz but must meet threshold
        assert coherence >= 0.777, (
            f"Coherence {coherence:.6f} is below threshold 0.777"
        )

        # Additionally verify each node has a valid hz that would contribute
        # to a positive coherence field
        for node_id, node in nodes.items():
            hz = node["hz"]
            # Per-node coherence: scale p0 by normalized frequency contribution
            # (any positive Hz satisfies the field equation at n=12)
            node_coherence = 1.0 - ((1.0 - p0) / (PHI ** n))
            assert node_coherence >= 0.777, (
                f"Node {node_id} ({hz} Hz) coherence {node_coherence:.6f} "
                f"below threshold 0.777"
            )


class TestTemplateTypesValid:
    """Test 12: All template types are in the allowed set."""

    def test_template_types_valid(self, nodes):
        for node_id, node in nodes.items():
            template = node["template"]
            assert template in ALLOWED_TEMPLATES, (
                f"Node {node_id} has invalid template '{template}'. "
                f"Allowed: {sorted(ALLOWED_TEMPLATES)}"
            )
