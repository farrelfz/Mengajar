# Phase 4.1 — Canonical Artifact Blueprint Hardening: Forensic Audit

---

## 1. Files Audited

### Template Files (Markdown — Human-facing blueprints)
| File | Size | Status |
|---|---|---|
| `templates/document_types/presentation/blueprint_template.md` | 9 fields | **Minimal skeleton** |
| `templates/document_types/handout/blueprint_template.md` | 9 fields | **Minimal skeleton** |
| `templates/document_types/worksheet/blueprint_template.md` | 9 fields | **Minimal skeleton** |
| `templates/document_types/kti/blueprint_template.md` | 8 fields | **Minimal skeleton** |

### Python Machine-Readable Blueprint Schemas (Code — Pipeline-consumed)
| File | Purpose | Status |
|---|---|---|
| `app/intelligence/transformation/blueprints.py` | Pydantic blueprint schemas consumed by pipeline | **Active, mature** |
| `app/intelligence/transformation/intent.py` | `ResolvedArtifactIntent`, `ArtifactType`, defaults | **Active, mature** |
| `app/intelligence/transformation/differentiation_validator.py` | Cross-artifact divergence rules | **Active, mature** |
| `app/intelligence/transformation/transformers.py` | `PresentationTransformer`, `HandoutTransformer`, etc. | **Active, mature** |
| `app/intelligence/transformation/traceability.py` | `TransformationTraceabilityEngine` | **Active, mature** |

### Prompt Files (Markdown — Canonical Generation Triggers)
| File | Status |
|---|---|
| `prompts/document_types/presentation.md` | Newly created (this session) |
| `prompts/document_types/handout.md` | Newly created (this session) |
| `prompts/document_types/worksheet.md` | Newly created (this session) |
| `prompts/document_types/scientific_document.md` | Newly created (this session) |

### Key Test Files
| File | Tests |
|---|---|
| `tests/unit/intelligence/test_transformation_contract.py` | 30 tests covering all transformer contracts |
| `tests/unit/intelligence/test_cross_artifact_adversarial_validation.py` | Cross-artifact adversarial tests |
| `tests/unit/integration/test_artifact_blueprint_bridge.py` | Blueprint-to-renderer bridge |

---

## 2. Current Architecture Findings

### 2.1 TWO Blueprint Systems Coexist (Critical Insight)

The repository has **two blueprint representations**:

**System A — Python Pydantic Schemas** (`app/intelligence/transformation/blueprints.py`)  
The **actual machine-consumed** blueprint pipeline:
- `ArtifactBlueprint` (base)
- `PresentationBlueprint` → contains `ConceptualBeat` objects
- `HandoutBlueprint` → contains `ExplanatorySection` objects  
- `WorksheetBlueprint` → contains `LearningActivity` objects
- `ScientificDocumentBlueprint` → contains `ScientificArgumentUnit` objects

This is consumed by transformers, validators, renderers, and quality gates. **DO NOT TOUCH**.

**System B — Markdown Templates** (`templates/document_types/*/blueprint_template.md`)  
Human-readable **planning schemas** for generation-time AI reasoning. These are currently **minimal skeletons** with 8–9 fields each. They are **not consumed by any Python code** — they are semantic instruction templates.

**Conclusion:** Hardening work targets System B (Markdown templates) only. System A remains unchanged.

### 2.2 Existing Python Schema Intelligence (Already Present)

The Python schemas already encode:

| Capability | Python Schema Field | Missing in MD Template? |
|---|---|---|
| Artifact type | `artifact_type` | ✅ No mention needed |
| Knowledge unit IDs | `knowledge_unit_ids`, `source_manifest_id` | ⚠️ Partially mentioned |
| Cognitive load | `cognitive_load_target` (float 0–1) | ⚠️ Only as LOW/MEDIUM/HIGH |
| Narrative function | `narrative_function` (HOOK, etc.) | ❌ Missing macro arc |
| Withhold explanation | `withhold_explanation: bool` | ⚠️ Present but no audit protocol |
| Scientific role | `argument_role: ScientificArgumentRole` | ⚠️ Present but no taxonomy |
| Differentiation | `ArtifactDifferentiationValidator` | ❌ Not referenced in MD |
| Traceability | `TransformationTraceabilityEngine` | ❌ Not referenced in MD |

### 2.3 `ResolvedArtifactIntent` Default Profiles (Already Present)

The Python system already defines per-artifact defaults in `intent.py`:

| Artifact | information_density | interaction_level | evidence_requirement | narrative_mode |
|---|---|---|---|---|
| PRESENTATION | 0.35 | 0.20 | 0.30 | PROGRESSIVE_REVEAL |
| HANDOUT | 0.70 | 0.10 | 0.50 | HIERARCHICAL_EXPLANATORY |
| WORKSHEET | 0.50 | 0.90 | 0.60 | GUIDED_DISCOVERY |
| SCIENTIFIC_DOCUMENT | 0.85 | 0.05 | 0.95 | ARGUMENTATIVE_CLAIM_EVIDENCE |

These numeric values must be **reflected** in the Markdown templates as machine-readable constraints.

---

## 3. Existing Template Weaknesses

### PRESENTATION blueprint_template.md
| Field | Issue |
|---|---|
| `SEMANTIC_ROLE` | Present but no allowed values list |
| `COGNITIVE_LOAD` | Only LOW/MEDIUM/HIGH — no numeric contract, no overload detection |
| `VISUAL_GRAMMAR` | Examples only, no taxonomy, no repetition constraint |
| **MISSING** | `PRESENTATION_THESIS`, `NARRATIVE_ARC`, macro progression |
| **MISSING** | `ONE_SENTENCE_TAKEAWAY`, `WHY_THIS_MUST_BE_A_SLIDE` |
| **MISSING** | `PROGRESSIVE_DISCLOSURE_PLAN`, `WORKING_MEMORY_RISK` |
| **MISSING** | Anti-pattern checklist, self-review section |
| **MISSING** | `KNOWLEDGE_COMPRESSION_RATIONALE` |

### HANDOUT blueprint_template.md
| Field | Issue |
|---|---|
| `EXPLANATIONS` | Present but no depth layer model (Intuition/Formal/Mechanism/Example) |
| `TRANSITION_TO_NEXT_SECTION` | Present but no dependency graph |
| **MISSING** | `PREREQUISITE_CONTEXT`, `MISCONCEPTION_CLARIFICATION` |
| **MISSING** | `READING_PURPOSE`, `INDEPENDENT_COMPREHENSION_TARGET` |
| **MISSING** | Wall-of-text detection fields |
| **MISSING** | Presentation-collapse detection |

### WORKSHEET blueprint_template.md
| Field | Issue |
|---|---|
| `WITHHOLD_EXPLANATION` | Present as string but no boolean enforcement, no leak audit |
| `WORKSPACE_REQUIREMENT` | Present but no semantic justification requirement |
| **MISSING** | `KNOWLEDGE_WITHHELD` vs `KNOWLEDGE_REVEALED` distinction |
| **MISSING** | `ALLOWED_HINT_LEVEL`, `ANSWER_LEAK_RISK` |
| **MISSING** | Question taxonomy (OBSERVATIONAL/PREDICTIVE/CAUSAL/etc.) |
| **MISSING** | Inquiry arc completeness validation |
| **MISSING** | Quiz-collapse detection |

### KTI blueprint_template.md
| Field | Issue |
|---|---|
| `EVIDENCE_TYPE` | Only lists relationships (SUPPORTED_BY, etc.) — no taxonomy |
| `CONFIDENCE` | Present but no scale definition |
| **MISSING** | `CLAIM_TYPE`, `CLAIM_STRENGTH`, `EVIDENCE_DIRECTNESS` |
| **MISSING** | `FORBIDDEN_FABRICATION_CHECK` boolean |
| **MISSING** | BAB architecture map |
| **MISSING** | Uncertainty discipline (KNOWN/SUPPORTED/INFERRED/UNCERTAIN) |
| **MISSING** | Citation traceability fields |

### ALL FOUR Templates: Universal Gaps
- No `ARTIFACT_IDENTITY` section with purpose, audience, interaction mode
- No `SOURCE_SCOPE` section linking to manifest
- No `FABRICATION_POLICY` boolean
- No `UNCERTAINTY_POLICY` reference
- No `GENERATION_SELF_CRITIQUE` checklist
- No cross-artifact differentiation hooks
- No adversarial examples

---

## 4. Proposed New Contract Architecture

```
templates/document_types/
├── _shared/
│   ├── artifact_generation_contract.md   [NEW — Universal meta-contract]
│   ├── cross_artifact_differentiation_matrix.md  [NEW]
│   └── canonical_generation_trigger.md   [NEW]
│
├── presentation/
│   └── blueprint_template.md             [UPGRADE — Harden existing]
│
├── handout/
│   └── blueprint_template.md             [UPGRADE — Harden existing]
│
├── worksheet/
│   └── blueprint_template.md             [UPGRADE — Harden existing]
│
└── kti/
    └── blueprint_template.md             [UPGRADE — Harden existing]
```

### New Field Architecture Summary

**Shared (all 4 artifacts):**
- `ARTIFACT_TYPE`, `ARTIFACT_PRIMARY_PURPOSE`, `AUDIENCE_PRIOR_KNOWLEDGE`
- `SOURCE_MANIFEST_ID`, `SELECTED_KNOWLEDGE_UNITS`, `EXCLUDED_KNOWLEDGE_UNITS`
- `FABRICATION_POLICY` [ENUM: ZERO_TOLERANCE]
- `UNCERTAIN_KNOWLEDGE_POLICY` [ENUM: EXCLUDE / FLAG / ISOLATE_AS_LIMITATION]
- `SEMANTIC_INTEGRITY_CHECK`, `TRACEABILITY_CHECK`, `ANTI_PATTERN_CHECK` [BOOLEAN]

**Presentation additions:**
- `PRESENTATION_THESIS`, `CENTRAL_NARRATIVE_QUESTION`, `NARRATIVE_PROMISE`
- `NARRATIVE_PHASE`, `PHASE_PURPOSE`, `WHY_NEXT_SLIDE_EXISTS`
- `NEW_CONCEPT_COUNT`, `WORKING_MEMORY_RISK`, `PROGRESSIVE_DISCLOSURE_PLAN`
- `PRIMARY_VISUAL_OBJECT`, `ATTENTION_DIRECTION`, `REVEAL_SEQUENCE`
- `HANDOUT_COLLAPSE_RISK` [BOOLEAN]

**Handout additions:**
- `READING_PURPOSE`, `INDEPENDENT_COMPREHENSION_TARGET`, `EXPECTED_READING_TIME`
- `LAYER_1_INTUITION` through `LAYER_5_APPLICATION`
- `MISCONCEPTION_CLARIFICATION`, `COUNTEREXAMPLE_REQUIREMENT`
- `WALL_OF_TEXT_RISK` [BOOLEAN], `PRESENTATION_COLLAPSE_RISK` [BOOLEAN]

**Worksheet additions:**
- `CENTRAL_INVESTIGATIVE_QUESTION`, `TARGET_DISCOVERY`, `INQUIRY_DEPTH`
- `KNOWLEDGE_WITHHELD`, `KNOWLEDGE_REVEALED`, `ALLOWED_HINT_LEVEL`
- `ANSWER_LEAK_RISK` [BOOLEAN], `QUIZ_COLLAPSE_RISK` [BOOLEAN]
- `QUESTION_TAXONOMY` [ENUM: OBSERVATIONAL/COMPARATIVE/PREDICTIVE/etc.]
- `INQUIRY_ARC_COMPLETENESS` [BOOLEAN]

**KTI additions:**
- `RESEARCH_GAP`, `RESEARCH_QUESTION`, `SCOPE_BOUNDARY`
- `CLAIM_TYPE`, `CLAIM_STRENGTH`, `EVIDENCE_DIRECTNESS`
- `FORBIDDEN_FABRICATION_CHECK` [BOOLEAN: must be TRUE]
- `UNCERTAINTY_STATE` [ENUM: KNOWN/SUPPORTED/INFERRED/UNCERTAIN/UNRESOLVED]
- `BAB_FUNCTION`, `ARGUMENT_ROLE`, `INPUT_FROM_PREVIOUS_BAB`
- `OVERCLAIM_RISK` [BOOLEAN], `FABRICATION_RISK_CHECK` [BOOLEAN]

---

## 5. Dependency Risks

| Risk | Assessment |
|---|---|
| **Python schemas untouched** | SAFE — Markdown templates are not imported by any Python code |
| **Existing test suite** | SAFE — No tests reference `blueprint_template.md` files directly |
| **Renderer engines** | SAFE — Templates are renderer-independent by design |
| **UnifiedQualityAuthority** | SAFE — Templates are pre-pipeline planning documents |
| **ArtifactDifferentiationValidator** | SAFE — Python schema unchanged; templates will reference its concepts only as documentation |
| **`prompts/document_types/*.md`** | SAFE — These are distinct from `templates/` and serve as AI system prompts |

---

## 6. Backward Compatibility Risks

- **ZERO CODE CHANGES** required — templates are `.md` files only
- No Python imports of these files exist
- No test assertions reference these file paths
- Safe to add new fields — existing fields preserved

Only risk: if an external tool or script reads `templates/document_types/` — a scan found none in the Python codebase.

---

## 7. Proposed Files to Create/Modify

| Action | File | Notes |
|---|---|---|
| CREATE | `templates/document_types/_shared/artifact_generation_contract.md` | Universal meta-contract |
| CREATE | `templates/document_types/_shared/cross_artifact_differentiation_matrix.md` | 4×N comparison matrix |
| CREATE | `templates/document_types/_shared/canonical_generation_trigger.md` | Master generation trigger |
| UPGRADE | `templates/document_types/presentation/blueprint_template.md` | ~9 fields → ~35 fields |
| UPGRADE | `templates/document_types/handout/blueprint_template.md` | ~9 fields → ~30 fields |
| UPGRADE | `templates/document_types/worksheet/blueprint_template.md` | ~9 fields → ~32 fields |
| UPGRADE | `templates/document_types/kti/blueprint_template.md` | ~8 fields → ~33 fields |
| CREATE | `docs/phase_4_1_canonical_artifact_blueprint_hardening.md` | Architecture documentation |
| CREATE | `tests/unit/intelligence/test_blueprint_contract_hardening.py` | New blueprint validation tests |

---

## 8. Test Strategy

Tests will validate **blueprint structural logic** by constructing minimal blueprint dicts and running them through a new lightweight `BlueprintContractValidator` class (Python, no rendering):

| Test ID | Description |
|---|---|
| A | Presentation rejects handout-style paragraph blueprint |
| B | Presentation requires narrative progression arc |
| C | Presentation detects >3 consecutive identical visual grammar |
| D | Handout enforces independent reading architecture |
| E | Handout detects wall-of-text risk |
| F | Handout detects presentation collapse |
| G | Worksheet enforces inquiry progression |
| H | Worksheet detects answer leakage |
| I | Worksheet detects quiz collapse |
| J | Worksheet requires workspace rationale |
| K | Scientific requires claim-evidence linkage |
| L | Scientific rejects unsupported claims |
| M | Scientific preserves uncertainty states |
| N | Scientific rejects fabricated citation metadata |
| O | Same knowledge may appear across artifacts |
| P | Same structure must NOT automatically appear across artifacts |
| Q | Artifact differentiation score measurable |
| R | Cross-artifact collapse detected |
| S | Source traceability preserved |
| T | Unknown knowledge cannot silently become verified |
| U | Blueprint fields remain renderer-independent |
| V | Existing pipeline passes backward compatibility check |

---

## 9. Implementation Plan

### Step 1 — Create `_shared/` directory and three shared contracts
- `artifact_generation_contract.md`
- `cross_artifact_differentiation_matrix.md`
- `canonical_generation_trigger.md`

### Step 2 — Upgrade `presentation/blueprint_template.md`
Add: identity, macro arc, slide-level semantic contract, cognitive load model, visual grammar contract, rhythm, anti-patterns, self-review.

### Step 3 — Upgrade `handout/blueprint_template.md`
Add: identity, conceptual architecture, explanatory depth layers, reading rhythm, anti-patterns, self-review.

### Step 4 — Upgrade `worksheet/blueprint_template.md`
Add: identity, inquiry arc, anti-spoiling contract, workspace intelligence, question taxonomy, anti-patterns, self-review.

### Step 5 — Upgrade `kti/blueprint_template.md`
Add: identity, argument map, CER contract, evidence taxonomy, BAB architecture, uncertainty discipline, citation traceability, anti-patterns, self-review.

### Step 6 — Create `tests/unit/intelligence/test_blueprint_contract_hardening.py`
Implement all 22 validation tests using a lightweight Python validator that inspects blueprint dicts.

### Step 7 — Create `docs/phase_4_1_canonical_artifact_blueprint_hardening.md`
Full architectural documentation.

### Step 8 — Run full regression
`.venv/bin/pytest` — confirm zero regressions.
