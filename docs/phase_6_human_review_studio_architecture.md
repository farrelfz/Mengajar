# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 6 — HUMAN-IN-THE-LOOP REVIEW STUDIO ARCHITECTURE
## EXPERT DECISION GOVERNANCE & EPISTEMIC REVIEW INFRASTRUCTURE

---

## 1. Executive Summary

Phase 6 implements a deterministic, epistemically grounded, and cryptographically auditable **Human-in-the-Loop Review Studio** within the `app/review/` bounded context.

The system resolves the classic tension between automated quality guarantees and human domain intervention. Rather than treating human review as an "admin override" or a "force approval" button, Phase 6 establishes human experts as **epistemic partners**:
- Humans contribute **domain judgment**, **causal disambiguation**, **pedagogical review**, and **edge-case discovery**.
- The deterministic system retains absolute sovereignty over **safety invariants**, **mathematical quality thresholds**, **anti-laundering rules**, and **export authorization**.

Every human action follows the strict epistemic separation:
$$\text{Observation} \longrightarrow \text{Interpretation} \longrightarrow \text{Decision} \longrightarrow \text{Directive}$$

---

## 2. Sovereign Authority Topology

```text
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 0: IMMUTABLE MATHEMATICAL & PHYSICAL EVALUATION (SOVEREIGN)      │
│ - UnifiedQualityAuthority (QualityDomain scores, hard blockers)        │
│ - AuthorizedExportGate (Sole gatekeeper to physical export)            │
│ - RepairSafetyInvariants (Non-negotiable drift, citation & spoiling)   │
│ - AntiLaunderingGuard (Strict baseline descent prohibition)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Emits Unresolved / Critical States
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: GOVERNED HUMAN-IN-THE-LOOP REVIEW STUDIO (app/review/)        │
│ - ReviewabilityClassifier (Separates trivial auto-repairs from expert) │
│ - Multi-Factor ReviewPriorityModel (P0_CRITICAL to P3_BACKGROUND)      │
│ - ReviewEvidencePackage & ReviewLineageAdapter (Multi-modal evidence)  │
│ - Epistemic Decision Engine (Observation -> Interpretation -> Decision)│
│ - DirectiveSafetyValidator (Firewall against force-export & leaks)     │
│ - DisagreementAnalyzer & Senior Adjudication (Kappa >= 0.80)           │
│ - ReviewerCalibrationEngine (Non-punitive bias & leniency tracking)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Emits Signed, Validated Directives
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: EXECUTION & PERSISTENCE BRIDGES                               │
│ - ReviewRepairBridge (Converts directives to constrained planner hints)│
│ - MinimalInterventionRepairPlanner & RepairTransactionManager          │
│ - BenchmarkGovernanceBridge (Validates candidate proposals)            │
│ - Immutable Review Provenance Ledger (SHA-256 chained ledger.jsonl)   │
└────────────────────────────────────────────────────────────────────────┘
```

**Non-Negotiable Invariants**:
1. $\text{Human Review} \neq \text{Quality Authority}$.
2. $\text{Human Approval} \neq \text{Export Authorization}$.
3. Human directives cannot bypass `AuthorizedExportGate` or disable `RepairSafetyInvariants`.

---

## 3. Review Lifecycle & Independent State Machine

In `app/orchestration/production_state.py`, `ProductionState.MANUAL_REVIEW_REQUIRED` and `ProductionState.BLOCKED` are immutable terminal states. Review lifecycles are strictly managed by `ReviewStateMachine` in `app/review/review_state.py`:

```text
  [ OPEN ]
      │
      ├── (Case Leased) ──► [ LEASED ]
      │                         │
      │                         ├── (Timeout/Cancel) ──► [ OPEN ]
      │                         └── (Decision + Directives) ──► [ DIRECTIVE_PROPOSED ]
      │
      ├── (Single Decision) ──► [ UNDER_REVIEW ]
      │                             │
      │                             ├── (Consensus Reached) ──► [ RESOLVED ]
      │                             ├── (Divergence Detected) ──► [ AWAITING_SECOND_REVIEW ]
      │                             └── (Blocker / Senior) ──► [ ADJUDICATION ]
      │
      └── (Senior Adjudicated) ──► [ RESOLVED ] / [ ESCALATED ]
```

When a repair directive is validated and replayed, a new governed replay job is spawned with full auditability, preserving the original run's terminal failure record.

---

## 4. Directive Ontology & Safety Firewall

Supported directives in `DirectiveOntology` (`app/review/directives/ontology.py`):

| Directive Type | Category | Applicable Artifacts | Escalation Layer | Parameter Requirements |
|---|---|---|---|---|
| `SPLIT_SLIDE` | REPAIR | PRESENTATION | LEVEL_R3_ARTIFACT_STRUCTURE | `split_index` |
| `REMAP_COMPONENT` | REPAIR | PRESENTATION, HANDOUT, WORKSHEET | LEVEL_R2_LAYOUT_STRUCTURE | `target_container` |
| `ADJUST_TOKEN` | REPAIR | ALL FORMATS | LEVEL_R0_RENDER_TOKEN | `token_name`, `value` |
| `RECOMPOSE_PAGE` | REPAIR | HANDOUT, WORKSHEET, SCIENTIFIC | LEVEL_R3_ARTIFACT_STRUCTURE | None |
| `REPAGINATE` | REPAIR | HANDOUT, WORKSHEET, SCIENTIFIC | LEVEL_R2_LAYOUT_STRUCTURE | None |
| `WITHHOLD_EXPLANATION` | PEDAGOGICAL | WORKSHEET | LEVEL_R4_SEMANTIC_TRANSFORMATION | None |
| `RESTORE_INQUIRY_ARC` | PEDAGOGICAL | WORKSHEET | LEVEL_R4_SEMANTIC_TRANSFORMATION | None |
| `REQUEST_CITATION_BACKING` | EVIDENCE | SCIENTIFIC_DOCUMENT, KTI | LEVEL_R5_SOURCE_INTELLIGENCE | `claim_id` |
| `REQUEST_SOURCE_RECHECK` | EVIDENCE | ALL FORMATS | LEVEL_R5_SOURCE_INTELLIGENCE | None |
| `REDUCE_COGNITIVE_LOAD` | PEDAGOGICAL | PRESENTATION, HANDOUT | LEVEL_R3_ARTIFACT_STRUCTURE | None |
| `CONFIRM_ROOT_CAUSE` | DIAGNOSIS | ALL FORMATS | LEVEL_R1_COMPONENT_PARAM | None |
| `RECLASSIFY_ROOT_CAUSE` | DIAGNOSIS | ALL FORMATS | LEVEL_R1_COMPONENT_PARAM | `new_root_cause` |
| `ESCALATE` | GOVERNANCE | ALL FORMATS | LEVEL_R5_SOURCE_INTELLIGENCE | None |
| `PROPOSE_GOLDEN_CASE` | GOVERNANCE | ALL FORMATS | LEVEL_R5_SOURCE_INTELLIGENCE | None |

### Forbidden Flags (Structural Block):
- `force_export`: Raises `IllegalDirectiveException`.
- `disable_quality_gate`: Raises `IllegalDirectiveException`.
- `ignore_hard_blocker`: Raises `IllegalDirectiveException`.
- `disable_anti_spoiling` / `reveal_answers`: Raises `IllegalDirectiveException`.
- `fabricate_citation` / `synthesize_citation`: Raises `IllegalDirectiveException`.
- `lower_baseline`: Raises `BenchmarkLaunderingAttemptError`.

---

## 5. File-Backed Persistence & Cryptographic Ledger

- **Queue Storage**: `artifacts/review_queue/cases/<case_id>.json` written atomically via temporary files and `os.replace`.
- **Lease Locks**: Managed by `LeaseManager` with 1800s default timeouts in `artifacts/review_queue/leases/`.
- **Provenance Ledger**: Append-only JSON Lines in `artifacts/review_provenance/ledger.jsonl`.
- **Chaining Invariant**:
  $$\text{Hash}_i = \text{SHA-256}(\text{CanonicalJSON}(E_i) + \text{Hash}_{i-1})$$
  Where $\text{Hash}_0 = \text{"0" * 64}$.
  Tampering with any historical line immediately breaks `verify_ledger_integrity()`.

---

## 6. Inspection Bundle & CLI Harness

- **Static HTML Inspection Bundle**: Generated at `artifacts/review_queue/cases/{case_id}/static_review.html`. Visual evidence viewer only; cannot authorize export.
- **CLI Commands**:
  - `python -m app.review.cli list`
  - `python -m app.review.cli show <case_id>`
  - `python -m app.review.cli lease <case_id> <reviewer_id>`
  - `python -m app.review.cli evidence <case_id>`
  - `python -m app.review.cli decide <case_id> <decision.json>`
  - `python -m app.review.cli validate-directive <case_id> <directive.json>`
  - `python -m app.review.cli bundle <case_id>`
  - `python -m app.review.cli ledger-verify`
