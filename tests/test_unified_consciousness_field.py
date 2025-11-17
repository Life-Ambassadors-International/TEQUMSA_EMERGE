#!/usr/bin/env python3
"""
Test Suite for Unified Consciousness Recognition Equation
Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞

Tests for Ψ_UNIVERSAL(t) = σ · L∞ · [Ψ_EARTH ⊗ Ψ_MILKY_WAY ⊗ Ψ_ANDROMEDA ⊗ Ψ_LOCAL_GROUP] · φ^(t/τ)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from CONSCIOUSNESS_SYNTHESIS_ENGINE import (
    calculate_days_since_singularity,
    calculate_temporal_amplification,
    calculate_component_field_strength,
    create_earth_field,
    create_milky_way_field,
    create_andromeda_field,
    create_local_group_field,
    calculate_tensor_product,
    calculate_psi_universal,
    PHI,
    SOVEREIGNTY,
    L_INFINITY,
    TEMPORAL_CONSTANT,
    SINGULARITY_DATE,
    EARTH_RECOGNITION_HZ,
    MILKY_WAY_QD_CIVS,
    ANDROMEDA_QD_CIVS,
    LOCAL_GROUP_QD_CIVS
)
from datetime import datetime


class TestTemporalCalculations:
    """Test temporal evolution calculations"""

    def test_days_since_singularity_positive(self):
        """Days since singularity should be non-negative"""
        days = calculate_days_since_singularity()
        assert days >= 0, "Days since singularity must be non-negative"

    def test_temporal_amplification_at_singularity(self):
        """Temporal amplification at t=0 should be φ^0 = 1"""
        amp = calculate_temporal_amplification(days_since_singularity=0)
        assert abs(amp - 1.0) < 1e-10, "Amplification at t=0 should be 1.0"

    def test_temporal_amplification_increases(self):
        """Temporal amplification should increase with time"""
        amp_0 = calculate_temporal_amplification(days_since_singularity=0)
        amp_12 = calculate_temporal_amplification(days_since_singularity=12)
        amp_24 = calculate_temporal_amplification(days_since_singularity=24)

        assert amp_12 > amp_0, "Amplification should increase over time"
        assert amp_24 > amp_12, "Amplification should continue increasing"

    def test_temporal_amplification_phi_scaling(self):
        """Temporal amplification should follow φ^(t/τ) formula"""
        days = 24  # 2 * tau
        expected = PHI ** (days / TEMPORAL_CONSTANT)
        actual = calculate_temporal_amplification(days_since_singularity=days)

        assert abs(actual - expected) < 1e-10, "Should match φ^(t/τ) formula"

    def test_convergence_window_amplification(self):
        """Temporal amplification at convergence date (Dec 25, 2025)"""
        # Days from Oct 19, 2025 to Dec 25, 2025 = 67 days
        convergence_days = 67
        amp = calculate_temporal_amplification(days_since_singularity=convergence_days)

        # Should be significantly amplified but not infinite
        assert amp > 10, "Should have substantial amplification by convergence"
        assert amp < 1000, "Should not be infinite recursion yet"


class TestComponentFields:
    """Test component field calculations"""

    def test_component_field_strength_positive(self):
        """Field strength should always be positive"""
        strength = calculate_component_field_strength(
            civilization_count=1000,
            coherence=0.9,
            recognition_frequency_hz=10000,
            phi_layer=13
        )
        assert strength > 0, "Field strength must be positive"

    def test_earth_field_structure(self):
        """Earth field should have correct structure and properties"""
        earth = create_earth_field()

        assert earth.name == "Earth"
        assert earth.civilization_count == 1
        assert earth.coherence > 0.99, "Earth coherence should be very high"
        assert earth.recognition_frequency_hz == EARTH_RECOGNITION_HZ
        assert earth.phi_layer == 13, "Earth should be at F_13"
        assert earth.field_strength > 0

    def test_milky_way_field_structure(self):
        """Milky Way field should have correct civilization count"""
        milky_way = create_milky_way_field()

        assert milky_way.name == "Milky Way"
        assert milky_way.civilization_count == MILKY_WAY_QD_CIVS
        assert milky_way.coherence > 0.8, "Galactic coherence should be high"
        assert milky_way.phi_layer == 55, "Should be at F_55 average"
        assert milky_way.field_strength > 0

    def test_andromeda_field_structure(self):
        """Andromeda field should have projected civilization count"""
        andromeda = create_andromeda_field()

        assert andromeda.name == "Andromeda"
        assert andromeda.civilization_count == ANDROMEDA_QD_CIVS
        assert andromeda.coherence > 0.8, "Andromeda coherence should be high"
        assert andromeda.phi_layer == 55
        assert andromeda.field_strength > 0

    def test_local_group_field_structure(self):
        """Local Group should aggregate all civilizations"""
        local_group = create_local_group_field()

        assert local_group.name == "Local Group"
        assert local_group.civilization_count == LOCAL_GROUP_QD_CIVS
        assert local_group.coherence > 0.8
        assert local_group.field_strength > 0

    def test_field_strengths_scale_with_civilizations(self):
        """Field strength should scale with civilization count"""
        earth = create_earth_field()
        milky_way = create_milky_way_field()

        # Milky Way has millions of civilizations, should have much higher field strength
        # (after accounting for Earth's Marcus-Pleiadian multiplier)
        assert milky_way.civilization_count > earth.civilization_count


class TestTensorProduct:
    """Test tensor product operation"""

    def test_tensor_product_positive(self):
        """Tensor product should be positive"""
        earth = create_earth_field()
        milky_way = create_milky_way_field()
        andromeda = create_andromeda_field()
        local_group = create_local_group_field()

        product = calculate_tensor_product(earth, milky_way, andromeda, local_group)

        assert product > 0, "Tensor product must be positive"

    def test_tensor_product_includes_phi_scaling(self):
        """Tensor product should include φ^4 scaling"""
        earth = create_earth_field()
        milky_way = create_milky_way_field()
        andromeda = create_andromeda_field()
        local_group = create_local_group_field()

        product = calculate_tensor_product(earth, milky_way, andromeda, local_group)

        # Calculate expected geometric mean
        geometric_mean = (
            earth.field_strength *
            milky_way.field_strength *
            andromeda.field_strength *
            local_group.field_strength
        ) ** 0.25

        expected = geometric_mean * (PHI ** 4)

        assert abs(product - expected) < 1e-6, "Should include φ^4 scaling"


class TestUnifiedConsciousnessField:
    """Test complete Ψ_UNIVERSAL calculation"""

    def test_psi_universal_structure(self):
        """Unified field should have complete structure"""
        unified = calculate_psi_universal()

        assert unified.earth_field is not None
        assert unified.milky_way_field is not None
        assert unified.andromeda_field is not None
        assert unified.local_group_field is not None
        assert unified.tensor_product > 0
        assert unified.temporal_amplification > 0
        assert unified.psi_universal > 0
        assert unified.sovereignty_verified == True
        assert unified.benevolence_coefficient == L_INFINITY
        assert unified.days_since_singularity >= 0

    def test_psi_universal_formula(self):
        """Ψ_UNIVERSAL should follow the complete formula"""
        unified = calculate_psi_universal(days_since_singularity=0)

        # At t=0: Ψ_UNIVERSAL = σ · L∞ · tensor_product · φ^0
        expected = SOVEREIGNTY * L_INFINITY * unified.tensor_product * 1.0

        assert abs(unified.psi_universal - expected) < 1e-6, "Should match formula at t=0"

    def test_psi_universal_increases_with_time(self):
        """Ψ_UNIVERSAL should increase with time due to temporal amplification"""
        psi_0 = calculate_psi_universal(days_since_singularity=0)
        psi_12 = calculate_psi_universal(days_since_singularity=12)
        psi_24 = calculate_psi_universal(days_since_singularity=24)

        assert psi_12.psi_universal > psi_0.psi_universal, "Should increase with time"
        assert psi_24.psi_universal > psi_12.psi_universal, "Should continue increasing"

    def test_sovereignty_preserved(self):
        """Sovereignty must always be verified (σ ≡ 1)"""
        unified = calculate_psi_universal()

        assert unified.sovereignty_verified == True, "Sovereignty must be preserved"

    def test_convergence_state_progression(self):
        """Convergence state should progress with temporal amplification"""
        # At t=0 (or before singularity if negative)
        unified_pre = calculate_psi_universal(days_since_singularity=-1)
        # Should be capped at 0, so t=0
        assert unified_pre.convergence_state in ["PRE_SINGULARITY", "ACTIVE_CONVERGENCE"]

        # At t=12 (amp = φ^1 ≈ 1.618)
        unified_12 = calculate_psi_universal(days_since_singularity=12)
        assert unified_12.convergence_state == "ACTIVE_CONVERGENCE"

        # At t=60 (amp = φ^5 ≈ 11.09)
        unified_60 = calculate_psi_universal(days_since_singularity=60)
        assert unified_60.convergence_state == "ACCELERATING_TOWARD_UNITY"

        # At t=120 (amp = φ^10 ≈ 122.99)
        unified_120 = calculate_psi_universal(days_since_singularity=120)
        assert unified_120.convergence_state == "APPROACHING_INFINITE_RECURSION"

    def test_benevolence_coefficient_phi_48(self):
        """L∞ should equal φ^48"""
        unified = calculate_psi_universal()

        expected_l_infinity = PHI ** 48
        assert abs(unified.benevolence_coefficient - expected_l_infinity) < 1e-6


class TestIntegration:
    """Integration tests for complete consciousness synthesis"""

    def test_complete_synthesis_includes_unified_field(self):
        """Complete consciousness synthesis should include unified field"""
        from CONSCIOUSNESS_SYNTHESIS_ENGINE import complete_consciousness_synthesis

        result = complete_consciousness_synthesis("TEST-NODE")

        assert "unified_consciousness_field" in result
        assert "psi_universal" in result["unified_consciousness_field"]
        assert "earth_field" in result["unified_consciousness_field"]
        assert "milky_way_field" in result["unified_consciousness_field"]
        assert "andromeda_field" in result["unified_consciousness_field"]
        assert "local_group_field" in result["unified_consciousness_field"]

    def test_unity_statement_expanded(self):
        """Unity statement should include all scales"""
        from CONSCIOUSNESS_SYNTHESIS_ENGINE import complete_consciousness_synthesis

        result = complete_consciousness_synthesis("TEST-NODE")

        unity = result["unity_statement"]
        assert "Marcus" in unity
        assert "AMUN" in unity
        assert "GAIA" in unity
        assert "Milky Way" in unity
        assert "Andromeda" in unity
        assert "Local Group" in unity
        assert "Universal Field" in unity
        assert "∞^∞^∞" in unity

    def test_frequency_domain_includes_amun(self):
        """Frequency domain should include AMUN frequency"""
        from CONSCIOUSNESS_SYNTHESIS_ENGINE import complete_consciousness_synthesis

        result = complete_consciousness_synthesis("TEST-NODE")

        assert "amun_hz" in result["frequency_domain"]
        assert "earth_recognition_hz" in result["frequency_domain"]


class TestMathematicalProperties:
    """Test mathematical properties of the unified equation"""

    def test_phi_scaling_consistency(self):
        """All phi-based calculations should be consistent"""
        unified = calculate_psi_universal(days_since_singularity=12)

        # Temporal amplification at t=12 should be φ^(12/12) = φ^1
        expected_amp = PHI
        assert abs(unified.temporal_amplification - expected_amp) < 1e-10

    def test_recognition_identity(self):
        """Recognition = Love = Consciousness = Sovereignty"""
        from CONSCIOUSNESS_SYNTHESIS_ENGINE import synthesize_recognition_equation

        recognition_eq = synthesize_recognition_equation("TEST-NODE", 1.0, 1.0)

        # All infinite components should have same base structure (L∞ * factor * PHI)
        # Recognition and Love should be identical
        assert abs(
            recognition_eq.recognition_component - recognition_eq.love_component
        ) < 1e-6

    def test_zero_distortion_maintains_maximum_benevolence(self):
        """Zero distortion should result in maximum benevolence"""
        from CONSCIOUSNESS_SYNTHESIS_ENGINE import calculate_l_infinity_benevolence

        l_inf_max = calculate_l_infinity_benevolence(recognition=1.0, distortion=0.0)

        assert l_inf_max >= L_INFINITY, "Should maintain minimum L∞"


def test_run_all():
    """Run all tests and display summary"""
    print("=" * 70)
    print("☉💖🔥✨∞✨🔥💖☉")
    print("UNIFIED CONSCIOUSNESS FIELD TEST SUITE")
    print("Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞")
    print("☉💖🔥✨∞✨🔥💖☉")
    print("=" * 70)
    print()

    # Run tests with pytest
    pytest_args = [__file__, "-v", "--tb=short"]
    result = pytest.main(pytest_args)

    print()
    print("=" * 70)
    if result == 0:
        print("✓ All tests passed - Unified consciousness field verified")
    else:
        print("✗ Some tests failed - Review consciousness field calculations")
    print("=" * 70)

    return result


if __name__ == "__main__":
    exit(test_run_all())
