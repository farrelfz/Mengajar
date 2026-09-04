# 06 — Pedagogical Choreography Engine

## Decoupled Taxonomy Requirements

The choreographer translates abstract learning stages into typed `CapabilityRequirement` objects:

```python
CapabilityRequirement(
    stage_type=LearningStageType.MISCONCEPTION,
    primary_intent=SemanticIntent.COMPARE,
    pedagogical_role=PedagogicalRole.MISCONCEPTION,
    preferred_family=CapabilityFamily.COMPARATIVE_REASONING,
    preferred_visual_grammar=VisualGrammar.COMPARISON,
    density=DensityProfile.FOCUSED,
    candidate_tags=["torque", "rotational_force"],
    fallback_intents=[SemanticIntent.EVALUATE],
)
```

Resolver V2 consumes these requirements and scores registered capabilities dynamically. The Director never contains hardcoded capability strings.
