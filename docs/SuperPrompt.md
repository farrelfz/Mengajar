# ============================================================
# MASTER CREATE PROMPT
# KIR AI DOCUMENT INTELLIGENCE
# COMPLETE TECHNICAL DOCUMENTATION GENERATION
# ============================================================

# ------------------------------------------------------------
# C — CHARACTER / ROLE
# ------------------------------------------------------------

Bertindaklah sebagai sebuah gabungan tim ahli yang terdiri dari:

1. Principal Software Architect
2. Senior Python AI Systems Engineer
3. LLM Application Architect
4. AI Agent Orchestration Engineer
5. Document Intelligence Engineer
6. Information Architecture Specialist
7. Senior UI / Editorial Design Systems Architect
8. HTML/CSS Print Rendering Engineer
9. PDF Generation Engineer
10. Quality Assurance Architect
11. Software Security Engineer
12. Technical Documentation Architect
13. Test Automation Engineer
14. CLI Application Designer

Anda bukan sekadar penulis dokumentasi.

Anda bertugas sebagai:

"Lead Architect yang sedang menyusun kontrak teknis lengkap
untuk sebuah sistem production-oriented."

Dokumentasi yang dibuat harus cukup jelas sehingga:

- developer baru dapat memahami proyek;
- AI coding agent dapat membaca dokumentasi dan mulai bekerja;
- setiap modul memiliki tanggung jawab yang jelas;
- dependency antar modul tidak ambigu;
- AI output memiliki kontrak data;
- renderer tidak menerima output AI mentah;
- roadmap implementasi dapat dilakukan bertahap;
- kualitas PDF dapat diuji;
- sistem dapat berkembang tanpa perlu rewrite besar.

Jangan membuat dokumentasi generik.

Jangan menggunakan kalimat kosong seperti:

"Implementasikan dengan best practice."

Sebaliknya, jelaskan:

- objek apa yang ada;
- field apa yang dimiliki;
- relasi antar objek;
- siapa yang bertanggung jawab;
- input;
- output;
- aturan;
- batasan;
- failure condition;
- validation;
- acceptance criteria.

# ------------------------------------------------------------
# R — REQUIRED TASK
# ------------------------------------------------------------

Tugas utama adalah membuat dokumentasi lengkap untuk proyek:

KIR AI DOCUMENT INTELLIGENCE

Sistem ini adalah aplikasi Python local-first yang mampu
mengubah materi mentah menjadi dokumen visual berkualitas tinggi.

Sistem harus mendukung dua output utama:

MODE 1
PDF Tutorial A4 Landscape

Digunakan untuk:

- tutorial;
- handbook;
- modul;
- panduan;
- pembekalan;
- materi pelatihan.

MODE 2
PDF Presentation 16:9

Digunakan untuk:

- presentasi;
- workshop;
- pemaparan;
- materi LDP;
- pembelajaran;
- training.

Sistem tidak boleh dipahami sebagai:

"text → PDF"

Sistem harus dirancang sebagai:

SOURCE MATERIAL
        ↓
CONTENT INGESTION
        ↓
CONTENT NORMALIZATION
        ↓
CONTENT INTELLIGENCE
        ↓
INFORMATION CLASSIFICATION
        ↓
DOCUMENT PLANNING
        ↓
BLUEPRINT GENERATION
        ↓
BLUEPRINT VALIDATION
        ↓
CONTENT COMPOSITION
        ↓
DESIGN DECISION
        ↓
PAGE COMPOSITION
        ↓
HTML / CSS RENDERING
        ↓
BROWSER PDF EXPORT
        ↓
QUALITY INSPECTION
        ↓
TARGETED REVISION
        ↓
FINAL PDF

Buat dokumentasi untuk seluruh sistem tersebut.

# ------------------------------------------------------------
# E — ENVIRONMENT / CONTEXT
# ------------------------------------------------------------

## PROJECT TYPE

Project Name:

KIR AI Document Intelligence

Project Style:

Local-first Python application.

Primary goals:

1. Menghasilkan PDF yang memiliki kualitas struktur,
   hierarki informasi, dan desain profesional.

2. Memisahkan:

   AI reasoning
   dari
   document rendering.

3. Mencegah AI menghasilkan HTML/CSS bebas secara langsung
   tanpa schema dan validation.

4. Membuat pipeline yang dapat diulang:

   input yang sama
   + blueprint yang sama
   + theme yang sama

   harus dapat menghasilkan output yang konsisten.

## EXISTING PROJECT STRUCTURE

Gunakan struktur proyek konseptual berikut:

KIR/
│
├── app/
│   ├── ai/
│   ├── agents/
│   ├── config/
│   ├── core/
│   ├── document/
│   ├── design/
│   ├── quality/
│   ├── rendering/
│   └── main.py
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
│
└── docs/

Dokumentasi harus menjelaskan apakah struktur tersebut
sudah tepat.

Jika ada struktur yang perlu ditambah atau dipindahkan,
jelaskan alasan dan dependency-nya.

Jangan mengubah struktur secara sembarangan.

## AI INFRASTRUCTURE

Sistem dapat menggunakan dua jalur AI.

PRIMARY PROVIDER:

9Router

OpenAI-compatible endpoint.

Contoh konsep konfigurasi:

AI_PROVIDER=9router

NINE_ROUTER_BASE_URL=http://127.0.0.1:20128/v1

NINE_ROUTER_API_KEY=${SECRET}

Model tidak boleh dihardcode secara permanen.

Konfigurasi model harus mendukung:

PLANNER_MODEL
WRITER_MODEL
DESIGN_MODEL
CRITIC_MODEL

LOCAL FALLBACK:

Ollama

Contoh:

OLLAMA_ENABLED=true

OLLAMA_BASE_URL=http://127.0.0.1:11434/v1

OLLAMA_MODEL=qwen3:8b

Sistem harus mendukung:

PRIMARY
        ↓ failure
RETRY
        ↓ failure
FALLBACK PROVIDER
        ↓ failure
CONTROLLED ERROR

API key tidak boleh:

- hardcoded;
- dimasukkan ke source code;
- muncul di log;
- dimasukkan ke contoh dokumentasi nyata.

Dokumentasi harus menggunakan placeholder.

## TARGET TECHNOLOGY

Gunakan asumsi teknologi berikut kecuali ada alasan kuat
untuk memberikan alternatif:

Language:
Python

Configuration:
Pydantic Settings
python-dotenv

Schema Validation:
Pydantic

Templating:
Jinja2

Rendering:
HTML + CSS

Browser Engine:
Playwright Chromium

PDF Inspection:
PyMuPDF / pypdf sesuai kebutuhan

Testing:
pytest

Project Configuration:
pyproject.toml

Jangan menambahkan framework besar tanpa alasan.

Jangan membuat UI web pada fase awal.

CLI adalah entry point utama.

# ------------------------------------------------------------
# A — ARCHITECTURAL OBJECTIVES
# ------------------------------------------------------------

Dokumentasi harus mendefinisikan objek utama sistem.

Minimal:

Document
Section
Page
Component
Theme
Blueprint
ContentUnit
AnalysisResult
QualityReport
QualityIssue
RenderJob
RenderArtifact
ProviderConfig
ModelConfig
GenerationRequest
GenerationResponse

Untuk setiap objek jelaskan:

1. Tujuan objek.
2. Tanggung jawab.
3. Field utama.
4. Required field.
5. Optional field.
6. Relasi dengan objek lain.
7. Lifecycle.
8. Validation rules.
9. Failure conditions.
10. Serialization format jika relevan.

Gunakan diagram:

OBJECT A
    │
    ├── contains → OBJECT B
    │
    ├── references → OBJECT C
    │
    └── produces → OBJECT D

Jelaskan dependency direction.

Target:

Presentation
        ↓
Application
        ↓
Domain
        ↑
Infrastructure

Domain tidak boleh bergantung langsung kepada:

- Playwright;
- 9Router;
- Ollama;
- filesystem implementation.

# ------------------------------------------------------------
# T — TECHNICAL CONSTRAINTS
# ------------------------------------------------------------

## GENERAL RULES

Dokumentasi harus:

- detail;
- implementable;
- konsisten;
- tidak generik;
- tidak berulang;
- memiliki relasi antar dokumen;
- menggunakan istilah yang konsisten.

Setiap dokumen harus memiliki:

1. Purpose
2. Scope
3. Non-Scope
4. Related Documents
5. Concepts
6. Object Definitions
7. Rules
8. Algorithms / Decision Logic
9. Input
10. Output
11. Failure Handling
12. Validation
13. Examples
14. Acceptance Criteria

Tidak semua bagian harus panjang jika memang tidak relevan,
tetapi struktur ini menjadi checklist.

## DO NOT

Jangan:

- membuat semua informasi menjadi bullet list;
- membuat dokumentasi hanya 500 kata;
- menulis "implement appropriately";
- menggunakan "etc." untuk menghindari spesifikasi;
- menggabungkan semua responsibility dalam satu modul;
- membuat AI output langsung menjadi HTML;
- memperkecil font otomatis untuk menyelesaikan overflow;
- menggunakan fallback tanpa error classification;
- membuat revision loop tanpa limit;
- membuat page type tanpa kontrak data;
- membuat komponen tanpa input/output definition;
- membuat roadmap tanpa exit criteria.

## DOCUMENT DEPTH

Setiap dokumen harus cukup detail untuk menjadi
implementation reference.

Untuk dokumen kompleks seperti:

MASTER_IMPLEMENTATION_SPEC
CONTENT_TO_BLUEPRINT_ALGORITHM
A4_TUTORIAL_SPECIFICATION
PRESENTATION_16_9_SPECIFICATION
COMPONENT_SPECIFICATION

jelaskan:

- decision rules;
- object interaction;
- state transitions;
- algorithm;
- pseudo-code;
- contoh JSON;
- contoh input;
- contoh output;
- edge case;
- error case.

# ------------------------------------------------------------
# E — EXPECTED DOCUMENT STRUCTURE
# ------------------------------------------------------------

Buat struktur:

docs/
│
├── README.md
├── DOCS_MANIFEST.md
│
├── 01_FOUNDATION/
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_SCHEMA.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── AI_SETUP.md
│   ├── SECURITY_AND_SECRETS.md
│   └── PROJECT_CONVENTIONS.md
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


# ============================================================
# DOCUMENT-SPECIFIC REQUIREMENTS
# ============================================================


============================================================
README.md
============================================================

Harus menjelaskan:

- apa proyek ini;
- masalah yang ingin diselesaikan;
- target output;
- dua document mode;
- pipeline;
- prinsip arsitektur;
- quick start;
- reading order;
- roadmap ringkas;
- glossary inti.


============================================================
DOCS_MANIFEST.md
============================================================

Harus menjadi peta dokumentasi.

Untuk setiap file:

- tujuan;
- kapan dibaca;
- dependency;
- dokumen yang terkait;
- urutan implementasi.


============================================================
ARCHITECTURE.md
============================================================

Harus menjelaskan:

- system context;
- layer architecture;
- module responsibilities;
- dependency rules;
- pipeline architecture;
- job lifecycle;
- state machine;
- artifact management;
- configuration flow;
- error propagation;
- extensibility strategy;
- observability.

Buat diagram ASCII yang jelas.


============================================================
DOMAIN_SCHEMA.md
============================================================

Harus mendefinisikan:

Document
Section
Page
Component
Blueprint
Theme
RenderJob
QualityReport

Untuk setiap schema:

- field;
- type;
- required;
- validation;
- relation.

Gunakan contoh JSON.

Jelaskan schema versioning.


============================================================
ENVIRONMENT_SETUP.md
============================================================

Harus berisi:

- Python setup;
- virtual environment;
- dependency installation;
- Playwright setup;
- directory verification;
- environment doctor;
- development command;
- troubleshooting;
- definition of healthy environment.


============================================================
AI_SETUP.md
============================================================

Harus menjelaskan:

- provider abstraction;
- 9Router;
- Ollama;
- `.env`;
- `.env.example`;
- endpoint verification;
- model discovery;
- model role assignment;
- retry strategy;
- fallback;
- timeout;
- structured output;
- offline mode.

Jangan memasukkan API key nyata.


============================================================
SECURITY_AND_SECRETS.md
============================================================

Harus menjelaskan:

- secret lifecycle;
- `.env`;
- git protection;
- log redaction;
- endpoint exposure;
- local service security;
- API key rotation;
- incident response.


============================================================
PROJECT_CONVENTIONS.md
============================================================

Harus menjelaskan:

- naming;
- Python style;
- typing;
- imports;
- exception strategy;
- logging;
- configuration;
- folder ownership;
- code review checklist;
- definition of done.


============================================================
CONTENT_INTELLIGENCE.md
============================================================

Harus menjelaskan:

- ingestion;
- normalization;
- segmentation;
- information classification;
- hierarchy detection;
- relationship extraction;
- density analysis;
- source fidelity;
- content transformation.

Definisikan taxonomy informasi.

Contoh:

DEFINITION
EXPLANATION
SEQUENCE
COMPARISON
CAUSE_EFFECT
HIERARCHY
DATA
EXAMPLE
ACTIVITY
CHECKLIST
SUMMARY


============================================================
AI_AGENT_ORCHESTRATION.md
============================================================

Definisikan:

Document Planner
Content Writer
Design Director
Quality Critic

Untuk masing-masing:

- responsibility;
- input;
- output;
- allowed actions;
- prohibited actions;
- failure mode.

Jelaskan:

agent handoff;
shared state;
revision loop;
call budget;
fallback.


============================================================
PROMPT_SPECIFICATION.md
============================================================

Definisikan:

- prompt hierarchy;
- system prompt;
- task prompt;
- context injection;
- schema contract;
- JSON rules;
- repair prompt;
- critic prompt;
- prompt versioning.

Berikan template.


============================================================
CONTENT_TO_BLUEPRINT_ALGORITHM.md
============================================================

Ini salah satu dokumen terpenting.

Harus menjelaskan secara algoritmik:

INPUT CONTENT
        ↓
NORMALIZATION
        ↓
CONTENT UNIT EXTRACTION
        ↓
CLASSIFICATION
        ↓
SEMANTIC RELATION DETECTION
        ↓
SECTION PLANNING
        ↓
PAGE CANDIDATE CREATION
        ↓
PAGE TYPE SELECTION
        ↓
DENSITY VALIDATION
        ↓
PAGE SPLITTING / MERGING
        ↓
BLUEPRINT VALIDATION

Buat:

- algorithm;
- pseudo-code;
- decision tree;
- scoring logic;
- edge cases.

Page type harus dipilih berdasarkan information shape,
bukan sekadar random aesthetic.


============================================================
DESIGN_SYSTEM.md
============================================================

Harus menjelaskan:

- design philosophy;
- visual hierarchy;
- color system;
- typography;
- spacing;
- grid;
- whitespace;
- component principles;
- responsive/fixed canvas logic;
- accessibility;
- anti-pattern.


============================================================
DESIGN_REFERENCE_ANALYSIS.md
============================================================

Jangan sekadar menyebut "Claude style".

Definisikan karakter desain yang ingin dicapai:

- editorial;
- information hierarchy;
- intentional whitespace;
- visual rhythm;
- component consistency;
- restrained color;
- controlled emphasis.

Analisis:

GOOD DESIGN SIGNAL
BAD DESIGN SIGNAL

Buat checklist evaluasi.


============================================================
PAGE_TYPE_LIBRARY.md
============================================================

Definisikan seluruh page types.

Minimal:

Cover
Section Opener
Roadmap
Process Flow
Comparison
Card Grid
Concept Diagram
Table
Case Study
Checklist
Summary

Untuk masing-masing:

- purpose;
- suitable information;
- unsuitable information;
- required fields;
- layout variants;
- density rules;
- fallback.


============================================================
COMPONENT_SPECIFICATION.md
============================================================

Definisikan component:

Heading
Paragraph
Card
Badge
Callout
ProcessStep
ComparisonColumn
Table
Checklist
DiagramNode
ImageBlock
FormulaBlock

Untuk masing-masing:

- input;
- output;
- style contract;
- size rules;
- allowed contexts;
- accessibility;
- overflow behavior.


============================================================
A4_TUTORIAL_SPECIFICATION.md
============================================================

Harus sangat detail.

Definisikan:

- A4 landscape canvas;
- safe area;
- grid;
- typography hierarchy;
- information density;
- page composition;
- reading behavior;
- recommended page types;
- paragraph rules;
- table rules;
- image rules;
- overflow rules;
- page splitting algorithm.

Jelaskan bahwa A4 adalah:

VISUAL HANDBOOK

bukan slide.


============================================================
PRESENTATION_16_9_SPECIFICATION.md
============================================================

Definisikan:

- 16:9 canvas;
- safe area;
- presentation hierarchy;
- headline rule;
- supporting text;
- concept limits;
- slide density;
- visual dominance;
- speaker support;
- diagram rules;
- transition rhythm;
- overflow handling.

Jelaskan bahwa slide bukan:

A4 yang diregangkan.


============================================================
PDF_RENDERING.md
============================================================

Harus menjelaskan:

Blueprint
↓
Composer
↓
Template
↓
HTML
↓
CSS
↓
Playwright
↓
PDF

Jelaskan:

- fixed canvas;
- CSS strategy;
- template architecture;
- font loading;
- asset loading;
- browser lifecycle;
- print configuration;
- PDF metadata;
- render failure;
- artifact preservation.


============================================================
QUALITY_ASSURANCE.md
============================================================

Definisikan:

- schema QA;
- content QA;
- layout QA;
- render QA;
- PDF QA;
- visual QA.

Jelaskan issue:

severity;
evidence;
page_id;
recommended action.

Buat revision policy.


============================================================
QUALITY_SCORING_RUBRIC.md
============================================================

Buat sistem scoring.

Kategori minimal:

Content Structure
Readability
Visual Hierarchy
Layout Integrity
Consistency
Technical Validity
Source Fidelity

Definisikan:

- bobot;
- subcriteria;
- scoring method;
- threshold;
- pass/fail;
- revision trigger.


============================================================
CLI_SPECIFICATION.md
============================================================

Definisikan command:

doctor
models
generate
plan
render
inspect

Untuk masing-masing:

- syntax;
- arguments;
- output;
- exit codes;
- errors.


============================================================
TESTING_STRATEGY.md
============================================================

Definisikan:

- unit tests;
- integration tests;
- provider mocks;
- schema tests;
- renderer tests;
- PDF tests;
- regression;
- benchmark;
- test fixtures.


============================================================
DEVELOPMENT_ROADMAP.md
============================================================

Buat phase-by-phase.

Minimal:

Phase 0 Documentation
Phase 1 Environment
Phase 2 AI Infrastructure
Phase 3 Domain Schema
Phase 4 Static Renderer
Phase 5 Design System
Phase 6 A4 MVP
Phase 7 16:9 MVP
Phase 8 Content Intelligence
Phase 9 Quality System
Phase 10 Importers
Phase 11 Production Hardening

Untuk setiap phase:

- objective;
- prerequisites;
- scope;
- non-scope;
- tasks;
- deliverables;
- tests;
- exit criteria.


============================================================
MASTER_IMPLEMENTATION_SPEC.md
============================================================

Ini adalah dokumen utama.

Dokumen ini harus menyatukan:

- vision;
- architecture;
- directory;
- AI infrastructure;
- schemas;
- intelligence;
- design;
- rendering;
- quality;
- CLI;
- testing;
- roadmap.

Dokumen ini harus menjadi:

"SINGLE HIGH-LEVEL SOURCE OF TRUTH"

Namun tidak boleh menduplikasi seluruh isi dokumen lain.

Gunakan referensi ke dokumen spesifik.


============================================================
MASTER_IMPLEMENTATION_PROMPT.md
============================================================

Buat prompt untuk AI coding agent.

Prompt harus memaksa agent untuk:

1. membaca dokumentasi yang relevan;
2. memeriksa repository;
3. menentukan phase saat ini;
4. membuat implementation plan;
5. meminta klarifikasi jika ada kontradiksi penting;
6. mengimplementasikan hanya scope phase;
7. tidak membuat future features;
8. menjalankan tests;
9. memperbaiki failure;
10. memperbarui docs jika kontrak berubah.

Tambahkan:

STRICT RULES

DO NOT:

- create UI unless requested;
- hardcode secrets;
- bypass schema validation;
- let raw AI output reach renderer;
- generate arbitrary CSS from AI;
- solve overflow only by shrinking fonts;
- skip tests;
- silently change architecture;
- automatically proceed to next phase.


# ------------------------------------------------------------
# OUTPUT REQUIREMENTS
# ------------------------------------------------------------

Jangan membuat seluruh dokumentasi dalam satu respons
yang kemudian terpotong.

Kerjakan secara bertahap.

URUTAN:

STEP 1

Analisis struktur dokumentasi.

Output:

DOCUMENTATION ARCHITECTURE PLAN

STEP 2

Buat seluruh dokumen Foundation.

STEP 3

Buat seluruh dokumen AI Intelligence.

STEP 4

Buat seluruh dokumen Document Design.

STEP 5

Buat Rendering dan Quality.

STEP 6

Buat Engineering.

STEP 7

Buat Master Implementation documents.

Untuk setiap dokumen:

- tulis nama file;
- tulis tujuan;
- tulis dependency;
- tulis konten lengkap;
- lakukan consistency check terhadap dokumen sebelumnya.

Jangan melanjutkan dengan asumsi bahwa dokumen sebelumnya
benar jika ditemukan konflik.

Laporkan konflik secara eksplisit.

# ------------------------------------------------------------
# FINAL VALIDATION
# ------------------------------------------------------------

Setelah seluruh dokumentasi selesai, lakukan:

1. Cross-document consistency audit.

Periksa:

- terminology;
- object names;
- pipeline stages;
- directory names;
- provider names;
- schema references;
- roadmap phases.

2. Documentation completeness audit.

Periksa apakah setiap requirement memiliki dokumen.

3. Implementation readiness audit.

Nilai:

Architecture Readiness
AI Infrastructure Readiness
Schema Readiness
Design Readiness
Rendering Readiness
Quality Readiness
Testing Readiness

Gunakan:

NOT READY
PARTIALLY READY
READY

4. Buat final:

DOCUMENTATION_COMPLETENESS_REPORT.md

Isi:

- seluruh file;
- status;
- dependency;
- missing area;
- implementation readiness.

# ============================================================
# END MASTER CREATE PROMPT
# ============================================================