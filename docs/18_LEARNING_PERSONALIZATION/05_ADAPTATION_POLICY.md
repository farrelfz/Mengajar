# ADAPTATION POLICIES
## BATCH 18 — LEARNING PERSONALIZATION & ADAPTIVE PEDAGOGICAL PROFILE SYSTEM

### 1. Macro Policies (`app/personalization/policies.py`)
- `BALANCED`: Standard adaptive policy adjusting density modifier (0.8 - 1.2) and scaffolding according to profile.
- `ACCESSIBILITY_FIRST`: Reduces cognitive load (density 0.75) and maximizes structural scaffolding (`FULL_SUPPORT`).
- `MASTERY_FIRST`: Increases density (1.25) and emphasizes independent challenge problems (`MINIMAL` scaffolding).
- `EXAM_PREPARATION`: Emphasizes stepwise worked solutions, diagnostic practice checkpoints, and transfer problems.
