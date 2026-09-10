# Dinamika Rotasi dan Momen Inersia

## 1. Konsep Torsi dan Momen Gaya
Torsi ($\tau$) merupakan kecenderungan gaya untuk memutar suatu benda tegar terhadap poros tertentu. Besaran torsi didefinisikan secara matematis melalui perkalian silang antara vektor posisi $\vec{r}$ dan vektor gaya $\vec{F}$:
$$\tau = \vec{r} \times \vec{F} = r F \sin\theta$$
di mana $\theta$ adalah sudut antara lengan gaya dan garis kerja gaya.

## 2. Hukum II Newton untuk Gerak Rotasi
Analog dengan hukum II Newton translasi ($F = ma$), percepatan sudut ($\alpha$) benda berbanding lurus dengan torsi total dan berbanding terbalik dengan momen inersia ($I$):
$$\sum \tau = I \alpha$$

### Tabel Momen Inersia Benda Tegar
| Bentuk Benda | Letak Poros | Rumus Momen Inersia |
| :--- | :--- | :--- |
| Silinder Pejal | Melalui sumbu simetri | $I = \frac{1}{2} M R^2$ |
| Bola Pejal | Melalui pusat massa | $I = \frac{2}{5} M R^2$ |
| Bola Berongga | Melalui diameter | $I = \frac{2}{3} M R^2$ |
| Batang Homogen | Melalui pusat massa | $I = \frac{1}{12} M L^2$ |

## 3. Kekekalan Momentum Sudut
Jika tidak ada torsi eksternal yang bekerja pada sistem ($\sum \tau_{\text{ext}} = 0$), maka momentum sudut total ($L$) sistem bernilai konstan:
$$L_1 = L_2 \implies I_1 \omega_1 = I_2 \omega_2$$
Aplikasi fenomena ini dapat diamati secara jelas pada gerakan penari balet yang melipat tangannya untuk memperbesar kecepatan sudut.
