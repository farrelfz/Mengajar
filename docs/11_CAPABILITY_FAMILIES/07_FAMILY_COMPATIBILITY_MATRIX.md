# 07 — Family Compatibility & Resolution Matrix

## Semantic Intent to Family Mapping

| Semantic Intent | Compatible Families | Preferred Visual Grammars | Example Capabilities |
|---|---|---|---|
| `SEQUENCE` | `PROCESS_VISUALIZATION`, `STEPWISE_REASONING` | `PROCESS_FLOW`, `REASONING_FLOW` | `diagram.process_flow`, `research.experiment_workflow` |
| `COMPARE` | `COMPARATIVE_REASONING` | `COMPARISON`, `MATRIX` | `universal.comparison_matrix`, `pedagogy.misconception_correction` |
| `RELATE` | `RELATIONSHIP_MAPPING` | `ANNOTATED_DIAGRAM`, `MATRIX` | `research.variable_relationship_map` |
| `CLASSIFY` | `CONCEPT_STRUCTURE` | `CONCEPT_MAP`, `FUNNEL` | `universal.concept_hierarchy`, `research.problem.funnel` |
| `ARGUE` / `INVESTIGATE` | `EVIDENCE_ANALYSIS`, `STEPWISE_REASONING` | `REASONING_FLOW`, `CHECKPOINT_CARD` | `universal.evidence_chain`, `pedagogy.question_progression` |
| `DERIVE` | `STEPWISE_REASONING`, `QUANTITATIVE_ANALYSIS` | `EQUATION_CHAIN`, `TABLE` | `mathematics.equation_derivation`, `pedagogy.worked_example` |
| `INTRODUCE` / `HOOK` | `CONCEPT_STRUCTURE`, `TITLE_FRAMING` | `HERO`, `CONCEPT_PANEL` | `presentation.hero_statement`, `presentation.concept_introduction` |
| `ASSESS` | `ASSESSMENT_CHECKPOINT`, `STEPWISE_REASONING` | `CHECKPOINT_CARD` | `pedagogy.concept_checkpoint` |

---

## Enhanced Resolution Trace

Every resolution result in Resolver V2 records:
1. `family`: The structural family of the chosen capability.
2. `template_selected`: The underlying generative template invoked.
3. `family_candidates`: The distinct families present among top scored candidates.
4. `family_score`: Points awarded for explicit or implicit family alignment.
