# LEARNER PROFILE CONTRACTS & DATA MODELS
## BATCH 18 — LEARNING PERSONALIZATION & ADAPTIVE PEDAGOGICAL PROFILE SYSTEM

### 1. The LearnerProfile Model (`app/personalization/contracts.py`)
Encapsulates independent, orthogonal pedagogical dimensions:
- `knowledge_level`: `KnowledgeLevel` (`NOVICE`, `BEGINNER`, `INTERMEDIATE`, `PROFICIENT`, `ADVANCED`).
- `prior_knowledge`: `PriorKnowledgeState` (`NONE`, `FRAGMENTED`, `BASIC`, `SOLID`, `STRONG`).
- `cognitive_support`: `CognitiveSupportNeed` (`HIGH_SUPPORT`, `GUIDED`, `MODERATE`, `INDEPENDENT`, `CHALLENGE_ORIENTED`).
- `abstraction_preference`: `AbstractionPreference` (`CONCRETE_FIRST`, `CONCRETE_TO_ABSTRACT`, `BALANCED`, `ABSTRACT_READY`, `FORMAL_FIRST`).
- `density_tolerance`: `DensityTolerance` (`LOW`, `MEDIUM_LOW`, `MEDIUM`, `MEDIUM_HIGH`, `HIGH`).
- `pacing`: `PacingPreference` (`SLOW`, `MODERATE`, `FAST`, `ACCELERATED`).
- `assessment_readiness`: `AssessmentReadiness` (`FOUNDATIONAL`, `PRACTICE_READY`, `APPLICATION_READY`, `TRANSFER_READY`, `MASTERY_READY`).
- `preferred_representations`: List of `PreferredRepresentation` (`TEXTUAL`, `VISUAL`, `DIAGRAMMATIC`, `SYMBOLIC`, `QUANTITATIVE`, `MIXED`).
- `learning_goal`: `LearningGoalType` (`UNDERSTAND`, `PRACTICE`, `APPLY`, `ANALYZE`, `CREATE`, `PREPARE_FOR_EXAM`, `CONDUCT_RESEARCH`, `TEACH_OTHERS`).
- `misconception_risks`: List of `MisconceptionRiskItem`.
