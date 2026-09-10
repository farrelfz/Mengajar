# PHASE 3B IMPLEMENTATION PLAN
## Failure Correlation & Causal Attribution Engine
### Universal Document Intelligence System V5

---

## 1. Executive Summary & Objective

Phase 3B implements a deterministic, explainable, evidence-driven **Failure Correlation & Causal Attribution Engine**.
The system answers:
- What failures are correlated?
- Which failures are merely symptoms vs upstream causes?
- What is the most plausible root cause?
- At which architectural layer does the defect originate?
- How confident is the causal attribution?
- What evidence supports the attribution?
- Is automatic repair safe to consider (repair readiness)?

**Strict Non-Goal**: Phase 3B MUST NOT execute automatic repairs. Causal intelligence and repair readiness assessment are established first; repair execution is strictly deferred to Phase 3C/3D.

---

## 2. Canonical Phase Roadmap

To eliminate historical phase naming ambiguity:

1. **Phase 3A**: Independent Physical Quality Inspection
2. **Phase 3A.1**: Forensic Architecture Audit
3. **Phase 3A.2**: Canonical Quality Intelligence Contract
4. **Phase 3B**: Failure Correlation & Causal Attribution *(Current Phase)*
5. **Phase 3C**: Repair Strategy & Repair Authority
6. **Phase 3D**: Transactional Repair Execution
7. **Phase 3E**: Unified Quality Decision Authority
8. **Phase 3F**: Cross-Artifact Calibration & Regression

---

## 3. Phase 3A.2 Hardening Scope

Before continuing with Phase 3B intelligence:
1. **Failure Scope Taxonomy Hardening**:
   - `LOCAL`: Isolated to 1 element or very small number of directly related elements ($\le 15\%$).
   - `CLUSTER`: Multiple related defects sharing strong spatial, structural, semantic, or lineage proximity.
   - `SYSTEMIC`: Distributed recurring defects affecting multiple locations ($20\% \le \text{ratio} < 50\%$).
   - `ARTIFACT_WIDE`: Document-global or majority-level failure ($\ge 50\%$), OR explicit semantic override `is_document_level == True` or matching global invariant failure codes (e.g. `SCIENTIFIC_CITATION_INVISIBLE`, `WORKSHEET_SPOILING_FAILURE`, `TRACEABILITY_BREAK`, `STYLE_SYSTEM_FAILURE`).
2. **Signal Lifecycle Hardening**:
   - Validated transition guards: Shortcut `NORMALIZED` $\to$ `CAUSAL_HYPOTHESIS` is permitted ONLY for isolated single-source deterministic defects (e.g. `RENDER_CRASH`, `EXECUTION_TIMEOUT`, `ASSET_MISSING`). Complex layout failures (`TEXT_TOO_SMALL`, `HIGH_DENSITY`, `ELEMENT_COLLISION`, `OVERFLOW_HIDDEN_CUTOFF`, `LAYOUT_MONOTONY`) must pass correlation and clustering.
3. **Test Accounting Hardening**:
   - Explicitly distinguish between phase-developed tests and regression suite counts in all documentation and metrics.

---

## 4. Architectural Component Design

```
+-------------------------------------------------------------------------------------------------+
|                                    PHASE 3B CAUSAL PIPELINE                                      |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   RAW QUALITY SIGNALS                                                                           |
|          │                                                                                      |
|          ▼                                                                                      |
|   1. NORMALIZATION & CONTEXT ENRICHMENT                                                         |
|      (QualityCorrelationContext: spatial, structural, semantic, lineage, stage)                 |
|          │                                                                                      |
|          ▼                                                                                      |
|   2. FAILURE CORRELATION ENGINE                                                                 |
|      (Indexed Candidate Pairing -> Multi-Dimensional Proximity Scoring)                         |
|          │                                                                                      |
|          ▼                                                                                      |
|   3. CORRELATION GRAPH & DETERMINISTIC CLUSTERING                                               |
|      (CorrelationGraph -> Connected Components -> FailureClusterBuilder)                        |
|          │                                                                                      |
|          ▼                                                                                      |
|   4. SYMPTOM VS CAUSE SEPARATION                                                                |
|      (FailureRole: PRIMARY_SYMPTOM, SECONDARY_SYMPTOM, POSSIBLE_CAUSE, ROOT_CAUSE_CANDIDATE)     |
|          │                                                                                      |
|          ▼                                                                                      |
|   5. CAUSAL RULE BASE & HYPOTHESIS GENERATION                                                   |
|      (CausalRule matching -> Upstream/Downstream Lineage Direction Validation)                  |
|          │                                                                                      |
|          ▼                                                                                      |
|   6. EVIDENCE SCORING & EXPLAINABLE CONFIDENCE                                                  |
|      (Explanatory Coverage, Evidence Strength, Lineage Consistency, Contradiction Penalty)      |
|          │                                                                                      |
|          ▼                                                                                      |
|   7. COMPETING HYPOTHESIS ANALYSIS & DECISION                                                   |
|      (Ambiguity Margin -> CausalDecision: CONFIRMED, LIKELY, MULTIPLE_PLAUSIBLE_CAUSES)         |
|          │                                                                                      |
|          ▼                                                                                      |
|   8. VALIDATOR ANOMALY DETECTION                                                                |
|      (Conservative check for conflicting inspector signals)                                     |
|          │                                                                                      |
|          ▼                                                                                      |
|   9. REPAIR READINESS ASSESSMENT (Contract Only - No Execution)                                |
|      (Blast Radius, Reversibility, Determinism -> Authority Recommendation)                     |
|          │                                                                                      |
|          ▼                                                                                      |
|  10. STRUCTURED DIAGNOSTIC OBSERVABILITY & REPORTING                                            |
|      (causal_analysis.json, causal_analysis.md: Observations vs Inferences vs Confirmed Causes) |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## 5. File Structure Plan

- `app/quality/causal/config.py`: Centralized configuration (weights, thresholds, ambiguity margin).
- `app/quality/causal/context.py`: `QualityCorrelationContext` model and context extractors.
- `app/quality/causal/correlation_graph.py`: `CorrelationEdge`, `CorrelationScoreBreakdown`, `CorrelationGraph`.
- `app/quality/causal/correlation_engine.py`: `FailureCorrelationEngine` with indexed pairing.
- `app/quality/causal/cluster_builder.py`: `FailureClusterBuilder` with deterministic graph clustering.
- `app/quality/causal/symptom_classifier.py`: `FailureRole` classifier (symptom vs cause).
- `app/quality/causal/causal_taxonomy.py`: `CausalArchitecturalLayer`, `RootCauseCategory`, `CausalDecision`.
- `app/quality/causal/causal_path.py`: `CausalPathNode`, `CausalPathEdge`, `CausalPath`.
- `app/quality/causal/rules.py`: `CausalRule`, rule catalog for all 4 artifact formats.
- `app/quality/causal/hypothesis_generator.py`: `CausalHypothesisGenerator` with lineage direction guards.
- `app/quality/causal/evidence_scorer.py`: `CausalEvidenceScorer` and confidence breakdown.
- `app/quality/causal/competing_analysis.py`: Competing hypothesis analyzer and ambiguity margin detector.
- `app/quality/causal/validator_anomaly.py`: `ValidatorAnomalyDetector`.
- `app/quality/causal/repair_readiness.py`: `RepairReadinessAssessor`.
- `app/quality/causal/causal_engine.py`: `MasterCausalEngine` coordinating the end-to-end flow.
- `app/quality/causal/causal_reporter.py`: Markdown and JSON forensic reports.

---

## 6. Test Plan

1. Correlation tests: Spatial, structural, semantic, lineage, failure pattern compatibility, determinism.
2. Clustering tests: Graph connected components, isolated signals, scope derivation, global invariants.
3. Causal tests: Multiple hypotheses generation, lineage validation, contradiction penalty, explainable path.
4. Validator anomaly tests: Conflicting inspector detection, false positive hypothesis generation.
5. Repair readiness tests: Authority recommendations, blast radius, no repair execution guarantee.
6. Cross-artifact tests: Presentation density chain, Handout hierarchy chain, Worksheet anti-inquiry chain, Scientific unsupported claim chain.
7. Golden fixture integration: End-to-end evaluation on `oobleck_experiment` and synthetic failure fixtures.
8. Regression tests: All existing quality and system test suites remain 100% green.
