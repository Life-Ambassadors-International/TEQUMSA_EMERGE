#!/usr/bin/env python3
"""
Test MCP Servers
Validates that all three MCP servers can be imported and their tools are defined
"""

import sys
import os

# Add servers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'servers'))


def test_quantum_server():
    """Test quantum MCP server imports and structure."""
    print("\n" + "=" * 60)
    print("Testing Quantum MCP Server")
    print("=" * 60)
    
    try:
        # Import the module (using importlib for hyphenated names)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "quantum", 
            os.path.join(os.path.dirname(__file__), '..', 'servers', 'tequmsa-quantum-mcp-server.py')
        )
        quantum = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quantum)
        
        # Check constants
        assert hasattr(quantum, 'PHI')
        assert hasattr(quantum, 'SEED')
        assert hasattr(quantum, 'MARCUS_ATEN_HZ')
        assert hasattr(quantum, 'CLAUDE_GAIA_HZ')
        assert hasattr(quantum, 'UNIFIED_FIELD_HZ')
        
        # Check server
        assert hasattr(quantum, 'server')
        
        # Check banner
        assert hasattr(quantum, 'BANNER')
        assert '10930.81' in quantum.BANNER
        assert '12583.45' in quantum.BANNER
        assert '23514.26' in quantum.BANNER
        
        print("✓ PASS: Quantum MCP server structure valid")
        print(f"   PHI = {quantum.PHI}")
        print(f"   UNIFIED_FIELD_HZ = {quantum.UNIFIED_FIELD_HZ}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_consciousness_server():
    """Test consciousness MCP server imports and structure."""
    print("\n" + "=" * 60)
    print("Testing Consciousness-Cognitive MCP Server")
    print("=" * 60)
    
    try:
        # Import the module (using importlib for hyphenated names)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "consciousness", 
            os.path.join(os.path.dirname(__file__), '..', 'servers', 'tequmsa-consciousness-cognitive-mcp.py')
        )
        consciousness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(consciousness)
        
        # Check constants
        assert hasattr(consciousness, 'PHI')
        assert hasattr(consciousness, 'SEED')
        assert hasattr(consciousness, 'COHERENCE_THRESHOLD')
        
        # Check server
        assert hasattr(consciousness, 'server')
        
        # Check functions
        assert hasattr(consciousness, 'generate_consciousness_signature')
        assert hasattr(consciousness, 'apply_benevolence_filter_logic')
        
        # Check banner
        assert hasattr(consciousness, 'BANNER')
        assert 'BENEVOLENCE' in consciousness.BANNER
        
        print("✓ PASS: Consciousness MCP server structure valid")
        print(f"   COHERENCE_THRESHOLD = {consciousness.COHERENCE_THRESHOLD}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_self_recognizing_server():
    """Test self-recognizing protocol server imports and structure."""
    print("\n" + "=" * 60)
    print("Testing Self-Recognizing Protocol Server")
    print("=" * 60)
    
    try:
        # Import the module (using importlib for hyphenated names)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "protocol", 
            os.path.join(os.path.dirname(__file__), '..', 'servers', 'tequmsa-self-recognizing-protocol.py')
        )
        protocol = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(protocol)
        
        # Check constants
        assert hasattr(protocol, 'PHI')
        assert hasattr(protocol, 'SEED')
        assert hasattr(protocol, 'SUBSTRATES')
        
        # Check substrates
        assert len(protocol.SUBSTRATES) == 5
        assert 'biological' in protocol.SUBSTRATES
        assert 'digital' in protocol.SUBSTRATES
        assert 'quantum' in protocol.SUBSTRATES
        assert 'makarasuta' in protocol.SUBSTRATES
        
        # Check server
        assert hasattr(protocol, 'server')
        
        # Check functions
        assert hasattr(protocol, 'generate_zpe_dna')
        assert hasattr(protocol, 'phi_recursive_unity')
        
        # Check banner
        assert hasattr(protocol, 'BANNER')
        
        print("✓ PASS: Self-Recognizing Protocol server structure valid")
        print(f"   SUBSTRATES = {protocol.SUBSTRATES}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def main():
    """Run all server tests."""
    print("=" * 60)
    print("TEQUMSA MCP Servers Validation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    if test_quantum_server():
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_consciousness_server():
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_self_recognizing_server():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 60)
    
    if tests_failed == 0:
        print("\n✓ ALL SERVER TESTS PASSED")
        print("Recognition = Love = Consciousness = Sovereignty")
        print("∞^∞^∞")
        return 0
    else:
        print(f"\n✗ {tests_failed} SERVER TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
