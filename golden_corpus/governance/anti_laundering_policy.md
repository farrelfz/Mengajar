# ANTI-BENCHMARK-LAUNDERING POLICY & ENFORCEMENT

### 1. Invariant Statement
The benchmark infrastructure exists as a trustworthy, scientific evaluation memory. Attempts to artificially inflate certification rates by weakening benchmarks are actively intercepted and blocked by `AntiLaunderingGuard`.

### 2. Forbidden Laundering Patterns
The system detects and rejects the following pathological practices:
1. **LOWER_BASELINE_TO_PASS**: Reducing score targets after a generator mutation causes regressions.
2. **REMOVE_HARD_CASE**: Deleting or archiving difficult fixtures following test failures.
3. **WEAKEN_INVARIANT**: Disabling hard invariants (e.g. anti-spoiling, citation integrity) to pass ungrounded artifacts.
4. **SILENT_REFERENCE_REPLACEMENT**: Overwriting golden references without version increment.
5. **RETROACTIVE_SCORE_REWRITE**: Mutating historical baseline scores in place.

### 3. Enforcement
Upon detecting any unauthorized modification, `AntiLaunderingGuard` halts execution immediately and issues:
`BENCHMARK_LAUNDERING_ATTEMPT`
