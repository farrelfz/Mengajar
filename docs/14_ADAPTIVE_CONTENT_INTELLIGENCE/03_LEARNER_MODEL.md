# 03 — Multi-Dimensional Learner Model

## Decoupled Readiness Architecture

The system models learners across 8 distinct dimensions in `app/adaptation/contracts.py`:

```python
class LearnerProfile(BaseModel):
    educational_level: AudienceLevel          # Middle School, High School, Undergraduate, Researcher
    age_band: str                             # "12-15", "15-18", "18-22", "22+"
    knowledge_state: KnowledgeState           # NOVICE, DEVELOPING, INTERMEDIATE, ADVANCED
    prerequisite_mastery: dict[str, bool]     # {"scalar_forces": True, "vectors": False}
    mathematical_readiness: ComplexityLevel   # FOUNDATIONAL, INTERMEDIATE, ADVANCED, EXPERT
    scientific_reasoning_level: ComplexityLevel
    vocabulary_level: ComplexityLevel
    cognitive_readiness: CognitiveLevel       # RECOGNIZE, UNDERSTAND, APPLY, ANALYZE, EVALUATE
```

---

## Canonical Learner Profiles
- **Middle School (SMP)**: Foundational math, intuitive everyday analogies, non-vector representations.
- **High School (SMA)**: Intermediate trigonometry, scalar component models ($\tau = rF\sin\theta$).
- **Undergraduate**: Advanced vector calculus ($\vec{\tau} = \vec{r} \times \vec{F} = I\vec{\alpha}$).
- **Researcher**: Expert tensor formalisms ($\tau_i = \epsilon_{ijk} r_j F_k$).
