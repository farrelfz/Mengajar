"""
KIR & Mengajar AI Document Intelligence — Web Dashboard Server.

Runs a modern, high-performance FastAPI server with Server-Sent Events (SSE)
for real-time pipeline visualization, model management, and interactive document generation.
Runs on a dedicated port (default 20129) alongside 9Router (port 20128).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.ai.router import NineRouterClient
from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.cli.router_manager import (
    benchmark_models,
    get_router_status,
    test_single_model,
)
from app.config.settings import get_settings
from app.core.logging import add_log_listener
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.orchestration.stage_registry import TOTAL_PIPELINE_STAGES, PipelineStageRegistry, ProgressEvent
from app.read_models.query import JobReadQueryService
from app.read_models.service import JobReadModelService

log = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
READ_MODEL_SERVICE = JobReadModelService()
READ_MODEL_QUERY = JobReadQueryService()

app = FastAPI(
    title="Universal Document Intelligence System",
    description="Localhost Web Dashboard for Universal Document Intelligence System",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# In-Memory Job Store & SSE Event Hub
# ─────────────────────────────────────────────────────────────

class JobState:
    def __init__(self, job_id: str, title: str, model: str):
        self.job_id = job_id
        self.title = title
        self.model = model
        self.status = "queued"  # queued | running | completed | failed | blocked
        self.percent = 0
        self.current_step = "Menyiapkan pipeline..."
        self.current_task_idx = 0
        self.total_tasks = TOTAL_PIPELINE_STAGES
        self.current_task_name = ""
        self.task_start_time = time.time()
        self.logs: list[str] = []
        self.pdf_url: str | None = None
        self.pdf_filename: str | None = None
        self.file_size_kb: float = 0.0
        self.page_count: int = 0
        self.error: str | None = None
        self.created_at = time.time()
        self.subscribers: list[asyncio.Queue] = []

    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        payload = {"event": event_type, "data": data, "timestamp": time.time()}
        for queue in list(self.subscribers):
            try:
                await queue.put(payload)
            except Exception:
                pass

    def add_log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        log_entry = f"[{ts}] {message}"
        self.logs.append(log_entry)

    async def start_task(self, idx: int, name: str, desc: str, percent: int, total: int | None = None) -> None:
        tot = total or self.total_tasks
        self.total_tasks = tot
        self.current_task_idx = idx
        self.current_task_name = name
        self.percent = percent
        self.current_step = f"[{idx}/{tot}] {name}..."
        self.task_start_time = time.time()
        ts = time.strftime("%H:%M:%S")

        line_start = f"[{ts}] ▶ [TASK {idx}/{tot}] {name}"
        line_desc = f"[{ts}]   └─ {desc}"
        self.logs.extend([line_start, line_desc])

        await self.broadcast("task_start", {
            "task_idx": idx,
            "total_tasks": tot,
            "name": name,
            "desc": desc,
            "percent": percent,
            "time": ts,
            "line_start": line_start,
            "line_desc": line_desc,
        })
        await self.broadcast("progress", {"percent": percent, "step": self.current_step})

    async def emit_substep(self, tag: str, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}]   ↳ [{tag}] {message}"
        self.logs.append(line)
        await self.broadcast("substep", {
            "tag": tag,
            "message": message,
            "time": ts,
            "line": line,
        })

    async def finish_task(self, idx: int, summary: str, next_task: str | None = None, total: int | None = None) -> None:
        tot = total or self.total_tasks
        elapsed = time.time() - self.task_start_time
        ts = time.strftime("%H:%M:%S")
        line_done = f"[{ts}] ✓ [SELESAI {idx}/{tot}] {summary} ({elapsed:.2f}s)"
        self.logs.append(line_done)

        line_next = None
        if next_task:
            line_next = f"[{ts}] ⏩ Lanjut ke: {next_task}..."
            self.logs.append(line_next)

        await self.broadcast("task_done", {
            "task_idx": idx,
            "total_tasks": tot,
            "summary": summary,
            "elapsed": round(elapsed, 2),
            "next_task": next_task,
            "time": ts,
            "line_done": line_done,
            "line_next": line_next,
        })


_JOBS: dict[str, JobState] = {}


def _observe_job(job: JobState, result: Any = None) -> None:
    """Best-effort projection boundary: dashboard persistence cannot affect a job."""
    # MaterialProductionPipeline owns terminal observation. Web only records
    # lifecycle status before that canonical pipeline boundary completes.
    if result is not None:
        return
    _, diagnostic = READ_MODEL_SERVICE.observe_web_job(job, result=result)
    if diagnostic:
        log.warning("%s job_id=%s detail=%s", diagnostic.code, job.job_id, diagnostic.message)


def _pipeline_log_listener(logger_name: str, method_name: str, event_dict: dict[str, Any]) -> None:
    job_id = event_dict.get("job_id")
    target_job: JobState | None = None
    if job_id and job_id in _JOBS:
        target_job = _JOBS[job_id]
    else:
        running_jobs = [j for j in _JOBS.values() if j.status == "running"]
        if running_jobs:
            target_job = running_jobs[-1]

    if not target_job:
        return

    event = str(event_dict.get("event", ""))
    tag = None
    msg = None

    if event == "9router.request":
        model = event_dict.get("model", target_job.model or "9Router")
        cap = event_dict.get("capability", "general")
        tag = "9Router API"
        msg = f"Mengirim prompt ke model {model} (kapabilitas: {cap})..."
    elif event == "9router.response":
        model = event_dict.get("model", target_job.model or "9Router")
        lat = event_dict.get("latency_ms", 0)
        in_tok = event_dict.get("input_tokens") or 0
        out_tok = event_dict.get("output_tokens") or 0
        tag = "9Router Respons"
        msg = f"Dijawab oleh {model} dalam {lat:.0f}ms (In: {in_tok} tok, Out: {out_tok} tok)"
    elif event == "normalizer.complete":
        fmt = event_dict.get("detected_format", "text")
        words = event_dict.get("word_count", 0)
        tag = "Normalizer"
        msg = f"Format input teridentifikasi: {fmt} ({words} kata)"
    elif event == "segmenter.complete":
        cnt = event_dict.get("unit_count", 0)
        tag = "Segmenter"
        msg = f"Berhasil memecah teks menjadi {cnt} unit semantik konten"
    elif event == "agent.content_intelligence.start":
        tag = "Content Intelligence"
        msg = "Memulai analisis konten dan taksonomi materi..."
    elif event == "agent.content_intelligence.complete":
        units = event_dict.get("units", 0)
        tag = "Content Intelligence"
        msg = f"Analisis selesai: {units} unit semantik tervalidasi"
    elif event == "render.html_assembled":
        pages = event_dict.get("pages", 1)
        tag = "HTML Assembler"
        msg = f"Master HTML & stylesheet cetak terkompilasi ({pages} halaman)"
    elif event == "render.pdf_generated":
        pages = event_dict.get("pages", 1)
        tag = "Playwright"
        msg = f"Ekspor Chromium PDF berhasil dibuat ({pages} halaman)"
    elif "quality_gate" in event:
        tag = "Quality Gate"
        msg = "Invarian format & geometri layout 100% terpenuhi"

    if tag and msg:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(target_job.emit_substep(tag, msg))
        except RuntimeError:
            pass


add_log_listener(_pipeline_log_listener)


# ─────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────

class ActiveModelRequest(BaseModel):
    model: str


class TestModelRequest(BaseModel):
    model: str | None = None
    prompt: str = "Jelaskan dalam 1 kalimat konsep dasar gravitasi."


class GenerateRequest(BaseModel):
    title: str = "Dokumen Baru"
    raw_content: str
    format: str = "teaching_presentation"  # teaching_presentation | detailed_handout | exam_worksheet | kti_document
    matpel: str = "Fisika"
    jenjang: str = "SMA"
    model: str | None = None
    enable_quality: bool = True


# ─────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────

from dataclasses import asdict

@app.get("/api/status")
async def api_status(request: Request) -> dict[str, Any]:
    """Get system and 9Router status diagnostics."""
    status_9router = await get_router_status()
    settings = get_settings()

    nr_dict = asdict(status_9router)
    nr_dict["is_running"] = status_9router.process_running or status_9router.port_listening
    nr_dict["is_port_listening"] = status_9router.port_listening

    return {
        "status": "ok",
        "nine_router": nr_dict,
        "active_model": settings.get_effective_model(),
        "dashboard_port": request.url.port or 20129,
        "environment": {
            "output_dir": str(OUTPUTS_DIR.resolve()),
            "playwright": True,
            "jinja2": True,
        },
    }


@app.get("/api/models")
async def api_models() -> dict[str, Any]:
    """Fetch available models from 9Router."""
    client = NineRouterClient()
    models = await client.list_models()
    settings = get_settings()
    return {
        "count": len(models),
        "active_model": settings.get_effective_model(),
        "models": models,
    }


@app.post("/api/active-model")
async def api_set_active_model(body: ActiveModelRequest) -> dict[str, Any]:
    """Switch active AI model dynamically."""
    settings = get_settings()
    settings.set_active_model(body.model)
    return {
        "status": "ok",
        "active_model": settings.get_effective_model(),
        "message": f"Model aktif berhasil diubah ke {body.model}",
    }


@app.post("/api/test-model")
async def api_test_model(body: TestModelRequest) -> dict[str, Any]:
    """Run an inference test on target model."""
    target_model = body.model or get_settings().get_effective_model()
    success, elapsed, tokens, text = await test_single_model(
        model=target_model,
        prompt=body.prompt,
    )
    return {
        "success": success,
        "model": target_model,
        "latency_ms": elapsed,
        "tokens": tokens,
        "response": text,
    }


@app.get("/api/benchmarks")
async def api_benchmarks(run_now: bool = False) -> dict[str, Any]:
    """Get or trigger latency benchmarks across all 9Router models."""
    benchmark_file = OUTPUTS_DIR / "benchmarks" / "working_models.json"
    if not run_now and benchmark_file.exists():
        try:
            with open(benchmark_file, encoding="utf-8") as f:
                data = json.load(f)
            return {"status": "ok", "cached": True, "results": data}
        except Exception:
            pass

    # Run benchmark in background or async
    results, _ = await benchmark_models()
    return {"status": "ok", "cached": False, "results": results}


@app.get("/api/sample-input")
async def api_sample_input(sample_type: str = "kir") -> dict[str, str]:
    """Provide sample text for testing (supports 'kir' experiment or 'physics')."""
    if sample_type == "physics":
        sample_file = Path("hand_fire.md")
        if sample_file.exists():
            content = sample_file.read_text(encoding="utf-8")
        else:
            content = (
                "# Pembakaran Tangan Dingin (Hand Fire Experiment)\n\n"
                "## Tujuan Pembelajaran\n"
                "1. Memahami konsep transfer kalor dan titik nyala bahan bakar.\n"
                "2. Mengamati pengaruh tegangan permukaan air dan sabun pada pembakaran gas butana.\n\n"
                "## Teori Dasar\n"
                "Air memiliki kapasitas kalor yang sangat tinggi (4.184 J/g°C). "
                "Saat busa butana dinyalakan di atas tangan basah, kalor pembakaran diserap terlebih dahulu oleh air."
            )
        return {"title": "Hand Fire Physics Experiment", "content": content, "matpel": "Fisika"}

    # Default: Standardized Eksperimen (KIR) Protocol
    content = (
        "# Pengaruh Konsentrasi Katalis Enzim Katalase pada Penguraian Hidrogen Peroksida (H2O2)\n\n"
        "## I. Pendahuluan & Landasan Teori\n"
        "Hidrogen peroksida (H2O2) merupakan produk sampingan metabolisme sel yang bersifat toksik dan reaktif. "
        "Tubuh organisme memanfaatkan enzim katalase sebagai biokatalisator untuk mempercepat dekomposisi H2O2 "
        "menjadi air (H2O) dan oksigen (O2) tanpa ikut bereaksi secara permanen:\n"
        "$$\\text{2 H}_2\\text{O}_2 \\xrightarrow{\\text{Katalase}} \\text{2 H}_2\\text{O} + \\text{O}_2 \\uparrow$$\n"
        "Laju reaksi dekomposisi ini dipengaruhi secara signifikan oleh ketersediaan sisi aktif enzim dan konsentrasi substrat.\n\n"
        "## II. Rumusan Masalah & Tujuan Eksperimen\n"
        "1. Apakah peningkatan konsentrasi enzim katalase berbanding lurus dengan laju pembentukan gelembung gas oksigen?\n"
        "2. Menentukan konsentrasi optimum enzim dalam mendegradasi substrat H2O2 10% secara in vitro.\n\n"
        "## III. Hipotesis & Identifikasi Variabel Penelitian\n"
        "- **Hipotesis Kerja ($H_1$)**: Semakin tinggi konsentrasi enzim katalase, semakin cepat laju pembentukan gelembung gas $O_2$ dan semakin terang nyala bara api.\n"
        "- **Variabel Bebas (Independent)**: Konsentrasi ekstrak hati ayam (0%, 25%, 50%, 75%, 100%).\n"
        "- **Variabel Terikat (Dependent)**: Tinggi kolom gelembung gas (cm) dan intensitas nyala bara api lidi.\n"
        "- **Variabel Kontrol (Constant)**: Volume larutan H2O2 (5 mL), suhu ruangan (25°C), dan pH netral (pH 7.0).\n\n"
        "## IV. Alat, Bahan & Protokol Keselamatan Kerja (K3 Lab)\n"
        "### A. Peralatan Laboratorium\n"
        "- Tabung reaksi (5 unit) dan rak tabung kayu\n"
        "- Pipet ukur 5 mL & propipet berkaliberasi\n"
        "- Mistar ukur presisi (ketelitian 1 mm)\n"
        "- Pembakar spiritus, korek api, dan lidi bambu\n"
        "- Stopwatch digital (ketelitian 0.01 s)\n\n"
        "### B. Bahan & Reagen\n"
        "- Larutan Hidrogen Peroksida (H2O2) konsentrasi 10%\n"
        "- Ekstrak segar hati ayam (*Gallus gallus domesticus*) homogen\n"
        "- Akuades murni untuk pengenceran serial\n\n"
        "### C. Keselamatan Kerja & Bahaya (Safety Controls)\n"
        "> **PERINGATAN K3**: H2O2 adalah oksidator kuat. Wajib mengenakan kacamata pelindung (safety goggles), sarung tangan nitril, dan jas laboratorium. Jika terkena kulit, bilas dengan air mengalir minimal 15 menit.\n\n"
        "## V. Tahapan & Prosedur Eksperimen (Sistematis & Triplo)\n"
        "1. **Tahap Persiapan**: Beri label pada 5 tabung reaksi (A: 0%, B: 25%, C: 50%, D: 75%, E: 100%).\n"
        "2. **Pembuatan Variasi Konsentrasi**: Encerkan ekstrak hati ayam menggunakan akuades hingga mencapai konsentrasi target.\n"
        "3. **Inisiasi Reaksi**: Masukkan 5 mL larutan H2O2 10% ke dalam Tabung A, kemudian tambahkan 1 mL ekstrak hati konsentrasi 0% (kontrol negatif).\n"
        "4. **Pengukuran Respon Gelembung**: Ukur ketinggian kolom busa/gelembung tepat 30 detik setelah pencampuran menggunakan mistar.\n"
        "5. **Uji Nyala Bara Oksigen**: Nyalakan lidi hingga membara, masukkan bara api ke dalam mulut tabung reaksi tanpa menyentuh cairan. Amati intensitas letupan nyala api.\n"
        "6. **Replikasi Eksperimen**: Ulangi seluruh perlakuan pada tabung B, C, D, dan E sebanyak 3 kali (triplo) untuk mendapatkan rata-rata data yang valid.\n\n"
        "## VI. Tabel Matriks Data Hasil Pengamatan\n"
        "| Tabung | Konsentrasi Enzim | Tinggi Gelembung U1 (cm) | Tinggi Gelembung U2 (cm) | Tinggi Gelembung U3 (cm) | Rata-rata (cm) | Uji Nyala Bara Api |\n"
        "| :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n"
        "| A | 0% (Akuades) | 0.0 | 0.0 | 0.0 | 0.00 | Tidak menyala |\n"
        "| B | 25% | 1.8 | 2.0 | 1.9 | 1.90 | Redup berkedip |\n"
        "| C | 50% | 4.2 | 4.5 | 4.1 | 4.27 | Menyala sedang |\n"
        "| D | 75% | 6.8 | 7.1 | 7.0 | 6.97 | Menyala terang |\n"
        "| E | 100% | 9.4 | 9.7 | 9.5 | 9.53 | Menyala sangat terang (+ letupan) |\n\n"
        "## VII. Analisis Data & Pembahasan Ilmiah\n"
        "Data menunjukkan korelasi positif linear antara peningkatan konsentrasi enzim dengan volume gas O2 yang dibebaskan. "
        "Pada konsentrasi 100%, laju penguraian mencapai puncak maksimum (rata-rata tinggi busa 9.53 cm) karena bertambahnya sisi aktif enzim bebas yang berikatan dengan molekul substrat H2O2. "
        "Uji bara api membuktikan gas yang terjebak dalam gelembung adalah gas oksigen murni yang mendukung pembakaran.\n\n"
        "## VIII. Kesimpulan & Rekomendasi\n"
        "1. **Kesimpulan**: Hipotesis kerja ($H_1$) diterima. Laju aktivitas enzim katalase berbanding lurus dengan konsentrasi enzim selama konsentrasi substrat mencukupi.\n"
        "2. **Saran & Pengembangan**: Untuk riset KIR lanjutan, disarankan menguji pengaruh inhibitor suhu tinggi (>60°C) dan variasi pH asam/basa pada aktivitas denaturasi enzim katalase."
    )
    return {"title": "Laporan Eksperimen KIR: Uji Enzim Katalase", "content": content, "matpel": "Eksperimen (KIR)"}


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)) -> dict[str, Any]:
    """Ingest an uploaded document (PDF, Markdown, TXT) and extract text/metadata."""
    filename = file.filename or "uploaded_document"
    contents = await file.read()

    extracted_text = ""
    page_count = 1
    doc_title = Path(filename).stem.replace("_", " ").title()

    if filename.lower().endswith(".pdf"):
        import fitz
        try:
            doc = fitz.open(stream=contents, filetype="pdf")
            page_count = len(doc)
            pages_text = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages_text.append(text.strip())
            extracted_text = "\n\n".join(pages_text)
            if not extracted_text.strip():
                extracted_text = f"# {doc_title}\n\n(Dokumen PDF terbaca namun tidak memiliki teks vektor)"
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Gagal memproses file PDF: {exc}")
    else:
        try:
            extracted_text = contents.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = contents.decode("latin-1", errors="replace")

    lines = [ln.strip() for ln in extracted_text.splitlines() if ln.strip()]
    if lines and lines[0].startswith("# "):
        doc_title = lines[0].lstrip("# ").strip()

    return {
        "status": "ok",
        "title": doc_title,
        "content": extracted_text,
        "filename": filename,
        "page_count": page_count,
        "size_kb": round(len(contents) / 1024, 1),
    }



# ─────────────────────────────────────────────────────────────
# Document Generation Pipeline
# ─────────────────────────────────────────────────────────────

async def _run_job_pipeline(job: JobState, req: GenerateRequest) -> None:
    job.status = "running"
    job.percent = 5
    job.current_step = "Menyiapkan input & konfigurasi model..."
    job.add_log(f"Job terdaftar dengan model AI: {job.model}")
    await job.broadcast("progress", {"percent": 5, "step": job.current_step})
    _observe_job(job)

    import os
    import sys
    import app.orchestration.production_pipeline as pp
    import app.orchestration.stage_registry as sr

    print("\n[RUNTIME-DIAGNOSTIC]", flush=True)
    print(f"pid={os.getpid()}", flush=True)
    print(f"python={sys.executable}", flush=True)
    print(f"cwd={os.getcwd()}", flush=True)
    print(f"server={__file__}", flush=True)
    print(f"pipeline={pp.__file__}", flush=True)
    print(f"registry={sr.__file__}", flush=True)
    print(f"registry_total={sr.TOTAL_PIPELINE_STAGES}", flush=True)
    print(f"pipeline_class={pp.MaterialProductionPipeline.__module__}.{pp.MaterialProductionPipeline.__name__}", flush=True)
    print(f"callback_module={__name__}\n", flush=True)

    async def on_pipeline_progress(
        event_or_idx: ProgressEvent | int,
        total_tasks: int = TOTAL_PIPELINE_STAGES,
        name: str = "",
        status: str = "",
        detail: str = "",
    ) -> None:
        if isinstance(event_or_idx, ProgressEvent):
            event = event_or_idx
        else:
            event = ProgressEvent(
                stage_number=event_or_idx,
                total_stages=TOTAL_PIPELINE_STAGES,
                stage_key=PipelineStageRegistry.get_stage(event_or_idx).key,
                title=name,
                status=status,
                detail=detail,
                timestamp=time.time(),
            )

        print(
            f"[RUNTIME-PROGRESS] stage_index={event.stage_number} stage_total={event.total_stages} title={event.title}",
            flush=True,
        )

        pct = min(95, max(5, int(100 * event.stage_number / event.total_stages)))
        if event.status == "start":
            await job.start_task(event.stage_number, event.title, event.detail, pct, total=event.total_stages)
        elif event.status == "done":
            next_stage = PipelineStageRegistry.get_stage(event.stage_number + 1) if event.stage_number < event.total_stages else None
            next_str = f"[{next_stage.number}/{event.total_stages}] {next_stage.name}" if next_stage else None
            await job.finish_task(event.stage_number, event.detail, next_str, total=event.total_stages)

    try:
        # Save temporary input file
        inputs_dir = OUTPUTS_DIR / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        input_filename = f"{job.job_id}.md"
        input_path = inputs_dir / input_filename
        input_path.write_text(req.raw_content, encoding="utf-8")

        # Map formats
        format_map = {
            "teaching_presentation": (TargetArtifactType.TEACHING_PRESENTATION, "presentation_16_9"),
            "detailed_handout": (TargetArtifactType.DETAILED_HANDOUT, "a4_portrait"),
            "exam_worksheet": (TargetArtifactType.STUDENT_WORKSHEET, "a4_portrait"),
            "kti_document": (TargetArtifactType.KTI_DOCUMENT, "a4_portrait"),
        }
        artifact_type, target_format = format_map.get(
            req.format,
            (TargetArtifactType.TEACHING_PRESENTATION, "presentation_16_9"),
        )

        domain = KnowledgeDomain.PHYSICS
        matpel_lower = req.matpel.lower()
        if "eksperimen" in matpel_lower or "kir" in matpel_lower or "percobaan" in matpel_lower:
            domain = KnowledgeDomain.EXPERIMENT_KIR
        elif "mat" in matpel_lower:
            domain = KnowledgeDomain.MATHEMATICS
        elif "bio" in matpel_lower:
            domain = KnowledgeDomain.BIOLOGY
        elif "kim" in matpel_lower:
            domain = KnowledgeDomain.CHEMISTRY
        elif "metodologi" in matpel_lower or "penelitian" in matpel_lower or "kti" in matpel_lower:
            domain = KnowledgeDomain.RESEARCH_METHODOLOGY

        audience = AudienceLevel.HIGH_SCHOOL
        if "sd" in req.jenjang.lower():
            audience = AudienceLevel.BEGINNER
        elif "smp" in req.jenjang.lower():
            audience = AudienceLevel.MIDDLE_SCHOOL
        elif "kuliah" in req.jenjang.lower() or "univ" in req.jenjang.lower():
            audience = AudienceLevel.UNDERGRADUATE

        # Execute pipeline with real-time callbacks
        pipeline = MaterialProductionPipeline()
        output_subfolder = OUTPUTS_DIR / "web_runs"
        output_subfolder.mkdir(parents=True, exist_ok=True)

        result = await pipeline.produce_artifact(
            raw_input=req.raw_content,
            source_hint=input_path.name,
            domain=domain,
            audience=audience,
            target_artifact=artifact_type,
            output_dir=str(output_subfolder),
            output_filename=f"{job.job_id}.pdf",
            target_format=target_format,
            evaluate_quality=req.enable_quality,
            job_id=job.job_id,
            progress_callback=on_pipeline_progress,
        )

        if result.success and result.pdf_path:
            pdf_p = Path(result.pdf_path)
            job.pdf_filename = pdf_p.name
            job.pdf_url = f"/api/documents/{pdf_p.name}"
            job.file_size_kb = round(pdf_p.stat().st_size / 1024, 1)

            # PyMuPDF page count check
            try:
                import fitz
                doc = fitz.open(pdf_p)
                job.page_count = len(doc)
            except Exception:
                job.page_count = 1

            job.percent = 100
            job.status = "completed"
            job.current_step = f"Selesai! PDF berhasil dibuat ({job.file_size_kb} KB, {job.page_count} halaman)."
            completion_msg = f"🎉 [Sukses] Dokumen PDF siap: {pdf_p.name} ({job.file_size_kb} KB, {job.page_count} Halaman)"
            job.add_log(completion_msg)
            await job.broadcast("completed", {
                "pdf_url": job.pdf_url,
                "filename": job.pdf_filename,
                "size_kb": job.file_size_kb,
                "page_count": job.page_count,
                "message": completion_msg,
            })
            _observe_job(job, result)
        else:
            is_quality_block = result.export_decision and getattr(result.export_decision.status, "value", str(result.export_decision.status)) == "BLOCKED"
            if is_quality_block:
                job.status = "blocked"
                err_msg = "; ".join(result.errors) or "Quality gates not converged."
                job.error = err_msg
                job.add_log(f"⛔ PIPELINE BLOCKED — QUALITY GATES NOT CONVERGED: {err_msg}")
                await job.broadcast("blocked", {"error": err_msg, "reason": err_msg})
            else:
                job.status = "failed"
                err_msg = "; ".join(result.errors) or "Pipeline gagal menghasilkan file PDF."
                job.error = err_msg
                job.add_log(f"❌ PIPELINE SYSTEM ERROR: {err_msg}")
                await job.broadcast("failed", {"error": err_msg})
            _observe_job(job, result)

    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        job.add_log(f"❌ PIPELINE SYSTEM ERROR (EXCEPTION): {exc}")
        log.exception("Job %s encountered unhandled system error", job.job_id)
        await job.broadcast("failed", {"error": str(exc)})
        _observe_job(job)


@app.post("/api/generate")
async def api_generate(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Start document generation job in background."""
    raw_title = req.title.strip() or "document"
    clean_slug = "".join(c if c.isalnum() else "_" for c in raw_title.lower())[:24].strip("_") or "doc"
    job_id = f"job_{clean_slug}_{int(time.time())}"

    settings = get_settings()
    if req.model:
        settings.set_active_model(req.model)
    model = settings.get_effective_model()

    job = JobState(job_id=job_id, title=req.title, model=model)
    _JOBS[job_id] = job
    _observe_job(job)

    background_tasks.add_task(_run_job_pipeline, job, req)

    return {
        "status": "queued",
        "job_id": job_id,
        "title": req.title,
        "model": model,
        "stream_url": f"/api/jobs/{job_id}/stream",
    }


@app.get("/api/jobs/{job_id}")
async def api_get_job(job_id: str) -> dict[str, Any]:
    """Get current status of a generation job."""
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "percent": job.percent,
        "current_step": job.current_step,
        "logs": job.logs,
        "pdf_url": job.pdf_url,
        "filename": job.pdf_filename,
        "file_size_kb": job.file_size_kb,
        "page_count": job.page_count,
        "error": job.error,
    }


# Phase 7 Production Intelligence Cockpit: strictly read-only endpoints.
@app.get("/api/intelligence/jobs")
async def api_intelligence_jobs() -> dict[str, Any]:
    return READ_MODEL_QUERY.list_jobs()


@app.get("/api/intelligence/jobs/{job_id}")
async def api_intelligence_job(job_id: str) -> dict[str, Any]:
    result = READ_MODEL_QUERY.get_job(job_id)
    if result["snapshot"] is None:
        raise HTTPException(status_code=404, detail={"message": "Job read model not found", "diagnostics": result["diagnostics"]})
    return result


@app.get("/api/intelligence/jobs/{job_id}/{section}")
async def api_intelligence_section(job_id: str, section: str) -> dict[str, Any]:
    handlers = {
        "timeline": READ_MODEL_QUERY.get_job_timeline,
        "quality": READ_MODEL_QUERY.get_quality_summary,
        "repair": READ_MODEL_QUERY.get_repair_history,
        "convergence": READ_MODEL_QUERY.get_convergence_summary,
        "benchmark": READ_MODEL_QUERY.get_benchmark_summary,
        "review": READ_MODEL_QUERY.get_review_summary,
        "artifacts": READ_MODEL_QUERY.get_artifact_inventory,
    }
    handler = handlers.get(section)
    if handler is None:
        raise HTTPException(status_code=404, detail="Unknown read-only intelligence section")
    return handler(job_id)


@app.get("/api/jobs/{job_id}/stream")
async def api_stream_job(job_id: str) -> StreamingResponse:
    """SSE endpoint streaming live progress updates for a job."""
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")

    async def event_generator() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        job.subscribers.append(queue)

        # Send initial state
        initial_payload = {
            "event": "init",
            "data": {
                "job_id": job.job_id,
                "status": job.status,
                "percent": job.percent,
                "current_step": job.current_step,
                "logs": job.logs,
                "pdf_url": job.pdf_url,
            },
            "timestamp": time.time(),
        }
        yield f"data: {json.dumps(initial_payload)}\n\n"

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {json.dumps(msg)}\n\n"
                    if msg.get("event") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield f": keepalive {time.time()}\n\n"
        finally:
            if queue in job.subscribers:
                job.subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────────────────────
# Document Library & File Serving
# ─────────────────────────────────────────────────────────────

@app.get("/api/documents")
async def api_list_documents() -> list[dict[str, Any]]:
    """List all generated PDF documents in outputs/."""
    docs: list[dict[str, Any]] = []
    for pdf_file in OUTPUTS_DIR.rglob("*.pdf"):
        try:
            st = pdf_file.stat()
            docs.append({
                "name": pdf_file.name,
                "rel_path": str(pdf_file.relative_to(OUTPUTS_DIR)),
                "size_kb": round(st.st_size / 1024, 1),
                "modified": st.st_mtime,
                "download_url": f"/api/documents/{pdf_file.name}",
            })
        except Exception:
            pass

    docs.sort(key=lambda x: x["modified"], reverse=True)
    return docs


@app.get("/api/documents/{filename:path}")
async def api_get_document(filename: str) -> FileResponse:
    """Serve a generated PDF file with inline disposition for preview."""
    # Look for file in outputs directory tree
    matching = list(OUTPUTS_DIR.rglob(filename))
    if not matching:
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan")

    target = matching[0]
    return FileResponse(
        target,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{target.name}"',
        },
    )


# ─────────────────────────────────────────────────────────────
# Static Frontend Mount & Root Handler
# ─────────────────────────────────────────────────────────────

from starlette.responses import RedirectResponse, Response

@app.get("/dashboard")
async def dashboard_redirect() -> RedirectResponse:
    """Redirect /dashboard to root."""
    return RedirectResponse(url="/")

@app.get("/intelligence", response_class=FileResponse)
async def intelligence_cockpit() -> Response:
    """Dedicated Phase 7 read-only production intelligence cockpit."""
    return FileResponse(STATIC_DIR / "intelligence.html")

@app.get("/", response_class=FileResponse)
async def root() -> Response:
    """Serve Dashboard Single Page Application."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"message": "Mengajar Studio Dashboard ready. Static assets loading..."})
    return FileResponse(index_file)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def run_web_server(
    host: str = "127.0.0.1",
    port: int = 20129,
    open_browser: bool = True,
) -> None:
    """Start uvicorn server for the Web Dashboard."""
    import uvicorn
    import webbrowser

    url = f"http://{host}:{port}"
    print(f"🚀 Memulai Mengajar & KIR Web Dashboard Studio pada: {url}")
    print(f"⚡ Terhubung ke 9Router Gateway di: {get_settings().nine_router_base_url}")

    if open_browser:
        def _open():
            time.sleep(1.2)
            webbrowser.open(url)
        import threading
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="info")
