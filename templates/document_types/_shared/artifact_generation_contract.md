# UNIVERSAL ARTIFACT GENERATION CONTRACT
# Blueprint Version: 1.0

> A blueprint is NOT content. It is a semantic transformation plan.
> The renderer must never decide the intellectual structure of an artifact.
> The blueprint must already encode: what knowledge is selected, why it is selected,
> how it is transformed, what role it plays, what is intentionally omitted,
> and how the artifact differs from the other three formats.

---

## ARTIFACT_IDENTITY

**ARTIFACT_TYPE**: [PRESENTATION | HANDOUT | WORKSHEET | SCIENTIFIC_DOCUMENT]
**ARTIFACT_TITLE**: [Document title]
**ARTIFACT_PURPOSE**: [What this specific artifact is designed to achieve]
**TARGET_AUDIENCE**: [Who will consume this artifact]
**AUDIENCE_PRIOR_KNOWLEDGE**: [What prior knowledge is assumed]
**PRIMARY_USE_CONTEXT**: [CLASSROOM_PROJECTION | INDEPENDENT_STUDY | LAB_ACTIVITY | RESEARCH_SUBMISSION]
**EXPECTED_INTERACTION_MODE**: [PASSIVE_VIEWING | ACTIVE_READING | GUIDED_INQUIRY | FORMAL_ARGUMENT_CONSUMPTION]
**PRIMARY_SUCCESS_CRITERION**: [How we know this artifact succeeded]

---

## SOURCE_INTELLIGENCE

**SOURCE_MANIFEST_ID**: [ID linking to the source knowledge manifest]
**SOURCE_KNOWLEDGE_UNITS**: [Total count of available knowledge units in source]
**SELECTED_KNOWLEDGE_UNITS**: [List of selected unit IDs]
**EXCLUDED_KNOWLEDGE_UNITS**: [List of excluded unit IDs with rationale]
**KNOWLEDGE_SELECTION_RATIONALE**: [Why these units were selected for THIS artifact type]
**UNCERTAINTY_STATE**: [KNOWN | SUPPORTED | INFERRED | UNCERTAIN | UNRESOLVED — for each major claim]

---

## SEMANTIC_INTENT

**PRIMARY_GOAL**: [The fundamental intellectual task this artifact performs]
**INFORMATION_DENSITY_TARGET**: [0.0-1.0]
  - Reference: PRESENTATION ≈ 0.35, HANDOUT ≈ 0.70, WORKSHEET ≈ 0.50, SCIENTIFIC_DOCUMENT ≈ 0.85
**COMPRESSION_STRATEGY**: [HIGH_COMPRESSION_BEATS | MODERATE_EXPLANATORY | QUESTION_WITHHOLDING | EVIDENCE_STRUCTURED]
**SEQUENCING_STRATEGY**: [STORY_BEATS | TAXONOMIC_SECTIONS | INQUIRY_STAGES | IMRAD_SECTIONS]
**NARRATIVE_MODE**: [PROGRESSIVE_REVEAL | HIERARCHICAL_EXPLANATORY | GUIDED_DISCOVERY | ARGUMENTATIVE_CLAIM_EVIDENCE]
**INTERACTION_LEVEL**: [0.0-1.0 — Reference: PRESENTATION ≈ 0.20, HANDOUT ≈ 0.10, WORKSHEET ≈ 0.90, SCIENTIFIC ≈ 0.05]
**EVIDENCE_REQUIREMENT**: [0.0-1.0 — Reference: PRESENTATION ≈ 0.30, HANDOUT ≈ 0.50, WORKSHEET ≈ 0.60, SCIENTIFIC ≈ 0.95]

---

## INTEGRITY

**FABRICATION_POLICY**: ZERO_TOLERANCE
  - Never invent: citations, authors, measurements, experimental results, DOIs, URLs
  - If source unavailable: FLAG_FOR_LIMITATION, not fabricate
**UNCERTAINTY_POLICY**: [EXCLUDE_UNRESOLVED | FLAG_FOR_CLARIFICATION | ISOLATE_AS_LIMITATION]
**TRACEABILITY_REQUIREMENT**: [Every major claim must link to a SOURCE_KNOWLEDGE_UNIT_ID]
**SOURCE_ATTRIBUTION_REQUIREMENT**: [All evidence must be traceable to source manifest]

---

## SELF_VALIDATION

**ANTI_PATTERN_CHECK**: [List detected anti-patterns or NONE]
**ARTIFACT_COLLAPSE_CHECK**: [Could this be mistaken for another artifact type? Explain.]
**CONTRACT_COMPLETENESS_CHECK**: [Are all required fields filled? List missing fields or COMPLETE]
**FABRICATION_RISK_CHECK**: [Any unsupported claims present? NONE or list them]
**CROSS_ARTIFACT_DIFFERENTIATION**: [How does this artifact differ from the other three in structure?]
