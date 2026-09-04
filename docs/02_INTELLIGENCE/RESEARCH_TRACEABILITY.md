# Research Traceability

## 1. Purpose
Mendefinisikan model graf konseptual untuk KTI yang melacak dari Masalah → Kesimpulan, memastikan dokumen tidak kehilangan komponen utamanya.

## 2. Model Relasi (`RelationshipType`)
Sistem membangun graf terarah (`ContentRelationship`) dengan edge seperti:
- `addresses`
- `supports`
- `derived_from`
- `measured_by`
- `analyzed_by`
- `interprets`
- `answers`
- `concludes_from`
- `based_on`
- `recommends`

## 3. Aturan Keterlacakan (Traceability Rules)
Sebuah dokumen riset dianggap sehat jika:
1. `CONCLUSION` memiliki edge `answers` ke `RESEARCH_QUESTION` atau `RESEARCH_OBJECTIVE`.
2. `RECOMMENDATION` memiliki edge `based_on` ke `FINDING`, `LIMITATION`, atau `IMPLICATION`.
3. `FINDING` memiliki sumber `derived_from` ke `DATA`.

Jika aturan ini terlanggar, sistem menghasilkan `TraceabilityWarning` (misal: `CONCLUSION_WITHOUT_OBJECTIVE_TRACE`, `RECOMMENDATION_WITHOUT_BASIS`).
Model datanya menggunakan schema `ResearchTraceability`.
