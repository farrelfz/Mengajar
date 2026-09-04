# CONVERGENCE & OSCILLATION DETECTION
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. State Fingerprinting (`app/refinement/convergence.py`)
Computes a SHA-256 hash of:
$$\text{Fingerprint} = \text{hash}(\text{quality\_score}, \text{sorted\_finding\_ids}, \text{page\_count})$$

### 2. Oscillation Guard
If the current fingerprint matches any previously recorded fingerprint in history, the controller immediately stops with `STOP_OSCILLATION` to avoid endless circular thrashing ($A \to B \to A$).
