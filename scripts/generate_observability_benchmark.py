"""
Batch 21 Observability & Runtime Intelligence Benchmark Runner.

Runs 5 production scenarios:
Case 1: Physics material
Case 2: Research methodology material
Case 3: Academic writing material
Case 4: Experiment design material
Case 5: Data literacy material

Measures tracing overhead and generates:
- outputs/observability_benchmark/<case_dir>/observability_manifest.json
- outputs/observability_benchmark/<case_dir>/runtime_summary.txt
- outputs/observability_benchmark/master_benchmark_manifest.json
"""

import json
import time
from pathlib import Path
from typing import Any

from app.agents.content_intelligence_agent import ContentIntelligenceAgent
from app.config.settings import AppSettings
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.normalizer import InputNormalizer
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.segmenter import ContentSegmenter
from app.intelligence.traceability_engine import ResearchTraceabilityEngine
from app.intelligence.visual_intent_detector import VisualIntentDetector
from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.intelligence.output_validator import OutputValidator
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.orchestration.checkpoints import InMemoryCheckpointStore
from app.orchestration.contracts import JobMetadata, ProductionJobRequest
from app.orchestration.engine import ProductionOrchestrator
from app.orchestration.idempotency import IdempotencyRegistry
from app.orchestration.stages.blueprint import BlueprintGenerationStage
from app.observability import (
    ObservabilityContextManager,
    export_report,
    generate_runtime_summary,
)


class MockBenchmarkAI(AIClient):
    @property
    def provider_name(self) -> str:
        return "mock_benchmark_ai"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [
            AICapability.SEMANTIC_REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.CRITIQUE,
        ]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        step = request.step or ""
        if "semantic_classification" in step:
            resp = '{"unit_id": "u", "content_type": "explanation", "reasons": ["Mocked"]}'
        elif "research_role_detection" in step:
            resp = '{"unit_id": "u", "content_type": "finding", "research_role": "research_finding", "kti_bab": "BAB_4", "is_core_component": true}'
        elif "relationship_extraction" in step:
            resp = '{"relationships": []}'
        elif "visual_intent_detection" in step:
            resp = '{"intents": []}'
        elif "quality_critique" in step:
            resp = '{"is_acceptable": true, "critical_issues": [], "warnings": []}'
        else:
            resp = "{}"

        return GenerationResponse(
            content=resp,
            model_used="mock-benchmark-model",
            provider=self.provider_name,
            capability_used=request.required_capability,
        )


def build_intel_agent() -> ContentIntelligenceAgent:
    mock_ai = MockBenchmarkAI()
    registry = ModelRegistry()
    registry.register(mock_ai)
    settings = AppSettings(
        primary_provider="mock_benchmark_ai",  # type: ignore
        fallback_to_ollama=False,
        offline_mode=False,
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)

    return ContentIntelligenceAgent(
        normalizer=InputNormalizer(),
        segmenter=ContentSegmenter(),
        classifier=SemanticClassifier(validator=validator),
        research_role_detector=ResearchRoleDetector(validator=validator),
        relationship_extractor=RelationshipExtractor(validator=validator),
        importance_scorer=ImportanceScorer(),
        visual_intent_detector=VisualIntentDetector(validator=validator),
        traceability_engine=ResearchTraceabilityEngine(),
    )


def run_benchmark():
    out_base = Path("outputs/observability_benchmark")
    out_base.mkdir(parents=True, exist_ok=True)
    IdempotencyRegistry.clear()

    chk_store = InMemoryCheckpointStore()
    orchestrator = ProductionOrchestrator(checkpoint_store=chk_store)
    fast_agent = build_intel_agent()
    orchestrator.register_stage(BlueprintGenerationStage(agent=fast_agent))

    print("=" * 80)
    print("BATCH 21 — OBSERVABILITY & RUNTIME INTELLIGENCE BENCHMARK")
    print("=" * 80)

    cases = [
        {
            "id": "case_01_physics",
            "name": "Case 1: Physics Educational Material",
            "domain": "physics",
            "profile": "standard",
            "raw_input": "Torque tau = r * F sin(theta). Rotational equilibrium occurs when sum of torques is zero.",
        },
        {
            "id": "case_02_research",
            "name": "Case 2: Research Methodology Material",
            "domain": "research_methodology",
            "profile": "standard",
            "raw_input": "An independent variable is manipulated while dependent variables are measured to test hypotheses.",
        },
        {
            "id": "case_03_academic",
            "name": "Case 3: Academic Writing Material",
            "domain": "general",
            "profile": "standard",
            "raw_input": "A coherent literature review synthesizes theoretical perspectives and compares empirical methodologies.",
        },
        {
            "id": "case_04_experiment",
            "name": "Case 4: Experiment Design Material",
            "domain": "general",
            "profile": "fast_preview",
            "raw_input": "Steps to establish double-blind control configurations in pharmacological trials.",
        },
        {
            "id": "case_05_data_literacy",
            "name": "Case 5: Data Literacy Material",
            "domain": "general",
            "profile": "fast_preview",
            "raw_input": "Interpreting standard deviations and statistical variances in graphical plots.",
        },
    ]

    case_summaries = []
    durations = []
    span_counts = []
    artifact_counts = []

    # 1. Execute Benchmark Cases
    for c in cases:
        print(f"\n[Running] {c['name']}...")
        req = ProductionJobRequest(
            job_id=c["id"],
            raw_input=c["raw_input"],
            metadata=JobMetadata(domain=c["domain"], profile=c["profile"]),
        )

        res = orchestrator.run(req)

        # Retrieve report from tracing active_reports
        from app.observability.tracing import active_reports
        # Find corresponding report
        report = None
        for r in active_reports.values():
            if r.run_summary.run_id == res.metadata.get("run_id") or any(s.stage == "finalization" for s in r.spans):
                # since we know the last added report is our run, retrieve it
                report = r
        if not report:
            report = list(active_reports.values())[-1]

        run_id = report.run_summary.run_id
        
        # Save individual manifest and summary
        case_dir = out_base / c["id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        
        # Export trace manifest
        manifest_data = export_report(run_id)
        (case_dir / "observability_manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        
        # Export runtime summary
        summary_text = generate_runtime_summary(run_id)
        (case_dir / "runtime_summary.txt").write_text(summary_text, encoding="utf-8")

        # Capture metrics
        durations.append(report.run_summary.duration_ms or 0.0)
        span_counts.append(report.run_summary.span_count)
        artifact_counts.append(report.run_summary.artifact_count)

        # Find primary bottleneck
        from app.observability.profiling import identify_bottlenecks
        bottlenecks = identify_bottlenecks()
        top_bottleneck = bottlenecks[0]["component"] if bottlenecks else "None"

        # Warning counts
        warning_count = sum(
            1 for e in report.events if e.level.value == "warning" or "warning" in e.message.lower()
        )

        entry = {
            "scenario": c["name"],
            "profile": c["profile"],
            "duration_ms": report.run_summary.duration_ms,
            "span_count": report.run_summary.span_count,
            "event_count": len(report.events),
            "metrics_count": len(report.metrics),
            "artifact_count": report.run_summary.artifact_count,
            "bottleneck": top_bottleneck,
            "warnings": warning_count,
            "failures": len(report.errors),
            "status": report.run_summary.status,
        }
        case_summaries.append(entry)
        print(f"  --> Status: {report.run_summary.status} | Spans: {report.run_summary.span_count} | Artifacts: {report.run_summary.artifact_count}")

    # 2. Measure Telemetry Overhead
    print("\nMeasuring Observability Instrumentation Overhead...")
    req_overhead = ProductionJobRequest(
        job_id="case_overhead",
        raw_input="Overhead test prompt query.",
        metadata=JobMetadata(domain="physics", profile="fast_preview"),
    )

    # Run A: Observability Disabled
    ObservabilityContextManager.set_enabled(False)
    t0_disabled = time.perf_counter()
    res_disabled = orchestrator.run(req_overhead)
    t1_disabled = time.perf_counter()
    dur_disabled = (t1_disabled - t0_disabled) * 1000.0

    # Run B: Observability Enabled
    ObservabilityContextManager.set_enabled(True)
    IdempotencyRegistry.clear()
    t0_enabled = time.perf_counter()
    res_enabled = orchestrator.run(req_overhead)
    t1_enabled = time.perf_counter()
    dur_enabled = (t1_enabled - t0_enabled) * 1000.0

    overhead_pct = ((dur_enabled - dur_disabled) / dur_disabled) * 100.0 if dur_disabled > 0 else 0.0
    print(f"  --> Disabled: {dur_disabled:.2f}ms | Enabled: {dur_enabled:.2f}ms | Overhead: {overhead_pct:.1f}%")

    # 3. Compile Master Manifest
    master_manifest = {
        "benchmark_version": "21.0",
        "cases": case_summaries,
        "observability_overhead_percent": round(overhead_pct, 2),
        "aggregate": {
            "total_runs": len(cases),
            "successful_runs": sum(1 for cs in case_summaries if cs["status"] == "completed"),
            "failed_runs": sum(1 for cs in case_summaries if cs["status"] == "failed"),
            "average_duration_ms": round(sum(durations) / len(durations), 1) if durations else 0.0,
            "average_span_count": round(sum(span_counts) / len(span_counts), 1) if span_counts else 0.0,
            "slowest_stage": max(case_summaries, key=lambda x: x["duration_ms"] or 0.0)["scenario"],
            "artifact_count": sum(artifact_counts),
        },
    }

    master_file = out_base / "master_benchmark_manifest.json"
    master_file.write_text(json.dumps(master_manifest, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print("ALL BATCH 21 OBSERVABILITY BENCHMARKS COMPLETE!")
    print(f"Master summary report written to: {master_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
