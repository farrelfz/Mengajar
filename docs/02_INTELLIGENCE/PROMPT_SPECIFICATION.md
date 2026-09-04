# Prompt Specification

## 1. Purpose
Mendefinisikan arsitektur prompt yang modular, versioned, dan berorientasi kapabilitas (capability-driven). Tidak ada prompt raksasa (giant prompts) yang disimpan secara hard-coded di dalam kode Python.

## 2. Struktur Prompt YAML
Semua prompt disimpan di `/prompts/` sebagai file YAML.

### Format Kontrak:
```yaml
name: [nama_prompt_vX]
description: [Tujuan]
version: "1.X"
capabilities:
  - semantic_reasoning | structured_output | critique

system_prompt: |
  [Peran AI]
  [Instruksi Utama]
  [Aturan Ketat (RULES)]
  
schema_hint: [Nama Pydantic Schema]
```

## 3. Daftar Prompt Batch 2
1. `content_intelligence_v1`: Klasifikasi tipe semantik umum.
2. `research_role_classifier_v1`: Deteksi spesifik peran KTI BAB 1–5.
3. `relationship_extractor_v1`: Pengekstrakan graf keterlacakan (is_derived_from, answers).
4. `visual_intent_detector_v1`: Usulan layout konseptual (PROCESS_FLOW, COMPARATIVE).
5. `quality_critic_v1`: Evaluasi halusinasi dan konsistensi struktur.

## 4. Aturan Kesetiaan Sumber (Source Fidelity)
- Prompt wajib melarang AI menemukan (hallucinating) data riset, sitasi, hasil eksperimen.
- Membedakan teks asli (source) dari penjelasan (inference).
- Tidak boleh diam-diam mengubah batasan (limitation) menjadi temuan (finding).
