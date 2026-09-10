# SCIENTIFIC DOCUMENT / KTI SEMANTIC BLUEPRINT TEMPLATE
# Artifact: SCIENTIFIC_DOCUMENT / KARYA TULIS ILMIAH (Formal Indonesian Scientific Paper)
# Mode: Claim-Evidence-Reasoning, Epistemic Rigor & Methodological Traceability

---

## 1. SCIENTIFIC IDENTITY & SCOPE
**RESEARCH_TITLE**: [Formal academic title stating independent, dependent, and contextual variables]
**RESEARCH_DOMAIN**: [e.g., Applied Physics, Fluid Dynamics, Materials Science]
**RESEARCH_PROBLEM**: [The real-world or theoretical discrepancy requiring investigation]
**RESEARCH_GAP**: [What is currently missing from existing literature or local knowledge]
**RESEARCH_QUESTION**: [Formal research question formulated under formal academic standards]
**RESEARCH_OBJECTIVE**: [Specific, measurable goals of the investigation]
**ARGUMENT_THESIS**: [Central scientific claim defended through empirical or derived evidence]
**SCOPE_BOUNDARY**: [Deliberate constraints: parameters tested, environmental controls, bounds of validity]

---

## 2. FORMAL BAB ARCHITECTURE
- **BAB I (PENDAHULUAN)**: [Problem framing, background hierarchy, gap, formulation, objectives, benefits]
- **BAB II (TINJAUAN PUSTAKA)**: [Theoretical foundation, literature consensus, conceptual framework, hypotheses]
- **BAB III (METODOLOGI)**: [Research design, variables, apparatus/materials, protocol, analysis methods]
- **BAB IV (HASIL DAN PEMBAHASAN)**: [Empirical data, error analysis, mechanism interpretation, limitations]
- **BAB V (PENUTUP)**: [Defensible conclusions strictly bound by evidence, forward suggestions]

---

## 3. CLAIM-EVIDENCE-REASONING (CER) ARGUMENT UNITS
<!-- Repeat this block for every substantive scientific argument (ARG_01, ARG_02, ...) -->

### ARGUMENT_UNIT_ID: [e.g., arg_01_shear_thickening]
- **BAB_LOCATION**: [BAB II | BAB IV | BAB V]
- **CLAIM**: [Substantive assertion about phenomenon, mechanism, or empirical relationship]
- **CLAIM_TYPE**: [OBSERVATIONAL | DESCRIPTIVE | CORRELATIONAL | CAUSAL | THEORETICAL | INFERENTIAL]
- **CLAIM_STRENGTH**: [WEAK | MODERATE | STRONG; calibrated honestly to evidence strength]

#### Evidence Foundation & Directness
- **EVIDENCE**: [Direct observation, statistical measurement, literature finding, mathematical proof]
- **EVIDENCE_TYPE**: [EMPIRICAL_DATA | EXPERIMENTAL_RESULT | OBSERVATIONAL_RESULT | LITERATURE_EVIDENCE | THEORETICAL_DERIVATION | MEASUREMENT | SIMULATION]
- **EVIDENCE_DIRECTNESS**: [DIRECT | INDIRECT | DERIVED | SECONDARY | INFERRED]
  *(Rule: CAUSAL claim requires DIRECT or DERIVED evidence; cannot rely solely on INFERRED/SECONDARY)*
- **SOURCE_TRACEABILITY**: [Citation key, lab notebook dataset ID, or source knowledge unit ID: ku_014]

#### Reasoning, Counterpoint & Uncertainty
- **REASONING**: [Logical/theoretical derivation explaining how evidence necessitates the claim]
- **ALTERNATIVE_EXPLANATION**: [Competing hypothesis or confounding factor considered and ruled out]
- **LIMITATION**: [Experimental error bounds, sample size constraints, non-tested conditions]
- **UNCERTAINTY_STATE**: [KNOWN | SUPPORTED | INFERRED | UNCERTAIN | UNRESOLVED]
- **FORBIDDEN_FABRICATION_CHECK**: TRUE (Verification that all data/sources are non-fabricated)

---

## 4. CITATION & FABRICATION INTEGRITY CONTRACT
- **FABRICATION_POLICY**: ZERO_TOLERANCE (Never invent citations, authors, DOIs, or measurements)
- **UNSUPPORTED_DATA_HANDLING**: If empirical data is absent from source, classify as `UNCERTAIN` or `HYPOTHETICAL_DESIGN`; do not report fabricated values.
- **CITATION_TRACEABILITY**: Every factual claim must link directly to an identified knowledge unit or verified reference.

---

## 5. SCIENTIFIC ANTI-PATTERNS CHECKLIST
- [ ] NO Unsupported Rhetorical Claims (every major conclusion supported by CER block)
- [ ] NO Causal Overclaiming (never assert causation when evidence is only correlational or descriptive)
- [ ] NO Citation Dumping (every reference must play an active evidentiary role in the argument)
- [ ] NO Concealed Limitations (methodological boundaries and uncertainties must be stated transparently)
- [ ] NO Narrative Essay Masquerading (formal BAB hierarchy and technical prose discipline enforced)

---

## 6. SCIENTIFIC SELF-REVIEW AUDIT
- **CLAIM_EVIDENCE_COVERAGE**: [100% of major assertions mapped to supporting evidence]
- **FABRICATION_RISK_CHECK**: [VERIFIED: ZERO_FABRICATION; all references grounded in source]
- **UNCERTAINTY_DISCIPLINE**: [Inferences and open questions explicitly designated as UNRESOLVED/INFERRED]
- **ESSAY_COLLAPSE_RISK**: [VERIFIED: FALSE; rigorous Claim-Evidence-Reasoning structure upheld]
