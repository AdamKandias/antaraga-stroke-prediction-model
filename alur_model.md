# Konsep Model AI — ANTARAGA

---

## 1. MLP (Multi-Layer Perceptron)

### Apa itu MLP?

MLP adalah jenis **jaringan saraf tiruan (neural network)** yang paling dasar
dan paling banyak dipakai. Ia meniru cara otak bekerja: sinyal masuk dari
satu sisi, diproses berlapis-lapis, dan keluar sebagai hasil prediksi di sisi
lain.

### Struktur

```
INPUT LAYER          HIDDEN LAYER 1     HIDDEN LAYER 2     OUTPUT LAYER
(23 fitur PPG)           (16 neuron)         (8 neuron)       (3 output)

  x₁  ──┐                                                  ┌─→ sistol (mmHg)
  x₂  ──┤     ┌──[○]──┐                ┌──[○]──┐          ├─→ diastol (mmHg)
  x₃  ──┼──►  ├──[○]──┤  ──────────►  ├──[○]──┤  ──────► └─→ gula darah (mg/dL)
  ...  ──┤     ├──[○]──┤                └──[○]──┘
  x₂₃ ──┘     └──[○]──┘
                 16 node                  8 node
```

### Cara Kerja

**1. Forward Pass (Maju)**

Setiap neuron menghitung:

```
output = aktivasi( w₁x₁ + w₂x₂ + ... + wₙxₙ + bias )
```

- `x` = nilai input dari neuron sebelumnya
- `w` = bobot (weight) — inilah yang dipelajari saat training
- `bias` = nilai geser
- `aktivasi` = fungsi nonlinear (di ANTARAGA: **tanh**)

Fungsi **tanh** mengubah nilai apapun menjadi rentang −1 sampai +1:

```
tanh(x) = (eˣ − e⁻ˣ) / (eˣ + e⁻ˣ)
```

Fungsi ini dipilih karena sinyal PPG punya nilai positif dan negatif
(setelah bandpass filter), dan tanh lebih stabil dari ReLU untuk sinyal
fisiologis.

**2. Backpropagation (Mundur) — Proses Belajar**

Setelah forward pass, MLP membandingkan hasilnya dengan nilai referensi
(ground truth dari kalibrasi). Selisihnya disebut **loss (error)**:

```
Loss = MSE = (1/n) Σ (prediksi − nilai_nyata)²
```

Lalu error ini disebarkan **mundur** ke seluruh jaringan dengan
**aturan rantai (chain rule)** kalkulus untuk menghitung:
*"berapa kontribusi setiap bobot terhadap error ini?"*

Setelah itu setiap bobot diperbarui:

```
w_baru = w_lama − learning_rate × ∂Loss/∂w
```

Proses ini diulang ribuan kali (`max_iter=5000`) sampai error
tidak turun lagi.

**3. Regularisasi L2 (alpha=0.01)**

Agar bobot tidak terlalu besar (overfitting), ditambahkan penalti:

```
Loss_total = MSE + alpha × Σ w²
```

`alpha=0.01` adalah trade-off ringan — jaringan tetap fleksibel tapi
tidak menghafal noise data kalibrasi.

### Penggunaan di ANTARAGA

```
Sinyal PPG (green/red/IR, ≥8 detik)
    ↓ Pipeline PWA (Bandpass → Peak Detection → Fitur Morfologi)
23 fitur numerik + usia
    ↓ StandardScaler (z-score normalization)
MLP (16 → 8 → 3)  [tanh, alpha=0.01, max_iter=5000]
    ↓
Estimasi: sistol (mmHg) | diastol (mmHg) | gula darah (mg/dL)
```

### Status
Model ini **belum dilatih** — arsitektur dan pipeline sudah siap,
menunggu data kalibrasi dari hardware nyata (pasang smartband → ukur
dengan alat standar → simpan hasilnya).

---

## 2. XGBoost — Extreme Gradient Boosting

### Apa itu Gradient Boosting?

Gradient Boosting adalah teknik **ensemble** (gabungan banyak model lemah)
yang membangun model satu per satu secara berurutan. Setiap model baru
berfokus pada **kesalahan model sebelumnya**.

Analogi: seperti seorang murid yang setiap kali ujian hanya belajar soal
yang kemarin salah. Lama-lama ia jago di semua soal.

### Algoritma Gradient Boosting (Dasar)

```
Iterasi 1:  Buat pohon keputusan T₁ → prediksi F₁(x)
             Error₁ = y - F₁(x)

Iterasi 2:  Buat pohon T₂ yang belajar dari Error₁ → F₂(x)
             Error₂ = y - [F₁(x) + F₂(x)]

Iterasi 3:  Buat pohon T₃ yang belajar dari Error₂ → F₃(x)
             ...

Final:      F(x) = F₁(x) + F₂(x) + ... + Fₙ(x)
            (semua pohon dijumlahkan dengan bobot learning rate η)
```

Kata "Gradient" berasal dari cara mencari arah perbaikan: setiap pohon
baru dibuat untuk memprediksi **negatif gradien dari fungsi loss**,
bukan error biasa. Ini lebih umum dan bisa dipakai untuk berbagai jenis loss.

### Apa yang Membuat XGBoost *Extreme*?

XGBoost (Chen & Guestrin, 2016) adalah implementasi Gradient Boosting yang
dioptimasi secara matematis dan teknis:

**a. Fungsi Objektif dengan Regularisasi**

Berbeda dari GBM standar, XGBoost secara eksplisit meminimalkan:

```
Obj = Σ L(yᵢ, ŷᵢ) + Σₖ Ω(Tₖ)
           ↑                ↑
     Loss per data      Penalti kompleksitas pohon
```

Di mana:
```
Ω(T) = γ × (jumlah daun) + λ/2 × Σ (bobot daun)²
```

- `γ` = penalti per daun (pruning otomatis)
- `λ` = L2 regularisasi pada bobot daun → di ANTARAGA: `reg_lambda=1.0`

**b. Aproksimasi Histogram (tree_method="hist")**

Daripada mencoba semua nilai split yang mungkin (lambat untuk dataset besar),
XGBoost membagi nilai fitur menjadi **bucket histogram** dan hanya mencari
split terbaik di antara bucket. Jauh lebih cepat, akurasi hampir sama.

**c. Penanganan Imbalance: scale_pos_weight**

Dataset stroke: 95% negatif, 5% positif. Kalau dibiarkan, model malas
memprediksi stroke sama sekali. Solusi:

```
scale_pos_weight = jumlah_negatif / jumlah_positif ≈ 19.56
```

Artinya setiap satu data positif (stroke) dihitung **19,56× lebih berat**
daripada satu data negatif saat menghitung loss. Model jadi lebih sensitif
terhadap kasus stroke.

### Parameter ANTARAGA dan Maknanya

```python
XGBClassifier(
    n_estimators    = 100,    # jumlah pohon yang dibangun berurutan
    max_depth       = 4,      # kedalaman maks tiap pohon (semakin dalam → overfitting)
    learning_rate   = 0.03,   # η — seberapa besar kontribusi tiap pohon
                              # kecil = konservatif, butuh lebih banyak pohon
    min_child_weight= 5,      # jumlah minimum data di setiap daun
                              # makin besar → pohon lebih sederhana → anti-overfitting
    subsample       = 1.0,    # pakai 100% data per iterasi (tidak sub-sampling)
    colsample_bytree= 1.0,    # pakai 100% fitur per pohon
    reg_lambda      = 1.0,    # bobot penalti L2 pada daun pohon
    scale_pos_weight= 19.56,  # kompensasi imbalance kelas
    tree_method     = "hist", # histogram-based (lebih cepat)
    eval_metric     = "aucpr" # optimasi Area Under Precision-Recall Curve
)
```

### Cara Kerja di ANTARAGA

```
Input (8 fitur per pasien):
  age=65, glucose=180, bmi=27.4, hypertension=1,
  heart_disease=0, gender="Male", residence="Urban", smoking="smokes"
         ↓
  Pohon 1: "Usia > 60 DAN glukosa > 160?" → probabilitas awal 0.12
         ↓
  Pohon 2: "Hipertensi DAN perokok?" → tambah 0.08 × 0.03
         ↓
  Pohon 3: "BMI antara 25-30?" → tambah / kurangi ...
         ↓  (100 pohon berurutan)
  Probabilitas akhir: 0.78
         ↓
  Bandingkan dengan threshold 0.705
         ↓
  0.78 ≥ 0.705 → RISIKO TINGGI 🔴
```

### Hasil Pelatihan

| Metrik | Nilai |
|---|---|
| AUC-ROC | **0.823** |
| Recall (Sensitivitas) | 0.493 |
| Precision | 0.206 |
| F1-Score | 0.290 |
| Threshold optimal | **0.705** |

> Recall 49% artinya dari 100 orang yang benar-benar berisiko stroke,
> sistem berhasil mendeteksi ~49 orang. Angka ini rendah karena dataset
> publik — diharapkan meningkat setelah fine-tuning dengan data kalibrasi
> dari pengguna ANTARAGA nyata.

---

## 3. Perbandingan MLP vs XGBoost dalam ANTARAGA

| Aspek | MLP | XGBoost |
|---|---|---|
| **Dipakai untuk** | Estimasi vital dari PPG | Klasifikasi risiko stroke |
| **Tipe masalah** | Regresi (output angka) | Klasifikasi biner |
| **Cara belajar** | Gradient descent, semua parameter sekaligus | Boosting bertahap, pohon demi pohon |
| **Kekuatan** | Bisa tangkap pola nonlinear kompleks dari sinyal | Robust terhadap fitur campuran, tahan imbalance |
| **Kelemahan** | Butuh data banyak, sensitif ke skala fitur | Lebih sulit diinterpretasi dibanding satu pohon |
| **Preprocessing** | Wajib StandardScaler | Tidak perlu normalisasi |
| **Status** | Menunggu kalibrasi hardware | ✅ Sudah dilatih & deployed |

---

*Referensi: Chen & Guestrin (2016) "XGBoost: A Scalable Tree Boosting System";
Rumelhart et al. (1986) "Learning representations by back-propagating errors"*
