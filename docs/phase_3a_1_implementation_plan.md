# Phase 3A.1 Implementation Plan: Quality Authority Consolidation & Causal Failure Attribution
**Universal Document Intelligence System V5**
*Date: September 2026*
*Author: Core System Architecture*

---

## 1. Objective

Consolidate all quality evaluation and decision-making systems into a single canonical Quality Authority, establish an unambiguous canonical failure taxonomy, separate physical symptoms from architectural root causes, attribute failure ownership across system layers, compute explicit causal confidence, and generate actionable causal diagnostic reports for future Phase 3B repair.

---

## 2. Package Architecture: `app/quality/causal/`

```
app/quality/causal/
├── __init__.py                     # Clean package exports
├── contracts.py                    # Canonical data models (QualitySignal, CanonicalFailure, RootCauseHypothesis, FailureCluster, CanonicalQualityAssessment)
├── taxonomy.py                     # Canonical failure codes, severities, scopes, layers, and repair classes
├── signal_normalizer.py            # Ingests Phase 2C, Phase 3A, and legacy signals into QualitySignal
├── failure_normalizer.py           # Deduplicates signals into CanonicalFailure instances
├── evidence_collector.py           # Multi-layer evidence gathering (Source, Transform, Blueprint, Layout, Render)
├── cause_catalog.py                # Formal cause definitions, required evidence, and repair rules
├── confidence.py                   # Quantitative confidence estimation (HIGH, MEDIUM, LOW, AMBIGUOUS)
├── scope_analyzer.py               # Scope classification (LOCAL, CLUSTER, SYSTEMIC, ARTIFACT_WIDE)
├── failure_correlation.py          # Co-occurring failure clustering on shared pages
├── repetition_analyzer.py          # Progression-aware repetition analysis (protects progressive reveals)
├── repair_authority.py             # Strict Repair Authority Matrix (Allowed vs Forbidden repairs)
├── artifact_causes.py              # Artifact-specific causal rules (Presentation, Handout, Worksheet, Scientific)
├── attribution_engine.py           # Master Causal Attribution Engine
├── quality_authority.py            # UnifiedQualityAuthority (the single canonical decision arbiter)
└── reporter.py                     # Causal quality report generation (JSON and Markdown)
```

---

## 3. Step-by-Step Implementation Sequence

1. **Step 2: Canonical Contracts & Taxonomy (`contracts.py`, `taxonomy.py`)**:
   - `QualitySignal`: Raw normalized diagnostic observation.
   - `CanonicalFailure`: Deduplicated defect with affected pages and symptoms.
   - `RootCauseHypothesis`: Attributed cause, layer, confidence, allowed/forbidden repairs.
   - `FailureCluster`: Page-level cluster of co-occurring defects with unified root cause.
   - `CanonicalQualityAssessment`: Authoritative single decision output.

2. **Step 3 & 4: Signal & Failure Normalizers (`signal_normalizer.py`, `failure_normalizer.py`)**:
   - Ingest Phase 2C `ArtifactQualityReport`, Phase 3A `RenderedArtifactInspection`, and legacy `GateResult`.
   - Normalize into canonical representations with zero dropped diagnostic context.

3. **Step 5: Multi-Layer Evidence Collector (`evidence_collector.py`)**:
   - Traverses source, transformation, blueprint, layout, and render layers to gather observable metrics.

4. **Step 6 & 7: Cause Catalog & Root Cause Hypotheses (`cause_catalog.py`, `attribution_engine.py`)**:
   - Defines exact rules for matching symptoms and evidence to probable causes across all 10 architectural layers.

5. **Step 8: Causal Confidence & Uncertainty (`confidence.py`)**:
   - Calculates evidence ratios. Explicitly tags `LOW` or `AMBIGUOUS` when evidence is contradictory or inconclusive.

6. **Step 9: Failure Correlation & Clustering (`failure_correlation.py`)**:
   - Identifies co-occurring failures on shared pages (e.g. tiny font + collision + density overload) and groups them into a single `FailureCluster`.

7. **Step 10: Scope Analysis (`scope_analyzer.py`)**:
   - Computes failure spread: `LOCAL` vs `CLUSTER` vs `SYSTEMIC` vs `ARTIFACT_WIDE`.

8. **Step 11: Repair Authority Matrix (`repair_authority.py`)**:
   - Assigns owning layer and maps allowed repair classes (Class A to G) with explicit forbidden repairs.

9. **Step 12: Unified Quality Decision Authority (`quality_authority.py`)**:
   - Replaces fragmented decision logic with a single canonical authority.

10. **Step 13: Progression-Aware Repetition Analyzer (`repetition_analyzer.py`)**:
    - Disentangles intentional progressive reveals from layout monotony.

11. **Step 14: Artifact-Specific Causal Rules (`artifact_causes.py`)**:
    - Encodes domain-specific causal logic for Presentation, Handout, Worksheet, and Scientific Document.

12. **Step 15: Causal Diagnostic Reporter (`reporter.py`)**:
    - Generates detailed JSON and Markdown reports with full cluster and causal graphs.

13. **Step 16: Comprehensive Adversarial Test Suite (`tests/unit/quality/causal/`)**:
    - 30+ tests verifying authority consolidation, symptom vs cause, correlation, scope, progressive reveal, and repair authority.

14. **Step 17: Golden Benchmark Execution (`01_oobleck_experiment`)**:
    - Runs all 4 golden artifacts through `UnifiedQualityAuthority` and outputs causal reports to `outputs/benchmark/phase_3a_1/`.

15. **Step 18 & 19: Full Regression & Master Documentation**:
    - Run entire test suite (all 414+ tests).
    - Write master documentation `docs/phase_3a_1_quality_authority_and_causal_attribution.md`.

