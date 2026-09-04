# Semantic Taxonomy

## 1. Purpose
Mendefinisikan tipe-tipe semantik dari setiap `ContentUnit` yang diproses. Sistem harus tahu bukan hanya "apa teksnya", tapi "apa peran semantiknya".

## 2. General Content Types
Tipe umum (`app/intelligence/schemas.py:ContentType`) meliputi lebih dari 40 nilai, di antaranya:
- `DEFINITION`, `EXPLANATION`, `CONTEXT`, `BACKGROUND`, `PROBLEM`
- `QUESTION`, `OBJECTIVE`, `HYPOTHESIS`, `CONCEPT`, `THEORY`
- `PROCEDURE`, `SEQUENCE`, `COMPARISON`, `CAUSE_EFFECT`
- `DATA`, `RESULT`, `FINDING`, `ANALYSIS`, `INTERPRETATION`, `CONCLUSION`
- `WARNING`, `TIP`, `FORMULA`

## 3. KTI Research Roles
Perluasan untuk `RESEARCH_REPORT` (BAB 1–5):
- `RESEARCH_PROBLEM`, `RESEARCH_QUESTION`, `RESEARCH_OBJECTIVE`
- `THEORETICAL_FOUNDATION`, `RESEARCH_GAP_KTI`
- `RESEARCH_METHOD`, `RESEARCH_DESIGN`, `DATA_SOURCE`
- `RESEARCH_RESULT`, `RESEARCH_FINDING`, `RESEARCH_INTERPRETATION`, `RESEARCH_DISCUSSION`
- `RESEARCH_CONCLUSION`, `RESEARCH_RECOMMENDATION`

## 4. Validasi Kritis
Sistem **tidak boleh menyatukan** tipe-tipe ini secara otomatis:
- `DATA` ≠ `RESULT` ≠ `FINDING` ≠ `INTERPRETATION` ≠ `DISCUSSION`
- `CONCLUSION` ≠ `RECOMMENDATION`
- `LIMITATION` ≠ `FUTURE_WORK`
