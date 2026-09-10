# Phase 7 Operator Walkthrough

Start at `/intelligence`, select a job, then inspect its source-labelled timeline and the linked Quality, Repair, Convergence, Benchmark, Review, and Artifact records.

- Clean export: Timeline ends in `EXPORTED`; Quality displays the UQA decision and export eligibility; artifact inventory links final evidence.
- Repair success: compare ordered quality snapshots and repair iterations, then the final approved/exported snapshot.
- Repair failure: inspect strategy/mutation observations, zero-effect or regression evidence, and convergence escalation. No success is inferred from execution alone.
- Convergence failure: inspect authoritative iteration/state records, repeated-state or budget diagnostics when supplied, and the resulting manual-review/block terminal state.
- Benchmark regression: inspect certification/regression projection and baseline provenance supplied by the benchmark domain; the cockpit cannot change baseline.
- Human review: inspect independent review case/evidence/directive projection. A validated directive creates a governed new run; the original terminal job stays historical.
