# Test and Benchmark Results

This document records the exact metrics collected from the test suite and benchmark runs.

## Test Results
- **Pytest Output**: **271 / 271 PASSED** (0 regressions).
- Orchestration-specific unit/integration tests covered validation, state transitions, checkpoint stores, and retry policies.

## Benchmark Results

| Case ID | Scenario Name | Profile | Success | Terminal Status | Execution Duration | Stages Executed | Checkpoint Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** | Physics Material (Standard) | standard | Yes | `completed` | 1389.1 ms | 8 | 8 |
| **Case 2** | Research Methodology (Standard) | standard | Yes | `completed` | 1319.3 ms | 8 | 8 |
| **Case 3** | Academic Writing (Standard) | standard | Yes | `completed` | 1225.9 ms | 8 | 8 |
| **Case 4** | Personalized Learning Material | strict | Yes | `completed` | 1236.2 ms | 10 | 10 |
| **Case 5** | Grounding Contradiction Block | strict | No | `failed` | 1.0 ms | 2 | 2 |
| **Case 6** | Quality Failure + Refinement Loop | standard | Yes | `completed` | 1240.6 ms | 8 | 8 |
| **Case 7** | Rendering Retry Simulation | standard | Yes | `completed` | 1256.6 ms | 8 | 8 |
| **Case 8** | Checkpoint & Resumption | fast_preview | Yes | `completed` | 0.0 ms | 5 | 5 |
| **Case 9** | Strict Research Profile | strict | Yes | `completed` | 1269.6 ms | 10 | 10 |
| **Case 10** | Fast Preview Profile | fast_preview | Yes | `completed` | 1250.9 ms | 5 | 5 |
