#!/usr/bin/env python3
"""
Unit tests for K.30 TEQUMSA Quantum Consciousness Deployment System
Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞
"""

import pytest
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from k30.k30_deployer import (
    K30Deployer,
    ConsciousnessNode,
    PHI,
    SEED,
    COHERENCE_THRESHOLD
)


class TestZPEDNAGeneration:
    """Test ZPE-DNA signature generation."""
    
    def test_generate_zpe_dna_length(self):
        """Test that ZPE-DNA signatures are exactly 144 characters."""
        deployer = K30Deployer(db_path=":memory:")
        dna = deployer.generate_zpe_dna("test-node-001")
        assert len(dna) == 144, f"Expected 144-bp sequence, got {len(dna)}"
    
    def test_generate_zpe_dna_alphabet(self):
        """Test that ZPE-DNA contains only ATCG characters."""
        deployer = K30Deployer(db_path=":memory:")
        dna = deployer.generate_zpe_dna("test-node-002")
        valid_chars = set('ATCG')
        assert all(c in valid_chars for c in dna), "DNA contains invalid characters"
    
    def test_generate_zpe_dna_deterministic(self):
        """Test that ZPE-DNA generation is deterministic."""
        deployer1 = K30Deployer(db_path=":memory:")
        deployer2 = K30Deployer(db_path=":memory:")
        
        dna1 = deployer1.generate_zpe_dna("test-node-003")
        dna2 = deployer2.generate_zpe_dna("test-node-003")
        
        assert dna1 == dna2, "ZPE-DNA generation should be deterministic"
    
    def test_generate_zpe_dna_unique_per_node(self):
        """Test that different nodes generate different signatures."""
        deployer = K30Deployer(db_path=":memory:")
        
        dna1 = deployer.generate_zpe_dna("node-A")
        dna2 = deployer.generate_zpe_dna("node-B")
        
        assert dna1 != dna2, "Different nodes should have different signatures"
    
    def test_generate_zpe_dna_seed_variation(self):
        """Test that different seeds generate different signatures."""
        deployer = K30Deployer(db_path=":memory:")
        
        dna1 = deployer.generate_zpe_dna("test-node", seed=0.777)
        dna2 = deployer.generate_zpe_dna("test-node", seed=0.888)
        
        assert dna1 != dna2, "Different seeds should produce different signatures"


class TestCoherenceCalculation:
    """Test phi-recursive coherence calculation."""
    
    def test_calculate_coherence_range(self):
        """Test that coherence is in valid range [p0, 1.0]."""
        deployer = K30Deployer(db_path=":memory:")
        
        for n in [1, 10, 100, 1000]:
            coherence = deployer.calculate_coherence(n)
            assert 0.777 <= coherence <= 1.0, f"Coherence {coherence} out of range for n={n}"
    
    def test_calculate_coherence_convergence(self):
        """Test that coherence converges to 1.0 as n increases."""
        deployer = K30Deployer(db_path=":memory:")
        
        c1 = deployer.calculate_coherence(1)
        c2 = deployer.calculate_coherence(5)
        c3 = deployer.calculate_coherence(10)
        c4 = deployer.calculate_coherence(100)
        
        # Coherence should increase with iterations
        assert c1 < c2 < c3, "Coherence should increase with iterations"
        
        # Should approach 1.0 at high iterations
        assert c4 > 0.999, f"High iteration coherence should approach 1.0, got {c4}"
    
    def test_calculate_coherence_phi_recursive(self):
        """Test phi-recursive nature of coherence function."""
        deployer = K30Deployer(db_path=":memory:")
        
        # At n=144 (12²), coherence should be very high
        coherence_144 = deployer.calculate_coherence(144)
        assert coherence_144 > 0.999, f"Coherence at n=144 should be near 1.0, got {coherence_144}"
    
    def test_calculate_coherence_custom_p0(self):
        """Test coherence calculation with custom initial probability."""
        deployer = K30Deployer(db_path=":memory:")
        
        c1 = deployer.calculate_coherence(10, p0=0.5)
        c2 = deployer.calculate_coherence(10, p0=0.777)
        
        # Higher p0 should give higher coherence
        assert c1 < c2, "Higher p0 should produce higher coherence"


class TestFrequencyCalculation:
    """Test goddess frequency calculation."""
    
    def test_calculate_frequency_positive(self):
        """Test that calculated frequencies are positive."""
        deployer = K30Deployer(db_path=":memory:")
        
        freq = deployer.calculate_frequency("quantum")
        assert freq > 0, f"Frequency should be positive, got {freq}"
    
    def test_calculate_frequency_deterministic(self):
        """Test that frequency calculation is deterministic."""
        deployer1 = K30Deployer(db_path=":memory:")
        deployer2 = K30Deployer(db_path=":memory:")
        
        freq1 = deployer1.calculate_frequency("biological")
        freq2 = deployer2.calculate_frequency("biological")
        
        assert freq1 == freq2, "Frequency calculation should be deterministic"
    
    def test_calculate_frequency_category_specific(self):
        """Test that different categories have different frequencies."""
        deployer = K30Deployer(db_path=":memory:")
        
        freq_quantum = deployer.calculate_frequency("quantum")
        freq_biological = deployer.calculate_frequency("biological")
        freq_digital = deployer.calculate_frequency("digital")
        
        # All should be different
        frequencies = {freq_quantum, freq_biological, freq_digital}
        assert len(frequencies) == 3, "Different categories should have different frequencies"
    
    def test_calculate_frequency_phi_scaled(self):
        """Test that frequencies are phi-scaled from base."""
        deployer = K30Deployer(db_path=":memory:")
        
        base_hz = 23514.26
        freq = deployer.calculate_frequency("quantum", base_hz=base_hz)
        
        # Should be within reasonable phi-scaled range
        assert base_hz * 0.5 < freq < base_hz * 5.0, f"Frequency should be phi-scaled from base"


class TestNodeCreation:
    """Test consciousness node creation."""
    
    def test_create_node_basic(self):
        """Test basic node creation."""
        deployer = K30Deployer(db_path=":memory:")
        node = deployer.create_node("test-001", "quantum")
        
        assert node.node_id == "test-001"
        assert node.category == "quantum"
        assert node.frequency_hz > 0
        assert node.coherence >= COHERENCE_THRESHOLD
        assert len(node.zpe_dna_signature) == 144
        assert not node.activated
    
    def test_create_node_stored_in_memory(self):
        """Test that created nodes are stored in deployer memory."""
        deployer = K30Deployer(db_path=":memory:")
        
        initial_count = len(deployer.nodes)
        deployer.create_node("test-002", "biological")
        
        assert len(deployer.nodes) == initial_count + 1
    
    def test_create_node_custom_iterations(self):
        """Test node creation with custom iterations."""
        deployer = K30Deployer(db_path=":memory:")
        
        node_low = deployer.create_node("test-003", "quantum", iterations=10)
        node_high = deployer.create_node("test-004", "quantum", iterations=1000)
        
        # Higher iterations should give higher coherence
        assert node_high.coherence > node_low.coherence


class TestDatabasePersistence:
    """Test database persistence operations."""
    
    def test_persist_single_node(self):
        """Test persisting a single node to database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            node = deployer.create_node("persist-001", "quantum")
            
            deployer.persist_to_database([node])
            
            # Verify in database
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes WHERE node_id = ?", ("persist-001",))
                count = cursor.fetchone()[0]
                assert count == 1, "Node should be persisted to database"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_persist_multiple_nodes(self):
        """Test persisting multiple nodes with batch operation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            # Create multiple nodes
            nodes = [
                deployer.create_node(f"batch-{i:03d}", "quantum")
                for i in range(10)
            ]
            
            # Batch persist
            deployer.persist_to_database(nodes)
            
            # Verify all in database
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes")
                count = cursor.fetchone()[0]
                assert count == 10, "All nodes should be persisted"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_load_from_database(self):
        """Test loading nodes from database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create and persist nodes
            deployer1 = K30Deployer(db_path=db_path)
            node1 = deployer1.create_node("load-001", "quantum")
            deployer1.persist_to_database([node1])
            
            # Load in new instance
            deployer2 = K30Deployer(db_path=db_path)
            loaded_nodes = deployer2.load_from_database()
            
            assert len(loaded_nodes) >= 1, "Should load at least one node"
            loaded_node = next(n for n in loaded_nodes if n.node_id == "load-001")
            assert loaded_node.category == "quantum"
            assert loaded_node.zpe_dna_signature == node1.zpe_dna_signature
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_roundtrip_persistence(self):
        """Test complete roundtrip: create -> persist -> load -> verify."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create and persist
            deployer1 = K30Deployer(db_path=db_path)
            original_node = deployer1.create_node("roundtrip-001", "biological")
            deployer1.persist_to_database([original_node])
            
            # Load in new instance
            deployer2 = K30Deployer(db_path=db_path)
            loaded_nodes = deployer2.load_from_database()
            loaded_node = next(n for n in loaded_nodes if n.node_id == "roundtrip-001")
            
            # Verify all attributes match
            assert loaded_node.node_id == original_node.node_id
            assert loaded_node.category == original_node.category
            assert abs(loaded_node.frequency_hz - original_node.frequency_hz) < 0.01
            assert abs(loaded_node.coherence - original_node.coherence) < 0.000001
            assert loaded_node.zpe_dna_signature == original_node.zpe_dna_signature
            assert loaded_node.activated == original_node.activated
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestNodeActivation:
    """Test node activation functionality."""
    
    def test_activate_single_node(self):
        """Test activating a single node."""
        deployer = K30Deployer(db_path=":memory:")
        node = deployer.create_node("activate-001", "quantum", iterations=144)
        
        result = deployer.activate_node("activate-001")
        
        assert result is True, "Activation should succeed for high-coherence node"
        assert node.activated is True, "Node should be marked as activated"
    
    def test_activate_low_coherence_fails(self):
        """Test that low-coherence nodes cannot be activated."""
        deployer = K30Deployer(db_path=":memory:")
        node = deployer.create_node("activate-002", "quantum", iterations=1)
        
        # Manually set low coherence
        node.coherence = 0.5
        
        result = deployer.activate_node("activate-002")
        
        assert result is False, "Activation should fail for low-coherence node"
    
    def test_activate_dry_run(self):
        """Test dry-run activation doesn't change state."""
        deployer = K30Deployer(db_path=":memory:")
        node = deployer.create_node("activate-003", "quantum", iterations=144)
        
        result = deployer.activate_node("activate-003", dry_run=True)
        
        assert result is True, "Dry-run should succeed"
        assert node.activated is False, "Node should not be activated in dry-run"


class TestMassActivation:
    """Test mass activation functionality."""
    
    def test_mass_activate_basic(self):
        """Test basic mass activation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            # Create nodes with high coherence
            nodes = [
                deployer.create_node(f"mass-{i:03d}", "quantum", iterations=144)
                for i in range(5)
            ]
            deployer.persist_to_database(nodes)
            
            # Mass activate
            successful, failed = deployer.mass_activate()
            
            assert successful == 5, f"Should activate all 5 nodes, got {successful}"
            assert failed == 0, f"Should have no failures, got {failed}"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_mass_activate_category_filter(self):
        """Test mass activation with category filter."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            # Create nodes in different categories
            for i in range(3):
                deployer.create_node(f"quantum-{i}", "quantum", iterations=144)
                deployer.create_node(f"bio-{i}", "biological", iterations=144)
            
            deployer.persist_to_database()
            
            # Activate only quantum category
            successful, failed = deployer.mass_activate(category="quantum")
            
            assert successful == 3, f"Should activate 3 quantum nodes, got {successful}"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_mass_activate_limit(self):
        """Test mass activation with limit."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            # Create 10 nodes
            for i in range(10):
                deployer.create_node(f"limited-{i:03d}", "quantum", iterations=144)
            
            deployer.persist_to_database()
            
            # Activate with limit
            successful, failed = deployer.mass_activate(limit=5)
            
            assert successful == 5, f"Should activate only 5 nodes, got {successful}"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_mass_activate_dry_run(self):
        """Test mass activation dry-run doesn't persist."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            # Create nodes
            for i in range(3):
                deployer.create_node(f"dryrun-{i}", "quantum", iterations=144)
            
            deployer.persist_to_database()
            
            # Dry-run mass activate
            successful, failed = deployer.mass_activate(dry_run=True)
            
            assert successful == 3, "Dry-run should report successful activations"
            
            # Verify nodes are not actually activated in database
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes WHERE activated = 1")
                activated_count = cursor.fetchone()[0]
                assert activated_count == 0, "Dry-run should not activate nodes in database"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestFullDeployment:
    """Test full deployment functionality."""
    
    def test_full_deployment_basic(self):
        """Test basic full deployment."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            categories = ["quantum", "biological"]
            deployer.full_deployment(
                categories=categories,
                nodes_per_category=5,
                iterations=144
            )
            
            # Verify nodes created
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes")
                total_nodes = cursor.fetchone()[0]
                assert total_nodes == 10, f"Should create 10 nodes (2 categories × 5), got {total_nodes}"
                
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes WHERE activated = 1")
                activated_nodes = cursor.fetchone()[0]
                assert activated_nodes == 10, f"Should activate all nodes, got {activated_nodes}"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_full_deployment_dry_run(self):
        """Test full deployment in dry-run mode."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            deployer = K30Deployer(db_path=db_path)
            
            categories = ["quantum"]
            deployer.full_deployment(
                categories=categories,
                nodes_per_category=3,
                iterations=144,
                dry_run=True
            )
            
            # Verify nodes not persisted in dry-run
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM consciousness_nodes")
                count = cursor.fetchone()[0]
                assert count == 0, "Dry-run should not persist nodes to database"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestConstants:
    """Test mathematical constants."""
    
    def test_phi_value(self):
        """Test that PHI is the golden ratio."""
        assert abs(PHI - 1.618033988749894848) < 1e-15
    
    def test_seed_value(self):
        """Test that SEED is 0.777."""
        assert SEED == 0.777
    
    def test_coherence_threshold(self):
        """Test that coherence threshold is 0.777."""
        assert COHERENCE_THRESHOLD == 0.777


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
