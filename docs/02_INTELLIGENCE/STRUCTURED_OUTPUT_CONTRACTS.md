# Structured Output Contracts

## 1. Purpose
LLM dianggap sebagai sumber "UNTRUSTED INPUT". Semua respon dari agen AI wajib divalidasi ke dalam skema Pydantic (`app/intelligence/schemas.py`).

## 2. Kontrak Utama
- `AIClassificationOutput`: Hasil klasifikasi (mendukung fallback & alasan keyakinan).
- `AIRelationshipOutput`: Hasil ekstraksi relasi graf.
- `AIVisualIntentOutput`: Hasil deteksi usulan desain.
- `AIQualityCritiqueOutput`: Hasil review.
- `AIDocumentPlanOutput`: Opsi luaran dari DocumentPlanner (jika LLM digunakan).

## 3. Validator (`OutputValidator`)
Validator (`app/intelligence/output_validator.py`) secara otomatis:
1. Memotong (strip) *markdown blocks* (e.g. ````json ... ````).
2. Mem-parse JSON.
3. Mem-validasi lewat `schema.model_validate()`.
4. Jika gagal, validator otomatis melakukan **Repair Prompting** (mengirim kembali pesan error Pydantic ke model agar ia memperbaiki JSON-nya sendiri), hingga `max_repair_attempts`.
