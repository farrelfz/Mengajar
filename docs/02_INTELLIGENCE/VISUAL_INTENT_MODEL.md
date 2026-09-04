# Visual Intent Model

## 1. Purpose
Mendeteksi intent visual potensial dari suatu blok teks *sebelum* tahap render, sehingga Design System dapat memilih komponen yang tepat.

## 2. Visual Intents (`VisualIntent`)
Kandidat intent yang dideteksi oleh AI:
- `TEXT_FOCUSED`: (Default) Teks naratif standar.
- `HIERARCHICAL`: Struktur pohon / sub-poin.
- `SEQUENTIAL`: Langkah yang harus diikuti berurutan (misal: BAB 3 Metode).
- `COMPARATIVE`: Dua atau lebih entitas dipertentangkan.
- `PROCESS_FLOW`: Alur kerja atau algoritma.
- `DATA_TREND`: Angka pengukuran bertahap (membutuhkan chart garis).
- `DATA_COMPARISON`: Angka pengukuran antar subjek (bar chart).
- `TIMELINE`: Peristiwa berurut kronologis.
- `EVIDENCE_GALLERY`: Kumpulan quote atau data mentah (misal: transkrip).
- `KEY_MESSAGE`: Kalimat punchline (pull-quote).

## 3. Contract Rules
Batch 2 **HANYA** menghasilkan usulan klasifikasi semantik ini.
Tidak boleh ada satu pun atribut yang menentukan warna, font, margin, kolom flexbox, atau CSS class di tahap ini.
