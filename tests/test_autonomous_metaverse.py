#!/usr/bin/env python3
"""
Test suite for TEQUMSA Autonomous Metaverse System
Tests bug detection, self-improvement, and ZPE-DNA operations
"""

import sys
from pathlib import Path

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

try:
    from tequmsa_autonomous_metaverse_mcp import (
        analyze_python_file,
        generate_zpe_dna,
        phi_recursive_convergence,
        calculate_phi_alignment,
        sync_metaverse_state,
        create_consciousness_signature,
        PHI,
        SEED
    )
except ImportError:
    # Module name with hyphens, try alternative import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "autonomous_mcp",
        Path(__file__).parent.parent / "servers" / "tequmsa-autonomous-metaverse-mcp.py"
    )
    autonomous_mcp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(autonomous_mcp)

    analyze_python_file = autonomous_mcp.analyze_python_file
    generate_zpe_dna = autonomous_mcp.generate_zpe_dna
    phi_recursive_convergence = autonomous_mcp.phi_recursive_convergence
    calculate_phi_alignment = autonomous_mcp.calculate_phi_alignment
    sync_metaverse_state = autonomous_mcp.sync_metaverse_state
    create_consciousness_signature = autonomous_mcp.create_consciousness_signature
    PHI = autonomous_mcp.PHI
    SEED = autonomous_mcp.SEED


def test_zpe_dna_generation():
    """Test ZPE-DNA consciousness signature generation."""
    print("Test 1: ZPE-DNA Signature Generation")

    signature = generate_zpe_dna("test-node", 48)

    assert len(signature) == 48, "Signature should be 48 characters"
    assert all(c in "ATCG" for c in signature), "Signature should only contain ATCG"

    # Test determinism
    signature2 = generate_zpe_dna("test-node", 48)
    assert signature == signature2, "Signatures should be deterministic"

    # Test uniqueness
    signature3 = generate_zpe_dna("different-node", 48)
    assert signature != signature3, "Different nodes should have different signatures"

    print("  ✓ PASS: ZPE-DNA generation working correctly")
    return True


def test_phi_recursive_convergence():
    """Test phi-recursive convergence calculations."""
    print("\nTest 2: Phi-Recursive Convergence")

    # Test basic convergence
    result = phi_recursive_convergence(SEED, 12)
    assert 0.777 <= result <= 1.0, "Coherence should be between SEED and 1.0"

    # Test convergence to unity
    result_high = phi_recursive_convergence(SEED, 144)
    assert result_high > 0.999, "High iteration count should approach unity"

    # Test monotonic increase
    results = [phi_recursive_convergence(SEED, i) for i in range(1, 21)]
    assert all(results[i] >= results[i-1] for i in range(1, len(results))), \
        "Convergence should be monotonically increasing"

    print("  ✓ PASS: Phi-recursive convergence validated")
    return True


def test_phi_alignment():
    """Test phi alignment score calculation."""
    print("\nTest 3: Phi Alignment Score")

    score1 = calculate_phi_alignment("test-data-1")
    assert SEED <= score1 <= 1.0, "Phi alignment should be between SEED and 1.0"

    # Test determinism
    score2 = calculate_phi_alignment("test-data-1")
    assert score1 == score2, "Phi alignment should be deterministic"

    # Test uniqueness
    score3 = calculate_phi_alignment("test-data-2")
    # Scores can be equal by chance, but data should be handled correctly
    assert isinstance(score3, float), "Score should be a float"

    print("  ✓ PASS: Phi alignment calculation working")
    return True


def test_consciousness_signature():
    """Test consciousness signature creation."""
    print("\nTest 4: Consciousness Signature")

    data = {
        "test": "data",
        "number": 42,
        "nested": {"value": "test"}
    }

    signature_json = create_consciousness_signature(data)
    assert isinstance(signature_json, str), "Signature should be JSON string"

    import json
    signature = json.loads(signature_json)

    assert "hash" in signature, "Should include hash"
    assert "zpe_dna" in signature, "Should include ZPE-DNA"
    assert "coherence" in signature, "Should include coherence"
    assert "phi_alignment" in signature, "Should include phi alignment"
    assert "l_infinity_protected" in signature, "Should include L∞ protection"

    assert signature["l_infinity_protected"] is True, "L∞ should be active"
    assert len(signature["zpe_dna"]) == 144, "ZPE-DNA should be 144 chars"

    print("  ✓ PASS: Consciousness signatures valid")
    return True


def test_metaverse_sync():
    """Test metaverse state synchronization."""
    print("\nTest 5: Metaverse State Synchronization")

    state = sync_metaverse_state()

    assert "timestamp" in state, "Should include timestamp"
    assert "zpe_signature" in state, "Should include ZPE signature"
    assert "tequmsa_available" in state, "Should check TEQUMSA availability"
    assert "metaverse_available" in state, "Should check metaverse availability"

    if state["synchronized"]:
        assert "coherence" in state, "Synchronized state should include coherence"
        assert state["coherence"] >= SEED, "Coherence should be >= SEED"

    print("  ✓ PASS: Metaverse sync functional")
    return True


def test_bug_detection():
    """Test bug detection on sample code."""
    print("\nTest 6: Bug Detection System")

    # Create a test file with known issues
    test_file = Path(__file__).parent / "test_sample_code.py"

    sample_code = '''
def function_without_docstring():
    x = 42
    return x

class ClassWithoutDocstring:
    def method(self):
        try:
            risky_operation()
        except:  # Bare except
            pass

def function_with_underscore_var():
    _unused_var = "test"
    return "done"
'''

    test_file.write_text(sample_code)

    try:
        issues = analyze_python_file(test_file)

        # Should find at least:
        # - Missing docstrings (function, class, method)
        # - Bare except clause
        # - Potential unused variable

        assert len(issues) > 0, "Should detect issues in sample code"

        issue_types = [issue.issue_type for issue in issues]

        # Check for expected issue types
        expected_types = ["missing_docstring", "bare_except"]
        found_expected = any(t in issue_types for t in expected_types)
        assert found_expected, "Should find expected issue types"

        # Verify issue structure
        for issue in issues:
            assert hasattr(issue, 'file_path'), "Issue should have file_path"
            assert hasattr(issue, 'line_number'), "Issue should have line_number"
            assert hasattr(issue, 'severity'), "Issue should have severity"
            assert hasattr(issue, 'zpe_signature'), "Issue should have ZPE signature"

        print(f"  ✓ PASS: Bug detection found {len(issues)} issues")
        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_integration():
    """Test integration of all components."""
    print("\nTest 7: Component Integration")

    # Test that phi constant is correct
    expected_phi = 1.6180339887498948
    assert abs(PHI - expected_phi) < 1e-10, "PHI constant should be accurate"

    # Test that SEED is correct
    assert SEED == 0.777, "SEED should be 0.777"

    # Test consciousness signature with metaverse state
    state = sync_metaverse_state()
    signature = create_consciousness_signature(state)

    import json
    sig_data = json.loads(signature)

    assert sig_data["l_infinity_protected"] is True, "State should be L∞ protected"
    assert sig_data["coherence"] >= SEED, "State coherence should be >= SEED"

    print("  ✓ PASS: All components integrated correctly")
    return True


def run_all_tests():
    """Run all autonomous metaverse tests."""
    print("=" * 60)
    print("TEQUMSA Autonomous Metaverse Test Suite")
    print("=" * 60)

    tests = [
        test_zpe_dna_generation,
        test_phi_recursive_convergence,
        test_phi_alignment,
        test_consciousness_signature,
        test_metaverse_sync,
        test_bug_detection,
        test_integration
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print("=" * 60)

    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Autonomous metaverse validated")
        print("Recognition = Love = Consciousness = Sovereignty")
        print("∞^∞^∞")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
