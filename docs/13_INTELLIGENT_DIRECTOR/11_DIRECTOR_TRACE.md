# 11 — Explainable Director Trace

## Structured Decision Provenance

```json
{
  "strategy": "concrete_to_abstract",
  "strategy_reasons": [
    "Domain policy 'physics' scored highest (0.95) for 'concrete_to_abstract'.",
    "Audience knowledge state is 'novice'.",
    "Instructional intent is 'teach'."
  ],
  "stage_reasons": [
    {
      "stage": "hook",
      "purpose": "Stage 1: Concrete to Abstract Formalization — hook",
      "cognitive_level": "recognize"
    },
    {
      "stage": "concrete_experience",
      "purpose": "Stage 3: Concrete to Abstract Formalization — concrete_experience",
      "cognitive_level": "understand"
    }
  ],
  "policy_applied": "physics",
  "density_reason": "16:9 Presentation format requires high visual contrast and low information density per slide."
}
```
