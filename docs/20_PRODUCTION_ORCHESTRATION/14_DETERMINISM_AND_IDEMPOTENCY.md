# Determinism and Idempotency

This document details request fingerprinting, duplicate prevention, and replay verification.

## Idempotency
- **Idempotency Key**: Crypotographic SHA-256 fingerprint generated from the request inputs (prompt, domain, format, seed).
- **Registry Caching**: If the fingerprint matches an entry in the `IdempotencyRegistry`, the orchestrator immediately returns the cached job results without triggering re-computation.

## Determinism
If underlying agents and renderers run deterministically, the orchestrator guarantees:
1. Identical stage execution ordering.
2. Identical checkpoint structures.
3. Matching final states and artifacts.
The `ReplayEngine` compares runs to confirm execution invariance.
