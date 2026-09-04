# 06 — Resolution Trace

## Explainability and Observability

Resolver V2 attaches an explainable `ResolutionTrace` to every decision, eliminating magic scoring and exposing the exact reasons why a capability was chosen.

## Data Structures

```python
class ScoreBreakdown(BaseModel):
    intent_score: float = 0.0
    structure_score: float = 0.0
    pedagogical_role_score: float = 0.0
    visual_grammar_score: float = 0.0
    domain_score: float = 0.0
    format_score: float = 0.0
    density_score: float = 0.0
    tag_score: float = 0.0
    total_score: float = 0.0
    matched_dimensions: list[str] = Field(default_factory=list)

class ResolutionCandidate(BaseModel):
    capability_id: str
    display_name: str
    category: str
    family: str
    score: float
    breakdown: ScoreBreakdown
    reason: str

class ResolutionResult(BaseModel):
    step_id: str
    semantic_type: str
    selected_capability_id: str
    score: float
    is_fallback: bool = False
    candidates: list[ResolutionCandidate] = Field(default_factory=list)
    resolved_parameters: dict[str, Any] = Field(default_factory=dict)
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
```

## Trace Inspection Example

```json
{
  "step_id": "step_problem_01",
  "semantic_type": "problem_funnel",
  "selected_capability_id": "research.problem.funnel",
  "score": 85.0,
  "breakdown": {
    "intent_score": 30.0,
    "structure_score": 15.0,
    "pedagogical_role_score": 0.0,
    "visual_grammar_score": 15.0,
    "domain_score": 20.0,
    "format_score": 10.0,
    "density_score": 0.0,
    "tag_score": 15.0,
    "total_score": 85.0,
    "matched_dimensions": [
      "primary_intent",
      "visual_grammar",
      "domain_exact",
      "format_supported",
      "tags"
    ]
  },
  "candidates": [
    {
      "capability_id": "research.problem.funnel",
      "score": 85.0,
      "reason": "Primary intent match (narrow_scope); Grammar match (funnel); Domain match (research_education)"
    },
    {
      "capability_id": "presentation.concept_introduction",
      "score": 25.0,
      "reason": "Domain match (general)"
    }
  ]
}
```
