# KIR AI Document Intelligence

> **Versi Dokumentasi:** 1.0  
> **Status:** Draft — Foundation Batch  
> **Terakhir diperbarui:** 2026-08-23

---

## Apa Ini?

**KIR AI Document Intelligence** adalah aplikasi Python *local-first* yang mengubah materi mentah (teks, outline, catatan) menjadi dokumen visual berkualitas tinggi dalam format PDF.

Sistem ini bukan sekadar konverter teks ke PDF. Sistem ini adalah **pipeline kecerdasan dokumen** yang memisahkan secara tegas:

- **AI reasoning** — memahami konten, merencanakan struktur, memutuskan tata letak
- **Document rendering** — mengeksekusi desain secara deterministik berdasarkan blueprint yang tervalidasi

AI tidak pernah menghasilkan HTML atau CSS secara langsung. AI menghasilkan **Blueprint** — sebuah struktur data tervalidasi — yang kemudian dirender oleh mesin rendering terpisah.

---

## Masalah yang Diselesaikan

| Masalah | Pendekatan Sistem Ini |
|---|---|
| AI menghasilkan HTML sembarangan → hasil tidak konsisten | AI hanya menghasilkan Blueprint (JSON terstruktur) |
| Font mengecil otomatis saat overflow | Overflow ditangani eksplisit: split halaman atau error |
| Dokumen berbeda-beda meski input sama | Pipeline deterministik: input + blueprint + theme = output identik |
| PDF tidak memiliki hierarki informasi | Classification konten → pemilihan page type yang sesuai |
| Tidak ada quality gate | Quality inspection layer dengan scoring rubric |

---

## Target Output

Sistem menghasilkan dua mode dokumen utama:

### MODE 1 — PDF Tutorial A4 Landscape

**Digunakan untuk:** tutorial, handbook, modul, panduan, pembekalan, materi pelatihan, **laporan penelitian (KTI)**, karya ilmiah.

Karakteristik:
- Canvas A4 landscape (297mm × 210mm)
- Visual handbook — bukan slide yang dipaksa cetak
- Informasi padat dengan hierarki yang jelas
- Bacaan linear dari halaman ke halaman

### MODE 2 — PDF Presentation 16:9

**Digunakan untuk:** presentasi, workshop, pemaparan, materi LDP, pembelajaran, training, **pemaparan hasil penelitian**.

Karakteristik:
- Canvas 1920×1080px (atau setara)
- Satu konsep utama per slide
- Visual dominance — teks pendukung minimal
- Dirancang untuk tampil di layar, bukan dicetak

### Genre Dokumen yang Didukung

Sistem mendukung dua genre dokumen utama yang dideteksi secara otomatis:

| Genre | Keterangan | Contoh Dokumen |
|---|---|---|
| **TUTORIAL** | Materi pembelajaran dengan penjelasan konsep dan langkah-langkah | Modul pelatihan, panduan teknis, handbook |
| **RESEARCH_REPORT** | Laporan penelitian dengan alur naratif ilmiah BAB 1–5 | KTI, skripsi, makalah, laporan penelitian |

Untuk genre **RESEARCH_REPORT**, sistem memiliki pemahaman khusus terhadap:
- Struktur **BAB 1–5** (Pendahuluan → Tinjauan Pustaka → Metodologi → Hasil & Pembahasan → Kesimpulan)
- Alur **keterlacakan penelitian** (Research Traceability): dari Rumusan Masalah hingga Simpulan
- Pemisahan semantik antara **DATA**, **FINDING**, **ANALISIS**, dan **INTERPRETASI**
- Prinsip **Source Fidelity**: AI tidak mengarang data yang tidak ada dalam materi sumber

Lihat [`KTI_DOMAIN_MODEL.md`](01_FOUNDATION/KTI_DOMAIN_MODEL.md) untuk model domain KTI yang lengkap.

---


## Pipeline Sistem

```
SOURCE MATERIAL
      ↓
CONTENT INGESTION        ← membaca file input (txt, md, docx)
      ↓
CONTENT NORMALIZATION    ← membersihkan, mengatur struktur dasar
      ↓
CONTENT INTELLIGENCE     ← AI mengklasifikasi informasi
      ↓
INFORMATION CLASSIFICATION ← menentukan tipe setiap unit konten
      ↓
DOCUMENT PLANNING        ← AI merencanakan struktur dokumen
      ↓
BLUEPRINT GENERATION     ← AI menghasilkan Blueprint JSON
      ↓
BLUEPRINT VALIDATION     ← Pydantic memvalidasi schema
      ↓
CONTENT COMPOSITION      ← konten dimasukkan ke Blueprint
      ↓
DESIGN DECISION          ← pemilihan theme, page type
      ↓
PAGE COMPOSITION         ← Blueprint → struktur per halaman
      ↓
HTML / CSS RENDERING     ← Jinja2 render template
      ↓
BROWSER PDF EXPORT       ← Playwright Chromium → PDF
      ↓
QUALITY INSPECTION       ← inspeksi PDF: layout, konten, visual
      ↓
TARGETED REVISION        ← revisi halaman tertentu jika gagal QA
      ↓
FINAL PDF
```

---

## Prinsip Arsitektur

1. **Separation of Concerns** — AI reasoning dipisah dari rendering engine.
2. **Schema-first** — semua output AI harus melalui schema Pydantic sebelum diproses lebih lanjut.
3. **Determinism** — input yang sama + blueprint yang sama + theme yang sama → output yang sama.
4. **Controlled Failure** — setiap tahap memiliki failure condition yang terdefinisi; tidak ada silent failure.
5. **Domain Independence** — domain layer tidak bergantung pada Playwright, 9Router, Ollama, atau filesystem implementation.
6. **CLI-first** — entry point utama adalah CLI; tidak ada UI web pada fase awal.

---

## Quick Start

### 1. Persiapan Environment

```bash
# Clone / masuk ke direktori project
cd KIR/

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# atau: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Install Playwright
playwright install chromium
```

### 2. Konfigurasi AI

```bash
# Salin template environment
cp .env.example .env

# Edit .env — isi API key dan endpoint
# Lihat: docs/01_FOUNDATION/AI_SETUP.md
```

### 3. Verifikasi Environment

```bash
kir doctor
```

### 4. Generate Dokumen

```bash
# A4 Tutorial
kir generate --input data/input/materi.md --mode a4-tutorial --output outputs/

# Presentasi 16:9
kir generate --input data/input/materi.md --mode presentation-16-9 --output outputs/
```

---

## Urutan Membaca Dokumentasi

Untuk **developer baru** atau **AI coding agent** yang baru bergabung:

| Urutan | File | Tujuan |
|---|---|---|
| 1 | `docs/README.md` *(ini)* | Orientasi sistem |
| 2 | `docs/DOCS_MANIFEST.md` | Peta semua dokumentasi |
| 3 | `docs/01_FOUNDATION/ARCHITECTURE.md` | Arsitektur sistem secara menyeluruh |
| 4 | `docs/01_FOUNDATION/DOMAIN_SCHEMA.md` | Semua objek domain dan relasinya |
| 5 | `docs/01_FOUNDATION/ENVIRONMENT_SETUP.md` | Setup lokal |
| 6 | `docs/01_FOUNDATION/AI_SETUP.md` | Konfigurasi provider AI |
| 7 | `docs/01_FOUNDATION/SECURITY_AND_SECRETS.md` | Pengelolaan rahasia |
| 8 | `docs/01_FOUNDATION/PROJECT_CONVENTIONS.md` | Konvensi kode |
| 9 | `docs/02_AI_INTELLIGENCE/` | Setelah foundation dipahami |
| 10 | `docs/07_IMPLEMENTATION/MASTER_IMPLEMENTATION_SPEC.md` | Referensi implementasi terpadu |

---

## Roadmap Ringkas

| Phase | Nama | Status |
|---|---|---|
| 0 | Documentation | ✅ In Progress |
| 1 | Environment & Project Setup | ⬜ Belum dimulai |
| 2 | AI Infrastructure | ⬜ Belum dimulai |
| 3 | Domain Schema | ⬜ Belum dimulai |
| 4 | Static Renderer | ⬜ Belum dimulai |
| 5 | Design System | ⬜ Belum dimulai |
| 6 | A4 Tutorial MVP | ⬜ Belum dimulai |
| 7 | Presentation 16:9 MVP | ⬜ Belum dimulai |
| 8 | Content Intelligence | ⬜ Belum dimulai |
| 9 | Quality System | ⬜ Belum dimulai |
| 10 | Importers | ⬜ Belum dimulai |
| 11 | Production Hardening | ⬜ Belum dimulai |

Detail setiap phase: [`docs/06_ENGINEERING/DEVELOPMENT_ROADMAP.md`](06_ENGINEERING/DEVELOPMENT_ROADMAP.md)

---

## Glossary Inti

| Istilah | Definisi |
|---|---|
| **Blueprint** | Struktur data JSON tervalidasi yang mendeskripsikan seluruh dokumen (halaman, komponen, konten). Ini yang dihasilkan AI — bukan HTML. |
| **ContentUnit** | Unit informasi atomik yang diekstrak dari source material. Memiliki tipe klasifikasi (DEFINITION, SEQUENCE, dll). |
| **Page Type** | Template tata letak halaman yang dipilih berdasarkan information shape (Cover, Process Flow, Comparison, dll). |
| **Component** | Elemen visual atomik dalam sebuah halaman (Heading, Card, ProcessStep, dll). Memiliki input/output contract. |
| **Theme** | Sekumpulan token desain (warna, tipografi, spacing) yang diterapkan secara konsisten ke seluruh dokumen. |
| **RenderJob** | Unit kerja rendering — satu dokumen dari Blueprint hingga PDF final. |
| **QualityReport** | Hasil inspeksi kualitas setelah rendering, berisi daftar QualityIssue dengan severity dan recommended action. |
| **9Router** | Primary AI provider — OpenAI-compatible endpoint lokal. |
| **Ollama** | Local fallback AI provider. |
| **Provider** | Abstraksi untuk AI provider (9Router atau Ollama). |
| **PLANNER_MODEL** | Model AI yang bertugas merencanakan struktur dokumen. |
| **WRITER_MODEL** | Model AI yang bertugas mengisi konten. |
| **DESIGN_MODEL** | Model AI yang bertugas memutuskan desain. |
| **CRITIC_MODEL** | Model AI yang bertugas melakukan evaluasi kualitas. |
| **Mode** | Jenis output dokumen: `a4-tutorial` atau `presentation-16-9`. |

---

## Teknologi Utama

| Komponen | Teknologi |
|---|---|
| Language | Python |
| Configuration | Pydantic Settings + python-dotenv |
| Schema Validation | Pydantic |
| Templating | Jinja2 |
| Rendering | HTML + CSS |
| Browser Engine | Playwright Chromium |
| PDF Inspection | PyMuPDF / pypdf |
| Testing | pytest |
| Project Config | pyproject.toml |

---

---

## Repository Execution Safety Guideline

> **Important Rule for Developers & AI Agents:**
> "Never use unrestricted recursive glob/rglob from repository root in this project unless there is an explicit justification. The repository may contain large virtual environments, dependency trees, caches, and generated artifacts. Recursive scans must either target a known directory or prune excluded directories before traversal."

Use the safe discovery utility:
```python
from app.utils.file_discovery import find_files

# Safe search pruning venv, .git, node_modules before traversal:
pdf_files = find_files("outputs", patterns="*.pdf")
```
Or for CLI inspection:
```bash
PYTHONPATH=. python scripts/inspect_pdfs.py outputs
```

---

*Untuk pertanyaan arsitektur: lihat [`ARCHITECTURE.md`](01_FOUNDATION/ARCHITECTURE.md)*  
*Untuk implementasi: lihat [`MASTER_IMPLEMENTATION_SPEC.md`](07_IMPLEMENTATION/MASTER_IMPLEMENTATION_SPEC.md)*
