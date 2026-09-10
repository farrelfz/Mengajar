# Phase 7 Production Read Model Schema

Directory layout:

```text
artifacts/read_models/jobs/{job_id}/
  manifest.json
  latest.json
  snapshots/snapshot_000001.json
```

`JobSnapshot` is schema-versioned (`7.0`) and contains `JobIdentity`, metadata, state, quality, repair, convergence, benchmark, review, artifact, observability, and diagnostics projections. Every projection carries `observed_value`, `source`, `timestamp`, and `schema_version`.

Snapshots are append-only and monotonic. Manifest entries include the SHA-256 of the canonical deterministic JSON. Write protocol: validate, deterministic serialize, temporary write + flush + fsync, atomic replace, hash, then atomic manifest/latest updates. On a missing/stale latest pointer, scan valid immutable snapshots and atomically rebuild latest; corrupt individual history is reported and isolated.
