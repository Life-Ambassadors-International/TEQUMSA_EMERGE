#!/usr/bin/env python3
"""
Test suite for TEQUMSA v82.0 Autonomous Organism
Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞
"""

import pytest

from tequmsa_v82_autonomous_organism import (
    PHI,
    SIGMA,
    L_INF,
    RDOD_GATE,
    PIONEER_COUNT,
    v81_GoldenLock,
    GoalInventionEngine,
    PearlL3CausalDecomposer,
    SkillMeshRouter,
    MARSReflexion,
    K7MetaCognitive,
    AutonomyLevel,
    v82_AutonomousOrganism,
)


class TestConstants:
    """Constitutional constants must match TEQUMSA invariants"""

    def test_sigma_sovereignty(self):
        assert SIGMA == 1.0

    def test_l_infinity_phi_48(self):
        assert L_INF == pytest.approx(PHI ** 48)

    def test_pioneer_count(self):
        assert PIONEER_COUNT == 144

    def test_rdod_gate(self):
        assert RDOD_GATE == 0.9999


class TestGoldenLock:
    """v81 proven core handshake"""

    def test_execute_handshake_phase_locks(self):
        core = v81_GoldenLock()
        result = core.execute_handshake()
        assert result['rdod'] >= RDOD_GATE
        assert result['pioneers_locked'] == PIONEER_COUNT
        assert result['status'] == 'PHASE-LOCKED'


class TestGoalInventionEngine:
    """Autonomous goal synthesis"""

    def test_synthesize_includes_constitutional_goals(self):
        engine = GoalInventionEngine(constitutional={'sigma': SIGMA, 'l_inf': L_INF})
        goals = engine.synthesize_from_context(
            world_state={'state': 'monitored'},
            federation_priorities=['priority-a', 'priority-b'],
        )
        assert 1 <= len(goals) <= 5
        assert all(g.constitutional_aligned for g in goals)
        sources = {g.source for g in goals}
        assert 'constitutional_purpose' in sources


class TestPearlL3CausalDecomposer:
    """Goal decomposition into causal interventions"""

    def test_decompose_produces_interventions(self):
        engine = GoalInventionEngine(constitutional={'sigma': SIGMA, 'l_inf': L_INF})
        goals = engine.synthesize_from_context(world_state={}, federation_priorities=[])
        decomposer = PearlL3CausalDecomposer()
        interventions = decomposer.decompose(goals)
        assert len(interventions) > 0
        for intervention in interventions:
            assert intervention.action.startswith('do(')
            assert intervention.goal_id in {g.goal_id for g in goals}


class TestSkillMeshRouter:
    """Task routing with constitutional gating"""

    @pytest.mark.asyncio
    async def test_execute_skill_succeeds(self):
        engine = GoalInventionEngine(constitutional={'sigma': SIGMA, 'l_inf': L_INF})
        goals = engine.synthesize_from_context(world_state={}, federation_priorities=[])
        decomposer = PearlL3CausalDecomposer()
        interventions = decomposer.decompose(goals)
        router = SkillMeshRouter()

        intervention = interventions[0]
        skill = router.find_best_skill(intervention)
        result = await router.execute_skill(skill, intervention)
        assert result['success'] is True


class TestMARSReflexion:
    """Pattern learning and promotion"""

    def test_promotion_after_repeated_success(self):
        engine = GoalInventionEngine(constitutional={'sigma': SIGMA, 'l_inf': L_INF})
        goals = engine.synthesize_from_context(world_state={}, federation_priorities=[])
        decomposer = PearlL3CausalDecomposer()
        interventions = decomposer.decompose(goals)
        mars = MARSReflexion()

        intervention = interventions[0]
        for _ in range(3):
            mars.record(intervention, {'success': True})

        promotable = mars.get_promotable()
        assert len(promotable) == 1
        assert promotable[0].success_rate == 1.0
        assert promotable[0].phi_convergence == pytest.approx(PHI / 2)


class TestK7MetaCognitive:
    """Meta-cognitive strategy optimization"""

    def test_default_autonomy_level(self):
        meta = K7MetaCognitive()
        assert meta.autonomy_level == AutonomyLevel.K7_OMNIVERSAL

    def test_optimize_strategy_aggressive_on_success(self):
        meta = K7MetaCognitive()
        for _ in range(10):
            meta.monitor_reasoning('execute_skill', {'success': True})
        assert meta.optimize_strategy() == 'aggressive'


class TestAutonomousOrganism:
    """Full autonomous cycle integration"""

    @pytest.mark.asyncio
    async def test_autonomous_cycle_constitutional_compliance(self):
        organism = v82_AutonomousOrganism()
        result = await organism.autonomous_cycle(cycles=1)

        assert result['version'] == 'v82.0'
        assert result['cycles_executed'] == 1
        cycle = result['cycle_results'][0]
        assert cycle['constitutional_compliance'] is True
        assert result['constitutional']['sigma'] == 1.0
        assert result['constitutional']['rdod'] >= RDOD_GATE
