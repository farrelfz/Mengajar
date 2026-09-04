# FALSE-POSITIVE SAFEGUARDS & SYSTEM LIMITATIONS
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. False-Positive Safeguards
1. **HTML Markup Stripping**: Cleaned plain-text extraction prevents SVG definitions and HTML structural tags from falsely triggering slide overdensity.
2. **Short-Span Exclusion**: Short navigational labels ($< 50$ chars) are excluded from duplicate block detection.
3. **Format Tolerance**: 2.0 pt tolerance on PDF dimension checks avoids rounding artifacts from PDF point conversions.

### 2. Explicit System Boundaries (What Batch 15 Does NOT Do)
- **No External Fact-Checking**: Batch 15 assesses internal semantic and structural consistency, not external truth (belongs to Batch 19 Knowledge Grounding).
- **No Content Rewriting**: Batch 15 does not rewrite content or modify layouts (belongs to Batch 16 Generative Critic and Batch 17 Iterative Refinement).
- **No Learner Personalization**: Batch 15 does not adapt dynamically per individual student (belongs to Batch 18).
