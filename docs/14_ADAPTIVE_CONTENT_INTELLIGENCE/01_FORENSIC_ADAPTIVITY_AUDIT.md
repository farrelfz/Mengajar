# 01 — Forensic Adaptivity Audit

## 1. Audit Objective & Code Investigation
This forensic audit examines how learner demographics, cognitive readiness, prerequisite structures, instructional duration, and multi-artifact distribution are handled in the existing codebase prior to Batch 12.

---

## 2. Forensic Findings (10 Core Architectural Questions)

### 1. Is `AudienceLevel` currently only enum metadata?
- **Status**: **YES / LARGELY PASSIVE METADATA**.
- In [`app/blueprints/content.py:28-35`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/blueprints/content.py#L28-L35), `AudienceLevel` is defined as `MIDDLE_SCHOOL`, `HIGH_SCHOOL`, `UNDERGRADUATE`, `POSTGRADUATE`, `PROFESSIONAL`.
- In [`app/blueprints/generator.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/blueprints/generator.py), `audience` is stored on `metadata.audience`, but does not systematically transform the raw vocabulary, equations, or abstraction level of extracted units.

### 2. Does `AudienceLevel` truly alter blueprint content, vocabulary, and formulas?
- **Status**: **PARTIAL IN DIRECTOR / NO IN CONTENT TRANSFORMATION**.
- In Batch 11 [`app/director/cognition.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/director/cognition.py), `prior_knowledge == NOVICE` triggers diagnostic warnings for cognitive leaps.
- However, raw mathematical representations (e.g. $\tau = rF\sin\theta$ vs $\vec{\tau} = \vec{r} \times \vec{F}$ vs scalar $\tau = F \times r$) and vocabulary terms (e.g. "gaya putar" vs "momen gaya" vs "torque tensor") are NOT yet transformed dynamically.

### 3. Is `LearningGoal` sufficiently granular?
- **Status**: **MACRO ONLY**.
- In [`app/director/contracts.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/director/contracts.py), `LearningGoal` represents a single high-level concept string. It lacks decomposed, atomic `SharedLearningObjective` items (e.g., LO1: Identify torque, LO2: Calculate scalar torque, LO3: Solve multi-body rotational equilibrium).

### 4. Does the Director currently understand prerequisite knowledge?
- **Status**: **NO / ISOLATED FIELD ONLY**.
- While `LearningStage` has a `prerequisites: list[str]` field, there is no `ConceptPrerequisiteGraph` to check whether a learner has mastered prerequisites or to inject `PREREQUISITE_CHECK` / `MICRO_REMEDIATION` stages.

### 5. Is `CognitiveLevel` only a validator or does it alter content generation?
- **Status**: **PRIMARILY A VALIDATOR**.
- `CognitiveProgressionPolicy` verifies rank progression (1–6). It does not actively re-tier task open-endedness, evidence requirements, or problem complexity.

### 6. Does instructional duration affect journey structure?
- **Status**: **MINIMAL / FORMAT PROXY ONLY**.
- Duration was not an explicit contract in `MaterialRequest`. Pacing was loosely approximated via format (presentation vs handout) rather than an explicit `InstructionalTimeBudget` (15m, 45m, 90m).

### 7. Can the pipeline generate more than one artifact from one semantic model?
- **Status**: **NO / SINGLE ARTIFACT PER JOB**.
- `MaterialProductionPipeline.produce_artifact()` accepts one `target_artifact` and renders one PDF.

### 8. If generating Presentation and Handout from the same concept, does the system just re-render the same content?
- **Status**: **YES / REDUNDANCY HAZARD**.
- The same content steps are passed to different CSS stylesheets and page layouts. There is no instructional role differentiation (e.g. Presentation = Visual hook, Handout = Comprehensive reference, Worksheet = Problem scaffold, Assessment = Mastery evidence).

### 9. Where is the risk of "format adaptation disguised as pedagogical adaptation"?
- **Risk Location**: When switching from A4 to 16:9 merely limits items per page without altering vocabulary, abstraction, pedagogical mission, or exercise difficulty.

### 10. Is the semantic source of truth still unified?
- **Status**: **YES / SOLID FOUNDATION**.
- `SemanticMaterialBlueprint` provides a clean, single source of truth from which adaptive projections and multi-artifact bundles can be derived.

---

## 3. Mandatory Architectural Invariants for Batch 12
1. **True Semantic Adaptation**: Middle School vs High School vs University must differ in vocabulary, abstraction, and mathematical formalism, NOT just page count.
2. **Pacing Intelligence**: 15m vs 45m vs 90m journeys must differ in pedagogical depth and scaffolded stages.
3. **Role Differentiation**: Bundles must allocate distinct, non-redundant educational roles to Presentation, Handout, Worksheet, Assessment, and Teacher Guide.
4. **Shared Semantic Traceability**: All bundle artifacts must trace back to shared atomic learning objectives.
