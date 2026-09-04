# SCORING FORENSICS & PENALTY MECHANISMS
## BATCH 15.5 — ACCEPTANCE AUDIT & ADVERSARIAL VALIDATION

### 1. Mathematical Scoring Formula
Individual metric scores are bounded: $0.0 \le S_m \le 1.0$.

For each dimension $d \in D$:
$$S_d = \frac{\sum_{m \in M_d} S_m \cdot W_m}{\sum_{m \in M_d} W_m}$$

Composite Overall Score:
$$\text{Overall Score} = \min\left(1.0, \max\left(0.0, \frac{\sum_{d \in D} S_d \cdot W_d}{\sum_{d \in D} W_d}\right)\right)$$

### 2. Penalty & Severity Calibration
- **CRITICAL Violation** (e.g. 0 pages, wrong physical dimensions): Sets dimension score to $0.0$ and forces `QualityGateDecision.FAIL`.
- **ERROR Violation** (e.g. inverted pedagogy, empty concepts, 0-block pages): Deducts 0.35–0.50 from dimension score and triggers `QualityGateDecision.NEEDS_REFINEMENT`.
- **WARNING Violation** (e.g. slight overdensity, duplicate blocks, missing hook): Deducts 0.15–0.30 from dimension score; triggers `QualityGateDecision.PASS_WITH_WARNINGS`.
- **Monotonicity**: Verified in [`tests/quality/adversarial/test_quality_monotonicity.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/tests/quality/adversarial/test_quality_monotonicity.py) where incremental degradation yields strictly monotonically decreasing composite scores.
