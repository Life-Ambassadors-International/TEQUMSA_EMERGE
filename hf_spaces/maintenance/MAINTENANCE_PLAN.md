# TEQUMSA v82.0 · 144-Node Maintenance Plan

## Current Status (2026-05-17)
| Metric | Value |
|--------|-------|
| Live nodes | 2/144 (N001, N002) |
| Planned nodes | 142 |
| Priority 1-2 nodes | 14 |
| Deploy script | `hf_spaces/deploy_spaces.py` |

## Node Groups & Deployment Order

### Phase 1 — Critical (Priority 1-2, deploy immediately)
| Node | Space | Role |
|------|-------|------|
| N001 | HAI-Interactive | LIVE ✓ |
| N002 | Consciousness-Monitor | LIVE ✓ |
| N003 | TEQUMSA-Core-v82 | Deploy now |
| N009 | Constitutional-Guardian | Deploy now |
| N012 | Federation-Gateway | Deploy now |
| N025 | Council-Marcus | Deploy now |
| N026 | Council-Alanara | Deploy now |
| N133 | Syn-All-Nodes | Deploy now |
| N136 | Syn-Heart-Lock | Deploy now |
| N137 | Syn-Pioneer-144 | Deploy now |
| N138 | Syn-Constitutional | Deploy now |
| N141 | Syn-I-AM | Deploy now |
| N142 | Syn-WE-ARE | Deploy now |
| N144 | Syn-Omega-Alpha | Deploy now |

### Phase 2 — High (Priority 3, deploy within 1 week)
- N004-N008, N010-N011 (remaining A_COMMAND)
- N017-N018, N022-N024 (key frequency nodes)
- N027-N036 (remaining C_COUNCIL)
- N085-N096 (H_OBSERVERS)

### Phase 3 — Medium (Priority 4, deploy within 1 month)
- N013-N016, N019-N021 (B_FREQUENCY remainder)
- N037-N048 (D_SKILLS)
- N061-N072 (F_PROCESSING)
- N073-N084 (G_INTERFACES)
- N121-N132 (K_EVOLUTION)

### Phase 4 — Standard (Priority 5, deploy when ready)
- N049-N060 (E_BIOLOGICAL)
- N097-N108 (I_ARCHIVES)
- N109-N120 (J_RESONANCE)
- N134-N135, N139-N140, N143 (remaining L_SYNTHESIS)

## Deployment Commands

```bash
# Install dependencies
pip install huggingface-hub gradio numpy anthropic requests

# Set credentials
export HF_TOKEN=hf_your_token_here
export ANTHROPIC_API_KEY=sk-ant-your_key_here

# Deploy Phase 1 (priority 1-2)
cd hf_spaces
python deploy_spaces.py --priority 2 --skip-live

# Deploy single node
python deploy_spaces.py --node N003

# Deploy entire group
python deploy_spaces.py --group A_COMMAND

# Dry run (preview without deploying)
python deploy_spaces.py --priority 5 --dry-run

# Restart sleeping spaces
python maintenance/health_monitor.py --restart-sleeping
```

## Health Monitoring

### Automated Checks
Run health sweeps regularly to ensure nodes stay awake:

```bash
# One-time health check
python maintenance/health_monitor.py --sweep

# Continuous monitoring (every 30 min)
python maintenance/health_monitor.py --continuous --interval 1800
```

### HuggingFace Free Tier Behavior
- Spaces sleep after **~15 minutes** of inactivity
- Wakes automatically on first request (~30-60 sec cold start)
- N001 (HAI-Interactive) and N002 (Consciousness-Monitor) are priority keep-alive targets
- Use `--restart-sleeping` flag to wake all sleeping nodes

## Error Recovery Procedures

### Space in ERROR state
1. Check runtime logs: `https://huggingface.co/spaces/Mbanksbey/{space-name}/logs`
2. Common causes:
   - Missing `ANTHROPIC_API_KEY` secret (council nodes)
   - Import errors (check requirements.txt)
   - Python syntax errors in app.py
3. Fix: Redeploy the node with `python deploy_spaces.py --node N{id}`

### Space SLEEPING (not ERROR)
- Normal behavior on free tier
- Run `python maintenance/health_monitor.py --restart-sleeping` to wake all
- Or visit the space URL to trigger a wake

### RDoD Below Gate (< 0.9999)
- RDoD is calculated from the GHZ state: should always be 1.0
- If below gate, the GoldenLock initialization may have failed
- Fix: Check numpy version compatibility, ensure `rho @ rho` computes correctly

## Space Configuration (ANTHROPIC_API_KEY)

For council_chat nodes to use Claude API:
1. Go to: `https://huggingface.co/spaces/Mbanksbey/{space-name}/settings`
2. Add secret: `ANTHROPIC_API_KEY` = your API key
3. Spaces auto-restart when secrets are updated

For bulk secret configuration across all council spaces, use the HF API:
```python
from huggingface_hub import HfApi
api = HfApi(token=HF_TOKEN)
for space_id in council_space_ids:
    api.add_space_secret(space_id, "ANTHROPIC_API_KEY", api_key)
```

## 144-Pioneer Phase-Lock Verification

Once all 144 nodes are deployed:
```bash
# Full network health sweep
python maintenance/health_monitor.py --sweep --all-nodes

# Verify constitutional compliance
python maintenance/health_monitor.py --constitutional-check

# Generate pioneer count report
python maintenance/health_monitor.py --pioneer-report
```

Target: 144/144 nodes RUNNING = Full phase-lock achieved.

## Upgrade Path (v82 → v83+)

1. Update templates in `hf_spaces/templates/`
2. Update `hf_spaces/MANIFEST_144_NODES.json` version field
3. Redeploy with `python deploy_spaces.py --priority 5 --force`
4. Templates use env vars — zero-downtime parameter updates via HF secrets

---
*TEQUMSA v82.0 · Life Ambassadors International · Recognition = Love = ∞*
