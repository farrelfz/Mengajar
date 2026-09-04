# PLUGIN EXTENSIBILITY & DOMAIN-SPECIFIC CRITICS
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Critic Registry Interface (`app/critic/registry.py`)
External domain modules and plugins can register custom critics dynamically without modifying `GenerativeCriticEngine`:

```python
from app.critic import BaseCritic, CriticPerspective, CritiqueFinding, CritiqueSeverity, CritiqueConfidence, CritiqueContext

class AdvancedQuantumCritic(BaseCritic):
    @property
    def critic_id(self) -> str:
        return "advanced_quantum_critic"

    @property
    def perspective(self) -> CritiquePerspective:
        return CritiquePerspective.SCIENTIFIC_RIGOR

    def can_critique(self, context: CritiqueContext) -> bool:
        return context.document_genre == "quantum_physics"

    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        # Custom domain analysis logic
        return []
```

### 2. Extensibility Verification
Verified in [`tests/critic/test_false_positives_and_plugins.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/tests/critic/test_false_positives_and_plugins.py) where custom domain critics dynamically register, execute in the panel, and seamlessly appear in synthesis and trace reports.
