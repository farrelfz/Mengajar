# Analisis Karakteristik Reologi dan Viskositas Fluida Kompleks Berbasis Suspensi Pati

<!-- SYNTHETIC BENCHMARK FIXTURE: Designed to test data-heavy research structures, empirical tables, and scientific argumentation -->

## BAB I: Pendahuluan
Penelitian ini bertujuan untuk mengkarakterisasi perilaku reologi fluida non-Newtonian pengental geser (*shear-thickening*) berbasis suspensi pati jagung (*Zea mays*) dalam pelarut berair. Investigasi empiris difokuskan pada penentuan laju geser kritis ($\dot{\gamma}_c$) di mana transisi fase hidrodinamik terjadi.

## BAB II: Tinjauan Pustaka dan Landasan Teori
Menurut model reologi Ostwald-de Waele, fluida non-Newtonian mengikuti persamaan daya:
$$\tau = K \cdot \dot{\gamma}^n$$

di mana:
- $\tau$ = tegangan geser (*shear stress*, Pa)
- $K$ = indeks konsistensi aliran ($\text{Pa}\cdot\text{s}^n$)
- $\dot{\gamma}$ = laju regangan geser ($\text{s}^{-1}$)
- $n$ = indeks perilaku aliran ($n > 1$ untuk fluida *shear-thickening*)

Teori klaster hidrodinamik memprediksi bahwa pada laju geser tinggi, gaya pelumasan hidrodinamik antarpartikel mengatasi gaya tolak elektrostatik, menyebabkan partikel membentuk aglomerasi sementara yang meningkatkan viskositas nyata secara tajam.

## BAB III: Metodologi Eksperimental
Eksperimen reometri dilakukan menggunakan reometer rotasional silinder konsentris (*Couette geometry*) berdiameter 25 mm pada temperatur terkontrol $25.0 \pm 0.1^\circ\text{C}$. Suspensi disiapkan dengan fraksi volume partikel ($\phi$) bervariasi antara 0.40 hingga 0.52.

## BAB IV: Hasil dan Pembahasan

### 1. Data Pengukuran Viskositas terhadap Laju Geser
Data kuantitatif respon viskositas terukur disajikan pada Tabel 1 berikut:

| Laju Geser $\dot{\gamma}$ ($\text{s}^{-1}$) | Tegangan Geser $\tau$ (Pa) | Viskositas Nyata $\eta$ ($\text{Pa}\cdot\text{s}$) | Fraksi Volume $\phi$ | Status Reologi |
| :--- | :--- | :--- | :--- | :--- |
| **0.10** | 0.08 | 0.80 | 0.48 | Newtonian |
| **0.50** | 0.42 | 0.84 | 0.48 | Newtonian |
| **1.00** | 0.89 | 0.89 | 0.48 | Newtonian Awal |
| **5.00** | 5.20 | 1.04 | 0.48 | Pengentalan Transisi |
| **10.00** | 18.50 | 1.85 | 0.48 | Shear-Thickening Aktif |
| **25.00** | 87.50 | 3.50 | 0.48 | Aglomerasi Klaster |
| **50.00** | 315.00 | 6.30 | 0.48 | Discontinuous Shear Thickening |
| **100.00** | 1420.00 | 14.20 | 0.48 | Penguncian Padat Semu |

### 2. Argumen Ilmiah dan Pembuktian Hipotesis
Hasil pengukuran empiris pada Tabel 1 mengonfirmasi bahwa fluida mengalami transisi dari perilaku kuasi-Newtonian pada $\dot{\gamma} < 5.0\text{ s}^{-1}$ menjadi *shear-thickening* tajam pada $\dot{\gamma} \ge 10.0\text{ s}^{-1}$. 

- **Klaim Ilmiah 1**: Indeks perilaku aliran terhitung $n = 1.62 \pm 0.04$ ($n > 1.0$) membuktikan secara meyakinkan sifat dilatansi suspensi.
- **Klaim Ilmiah 2**: Peningkatan viskositas lebih dari 17 kali lipat membuktikan pembentukan klaster hidrodinamik makroskopis di bawah tegangan geser tinggi.
- **Batasan Metodologis**: Pengukuran pada $\dot{\gamma} > 120\text{ s}^{-1}$ dibatasi oleh ketidakstabilan aliran permukaan (*Taylor vortex*) dan efek fraktur elastis tepi sampel.

## BAB V: Kesimpulan dan Saran
Suspensi pati jagung pada fraksi volume $\phi = 0.48$ terbukti secara kuantitatif menunjukkan transisi pengentalan geser discontinuous pada laju geser kritis $7.8 \pm 0.5\text{ s}^{-1}$. Penelitian selanjutnya disarankan untuk menganalisis pengaruh modifikasi permukaan partikel dan variasi kekuatan ionik larutan penyangga.
