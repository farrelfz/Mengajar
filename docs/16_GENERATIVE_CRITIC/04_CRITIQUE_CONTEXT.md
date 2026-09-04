# CRITIQUE CONTEXT & EVIDENCE ASSEMBLY
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Progressive Evidence Model
The Generative Critic does not require an all-or-nothing artifact bundle. Through [`CritiqueContextBuilder`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/critic/context.py), critics gracefully adapt to available pipeline stages:

- **Level 1 (Blueprint Only)**: Executes `StructuralCritic`, `SemanticCritic`, `AudienceCritic`, `ScientificRigorCritic`.
- **Level 2 (Blueprint + Composition)**: Adds `CognitiveLoadCritic`, `VisualCommunicationCritic`, `CapabilitySelectionCritic`, `RedundancyCritic`.
- **Level 3 (Blueprint + Composition + Director Journey)**: Adds full `PedagogicalCritic` and `NarrativeCritic`.
- **Level 4 (Full Context + Quality Report)**: Enriches all critics with physical PDF and rule verification diagnostics.

---

### 2. Available Evidence Tracking
Every `CritiqueContext` tracks its available inputs via `available_evidence_sources()`, which is recorded in the execution trace for transparent auditability.
