# AI Agent Orchestration

## 1. Purpose
Mendefinisikan arsitektur agen berbasis tanggung jawab (responsibility-based agent architecture) untuk mengontrol aliran data kecerdasan konten, menjamin pemisahan tugas, dan menegakkan kontrak.

## 2. Agent Responsibility Matrix

| Agen | Input | Tanggung Jawab Utama | Output | Forbidden Actions |
|---|---|---|---|---|
| **Content Intelligence** | Raw Text, Genre | Menjalankan pipeline normalisasi hingga intent visual. | `AnalysisResult` | Tidak boleh membuat struktur halaman / blueprint. |
| **Document Planner** | `AnalysisResult` | Mengelompokkan unit menjadi kandidat blueprint. | `BlueprintProposal` | Tidak boleh mengubah teks sumber. |
| **Quality Critic** | `BlueprintProposal` | Mengevaluasi fidelity sumber dan keterlacakan. | `AIQualityCritique` | Tidak boleh me-rewrite teks tanpa mencatat overrides. |

*(Catatan: Agen desain dan rendering ditangguhkan ke Batch 3).*

## 3. Orchestration Flow (`IntelligencePipeline`)

1. **Inisialisasi**: Pipeline menerima input mentah dan profil target (`DocumentGenre`, `DocumentMode`).
2. **Eksekusi Pipeline**:
   - `ContentIntelligenceAgent` memanggil normalizer, segmenter, dan multi-prompt LLM secara berurutan.
   - Mengembalikan `AnalysisResult` terstruktur.
3. **Perencanaan Blueprint**:
   - `DocumentPlanner` memproses `AnalysisResult` menjadi grup-grup koheren (`BlueprintProposal`).
4. **Kritik Kualitas**:
   - `QualityCritic` meninjau `BlueprintProposal`. Jika menemukan isu fatal (contoh: halusinasi), ia melampirkan *warnings*.

## 4. Failure and Recovery
Orkestrasi dibungkus dalam blok try-catch dengan kategori kegagalan terstruktur (`FailureCategory`). Semua interaksi LLM melalui agen di-validate oleh `OutputValidator`.
