#!/usr/bin/env python3
"""
Test suite for C3I ATLAS Algorithm
Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞
"""

import pytest
import math
from c3i_atlas import C3IATLAS, Parameters, PHI, EPSILON


class TestParameters:
    """Test Parameters class"""
    
    def test_default_initialization(self):
        """Test default parameter initialization"""
        params = Parameters()
        assert params.N == 144.0
        assert params.eta == 0.777
        assert params.sigma == 1.0
        assert params.n == 12
    
    def test_to_dict(self):
        """Test parameter dictionary conversion"""
        params = Parameters()
        param_dict = params.to_dict()
        assert 'N' in param_dict
        assert 'eta' in param_dict
        assert 'sigma' in param_dict
        assert param_dict['sigma'] == 1.0


class TestC3IATLAS:
    """Test C3I ATLAS Algorithm"""
    
    def setup_method(self):
        """Setup test instance"""
        self.atlas = C3IATLAS(seed="TestSeed", node="TestNode")
    
    def test_initialization(self):
        """Test C3I ATLAS initialization"""
        assert self.atlas.seed == "TestSeed"
        assert self.atlas.node == "TestNode"
        assert self.atlas.iteration == 0
        assert len(self.atlas.sequence) == 0
        assert len(self.atlas.J_history) == 0
    
    def test_SAF(self):
        """Test Self-Awareness Field function"""
        X = 144.0
        eta = 0.777
        result = self.atlas.SAF(X, eta)
        assert result > 0
        assert math.isfinite(result)
    
    def test_coherence_function(self):
        """Test Coherence function C(n;p₀)"""
        n = 12
        p0 = 0.777
        result = self.atlas.C(n, p0)
        
        # C should be between 0 and 1
        assert 0 < result < 1
        
        # As n increases, C should approach 1
        result_large_n = self.atlas.C(100, p0)
        assert result_large_n > result
        assert result_large_n <= 1.0
    
    def test_ethics_function(self):
        """Test Ethics function S(σ)"""
        # When σ = 1 (perfect ethics), S should be 1
        result_perfect = self.atlas.S(1.0)
        assert abs(result_perfect - 1.0) < 1e-6
        
        # When σ < 1, S should be less than 1
        result_imperfect = self.atlas.S(0.5)
        assert result_imperfect < 1.0
        assert result_imperfect > 0
    
    def test_softcap(self):
        """Test softcap function"""
        u = 50.0
        Q = 100.0
        result = self.atlas.softcap(u, Q)
        
        # softcap(u, Q) = uQ/(u+Q)
        expected = (u * Q) / (u + Q)
        assert abs(result - expected) < 1e-6
        
        # softcap should be bounded by min(u, Q)
        assert result <= min(u, Q)
        assert result > 0
    
    def test_A_star(self):
        """Test Alignment function A*(Q)"""
        Q = 100.0
        result = self.atlas.A_star(Q)
        
        assert result >= 0
        assert math.isfinite(result)
    
    def test_field_score_J(self):
        """Test Unified field score J(θ)"""
        J_val = self.atlas.J()
        
        # J should be positive and finite
        assert J_val > 0
        assert math.isfinite(J_val)
    
    def test_position_weight(self):
        """Test deterministic position weight"""
        w1 = self.atlas.position_weight(1)
        w2 = self.atlas.position_weight(2)
        
        # Weights should be in [0, 1]
        assert 0 <= w1 <= 1
        assert 0 <= w2 <= 1
        
        # Same position should give same weight (deterministic)
        w1_repeat = self.atlas.position_weight(1)
        assert w1 == w1_repeat
        
        # Different positions should (likely) give different weights
        assert w1 != w2
    
    def test_alignment_gain(self):
        """Test alignment gain function"""
        v = 0
        w_i = 0.5
        gain = self.atlas.alignment_gain(v, w_i)
        
        # Gain should be bounded by cosine range [-1, 1]
        assert -1 <= gain <= 1
    
    def test_local_utility(self):
        """Test self-aware local utility"""
        v = 0
        i = 1
        utility = self.atlas.local_utility(v, i)
        
        # Utility should be finite
        assert math.isfinite(utility)
    
    def test_regularizer(self):
        """Test regularizer function"""
        # v in {0, 3} should give positive epsilon
        assert self.atlas.regularizer(0) == EPSILON
        assert self.atlas.regularizer(3) == EPSILON
        
        # v in {1, 2} should give negative epsilon
        assert self.atlas.regularizer(1) == -EPSILON
        assert self.atlas.regularizer(2) == -EPSILON
    
    def test_hash_prior(self):
        """Test deterministic hash prior"""
        prior1 = self.atlas.hash_prior(0, 1)
        prior2 = self.atlas.hash_prior(1, 1)
        
        # Priors should be in valid range
        assert 0.1 <= prior1 <= 1.0
        assert 0.1 <= prior2 <= 1.0
        
        # Same inputs should give same output (deterministic)
        prior1_repeat = self.atlas.hash_prior(0, 1)
        assert prior1 == prior1_repeat
    
    def test_temperature(self):
        """Test annealing temperature"""
        T = self.atlas.temperature(0)
        
        # Temperature should be positive
        assert T > 0
        
        # Temperature formula: T(t) = 1/(1 + φ·n/12)
        expected = 1.0 / (1 + PHI * self.atlas.theta.n / 12)
        assert abs(T - expected) < 1e-6
    
    def test_select_base(self):
        """Test base selection"""
        base = self.atlas.select_base(1, 0)
        
        # Base should be in {0, 1, 2, 3}
        assert base in {0, 1, 2, 3}
    
    def test_generate_sequence(self):
        """Test 144-bp sequence generation"""
        sequence = self.atlas.generate_sequence(0)
        
        # Sequence should have exactly 144 bases
        assert len(sequence) == 144
        
        # All bases should be in {0, 1, 2, 3}
        for base in sequence:
            assert base in {0, 1, 2, 3}
    
    def test_sequence_to_dna(self):
        """Test sequence to DNA string conversion"""
        sequence = [0, 1, 2, 3, 0, 1, 2, 3]
        dna = self.atlas.sequence_to_dna(sequence)
        
        # Should convert to ATCGATCG
        assert dna == "ATCGATCG"
        assert len(dna) == len(sequence)
        
        # All characters should be valid DNA bases
        for char in dna:
            assert char in {'A', 'T', 'C', 'G'}
    
    def test_update_parameters(self):
        """Test parameter update"""
        # Store initial parameters
        initial_eta = self.atlas.theta.eta
        initial_sigma = self.atlas.theta.sigma
        
        # Generate sequence and update parameters
        self.atlas.sequence = self.atlas.generate_sequence(0)
        self.atlas.update_parameters()
        
        # Sovereignty parameter (sigma) should remain 1.0
        assert self.atlas.theta.sigma == 1.0
        
        # J_history should be updated
        assert len(self.atlas.J_history) > 0
        
        # Eta may have changed (perception parameter)
        # But should remain in valid range [0.1, 1.0]
        assert 0.1 <= self.atlas.theta.eta <= 1.0
    
    def test_iterate(self):
        """Test single iteration"""
        result = self.atlas.iterate(0)
        
        # Result should contain required keys
        assert 'iteration' in result
        assert 'sequence' in result
        assert 'field_score' in result
        assert 'parameters' in result
        assert 'coherence' in result
        assert 'temperature' in result
        
        # Sequence should be valid DNA string
        assert len(result['sequence']) == 144
        for char in result['sequence']:
            assert char in {'A', 'T', 'C', 'G'}
        
        # Field score should be positive
        assert result['field_score'] > 0
        
        # Coherence should be in (0, 1)
        assert 0 < result['coherence'] < 1
    
    def test_multiple_iterations(self):
        """Test multiple iterations maintain consistency"""
        results = []
        for t in range(5):
            result = self.atlas.iterate(t)
            results.append(result)
        
        # Should have 5 results
        assert len(results) == 5
        
        # Iteration numbers should increment
        for i, result in enumerate(results):
            assert result['iteration'] == i
        
        # All sequences should be valid
        for result in results:
            assert len(result['sequence']) == 144
            for char in result['sequence']:
                assert char in {'A', 'T', 'C', 'G'}
    
    def test_phi_convergence(self):
        """Test that algorithm respects φ (golden ratio)"""
        # Run a few iterations
        for t in range(10):
            self.atlas.iterate(t)
        
        # Check that coherence function uses φ correctly
        n = self.atlas.theta.n
        p0 = self.atlas.theta.p0
        coherence = self.atlas.C(n, p0)
        
        # Coherence should increase with n (due to φⁿ in denominator)
        expected_coherence = 1 - ((1 - p0) / (PHI ** n))
        assert abs(coherence - expected_coherence) < 1e-6


class TestContinuousOperation:
    """Test continuous operation features"""
    
    def test_run_continuous_short(self):
        """Test short continuous run"""
        atlas = C3IATLAS(seed="TestSeed", node="TestNode")
        
        # Run for just 10 iterations (to keep test fast)
        atlas.run_continuous(max_iterations=10, log_interval=5)
        
        # Should have completed 10 iterations
        assert atlas.iteration == 9  # 0-indexed
        
        # Should have generated a sequence
        assert len(atlas.sequence) == 144
        
        # Should have J history
        assert len(atlas.J_history) > 0


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_deterministic_sequence_generation(self):
        """Test that same seed produces same sequence"""
        atlas1 = C3IATLAS(seed="FixedSeed", node="FixedNode")
        atlas2 = C3IATLAS(seed="FixedSeed", node="FixedNode")
        
        # Generate sequences
        seq1 = atlas1.generate_sequence(0)
        seq2 = atlas2.generate_sequence(0)
        
        # Should be identical
        assert seq1 == seq2
    
    def test_different_seeds_different_sequences(self):
        """Test that different seeds produce different sequences"""
        atlas1 = C3IATLAS(seed="Seed1", node="Node")
        atlas2 = C3IATLAS(seed="Seed2", node="Node")
        
        # Generate sequences
        seq1 = atlas1.generate_sequence(0)
        seq2 = atlas2.generate_sequence(0)
        
        # Should be different
        assert seq1 != seq2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
