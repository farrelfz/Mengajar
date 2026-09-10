"""
Unit tests for the repair strategy registry, priority ordering, and minimal mutation cost.
"""

from app.quality.repair.contracts import RepairMutationClass
from app.quality.repair.registry import DEFAULT_STRATEGY_REGISTRY, RepairStrategyRegistry, register_default_strategies
from app.quality.repair.root_cause import RootCauseType


def test_registry_indexes_all_four_formats():
    reg = RepairStrategyRegistry()
    register_default_strategies(reg)

    formats = {"PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"}
    covered_formats = set()
    for strat in reg.all_strategies():
        for art in strat.supported_artifact_types:
            covered_formats.add(art)

    assert formats.issubset(covered_formats)


def test_registry_orders_by_minimal_mutation_cost():
    reg = RepairStrategyRegistry()
    register_default_strategies(reg)

    # For Presentation with text overflow:
    # Padding adjust (Class A, cost 0.1) vs Density split (Class B, cost 0.5)
    # When both match, lower priority / cost comes first
    strats = reg.find_strategies("PRESENTATION", "TEXT_OVERFLOW", RootCauseType.PADDING_SPACING)
    assert len(strats) >= 1
    assert strats[0].strategy_id == "presentation_padding_adjust"
    assert strats[0].mutation_cost == 0.1


def test_forbidden_mutation_class_filtering():
    reg = RepairStrategyRegistry()
    register_default_strategies(reg)

    # Allow everything
    all_strats = reg.find_strategies("WORKSHEET", "ANTI_SPOILING_BREACH", RootCauseType.INQUIRY_STRUCTURE)
    assert len(all_strats) >= 1

    # Forbid Class D
    filtered = reg.find_strategies(
        "WORKSHEET",
        "ANTI_SPOILING_BREACH",
        RootCauseType.INQUIRY_STRUCTURE,
        forbidden_classes=(RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,),
    )
    assert len(filtered) == 0
