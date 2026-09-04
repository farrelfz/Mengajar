# DOCS MANIFEST — KIR AI Document Intelligence

> **Versi:** 1.0  
> **Tujuan:** Peta navigasi seluruh dokumentasi proyek.  
> Baca dokumen ini **sebelum** membaca dokumen lain.

---

## Cara Menggunakan Manifest Ini

Setiap entri mencakup:
- **Tujuan** — apa yang dijelaskan dokumen ini
- **Kapan dibaca** — kondisi atau konteks yang relevan
- **Dependency** — dokumen yang harus dibaca lebih dulu
- **Dokumen terkait** — dokumen lain yang saling berkaitan
- **Urutan implementasi** — posisi dalam roadmap

---

## Struktur Lengkap Dokumentasi

```
docs/
├── README.md                              ← Mulai di sini
├── DOCS_MANIFEST.md                       ← Dokumen ini
│
├── 01_FOUNDATION/
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_SCHEMA.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── AI_SETUP.md
│   ├── SECURITY_AND_SECRETS.md
│   ├── PROJECT_CONVENTIONS.md
│   ├── KTI_DOMAIN_MODEL.md
│   └── FOUNDATION_AUDIT_REPORT.md
│
├── 02_AI_INTELLIGENCE/
│   ├── CONTENT_INTELLIGENCE.md
│   ├── AI_AGENT_ORCHESTRATION.md
│   ├── PROMPT_SPECIFICATION.md
│   └── CONTENT_TO_BLUEPRINT_ALGORITHM.md
│
├── 03_DOCUMENT_DESIGN/
│   ├── DESIGN_SYSTEM.md
│   ├── DESIGN_REFERENCE_ANALYSIS.md
│   ├── PAGE_TYPE_LIBRARY.md
│   ├── COMPONENT_SPECIFICATION.md
│   ├── A4_TUTORIAL_SPECIFICATION.md
│   └── PRESENTATION_16_9_SPECIFICATION.md
│
├── 04_RENDERING/
│   └── PDF_RENDERING.md
│
├── 05_QUALITY/
│   ├── QUALITY_ASSURANCE.md
│   └── QUALITY_SCORING_RUBRIC.md
│
├── 06_ENGINEERING/
│   ├── CLI_SPECIFICATION.md
│   ├── TESTING_STRATEGY.md
│   └── DEVELOPMENT_ROADMAP.md
│
└── 07_IMPLEMENTATION/
    ├── MASTER_IMPLEMENTATION_SPEC.md
    └── MASTER_IMPLEMENTATION_PROMPT.md
```

---

## 01_FOUNDATION

### README.md

| Field | Detail |
|---|---|
| **Tujuan** | Orientasi umum: apa sistem ini, masalah yang diselesaikan, pipeline, teknologi, glossary |
| **Kapan dibaca** | Pertama kali bergabung ke proyek; sebelum membaca dokumen lain |
| **Dependency** | — |
| **Dokumen terkait** | Semua dokumen (ini adalah pintu masuk) |
| **Urutan implementasi** | Phase 0 — sebelum implementasi dimulai |

---

### DOCS_MANIFEST.md *(dokumen ini)*

| Field | Detail |
|---|---|
| **Tujuan** | Peta navigasi dan panduan membaca seluruh dokumentasi |
| **Kapan dibaca** | Segera setelah README; saat bingung harus membaca dokumen mana |
| **Dependency** | README.md |
| **Dokumen terkait** | Semua dokumen |
| **Urutan implementasi** | Phase 0 |

---

### 01_FOUNDATION/ARCHITECTURE.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan arsitektur sistem secara menyeluruh: layer, modul, dependency rules, pipeline, state machine, artifact management |
| **Kapan dibaca** | Setelah README; sebelum mulai coding apapun; saat merancang modul baru |
| **Dependency** | README.md |
| **Dokumen terkait** | DOMAIN_SCHEMA.md, AI_SETUP.md, PDF_RENDERING.md, MASTER_IMPLEMENTATION_SPEC.md |
| **Urutan implementasi** | Phase 0–1: harus dipahami sebelum Phase 1 dimulai |

---

### 01_FOUNDATION/DOMAIN_SCHEMA.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan semua objek domain (Document, Blueprint, Page, Component, dll) beserta field, relasi, validation rule, dan contoh JSON |
| **Kapan dibaca** | Setelah ARCHITECTURE.md; sebelum menulis kode apapun yang menyentuh objek domain |
| **Dependency** | ARCHITECTURE.md |
| **Dokumen terkait** | COMPONENT_SPECIFICATION.md, AI_AGENT_ORCHESTRATION.md, CONTENT_TO_BLUEPRINT_ALGORITHM.md |
| **Urutan implementasi** | Phase 3 — Domain Schema |

---

### 01_FOUNDATION/ENVIRONMENT_SETUP.md

| Field | Detail |
|---|---|
| **Tujuan** | Panduan setup lokal: Python, virtualenv, dependencies, Playwright, directory verification, environment doctor, troubleshooting |
| **Kapan dibaca** | Saat pertama kali setup mesin development; setelah clone repository |
| **Dependency** | README.md |
| **Dokumen terkait** | AI_SETUP.md, SECURITY_AND_SECRETS.md |
| **Urutan implementasi** | Phase 1 — Environment Setup |

---

### 01_FOUNDATION/AI_SETUP.md

| Field | Detail |
|---|---|
| **Tujuan** | Konfigurasi provider AI: 9Router, Ollama, .env, endpoint verification, model role assignment, retry strategy, fallback, offline mode |
| **Kapan dibaca** | Setelah environment siap; sebelum menjalankan pipeline AI apapun |
| **Dependency** | ENVIRONMENT_SETUP.md, SECURITY_AND_SECRETS.md |
| **Dokumen terkait** | AI_AGENT_ORCHESTRATION.md, PROMPT_SPECIFICATION.md |
| **Urutan implementasi** | Phase 2 — AI Infrastructure |

---

### 01_FOUNDATION/SECURITY_AND_SECRETS.md

| Field | Detail |
|---|---|
| **Tujuan** | Pengelolaan rahasia: secret lifecycle, .env rules, git protection, log redaction, API key rotation, incident response |
| **Kapan dibaca** | Sebelum mengonfigurasi AI; sebelum commit pertama; saat onboarding contributor baru |
| **Dependency** | README.md |
| **Dokumen terkait** | AI_SETUP.md, ENVIRONMENT_SETUP.md |
| **Urutan implementasi** | Phase 0–1 — harus dipahami dari awal |

---

### 01_FOUNDATION/PROJECT_CONVENTIONS.md

| Field | Detail |
|---|---|
| **Tujuan** | Konvensi kode: naming, Python style, typing, imports, exception strategy, logging, configuration pattern, folder ownership, code review checklist, definition of done |
| **Kapan dibaca** | Sebelum menulis baris pertama kode; saat code review |
| **Dependency** | ARCHITECTURE.md |
| **Dokumen terkait** | TESTING_STRATEGY.md |
| **Urutan implementasi** | Phase 0–1 |

---

### 01_FOUNDATION/KTI_DOMAIN_MODEL.md

| Field | Detail |
|---|---|
| **Tujuan** | Model pengetahuan kanonik untuk KTI / laporan penelitian: struktur BAB 1–5, peran semantik, alur keterlacakan penelitian, prinsip fidelitas sumber, variasi struktur, dan worked example |
| **Kapan dibaca** | Sebelum mengimplementasikan Content Intelligence; sebelum menulis prompt untuk agent KTI; sebelum merancang Content-to-Blueprint algorithm untuk genre research report |
| **Dependency** | DOMAIN_SCHEMA.md, ARCHITECTURE.md |
| **Dokumen terkait** | CONTENT_INTELLIGENCE.md, AI_AGENT_ORCHESTRATION.md, CONTENT_TO_BLUEPRINT_ALGORITHM.md, PROMPT_SPECIFICATION.md |
| **Urutan implementasi** | Phase 1.5 — Domain Knowledge (sebelum Phase 2 AI Implementation) |

---

### 01_FOUNDATION/FOUNDATION_AUDIT_REPORT.md

| Field | Detail |
|---|---|
| **Tujuan** | Laporan audit komprehensif BATCH 1 Foundation: konsistensi terminologi, cakupan objek domain, validasi arah dependency, sinkronisasi konfigurasi, kesiapan implementasi |
| **Kapan dibaca** | Setelah menyelesaikan satu batch dokumentasi; sebelum memulai batch berikutnya |
| **Dependency** | Semua dokumen dalam 01_FOUNDATION |
| **Dokumen terkait** | Semua dokumen BATCH 1 |
| **Urutan implementasi** | Phase 0 — Foundation QA |

---

## 02_AI_INTELLIGENCE

### CONTENT_INTELLIGENCE.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan proses ingestion, normalisasi, segmentasi, klasifikasi informasi, dan content transformation |
| **Kapan dibaca** | Setelah Domain Schema; saat mengimplementasikan layer AI intelligence |
| **Dependency** | DOMAIN_SCHEMA.md, AI_SETUP.md |
| **Dokumen terkait** | AI_AGENT_ORCHESTRATION.md, CONTENT_TO_BLUEPRINT_ALGORITHM.md |
| **Urutan implementasi** | Phase 8 — Content Intelligence |

---

### AI_AGENT_ORCHESTRATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan empat agent (Planner, Writer, Design Director, Critic) beserta responsibility, handoff, shared state, revision loop, call budget |
| **Kapan dibaca** | Setelah AI_SETUP.md; saat mengimplementasikan agent pipeline |
| **Dependency** | AI_SETUP.md, DOMAIN_SCHEMA.md |
| **Dokumen terkait** | PROMPT_SPECIFICATION.md, CONTENT_INTELLIGENCE.md |
| **Urutan implementasi** | Phase 2, 8 |

---

### PROMPT_SPECIFICATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan prompt hierarchy, system prompt, task prompt, schema contract, repair prompt, critic prompt, prompt versioning |
| **Kapan dibaca** | Saat menulis atau memodifikasi prompt AI; saat debugging output AI yang tidak sesuai |
| **Dependency** | AI_AGENT_ORCHESTRATION.md |
| **Dokumen terkait** | CONTENT_TO_BLUEPRINT_ALGORITHM.md |
| **Urutan implementasi** | Phase 2, 8 |

---

### CONTENT_TO_BLUEPRINT_ALGORITHM.md

| Field | Detail |
|---|---|
| **Tujuan** | Algoritma lengkap dari content unit → classification → section planning → page candidate → page type selection → blueprint validation |
| **Kapan dibaca** | Saat mengimplementasikan logic utama AI pipeline; saat debugging hasil Blueprint yang tidak tepat |
| **Dependency** | CONTENT_INTELLIGENCE.md, DOMAIN_SCHEMA.md, PAGE_TYPE_LIBRARY.md |
| **Dokumen terkait** | AI_AGENT_ORCHESTRATION.md |
| **Urutan implementasi** | Phase 8 |

---

## 03_DOCUMENT_DESIGN

### DESIGN_SYSTEM.md

| Field | Detail |
|---|---|
| **Tujuan** | Design philosophy, visual hierarchy, color system, typography, spacing, grid, component principles |
| **Kapan dibaca** | Sebelum membuat template HTML/CSS; sebelum mendefinisikan Theme |
| **Dependency** | DOMAIN_SCHEMA.md |
| **Dokumen terkait** | COMPONENT_SPECIFICATION.md, A4_TUTORIAL_SPECIFICATION.md, PRESENTATION_16_9_SPECIFICATION.md |
| **Urutan implementasi** | Phase 5 — Design System |

---

### DESIGN_REFERENCE_ANALYSIS.md

| Field | Detail |
|---|---|
| **Tujuan** | Definisi karakter desain yang ingin dicapai, analisis good/bad design signal, checklist evaluasi visual |
| **Kapan dibaca** | Sebelum membuat template; saat review desain halaman |
| **Dependency** | DESIGN_SYSTEM.md |
| **Dokumen terkait** | PAGE_TYPE_LIBRARY.md, QUALITY_ASSURANCE.md |
| **Urutan implementasi** | Phase 5 |

---

### PAGE_TYPE_LIBRARY.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan semua page type yang tersedia (Cover, Process Flow, Comparison, dll) beserta purpose, suitable information, required fields, density rules |
| **Kapan dibaca** | Setelah DESIGN_SYSTEM.md; saat mengimplementasikan page type selection logic |
| **Dependency** | DESIGN_SYSTEM.md, DOMAIN_SCHEMA.md |
| **Dokumen terkait** | CONTENT_TO_BLUEPRINT_ALGORITHM.md, COMPONENT_SPECIFICATION.md |
| **Urutan implementasi** | Phase 5–6 |

---

### COMPONENT_SPECIFICATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan semua komponen visual (Heading, Card, ProcessStep, dll) beserta input, output, style contract, overflow behavior |
| **Kapan dibaca** | Saat mengimplementasikan template HTML/CSS untuk komponen |
| **Dependency** | DESIGN_SYSTEM.md |
| **Dokumen terkait** | PAGE_TYPE_LIBRARY.md, A4_TUTORIAL_SPECIFICATION.md |
| **Urutan implementasi** | Phase 5–6 |

---

### A4_TUTORIAL_SPECIFICATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Spesifikasi lengkap mode A4 landscape: canvas, safe area, grid, typography hierarchy, density, overflow rules, page splitting algorithm |
| **Kapan dibaca** | Saat mengimplementasikan A4 tutorial mode |
| **Dependency** | DESIGN_SYSTEM.md, COMPONENT_SPECIFICATION.md, PAGE_TYPE_LIBRARY.md |
| **Dokumen terkait** | PDF_RENDERING.md, PRESENTATION_16_9_SPECIFICATION.md |
| **Urutan implementasi** | Phase 6 — A4 Tutorial MVP |

---

### PRESENTATION_16_9_SPECIFICATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Spesifikasi mode presentasi 16:9: canvas, slide density, visual dominance, overflow handling |
| **Kapan dibaca** | Saat mengimplementasikan presentation mode |
| **Dependency** | DESIGN_SYSTEM.md, COMPONENT_SPECIFICATION.md, PAGE_TYPE_LIBRARY.md |
| **Dokumen terkait** | A4_TUTORIAL_SPECIFICATION.md, PDF_RENDERING.md |
| **Urutan implementasi** | Phase 7 — Presentation 16:9 MVP |

---

## 04_RENDERING

### PDF_RENDERING.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan pipeline rendering Blueprint → HTML → CSS → Playwright → PDF; CSS strategy, template architecture, font loading, render failure |
| **Kapan dibaca** | Saat mengimplementasikan rendering engine; saat debugging render failure |
| **Dependency** | DOMAIN_SCHEMA.md, A4_TUTORIAL_SPECIFICATION.md, PRESENTATION_16_9_SPECIFICATION.md |
| **Dokumen terkait** | QUALITY_ASSURANCE.md |
| **Urutan implementasi** | Phase 4 — Static Renderer |

---

## 05_QUALITY

### QUALITY_ASSURANCE.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan QA pipeline: schema QA, content QA, layout QA, render QA, PDF QA, visual QA, issue severity, revision policy |
| **Kapan dibaca** | Setelah rendering pipeline berjalan; saat mengimplementasikan quality inspection |
| **Dependency** | PDF_RENDERING.md, DOMAIN_SCHEMA.md |
| **Dokumen terkait** | QUALITY_SCORING_RUBRIC.md |
| **Urutan implementasi** | Phase 9 — Quality System |

---

### QUALITY_SCORING_RUBRIC.md

| Field | Detail |
|---|---|
| **Tujuan** | Sistem scoring kualitas: kategori, bobot, subcriteria, threshold, pass/fail, revision trigger |
| **Kapan dibaca** | Saat mengimplementasikan quality scoring; saat kalibrasi threshold kualitas |
| **Dependency** | QUALITY_ASSURANCE.md |
| **Dokumen terkait** | DESIGN_REFERENCE_ANALYSIS.md |
| **Urutan implementasi** | Phase 9 |

---

## 06_ENGINEERING

### CLI_SPECIFICATION.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan semua CLI command (doctor, models, generate, plan, render, inspect) beserta syntax, arguments, output, exit codes |
| **Kapan dibaca** | Saat mengimplementasikan CLI; saat menulis test untuk CLI |
| **Dependency** | ARCHITECTURE.md |
| **Dokumen terkait** | TESTING_STRATEGY.md |
| **Urutan implementasi** | Phase 1 (doctor), Phase 2 (models), Phase 6+ (generate, plan, render, inspect) |

---

### TESTING_STRATEGY.md

| Field | Detail |
|---|---|
| **Tujuan** | Mendefinisikan strategi testing: unit tests, integration tests, provider mocks, schema tests, renderer tests, PDF tests, regression, benchmark |
| **Kapan dibaca** | Sebelum menulis test apapun; saat merancang test fixtures |
| **Dependency** | PROJECT_CONVENTIONS.md, DOMAIN_SCHEMA.md |
| **Dokumen terkait** | CLI_SPECIFICATION.md, QUALITY_ASSURANCE.md |
| **Urutan implementasi** | Dimulai Phase 1, diterapkan di setiap phase |

---

### DEVELOPMENT_ROADMAP.md

| Field | Detail |
|---|---|
| **Tujuan** | Roadmap phase-by-phase: objective, prerequisites, scope, tasks, deliverables, exit criteria untuk setiap phase |
| **Kapan dibaca** | Di awal setiap phase baru; saat merencanakan sprint |
| **Dependency** | MASTER_IMPLEMENTATION_SPEC.md |
| **Dokumen terkait** | Semua dokumen |
| **Urutan implementasi** | Phase 0 — referensi sepanjang proyek |

---

## 07_IMPLEMENTATION

### MASTER_IMPLEMENTATION_SPEC.md

| Field | Detail |
|---|---|
| **Tujuan** | Single high-level source of truth yang menyatukan vision, architecture, directory, AI infrastructure, schemas, design, rendering, quality, CLI, testing, roadmap |
| **Kapan dibaca** | Sebelum memulai implementasi apapun; saat ada keraguan tentang keputusan arsitektur |
| **Dependency** | Semua dokumen Foundation |
| **Dokumen terkait** | Semua dokumen |
| **Urutan implementasi** | Phase 0 — dibuat setelah Foundation selesai |

---

### MASTER_IMPLEMENTATION_PROMPT.md

| Field | Detail |
|---|---|
| **Tujuan** | Prompt untuk AI coding agent yang memaksa agent membaca dokumentasi, memeriksa repository, menentukan phase, dan mengimplementasikan secara bertahap |
| **Kapan dibaca** | Saat akan menggunakan AI coding agent untuk implementasi |
| **Dependency** | MASTER_IMPLEMENTATION_SPEC.md |
| **Dokumen terkait** | DEVELOPMENT_ROADMAP.md |
| **Urutan implementasi** | Phase 0 — digunakan sepanjang proyek |

---

## Matriks Dependency Dokumen

```
README
  └── DOCS_MANIFEST
  └── ARCHITECTURE
        └── DOMAIN_SCHEMA
              ├── CONTENT_INTELLIGENCE
              │     └── CONTENT_TO_BLUEPRINT_ALGORITHM
              ├── AI_AGENT_ORCHESTRATION
              │     └── PROMPT_SPECIFICATION
              ├── DESIGN_SYSTEM
              │     ├── COMPONENT_SPECIFICATION
              │     ├── PAGE_TYPE_LIBRARY
              │     ├── A4_TUTORIAL_SPECIFICATION
              │     │     └── PDF_RENDERING
              │     └── PRESENTATION_16_9_SPECIFICATION
              │           └── PDF_RENDERING
              └── PDF_RENDERING
                    └── QUALITY_ASSURANCE
                          └── QUALITY_SCORING_RUBRIC
  └── ENVIRONMENT_SETUP
        └── AI_SETUP
  └── SECURITY_AND_SECRETS
  └── PROJECT_CONVENTIONS
        └── TESTING_STRATEGY

MASTER_IMPLEMENTATION_SPEC ← menyatukan semua di atas
MASTER_IMPLEMENTATION_PROMPT ← menggunakan MASTER_IMPLEMENTATION_SPEC
```

---

## Status Dokumentasi

| File | Status | Batch |
|---|---|---|
| README.md | ✅ Selesai | 1 |
| DOCS_MANIFEST.md | ✅ Selesai | 1 |
| 01_FOUNDATION/ARCHITECTURE.md | ✅ Selesai | 1 |
| 01_FOUNDATION/DOMAIN_SCHEMA.md | ✅ Selesai | 1 |
| 01_FOUNDATION/ENVIRONMENT_SETUP.md | ✅ Selesai | 1 |
| 01_FOUNDATION/AI_SETUP.md | ✅ Selesai | 1 |
| 01_FOUNDATION/SECURITY_AND_SECRETS.md | ✅ Selesai | 1 |
| 01_FOUNDATION/PROJECT_CONVENTIONS.md | ✅ Selesai | 1 |
| 02_AI_INTELLIGENCE/CONTENT_INTELLIGENCE.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/AI_AGENT_ORCHESTRATION.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/PROMPT_SPECIFICATION.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/CONTENT_TO_BLUEPRINT_ALGORITHM.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/SEMANTIC_TAXONOMY.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/RESEARCH_TRACEABILITY.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/VISUAL_INTENT_MODEL.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/STRUCTURED_OUTPUT_CONTRACTS.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/FAILURE_AND_RECOVERY.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/BATCH_2_IMPLEMENTATION_REPORT.md | ✅ Selesai | 2 |
| 02_AI_INTELLIGENCE/BATCH_2_5_AUDIT_BASELINE.md | ✅ Selesai | 2.5 |
| 02_AI_INTELLIGENCE/IMPORT_GRAPH_AUDIT.md | ✅ Selesai | 2.5 |
| 02_AI_INTELLIGENCE/TESTING_HARDENING_REPORT.md | ✅ Selesai | 2.5 |
| 02_AI_INTELLIGENCE/BATCH_2_5_IMPLEMENTATION_REPORT.md | ✅ Selesai | 2.5 |
| 03_DOCUMENT_DESIGN/DESIGN_SYSTEM.md | ⬜ Belum | 3 |
| 03_DOCUMENT_DESIGN/DESIGN_REFERENCE_ANALYSIS.md | ⬜ Belum | 3 |
| 03_DOCUMENT_DESIGN/PAGE_TYPE_LIBRARY.md | ⬜ Belum | 3 |
| 03_DOCUMENT_DESIGN/COMPONENT_SPECIFICATION.md | ⬜ Belum | 3 |
| 03_DOCUMENT_DESIGN/A4_TUTORIAL_SPECIFICATION.md | ⬜ Belum | 3 |
| 03_DOCUMENT_DESIGN/PRESENTATION_16_9_SPECIFICATION.md | ⬜ Belum | 3 |
| 04_RENDERING/PDF_RENDERING.md | ⬜ Belum | 4 |
| 05_QUALITY/QUALITY_ASSURANCE.md | ⬜ Belum | 4 |
| 05_QUALITY/QUALITY_SCORING_RUBRIC.md | ⬜ Belum | 4 |
| 06_ENGINEERING/CLI_SPECIFICATION.md | ⬜ Belum | 5 |
| 06_ENGINEERING/TESTING_STRATEGY.md | ⬜ Belum | 5 |
| 06_ENGINEERING/DEVELOPMENT_ROADMAP.md | ⬜ Belum | 5 |
| 07_IMPLEMENTATION/MASTER_IMPLEMENTATION_SPEC.md | ⬜ Belum | 6 |
| 07_IMPLEMENTATION/MASTER_IMPLEMENTATION_PROMPT.md | ⬜ Belum | 6 |
