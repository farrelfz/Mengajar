# Gerak Harmonik Sederhana (GHS) dan Resonansi

## 1. Konsep Gaya Pemulih dan Hukum Hooke
Gerak harmonik sederhana merupakan gerak bolak-balik periodik di sekitar titik kesetimbangan stabil tanpa redaman. Gaya pemulih linier berbanding lurus dengan simpangan:
$$F = -k x$$
Tanda negatif menunjukkan bahwa arah gaya pemulih selalu berlawanan arah dengan vektor perpindahan posisi partikel dari titik kesetimbangan.

## 2. Persamaan Diferensial Osilator Harmonik
Persamaan diferensial gerak satu dimensi untuk osilator bermassa $m$ dan konstanta pegas $k$ dirumuskan sebagai:
$$\frac{d^2 x}{dt^2} + \omega^2 x = 0$$
dengan frekuensi sudut natural osilasi:
$$\omega = \sqrt{\frac{k}{m}} = 2\pi f = \frac{2\pi}{T}$$

## 3. Kinematika Posisi, Kecepatan, dan Percepatan
Solusi analitis persamaan gerak untuk kondisi awal simpangan maksimum $A$ pada $t=0$:
$$x(t) = A \cos(\omega t + \phi_0)$$
Turunan pertama menghasilkan fungsi kecepatan osilator:
$$v(t) = \frac{dx}{dt} = -A \omega \sin(\omega t + \phi_0)$$
Turunan kedua menghasilkan fungsi percepatan:
$$a(t) = \frac{dv}{dt} = -A \omega^2 \cos(\omega t + \phi_0) = -\omega^2 x(t)$$

## 4. Transformasi dan Konservasi Energi Mekanik
Total energi mekanik sistem osilator ideal selalu kekal setiap saat:
$$E = E_k + E_p = \frac{1}{2} m v^2 + \frac{1}{2} k x^2 = \frac{1}{2} k A^2$$
Pada simpangan maksimum ($x = \pm A$), kecepatan bernilai nol sehingga seluruh energi berbentuk energi potensial pegas. Sebaliknya, pada titik kesetimbangan ($x = 0$), energi potensial nol dan energi kinetik bernilai maksimum.

## 5. Bandul Sederhana sebagai Aproksimasi GHS
Untuk ayunan bandul matematis bersudut kecil ($\theta < 10^\circ$), berlaku aproksimasi $\sin\theta \approx \theta$. Periode osilasi hanya bergantung pada panjang tali $L$ dan percepatan gravitasi $g$:
$$T = 2\pi \sqrt{\frac{L}{g}}$$
Massa beban bandul tidak memengaruhi periode ayunan.

## 6. Fenomena Resonansi dan Osilasi Terdorong
Ketika osilator dipacu oleh gaya periodik eksternal $F_{\text{ext}} = F_0 \cos(\omega_d t)$, amplitudo osilasi mencapai nilai maksimum jika frekuensi pemacu mendekati frekuensi alami sistem ($\omega_d \to \omega_0$). Fenomena resonansi akustik dan mekanik memiliki aplikasi krusial pada desain jembatan gantung dan instrumen musik.
