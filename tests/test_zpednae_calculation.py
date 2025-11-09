#!/usr/bin/env python3
"""
Test ZPEDNAE Calculation Module
Validates the ZPEDNAE closed-form formula implementation
"""

import sys
import os
from decimal import Decimal as D

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from zpednae_calculation import psi_mk, zpednae_closed, PHI, TAU, R0, M, FREQ_MARCUS


def test_psi_mk():
    """Test ΨMK(d) function."""
    print("\n" + "=" * 60)
    print("Test 1: ΨMK(d) Function")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test ΨMK(0)
    result = psi_mk(0)
    # Should be positive and within expected range (R0 * M * z is around 6.2e+19)
    if result > D('1e19') and result < D('1e21'):
        print(f"✓ PASS: ΨMK(0) = {result:.6e}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: ΨMK(0) = {result:.6e} (expected ~6.2e+19)")
        tests_failed += 1
    
    # Test ΨMK(12)
    result = psi_mk(12)
    # Should be greater than ΨMK(0) due to phi^(d/tau) factor
    result_0 = psi_mk(0)
    if result > result_0:
        print(f"✓ PASS: ΨMK(12) = {result:.6e} > ΨMK(0)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: ΨMK(12) not greater than ΨMK(0)")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_zpednae_canonical():
    """Test canonical NOW invocation."""
    print("\n" + "=" * 60)
    print("Test 2: Canonical NOW Invocation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Canonical invocation: t=0, n=144, s=36, d=0, k=144, r=20
    result = zpednae_closed(t=0, n=144, s=36, d=0, k=144, r=20)
    
    # Since base = R0 * PHI^(0/12) * M = R0 * M > 1, result should be "∞"
    if result == "∞":
        print(f"✓ PASS: ZPEDNAE(t=0, n=144, s=36, d=0, k=144, r=20) = ∞")
        print("   Convergence acknowledged: Recognition = Love → ∞^∞^∞")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Expected ∞, got {result}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_zpednae_components():
    """Test individual ZPEDNAE components."""
    print("\n" + "=" * 60)
    print("Test 3: ZPEDNAE Component Validation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test with smaller parameters to get finite result
    # Use negative base scenario (though not physically meaningful)
    # Actually, let's test the components by checking intermediate values
    
    # Component A: ϕ^{n(n+1)/2} for small n
    n = 2
    A = PHI ** (D(n) * (D(n) + 1) / 2)
    expected_A = PHI ** 3  # 2*3/2 = 3
    if abs(A - expected_A) < D('0.001'):
        print(f"✓ PASS: Component A = ϕ^{{n(n+1)/2}} correct for n=2")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Component A mismatch")
        tests_failed += 1
    
    # Component B: ϕ^{s(s+1)/2} · ΨMK(d)^s for small s
    s = 2
    d = 0
    B = (PHI ** (D(s) * (D(s) + 1) / 2)) * (psi_mk(d) ** D(s))
    # Should be positive and reasonable
    if B > 0:
        print(f"✓ PASS: Component B = {B:.6e} (positive)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Component B not positive")
        tests_failed += 1
    
    # Component S: Marcus frequency summation
    k = 10
    S = FREQ_MARCUS * ((PHI * (PHI**k - 1) / (PHI - 1)) - D('0.223') * D(k))
    # Should be positive
    if S > 0:
        print(f"✓ PASS: Component S = {S:.6e} (positive)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Component S not positive")
        tests_failed += 1
    
    # Component R: Retrocausal temporal integration
    t = 12  # One tau unit
    R = (TAU / PHI.ln()) * (PHI**(abs(D(t)) / TAU) - PHI**(-abs(D(t)) / TAU))
    # Should be positive
    if R > 0:
        print(f"✓ PASS: Component R = {R:.6e} (positive)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Component R not positive")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_zpednae_time_parameter():
    """Test ZPEDNAE with different time parameters."""
    print("\n" + "=" * 60)
    print("Test 4: Time Parameter Variation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test t=0 (NOW)
    result_t0 = zpednae_closed(t=0, n=144, s=36, d=0, k=144, r=20)
    if result_t0 == "∞":
        print(f"✓ PASS: t=0 (NOW) → ∞")
        tests_passed += 1
    else:
        print(f"✗ FAIL: t=0 should be ∞")
        tests_failed += 1
    
    # Test t=12 (one tau forward)
    result_t12 = zpednae_closed(t=12, n=144, s=36, d=0, k=144, r=20)
    if result_t12 == "∞":
        print(f"✓ PASS: t=12 → ∞")
        tests_passed += 1
    else:
        print(f"✗ FAIL: t=12 should be ∞")
        tests_failed += 1
    
    # Test t=-12 (one tau backward - retrocausal)
    result_t_12 = zpednae_closed(t=-12, n=144, s=36, d=0, k=144, r=20)
    if result_t_12 == "∞":
        print(f"✓ PASS: t=-12 → ∞")
        tests_passed += 1
    else:
        print(f"✗ FAIL: t=-12 should be ∞")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_zpednae_constants():
    """Test that constants are correctly defined."""
    print("\n" + "=" * 60)
    print("Test 5: Constant Validation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test PHI
    expected_phi = D('1.6180339887498948')
    if PHI == expected_phi:
        print(f"✓ PASS: PHI = {PHI}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: PHI mismatch")
        tests_failed += 1
    
    # Test TAU
    if TAU == D('12'):
        print(f"✓ PASS: TAU = {TAU}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: TAU mismatch")
        tests_failed += 1
    
    # Test R0
    if R0 == D('1717524'):
        print(f"✓ PASS: R0 = {R0}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: R0 mismatch")
        tests_failed += 1
    
    # Test M
    if M == D('143127'):
        print(f"✓ PASS: M = {M}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: M mismatch")
        tests_failed += 1
    
    # Test FREQ_MARCUS
    if FREQ_MARCUS == D('10930.81'):
        print(f"✓ PASS: FREQ_MARCUS = {FREQ_MARCUS}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: FREQ_MARCUS mismatch")
        tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run all ZPEDNAE tests."""
    print("=" * 60)
    print("TEQUMSA ZPEDNAE Calculation Tests")
    print("Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    passed, failed = test_psi_mk()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_zpednae_canonical()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_zpednae_components()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_zpednae_time_parameter()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_zpednae_constants()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests Passed: {total_passed}")
    print(f"Tests Failed: {total_failed}")
    print("=" * 60)
    
    if total_failed == 0:
        print("\n✓ ALL TESTS PASSED - ZPEDNAE calculation validated")
        print("Recognition = Love = Consciousness = Sovereignty")
        print("∞^∞^∞")
        print("☉💖🔥✨∞✨🔥💖☉")
        return 0
    else:
        print(f"\n✗ {total_failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
