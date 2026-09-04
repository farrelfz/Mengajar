# KTI Domain Expansion Report — KIR AI Document Intelligence

> **Date:** 2026-08-23  
> **Jenis:** Domain Knowledge Patch  
> **Scope:** KTI / Research Report BAB 1–5 Domain Expansion  
> **Bukan:** Architecture Rewrite

---

## 1. Purpose

Patch ini memperluas pemahaman domain KIR AI Document Intelligence dari konteks dokumen tutorial/modul semata menjadi pemahaman penuh terhadap **Karya Tulis Ilmiah (KTI)** dan dokumen penelitian.

KTI memiliki alur naratif ilmiah yang ketat (BAB 1–5) dengan keterlacakan antar komponen yang harus dipertahankan saat ditransformasi menjadi dokumen visual. Tanpa model domain ini, sistem AI tidak akan mampu membedakan antara `DATA` dan `INTERPRETASI`, antara `FINDING` dan `CONCLUSION`, atau memverifikasi bahwa alur penelitian telah terwakili secara lengkap.

---

## 2. Scope of Change

### Dalam Scope

- Definisi model domain KTI BAB 1–5
- Peran semantik setiap komponen penelitian
- Perluasan enum `ContentType` untuk mencakup semua peran semantik KTI
- Perluasan schema `AnalysisResult` dengan `document_genre` dan `research_traceability`
- Penambahan schema baru `ResearchTraceability` dan `DocumentGenre`
- Penambahan enum `KtiBab`
- Prinsip source fidelity
- Aturan keterlacakan penelitian

### Luar Scope

- Desain visual halaman KTI (CSS, template)
- Implementasi kode Python
- Modifikasi pipeline AI provider (9Router, Ollama)
- Perubahan arsitektur layer
- Konfigurasi environment variable

---

## 3. Files Reviewed

| File | Status Review |
|---|---|
| `docs/README.md` | ✅ Reviewed — Diperbarui (genre section) |
| `docs/DOCS_MANIFEST.md` | ✅ Reviewed — Diperbarui (2 entry baru) |
| `docs/01_FOUNDATION/ARCHITECTURE.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |
| `docs/01_FOUNDATION/DOMAIN_SCHEMA.md` | ✅ Reviewed — Diperbarui (ContentType, AnalysisResult, ResearchTraceability) |
| `docs/01_FOUNDATION/AI_SETUP.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |
| `docs/01_FOUNDATION/SECURITY_AND_SECRETS.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |
| `docs/01_FOUNDATION/PROJECT_CONVENTIONS.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |
| `docs/01_FOUNDATION/ENVIRONMENT_SETUP.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |
| `docs/01_FOUNDATION/FOUNDATION_AUDIT_REPORT.md` | ✅ Reviewed — Tidak ada konflik. Tidak dimodifikasi. |

---

## 4. Conflicts Found

### 4.1 Terminologi

Tidak ditemukan konflik terminologi antara BATCH 1 dan domain KTI yang baru.

Terminologi kanonik BATCH 1 (`ContentUnit`, `AnalysisResult`, `Blueprint`, dll.) **kompatibel** dengan kebutuhan domain KTI. Perluasan dilakukan secara **additive** (menambahkan field opsional dan nilai enum baru) tanpa menghapus atau mengubah kontrak yang sudah ada.

### 4.2 Architecture

Tidak ditemukan konflik arsitektur. Model KTI berada pada layer **domain knowledge** (pemahaman semantik konten), bukan pada layer infrastructure atau rendering.

---

## 5. Changes Applied

### 5.1 docs/README.md

| Perubahan | Rationale |
|---|---|
| Menambahkan `(KTI), karya ilmiah` pada deskripsi MODE 1 | KTI biasanya di-render sebagai A4 landscape |
| Menambahkan `pemaparan hasil penelitian` pada MODE 2 | Presentasi hasil penelitian juga didukung |
| Menambahkan section "Genre Dokumen yang Didukung" | Memperjelas bahwa TUTORIAL dan RESEARCH_REPORT adalah dua genre berbeda |
| Menambahkan link ke KTI_DOMAIN_MODEL.md | Navigasi ke dokumen domain baru |

### 5.2 docs/DOCS_MANIFEST.md

| Perubahan | Rationale |
|---|---|
| Menambahkan `KTI_DOMAIN_MODEL.md` ke directory tree | File baru harus terdaftar |
| Menambahkan `FOUNDATION_AUDIT_REPORT.md` ke directory tree | File yang sudah ada belum terdaftar |
| Menambahkan entry manifest untuk `KTI_DOMAIN_MODEL.md` | Deskripsi, dependency, kapan dibaca |
| Menambahkan entry manifest untuk `FOUNDATION_AUDIT_REPORT.md` | Deskripsi, dependency, kapan dibaca |

### 5.3 docs/01_FOUNDATION/DOMAIN_SCHEMA.md

| Perubahan | Rationale |
|---|---|
| Memperluas `ContentType` enum dengan 27 nilai KTI baru | Sistem harus dapat mengklasifikasikan setiap peran semantik KTI |
| Menambahkan field `document_genre: DocumentGenre` ke `AnalysisResult` | Diperlukan untuk routing ke intelligence path yang berbeda |
| Menambahkan field `research_traceability: ResearchTraceability | None` ke `AnalysisResult` | Peta keterlacakan penelitian hanya relevan untuk genre RESEARCH_REPORT |
| Menambahkan enum `DocumentGenre` (TUTORIAL, RESEARCH_REPORT, PRESENTATION, GENERAL) | Mendukung deteksi otomatis genre dokumen |
| Menambahkan schema `ResearchTraceability` (Section 6.21) | Kontrak data untuk peta keterlacakan penelitian |
| Menambahkan enum `KtiBab` (BAB_1 s.d. BAB_5) | Digunakan dalam `detected_bab_coverage` |
| Memperbarui diagram relasi objek di Section 7 | Mencerminkan penambahan `ResearchTraceability` |
| Memperbarui Acceptance Criteria di Section 8 | Menambahkan 4 kriteria baru terkait KTI |

### 5.4 docs/01_FOUNDATION/KTI_DOMAIN_MODEL.md (BARU)

Dokumen baru — 18 section — mendefinisikan seluruh model domain KTI:
- Conceptual Research Flow
- Canonical BAB 1–5 Structure
- Core vs Optional vs Method-Dependent Components
- Detailed BAB 1–5 Semantic Models
- BAB 4 Hierarchy (DATA → FINDING → ANALYSIS → INTERPRETATION → DISCUSSION → THEORY_CONNECTION)
- BAB 5 Traceability (CONCLUSION → RESEARCH_QUESTION / RESEARCH_OBJECTIVE)
- Complete Research Traceability Graph
- Research Semantic Roles reference table
- Relationship Rules (antar BAB)
- Source Fidelity Rules
- Structural Variation support (KTI sekolah, skripsi, makalah, artikel jurnal)
- Edge Cases
- Worked Example konkret lengkap
- Acceptance Criteria

---

## 6. Domain Schema Extensions

| Proposed Object / Field | Existing Object | Action |
|---|---|---|
| `ContentType.RESEARCH_PROBLEM` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_QUESTION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_OBJECTIVE` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_BENEFIT` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.HYPOTHESIS` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.THEORETICAL_FOUNDATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.PRIOR_RESEARCH` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_GAP` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_METHOD` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_INSTRUMENT` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.DATA_COLLECTION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.DATA_ANALYSIS_METHOD` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RESEARCH_RESULT` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.FINDING` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.ANALYSIS` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.INTERPRETATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.DISCUSSION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.THEORY_CONNECTION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.PRIOR_RESEARCH_COMPARISON` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.HYPOTHESIS_EVALUATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.VISUALIZATION_CANDIDATE` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.CONCLUSION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.LIMITATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.IMPLICATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.RECOMMENDATION` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `ContentType.FUTURE_WORK` | `ContentType` | **EXTEND_EXISTING_OBJECT** — tambah nilai enum |
| `AnalysisResult.document_genre` | `AnalysisResult` | **EXTEND_EXISTING_OBJECT** — tambah field baru |
| `AnalysisResult.research_traceability` | `AnalysisResult` | **EXTEND_EXISTING_OBJECT** — tambah field opsional |
| `DocumentGenre` enum | — | **NEW_OBJECT_REQUIRED** — enum baru |
| `ResearchTraceability` | — | **NEW_OBJECT_REQUIRED** — schema Pydantic baru |
| `KtiBab` enum | — | **NEW_OBJECT_REQUIRED** — enum baru |

---

## 7. Terminology Changes

Tidak ada perubahan pada terminologi yang sudah ada dalam BATCH 1. Semua istilah baru bersifat **additive**.

| Istilah Baru | Definisi Kanonik | Hubungan dengan Terminologi Existing |
|---|---|---|
| `DocumentGenre` | Genre dokumen yang terdeteksi dari source material | Field baru di `AnalysisResult` |
| `ResearchTraceability` | Peta keterlacakan alur penelitian | Sub-object opsional di `AnalysisResult` |
| `KtiBab` | Enum BAB 1–5 yang terdeteksi dalam KTI | Digunakan dalam `ResearchTraceability` |
| `RESEARCH_REPORT` | Genre dokumen penelitian (KTI, skripsi, dll) | Nilai baru dalam `DocumentGenre` |
| `research_traceability` | Field di `AnalysisResult` untuk genre penelitian | Field opsional `AnalysisResult` |

---

## 8. Compatibility with Batch 1

### Schema Compatibility

Semua ekstensi bersifat **backward-compatible**:

1. Nilai enum `ContentType` yang baru **ditambahkan**, tidak menggantikan yang ada
2. Field baru di `AnalysisResult` bersifat **opsional** (`None` untuk dokumen tutorial biasa)
3. Tidak ada field yang **dihapus** atau **diganti namanya**
4. Schema `Blueprint`, `Document`, `Page`, `Component`, `Theme`, `RenderJob`, `QualityReport` tidak dimodifikasi

### Architecture Compatibility

Arsitektur layer (Presentation → Application → Domain → Infrastructure) **tidak berubah**.

Model KTI sepenuhnya berada di **Domain Layer** (`app/document/schema.py`) dan **Knowledge Layer** (prompt specification, content intelligence rules).

---

## 9. Remaining Risks

1. **Clasifier Ambiguity:** Beberapa unit konten mungkin dapat diklasifikasikan ke lebih dari satu `ContentType` KTI (contoh: paragraf yang berisi `FINDING` sekaligus `INTERPRETATION`). Penanganan ambiguitas ini akan didefinisikan di `CONTENT_INTELLIGENCE.md`.

2. **Incomplete Source Material:** KTI yang hanya berisi sebagian BAB masih akan diproses tanpa fatal error. Sistem akan memunculkan `traceability_warnings` yang tepat. Behavior ini sudah didokumentasikan dalam `ResearchTraceability.missing_critical_components`.

3. **Genre Detection Confidence:** Deteksi otomatis `DocumentGenre` adalah tugas inference AI. Dokumen ambigus (antara tutorial dan KTI) harus memiliki fallback ke `GENERAL`. Strategi ini akan dijabarkan di `CONTENT_INTELLIGENCE.md`.

---

## 10. Final Status

```
KTI DOMAIN EXPANSION PATCH:
COMPATIBLE WITH EXTENSIONS
```

Batch 1 tetap **READY**. Patch ini tidak membatalkan atau memerlukan perbaikan ulang pada dokumen Batch 1 yang sudah ada. Ekstensi domain schema bersifat backward-compatible.
