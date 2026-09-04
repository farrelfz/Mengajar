# 02 — Adaptive Content Architecture

## Architectural Evolution

Batch 12 introduces the **Adaptive Content Intelligence & Multi-Artifact Curriculum Engine**, transforming single-artifact generation into multi-tier, multi-artifact curriculum production:

```
                    SOURCE RAW KNOWLEDGE
                             │
                             ▼
                  [Content Intelligence]
                             │
                             ▼
              [Semantic Material Blueprint]
                             │
                             ▼
            [ADAPTIVE CONTENT TRANSFORMER]
             ┌───────────────┼───────────────┐
             │               │               │
      Learner Profile   Complexity     Prerequisite
        (SMP/SMA/Univ)    Profile          Graph
             │               │               │
             └───────────────┼───────────────┘
                             ▼
               [Adaptive Material Blueprint]
                             │
                             ▼
              [INTELLIGENT MATERIAL DIRECTOR]
                             │
                             ▼
                  [BUNDLE PLANNER ENGINE]
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   [Presentation]        [Handout]         [Worksheet]
   (Visual Anchor)      (Reference)      (Active Task)
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                [COHERENCE & COVERAGE VALIDATION]
                             │
                             ▼
               [HYBRID RENDER ENGINE (PDF)]
```

---

## Architectural Separation of Concerns
1. **Adaptation Layer (`app/adaptation/`)**: Determines *what conceptual level, vocabulary, and mathematical formalism* is appropriate for the learner.
2. **Director Layer (`app/director/`)**: Determines *how the pedagogical learning journey progresses*.
3. **Bundle Engine (`app/bundles/`)**: Determines *how shared learning objectives are allocated across complementary artifacts*.
4. **Composition & Rendering (`app/composition/`, `app/rendering/`)**: Realizes pixel-perfect physical geometry.
