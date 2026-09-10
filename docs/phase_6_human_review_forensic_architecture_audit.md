# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 6.0 — FORENSIC ARCHITECTURE AUDIT REPORT
## HUMAN-IN-THE-LOOP REVIEW STUDIO & EXPERT DECISION GOVERNANCE

---

## 1. Executive Summary

This forensic architecture audit establishes the operational, governance, and contractual foundations for **Phase 6: Human-in-the-Loop Review Studio & Expert Decision Governance** within the *Universal Document Intelligence System V5*.

Prior architectural phases have established a high-rigor, deterministic, and autonomous generation, evaluation, repair, and benchmark certification pipeline:
- **Phase 3A**: `UnifiedQualityAuthority` (sovereign Level-0 quality evaluation across semantic, fidelity, artifact, and rendered domains).
- **Phase 3B / 3C / 3D**: `RepairTransactionManager`, `MinimalInterventionRepairPlanner`, `RepairSafetyInvariants`, and `ProductionOrchestrator` (autonomous targeted repair and vector convergence).
- **Phase 4.1**: Hardened Canonical Blueprint generation and differentiation contracts.
- **Phase 5**: `GoldenCorpusRegistry`, `CertificationEngine`, `RegressionDetector`, and `AntiLaunderingGuard`.

Across this landscape, human intervention cannot simply be an unconstrained "admin dashboard" or a web frontend that injects arbitrary edits. If a human reviewer were permitted to unilaterally click "Force Export", disable safety invariants, synthesize citations, reveal worksheet answer keys, or silently mutate benchmark baselines, the mathematical and empirical guarantees established in Phases 3, 4, and 5 would be nullified.

Therefore, the **Human-in-the-Loop Review Studio** is designed as a **strictly bounded context (`app/review/`)** governed by typed contracts, mathematical safety invariants, calibration engines, and immutable provenance ledgers. Human review operates as an **epistemic partner and governance layer**, providing:
1. Ground-truth defect confirmation or dispute.
2. Root-cause hypothesis correction and disambiguation.
3. Constrained, declarative repair directives dispatched through the existing `RepairSafetyInvariants` gateway.
4. Governed Golden Corpus candidate proposals validated through the `AntiLaunderingGuard`.

This report provides the exhaustive forensic analysis of the repository's existing contracts, state machines, evidence channels, and persistence topology, followed by a formal 12-phase implementation blueprint.

---

## 2. Repository Topology

The repository contains an established, modular architecture spanning intelligence, quality evaluation, repair actuation, orchestration, and benchmarking:

```text
app/
├── benchmarking/
│   ├── certification/           # CertificationEngine, CertificationPolicy, RegressionDetector
│   ├── comparison/              # Visual, semantic, structural, and artifact-specific comparators
│   ├── anti_laundering.py       # Active anti-laundering rules and validation
│   ├── contracts.py             # BenchmarkRun, BenchmarkResult, BenchmarkMetrics
│   ├── corpus_registry.py       # BenchmarkCorpusRegistry
│   ├── divergence.py            # CrossArtifactDivergenceAnalyzer
│   ├── golden_contracts.py      # GoldenArtifactReference, BenchmarkEvaluation, CertificationDecision
│   ├── golden_registry.py       # GoldenCorpusRegistry, GoldenCorpusVersionManager
│   ├── governance.py            # AntiLaunderingGuard, BaselineMutationRecord
│   ├── leakage_guard.py         # DataLeakageGuard (split protection)
│   ├── overfitting.py           # OverfittingDetector
│   ├── replay_harness.py        # BenchmarkReplayHarness
│   └── statistical_honesty.py   # StatisticalHonestyGuard
├── intelligence/
│   ├── blueprint_validation/    # Hardened Pydantic contracts & anti-pattern detectors (Phase 4.1)
│   ├── transformation/          # Blueprints, differentiation validator, traceability engine
│   └── pipeline/                # Source manifest parser & knowledge unit extraction
├── orchestration/
│   ├── decision_router.py       # QualityDecisionRouter (routes UQA decisions deterministically)
│   ├── escalation_router.py     # RepairEscalationRouter (R0-R5 architectural layers)
│   ├── export_gate.py           # AuthorizedExportGate (enforces zero-bypass export)
│   ├── failure_reporter.py      # ConvergenceFailureReporter (convergence_failure_report.md)
│   ├── forensics_exporter.py    # Complete run forensic artifacts
│   ├── production_context.py    # ArtifactProductionContext
│   ├── production_orchestrator.py # ProductionOrchestrator
│   └── production_state.py      # ProductionState enum & ProductionStateMachine
├── quality/
│   ├── authority/               # UnifiedQualityAuthority, decision_engine, master_authority
│   ├── contracts/               # QualityFinding, QualitySignal, QualityProvenanceGraph, ExportDecision
│   ├── causal/                  # Causal engine, hypothesis generator, symptom classifier
│   ├── repair/                  # RepairTransactionManager, RepairSafetyInvariants, planner
│   └── artifact_fidelity/       # Format-specific fidelity evaluators
└── renderers/                   # PlaywrightRenderer, PDF/HTML generation
```

### Proposed Domain Location (Question A)
The Human Review domain belongs at:
```text
app/review/
```
It is a sibling bounded context to `app/quality/`, `app/orchestration/`, and `app/benchmarking/`. 

**Architectural Rationale:**
- Placing review inside `app/quality/` would violate the separation between Level-0 objective automated evaluation and Level-1 subjective human appraisal.
- Placing review inside `app/orchestration/` would tangle queue management and reviewer workflows with execution pipeline state machines.
- Placing review inside a separate web repository or UI tier would orphan the domain models, leading to duplicate validation logic and unsafe schema drift.
- A dedicated `app/review/` domain encapsulates review contracts, queues, safety gateways, calibration, and consensus logic, depending on `app/quality/` and `app/orchestration/` strictly via typed contracts and adapters.

---

## 3. Existing Authority Map

The system enforces a strict hierarchy of authority. Phase 6 preserves this topology without inversion:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 0: Sovereign Mathematical & Physical Evaluation                  │
│ - UnifiedQualityAuthority (QualityDomain scores, hard blockers)        │
│ - RepairSafetyInvariants (Non-negotiable drift & format constraints)    │
│ - AntiLaunderingGuard (Strict baseline descent prohibition)            │
│ - AuthorizedExportGate (Physical export verification)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Emits Unresolved / Critical States
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: Governed Human-in-the-Loop Review Studio                      │
│ - Expert Review Decision (Confirm/Dispute finding, clarify intent)     │
│ - Root-Cause Adjudication (Disambiguate competing hypotheses)          │
│ - Constrained Repair Directive (Declarative guidance, bounded scope)   │
│ - Benchmark Candidate Proposal (Nominate edge cases to Golden Corpus)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Passes Through Safety Gateways
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: Execution & Actuation Subsystems                              │
│ - MinimalInterventionRepairPlanner (Executes within approved scopes)   │
│ - GoldenCorpusVersionManager (Applies versioned corpus updates)        │
│ - ProductionPipeline (Replays execution from designated stage)         │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Invariant**: Level 1 (Human Review) NEVER overrides Level 0. Human decisions are inputs to Level 2 execution, but all resulting artifacts must re-pass Level 0 verification before export.

---

## 4. Review Trigger Sources (Question B)

Forensic audit of existing production, repair, and benchmark modules identifies four distinct trigger sources that generate review cases:

### 1. Production Quality Triggers
- **Trigger A.1**: `ProductionState.MANUAL_REVIEW_REQUIRED` emitted by `QualityDecisionRouter.route_decision()` when `UnifiedQualityReport.decision == ExportDecision.MANUAL_REVIEW_REQUIRED`.
- **Trigger A.2**: `ProductionState.BLOCKED` when an unrepairable hard blocker is encountered.
- **Trigger A.3**: `ConvergenceFailureReporter` emission: When `ProductionOrchestrator` exhausts its mutation budget (`MutationBudgetTracker`), detects vector stagnation (`FailurePatternType.OSCILLATING_MUTATIONS`, `STAGNANT_LOW_IMPACT`), or encounters zero-effect repairs, generating `convergence_failure_report.md`.

### 2. Benchmark Certification Triggers
- **Trigger B.1**: `CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED` issued by `CertificationPolicy.evaluate()`.
- **Trigger B.2**: `CertificationDecision.BENCHMARK_REGRESSION` when `RegressionDetector.detect()` identifies statistical performance loss on a golden case.
- **Trigger B.3**: `CertificationDecision.BENCHMARK_INSUFFICIENT` when coverage or sample size fails statistical validity.

### 3. Repair Actuation Triggers
- **Trigger C.1**: Self-disqualification of all available repair strategies in `StrategySelfDisqualification`.
- **Trigger C.2**: Invariant rejection: When a candidate repair plan violates `RepairSafetyInvariants.evaluate_all()` (e.g., drift score exceeds threshold, citation dropped, or worksheet answer leaked).
- **Trigger C.3**: Escalation layer mismatch: When root cause attribution points to `LEVEL_R5_SOURCE_INTELLIGENCE` or `LEVEL_R4_SEMANTIC_TRANSFORMATION` but autonomous repair is locked to lower levels.

### 4. Blueprint & Divergence Triggers
- **Trigger D.1**: `CrossArtifactDivergenceReport.collapse_warning` emitted by `CrossArtifactDivergenceAnalyzer` when structural differentiation drops below acceptable distance.
- **Trigger D.2**: `BlueprintValidationReport.is_valid == False` containing `hard_invariant_violations` that the autonomous pipeline cannot resolve.

---

## 5. Review Case Lifecycle Analysis (Question L & C)

### Production State Machine Discovery
Forensic examination of `app/orchestration/production_state.py` reveals:
```python
# Terminal states have no further transitions (immutable end)
ProductionState.EXPORTED: set(),
ProductionState.MANUAL_REVIEW_REQUIRED: set(),
ProductionState.BLOCKED: set(),
ProductionState.FAILED: set(),
ProductionState.CANCELLED: set(),
```
And the explicit guard:
> *"Artifacts flagged for manual review cannot be repaired autonomously."*

This confirms that within `ProductionStateMachine`, `MANUAL_REVIEW_REQUIRED` is an **immutable terminal state** for that autonomous execution run. 

### The Review State Machine (`ReviewStateMachine`)
Because `ProductionStateMachine` cannot and should not be modified, the lifecycle of manual review must be managed by an independent `ReviewStateMachine` within `app/review/`:

```text
  [ DISCOVERED ]
        │
        ▼
   [ QUEUED ] ──────────────► [ DISMISSED / FP ]
        │
        ▼
   [ ASSIGNED ]
        │
        ▼
  [ IN_REVIEW ]
        │
        ▼
[ DECISION_SUBMITTED ]
        │
        ▼
 [ CONSENSUS_CHECK ]
   ├── (Consensus Reached) ───────► [ DIRECTIVE_PENDING ] ──► [ DISPATCHED_TO_REPAIR ]
   ├── (Disagreement Detected) ──► [ ADJUDICATION_REQUIRED ] ──► [ ADJUDICATED ]
   └── (Pure Feedback / Golden) ──► [ PROPOSED_TO_GOLDEN ] ──► [ RESOLVED ]
```

When a repair directive is validated and dispatched, a new, governed replay/repair job is initialized via `ProductionOrchestrator.replay_with_directive()`, preserving the original job's terminal state record for full auditability.

---

## 6. Artifact Lineage Availability (Question D)

The system already maintains rich lineage across three primary provenance graphs:

1. **Quality Lineage (`app/quality/contracts/provenance.py`)**:
   - `QualityProvenanceGraph`: Maps `Decision -> Finding -> Signal -> Evaluator -> Raw Measurement -> Element Bounding Box`.
   - Methods `trace_decision()` and `trace_finding(finding_id)` return the exact chain of causality.

2. **Transformation Lineage (`app/intelligence/transformation/traceability.py`)**:
   - `TransformationTraceabilityEngine`: Maps `Source Knowledge Unit ID -> Transformation Step -> Blueprint Section -> Rendered Component`.

3. **Repair History Lineage (`app/orchestration/production_context.py` & `app/quality/repair/transaction.py`)**:
   - `context.repair_history`: Sequence of `RepairTransactionRecord` objects capturing `before_state_hash`, `after_state_hash`, `selected_strategy`, `mutation_scope`, `quality_before`, `quality_after`, and `drift_score`.

4. **Benchmark Lineage (`app/benchmarking/golden_contracts.py`)**:
   - `BenchmarkEvaluation.reproducibility_metadata`: Captures git commit, environment hash, input digest, and corpus version.

**Architectural Decision**: Phase 6 does NOT create a new lineage database. It implements a read-only adapter `ReviewLineageAdapter` that aggregates these existing structures into a unified, reviewer-facing timeline.

---

## 7. Finding Identity Analysis (Question E)

In `app/quality/contracts/findings.py`, defects are canonically modeled as:
```python
class QualityFinding(BaseModel):
    finding_id: str
    failure_code: str
    domain: QualityDomain
    dimension: Any
    severity: SignalSeverity
    artifact_type: str
    message: str
    causal_hypothesis: Optional[str]
    affected_pages: Tuple[int, ...]
    affected_elements: Tuple[str, ...]
    affected_section: Optional[str]
    repairability: bool
    repair_class: str
    evidence_refs: Tuple[str, ...]
    originating_signal_ids: Tuple[str, ...]
    recommendation: str
    score_impact: float
    confidence: float
```

### Review Identity Requirements
When human reviewers inspect findings, the review system must bind to `finding_id`. Furthermore, because autonomous mutations may shift line numbers or generate new findings in subsequent iterations, the review contract must track:
- `finding_id`: The immutable UUID assigned during evaluation.
- `defect_fingerprint`: SHA-256 digest of `(failure_code, affected_section, affected_elements, dimension)` to track persistent defects across repair attempts.
- `status`: `ACTIVE`, `DISPUTED`, `CONFIRMED_DEFECT`, `RESOLVED`, `FALSE_POSITIVE`.

---

## 8. Evidence Availability Matrix (Question F)

A human reviewer must be presented with verified, multi-modal evidence before making a determination. The existing system provides rich evidence across four distinct channels:

| Evidence Channel | Source Component | Available Data | Human Presentation |
|---|---|---|---|
| **Render Evidence** | `output_dir/`, `PlaywrightRenderer` | Rendered PDF, PNG page previews, DOM snapshots | Side-by-side visual diff, bounding box overlays |
| **Geometry Evidence** | `PyMuPDF`, `DOM_INSPECTION` | Bounding boxes `(x0, y0, x1, y1)`, text clipping metrics, element overlap ratios | Visual defect box highlighted on page/slide |
| **Semantic Evidence** | `UniversalKnowledgeManifest`, `blueprints.py` | Source knowledge unit text, blueprint AST, uncertainty tags | Claim-to-source traceability viewer, knowledge unit alignment |
| **Repair Evidence** | `RepairTransactionRecord`, `ArtifactDriftReport` | Blueprint AST diff, strategy cost, drift vector, rejected strategies | Before/after structural diff, blast radius summary |
| **Benchmark Evidence** | `BenchmarkEvaluation`, `RegressionDetector` | Normalized score deltas, historical baseline comparison, radar chart vectors | Longitudinal regression curves, golden case diff |

---

## 9. Human Decision Taxonomy (Question G)

Human review decisions must be strictly categorized into canonical enumerations. Arbitrary or unclassified text notes cannot drive system behavior:

```python
class ExpertDecisionType(str, Enum):
    # Finding Adjudication
    CONFIRM_DEFECT = "CONFIRM_DEFECT"
    DISPUTE_FALSE_POSITIVE = "DISPUTE_FALSE_POSITIVE"
    IDENTIFY_FALSE_NEGATIVE = "IDENTIFY_FALSE_NEGATIVE"
    
    # Causal & Diagnostic Adjudication
    CONFIRM_ROOT_CAUSE = "CONFIRM_ROOT_CAUSE"
    CORRECT_ROOT_CAUSE = "CORRECT_ROOT_CAUSE"
    
    # Action Directives
    APPROVE_REPAIR_PLAN = "APPROVE_REPAIR_PLAN"
    DIRECT_TARGETED_REPAIR = "DIRECT_TARGETED_REPAIR"
    ESCALATE_TO_SPECIALIST = "ESCALATE_TO_SPECIALIST"
    REJECT_AND_TERMINATE = "REJECT_AND_TERMINATE"
    
    # Benchmark Governance
    PROPOSE_GOLDEN_CANDIDATE = "PROPOSE_GOLDEN_CANDIDATE"
    REJECT_BENCHMARK_PROPOSAL = "REJECT_BENCHMARK_PROPOSAL"
    FLAG_BENCHMARK_DEPRECATION = "FLAG_BENCHMARK_DEPRECATION"
```

Each decision requires a mandatory `rationale` (min 20 characters), reference to specific evidence IDs, and a cryptographically verifiable reviewer identity.

---

## 10. Directive Safety Boundary (Question H)

Human reviewers may issue repair directives (e.g., instructing the system to split a slide, rebalance handout density, or re-verify a citation). However, human directives **must pass through the `DirectiveSafetyValidator`** before reaching the `RepairTransactionManager`.

### Forbidden Human Directives (Hard Blockers):
1. **Force Export (`force_export=True`)**: Bypassing `UnifiedQualityAuthority` hard blockers or minimum quality thresholds is strictly forbidden.
2. **Safety Invariant Disable (`disable_safety_invariants=True`)**: Reviewers cannot suspend `RepairSafetyInvariants`.
3. **Anti-Spoiling Override (`reveal_answers=True`)**: Reviewers cannot force question solutions into student worksheet sections.
4. **Fabrication Override (`accept_unsupported_citation=True`)**: Reviewers cannot certify claims that have zero source manifest backing.
5. **Direct Baseline Lowering (`lower_threshold=True`)**: Reviewers cannot unilaterally reduce golden corpus score baselines to make a test pass.

Directives that violate any of these rules trigger an immediate `IllegalDirectiveException`, and the action is rejected and logged.

---

## 11. Review State Machine Analysis (Question L)

The `ReviewStateMachine` governs the transition of review cases independently of the production pipeline.

```text
State Transitions:
DISCOVERED       ──► QUEUED
QUEUED           ──► ASSIGNED, DISMISSED
ASSIGNED         ──► IN_REVIEW, QUEUED (on timeout)
IN_REVIEW        ──► DECISION_SUBMITTED, ESCALATED
DECISION_SUBMITTED ──► CONSENSUS_CHECK
CONSENSUS_CHECK  ──► DIRECTIVE_PENDING (unanimous/majority)
                 ──► ADJUDICATION_REQUIRED (high variance)
                 ──► RESOLVED (no action needed)
DIRECTIVE_PENDING ──► DISPATCHED_TO_REPAIR, REJECTED_BY_SAFETY_GATE
ADJUDICATION_REQUIRED ──► ADJUDICATED (senior expert decision)
DISPATCHED_TO_REPAIR ──► RESOLVED (upon successful verified replay)
```

**State Machine Invariants**:
- All state transitions emit immutable `ReviewStateTransitionRecord` entries.
- Cases cannot transition to `RESOLVED` while an active `DIRECTIVE_PENDING` remains undispatched.
- A case cannot reach `DISPATCHED_TO_REPAIR` without a cryptographic signature from `DirectiveSafetyValidator`.

---

## 12. Disagreement Architecture (Question I)

When high-stakes documents (e.g., scientific papers or certification benchmarks) are reviewed by multiple human experts, opinions may diverge. The system implements a deterministic `DisagreementAnalyzer`:

### Disagreement Dimensions:
1. **Decision Divergence**: One reviewer selects `CONFIRM_DEFECT` while another selects `DISPUTE_FALSE_POSITIVE`.
2. **Severity Divergence**: One reviewer rates a defect as `INFO` while another rates it `BLOCKING`.
3. **Root-Cause Divergence**: Disagreement on whether a layout failure is caused by font styling (`LEVEL_R0`) or structural excess (`LEVEL_R3`).

### Resolution Protocol:
- If Inter-Annotator Agreement (Cohen's Kappa / Fleiss' Kappa) is $\ge 0.80$, the system adopts the consensus decision.
- If agreement is $< 0.80$, or if any single reviewer flags a `BLOCKING` safety invariant violation, the case is automatically transitioned to `ADJUDICATION_REQUIRED`.
- Adjudication must be performed by a designated `SeniorAdjudicator`, whose decision is recorded alongside the original conflicting votes for transparency.

---

## 13. Reviewer Calibration Architecture (Question J)

To prevent reviewer drift, fatigue, or subjective bias from corrupting document intelligence standards, the system includes an empirical `ReviewerCalibrationEngine`:

### Calibration Mechanisms:
1. **Blind Golden Benchmark Insertion**: The queue periodically interleaves known Golden Corpus artifacts (both certified perfect documents and seeded adversarial failures) without alerting the reviewer.
2. **Consistency Scoring**: The reviewer's determinations on golden cases are measured against canonical labels across precision, recall, and false positive attribution.
3. **Calibration Metrics**:
   - `LeniencyBias`: Tendency to overlook minor/major defects.
   - `HarshnessBias`: Tendency to flag false positives on conformant documents.
   - `DomainSpecialization`: Tracked per artifact type (`PRESENTATION`, `HANDOUT`, `WORKSHEET`, `SCIENTIFIC_DOCUMENT`).
4. **Calibration Gating**: Reviewers whose rolling calibration score drops below bash.85$ are restricted to non-blocking review queues and cannot act as solo adjudicators until recalibrated.

---

## 14. Review Provenance Integration (Question K)

Every human action, comment, decision, and directive must be recorded in an immutable ledger. 

### `ReviewProvenanceRecord` Contract:
```python
class ReviewProvenanceRecord(BaseModel):
    record_id: str
    case_id: str
    artifact_id: str
    artifact_sha256: str
    reviewer_id: str
    reviewer_calibration_score: float
    decision: ExpertDecisionType
    directive: Optional[Dict[str, Any]]
    evidence_ids_referenced: Tuple[str, ...]
    parent_finding_id: Optional[str]
    timestamp: float
    signature: str  # Cryptographic hash of record content + reviewer secret/salt
```

These records are linked directly into the artifact's permanent audit directory (`output/review_provenance/` or `artifacts/provenance/`), ensuring that months later, an audit can verify who approved an export, why a finding was disputed, and what evidence was considered.

---

## 15. RepairEngine Boundary (Question N)

The boundary between Phase 6 Human Review and the existing `RepairEngine` (`RepairTransactionManager`, `MinimalInterventionRepairPlanner`) is one of the most critical security interfaces in the system.

```text
[ Human Reviewer ]
        │
        ▼ Issues Directive (e.g. SPLIT_SLIDE, TARGET_ELEMENT_ID)
[ DirectiveSafetyValidator ]  <── Checks forbidden flags & invariants
        │
        ▼ Approved Directive
[ ReviewEscalationBridge ]
        │
        ▼ Converts Directive to Constrained CandidateRepairOption
[ MinimalInterventionRepairPlanner ]
        │
        ▼ Normal Transaction Lifecycle:
[ RepairTransactionManager.execute_transaction() ]
        │
        ├── Snapshot
        ├── Actuator Execution
        ├── Re-Evaluation via UnifiedQualityAuthority
        ├── Drift Analysis (ArtifactDriftReport)
        ├── Invariant Check (RepairSafetyInvariants)
        └── Commit OR Rollback
```

**Key Boundary Invariant**: A human directive CANNOT directly alter code or AST nodes. A directive only acts as a **constrained parameter or constraint hint** to a registered, deterministic repair actuator. The resulting mutation must still pass through `RepairSafetyInvariants` and `UnifiedQualityAuthority` re-evaluation!

---

## 16. UnifiedQualityAuthority Boundary (Question M)

The relationship between Human Review and the `UnifiedQualityAuthority` (UQA) is strictly defined:

1. **UQA is the Level-0 Physical & Mathematical Authority**: UQA evaluates text geometry, font rendering, structural balance, and grounding metrics.
2. **Reviewers Cannot Modify Scores**: A human reviewer cannot change a UQA score from `0.65` to `0.95`.
3. **Disputes are Recorded as Metadata**: If a reviewer disputes a finding as a false positive, the finding status is marked `DISPUTED_BY_HUMAN` in the review record. However, if the finding was a **Hard Blocker**, the export remains blocked unless:
   - A verified repair eliminates the signal physically, OR
   - The finding rule itself is officially updated via an authoritative policy evolution in `app/quality/`.
4. **Zero Bypass**: `AuthorizedExportGate.validate_for_export()` will reject any artifact whose `UnifiedQualityReport.decision != ExportDecision.EXPORT_APPROVED` (or `APPROVED_WITH_WARNINGS`), regardless of whether a human clicked "approve".

---

## 17. Golden Corpus Governance Boundary (Question O)

Reviewers frequently identify edge cases during manual review that would make ideal benchmark test cases. To prevent **Benchmark Laundering**, the flow from review to the Golden Corpus is strictly guarded:

```text
[ Human Reviewer ]
        │
        ▼ Nominates Case as Golden Candidate
[ BenchmarkCandidateProposal ] (Captures candidate artifact, failure notes, expected invariants)
        │
        ▼
[ AntiLaunderingGuard.validate_mutation() ]
        │
        ├── Checks: Is baseline being lowered? (FORBIDDEN)
        ├── Checks: Is change classification legitimate? (CORPUS_EXPANSION)
        └── Checks: Does artifact satisfy minimum syntactic validity?
        │
        ▼
[ GoldenCorpusVersionManager ]
        │
        ▼ Issues Incremental Minor/Patch Corpus Version (e.g. 1.0.0 -> 1.1.0)
[ golden_corpus/cases/ & manifest.json ] Updated
```

This prevents engineers or reviewers from modifying benchmark baselines to artificially inflate regression scores.

---

## 18. Persistence Strategy (Question P)

Consistent with the architecture of Phases 3, 4, and 5, Phase 6 relies on **zero external databases, zero cloud dependencies, and zero heavy ORMs**.

### Architecture: File-Backed Immutable Ledger
- **Review Cases**: Persisted as deterministic JSON files in `artifacts/review_queue/cases/<case_id>.json`.
- **Review Decisions**: Persisted in `artifacts/review_queue/decisions/<case_id>_<review_id>.json`.
- **Provenance Ledger**: Appended to `artifacts/review_provenance/ledger.jsonl`.
- **In-Memory Query Index**: `ReviewQueueRegistry` maintains an in-memory index over the directory, rebuilding state on startup in $< 100	ext{ ms}$.
- **Concurrency & Locking**: File-system level atomic rename (`os.replace`) and flock semantics guarantee transactional writes without database corruption.

---

## 19. UI Boundary (Question Q)

To maintain clean separation between domain logic and presentation:
- **Phase 6 Scope**: Focuses strictly on the **Review Domain, Contracts, Queue Intelligence, Safety Gateways, Calibration Engines, CLI tools, and Static HTML/JSON Review Artifact Generation**.
- **Phase 7 Scope**: Interactive React/Web dashboard, WebSocket live updates, multi-user web servers.

In Phase 6, review cases can be fully inspected, evaluated, and decided via:
1. Pure Python API (`ReviewStudioSession`).
2. Deterministic CLI commands (`python -m app.review.cli ...`).
3. Self-contained, static visual HTML inspection bundles generated per review case (combining PDF page renders, bounding boxes, and finding sidebars).

---

## 20. Threat Model (Question R)

| Threat | Attack Vector | Mitigation in Phase 6 |
|---|---|---|
| **Unsafe Override** | Reviewer attempts to force export on a broken document | `AuthorizedExportGate` enforces Level-0 check; ignores human bypass flags |
| **Fabrication Override** | Reviewer attempts to approve ungrounded scientific claims | `DirectiveSafetyValidator` blocks claims lacking source manifest IDs |
| **Anti-Spoiling Bypass** | Teacher/Reviewer attempts to insert answers into student worksheet | `RepairSafetyInvariants._check_worksheet_invariants` rejects answer key insertion |
| **Benchmark Laundering** | Reviewer mutates golden baseline to hide model regression | `AntiLaunderingGuard` detects baseline descent and raises `BenchmarkLaunderingAttemptError` |
| **Provenance Tampering** | Retroactive modification of past review records | SHA-256 cryptographic chain and append-only ledger format |
| **Reviewer Fatigue** | Exhausted reviewer stamps "Approve" on everything | Blind golden cases inserted into queue; detects score variance drops |
| **Reviewer Bias** | Systematic hostility to specific formats or layouts | `ReviewerCalibrationEngine` tracks leniency and cross-format bias |

---

## 21. Review Priority Model (Question S)

Queue cases are prioritized dynamically using a deterministic multi-factor scoring formula:

31094	ext{PriorityScore} = w_1 S_{	ext{severity}} + w_2 S_{	ext{impact}} + w_3 S_{	ext{staleness}} + w_4 S_{	ext{governance}} + w_5 S_{	ext{convergence}}31094

Where:
- {	ext{severity}}$: Max severity of active findings (`BLOCKING`: 1.0, `MAJOR`: 0.7, `MINOR`: 0.3, `INFO`: 0.1).
- {	ext{impact}}$: Document reach (e.g., certification benchmark = 1.0, internal draft = 0.4).
- {	ext{staleness}}$: Time elapsed in queue (prevents starvation of low-severity cases).
- {	ext{governance}}$: Extra weight if triggered by `CertificationDecision.BENCHMARK_REGRESSION` or `AntiLaunderingGuard`.
- {	ext{convergence}}$: High weight if artifact suffered repeated budget exhaustion or oscillation.

Cases are partitioned into four priority bands: `P0_CRITICAL` (immediate block), `P1_HIGH`, `P2_NORMAL`, and `P3_BACKGROUND`.

---

## 22. Four Artifact-Type Review Extensions (Question T)

Each of the four canonical document types requires specialized human inspection interfaces and validation rules:

### 1. PRESENTATION
- **Reviewer Focus**: Cognitive load per slide, visual hierarchy, 16:9 viewport clipping, presenter-oral complementarity (is the slide a transcript or visual cue?).
- **Specialized Directives**: `SPLIT_SLIDE`, `MERGE_BEATS`, `REDUCE_CONTAINER_DENSITY`, `TOGGLE_PROGRESSIVE_REVEAL`.
- **Invariants**: Slide word count $< 60$, zero overlapping text boxes, 16:9 projection bounds preserved.

### 2. HANDOUT
- **Reviewer Focus**: Scannability, conceptual progression (5-layer explanation: Hook, Concept, Mechanism, Application, Pitfall), reading density, self-contained clarity.
- **Specialized Directives**: `ADJUST_SECTION_BALANCE`, `EXPAND_EXPLANATORY_LAYER`, `INSERT_READING_STOP`.
- **Invariants**: A4 pagination clean, margin integrity preserved, zero orphaned subheadings.

### 3. WORKSHEET
- **Reviewer Focus**: Anti-spoiling integrity, inquiry stage order (Observation $ightarrow$ Prediction $ightarrow$ Investigation $ightarrow$ Analysis $ightarrow$ Reflection), adequate physical workspace for student writing.
- **Specialized Directives**: `WITHHOLD_EXPLANATION`, `ADD_SCAFFOLDING_HINT`, `EXPAND_WRITING_BOX`.
- **Invariants**: **Strict Anti-Spoiling**: Answer key must never appear in student version; question prompts must not disclose downstream solutions.

### 4. SCIENTIFIC_DOCUMENT (KTI)
- **Reviewer Focus**: IMRaD argument rigor, Claim-Evidence-Reasoning linkage, uncertainty boundary classification, citation validity and Indonesian formal scientific register.
- **Specialized Directives**: `REQUEST_CITATION_BACKING`, `DEMOTE_CLAIM_TO_HYPOTHESIS`, `ISOLATE_LIMITATION`.
- **Invariants**: Zero fabricated citations, zero speculative claims stated as established fact without source attribution.

---

## 23. Backward Compatibility Risks (Question W)

A major risk in any Phase 6 implementation is accidental regression of existing modules:
1. **Production Pipeline Interruption**: Ensure that running `ProductionOrchestrator` without human review enabled continues to execute and terminate exactly as before (100% test compatibility).
2. **State Machine Immutability**: Do not add transition targets from `ProductionState.MANUAL_REVIEW_REQUIRED` inside `production_state.py`. Maintain separation via `ReviewStateMachine`.
3. **Data Model Compatibility**: `QualityFinding` in `app/quality/contracts/findings.py` must retain its existing frozen Pydantic structure; review annotations wrap `QualityFinding` rather than subclassing or mutating it.
4. **Zero Regression on Benchmark Suite**: All 246 existing tests across benchmarking, quality, and intelligence must pass without modification.

---

## 24. Recommended Phase 6 Architecture

### Complete System Architecture Diagram

```text
                               EXISTING SYSTEM (LEVEL 0)
──────────────────────────────────────────────────────────────────────────────────────────
UnifiedQualityAuthority          RepairSafetyInvariants             CertificationEngine
        │                                 │                                  │
        ├───────────► Export Gate         │                                  │
        │                                 │                                  │
        ▼ (MANUAL_REVIEW_REQ / BLOCKED)   ▼ (Safety Rejection)               ▼ (Regression / Insufficient)
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               REVIEW INTAKE ADAPTER                                    │
│  - Harvests ArtifactProductionContext, ConvergenceReports, BenchmarkEvaluations       │
│  - Extracts QualityFindings, Proof Geometries, Knowledge Manifests                    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              REVIEW QUEUE INTELLIGENCE                                 │
│  - Multi-Factor Priority Scorer (P0 - P3)                                              │
│  - File-Backed Queue Registry (artifacts/review_queue/)                                │
│  - Case State Machine (DISCOVERED -> QUEUED -> ASSIGNED -> IN_REVIEW)                  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           HUMAN REVIEW BOUNDED CONTEXT                                 │
│  ├── Evidence Aggregation Adapter (Side-by-side renders, BBoxes, Claim Traceability)   │
│  ├── Structured Decision Validator (CONFIRM_DEFECT, DISPUTE_FP, PROPOSE_GOLDEN)        │
│  ├── Multi-Reviewer Disagreement & Adjudication Engine (Kappa >= 0.80)                 │
│  └── Reviewer Calibration Engine (Blind golden cases, bias tracking)                   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Emits Signed Action Directives
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            DIRECTIVE SAFETY GATEWAY                                    │
│  - Strict Invariant Verification: Blocks force-export, citation fakes, answer leaks    │
│  - Scope Limiter: Restricts directives to valid architectural levels (R0 - R5)         │
└───────────────────┬───────────────────────┬─────────────────────────┬──────────────────┘
                    │                       │                         │
                    ▼                       ▼                         ▼
         [ SAFE REPAIR BRIDGE ]    [ BENCHMARK GOVERNANCE ]   [ ADJUDICATION ESCALATION ]
                    │                       │                         │
                    ▼                       ▼                         ▼
          MinimalIntervention       AntiLaunderingGuard       Senior Expert Escalation
             RepairPlanner          GoldenCorpusVersion       Review Queue
                    │                     Manager
                    ▼                       │
          RepairSafetyInvariants            ▼
                    │               Versioned Golden Corpus
                    ▼                       │
          Re-evaluate via UQA               │
                    │                       │
                    └───────────────────────┴─────────────────────────┐
                                                                      ▼
                                                       [ IMMUTABLE REVIEW PROVENANCE ]
                                                       - Append-only cryptographically
                                                         signed ledger (ledger.jsonl)
```

---

## 25. Explicit Non-Goals

To prevent scope creep and maintain architectural discipline, the following are explicitly **out of scope** for Phase 6:
- **No React / Vue / Frontend Frameworks**: The web dashboard belongs to Phase 7.
- **No PostgreSQL / MySQL / MongoDB**: Storage remains strictly file-backed JSON/JSONL with directory indexing.
- **No Redis / Celery / RabbitMQ**: Asynchronous background workers or external brokers are prohibited.
- **No Cloud Authentication (OAuth/Auth0)**: Reviewer identity is managed via local cryptographic tokens and configuration keys.
- **No Direct Quality Score Editing**: Reviewers will never possess the ability to alter numerical quality scores directly.
- **No Force-Export Overrides**: Human approval cannot bypass a Level-0 blocking finding without an approved, verified repair.

---

## 26. Open Questions & Risks

1. **Reviewer Throughput & Latency**: Manual review introduces human latency. The queue intelligence must support expiration timeouts and automatic reassignment if a reviewer becomes inactive.
2. **Adversarial Human Input**: A malicious or compromised reviewer might submit nonsense directives. The `DirectiveSafetyValidator` and `ReviewerCalibrationEngine` must treat all human input as potentially adversarial.
3. **Drift in Long-Running Review Replays**: If days elapse between review creation and repair dispatch, the underlying code or prompt models could drift. All review directives must bind immutably to the original artifact git commit and input digest.
