# DOMAIN SCHEMA — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/DOMAIN_SCHEMA.md`  
> **Tujuan:** Mendefinisikan semua objek domain beserta field, relasi, validation rule, dan contoh JSON  
> **Dependency:** ARCHITECTURE.md  
> **Dokumen terkait:** COMPONENT_SPECIFICATION.md, AI_AGENT_ORCHESTRATION.md, CONTENT_TO_BLUEPRINT_ALGORITHM.md

---

## 1. Purpose

Dokumen ini adalah **kontrak data** untuk seluruh domain layer sistem KIR.

Semua objek yang didefinisikan di sini:
- Digunakan oleh agent AI sebagai output target
- Divalidasi oleh Pydantic sebelum diteruskan ke layer manapun
- Digunakan oleh rendering engine sebagai input
- Diserialisasi ke JSON untuk artifact storage

Setiap perubahan pada schema ini harus diikuti dengan:
1. Pembaruan versi schema
2. Pembaruan validation logic
3. Pembaruan prompt AI yang menghasilkan schema tersebut
4. Pembaruan test fixtures

---

## 2. Scope

Seluruh objek yang berada di `app/document/schema.py` dan `app/document/blueprint.py`.

## 3. Non-Scope

- Implementasi rendering (lihat PDF_RENDERING.md)
- Implementasi AI agent (lihat AI_AGENT_ORCHESTRATION.md)
- Component HTML/CSS template (lihat COMPONENT_SPECIFICATION.md)

---

## 4. Schema Versioning

Setiap schema memiliki field `schema_version` bertype `str` dengan format `"MAJOR.MINOR"`.

Aturan versioning:
- **MAJOR** naik jika terjadi breaking change (field required dihapus, type berubah)
- **MINOR** naik jika terjadi penambahan field optional

Saat ini: `schema_version = "1.0"`

---

## 5. Object Overview

```
RawContent (from Ingestion)
  └── produces → NormalizedContent (from Normalization)
        └── produces → AnalysisResult (from Content Intelligence)
              └── contains → ContentUnit[]

ContentUnit[] ──→ DocumentPlan (from Document Planner)
                    │
                    ▼
Document
  │
  ├── contains → Section[]
  │     └── contains → Page[]
  │           ├── references → PageType
  │           ├── contains → Component[]
  │           │     └── references → ComponentType
  │           └── references → Theme
  │
  ├── references → Blueprint ──→ validated by → ValidationResult
  │     └── contains → Page[]
  │
  ├── references → Theme
  │
  └── produces → RenderJob
        ├── produces → RenderArtifact[]
        └── produces → QualityReport
              └── contains → QualityIssue[]

ProviderConfig ← infrastructure config
ModelConfig ← infrastructure config
GenerationRequest ← AI call input
GenerationResponse ← AI call output
```

---

## 6. Object Definitions

---

### 6.1 ContentUnit

**Tujuan:** Unit informasi atomik yang diekstrak dari source material. Merupakan bahan baku sebelum diproses menjadi Blueprint.

**Tanggung jawab:**
- Merepresentasikan satu potongan informasi yang memiliki makna mandiri
- Memiliki klasifikasi tipe informasi
- Menjadi dasar page type selection

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `unit_id` | `str` | ✅ | UUID v4, unik per job |
| `content_type` | `ContentType` | ✅ | Enum — lihat definisi ContentType |
| `raw_text` | `str` | ✅ | Teks asli dari source material |
| `normalized_text` | `str` | ✅ | Teks setelah normalisasi |
| `title` | `str \| None` | ❌ | Judul unit jika teridentifikasi |
| `order` | `int` | ✅ | Urutan dalam dokumen asli (0-indexed) |
| `depth` | `int` | ✅ | Kedalaman hierarki (0 = top level) |
| `parent_unit_id` | `str \| None` | ❌ | ID parent unit jika bersarang |
| `related_unit_ids` | `list[str]` | ✅ | ID unit yang secara semantik terkait |
| `estimated_word_count` | `int` | ✅ | Perkiraan jumlah kata |
| `density_score` | `float` | ✅ | 0.0–1.0; semakin tinggi semakin padat |
| `metadata` | `dict[str, Any]` | ✅ | Metadata tambahan, default `{}` |

**ContentType Enum:**

```python
class ContentType(str, Enum):
    # ── General information types ─────────────────────────
    DEFINITION     = "definition"      # Mendefinisikan konsep atau istilah
    EXPLANATION    = "explanation"     # Menjelaskan cara kerja sesuatu
    SEQUENCE       = "sequence"        # Langkah-langkah berurutan
    COMPARISON     = "comparison"      # Membandingkan dua atau lebih hal
    CAUSE_EFFECT   = "cause_effect"    # Hubungan sebab-akibat
    HIERARCHY      = "hierarchy"       # Struktur bertingkat
    DATA           = "data"            # Angka, statistik, tabel
    EXAMPLE        = "example"         # Contoh konkret
    ACTIVITY       = "activity"        # Latihan atau tugas
    CHECKLIST      = "checklist"       # Daftar item to-check
    SUMMARY        = "summary"         # Ringkasan materi
    TITLE          = "title"           # Judul section/chapter
    INTRODUCTION   = "introduction"    # Pembuka topik

    # ── KTI / Research semantic roles ────────────────────
    RESEARCH_PROBLEM     = "research_problem"     # Permasalahan/latar belakang
    RESEARCH_QUESTION    = "research_question"    # Rumusan masalah
    RESEARCH_OBJECTIVE   = "research_objective"   # Tujuan penelitian
    RESEARCH_BENEFIT     = "research_benefit"     # Manfaat penelitian
    HYPOTHESIS           = "hypothesis"           # Hipotesis penelitian
    THEORETICAL_FOUNDATION = "theoretical_foundation" # Landasan teori
    PRIOR_RESEARCH       = "prior_research"       # Penelitian terdahulu
    RESEARCH_GAP         = "research_gap"         # Gap / posisi penelitian
    RESEARCH_METHOD      = "research_method"      # Desain / jenis penelitian
    RESEARCH_INSTRUMENT  = "research_instrument"  # Instrumen / sumber data
    DATA_COLLECTION      = "data_collection"      # Teknik pengumpulan data
    DATA_ANALYSIS_METHOD = "data_analysis_method" # Teknik analisis data
    RESEARCH_RESULT      = "research_result"      # Penyajian hasil / temuan
    FINDING              = "finding"              # Temuan spesifik
    ANALYSIS             = "analysis"             # Analisis sistematis
    INTERPRETATION       = "interpretation"       # Interpretasi hasil
    DISCUSSION           = "discussion"           # Pembahasan / diskusi
    THEORY_CONNECTION    = "theory_connection"    # Hubungan dengan teori
    PRIOR_RESEARCH_COMPARISON = "prior_research_comparison"  # Perbandingan dengan penelitian lain
    HYPOTHESIS_EVALUATION = "hypothesis_evaluation"  # Evaluasi hipotesis
    VISUALIZATION_CANDIDATE = "visualization_candidate"  # Kandidat representasi data
    CONCLUSION           = "conclusion"           # Kesimpulan
    LIMITATION           = "limitation"           # Keterbatasan penelitian
    IMPLICATION          = "implication"          # Implikasi temuan
    RECOMMENDATION       = "recommendation"       # Saran / rekomendasi
    FUTURE_WORK          = "future_work"          # Rekomendasi penelitian selanjutnya
```

**Validation Rules:**
- `density_score` harus dalam range `[0.0, 1.0]`
- `order` harus >= 0
- `depth` harus >= 0
- `raw_text` tidak boleh kosong (setelah strip)
- `unit_id` harus valid UUID v4

**Failure Conditions:**
- Jika `content_type` tidak valid → `ClassificationError`
- Jika `raw_text` kosong → `NormalizationError`

**Contoh JSON:**

```json
{
  "unit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "content_type": "sequence",
  "raw_text": "Langkah 1: Buka aplikasi. Langkah 2: Login dengan akun Anda. Langkah 3: Pilih menu Generate.",
  "normalized_text": "Langkah 1: Buka aplikasi.\nLangkah 2: Login dengan akun Anda.\nLangkah 3: Pilih menu Generate.",
  "title": "Cara memulai aplikasi",
  "order": 5,
  "depth": 1,
  "parent_unit_id": "parent-uuid-here",
  "related_unit_ids": [],
  "estimated_word_count": 22,
  "density_score": 0.4,
  "metadata": {}
}
```

---

### 6.2 AnalysisResult

**Tujuan:** Hasil analisis content intelligence. Berisi seluruh ContentUnit yang diekstrak beserta metadata analisis keseluruhan.

**Tanggung jawab:**
- Merepresentasikan pemahaman AI terhadap source material
- Menyediakan foundation untuk document planning
- Mengidentifikasi genre dokumen (tutorial vs. KTI/laporan penelitian)
- Memetakan kelengkapan alur penelitian untuk dokumen KTI

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `schema_version` | `str` | ✅ | `"1.0"` |
| `job_id` | `str` | ✅ | UUID job yang menghasilkan ini |
| `source_file` | `str` | ✅ | Path relatif file input |
| `content_units` | `list[ContentUnit]` | ✅ | Minimal 1 unit |
| `total_word_count` | `int` | ✅ | Total kata dari semua unit |
| `dominant_content_type` | `ContentType` | ✅ | Tipe konten yang paling dominan |
| `complexity_score` | `float` | ✅ | 0.0–1.0; kompleksitas keseluruhan konten |
| `recommended_mode` | `DocumentMode` | ✅ | Mode dokumen yang direkomendasikan |
| `document_genre` | `DocumentGenre` | ✅ | Genre dokumen yang terdeteksi |
| `research_traceability` | `ResearchTraceability \| None` | ❌ | Peta keterlacakan alur penelitian (hanya untuk genre KTI) |
| `analyzed_at` | `str` | ✅ | ISO-8601 timestamp |

**DocumentMode Enum:**

```python
class DocumentMode(str, Enum):
    A4_TUTORIAL        = "a4-tutorial"
    PRESENTATION_16_9  = "presentation-16-9"
```

**DocumentGenre Enum:**

```python
class DocumentGenre(str, Enum):
    TUTORIAL          = "tutorial"           # Materi pembelajaran, panduan, modul
    RESEARCH_REPORT   = "research_report"    # KTI, laporan penelitian, skripsi, makalah
    PRESENTATION      = "presentation"       # Slide presentasi, paparan
    GENERAL           = "general"            # Genre tidak teridentifikasi dengan pasti
```

**Validation Rules:**
- `content_units` tidak boleh empty
- `complexity_score` harus dalam range `[0.0, 1.0]`
- `analyzed_at` harus valid ISO-8601
- Jika `document_genre == RESEARCH_REPORT`: `research_traceability` sebaiknya hadir

**Relasi:**
- `AnalysisResult` contains `ContentUnit[]`
- `AnalysisResult` digunakan oleh Document Planner agent untuk menghasilkan `DocumentPlan`
- `research_traceability` dipopulasi khusus untuk dokumen genre `RESEARCH_REPORT`

---

### 6.3 Document

**Tujuan:** Representasi lengkap sebuah dokumen yang akan dirender. Objek paling tinggi dalam hierarki domain.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `schema_version` | `str` | ✅ | `"1.0"` |
| `document_id` | `str` | ✅ | UUID v4 |
| `title` | `str` | ✅ | Judul dokumen, max 200 chars |
| `subtitle` | `str \| None` | ❌ | Subjudul |
| `author` | `str \| None` | ❌ | Penulis/penyusun |
| `mode` | `DocumentMode` | ✅ | `a4-tutorial` atau `presentation-16-9` |
| `theme_id` | `str` | ✅ | ID theme yang digunakan |
| `sections` | `list[Section]` | ✅ | Minimal 1 section |
| `created_at` | `str` | ✅ | ISO-8601 |
| `language` | `str` | ✅ | BCP-47, default `"id"` |
| `metadata` | `dict[str, Any]` | ✅ | Default `{}` |

**Validation Rules:**
- `title` tidak boleh kosong
- `sections` tidak boleh empty
- `mode` harus nilai yang valid

**Lifecycle:**
1. Dibuat oleh Document Planner dari AnalysisResult
2. Diisi oleh Content Writer
3. Divalidasi oleh Pydantic
4. Digunakan oleh Design Director untuk menambah design decisions
5. Diteruskan ke Blueprint Generator

**Relasi:**
```
Document
  └── contains → Section[]
  └── references → Theme (via theme_id)
```

---

### 6.4 Section

**Tujuan:** Kelompok halaman yang secara semantik membentuk satu topik atau chapter.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `section_id` | `str` | ✅ | UUID v4 |
| `title` | `str` | ✅ | Judul section |
| `description` | `str \| None` | ❌ | Deskripsi singkat |
| `order` | `int` | ✅ | Urutan dalam dokumen (0-indexed) |
| `pages` | `list[Page]` | ✅ | Minimal 1 halaman |
| `source_unit_ids` | `list[str]` | ✅ | ContentUnit ID yang menjadi sumber section ini |

**Validation Rules:**
- `pages` tidak boleh empty
- `order` >= 0

---

### 6.5 Page

**Tujuan:** Representasi satu halaman dokumen. Memiliki page type tertentu dan berisi komponen.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `page_id` | `str` | ✅ | UUID v4 |
| `page_type` | `PageType` | ✅ | Enum — tipe tata letak halaman |
| `title` | `str \| None` | ❌ | Judul halaman (opsional untuk beberapa page type) |
| `order` | `int` | ✅ | Urutan dalam section (0-indexed) |
| `components` | `list[Component]` | ✅ | Minimal 1 komponen |
| `layout_variant` | `str \| None` | ❌ | Varian layout jika page type mendukungnya |
| `notes` | `str \| None` | ❌ | Catatan speaker/presenter (untuk presentation mode) |
| `source_unit_ids` | `list[str]` | ✅ | ContentUnit ID sumber |

**PageType Enum:**

```python
class PageType(str, Enum):
    COVER           = "cover"
    SECTION_OPENER  = "section_opener"
    ROADMAP         = "roadmap"
    PROCESS_FLOW    = "process_flow"
    COMPARISON      = "comparison"
    CARD_GRID       = "card_grid"
    CONCEPT_DIAGRAM = "concept_diagram"
    TABLE           = "table"
    CASE_STUDY      = "case_study"
    CHECKLIST       = "checklist"
    SUMMARY         = "summary"
    CONTENT         = "content"         # halaman konten umum
    BLANK           = "blank"           # halaman kosong (spacer)
```

**Validation Rules:**
- `components` tidak boleh empty kecuali `page_type == BLANK`
- `order` >= 0

---

### 6.6 Component

**Tujuan:** Elemen visual atomik dalam sebuah halaman. Setiap komponen memiliki type yang menentukan cara renderingnya.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `component_id` | `str` | ✅ | UUID v4 |
| `component_type` | `ComponentType` | ✅ | Enum — tipe komponen |
| `content` | `dict[str, Any]` | ✅ | Konten komponen — struktur bergantung pada `component_type` |
| `order` | `int` | ✅ | Urutan dalam halaman (0-indexed) |
| `span` | `int` | ✅ | Lebar dalam grid columns (default: grid width) |
| `style_overrides` | `dict[str, str]` | ❌ | CSS property override (terbatas, tidak bebas) |

**ComponentType Enum:**

```python
class ComponentType(str, Enum):
    HEADING         = "heading"
    PARAGRAPH       = "paragraph"
    CARD            = "card"
    BADGE           = "badge"
    CALLOUT         = "callout"
    PROCESS_STEP    = "process_step"
    COMPARISON_COL  = "comparison_column"
    TABLE           = "table"
    CHECKLIST       = "checklist"
    DIAGRAM_NODE    = "diagram_node"
    IMAGE_BLOCK     = "image_block"
    FORMULA_BLOCK   = "formula_block"
    SPACER          = "spacer"
```

**Aturan `content` per ComponentType:**

Struktur `content` bergantung pada `component_type`. Lihat detail di [`COMPONENT_SPECIFICATION.md`](../03_DOCUMENT_DESIGN/COMPONENT_SPECIFICATION.md).

Contoh untuk `HEADING`:
```json
{
  "component_type": "heading",
  "content": {
    "text": "Pengenalan Machine Learning",
    "level": 1
  }
}
```

Contoh untuk `PROCESS_STEP`:
```json
{
  "component_type": "process_step",
  "content": {
    "step_number": 1,
    "title": "Persiapan Data",
    "description": "Kumpulkan dan bersihkan data training.",
    "icon": "database"
  }
}
```

**Validation Rules:**
- `component_type` harus valid enum value
- `content` tidak boleh empty
- Field wajib dalam `content` bergantung pada `component_type` — divalidasi oleh ComponentValidator

**style_overrides yang diizinkan:**

```python
ALLOWED_STYLE_OVERRIDES = {
    "color",
    "background-color",
    "font-weight",
    "text-align",
    "padding",
    "margin-top",
    "margin-bottom",
}
```

AI **tidak boleh** menghasilkan arbitrary CSS. Hanya property dalam set di atas yang diizinkan.

---

### 6.7 Blueprint

**Tujuan:** Representasi terstruktur dan tervalidasi dari seluruh dokumen yang siap dirender. Blueprint adalah output final AI pipeline sebelum rendering.

**Tanggung jawab:**
- Menjadi **satu-satunya** input untuk rendering engine
- Berisi semua informasi yang dibutuhkan untuk rendering tanpa referensi ke source material
- Harus dapat dirender ulang secara deterministik

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `schema_version` | `str` | ✅ | `"1.0"` |
| `blueprint_id` | `str` | ✅ | UUID v4 |
| `job_id` | `str` | ✅ | UUID job yang menghasilkan ini |
| `document` | `Document` | ✅ | Objek dokumen lengkap |
| `theme` | `Theme` | ✅ | Theme yang digunakan |
| `mode` | `DocumentMode` | ✅ | Mode rendering |
| `total_pages` | `int` | ✅ | Total halaman (dihitung dari document.sections) |
| `generated_at` | `str` | ✅ | ISO-8601 |
| `generator_model` | `str` | ✅ | Model yang menghasilkan blueprint ini |

**Lifecycle:**
1. AI (Design Director agent) menghasilkan Blueprint sebagai JSON
2. Pydantic memvalidasi seluruh struktur
3. Jika validasi gagal: repair prompt → retry (max 3x)
4. Blueprint tervalidasi disimpan ke `outputs/jobs/{job_id}/blueprint/blueprint.json`
5. Blueprint diteruskan ke DocumentComposer untuk rendering

**Aturan:**
- Blueprint tidak boleh mengandung reference ke file eksternal selain asset yang sudah terdaftar
- Blueprint harus self-contained (semua teks, struktur, dan layout info ada di dalamnya)
- Rendering engine hanya menerima Blueprint yang sudah tervalidasi

**Contoh JSON (disingkat):**

```json
{
  "schema_version": "1.0",
  "blueprint_id": "bp-uuid-here",
  "job_id": "job-uuid-here",
  "mode": "a4-tutorial",
  "total_pages": 8,
  "generated_at": "2026-08-23T21:00:00+07:00",
  "generator_model": "qwen3:8b",
  "theme": {
    "theme_id": "kir-default",
    "name": "KIR Default"
  },
  "document": {
    "document_id": "doc-uuid-here",
    "title": "Panduan Machine Learning",
    "mode": "a4-tutorial",
    "theme_id": "kir-default",
    "language": "id",
    "sections": [
      {
        "section_id": "sec-1",
        "title": "Pengenalan",
        "order": 0,
        "pages": [
          {
            "page_id": "page-1",
            "page_type": "cover",
            "order": 0,
            "components": [
              {
                "component_id": "comp-1",
                "component_type": "heading",
                "content": { "text": "Panduan Machine Learning", "level": 1 },
                "order": 0,
                "span": 12
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

### 6.8 Theme

**Tujuan:** Kumpulan token desain yang diterapkan secara konsisten ke seluruh dokumen.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `theme_id` | `str` | ✅ | Identifier unik (slug, e.g. `"kir-default"`) |
| `name` | `str` | ✅ | Nama human-readable |
| `description` | `str \| None` | ❌ | Deskripsi singkat |
| `colors` | `ThemeColors` | ✅ | Token warna |
| `typography` | `ThemeTypography` | ✅ | Token tipografi |
| `spacing` | `ThemeSpacing` | ✅ | Token spacing |
| `supported_modes` | `list[DocumentMode]` | ✅ | Mode yang didukung theme ini |

**ThemeColors:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `primary` | `str` | ✅ | Hex color, e.g. `"#1A1A2E"` |
| `secondary` | `str` | ✅ | Hex color |
| `accent` | `str` | ✅ | Hex color — warna penekanan |
| `background` | `str` | ✅ | Hex color — latar halaman |
| `surface` | `str` | ✅ | Hex color — latar komponen (card, dll) |
| `text_primary` | `str` | ✅ | Hex color — teks utama |
| `text_secondary` | `str` | ✅ | Hex color — teks sekunder |
| `border` | `str` | ✅ | Hex color — border/divider |
| `success` | `str` | ✅ | Hex color |
| `warning` | `str` | ✅ | Hex color |
| `error` | `str` | ✅ | Hex color |

**ThemeTypography:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `font_heading` | `str` | ✅ | Nama font keluarga untuk heading |
| `font_body` | `str` | ✅ | Nama font keluarga untuk body |
| `font_mono` | `str` | ✅ | Nama font keluarga untuk monospace |
| `scale` | `dict[str, str]` | ✅ | Ukuran font: `{"h1": "32px", "h2": "24px", ...}` |
| `line_height_body` | `float` | ✅ | e.g. `1.6` |
| `line_height_heading` | `float` | ✅ | e.g. `1.2` |

**ThemeSpacing:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `base_unit` | `str` | ✅ | e.g. `"8px"` |
| `scale` | `dict[str, str]` | ✅ | `{"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "2xl": "48px"}` |
| `page_padding` | `str` | ✅ | e.g. `"32px"` |
| `section_gap` | `str` | ✅ | e.g. `"24px"` |

**Validation Rules:**
- Semua hex color harus valid format `#RRGGBB` atau `#RGB`
- `scale` dalam ThemeTypography harus mengandung minimal: `h1`, `h2`, `h3`, `body`, `caption`
- `scale` dalam ThemeSpacing harus mengandung minimal: `xs`, `sm`, `md`, `lg`, `xl`

---

### 6.9 RenderJob

**Tujuan:** Unit kerja rendering — merepresentasikan satu request pembuatan dokumen dari awal hingga selesai.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `job_id` | `str` | ✅ | UUID v4 |
| `status` | `JobState` | ✅ | State saat ini |
| `mode` | `DocumentMode` | ✅ | Mode dokumen |
| `source_file` | `str` | ✅ | Path file input |
| `output_dir` | `str` | ✅ | Path direktori output |
| `created_at` | `str` | ✅ | ISO-8601 |
| `started_at` | `str \| None` | ❌ | ISO-8601 |
| `completed_at` | `str \| None` | ❌ | ISO-8601 |
| `revision_count` | `int` | ✅ | Jumlah revisi yang dilakukan (default: 0) |
| `max_revisions` | `int` | ✅ | Batas maksimum revisi (dari config) |
| `error` | `str \| None` | ❌ | Error message jika gagal |
| `artifacts` | `list[RenderArtifact]` | ✅ | Semua artifact yang dihasilkan |

**JobState Enum:**

```python
class JobState(str, Enum):
    CREATED       = "created"
    RUNNING       = "running"
    COMPLETED     = "completed"
    FAILED_QUALITY = "failed_quality"
    FAILED_AI     = "failed_ai"
    FAILED_RENDER = "failed_render"
```

---

### 6.10 RenderArtifact

**Tujuan:** Satu file output yang dihasilkan oleh pipeline (intermediate atau final).

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `artifact_id` | `str` | ✅ | UUID v4 |
| `artifact_type` | `ArtifactType` | ✅ | Tipe artifact |
| `file_path` | `str` | ✅ | Path relatif dari job directory |
| `file_size_bytes` | `int \| None` | ❌ | Ukuran file |
| `created_at` | `str` | ✅ | ISO-8601 |
| `metadata` | `dict[str, Any]` | ✅ | Default `{}` |

**ArtifactType Enum:**

```python
class ArtifactType(str, Enum):
    RAW_CONTENT     = "raw_content"     # source/input.txt
    NORMALIZED      = "normalized"       # normalized/content.json
    ANALYSIS        = "analysis"         # analysis/result.json
    BLUEPRINT       = "blueprint"        # blueprint/blueprint.json
    HTML            = "html"             # html/document.html
    QUALITY_REPORT  = "quality_report"   # quality/report.json
    FINAL_PDF       = "final_pdf"        # output/document.pdf
```

---

### 6.11 QualityReport

**Tujuan:** Hasil inspeksi kualitas setelah rendering. Berisi daftar issue dan score keseluruhan.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `report_id` | `str` | ✅ | UUID v4 |
| `job_id` | `str` | ✅ | UUID job |
| `blueprint_id` | `str` | ✅ | UUID blueprint yang diinspeksi |
| `revision_number` | `int` | ✅ | 0 = inspeksi pertama |
| `overall_score` | `float` | ✅ | 0.0–100.0 |
| `passed` | `bool` | ✅ | `True` jika `overall_score >= threshold` dan tidak ada issue CRITICAL |
| `issues` | `list[QualityIssue]` | ✅ | Daftar issue yang ditemukan |
| `category_scores` | `dict[str, float]` | ✅ | Score per kategori (lihat QUALITY_SCORING_RUBRIC.md) |
| `inspected_at` | `str` | ✅ | ISO-8601 |
| `inspector_model` | `str \| None` | ❌ | Model AI yang melakukan inspeksi (jika visual QA menggunakan AI) |

---

### 6.12 QualityIssue

**Tujuan:** Satu masalah kualitas yang ditemukan oleh QA inspector.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `issue_id` | `str` | ✅ | UUID v4 |
| `severity` | `IssueSeverity` | ✅ | CRITICAL, HIGH, MEDIUM, LOW |
| `category` | `str` | ✅ | Kategori QA (misal: `"layout"`, `"content"`, `"render"`) |
| `page_id` | `str \| None` | ❌ | ID halaman bermasalah (jika spesifik) |
| `component_id` | `str \| None` | ❌ | ID komponen bermasalah (jika spesifik) |
| `description` | `str` | ✅ | Penjelasan masalah yang ditemukan |
| `evidence` | `str \| None` | ❌ | Evidence konkret (misal: `"font-size: 6px detected"`) |
| `recommended_action` | `str` | ✅ | Tindakan yang harus dilakukan |
| `auto_fixable` | `bool` | ✅ | Apakah dapat diperbaiki otomatis |

**IssueSeverity Enum:**

```python
class IssueSeverity(str, Enum):
    CRITICAL = "critical"   # Dokumen tidak dapat digunakan
    HIGH     = "high"       # Masalah signifikan yang harus diperbaiki
    MEDIUM   = "medium"     # Masalah yang sebaiknya diperbaiki
    LOW      = "low"        # Penyempurnaan opsional
```

**Severity Impact:**
- `CRITICAL` → selalu trigger revision atau fatal error
- `HIGH` → trigger revision jika count > 0
- `MEDIUM` → trigger revision jika count > 2
- `LOW` → dicatat dalam report, tidak trigger revision

---

### 6.13 ProviderConfig

**Tujuan:** Konfigurasi untuk satu AI provider.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `provider_id` | `str` | ✅ | e.g. `"nine_router"`, `"ollama"` |
| `base_url` | `str` | ✅ | Endpoint URL |
| `api_key` | `SecretStr` | ❌ | API key — selalu `SecretStr`, tidak pernah `str` |
| `timeout_seconds` | `int` | ✅ | Default: `120` |
| `max_retries` | `int` | ✅ | Default: `3` |
| `enabled` | `bool` | ✅ | Default: `True` |

**Validation Rules:**
- `base_url` harus valid URL
- `timeout_seconds` harus > 0
- `max_retries` harus dalam range `[0, 10]`
- `api_key` menggunakan `SecretStr` sehingga tidak pernah muncul di log atau repr

---

### 6.14 ModelConfig

**Tujuan:** Assignment model AI ke setiap role dalam pipeline.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `planner_model` | `str` | ✅ | Model untuk Document Planner agent |
| `writer_model` | `str` | ✅ | Model untuk Content Writer agent |
| `design_model` | `str` | ✅ | Model untuk Design Director agent |
| `critic_model` | `str` | ✅ | Model untuk Quality Critic agent |
| `provider_preference` | `list[str]` | ✅ | Urutan provider: e.g. `["nine_router", "ollama"]` |

**Aturan:**
- Setiap model string mengacu pada model identifier yang didukung provider
- `provider_preference` menentukan urutan fallback

---

### 6.15 GenerationRequest

**Tujuan:** Input untuk satu AI generation call.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `request_id` | `str` | ✅ | UUID v4 |
| `model` | `str` | ✅ | Model identifier |
| `system_prompt` | `str` | ✅ | System prompt |
| `user_prompt` | `str` | ✅ | User prompt / task prompt |
| `response_format` | `dict \| None` | ❌ | JSON schema untuk structured output |
| `temperature` | `float` | ✅ | Default: `0.3` |
| `max_tokens` | `int \| None` | ❌ | Batas token output |
| `metadata` | `dict[str, Any]` | ✅ | e.g. `{"agent": "planner", "step": "planning"}` |

---

### 6.16 GenerationResponse

**Tujuan:** Output dari satu AI generation call.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `request_id` | `str` | ✅ | Sama dengan `GenerationRequest.request_id` |
| `model` | `str` | ✅ | Model yang sebenarnya digunakan |
| `provider` | `str` | ✅ | Provider yang sebenarnya digunakan |
| `content` | `str` | ✅ | Raw output text dari AI |
| `parsed_content` | `Any \| None` | ❌ | Parsed JSON jika response_format digunakan |
| `usage` | `TokenUsage` | ✅ | Token usage stats |
| `latency_ms` | `int` | ✅ | Waktu response dalam milliseconds |
| `attempt_number` | `int` | ✅ | Ke berapa percobaan ini (1-indexed) |

**TokenUsage:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `prompt_tokens` | `int` | ✅ | Jumlah prompt token |
| `completion_tokens` | `int` | ✅ | Jumlah completion token |
| `total_tokens` | `int` | ✅ | Total token (prompt + completion) |

---

### 6.17 RawContent

**Tujuan:** Merepresentasikan payload materi mentah yang baru dibaca dari file input pada tahap Ingestion.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `source_path` | `str` | ✅ | Path file sumber |
| `file_format` | `str` | ✅ | Format file: `"txt"`, `"md"`, `"docx"` |
| `raw_bytes_size` | `int` | ✅ | Ukuran file dalam bytes |
| `raw_text` | `str` | ✅ | Teks mentah apa adanya |
| `ingested_at` | `str` | ✅ | ISO-8601 timestamp |

**Validation Rules:**
- `raw_text` tidak boleh kosong (setelah whitespace strip)
- `file_format` harus salah satu dari format yang didukung: `"txt"`, `"md"`, `"docx"`

---

### 6.18 NormalizedContent

**Tujuan:** Merepresentasikan teks yang telah dibersihkan dari encoding anomali, whitespace liar, dan dinormalisasi strukturnya pada tahap Normalization.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `source_path` | `str` | ✅ | Path file sumber |
| `clean_text` | `str` | ✅ | Teks hasil normalisasi |
| `detected_language` | `str` | ✅ | Kode bahasa (BCP-47), e.g. `"id"`, `"en"` |
| `line_count` | `int` | ✅ | Jumlah baris |
| `char_count` | `int` | ✅ | Jumlah karakter |
| `normalized_at` | `str` | ✅ | ISO-8601 timestamp |

---

### 6.19 DocumentPlan

**Tujuan:** Rencana arsitektur dokumen tingkat tinggi yang dihasilkan oleh Document Planner Agent sebelum penyusunan Blueprint lengkap.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `plan_id` | `str` | ✅ | UUID v4 |
| `job_id` | `str` | ✅ | UUID job |
| `target_mode` | `DocumentMode` | ✅ | Mode dokumen yang ditargetkan |
| `document_title` | `str` | ✅ | Judul dokumen terencana |
| `estimated_pages` | `int` | ✅ | Estimasi jumlah halaman |
| `sections` | `list[PlannedSection]` | ✅ | Rencana section |
| `planned_at` | `str` | ✅ | ISO-8601 timestamp |

**PlannedSection:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `title` | `str` | ✅ | Judul section |
| `order` | `int` | ✅ | Urutan section (0-indexed) |
| `target_page_count` | `int` | ✅ | Target jumlah halaman |
| `content_unit_ids` | `list[str]` | ✅ | Unit konten yang dialokasikan ke section ini |
| `planned_pages` | `list[PlannedPage]` | ✅ | Rencana halaman dalam section |

**PlannedPage:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `page_order` | `int` | ✅ | Urutan halaman |
| `suggested_page_type` | `PageType` | ✅ | PageType yang disarankan |
| `key_takeaway` | `str` | ✅ | Poin pesan utama halaman ini |
| `content_unit_ids` | `list[str]` | ✅ | Unit konten yang ditampilkan |

---

### 6.20 ValidationResult

**Tujuan:** Hasil evaluasi validasi Blueprint atau komponen terhadap aturan integritas skema dan visual contract.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `is_valid` | `bool` | ✅ | True jika tidak ada error fatal |
| `errors` | `list[ValidationIssue]` | ✅ | Daftar error validasi |
| `warnings` | `list[ValidationIssue]` | ✅ | Daftar warning (non-fatal) |
| `validated_at` | `str` | ✅ | ISO-8601 timestamp |

**ValidationIssue:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `location` | `str` | ✅ | Path lokasi field/halaman yang error (e.g. `document.sections[0].pages[1]`) |
| `issue_type` | `str` | ✅ | Tipe isu (e.g. `SCHEMA_MISMATCH`, `DENSITY_OVERFLOW`, `INVALID_STYLE_OVERRIDE`) |
| `message` | `str` | ✅ | Deskripsi detail masalah |
| `rejected_value` | `Any \| None` | ❌ | Nilai yang ditolak jika ada |

---

### 6.21 ResearchTraceability

**Tujuan:** Peta keterlacakan alur penelitian untuk dokumen bertipe `RESEARCH_REPORT`. Merepresentasikan node-node inti yang terdeteksi dalam source material dan hubungan antar node.

Objek ini digunakan oleh Content Intelligence dan Document Planner untuk memastikan tidak ada komponen penelitian kritis yang hilang atau tidak terwakili dalam Blueprint.

**Fields:**

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `has_research_problem` | `bool` | ✅ | Terdeteksi latar belakang / rumusan masalah |
| `has_research_question` | `bool` | ✅ | Terdeteksi rumusan masalah yang eksplisit |
| `has_research_objective` | `bool` | ✅ | Terdeteksi tujuan penelitian |
| `has_hypothesis` | `bool` | ✅ | Terdeteksi hipotesis (opsional dalam KTI) |
| `has_theoretical_foundation` | `bool` | ✅ | Terdeteksi landasan teori |
| `has_prior_research` | `bool` | ✅ | Terdeteksi penelitian terdahulu |
| `has_research_method` | `bool` | ✅ | Terdeteksi metode penelitian |
| `has_results` | `bool` | ✅ | Terdeteksi hasil penelitian |
| `has_discussion` | `bool` | ✅ | Terdeteksi pembahasan / analisis |
| `has_conclusion` | `bool` | ✅ | Terdeteksi kesimpulan |
| `has_recommendation` | `bool` | ✅ | Terdeteksi saran / rekomendasi |
| `detected_bab_coverage` | `list[str]` | ✅ | BAB yang terdeteksi, e.g. `["BAB_1", "BAB_2", "BAB_3", "BAB_4", "BAB_5"]` |
| `missing_critical_components` | `list[str]` | ✅ | Komponen kritis yang tidak terdeteksi |
| `traceability_warnings` | `list[str]` | ✅ | Peringatan keterlacakan, e.g. `"FINDING_WITHOUT_INTERPRETATION"` |

**KTI BAB Enum (digunakan dalam `detected_bab_coverage`):**

```python
class KtiBab(str, Enum):
    BAB_1 = "BAB_1"   # Pendahuluan
    BAB_2 = "BAB_2"   # Tinjauan Pustaka
    BAB_3 = "BAB_3"   # Metodologi Penelitian
    BAB_4 = "BAB_4"   # Hasil dan Pembahasan
    BAB_5 = "BAB_5"   # Kesimpulan dan Saran
```

**Critical Components (komponen yang wajib hadir dalam dokumen KTI minimum):**

```
RESEARCH_PROBLEM
RESEARCH_OBJECTIVE
RESEARCH_METHOD
FINDING
CONCLUSION
```

**Optional Components (tergantung desain penelitian):**

```
RESEARCH_QUESTION     ← terkadang terintegrasi dalam RESEARCH_PROBLEM
HYPOTHESIS            ← hanya jika penelitian eksperimental/kuantitatif
PRIOR_RESEARCH        ← sebaiknya ada, namun minimal mungkin
DISCUSSION            ← terkadang terintegrasi dalam FINDING
LIMITATION            ← sebaiknya ada, dapat terintegrasi
RECOMMENDATION        ← sebaiknya ada, dapat terintegrasi
```

**Traceability Warning Types:**

| Warning | Keterangan |
|---|---|
| `FINDING_WITHOUT_INTERPRETATION` | Ada finding tanpa interpretasi yang menjelaskan maknanya |
| `DATA_WITHOUT_FINDING` | Ada data mentah tanpa kesimpulan temuan |
| `CONCLUSION_WITHOUT_OBJECTIVE_TRACE` | Kesimpulan tidak dapat dilacak ke tujuan penelitian |
| `RECOMMENDATION_WITHOUT_BASIS` | Rekomendasi tidak memiliki dasar dari finding atau limitation |
| `HYPOTHESIS_WITHOUT_EVALUATION` | Ada hipotesis namun tidak ada evaluasi hipotesis di BAB 4 |
| `MISSING_BAB_COVERAGE` | BAB tertentu tidak terdeteksi dalam source material |

**Validation Rules:**
- `detected_bab_coverage` tidak boleh kosong untuk dokumen KTI
- Jika `has_results` adalah `True` tetapi `has_conclusion` adalah `False`: wajib ditambahkan warning `MISSING_BAB_COVERAGE`
- `missing_critical_components` harus mencantumkan komponen wajib yang tidak terdeteksi

---

## 7. Relasi Antar Objek (Diagram)

```
ProviderConfig ──────────────────────────────────────┐
ModelConfig ─────────────────────────────────────────┤
                                                      │
GenerationRequest ──→ [AI Provider] ──→ GenerationResponse
                                                      │
                                                      ▼
ContentUnit[] ←── AnalysisResult ←── [Content Intelligence]
                     ├── document_genre (TUTORIAL / RESEARCH_REPORT)
                     └── research_traceability ─→ ResearchTraceability
     │
     ▼
Document
  └── Section[]
        └── Page[]
              └── Component[]

Document + Theme ──→ Blueprint ──→ [Rendering Engine]
                                         │
                                         ▼
                                    RenderJob
                                      ├── RenderArtifact[] (HTML, PDF, etc.)
                                      └── QualityReport
                                            └── QualityIssue[]
```

---

## 8. Acceptance Criteria

Schema dianggap benar jika:

- [ ] Semua objek domain dapat diinstansiasi dari JSON valid tanpa error Pydantic
- [ ] Field `api_key` dalam `ProviderConfig` menggunakan `SecretStr` dan tidak pernah muncul di log
- [ ] `Blueprint` dapat diserialisasi ke JSON dan deserialisasi kembali tanpa kehilangan data
- [ ] Rendering engine **hanya** menerima `Blueprint` yang sudah tervalidasi — tidak pernah menerima raw string AI
- [ ] Setiap `QualityIssue` memiliki `recommended_action` yang tidak kosong
- [ ] `ComponentType.style_overrides` hanya mengandung property yang ada dalam `ALLOWED_STYLE_OVERRIDES`
- [ ] Schema versioning berfungsi: schema dengan version berbeda dapat dideteksi
- [ ] `ContentType` enum mencakup seluruh peran semantik KTI (BAB 1–5)
- [ ] `AnalysisResult.document_genre` terisi untuk semua job
- [ ] Untuk `document_genre == RESEARCH_REPORT`: `research_traceability` hadir dan `detected_bab_coverage` tidak kosong
- [ ] `ResearchTraceability.traceability_warnings` hanya mengandung warning dari daftar yang terdefinisi
