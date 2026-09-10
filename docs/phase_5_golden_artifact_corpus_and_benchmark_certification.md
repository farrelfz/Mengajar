# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 5 — GOLDEN ARTIFACT CORPUS & BENCHMARK CERTIFICATION
# ARCHITECTURAL SPECIFICATION & OPERATIONAL GUIDE

---

## 1. Executive Summary & Purpose
The Universal Document Intelligence System V5 synthesizes raw educational content into four fundamentally distinct formats:
1. **PRESENTATION** (16:9 projection, cognitive load control, progressive visual disclosure).
2. **HANDOUT** (A4 continuous independent reading, 5-layer explanatory depth).
3. **WORKSHEET / LKS** (A4 guided discovery, strict anti-spoiling, inquiry dependency).
4. **SCIENTIFIC DOCUMENT / KTI** (Formal BAB hierarchy, Claim-Evidence-Reasoning, zero fabrication).

Phase 5 implements a **governed historical evaluation memory** capable of determining whether the generator is improving, remaining stable, or regressing over time across all four artifact targets.

---

## 2. Core Architectural Invariants
1. **UnifiedQualityAuthority Sovereign Level-0 Authority**: UQA remains the sole authority for export decisions. The benchmark system observes outputs and certifies longitudinal generator quality; it never grants or overrides export approval.
2. **Observational Non-Interference**: Benchmark evaluations never mutate production artifacts, blueprints, or repair operator registries.
3. **Immutable Scientific References**: Golden references and historical baselines cannot be silently rewritten. All transitions are recorded in an immutable DAG with SHA-256 digests.
4. **Anti-Benchmark-Laundering Enforcement**: Lowering baseline score targets or removing difficult fixtures without substantive justification and governed classification (`POLICY_EVOLUTION`, `LEGITIMATE_CORRECTION`) triggers `BENCHMARK_LAUNDERING_ATTEMPT`.
5. **Anti-Leakage Split Isolation**: Unseen generalization and adversarial fixtures execute under `BenchmarkLeakageGuard`, preventing mutation of persistent adaptive operator memory.
6. **100% Deterministic Offline Replay**: Benchmarking requires zero external network connections or runtime LLM calls.

---

## 3. Architecture Overview & Information Flow

```
SOURCE FIXTURE (e.g. oobleck_experiment.md)
      │
      ▼
CORPUS SPLIT MANAGER (TRAIN / VAL / UNSEEN / ADVERSARIAL)
      │
      ▼
PRODUCTION ORCHESTRATOR ──► UNIFIED QUALITY AUTHORITY (Level-0 Export Decision)
      │                                   │
      ▼                                   ▼
GENERATED ARTIFACT ───────────────► BENCHMARK DIMENSION EXTRACTOR
                                          │
                                          ▼
                               MULTI-DIMENSION COMPARISON
                               ├── Semantic Fidelity
                               ├── Structural Integrity
                               ├── Visual Density & Pacing
                               ├── Pedagogical Inquiry / Explanatory Flow
                               └── Scientific CER & Citation Integrity
                                          │
                                          ▼
                         CROSS-ARTIFACT DIVERGENCE BENCHMARK
                         (Ensures High Overlap != Low Divergence)
                                          │
                                          ▼
                              REGRESSION DETECTOR
                              (Dimension-Aware Noise Tolerances)
                                          │
                                          ▼
                              CERTIFICATION ENGINE
                              (Policy Thresholds & Invariant Gates)
                                          │
                                          ▼
                              CERTIFICATION EXPLAINER
                              (Causal Narrative: Why Certified / Regressed)
                                          │
                                          ▼
                              GENERATOR HEALTH MODEL
                              (Longitudinal Generator Stability Tracking)
```

---

## 4. Multi-Dimensional Benchmark Model
Benchmark evaluations preserve dimensional granularity across 12 orthogonal dimensions:
- `SEMANTIC_FIDELITY`: Concept coverage and conceptual relationship preservation.
- `FACTUAL_GROUNDING`: Grounding in source manifest; absence of fabricated assertions.
- `STRUCTURAL_INTEGRITY`: Heading tree compliance, block ordering, and visual balance.
- `PEDAGOGICAL_FIT`: Inquiry arc sequence, anti-spoiling integrity, and scaffolding.
- `ARTIFACT_DIFFERENTIATION`: Distinction from other formats; resistance to collapse.
- `VISUAL_QUALITY`: Typography readability, visual density, and collision freedom.
- `RENDERED_PHYSICAL_QUALITY`: UQA Level-0 physical print/render scores.
- `TRACEABILITY`: Direct linkage of claims, steps, and formulas to source knowledge units.
- `SAFETY_INVARIANTS`: Binary hard invariants (e.g. `no_answer_leak`, `no_fabricated_claims`).
- `FORMAT_SPECIFIC_RIGOR`: Format-unique criteria (e.g. 5-layer explanation in handouts).
- `REPAIR_STABILITY`: Resistance to mutation drift during repair cycles.
- `CROSS_VERSION_REGRESSION`: Quantitative longitudinal change relative to baselines.

---

## 5. Artifact-Specific Golden Profiles

### A. Presentation
- Pacing: Progressive disclosure; single dominant message per slide.
- Cognitive Load: Target $\le 0.55$; no wall-of-text ($>75$ words/card is penalized).
- Anti-Collapse: Must not function as continuous reading prose.

### B. Handout
- Comprehension: 100% self-explanatory without teacher intervention.
- 5-Layer Explanatory Structure: Intuition $\rightarrow$ Formalization $\rightarrow$ Mechanism $\rightarrow$ Example $\rightarrow$ Application.
- Anti-Collapse: Rejects bullet-point fragmentation; mandates narrative continuity.

### C. Worksheet / LKS
- Inquiry Sequence: Phenomenon $\rightarrow$ Prediction $\rightarrow$ Investigation $\rightarrow$ Analysis $\rightarrow$ Reflection.
- Hard Invariant: `WITHHOLD_EXPLANATION = TRUE`. Premature revelation of discovery conclusions triggers `ANSWER_LEAK`.
- Anti-Collapse: Rejects repetitive factual recall items (`QUIZ_COLLAPSE`).

### D. Scientific Document / KTI
- Formal Structure: BAB I through BAB V academic architecture.
- CER Discipline: Claim $\rightarrow$ Evidence $\rightarrow$ Reasoning with declared evidence directness.
- Hard Invariants: `ZERO FABRICATED CITATIONS`, `ZERO UNSUPPORTED CLAIMS`.

---

## 6. Anti-Overfitting & Generalization Assurance
- `OverfittingSignalAnalyzer` (`app/benchmarking/overfitting.py`) evaluates the gap between known training fixtures and unseen generalization fixtures.
- Gaps $> 0.15$ raise `OVERFITTING_SUSPECTED`.
- `BenchmarkLeakageGuard` enforces zero memory modification when executing unseen fixtures.

---

## 7. Operational Usage: Replay CLI Harness
Run the deterministic replay harness across the Golden Corpus:
```bash
# Replay full corpus
.venv/bin/python3 scripts/replay_golden_corpus.py --full

# Replay specific case
.venv/bin/python3 scripts/replay_golden_corpus.py --case GOLDEN_OOBLECK

# Replay specific artifact format
.venv/bin/python3 scripts/replay_golden_corpus.py --artifact-type WORKSHEET
```

Deliverables generated:
- `output/benchmark_reports/benchmark_evaluation.json`: Full machine-readable diagnostic schema.
- `output/benchmark_reports/benchmark_evaluation.md`: Human-readable certification matrix and causal narratives.
