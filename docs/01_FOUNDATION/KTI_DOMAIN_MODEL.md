# KTI DOMAIN MODEL — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/KTI_DOMAIN_MODEL.md`  
> **Tujuan:** Model pengetahuan kanonik untuk Karya Tulis Ilmiah (KTI) dan laporan penelitian  
> **Dependency:** DOMAIN_SCHEMA.md, ARCHITECTURE.md  
> **Dokumen terkait:** CONTENT_INTELLIGENCE.md, AI_AGENT_ORCHESTRATION.md, CONTENT_TO_BLUEPRINT_ALGORITHM.md

---

## 1. Purpose

Dokumen ini mendefinisikan model pengetahuan domain yang digunakan sistem KIR untuk memahami, menganalisis, dan memvisualisasikan **Karya Tulis Ilmiah (KTI)** serta dokumen penelitian sejenis.

KTI dalam konteks project ini adalah **genre dokumen khusus** yang berbeda secara fundamental dari tutorial atau modul pembelajaran biasa. KTI memiliki alur naratif penelitian yang ketat dengan keterlacakan antar komponen yang harus dipertahankan saat ditransformasi menjadi dokumen visual.

Dokumen ini menjadi acuan bagi:
1. **Content Intelligence** — mengidentifikasi dan mengklasifikasi unit informasi KTI
2. **Document Planner** — merancang struktur visual yang menghormati alur penelitian
3. **Prompt Specification** — prompt yang memahami peran semantik setiap unit konten
4. **Content-to-Blueprint Algorithm** — mapping dari konten ke halaman dan komponen visual

---

## 2. Scope

- Definisi KTI dan varian strukturnya (skripsi, makalah, laporan penelitian)
- Model semantik BAB 1 hingga BAB 5
- Aturan keterlacakan antar komponen penelitian
- Peran semantik setiap unit konten KTI
- Aturan fidelitas sumber (AI tidak boleh mengarang data)
- Variasi struktur yang didukung
- Contoh KTI kerja yang konkret

---

## 3. Research Report Conceptual Flow

KTI adalah narasi penelitian yang bergerak dari **pertanyaan** menuju **jawaban** secara sistematis:

```
RESEARCH PROBLEM
        ↓
  "Mengapa penelitian ini diperlukan?"
  (Latar Belakang, Identifikasi Masalah)
        ↓
RESEARCH QUESTION + OBJECTIVE
        ↓
  "Apa yang hendak dijawab dan dicapai?"
  (Rumusan Masalah, Tujuan Penelitian)
        ↓
SCIENTIFIC FOUNDATION
        ↓
  "Pengetahuan apa yang mendukung penelitian ini?"
  (Landasan Teori, Penelitian Terdahulu)
        ↓
RESEARCH METHOD
        ↓
  "Bagaimana penelitian dilakukan?"
  (Desain, Instrumen, Prosedur, Analisis)
        ↓
DATA & RESULTS
        ↓
  "Apa yang ditemukan?"
  (Hasil pengukuran, observasi, survei)
        ↓
INTERPRETATION & DISCUSSION
        ↓
  "Apa artinya temuan ini?"
  (Analisis, hubungan dengan teori, perbandingan)
        ↓
CONCLUSION & RECOMMENDATION
        ↓
  "Apa jawaban akhirnya dan apa yang harus dilakukan selanjutnya?"
```

Alur ini tidak boleh dibalik, dilewati secara sewenang-wenang, atau disederhanakan menjadi ringkasan kronologis.

---

## 4. Canonical BAB 1–5 Structure

```
KTI / RESEARCH REPORT
│
├── BAB 1 — PENDAHULUAN
│   │ [MENGAPA penelitian ini diperlukan?]
│   │
│   ├── Latar Belakang                  [CORE]
│   ├── Identifikasi / Fokus Masalah    [OPTIONAL]
│   ├── Rumusan Masalah                 [CORE]
│   ├── Tujuan Penelitian               [CORE]
│   ├── Manfaat Penelitian              [CORE]
│   └── Hipotesis                       [METHOD-DEPENDENT]
│
├── BAB 2 — TINJAUAN PUSTAKA
│   │ [PENGETAHUAN APA yang mendukung penelitian ini?]
│   │
│   ├── Landasan Teori                  [CORE]
│   ├── Konsep / Variabel Utama         [CORE]
│   ├── Penelitian Terdahulu            [CORE]
│   ├── Research Gap / Posisi Penelitian [CORE]
│   └── Kerangka Berpikir               [OPTIONAL]
│
├── BAB 3 — METODOLOGI PENELITIAN
│   │ [BAGAIMANA penelitian dilakukan?]
│   │
│   ├── Waktu dan Tempat                [CORE]
│   ├── Alat dan Bahan                  [METHOD-DEPENDENT: eksperimental]
│   ├── Jenis / Desain Penelitian       [CORE]
│   ├── Subjek / Objek Penelitian       [CORE]
│   ├── Instrumen / Sumber Data         [CORE]
│   ├── Prosedur Penelitian             [CORE]
│   ├── Teknik Pengumpulan Data         [CORE]
│   └── Pengolahan / Analisis Data      [CORE]
│
├── BAB 4 — HASIL DAN PEMBAHASAN
│   │ [APA yang ditemukan, dan apa artinya?]
│   │
│   ├── Penyajian Hasil                 [CORE]
│   ├── Data dan Temuan                 [CORE]
│   ├── Visualisasi Data                [OPTIONAL: tergantung ketersediaan]
│   ├── Analisis                        [CORE]
│   ├── Interpretasi                    [CORE]
│   ├── Pembahasan                      [CORE]
│   ├── Hubungan dengan Teori           [CORE]
│   ├── Perbandingan dengan Penelitian Terdahulu [OPTIONAL]
│   └── Evaluasi Hipotesis              [METHOD-DEPENDENT: jika ada hipotesis]
│
└── BAB 5 — KESIMPULAN DAN SARAN
    │ [APA jawaban akhirnya?]
    │
    ├── Kesimpulan                      [CORE]
    ├── Keterbatasan Penelitian         [OPTIONAL: sebaiknya ada]
    ├── Implikasi                       [OPTIONAL]
    ├── Saran                           [CORE]
    └── Rekomendasi Penelitian Selanjutnya [OPTIONAL]
```

---

## 5. Core vs Optional Structure

### Definisi

**CORE:**  
Komponen yang wajib ada dalam dokumen KTI yang valid. Ketidakhadiran komponen CORE menandakan dokumen yang tidak lengkap secara penelitian.

**OPTIONAL:**  
Komponen yang memperkuat dokumen namun tidak selalu hadir. Bergantung pada keputusan penulis atau kebijakan lembaga.

**METHOD-DEPENDENT:**  
Komponen yang hanya relevan untuk desain penelitian tertentu. Kehadiran atau ketidakhadirannya bergantung pada pendekatan penelitian yang digunakan.

### Tabel Klasifikasi Komponen

| Komponen | Klasifikasi | Catatan |
|---|---|---|
| Latar Belakang | CORE | Fondasi mengapa penelitian dilakukan |
| Identifikasi Masalah | OPTIONAL | Bisa diintegrasikan dalam Latar Belakang |
| Rumusan Masalah | CORE | Harus eksplisit dan terfokus |
| Tujuan Penelitian | CORE | Menjawab Rumusan Masalah secara spesifik |
| Manfaat Penelitian | CORE | Minimal disebutkan |
| Hipotesis | METHOD-DEPENDENT | Hanya untuk penelitian kuantitatif/eksperimental |
| Landasan Teori | CORE | Minimal ada satu konsep teoritis |
| Penelitian Terdahulu | CORE | Minimum 1 penelitian rujukan |
| Research Gap | CORE | Dapat diintegrasikan dalam Tinjauan Pustaka |
| Kerangka Berpikir | OPTIONAL | Bagan konseptual alur pemikiran |
| Waktu dan Tempat | CORE | Konteks penelitian |
| Alat dan Bahan | METHOD-DEPENDENT | Lebih menonjol dalam penelitian eksperimental |
| Desain Penelitian | CORE | Wajib ada |
| Subjek / Objek | CORE | Bergantung jenis penelitian |
| Instrumen | CORE | Bergantung pada teknik pengumpulan data |
| Prosedur Penelitian | CORE | Urutan langkah penelitian |
| Teknik Pengumpulan Data | CORE | Wajib dijelaskan |
| Analisis Data | CORE | Wajib dijelaskan |
| Penyajian Hasil | CORE | Data dan temuan utama |
| Visualisasi Data | OPTIONAL | Jika ada data kuantitatif yang layak divisualisasikan |
| Analisis | CORE | Pengolahan sistematis dari hasil |
| Interpretasi | CORE | Makna dari temuan |
| Pembahasan | CORE | Penjelasan dan kaitan dengan konteks |
| Hubungan dengan Teori | CORE | Menghubungkan temuan ke landasan teori |
| Perbandingan dengan Penelitian Lain | OPTIONAL | Memperkuat validitas |
| Evaluasi Hipotesis | METHOD-DEPENDENT | Hanya jika ada hipotesis |
| Kesimpulan | CORE | Wajib, menjawab rumusan masalah |
| Keterbatasan Penelitian | OPTIONAL | Sebaiknya ada |
| Implikasi | OPTIONAL | Jika ada signifikansi teoritis/praktis |
| Saran | CORE | Minimal ada |
| Rekomendasi Penelitian Selanjutnya | OPTIONAL | Memperkuat kontribusi |

---

## 6. BAB 1 Semantic Model

**Fungsi:** Membangun konteks dan justifikasi mengapa penelitian ini harus dilakukan.

### 6.1 Latar Belakang

**Peran semantik:** `RESEARCH_PROBLEM`

**Tujuan:** Menjelaskan kondisi/fenomena yang menjadi keprihatinan, gap yang ada, dan mengapa hal ini perlu diteliti.

**Source signals (penanda dalam teks sumber):**
- Kalimat yang mendeskripsikan masalah atau kondisi yang tidak ideal
- Data statistik pendukung urgensi masalah
- Narasi perkembangan fenomena yang relevan
- Pernyataan yang mengindikasikan perlunya solusi

**Expected relationships:**
- → Mengarah ke `RESEARCH_QUESTION`
- → Didukung oleh data/fenomena dari `DATA` / `EXAMPLE`

**Common confusions:**
- Latar Belakang bukan ringkasan tulisan — ini adalah argumentasi perlunya penelitian
- Bukan daftar fakta tanpa narasi yang menghubungkan ke masalah

### 6.2 Rumusan Masalah

**Peran semantik:** `RESEARCH_QUESTION`

**Tujuan:** Mengekspresikan pertanyaan penelitian secara eksplisit dan terukur.

**Source signals:**
- Kalimat tanya yang spesifik
- "Bagaimana...", "Apakah...", "Seberapa besar...", "Apa pengaruh..."
- Daftar bernomor yang merumuskan pertanyaan

**Expected relationships:**
- ← Berasal dari `RESEARCH_PROBLEM`
- → Harus dijawab oleh `CONCLUSION`

**Common confusions:**
- Rumusan masalah bukan pernyataan — harus berupa pertanyaan
- Bukan terlalu umum ("Bagaimana cara meningkatkan kualitas pendidikan?")
- Harus spesifik dan dapat dijawab oleh penelitian

### 6.3 Tujuan Penelitian

**Peran semantik:** `RESEARCH_OBJECTIVE`

**Tujuan:** Menyatakan apa yang hendak dicapai, biasanya sejajar dengan Rumusan Masalah dalam bentuk deklaratif.

**Expected relationships:**
- ← Sejajar dengan `RESEARCH_QUESTION` (versi deklaratif)
- → Harus tercermin dalam `CONCLUSION`

### 6.4 Manfaat Penelitian

**Peran semantik:** `RESEARCH_BENEFIT`

**Tujuan:** Menyatakan kontribusi penelitian bagi berbagai pihak.

### 6.5 Hipotesis (Method-Dependent)

**Peran semantik:** `HYPOTHESIS`

**Tujuan:** Jawaban sementara yang akan diuji dalam penelitian.

**Expected relationships:**
- → Diuji melalui `RESEARCH_METHOD` dan data
- → Dievaluasi dalam `HYPOTHESIS_EVALUATION` di BAB 4

---

## 7. BAB 2 Semantic Model

**Fungsi:** Menyediakan fondasi ilmiah yang mendukung penelitian dan memposisikan penelitian ini di antara penelitian-penelitian yang ada.

### 7.1 Landasan Teori

**Peran semantik:** `THEORETICAL_FOUNDATION`

**Tujuan:** Mendefinisikan konsep, teori, dan prinsip ilmiah yang relevan.

**Source signals:**
- Definisi konsep dari sumber ilmiah
- Penjelasan teori dengan atribusi
- Prinsip atau hukum ilmiah yang relevan

**Expected relationships:**
- → Mendukung `RESEARCH_METHOD` (memvalidasi pendekatan)
- → Menjadi rujukan dalam `THEORY_CONNECTION` di BAB 4

**Common confusions:**
- Bukan kamus — fokus pada teori yang relevan dengan penelitian
- Bukan sekadar kutipan panjang tanpa sintesis

### 7.2 Penelitian Terdahulu

**Peran semantik:** `PRIOR_RESEARCH`

**Tujuan:** Menunjukkan posisi penelitian ini dalam konteks penelitian yang telah ada.

**Expected relationships:**
- → Mengarah ke `RESEARCH_GAP`
- → Menjadi referensi dalam `PRIOR_RESEARCH_COMPARISON` di BAB 4

### 7.3 Research Gap / Posisi Penelitian

**Peran semantik:** `RESEARCH_GAP`

**Tujuan:** Mengidentifikasi apa yang belum dijawab oleh penelitian sebelumnya dan mengapa penelitian ini dibutuhkan.

**Expected relationships:**
- ← Berasal dari `PRIOR_RESEARCH`
- → Memvalidasi urgensi `RESEARCH_PROBLEM`

---

## 8. BAB 3 Semantic Model

**Fungsi:** Mendeskripsikan secara transparan dan terperinci bagaimana penelitian dilakukan sehingga dapat direplikasi.

### 8.1 Desain / Jenis Penelitian

**Peran semantik:** `RESEARCH_METHOD`

**Tujuan:** Menyatakan pendekatan penelitian (kuantitatif/kualitatif/campuran, eksperimental/survei/studi kasus, dll).

**Expected relationships:**
- → Menentukan relevansi `HYPOTHESIS`, `RESEARCH_INSTRUMENT`
- → Menentukan jenis `DATA` yang akan dikumpulkan

### 8.2 Instrumen / Sumber Data

**Peran semantik:** `RESEARCH_INSTRUMENT`

**Tujuan:** Mendeskripsikan alat pengumpulan data (kuesioner, wawancara, observasi, dll).

### 8.3 Teknik Pengumpulan Data

**Peran semantik:** `DATA_COLLECTION`

**Tujuan:** Menjelaskan prosedur pengumpulan data secara operasional.

### 8.4 Teknik Analisis Data

**Peran semantik:** `DATA_ANALYSIS_METHOD`

**Tujuan:** Menjelaskan cara data diolah dan dianalisis.

**Expected relationships:**
- → Diimplementasikan dalam BAB 4 (`ANALYSIS`)

---

## 9. BAB 4 Results and Discussion Model

**Fungsi:** Menyajikan temuan secara objektif, kemudian menginterpretasikan maknanya dalam konteks teori dan penelitian yang ada.

> **⚠️ Prinsip Kritis: DATA ≠ INTERPRETASI**
>
> Sistem tidak boleh mencampurkan "apa yang ditemukan" dengan "apa artinya temuan ini."
> Ini adalah dua lapisan makna yang berbeda dan harus dipertahankan sebagai unit terpisah.

### 9.1 Hierarki Semantik BAB 4

Alur naratif yang valid dalam BAB 4:

```
DATA / OBSERVATION
        ↓
RESEARCH_RESULT
(Apa yang terukur, terobservasi, dihasilkan?)
        ↓
FINDING
(Apa temuan spesifik yang dapat disimpulkan dari data?)
        ↓
ANALYSIS
(Bagaimana data diolah secara sistematis?)
        ↓
INTERPRETATION
(Apa artinya temuan ini dalam konteks penelitian?)
        ↓
DISCUSSION
(Mengapa ini terjadi? Apakah sesuai dengan yang diharapkan?)
        ↓
THEORY_CONNECTION
(Bagaimana temuan ini berhubungan dengan landasan teori?)
        ↓
PRIOR_RESEARCH_COMPARISON
(Apakah temuan ini selaras atau bertentangan dengan penelitian sebelumnya?)
        ↓
HYPOTHESIS_EVALUATION [jika ada]
(Apakah hipotesis terbukti, ditolak, atau perlu dimodifikasi?)
```

### 9.2 Definisi Peran Semantik BAB 4

#### RESEARCH_RESULT

**Tujuan:** Penyajian output dari proses penelitian — apa yang secara faktual diukur, diobservasi, dihasilkan, atau dikumpulkan.

**Sifat:** Faktual, netral, tidak interpretatif.

**Contoh representasi:**
- Nilai rata-rata hasil pengukuran
- Persentase responden yang memilih opsi tertentu
- Tabel hasil observasi lapangan
- Output sistem/prototipe
- Transkrip atau rekaman data

**Aturan:**
- AI **tidak boleh menambahkan** nilai atau fakta yang tidak ada dalam source material
- Jika data menggunakan tabel, keterangan tabel harus akurat

#### FINDING

**Tujuan:** Kesimpulan spesifik yang dapat ditarik dari satu atau lebih `RESEARCH_RESULT`.

**Sifat:** Masih dekat dengan data, namun sudah merupakan pernyataan bermakna.

**Contoh:**
- "Mayoritas responden (78%) menyatakan bahwa..."
- "Hasil pengujian menunjukkan peningkatan efisiensi sebesar 23%"
- "Pada kondisi X, terjadi fenomena Y"

**Expected relationships:**
- ← Berasal dari satu atau lebih `RESEARCH_RESULT` atau `DATA`
- → Diinterpretasikan oleh `INTERPRETATION`
- → Menjadi dasar `CONCLUSION`

#### ANALYSIS

**Tujuan:** Pengolahan sistematis terhadap data menggunakan metode yang didefinisikan di BAB 3.

**Sifat:** Metodologis, mengikuti `DATA_ANALYSIS_METHOD`.

**Common confusions:**
- Bukan sekadar deskripsi ulang data
- Bukan interpretasi tentang makna — itu tugas `INTERPRETATION`

#### INTERPRETATION

**Tujuan:** Penjelasan tentang *apa arti* temuan dalam konteks penelitian.

**Sifat:** Inferensial, berdasarkan bukti, tidak spekulatif.

**Contoh:**
- "Hal ini menunjukkan bahwa hipotesis peneliti terbukti sebagian"
- "Tingginya angka tersebut mengindikasikan adanya kebutuhan yang belum terpenuhi"

**Aturan:**
- Setiap INTERPRETATION harus merujuk pada `FINDING` atau `ANALYSIS` yang menjadi dasarnya
- AI tidak boleh membuat interpretasi yang tidak didukung data dalam source material

#### DISCUSSION

**Tujuan:** Penjelasan lebih luas tentang *mengapa* hasil ini terjadi, termasuk kaitannya dengan konteks yang lebih besar.

**Cakupan:**
- Penjelasan mekanisme mengapa hasil ini muncul
- Perbandingan dengan ekspektasi awal
- Diskusi tentang faktor-faktor yang mempengaruhi hasil
- Implikasi dari hasil yang ditemukan

#### THEORY_CONNECTION

**Tujuan:** Mengaitkan temuan atau interpretasi secara eksplisit dengan teori atau konsep yang didefinisikan di BAB 2.

**Expected relationships:**
- ← Merujuk ke `THEORETICAL_FOUNDATION` dari BAB 2
- ← Merujuk ke `FINDING` atau `INTERPRETATION` yang spesifik

**Aturan:**
- Harus mengidentifikasi TEMUAN atau INTERPRETASI mana yang dikaitkan dengan teori mana

#### PRIOR_RESEARCH_COMPARISON

**Tujuan:** Membandingkan temuan penelitian ini dengan hasil penelitian terdahulu.

**Expected relationships:**
- ← Merujuk ke `PRIOR_RESEARCH` dari BAB 2
- ← Merujuk ke `FINDING` yang spesifik

**Contoh:**
- "Temuan ini konsisten dengan penelitian X yang menyatakan bahwa..."
- "Berbeda dengan penelitian Y, penelitian ini menemukan bahwa..."

#### HYPOTHESIS_EVALUATION (Method-Dependent)

**Tujuan:** Mengevaluasi hipotesis berdasarkan temuan yang diperoleh.

**Keputusan yang valid:**
- Hipotesis diterima (terbukti)
- Hipotesis ditolak (tidak terbukti)
- Hipotesis diterima sebagian

**Aturan:**
- Hanya ada jika `HYPOTHESIS` ada di BAB 1
- Evaluasi harus didasarkan pada `FINDING` dan `ANALYSIS`, bukan opini

### 9.3 VISUALIZATION_CANDIDATE

**Tujuan:** Menandai unit konten yang memiliki potensi untuk direpresentasikan secara visual.

**Tipe visualisasi yang relevan untuk penelitian:**

| Tipe | Kegunaan | Contoh Konten Sumber |
|---|---|---|
| `TREND` | Menampilkan perubahan dari waktu ke waktu | Data longitudinal, perkembangan skor |
| `COMPARISON` | Membandingkan dua atau lebih kondisi | Pre-test vs post-test, kelompok kontrol vs eksperimen |
| `DISTRIBUTION` | Menampilkan sebaran data | Distribusi skor responden, frekuensi jawaban |
| `RELATIONSHIP` | Menampilkan korelasi antar variabel | Scatter plot, korelasi |
| `COMPOSITION` | Menampilkan proporsi dari keseluruhan | Komposisi responden berdasarkan kategori |
| `PROCESS` | Menampilkan urutan langkah | Prosedur eksperimen, alur sistem |
| `EVIDENCE` | Menampilkan bukti empiris | Foto dokumentasi, screenshot hasil |
| `MEASUREMENT` | Menampilkan nilai pengukuran | Tabel hasil pengujian |

**Aturan:**
- Visualisasi harus berdasarkan data yang ada dalam source material
- Sistem tidak boleh menarik angka atau fakta yang tidak tersedia dalam teks sumber
- `VISUALIZATION_CANDIDATE` tidak mendefinisikan desain visual — hanya mengidentifikasi tipe dan data yang akan direpresentasikan

---

## 10. BAB 5 Conclusion and Recommendation Model

**Fungsi:** Memberikan sintesis akhir yang menjawab pertanyaan penelitian dan memberikan arah masa depan.

### 10.1 Kesimpulan

**Peran semantik:** `CONCLUSION`

**Tujuan:** Sintesis langsung yang menjawab rumusan masalah dan tujuan penelitian.

**Sifat:** Padat, langsung, berdasarkan temuan.

**Kesimpulan BUKAN:**
- Pengulangan seluruh diskusi BAB 4
- Ringkasan kronologis proses penelitian
- Tempat untuk memperkenalkan temuan baru
- Sekadar restatement data

**Kesimpulan ADALAH:**
- Jawaban atas `RESEARCH_QUESTION`
- Pencapaian terhadap `RESEARCH_OBJECTIVE`
- Sintesis dari `FINDING` yang paling signifikan

**Aturan traceability:**
- Setiap poin kesimpulan harus dapat dilacak ke minimal satu `FINDING` atau `INTERPRETATION` di BAB 4

### 10.2 Keterbatasan Penelitian

**Peran semantik:** `LIMITATION`

**Tujuan:** Mengakui batasan penelitian yang dapat mempengaruhi validitas atau generalisabilitas temuan.

**Tipe keterbatasan yang umum:**
- Keterbatasan instrumen pengukuran
- Keterbatasan sampel (ukuran, representativitas)
- Keterbatasan waktu penelitian
- Keterbatasan kondisi lingkungan
- Keterbatasan akses data
- Keterbatasan sumber daya

**Aturan:**
- Tidak boleh meremehkan signifikansi penelitian secara berlebihan
- Harus jujur dan spesifik, bukan generik

### 10.3 Saran dan Rekomendasi

**Peran semantik:** `RECOMMENDATION`

**Tujuan:** Memberikan saran yang actionable berdasarkan temuan dan keterbatasan.

**Saran HARUS:**
- Spesifik dan dapat dilaksanakan
- Relevan dengan temuan atau keterbatasan penelitian
- Ditujukan kepada pihak yang dapat bertindak

**Saran TIDAK BOLEH:**
- Generik tanpa kaitan dengan temuan (contoh: "Penelitian selanjutnya harus lebih baik")
- Berdasarkan informasi yang tidak ada dalam penelitian

**Expected relationships:**

```
RECOMMENDATION
    ↓ based_on (minimal salah satu dari)
FINDING / LIMITATION / IMPLICATION
```

**Target penerima saran:**
- Praktisi / pengguna langsung
- Institusi / lembaga
- Peneliti masa depan
- Pembuat kebijakan

### 10.4 FUTURE_WORK (Rekomendasi Penelitian Selanjutnya)

**Peran semantik:** `FUTURE_WORK`

**Tujuan:** Mengarahkan penelitian masa depan berdasarkan `RESEARCH_GAP` yang belum terjawab atau `LIMITATION` yang ditemukan.

**Sifat:** Spesifik, berbasis gap yang teridentifikasi.

---

## 11. Research Traceability Graph

Keterlacakan penelitian adalah kemampuan untuk menelusuri hubungan dari satu komponen ke komponen lain dalam alur penelitian.

### 11.1 Graf Keterlacakan Kanonik

```
RESEARCH_PROBLEM
        │
        ├──→ RESEARCH_QUESTION ──→ CONCLUSION (harus dijawab)
        │
        └──→ RESEARCH_OBJECTIVE ──→ CONCLUSION (harus tercapai)

THEORETICAL_FOUNDATION
        │
        ├──→ Mendukung RESEARCH_METHOD
        │
        └──→ Dirujuk oleh THEORY_CONNECTION (BAB 4)

PRIOR_RESEARCH
        │
        ├──→ Diidentifikasi RESEARCH_GAP
        │
        └──→ Dirujuk oleh PRIOR_RESEARCH_COMPARISON (BAB 4)

HYPOTHESIS [jika ada]
        │
        └──→ Dievaluasi oleh HYPOTHESIS_EVALUATION (BAB 4)

RESEARCH_METHOD + RESEARCH_INSTRUMENT + DATA_COLLECTION
        │
        └──→ Menghasilkan DATA / RESEARCH_RESULT

DATA / RESEARCH_RESULT
        │
        └──→ FINDING

FINDING
        │
        ├──→ INTERPRETATION
        │
        └──→ CONCLUSION (sintesis dari finding signifikan)

INTERPRETATION
        │
        ├──→ DISCUSSION
        │
        └──→ THEORY_CONNECTION

DISCUSSION + THEORY_CONNECTION
        │
        └──→ memperkuat atau mempertanyakan THEORETICAL_FOUNDATION

CONCLUSION
        │
        └──→ RECOMMENDATION

LIMITATION
        │
        └──→ RECOMMENDATION / FUTURE_WORK
```

### 11.2 Aturan Keterlacakan

| Relasi | Status | Penjelasan |
|---|---|---|
| `RESEARCH_QUESTION` → `CONCLUSION` | REQUIRED | Setiap rumusan masalah harus dijawab |
| `RESEARCH_OBJECTIVE` → `CONCLUSION` | REQUIRED | Setiap tujuan harus tercermin di simpulan |
| `FINDING` → `CONCLUSION` | REQUIRED | Simpulan harus berbasis temuan |
| `FINDING` → `INTERPRETATION` | REQUIRED | Setiap temuan harus diinterpretasikan |
| `INTERPRETATION` → `FINDING` | REQUIRED | Interpretasi harus merujuk temuan konkret |
| `HYPOTHESIS` → `HYPOTHESIS_EVALUATION` | METHOD-DEPENDENT | Hanya jika hipotesis ada |
| `THEORY_CONNECTION` → `FINDING/INTERPRETATION` | REQUIRED | Kaitan teori harus spesifik |
| `RECOMMENDATION` → `FINDING/LIMITATION` | REQUIRED | Saran harus berbasis bukti |
| `PRIOR_RESEARCH_COMPARISON` → `PRIOR_RESEARCH` | OPTIONAL | Perbandingan diperkuat dengan referensi |

---

## 12. Research Semantic Roles

Tabel referensi lengkap semua peran semantik dalam KTI:

| Role | ContentType | Typical BAB | Purpose |
|---|---|---|---|
| `RESEARCH_PROBLEM` | `research_problem` | BAB 1 | Permasalahan yang mendorong penelitian |
| `RESEARCH_QUESTION` | `research_question` | BAB 1 | Pertanyaan spesifik yang hendak dijawab |
| `RESEARCH_OBJECTIVE` | `research_objective` | BAB 1 | Tujuan yang hendak dicapai |
| `RESEARCH_BENEFIT` | `research_benefit` | BAB 1 | Manfaat penelitian bagi stakeholder |
| `HYPOTHESIS` | `hypothesis` | BAB 1 | Jawaban sementara yang diuji |
| `THEORETICAL_FOUNDATION` | `theoretical_foundation` | BAB 2 | Landasan konseptual dan teoritis |
| `PRIOR_RESEARCH` | `prior_research` | BAB 2 | Penelitian yang telah dilakukan sebelumnya |
| `RESEARCH_GAP` | `research_gap` | BAB 2 | Gap yang belum terjawab |
| `RESEARCH_METHOD` | `research_method` | BAB 3 | Desain dan pendekatan penelitian |
| `RESEARCH_INSTRUMENT` | `research_instrument` | BAB 3 | Alat pengumpulan data |
| `DATA_COLLECTION` | `data_collection` | BAB 3 | Teknik mengumpulkan data |
| `DATA_ANALYSIS_METHOD` | `data_analysis_method` | BAB 3 | Teknik analisis data |
| `RESEARCH_RESULT` | `research_result` | BAB 4 | Hasil objektif dari penelitian |
| `FINDING` | `finding` | BAB 4 | Temuan spesifik yang dapat dikutip |
| `ANALYSIS` | `analysis` | BAB 4 | Pengolahan sistematis data |
| `INTERPRETATION` | `interpretation` | BAB 4 | Makna dari temuan |
| `DISCUSSION` | `discussion` | BAB 4 | Penjelasan, kaitan konteks |
| `THEORY_CONNECTION` | `theory_connection` | BAB 4 | Kaitan dengan landasan teori |
| `PRIOR_RESEARCH_COMPARISON` | `prior_research_comparison` | BAB 4 | Perbandingan dengan penelitian lain |
| `HYPOTHESIS_EVALUATION` | `hypothesis_evaluation` | BAB 4 | Evaluasi hipotesis berdasarkan data |
| `VISUALIZATION_CANDIDATE` | `visualization_candidate` | BAB 4 | Kandidat representasi data visual |
| `CONCLUSION` | `conclusion` | BAB 5 | Sintesis menjawab rumusan masalah |
| `LIMITATION` | `limitation` | BAB 5 | Keterbatasan penelitian |
| `IMPLICATION` | `implication` | BAB 5 | Implikasi teoritis atau praktis |
| `RECOMMENDATION` | `recommendation` | BAB 5 | Saran berbasis temuan |
| `FUTURE_WORK` | `future_work` | BAB 5 | Arah penelitian selanjutnya |

---

## 13. Relationship Rules

### 13.1 Aturan Lintas BAB

```
BAB 2 ────────────────────→ BAB 4
THEORETICAL_FOUNDATION     THEORY_CONNECTION
PRIOR_RESEARCH         →   PRIOR_RESEARCH_COMPARISON

BAB 1 ────────────────────→ BAB 5
RESEARCH_QUESTION      →   CONCLUSION (must be answered)
RESEARCH_OBJECTIVE     →   CONCLUSION (must be achieved)
HYPOTHESIS             →   HYPOTHESIS_EVALUATION (BAB 4 → BAB 5)

BAB 3 ────────────────────→ BAB 4
DATA_ANALYSIS_METHOD   →   ANALYSIS
DATA_COLLECTION        →   RESEARCH_RESULT
```

### 13.2 Aturan Keintegritas

1. Interpretasi tidak boleh muncul tanpa ada finding atau data yang mendukungnya
2. Kesimpulan tidak boleh memperkenalkan fakta baru yang tidak ada di BAB 4
3. Saran harus dapat dihubungkan ke minimal satu komponen yang mendahuluinya
4. Teori yang dirujuk di BAB 4 harus sudah didefinisikan di BAB 2
5. Penelitian terdahulu yang dibandingkan di BAB 4 harus sudah disebutkan di BAB 2

---

## 14. Source Fidelity Rules

Ini adalah aturan yang paling kritis untuk sistem AI yang memproses KTI.

### 14.1 Prinsip Utama

> **AI tidak boleh mengarang, menginterpolasi, atau mengekstrapolasi data yang tidak tersedia dalam source material.**

### 14.2 Aturan Per Peran

| Peran | Aturan Fidelitas |
|---|---|
| `RESEARCH_RESULT` | Hanya nilai/fakta yang tertera dalam source material |
| `FINDING` | Harus dapat diturunkan langsung dari RESEARCH_RESULT yang ada |
| `INTERPRETATION` | Boleh inferensial, namun harus berdasarkan FINDING yang ada |
| `CONCLUSION` | Hanya sintesis dari FINDING yang ada, tidak boleh menambah fakta baru |
| `RECOMMENDATION` | Boleh forward-looking, namun harus berbasis temuan atau keterbatasan yang ada |
| `THEORETICAL_FOUNDATION` | Definisi teori harus dari source, bukan dari pengetahuan AI sendiri |
| `PRIOR_RESEARCH` | Penelitian yang disebutkan harus dari source, bukan yang diketahui AI |
| `VISUALIZATION_CANDIDATE` | Data yang divisualisasikan harus ada dalam source |

### 14.3 Apa yang BOLEH Dilakukan AI

- Merestrukturisasi teks agar lebih jelas secara visual
- Mengelompokkan unit informasi yang secara semantik terkait
- Mengidentifikasi peran semantik dari setiap unit
- Menyarankan tipe visualisasi yang sesuai
- Memeriksa konsistensi dan kelengkapan alur penelitian

### 14.4 Apa yang TIDAK BOLEH Dilakukan AI

- Menambahkan data atau angka yang tidak ada dalam source
- Membuat interpretasi yang melompat melampaui data yang tersedia
- Mengarang penelitian terdahulu atau teori yang tidak disebutkan
- Menyederhanakan nuansa penelitian demi visualisasi yang lebih menarik
- Mengubah kesimpulan penelitian

---

## 15. Structural Variation

KTI hadir dalam berbagai format. Sistem harus fleksibel namun tetap menghormati alur inti.

### 15.1 Variasi yang Didukung

| Format | Karakteristik | Penyesuaian |
|---|---|---|
| KTI Sekolah (SMP/SMA) | Struktur BAB 1–5 sederhana, hipotesis mungkin ada | Prioritas pada BAB 1, 3, 4, 5 |
| Skripsi / Tugas Akhir | Struktur lengkap, BAB 2 komprehensif | Semua BAB diharapkan hadir |
| Makalah Ilmiah | Mungkin tidak berstruktur BAB-BAB, lebih padat | Pemetaan ke peran semantik, bukan BAB |
| Laporan Penelitian | Formal, bisa ada bab tambahan | Fleksibel dalam penambahan |
| Paper / Artikel Jurnal | Abstract, Introduction, Methods, Results, Discussion, Conclusion | Mapped ke BAB 1→5 secara konseptual |

### 15.2 Pemetaan Format Non-BAB ke Peran Semantik

Jika source material tidak menggunakan struktur BAB eksplisit:

```
Introduction / Abstract     → RESEARCH_PROBLEM + RESEARCH_QUESTION + RESEARCH_OBJECTIVE
Literature Review           → THEORETICAL_FOUNDATION + PRIOR_RESEARCH
Methods / Methodology       → RESEARCH_METHOD + DATA_COLLECTION + DATA_ANALYSIS_METHOD
Results                     → RESEARCH_RESULT + FINDING
Discussion                  → ANALYSIS + INTERPRETATION + THEORY_CONNECTION
Conclusion                  → CONCLUSION + RECOMMENDATION
```

### 15.3 Variasi yang Tidak Didukung

Sistem tidak mendukung dokumen yang:
- Tidak memiliki komponen RESEARCH_PROBLEM (tidak ada konteks penelitian)
- Tidak memiliki FINDING apapun (tidak ada hasil penelitian)
- Tidak memiliki CONCLUSION (narasi terbuka tanpa sintesis)

Dalam kasus ini, sistem dapat tetap menghasilkan dokumen namun wajib memunculkan `traceability_warnings` yang relevan.

---

## 16. Edge Cases

### 16.1 BAB 4 Tanpa Pemisahan Jelas Antara Hasil dan Pembahasan

Beberapa KTI menyatukan "Hasil" dan "Pembahasan" tanpa pemisahan eksplisit.

**Penanganan:**
- Identifikasi unit-unit konten secara semantik
- Pisahkan `RESEARCH_RESULT` / `FINDING` dari `INTERPRETATION` / `DISCUSSION`
- Bahkan jika dalam satu paragraf, keduanya mungkin ada

### 16.2 Hipotesis yang Tidak Dievaluasi

Source material memiliki hipotesis di BAB 1 tetapi tidak ada evaluasi eksplisit di BAB 4.

**Penanganan:**
- Tambahkan `HYPOTHESIS_WITHOUT_EVALUATION` ke `traceability_warnings`
- Jangan membuat evaluasi hipotesis yang tidak ada dalam sumber

### 16.3 Data Tanpa Interpretasi

Source material memiliki tabel atau angka tetapi tidak ada penjelasan makna.

**Penanganan:**
- Tandai sebagai `RESEARCH_RESULT` atau `DATA`
- Tambahkan `DATA_WITHOUT_FINDING` ke `traceability_warnings`
- Jangan mengarang interpretasi

### 16.4 Kesimpulan yang Tidak Menjawab Rumusan Masalah

**Penanganan:**
- Tandai sebagai warning `CONCLUSION_WITHOUT_OBJECTIVE_TRACE`
- Tetap visualisasikan konten yang ada
- Jangan membuat simpulan baru untuk "melengkapi"

### 16.5 Source Material Berupa BAB 4–5 Saja

User menyerahkan hanya bagian akhir penelitian tanpa BAB 1–3.

**Penanganan:**
- `detected_bab_coverage` hanya mencantumkan BAB yang terdeteksi
- `missing_critical_components` mencantumkan komponen yang tidak ada
- Pipeline tetap berjalan dengan peringatan, tidak gagal total

---

## 17. Worked Example

Contoh berikut menunjukkan pemetaan alur penelitian konkret ke peran semantik:

---

**Judul Penelitian:**  
*"Pengaruh Penggunaan Media Pembelajaran Berbasis Video terhadap Motivasi Belajar Siswa Kelas VIII di SMPN 1 Bontang"*

---

**TAHAP 1 — BAB 1 (Identifikasi Elemen)**

```
Teks sumber:
"Rendahnya motivasi belajar siswa menjadi permasalahan yang banyak dihadapi
guru di era digital. Data survei 2024 menunjukkan 62% siswa merasa bosan
dengan metode pembelajaran konvensional..."

→ ContentType: RESEARCH_PROBLEM
→ Signals: fenomena masalah, data pendukung urgensi
```

```
Teks sumber:
"Apakah penggunaan media pembelajaran berbasis video berpengaruh secara
signifikan terhadap motivasi belajar siswa kelas VIII?"

→ ContentType: RESEARCH_QUESTION
→ Must trace to: CONCLUSION
```

```
Teks sumber:
"Hipotesis penelitian: Terdapat pengaruh yang signifikan antara penggunaan
media pembelajaran berbasis video terhadap motivasi belajar siswa."

→ ContentType: HYPOTHESIS
→ Must be evaluated in: BAB 4 HYPOTHESIS_EVALUATION
```

---

**TAHAP 2 — BAB 4 (Identifikasi Elemen)**

```
Teks sumber:
"Hasil pre-test menunjukkan rata-rata skor motivasi 62.4,
sedangkan post-test menunjukkan rata-rata 78.7."

→ ContentType: RESEARCH_RESULT
→ Potential: VISUALIZATION_CANDIDATE (tipe: COMPARISON)
```

```
Teks sumber:
"Terdapat peningkatan skor motivasi sebesar 16.3 poin (26.1%)
setelah penerapan media berbasis video."

→ ContentType: FINDING
→ Based on: RESEARCH_RESULT di atas
```

```
Teks sumber:
"Peningkatan ini sejalan dengan teori motivasi Keller (ARCS Model) yang
menyatakan bahwa unsur Attention dan Relevance dalam media berdampak
positif pada keterlibatan siswa."

→ ContentType: THEORY_CONNECTION
→ References: THEORETICAL_FOUNDATION (Keller ARCS Model dari BAB 2)
→ References: FINDING (peningkatan 26.1%)
```

```
Teks sumber:
"Dengan nilai t-hitung 4.23 > t-tabel 1.68 pada α=0.05, hipotesis
penelitian diterima."

→ ContentType: HYPOTHESIS_EVALUATION
→ References: HYPOTHESIS dari BAB 1
→ References: RESEARCH_RESULT (data uji statistik)
```

---

**TAHAP 3 — BAB 5 (Identifikasi Elemen)**

```
Teks sumber:
"Penggunaan media pembelajaran berbasis video berpengaruh secara signifikan
terhadap motivasi belajar siswa kelas VIII SMPN 1 Bontang, terbukti dari
peningkatan rata-rata skor motivasi dari 62.4 menjadi 78.7."

→ ContentType: CONCLUSION
→ Traces to: RESEARCH_QUESTION ✓
→ Based on: FINDING ✓
```

```
Teks sumber:
"Keterbatasan penelitian: Sampel hanya mencakup satu sekolah sehingga
generalisabilitas hasil perlu diverifikasi pada konteks yang lebih luas."

→ ContentType: LIMITATION
```

```
Teks sumber:
"Peneliti selanjutnya disarankan untuk memperluas penelitian ke
beberapa sekolah dengan karakteristik yang berbeda."

→ ContentType: FUTURE_WORK / RECOMMENDATION
→ Based on: LIMITATION (keterbatasan sampel)
```

---

**TAHAP 4 — ResearchTraceability Result**

```json
{
  "has_research_problem": true,
  "has_research_question": true,
  "has_research_objective": true,
  "has_hypothesis": true,
  "has_theoretical_foundation": true,
  "has_prior_research": true,
  "has_research_method": true,
  "has_results": true,
  "has_discussion": true,
  "has_conclusion": true,
  "has_recommendation": true,
  "detected_bab_coverage": ["BAB_1", "BAB_2", "BAB_3", "BAB_4", "BAB_5"],
  "missing_critical_components": [],
  "traceability_warnings": []
}
```

---

## 18. Acceptance Criteria

KTI Domain Model dianggap benar dan siap menjadi landasan implementasi jika:

- [ ] Content Intelligence agent dapat mengklasifikasikan setiap unit konten KTI ke dalam `ContentType` yang tepat dari enum yang terdefinisi
- [ ] `RESEARCH_RESULT` tidak pernah digabungkan secara otomatis dengan `INTERPRETATION` tanpa pemisahan semantik
- [ ] `ResearchTraceability` selalu dihasilkan untuk dokumen dengan `document_genre == RESEARCH_REPORT`
- [ ] Setiap `FINDING` dalam output memiliki basis data yang dapat dilacak ke source material
- [ ] Setiap `CONCLUSION` dapat dilacak ke minimal satu `RESEARCH_QUESTION` atau `RESEARCH_OBJECTIVE`
- [ ] Setiap `RECOMMENDATION` memiliki basis `FINDING`, `LIMITATION`, atau `IMPLICATION`
- [ ] Sistem memunculkan `traceability_warnings` yang tepat ketika keterlacakan terputus
- [ ] Sistem tidak mengarang data, angka, atau referensi yang tidak ada dalam source material
- [ ] Sistem mendukung KTI yang hanya berisi sebagian BAB (tanpa error fatal)
- [ ] Variasi format non-BAB (paper, artikel jurnal) dapat dipetakan ke peran semantik yang sesuai
