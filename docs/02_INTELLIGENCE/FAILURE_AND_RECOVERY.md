# Failure and Recovery Model

## 1. Purpose
Memastikan pipeline intelijen tidak hancur lebur di tengah jalan akibat kegagalan AI, timeout, atau format input yang buruk.

## 2. Failure Hierarchy
`app/core/exceptions.py` mengelompokkan kegagalan:
- **Input Layer**: `NormalizationError`, `SegmentationError`.
- **Classification Layer**: `ClassificationError`, `ResearchRoleDetectionError`.
- **Validation Layer**: `StructuredOutputError` (gagal repair JSON).
- **AI Layer**: `ModelTimeoutError`, `ProviderError`, `ModelUnavailableError`, `FallbackExhaustedError`.

Setiap Exception selalu mencatat `job_id` dan `step` untuk pelacakan *structured logging*.

## 3. Strategi Fallback
Diatur oleh `app/ai/fallback.py`:
1. **Model Utama (9Router)**: Router akan memilih Claude Sonnet untuk *reasoning* berat.
2. **Repair Loop**: Jika JSON rusak, minta Claude memperbaiki dirinya sendiri (via `OutputValidator`).
3. **Fallback Lokal (Ollama)**: Jika 9Router timeout / error 5xx, atau jika pengguna menyalakan `offline_mode`, sistem secara transparan mengalihkan tugas yang gagal ke Ollama (misal: Llama3), lalu menandai `fallback_used = True` di hasil akhir.
4. **Degradasi Gracefully**: Jika semua gagal, tahap bersangkutan mengembalikan default aman (contoh: `TEXT_FOCUSED`, `OTHER`), alih-alih me-raise exception yang menghentikan batch.
