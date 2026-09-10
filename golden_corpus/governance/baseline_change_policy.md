# BASELINE CHANGE & EVOLUTION GOVERNANCE POLICY

### 1. Purpose & Scope
This policy regulates all modifications, updates, and re-calibrations of historical quality baselines within the Universal Document Intelligence System V5.

### 2. Mandatory Lineage Requirements
Every proposed modification to a benchmark baseline MUST be accompanied by an auditable `BaselineMutationRecord` containing:
- `change_id`: Unique deterministic mutation identifier.
- `timestamp`: Epoch timestamp of proposed transition.
- `previous_baseline_reference`: Explicit reference key to the predecessor baseline.
- `change_reason`: Substantive, non-superficial rationale (minimum 15 characters).
- `change_classification`: One of the recognized governed classifications.
- `expected_quality_impact`: Formal statement describing expected shift in benchmark stringency.

### 3. Authorized Classifications
- `LEGITIMATE_CORRECTION`: Rectification of a proven measurement error or fixture defect.
- `POLICY_EVOLUTION`: Formally approved shift in system-wide quality thresholds.
- `MEASUREMENT_FIX`: Bug fix in comparison adapters or metric calculation formulas.
- `CORPUS_EXPANSION`: Addition of new reference fixtures without altering existing standards.
- `REFERENCE_REGENERATION`: Authorized update of golden artifact references.

### 4. Prohibited Actions
- Any change classified as `UNKNOWN_CHANGE` is strictly rejected.
- Silently lowering a baseline score target to disguise generator degradation is strictly prohibited and triggers `BENCHMARK_LAUNDERING_ATTEMPT`.
