# Export and Runtime Manifest

This document explains telemetry serialization and disk export structures.

## Runtime Manifest Format
The `export_json` function outputs a serialized `observability_manifest.json` file structured as follows:

```json
{
  "schema_version": "1.0.0",
  "run": {
    "run_id": "uuid",
    "trace_id": "uuid",
    "status": "completed",
    "started_at": 1724982181.23,
    "completed_at": 1724982193.45,
    "duration_ms": 12220.0,
    "stage_count": 8,
    "span_count": 8,
    "error_count": 0,
    "artifact_count": 3
  },
  "spans": [...],
  "events": [...],
  "metrics": [...],
  "errors": [...],
  "lineage": [...],
  "diagnostics": null
}
```

## Exporter Operations
- **export_report(run_id)**: Converts report models to dictionaries and sorts keys to guarantee structural determinism.
- **export_json(run_id, dest_path)**: Saves the formatted report output to the specified directory.
