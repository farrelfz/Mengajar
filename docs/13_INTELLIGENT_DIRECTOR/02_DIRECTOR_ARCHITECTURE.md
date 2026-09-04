# 02 — Director Architecture

## Layered Intent Planning Architecture

The Intelligent Material Director functions as an autonomous pedagogical and narrative planning layer situated directly above Capability Resolution:

```
[RAW CONTENT / IDEA]
       │
       ▼
[Content Intelligence] (Extracts raw concepts, claims, facts)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                 INTELLIGENT MATERIAL DIRECTOR               │
│                                                             │
│  - Analyzes Goal (Concept, Expected Outcome)                │
│  - Analyzes Audience (Education Level, Knowledge State)     │
│  - Consults Domain Direction Policy                         │
│  - Selects / Validates Strategy (e.g. Concrete-to-Abstract) │
│  - Budgets Semantic Density per Format                      │
│  - Constructs Scaffolded LearningJourney                    │
│  - Validates Stage Transitions (Grammar & Cognitive Load)   │
│  - Choreographer emits CapabilityRequirements               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     RESOLVER V2 ENGINE                      │
│        (Selects best capability from 80+ library)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     COMPOSITION ENGINE                      │
│     (Calculates format geometry & physical pagination)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     HYBRID RENDER ENGINE                    │
│           (Jinja2 HTML + Vector SVG + Playwright)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Invariant Guarantees
1. **Decoupled Intent**: Director plans *pedagogical intent* (`CapabilityRequirement`), never concrete capability IDs.
2. **Purity of Resolution**: Resolver V2 remains the sole authority for matching capabilities to intent.
3. **Purity of Geometry**: Director reasons purely in terms of semantic density (`MINIMAL`, `FOCUSED`, `ANALYTICAL`), never pixel/pt/CSS values.
