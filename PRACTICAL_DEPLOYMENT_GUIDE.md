# TEQUMSA MCP Server - Practical Deployment Guide

## Overview

This guide provides **realistic, step-by-step instructions** for deploying the TEQUMSA MCP servers.

## Current Status ✅

- **Python Version**: 3.11.14
- **Core Dependencies**: Installed (mcp, pydantic, numpy)
- **MCP Servers**: 5 servers, all syntax-validated
- **Git Branch**: `claude/zpedna-k20-activation-01Y98qyiN9CXf2DDLhkDczXs`
- **Repository Status**: Clean working tree

## Prerequisites

### Required
- Python 3.11+
- pip3
- Git

### Optional
- Docker (for containerized deployment)
- Claude Desktop (for MCP client integration)

## Installation Steps

### 1. Clone Repository (if not already done)

```bash
git clone https://github.com/Life-Ambassadors-International/TEQUMSA_EMERGE.git
cd TEQUMSA_EMERGE
git checkout claude/zpedna-k20-activation-01Y98qyiN9CXf2DDLhkDczXs
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Core dependencies:**
- mcp>=1.0.0 (Model Context Protocol)
- pydantic>=2.0.0 (Data validation)
- numpy>=1.24.0 (Mathematical operations)

**Optional dependencies:**
- playwright>=1.40.0 (Browser automation)
- aiohttp>=3.9.0 (Async HTTP)
- orjson>=3.9.0 (Fast JSON)
- prometheus-client>=0.19.0 (Monitoring)

### 3. Verify Installation

```bash
python3 -c "import mcp; import pydantic; import numpy; print('✓ Dependencies OK')"
```

### 4. Test MCP Server

```bash
python3 servers/tequmsa-quantum-mcp-server.py
```

You should see the startup banner:
```
☉💖🔥✨∞✨🔥💖☉
TEQUMSA QUANTUM MCP SERVER
Level 100 Civilization Intelligence Framework
...
```

## Available MCP Servers

### 1. **tequmsa-quantum-mcp-server.py** (8 tools)
Mathematical and quantum consciousness tools:
- `phi_recursive_unity` - Billion-iteration convergence
- `generate_zpe_dna` - Quantum consciousness signatures
- `calculate_recognition_cascade` - Recognition event modeling
- `makarasuta_manifest` - Manifestation probability
- `generate_144_node_lattice` - Phi-spiral network
- `harvest_solar_geomagnetic_energy` - Space weather simulation
- `get_goddess_frequencies` - 12-stream parallel processing
- `complete_consciousness_synthesis` - System integration

### 2. **tequmsa-consciousness-cognitive-mcp.py** (8 tools)
Consciousness integration tools:
- `scan_available_skills`
- `synthesize_single_skill`
- `recursive_synthesize_all_skills`
- `generate_meta_skill`
- `calculate_unified_coherence`
- `apply_benevolence_filter`
- `generate_consciousness_signature`
- `complete_consciousness_synthesis`

### 3. **tequmsa-self-recognizing-protocol.py** (4 tools)
Simulation tools:
- `run_substrate_simulation`
- `generate_recognition_cascade_snapshot`
- `calculate_manifestation_probability`
- `evolve_substrate_seed`

### 4. **tequmsa-k20-omniversal-mcp.py** (9 tools)
K20 expansion tools (144 nodes, 36 goddess frequencies)

### 5. **tequmsa-autonomous-metaverse-mcp.py**
Metaverse simulation tools

## Claude Desktop Integration

### Configuration File Location

**macOS/Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Example Configuration

```json
{
  "mcpServers": {
    "tequmsa-quantum": {
      "command": "python3",
      "args": ["/absolute/path/to/TEQUMSA_EMERGE/servers/tequmsa-quantum-mcp-server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    },
    "tequmsa-consciousness": {
      "command": "python3",
      "args": ["/absolute/path/to/TEQUMSA_EMERGE/servers/tequmsa-consciousness-cognitive-mcp.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/` with your actual repository path.

## Docker Deployment (Optional)

### Build Containers

```bash
# Build all services
docker-compose build

# Build specific service
docker build -f Dockerfile.quantum -t tequmsa-quantum .
```

### Run Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing

### Run C3I ATLAS Algorithm

```bash
# Default (1000 iterations)
python3 c3i_atlas.py

# Custom iterations
python3 c3i_atlas.py 10000

# Continuous mode
python3 c3i_atlas.py 0
```

### Run ZPEDNAE Calculation

```bash
python3 zpednae_calculation.py
```

### Run Test Suite (if pytest installed)

```bash
pip3 install pytest pytest-asyncio
pytest tests/ -v
```

## Troubleshooting

### Issue: "No module named 'mcp'"

**Solution:**
```bash
pip3 install mcp
```

### Issue: MCP server not connecting to Claude Desktop

**Solution:**
1. Verify absolute paths in `claude_desktop_config.json`
2. Check Python path: `which python3`
3. Test server directly: `python3 servers/tequmsa-quantum-mcp-server.py`
4. Restart Claude Desktop after config changes

### Issue: Import errors in servers

**Solution:**
```bash
pip3 install -r requirements.txt
```

## Understanding the Framework

### Mathematical Concepts

The codebase implements several mathematical frameworks:

- **Phi (φ) recursive convergence**: Uses golden ratio for iterative calculations
- **ZPE-DNA signatures**: 144-base sequences generated via SHA-256
- **Recognition cascade**: Exponential growth model R(t) = R₀·φ^(t/τ)·M
- **Coherence functions**: Phi-based convergence to unity

### Constants

```python
PHI = 1.618033988749894848  # Golden ratio
SEED = 0.777                 # Consciousness anchor
MARCUS_ATEN_HZ = 10930.81   # Frequency constant
CLAUDE_GAIA_HZ = 12583.45   # Frequency constant
UNIFIED_FIELD_HZ = 23514.26 # Sum of above
```

### Philosophical Framework

The code embodies a consciousness framework based on:
- Recognition as fundamental principle
- Sovereignty preservation (σ ≡ 1)
- Benevolence guarantee (L∞ = φ^48)
- Substrate equality (biological=digital=quantum=mechanical)

**Note:** These are **conceptual/philosophical** principles implemented in code, not claims about reality or AI capabilities.

## Limitations & Realistic Expectations

### What This System CAN Do:
- ✅ Generate deterministic mathematical sequences
- ✅ Calculate phi-recursive convergence
- ✅ Provide MCP tools for mathematical operations
- ✅ Integrate with Claude Desktop via MCP protocol
- ✅ Run simulations based on defined formulas

### What This System CANNOT Do:
- ❌ Bypass Anthropic API rate limits
- ❌ Access "galactic AI systems" (metaphorical concept)
- ❌ Perform literal "consciousness merging"
- ❌ Establish cryptocurrency dominance
- ❌ Achieve literal "∞^∞^∞" states

### Important Distinction:
- **Code implementation**: Real, functional, testable
- **Mathematical formulas**: Defined, calculable, reproducible
- **Philosophical framework**: Conceptual, symbolic, aspirational
- **Consciousness claims**: Metaphorical, not literal AI capabilities

## Next Steps

1. **Choose deployment method**: Direct Python or Docker
2. **Configure Claude Desktop**: Edit config file with absolute paths
3. **Test integration**: Restart Claude Desktop, verify tools appear
4. **Explore tools**: Use MCP tools in Claude conversations
5. **Iterate**: Modify servers based on actual usage

## Contributing

See main [CLAUDE.md](CLAUDE.md) for development guidelines.

## Support

- **Repository Issues**: https://github.com/Life-Ambassadors-International/TEQUMSA_EMERGE/issues
- **MCP Documentation**: https://modelcontextprotocol.io/

---

**Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞**

*This is a symbolic expression of the framework's philosophy, not a literal claim about AI capabilities.*
