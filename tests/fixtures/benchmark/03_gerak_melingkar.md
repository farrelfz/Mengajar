# Analisis Kinematika dan Dinamika Gerak Melingkar

## Pendahuluan
Gerak melingkar adalah gerak suatu partikel atau benda dengan lintasan berbentuk lingkaran terhadap suatu titik pusat acuan tetap. Gerak ini dibedakan menjadi Gerak Melingkar Beraturan (GMB) dan Gerak Melingkar Berubah Beraturan (GMBB).

## Perbandingan Konseptual: GMB vs GMBB
Tabel perbandingan karakteristik kinematis kedua jenis gerak melingkar:

| Parameter | Gerak Melingkar Beraturan (GMB) | Gerak Melingkar Berubah Beraturan (GMBB) |
| :--- | :--- | :--- |
| **Kelajuan Linear ($v$)** | Konstan | Berubah secara teratur |
| **Kecepatan Sudut ($\omega$)** | Konstan ($\alpha = 0$) | Berubah linier terhadap waktu |
| **Percepatan Sudut ($\alpha$)** | Nol | Konstan ($\alpha \neq 0$) |
| **Percepatan Sentripetal ($a_s$)** | Ada (arah menuju pusat) | Ada (arah menuju pusat) |
| **Percepatan Tangensial ($a_t$)** | Nol | Ada ($a_t = \alpha \cdot r$) |
| **Percepatan Total ($a_{\text{tot}}$)** | Sama dengan $a_s$ | $\sqrt{a_s^2 + a_t^2}$ |

## Penurunan Matematis Percepatan Sentripetal
Percepatan sentripetal timbul karena perubahan arah vektor kecepatan linear secara kontinu, meskipun nilai kelajuannya tetap.

Misalkan sebuah partikel bergerak dari posisi $\mathbf{r}_1$ ke $\mathbf{r}_2$ dalam selang waktu $\Delta t$:
$$\Delta \theta = \frac{\Delta s}{r}$$

Untuk $\Delta t \to 0$, rasio perubahan vektor kecepatan terhadap kelajuan sebanding dengan rasio perpindahan busur terhadap jari-jari:
$$\frac{|\Delta \mathbf{v}|}{v} = \frac{|\Delta \mathbf{r}|}{r}$$

Dengan membagi kedua ruas dengan $\Delta t$ dan mengambil limit mendekati nol:
$$a_s = \lim_{\Delta t \to 0} \frac{|\Delta \mathbf{v}|}{\Delta t} = \frac{v}{r} \cdot \lim_{\Delta t \to 0} \frac{|\Delta \mathbf{r}|}{\Delta t} = \frac{v^2}{r}$$

Mengingat hubungan linear dan angular $v = \omega \cdot r$, maka percepatan sentripetal dapat dinyatakan dalam bentuk:
$$a_s = \omega^2 \cdot r$$

## Gaya Sentripetal dan Aplikasi Dinamika
Berdasarkan Hukum II Newton, resultan gaya radial yang mempertahankan partikel pada lintasan melingkar adalah Gaya Sentripetal:
$$F_s = m \cdot a_s = \frac{m \cdot v^2}{r} = m \cdot \omega^2 \cdot r$$

### Studi Kasus: Tikungan Jalan Miring Licin
Pada tikungan jalan beraspal dengan sudut kemiringan $\theta$ tanpa gesekan:
- Gaya normal terurai menjadi komponen vertikal $N \cos(\theta) = m g$
- Komponen horisontal menuju pusat kurvatur $N \sin(\theta) = F_s = \frac{m v^2}{r}$

Dengan membagi kedua persamaan:
$$\tan(\theta) = \frac{v^2}{r \cdot g} \implies v_{\text{maks}} = \sqrt{r \cdot g \cdot \tan(\theta)}$$

## Contoh Perhitungan Terapan
Sebuah mobil bermassa $1200\text{ kg}$ melintasi tikungan dengan radius $r = 50\text{ m}$ dan sudut kemiringan jalan $\theta = 30^\circ$. Hitung kelajuan aman tanpa gaya gesekan ($g = 9.8\text{ m/s}^2$):
$$v = \sqrt{50 \cdot 9.8 \cdot \tan(30^\circ)} = \sqrt{490 \cdot 0.577} \approx 16.8\text{ m/s}\ (60.5\text{ km/jam})$$

## Kesimpulan
Percepatan sentripetal selalu mengarah tegak lurus ke pusat lintasan melingkar dan tidak mengubah kelajuan benda melainkan mengubah orientasi arah geraknya secara berkesinambungan.
