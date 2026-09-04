"""
Human-readable summary generator for pipeline run tracing.
"""

from __future__ import annotations

from app.observability.tracing import active_reports
from app.observability.profiling import identify_bottlenecks


def generate_runtime_summary(run_id: str) -> str:
    """Format a detailed console summary of the execution run."""
    report = active_reports.get(run_id)
    if not report:
        return "No observability report found."

    summary = report.run_summary

    # Pipeline timeline breakdown
    stage_durations: dict[str, float] = {}
    for span in report.spans:
        if span.duration_ms and span.stage:
            stage_durations[span.stage] = (
                stage_durations.get(span.stage, 0.0) + span.duration_ms
            )

    timeline_lines = [
        f"   - {stage}: {dur:.1f} ms" for stage, dur in stage_durations.items()
    ]
    timeline_str = (
        "\n".join(timeline_lines)
        if timeline_lines
        else "   (No stage details recorded)"
    )

    # Resolve quality score metric
    quality_score = 0.0
    for metric in report.metrics:
        if "quality" in metric.name.lower() and "score" in metric.name.lower():
            quality_score = metric.value

    # Counter warning events
    warning_count = sum(
        1
        for event in report.events
        if event.level.value == "warning" or "warning" in event.message.lower()
    )

    # Extract primary bottleneck
    bottlenecks = identify_bottlenecks()
    top_bottleneck = "None"
    if bottlenecks:
        top = bottlenecks[0]
        top_bottleneck = f"{top['component']} ({top['percentage_of_run']}% of run)"

    # List produced lineage files
    artifact_lines = [
        f"   - {item.artifact_id} ({item.artifact_type})"
        for item in report.artifact_lineage
    ]
    artifacts_str = "\n".join(artifact_lines) if artifact_lines else "   - None"

    res = f"""
RUN SUMMARY
=================================

Run ID:
{summary.run_id}

Status:
{summary.status.upper()}

Total Duration:
{summary.duration_ms / 1000.0 if summary.duration_ms else 0.0:.2f} seconds

Pipeline Timeline:
{timeline_str}

Top Bottleneck:
{top_bottleneck}

Artifacts:
{artifacts_str}

Quality:
{quality_score:.2f}

Errors:
{len(report.errors)}

Warnings:
{warning_count}
"""
    return res.strip()
