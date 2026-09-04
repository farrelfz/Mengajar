# MULTI-PERSPECTIVE CRITIC CATALOG
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Catalog of 10 Perspective Critics
1. **`StructuralCritic` (`app/critic/structural.py`)**: Identifies empty compositions, unpopulated pages, and missing conceptual foundation layers.
2. **`SemanticCritic` (`app/critic/semantic.py`)**: Identifies objectives targeting undefined concepts and shallow/trivial concept definitions.
3. **`PedagogicalCritic` (`app/critic/pedagogical.py`)**: Identifies worked examples or practice exercises preceding concept formalization, and abrupt openings lacking cognitive hooks.
4. **`CognitiveLoadCritic` (`app/critic/cognitive_load.py`)**: Identifies simultaneous introduction of $>5$ novel concepts, slide overdensity ($>1500$ chars on 16:9), and split attention across $>7$ concurrent blocks.
5. **`NarrativeCritic` (`app/critic/narrative.py`)**: Identifies abrupt document terminations without synthesis or closure pages.
6. **`VisualCommunicationCritic` (`app/critic/visual.py`)**: Identifies visual monotony (identical region layout topology across all consecutive pages).
7. **`ScientificRigorCritic` (`app/critic/scientific.py`)**: Identifies correlation-causation fallacies and unsupported causal claims in scientific domains.
8. **`AudienceCritic` (`app/critic/audience.py`)**: Identifies advanced tertiary/graduate concepts (e.g. Lagrangian, Hamiltonian) inappropriately presented to high school learners.
9. **`CapabilitySelectionCritic` (`app/critic/capability_selection.py`)**: Identifies sequential processes formatted in parallel comparison blocks.
10. **`RedundancyCritic` (`app/critic/redundancy.py`)**: Identifies substantial duplicate paragraphs repeated across distinct pages.
