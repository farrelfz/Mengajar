# Content-to-Blueprint Algorithm

## 1. Purpose
Mengubah `AnalysisResult` (kumpulan unit semantik) menjadi `BlueprintProposal` (pengelompokan halaman logis) tanpa mengambil keputusan desain CSS atau tata letak akhir.

## 2. Conceptual Model
Input: `ContentUnit[]` (terklasifikasi, dengan relasi dan skor).
Output: `ContentGroup[]` (kandidat blok siap desain).

Algoritma difokuskan untuk menjawab:
- Apa yang harus dikelompokkan bersama? (Semantic Continuity)
- Apa yang butuh perlakuan visual khusus? (Visual Intent)
- Seberapa padat informasi ini? (Density Estimation)

## 3. Aturan Pengelompokan (Grouping Rules)
Algoritma (`app/intelligence/blueprint_proposer.py`) menggunakan heuristik deterministik:
1. **Heading Boundaries**: Sebuah heading tipe `TITLE` selalu memulai grup baru.
2. **Semantic Boundaries**: Perubahan tajam dalam peran (misal, transisi dari `DATA` ke `INTERPRETATION` atau `CONCLUSION`) memaksa pembuatan grup baru untuk memastikan pemisahan logis.
3. **Continuity**: Menetapkan `previous_group_dependency` agar mesin layout (Batch 3) tidak memisahkan grup yang saling berkaitan erat.

## 4. Blueprint Candidate Types
Kandidat desain semantik (BUKAN HTML/CSS):
- `TITLE_BLOCK`
- `RESEARCH_RESULT_BLOCK`
- `CONCLUSION_BLOCK`
- `PROCESS_SEQUENCE`
- `COMPARISON_BLOCK`
- `GENERIC_CONTENT`

Mesin layout di Batch 3 akan memetakan kandidat ini ke spesifikasi A4 atau Presentasi 16:9 yang sesuai.
