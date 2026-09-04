# ARCHITECTURE — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/ARCHITECTURE.md`  
> **Tujuan:** Mendefinisikan arsitektur sistem secara menyeluruh  
> **Dependency:** README.md  
> **Dokumen terkait:** DOMAIN_SCHEMA.md, AI_SETUP.md, PDF_RENDERING.md, MASTER_IMPLEMENTATION_SPEC.md

---

## 1. Purpose

Dokumen ini mendefinisikan:
- System context dan batasan sistem
- Layer architecture dan aturan dependency antar layer
- Tanggung jawab setiap modul
- Pipeline arsitektur dari input ke output
- Job lifecycle dan state machine
- Artifact management
- Configuration flow
- Error propagation strategy
- Extensibility dan observability

Dokumen ini adalah **kontrak arsitektur**. Setiap keputusan implementasi yang bertentangan dengan dokumen ini harus didiskusikan dan dokumen ini diperbarui terlebih dahulu — bukan diabaikan.

---

## 2. Scope

- Arsitektur internal sistem KIR AI Document Intelligence
- Dependency rules antar layer dan modul
- Pipeline dari source material ke PDF final

## 3. Non-Scope

- Detail implementasi setiap modul (lihat dokumen spesifik)
- Schema field secara detail (lihat DOMAIN_SCHEMA.md)
- Konfigurasi AI provider (lihat AI_SETUP.md)
- CSS dan HTML template (lihat PDF_RENDERING.md)

---

## 4. System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL ACTORS                          │
│                                                             │
│  User (via CLI)     9Router (AI Provider)    Ollama (Local) │
└────────┬───────────────────┬──────────────────┬────────────┘
         │                   │                  │
         ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 KIR AI DOCUMENT INTELLIGENCE                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Presentation │  │  AI Layer    │  │ Rendering Layer  │  │
│  │   (CLI)      │  │  (Agents)    │  │  (Playwright)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Application Layer                       │  │
│  │         (Pipeline Orchestration)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Domain Layer                          │  │
│  │  (Document, Blueprint, Page, Component, Theme, ...)  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Infrastructure Layer                     │  │
│  │  (AI Provider Client, Filesystem, Playwright, Cache) │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT                                 │
│            PDF File (A4 Tutorial / Presentation 16:9)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Layer Architecture

Sistem menggunakan **layered architecture** dengan aturan dependency yang ketat:

```
┌──────────────────────────────────────┐
│          Presentation Layer          │  ← app/main.py, CLI
│  (CLI commands, user interaction)    │
└───────────────────┬──────────────────┘
                    │ depends on
                    ▼
┌──────────────────────────────────────┐
│          Application Layer           │  ← app/core/, app/agents/
│  (Pipeline orchestration, use cases) │
└───────────────────┬──────────────────┘
                    │ depends on
                    ▼
┌──────────────────────────────────────┐
│            Domain Layer              │  ← app/document/, app/design/
│  (Business objects, rules, schemas)  │
└───────────────────┬──────────────────┘
                    │ ← depends on Domain (via interface)
┌──────────────────────────────────────┐
│        Infrastructure Layer          │  ← app/ai/, app/rendering/
│  (AI clients, Playwright, storage)   │
└──────────────────────────────────────┘
```

### Aturan Dependency yang WAJIB dipatuhi:

| Layer | Boleh bergantung ke | TIDAK BOLEH bergantung ke |
|---|---|---|
| Presentation | Application, Domain | Infrastructure langsung |
| Application | Domain, Infrastructure (via interface) | — |
| Domain | — | Presentation, Application, Infrastructure |
| Infrastructure | Domain (untuk schema) | Presentation, Application |

**Domain layer adalah inti yang bebas dari ketergantungan eksternal.**

Domain tidak boleh mengimport:
- `playwright`
- `openai` (atau client AI apapun)
- `requests` / `httpx` untuk memanggil AI
- Implementasi filesystem spesifik
- `app.ai.*`
- `app.rendering.*`

---

## 6. Module Responsibilities

### app/main.py

- Entry point aplikasi
- Mendaftarkan CLI commands
- Tidak boleh mengandung business logic

### app/config/

- Memuat konfigurasi dari environment variables
- Menggunakan Pydantic Settings
- Menyediakan `AppSettings` sebagai objek konfigurasi tunggal
- Harus diinisialisasi sekali dan di-inject ke seluruh sistem

**TIDAK BOLEH:**
- Mengakses `os.environ` langsung di luar module ini
- Hardcode nilai apapun

### app/core/

- Mengatur pipeline utama: `DocumentPipeline`
- Mengkoordinasikan antar agent dan rendering
- Mengelola state: `JobState`, `PipelineContext`
- Menangani error propagation

### app/ai/

- Abstraksi provider AI: `AIProvider` interface
- Implementasi: `NineRouterProvider`, `OllamaProvider`
- Retry logic, fallback, timeout
- Structured output parsing
- TIDAK BOLEH mengandung business logic dokumen

### app/agents/

- `DocumentPlannerAgent`
- `ContentWriterAgent`
- `DesignDirectorAgent`
- `QualityCriticAgent`

Setiap agent menerima input yang terdefinisi dan menghasilkan output yang terdefinisi. Agent berkomunikasi via Domain objects — bukan via raw string.

### app/document/

- Domain objects: `Document`, `Section`, `Page`, `Component`, `Blueprint`
- Validation logic
- Schema tidak bergantung pada implementasi AI manapun

### app/design/

- `Theme` objects dan theme registry
- Page type registry
- Component registry
- Design decision logic

### app/quality/

- `QualityInspector`
- `QualityReport`, `QualityIssue`
- Scoring engine
- Revision policy

### app/rendering/

- `DocumentComposer`: Blueprint → HTML string
- `PlaywrightRenderer`: HTML → PDF
- Template management via Jinja2
- Asset loading (fonts, icons)
- TIDAK BOLEH mengandung business logic; hanya eksekusi rendering

---

## 7. Pipeline Architecture

Pipeline adalah urutan transformasi deterministik dari source material ke PDF:

```
[INPUT]
Source Material (file: .txt, .md, .docx)
      │
      ▼
[STEP 1] CONTENT INGESTION
  Module: app/core/ingestion.py
  Output: RawContent object
  Failure: FileNotFoundError, UnsupportedFormatError
      │
      ▼
[STEP 2] CONTENT NORMALIZATION
  Module: app/core/normalization.py
  Output: NormalizedContent object
  Failure: NormalizationError
      │
      ▼
[STEP 3] CONTENT INTELLIGENCE  [← AI call: PLANNER_MODEL]
  Module: app/agents/planner.py
  Output: AnalysisResult object
  Failure: AIProviderError, SchemaValidationError
      │
      ▼
[STEP 4] INFORMATION CLASSIFICATION  [← AI call: WRITER_MODEL]
  Module: app/agents/writer.py
  Output: ContentUnit[] (dengan classification)
  Failure: ClassificationError
      │
      ▼
[STEP 5] DOCUMENT PLANNING  [← AI call: PLANNER_MODEL]
  Module: app/agents/planner.py
  Output: DocumentPlan object
  Failure: PlanningError
      │
      ▼
[STEP 6] BLUEPRINT GENERATION  [← AI call: DESIGN_MODEL]
  Module: app/agents/design_director.py
  Output: Blueprint (JSON, unvalidated)
  Failure: AIProviderError, JSONParseError
      │
      ▼
[STEP 7] BLUEPRINT VALIDATION
  Module: app/document/blueprint.py (Pydantic)
  Output: Blueprint (validated)
  Failure: SchemaValidationError → repair prompt → retry (max 3x)
      │
      ▼
[STEP 8] CONTENT COMPOSITION
  Module: app/core/composer.py
  Output: Blueprint (dengan konten terisi penuh)
  Failure: CompositionError
      │
      ▼
[STEP 9] DESIGN DECISION
  Module: app/design/decision.py
  Output: Blueprint (dengan theme dan page type terpilih)
  Failure: ThemeNotFoundError, PageTypeNotFoundError
      │
      ▼
[STEP 10] PAGE COMPOSITION
  Module: app/core/page_composer.py
  Output: RenderedPage[] (HTML string per halaman)
  Failure: CompositionError, OverflowError → split halaman
      │
      ▼
[STEP 11] HTML/CSS RENDERING
  Module: app/rendering/composer.py + Jinja2
  Output: HTML file (complete document)
  Failure: TemplateError, AssetNotFoundError
      │
      ▼
[STEP 12] BROWSER PDF EXPORT
  Module: app/rendering/playwright_renderer.py
  Output: PDF file (raw)
  Failure: PlaywrightError, TimeoutError
      │
      ▼
[STEP 13] QUALITY INSPECTION
  Module: app/quality/inspector.py
  Output: QualityReport
  Failure: InspectionError
      │
      ▼
[STEP 14] QUALITY EVALUATION
  Decision:
    IF score >= threshold AND no CRITICAL issues:
      → FINAL PDF
    ELSE IF revision_count < MAX_REVISIONS:
      → TARGETED REVISION (kembali ke Step 10 untuk halaman bermasalah)
    ELSE:
      → CONTROLLED ERROR dengan QualityReport
      │
      ▼
[OUTPUT]
FINAL PDF (A4 Landscape atau 16:9 Presentation)
```

---

## 8. Job Lifecycle

Setiap eksekusi pipeline disebut **RenderJob**. RenderJob memiliki lifecycle:

```
CREATED
   │
   ▼ (pipeline dimulai)
RUNNING
   │
   ├── [success] ──────────────────────────────────→ COMPLETED
   │
   ├── [quality OK setelah revisi] ─────────────→ COMPLETED
   │
   ├── [quality FAIL, revisi habis] ────────────→ FAILED_QUALITY
   │
   ├── [AI provider error, fallback habis] ─────→ FAILED_AI
   │
   └── [render error] ─────────────────────────→ FAILED_RENDER
```

Setiap state transition harus dicatat dengan timestamp.

### JobState Object

```python
class JobState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED_QUALITY = "failed_quality"
    FAILED_AI = "failed_ai"
    FAILED_RENDER = "failed_render"
```

---

## 9. State Machine — Blueprint Validation

Blueprint Validation memiliki mekanisme retry:

```
AI generates Blueprint JSON
         │
         ▼
Pydantic validation
         │
    ┌────┴────┐
  PASS      FAIL
    │          │
    ▼          ▼ (attempt <= MAX_REPAIR_ATTEMPTS=3)
 Continue   Repair Prompt → AI → Re-validate
                │
           ┌────┴────┐
         PASS      FAIL (attempt > 3)
           │          │
           ▼          ▼
        Continue  SchemaValidationError (fatal)
```

---

## 10. Artifact Management

Setiap RenderJob menghasilkan artifacts yang disimpan di:

```
outputs/
└── jobs/
    └── {job_id}/           ← UUID-based job directory
        ├── metadata.json   ← job info, timestamps, status, config
        ├── source/         ← copy dari input file
        ├── normalized/     ← NormalizedContent JSON
        ├── analysis/       ← AnalysisResult JSON
        ├── blueprint/      ← Blueprint JSON (tervalidasi)
        ├── html/           ← HTML output sebelum PDF
        ├── quality/        ← QualityReport JSON
        ├── revisions/      ← revision artifacts (jika ada)
        │   └── rev_{n}/
        └── output/
            └── {document_name}.pdf
```

Artifact disimpan meski job gagal — untuk debugging.

`metadata.json` format:

```json
{
  "job_id": "uuid-v4",
  "created_at": "ISO-8601",
  "completed_at": "ISO-8601 or null",
  "status": "completed | failed_quality | failed_ai | failed_render",
  "mode": "a4-tutorial | presentation-16-9",
  "source_file": "relative path",
  "revision_count": 0,
  "error": null
}
```

---

## 11. Configuration Flow

```
.env file
    │
    ▼
AppSettings (Pydantic Settings)
    │
    ├── AIConfig
    │     ├── NineRouterConfig
    │     └── OllamaConfig
    │
    ├── ModelConfig
    │     ├── PLANNER_MODEL
    │     ├── WRITER_MODEL
    │     ├── DESIGN_MODEL
    │     └── CRITIC_MODEL
    │
    ├── PathConfig
    │     ├── input_dir
    │     ├── output_dir
    │     └── cache_dir
    │
    └── PipelineConfig
          ├── max_repair_attempts
          ├── max_revision_count
          └── quality_threshold
```

Konfigurasi diinisialisasi satu kali di startup dan di-inject sebagai dependency.

Detail: lihat [`AI_SETUP.md`](AI_SETUP.md)

---

## 12. Error Propagation

Sistem menggunakan hierarki exception yang terdefinisi:

```
KIRError (base)
├── ConfigurationError
│     ├── MissingEnvironmentError
│     └── InvalidConfigError
├── AIError
│     ├── AIProviderError
│     │     ├── APIConnectionError
│     │     ├── APIRateLimitError
│     │     └── APITimeoutError
│     ├── SchemaValidationError
│     └── MaxRetryExceededError
├── PipelineError
│     ├── IngestionError
│     ├── NormalizationError
│     ├── PlanningError
│     └── CompositionError
├── RenderError
│     ├── TemplateError
│     ├── AssetLoadError
│     └── PlaywrightError
└── QualityError
      ├── InspectionError
      └── QualityThresholdError
```

**Aturan error propagation:**
1. Setiap exception harus membawa context: `job_id`, `step`, `message`.
2. Exception tidak boleh di-swallow secara diam-diam (silent catch).
3. Error yang dapat di-retry harus dibedakan dari error fatal.
4. Log harus mencatat exception class, message, dan stack trace — tetapi TIDAK mencatat API key atau secret.

---

## 13. Extensibility Strategy

Sistem dirancang untuk dapat diperluas tanpa rewrite besar:

### Menambah AI Provider baru:
1. Implementasikan `AIProvider` interface di `app/ai/providers/`
2. Daftarkan di `ProviderRegistry`
3. Tambahkan konfigurasi di `AppSettings`

### Menambah Mode Dokumen baru:
1. Buat spesifikasi baru (seperti A4_TUTORIAL_SPECIFICATION.md)
2. Buat template HTML/CSS di `templates/`
3. Daftarkan page types di page type registry
4. Implementasikan di `app/design/`

### Menambah Page Type baru:
1. Definisikan schema di domain layer
2. Buat template HTML/CSS
3. Daftarkan di page type registry
4. Tambahkan ke page type selection logic

### Menambah Component baru:
1. Definisikan schema di domain layer
2. Buat template HTML/CSS
3. Daftarkan di component registry

---

## 14. Observability

Sistem harus menyediakan informasi yang cukup untuk debugging tanpa membutuhkan UI.

### Logging

- Library: Python standard `logging`
- Format: `[timestamp] [level] [module] message`
- Level: DEBUG, INFO, WARNING, ERROR
- Aturan:
  - INFO: lifecycle events (job started, step completed, job finished)
  - WARNING: retry attempt, fallback triggered, quality issue
  - ERROR: exception yang menyebabkan step gagal
  - DEBUG: detail intermediate (ukuran output AI, validation result)

### Output Progress (CLI)

Saat pipeline berjalan, user melihat progress:

```
[kir] Starting job abc123 (mode: a4-tutorial)
[kir] ✓ Content ingested (2.3KB)
[kir] ✓ Content normalized
[kir] → Analyzing content... [AI call: planner/qwen3-8b]
[kir] ✓ Analysis complete (12 content units)
[kir] → Generating blueprint... [AI call: design/qwen3-8b]
[kir] ✓ Blueprint validated (8 pages)
[kir] → Rendering...
[kir] ✓ HTML generated
[kir] ✓ PDF exported (8 pages, 1.2MB)
[kir] → Quality inspection...
[kir] ✓ Quality score: 87/100 (PASS)
[kir] ✓ Job complete: outputs/jobs/abc123/output/document.pdf
```

### Artifact Inspection

Semua intermediate artifacts disimpan di `outputs/jobs/{job_id}/` sehingga developer dapat memeriksa setiap tahap:

```bash
kir inspect job abc123 --step blueprint
kir inspect job abc123 --step quality
```

---

## 15. Directory Structure (Konseptual)

```
KIR/
├── app/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py           ← AIProvider interface
│   │   └── providers/
│   │       ├── nine_router.py
│   │       └── ollama.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── writer.py
│   │   ├── design_director.py
│   │   └── critic.py
│   ├── config/
│   │   ├── settings.py       ← AppSettings (Pydantic)
│   │   └── models.py         ← ModelConfig
│   ├── core/
│   │   ├── pipeline.py       ← DocumentPipeline
│   │   ├── ingestion.py
│   │   ├── normalization.py
│   │   └── composer.py
│   ├── document/
│   │   ├── schema.py         ← Domain objects
│   │   └── blueprint.py
│   ├── design/
│   │   ├── theme.py
│   │   ├── page_types.py
│   │   └── decision.py
│   ├── quality/
│   │   ├── inspector.py
│   │   └── scoring.py
│   ├── rendering/
│   │   ├── composer.py       ← Blueprint → HTML
│   │   └── playwright_renderer.py
│   └── main.py               ← CLI entry point
│
├── assets/
│   ├── fonts/
│   ├── icons/
│   ├── images/
│   └── generated/
│
├── data/
│   ├── input/
│   ├── processed/
│   ├── examples/
│   └── cache/
│
├── outputs/
│   ├── jobs/
│   └── benchmarks/
│
├── prompts/
│   ├── system/
│   ├── agents/
│   ├── document_types/
│   └── output/
│
├── templates/
│   ├── html/
│   ├── css/
│   └── document_types/
│
├── themes/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── docs/
```

---

## 16. Acceptance Criteria

Arsitektur dianggap benar jika:

- [ ] Domain layer tidak mengimport apapun dari `app.ai`, `app.rendering`, atau library eksternal seperti `playwright`, `openai`.
- [ ] Setiap step pipeline memiliki input type dan output type yang terdefinisi.
- [ ] Setiap exception memiliki `job_id` dan `step` dalam context-nya.
- [ ] AI output tidak pernah langsung diteruskan ke rendering engine tanpa validasi Pydantic.
- [ ] Artifact dari setiap job tersimpan di `outputs/jobs/{job_id}/`.
- [ ] `kir doctor` dapat memverifikasi seluruh environment tanpa menjalankan pipeline.
- [ ] Menambah AI provider baru tidak memerlukan perubahan di domain layer.
