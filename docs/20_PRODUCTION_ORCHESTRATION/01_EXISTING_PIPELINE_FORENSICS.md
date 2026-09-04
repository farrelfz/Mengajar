# Existing Pipeline Forensics

## 1. Public Entry Points
The entry point to the generation process was `MaterialProductionPipeline` in [`production_pipeline.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py). It accepted requests via `produce_artifact` and coordinated all layers.

## 2. Problematic implicit coupling
* **State Mutation**: The personalization layer directly mutated the underlying blueprint, changing the pedagogical strategy which downstream elements relied upon without an immutable boundary.
* **Inline Feature Flags**: Numerous boolean flags (`enable_grounding`, `evaluate_quality`, `enable_refinement`) controlled routing, resulting in high complexity and implicit dependencies.

## 3. Failure Recovery & Resumability Gaps
* **Statelessness**: No state was cached between major stages. A transient network timeout or render glitch at the PDF generation phase forced the system to re-execute content intelligence, blueprint generation, and grounding from the very beginning.
* **Deterministic Replay Risks**: Random seeds and transient states were not captured inside a formal tracking envelope, making logical execution replays difficult to reproduce.
