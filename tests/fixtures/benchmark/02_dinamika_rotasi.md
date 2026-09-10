# Dinamika Rotasi dan Keseimbangan Benda Tegar

## Pendahuluan
Dinamika rotasi adalah cabang mekanika klasik yang mempelajari gerak rotasi benda tegar dengan mempertimbangkan penyebab terjadinya gerak tersebut, yaitu torsi atau momen gaya. Dalam kehidupan sehari-hari, prinsip dinamika rotasi diterapkan pada roda kendaraan, engsel pintu, turbin angin, hingga katrol pengangkat beban.

## Konsep Torsi dan Momen Gaya
Torsi ($\tau$) merupakan ukuran keefektifan suatu gaya dalam menghasilkan rotasi terhadap suatu sumbu putar tertentu. Besaran ini bergantung pada besarnya gaya yang bekerja, jarak titik tangkap gaya ke poros putar (lengan gaya), serta sudut antara vektor gaya dan vektor posisi.

### Hubungan Kausal Torsi
1. Semakin panjang lengan momen ($r$), torsi yang dihasilkan semakin besar untuk gaya ($F$) yang konstan.
2. Torsi mencapai nilai maksimum ketika arah gaya tegak lurus sempurna ($\theta = 90^\circ$) terhadap lengan momen.
3. Jika arah garis kerja gaya melewati poros rotasi ($r = 0$ atau $\theta = 0^\circ$), torsi bernilai nol dan tidak terjadi percepatan sudut.

Secara matematis, hubungan momen gaya didefinisikan sebagai:
$$\tau = r \times F = r F \sin(\theta)$$

## Momen Inersia
Momen inersia ($I$) adalah ukuran kelembaman suatu benda tegar untuk mempertahankan keadaan rotasinya. Berbeda dengan massa translasi yang bersifat skalar dan tetap, momen inersia bergantung pada distribusi massa benda terhadap sumbu rotasi yang dipilih.

Untuk sistem partikel titik:
$$I = \sum m_i r_i^2$$

Untuk benda tegar kontinu:
- Silinder pejal diputar terhadap sumbu simetrinya: $I = \frac{1}{2} M R^2$
- Bola pejal diputar terhadap diameternya: $I = \frac{2}{5} M R^2$
- Batang tipis diputar terhadap pusat massa: $I = \frac{1}{12} M L^2$
- Batang tipis diputar terhadap salah satu ujungnya: $I = \frac{1}{3} M L^2$

## Hukum II Newton untuk Rotasi
Analogi hukum kedua Newton dalam gerak rotasi menyatakan bahwa percepatan sudut ($\alpha$) berbanding lurus dengan resultan torsi luar ($\sum \tau$) dan berbanding terbalik dengan momen inersia ($I$) sistem:
$$\sum \tau = I \cdot \alpha$$

### Analisis Sebab-Akibat
Ketika torsi eksternal diterapkan pada silinder berputar:
- Peningkatan torsi sebesar 100% menghasilkan peningkatan percepatan sudut sebesar 100% jika momen inersia tidak berubah.
- Pergeseran massa ke bagian tepi silinder meningkatkan momen inersia, sehingga memperlambat respons akselerasi sudut untuk torsi yang sama.

## Momentum Sudut dan Hukum Kekekalan
Momentum sudut ($L$) dari benda tegar didefinisikan sebagai:
$$L = I \cdot \omega$$

Jika tidak ada torsi luar netto yang bekerja pada sistem ($\sum \tau_{\text{ext}} = 0$), maka momentum sudut sistem bersifat kekal:
$$I_1 \omega_1 = I_2 \omega_2$$

Penerapan nyata terjadi pada peselancar es (figure skater) yang merapatkan lengannya ke tubuh. Dengan merapatkan lengan, jarak massa ke sumbu rotasi mengecil sehingga momen inersia $I$ mengecil, yang secara otomatis melipatgandakan kecepatan sudut rotasi $\omega$.

## Kesimpulan
Keseimbangan dan dinamika rotasi ditentukan oleh keseimbangan resultan gaya translasi ($\sum F = 0$) dan keseimbangan resultan momen gaya ($\sum \tau = 0$).
