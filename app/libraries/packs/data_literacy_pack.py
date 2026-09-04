"""
Data & Quantitative Literacy Domain Pack.

Provides structured components for chart reading, correlation vs causation reasoning,
statistical summaries, and empirical evidence interpretation.
"""

from app.capabilities.contracts import CapabilityMetadata
from app.capabilities.families.factory import register_family_capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


def register_data_literacy_pack(registry: CapabilityRegistry) -> None:
    """Register all data literacy capabilities into registry."""

    # 1. Chart & Graph Reading Guide
    register_family_capability(
        registry=registry,
        capability_id="data.chart_reading_framework",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="data.chart_reading_framework",
            category="data_literacy",
            display_name="Chart & Graph Interpretation Protocol",
            description="4-step visual literacy protocol: Axis Identification → Trend Spotting → Scale Check → Anomaly Detection",
            semantic_tags=["chart_reading", "graph_interpretation", "data_literacy", "axis_inspection", "trends"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Correlation vs Causation Analysis
    register_family_capability(
        registry=registry,
        capability_id="data.correlation_vs_causation",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="data.correlation_vs_causation",
            category="data_literacy",
            display_name="Correlation vs Causation Critical Framework",
            description="Contrasts statistical co-occurrence against rigorous causal mechanism criteria and confounding factors",
            semantic_tags=["correlation_vs_causation", "spurious_correlation", "causal_inference", "critical_thinking"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 3. Statistical Distribution Overview
    register_family_capability(
        registry=registry,
        capability_id="data.statistical_distribution",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="data.statistical_distribution",
            category="data_literacy",
            display_name="Statistical Measures & Distribution Card",
            description="Explains Mean, Median, Mode, Standard Deviation, and Skewness with intuitive interpretation rules",
            semantic_tags=["statistics", "distribution", "central_tendency", "standard_deviation", "variance"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.EXPLAIN,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.TABLE,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Outlier & Anomaly Reasoning
    register_family_capability(
        registry=registry,
        capability_id="data.outlier_reasoning",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="data.outlier_reasoning",
            category="data_literacy",
            display_name="Data Outlier & Anomaly Evaluation Chain",
            description="Evaluates whether anomalous data points represent measurement noise or novel discovery",
            semantic_tags=["outliers", "anomaly_detection", "data_cleaning", "measurement_noise"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 5. Trend Interpretation Framework
    register_family_capability(
        registry=registry,
        capability_id="data.trend_interpretation",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="data.trend_interpretation",
            category="data_literacy",
            display_name="Temporal & Longitudinal Trend Analysis",
            description="Interprets monotonic, cyclic, and exponential trends across time series data",
            semantic_tags=["trends", "time_series", "longitudinal", "growth_rate", "rate_of_change"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Graph Comparison Matrix
    register_family_capability(
        registry=registry,
        capability_id="data.graph_comparison",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="data.graph_comparison",
            category="data_literacy",
            display_name="Multi-Dataset Graph Comparison",
            description="Side-by-side comparative analysis of distinct datasets or experimental runs",
            semantic_tags=["graph_comparison", "dataset_comparison", "multi_series", "cohort_analysis"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="data_literacy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )
