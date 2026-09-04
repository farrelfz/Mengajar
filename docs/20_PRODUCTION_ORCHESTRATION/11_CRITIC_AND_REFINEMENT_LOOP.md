# Critic and Refinement Loop

This document details closed-loop iterative refinements, critic integrations, and stagnation limits.

## Convergence Execution
When the quality gate emits `REFINE`:
1. The **Generative Critic** evaluates current artifacts and proposes localized changes.
2. The **Refinement Engine** compiles patches.
3. The orchestrator re-runs quality checks.
4. The loop compares scores:
   - Score improved >= 0.02: continues refinement.
   - Score improved < 0.02: increments stagnation count.

## Loop Termination
The controller terminates early if:
- `iterations >= max_iterations` (max 3 cycles).
- `stagnation_count >= stagnation_limit` (max 2 consecutive stagnated runs).
- This prevents endless loops and guarantees execution convergence.
