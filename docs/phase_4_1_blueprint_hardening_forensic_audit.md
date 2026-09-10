# Phase 4.1 Blueprint Hardening Forensic Audit

1. Executive Summary: Two blueprint systems exist. Python Pydantic = production untouched; Markdown templates = target for upgrade.
2. Repository Architecture Map: templates/document_types/*/*.md, app/intelligence/transformation/*, etc.
3. Existing Markdown Blueprint Analysis: 4 templates, each with 8-9 minimal fields, lacks robust constraints.
4. Existing Python Blueprint Analysis: blueprints.py schemas, differentiation_validator, traceability already mature.
5. Generation Entry Point Trace: prompts/ files are NOT loaded by Python; templates/ NOT loaded by Python; CLI generates via Python pipeline only.
6. Contract Ownership: Markdown = LLM generation instruction; Python = machine transformation contract.
7. Cross-Artifact Collapse Risks: Document all 5 collapse types (presentation-handout, worksheet-quiz, scientific-argument, etc.).
8. Duplication Risks: Do not duplicate ArtifactDifferentiationValidator.
9. Compatibility Constraints: Zero Python code changes to existing transformation layer.
10. Recommended Architecture: _shared/ directory + 4 hardened templates + app/intelligence/blueprint_validation/
11. Validation Architecture: BlueprintValidationReport, artifact-specific validators.
12. Proposed File Changes: templates/document_types/_shared/*.md, templates/document_types/*/blueprint_template.md, app/intelligence/blueprint_validation/*.py
13. Non-Goals: no renderer changes, no CSS, no QualityAuthority changes.
14. Migration: additive only.
15. Test Strategy: 22 tests covering all artifact types.
16. Phase Stop Condition: all 22 tests pass, zero regressions.
