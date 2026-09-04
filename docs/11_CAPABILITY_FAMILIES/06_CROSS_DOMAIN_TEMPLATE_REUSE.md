# 06 — Cross-Domain Template Reuse Proof

## Empirical Demonstration: 1 Template Reused Across 3 Distinct Domains

In `tests/capability_families/test_family_cross_domain_reuse.py`, the `LinearProcessTemplate` (`process.linear`) is deployed across 3 completely distinct academic domains:

```
                      ┌────────────────────────────┐
                      │    LinearProcessTemplate   │
                      │     ('process.linear')     │
                      └──────────────┬─────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ Research Edu     │       │ Physics          │       │ Pedagogy         │
│ Experiment       │       │ Problem Solving  │       │ Learning Journey │
│ Protocol         │       │ Protocol         │       │ Roadmap          │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

### Domain 1: Research Methodology
- **Capability ID**: `research.experiment_workflow_family`
- **Domain**: `research_education`
- **Rendered Output**: Formats Soil Inoculation and Drought Stress protocol steps.

### Domain 2: Classical Mechanics / Physics
- **Capability ID**: `physics.problem_solving_flow`
- **Domain**: `physics`
- **Rendered Output**: Formats 4-step Equilibrium problem-solving flow (Boundaries → FBD → Equilibrium Equations → Solve).

### Domain 3: General Pedagogy
- **Capability ID**: `pedagogy.learning_journey`
- **Domain**: `general`
- **Rendered Output**: Formats unit learning milestones (Limits → Derivatives → Integrals).

---

## Architectural Conclusion
All three capabilities:
- Were declared using `register_family_capability()`.
- Reused `LinearProcessTemplate` without writing any custom HTML or SVG code.
- Successfully passed unit testing and physical PDF rendering.
