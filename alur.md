# ANTARAGA - Alur Sistem Lengkap

> Dokumen ini menjelaskan alur teknis sistem ANTARAGA dari penerimaan data
> di backend sampai notifikasi ke pengguna, termasuk parameter dan hasil
> pelatihan kedua model ML.

---

## 1. Penerimaan Data (Backend)

### Stack
- **FastAPI** (Python) + **SQLAlchemy** ORM + **SQLite** (dev) / PostgreSQL (prod)
- Autentikasi: **JWT HS256** + **bcrypt** (custom, bukan pihak ketiga)

### Alur Masuk Data dari Smartband

```
Smartband / Sensor
      │
      │  HTTP POST  (Bearer JWT)
      ▼
┌─────────────────────────────────────────┐
│  POST /predict/stroke-risk              │
│  POST /estimate/vitals-from-ppg         │  ← dari sensor PPG mentah
└─────────────────────────────────────────┘
      │
      ├─ Validasi token → ambil user_id
      ├─ Resolve profil aktif (lansia yang sedang dipantau)
      ├─ Hitung fitur dari profil + vital
      ├─ Panggil model ML
      ├─ Tulis ke tabel  vital_readings   (data bersih per pembacaan)
      └─ Tulis ke tabel  prediction_logs  (request + response JSON lengkap)
```

### Endpoint Utama

| Endpoint | Metode | Fungsi |
|---|---|---|
| `/predict/stroke-risk` | POST | Input vital → prediksi risiko stroke (XGBoost) |
| `/estimate/vitals-from-ppg` | POST | Sinyal PPG mentah → estimasi vital (MLP) |
| `/assessment/abcd2` | POST | Skor ABCD2 → risiko pasca-TIA |
| `/vitals/latest` | GET | Pembacaan vital + risiko terbaru (polling dashboard) |
| `/vitals/history` | GET | Riwayat vital per hari (grafik Statistik Harian) |
| `/device/register-token` | POST | Daftarkan FCM token device untuk push notification |

### Tabel Database

```
users            - akun keluarga (email/telepon + password_hash + fcm_token)
profiles         - data profil lansia (usia, gender, BMI, riwayat, dll.)
vital_readings   - satu baris per pembacaan sensor (systolic, diastolic, HR, SpO2, gula)
prediction_logs  - log lengkap setiap panggilan endpoint ML
```

---

## 2. Model I - MLP untuk Estimasi Vital dari PPG

### Tujuan
Mengubah sinyal **PPG mentah** dari sensor (MAX30102 + SON1303/SON1303) menjadi
nilai vital yang dapat dibaca: tekanan darah sistolik, diastolik, dan gula darah.
Ini memungkinkan pengukuran non-invasif tanpa manset atau alat glukometer.

### Pipeline PPG → Fitur (Pulse Wave Analysis / PWA)

```
Sinyal PPG mentah (≥ 8 detik @ fs Hz)
         │
         ▼
  Bandpass Filter (Butterworth, order=3, 0.5–8.0 Hz)
  → menghilangkan drift baseline dan noise frekuensi tinggi
         │
         ▼
  Deteksi Puncak Sistolik (find_peaks, jarak minimum = 60/180 BPM)
  → temukan onset setiap denyut (minimum sebelum puncak)
         │
         ▼
  Ekstraksi Morfologi Per Denyut
  ┌─────────────────────────────────────────────────────┐
  │  amplitude       = puncak − baseline               │
  │  crest_time_s    = waktu naik dari onset ke puncak  │
  │  pulse_width_50  = lebar denyut di ½ amplitudo      │
  └─────────────────────────────────────────────────────┘
         │
         ▼
  Agregasi (rata-rata dan std dev seluruh denyut dalam window)
```

### Fitur Input MLP (per channel)

Diulangi untuk setiap channel yang tersedia: **green** (SON1303), **red**, **infrared** (MAX30102).

| Fitur | Keterangan |
|---|---|
| `{ch}_n_pulses` | Jumlah denyut terdeteksi dalam window |
| `{ch}_heart_rate_bpm` | Detak jantung dari interval antar puncak |
| `{ch}_amplitude_mean` | Rata-rata amplitudo denyut |
| `{ch}_amplitude_std` | Std dev amplitudo (indikator variabilitas) |
| `{ch}_crest_time_mean_s` | Rata-rata waktu naik (proxy stiffness arteri) |
| `{ch}_pulse_width_50_mean_s` | Rata-rata lebar denyut di ½ amplitudo |
| `{ch}_dc_mean` | Nilai DC rata-rata sinyal (intensitas cahaya rata-rata) |
| `green_red_amplitude_ratio` | Rasio amplitudo antar channel (seperti R-ratio SpO2) |
| `red_infrared_amplitude_ratio` | Rasio red/IR (dipakai kalkulasi SpO2 tradisional) |
| `age_years` | Usia pasien dari profil (fitur non-PPG) |

**Total fitur:** hingga 23 (tergantung channel yang aktif), disortir alfabetis saat inferensi.

### Arsitektur & Parameter MLP

```python
MLPRegressor(
    hidden_layer_sizes = (16, 8),   # 2 hidden layer: 16 → 8 neuron
    activation         = "tanh",    # fungsi aktivasi
    alpha              = 0.01,      # L2 regularization (weight decay)
    max_iter           = 5000,      # iterasi maksimum solver Adam
    random_state       = 42,
)
```

**Preprocessing:** `StandardScaler` (z-score normalization) sebelum masuk MLP.

**Output (regresi multitarget):**
- `systolic_bp_mmhg`
- `diastolic_bp_mmhg`
- `blood_glucose_mg_dl`

**Strategi validasi:**
- Jika data kalibrasi < 50 baris → **Leave-One-Out Cross-Validation (LOOCV)**
- Jika ≥ 50 baris → **KFold(5)**

Metrik: **MAE (Mean Absolute Error)** per target, cross-validated.

### Status Model MLP

> **⚠️ Belum dilatih.** Model ini sengaja TIDAK dilatih dengan data sintetis
> atau data dari jurnal lain (Gusti et al., 2025) karena hardware dan populasi
> berbeda → akurasi di kertas tapi tidak valid untuk pengguna nyata.
>
> Model baru dilatih setelah:
> 1. Hardware smartband ANTARAGA selesai dirakit (fase assembly)
> 2. Data kalibrasi dikumpulkan: pengukuran PPG dari smartband dicocokkan
>    dengan alat referensi (tensiometer standar + glukometer)
> 3. File disimpan di `data/calibration/calibration_data.csv`
> 4. Jalankan: `python model/train_ppg_vitals.py`

---

## 3. Model II - XGBoost untuk Deteksi Risiko Stroke

### Tujuan
Mengklasifikasikan apakah kombinasi data vital + profil pasien mengindikasikan
**risiko stroke tinggi** sehingga sistem dapat memberi peringatan dini.

### Dataset Pelatihan

| Item | Nilai |
|---|---|
| Sumber | Kaggle Stroke Prediction Dataset (WHO) |
| Jumlah baris | 5.110 pasien |
| Data latih | 3.577 (70%) |
| Data uji | 1.533 (30%) |
| Rasio kelas | 4,87% positif stroke - **sangat imbalanced** |

### Fitur Input

| Fitur | Tipe | Sumber |
|---|---|---|
| `age` | Numerik | Dihitung dari tanggal lahir profil |
| `avg_glucose_level` | Numerik | Pembacaan sensor (mg/dL) |
| `bmi` | Numerik | Dihitung dari berat/tinggi profil |
| `hypertension` | Biner (0/1) | **Diturunkan otomatis**: sistol ≥ 140 ATAU diastol ≥ 90 |
| `heart_disease` | Biner (0/1) | Dari profil pengguna |
| `gender` | Kategori | Dari profil (Male/Female/Other) |
| `residence_type` | Kategori | Dari profil (Urban/Rural) |
| `smoking_status` | Kategori | Dari profil (never smoked/formerly smoked/smokes/Unknown) |

> Fitur `ever_married` dan `work_type` (5 kategori) **sengaja dihapus** karena
> app tidak mengumpulkan data setara - memasukkan proxy yang ditebak lebih
> buruk daripada tidak memakai fitur sama sekali.

### Proses Pemilihan Model

Dua model diuji dengan **RandomizedSearchCV (40 iterasi, 5-fold CV)**,
dievaluasi dengan metrik **Average Precision** (lebih tepat untuk data imbalanced
daripada Accuracy atau AUC):

```
HistGradientBoostingClassifier  →  CV AP: 0.XXXX
XGBClassifier                   →  CV AP: 0.2313  ✓ MENANG
```

XGBClassifier dipilih sebagai model final.

### Parameter Terbaik (Hasil Tuning)

```python
XGBClassifier(
    tree_method        = "hist",         # histogram-based training (efisien)
    eval_metric        = "aucpr",        # area under precision-recall curve
    n_estimators       = 100,            # jumlah pohon
    max_depth          = 4,              # kedalaman maksimum tiap pohon
    learning_rate      = 0.03,           # step size (konservatif → stabil)
    min_child_weight   = 5,              # minimum sum of instance weight per leaf
    subsample          = 1.0,            # pakai semua data per iterasi
    colsample_bytree   = 1.0,            # pakai semua fitur per pohon
    reg_lambda         = 1.0,            # L2 regularization
    scale_pos_weight   = 19.56,          # bobot kelas positif ≈ neg/pos ratio
                                         # menangani imbalance 4.87%
)
```

### Penentuan Threshold (Tanpa Data Leakage)

Threshold **tidak** diambil dari test set. Prosedur:
1. Cross-validated **out-of-fold predictions** pada training set saja
2. Cari threshold (0.05–0.95, step 0.005) yang memaksimalkan **F1-score** OOF
3. Threshold final: **0.705**

Klasifikasi akhir:
```
probabilitas ≥ 0.705            → HIGH   (risiko tinggi)
probabilitas ≥ 0.705 × 0.5     → MEDIUM (risiko sedang)
probabilitas < 0.3525           → LOW    (risiko rendah)
```

### Hasil Pelatihan (Test Set)

| Metrik | Nilai |
|---|---|
| **AUC-ROC** | **0.823** |
| Average Precision | 0.250 |
| Precision | 0.206 |
| Recall (Sensitivity) | **0.493** |
| F1-Score | 0.290 |
| Threshold | 0.705 |

**Confusion Matrix (test set, n=1.533):**

```
                Prediksi
                Negatif   Positif
Aktual  Negatif   1.315      143    ← 143 false alarm (FP)
        Positif      38       37    ← 37 terdeteksi, 38 terlewat (FN)
```

> **Catatan interpretasi:** Recall 49% berarti hampir separuh kasus stroke
> nyata berhasil dideteksi. Untuk kasus medis berisiko tinggi, **Recall
> diprioritaskan di atas Precision** - false alarm lebih bisa diterima
> daripada melewatkan kasus stroke nyata. Threshold 0.705 secara sengaja
> digeser ke sisi konservatif untuk menjaga Recall tetap tinggi.

---

## 4. Skoring ABCD2 (Pasca Deteksi Anomali)

### Tujuan
ABCD2 bukan model ML melainkan **skor klinis berbasis aturan** yang digunakan
setelah ANTARAGA mendeteksi kemungkinan episode TIA (Transient Ischemic Attack)
atau ketika risiko XGBoost tinggi. Menghitung probabilitas stroke dalam
2, 7, dan 90 hari ke depan.

### Komponen Skor

| Komponen | Kondisi | Poin |
|---|---|---|
| **A** - Age | Usia ≥ 60 tahun | 1 |
| **B** - Blood Pressure | Sistol ≥ 140 mmHg atau Diastol ≥ 90 mmHg | 1 |
| **C** - Clinical Feature | Kelemahan unilateral | 2 |
| | Gangguan bicara tanpa kelemahan | 1 |
| | Gejala lain | 0 |
| **D** - Duration of TIA | ≥ 60 menit | 2 |
| | 10–59 menit | 1 |
| | < 10 menit | 0 |
| **D₂** - Diabetes | Ada riwayat diabetes | 1 |
| **Total** | | **0 – 7** |

### Interpretasi Skor & Risiko

| Skor | Kategori | Risiko 2 Hari | Risiko 7 Hari | Risiko 90 Hari |
|---|---|---|---|---|
| 0 – 3 | 🟢 **Rendah** | 1,0% | 1,2% | 3,1% |
| 4 – 5 | 🟡 **Sedang** | 4,1% | 5,9% | 9,8% |
| 6 – 7 | 🔴 **Tinggi** | 8,1% | 11,7% | 17,8% |

*Sumber: Johnston et al., 2007 (ABCD2 validation cohort)*

**Input ke skor ini:**
- Komponen A, B, D₂ → otomatis dari profil + vital terbaru
- Komponen C (gejala klinis) dan D (durasi) → diisi manual oleh keluarga
  melalui **formulir AssessmentFormScreen** di aplikasi Flutter

---

## 5. Alur End-to-End

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          SMARTBAND ANTARAGA                              │
│   MAX30102 (red/IR/SpO2/HR)  +  SON1303/SON1303 (green PPG)             │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ BLE / WiFi
                             │ HTTP POST Bearer JWT
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                                 │
│                                                                          │
│  [POST /estimate/vitals-from-ppg]                                        │
│   Sinyal PPG mentah                                                      │
│   → Bandpass Filter → Deteksi Pulsa → Fitur PWA                         │
│   → MLP (16,8) tanh  → sistol, diastol, gula darah    ← Model I        │
│                                                                          │
│  [POST /predict/stroke-risk]                                             │
│   vital + profil → susun 8 fitur                                        │
│   → XGBoost (n_est=100, depth=4, lr=0.03, spw=19.56)  ← Model II      │
│   → probabilitas  →  threshold 0.705  →  LOW / MEDIUM / HIGH            │
│                                                                          │
│   Tulis vital_readings + prediction_logs ke SQLite/PostgreSQL            │
└────────────┬──────────────────────────────────┬─────────────────────────┘
             │                                  │ Risiko HIGH?
             │ polling /vitals/latest (5 detik) │ → Firebase Admin SDK
             ▼                                  ▼
┌─────────────────────────┐        ┌──────────────────────────────────────┐
│   APLIKASI FLUTTER      │        │      FCM (Firebase Cloud Messaging)  │
│                         │        │  Cooldown: max 1 notif / 5 menit    │
│  Dashboard              │        └────────────────┬─────────────────────┘
│  ┌───────┐ ┌─────────┐  │                         │ Push Notification
│  │Tekanan│ │  Detak  │  │◄────────────────────────┘
│  │ Darah │ │Jantung  │  │  "⚠️ Risiko Stroke Tinggi Terdeteksi"
│  └───────┘ └─────────┘  │
│  ┌───────┐ ┌─────────┐  │   User tap notifikasi
│  │ SpO2  │ │  Gula   │  │         │
│  └───────┘ └─────────┘  │         ▼ deeplink
│                         │  ┌──────────────────────────────┐
│  Kartu animasi flash    │  │   AssessmentFormScreen       │
│  saat data baru masuk   │  │   (Formulir ABCD2)           │
│                         │  │                              │
│  "Update terakhir 18:13"│  │  Komponen A,B,D₂ otomatis   │
│   (timezone lokal)      │  │  Komponen C,D input manual  │
└─────────────────────────┘  │                              │
                             │  Kirim → POST /assessment/  │
                             │                              │
                             │  Hasil:                      │
                             │  Skor ABCD2: X/7             │
                             │  Risiko 2hr: X%              │
                             │  Risiko 7hr: X%              │
                             │  Risiko 90hr: X%             │
                             │  Rekomendasi teks            │
                             └──────────────────────────────┘
```

---

## 6. Ringkasan Parameter & Hasil

### Model I - MLP (PPG → Vital)

| Parameter | Nilai |
|---|---|
| Arsitektur | `(16, 8)` - 2 hidden layer |
| Aktivasi | `tanh` |
| Regularisasi | L2 `alpha=0.01` |
| Iterasi maks | 5000 |
| Preprocessing | StandardScaler (z-score) |
| Validasi | LOOCV (n<50) / KFold-5 (n≥50) |
| Metrik | MAE per target (sistol, diastol, gula) |
| Status | **Menunggu data kalibrasi hardware** |

### Model II - XGBoost (Risiko Stroke)

| Parameter | Nilai |
|---|---|
| Algoritma | XGBClassifier (`tree_method=hist`) |
| Dataset | 5.110 pasien, 4,87% positif stroke |
| `n_estimators` | 100 |
| `max_depth` | 4 |
| `learning_rate` | 0.03 |
| `scale_pos_weight` | 19.56 (kompensasi imbalance) |
| `reg_lambda` | 1.0 (L2) |
| `subsample` | 1.0 |
| `colsample_bytree` | 1.0 |
| `min_child_weight` | 5 |
| Threshold keputusan | **0.705** (dari F1-optimal OOF) |
| **AUC-ROC** | **0.823** |
| Recall (Sensitivity) | 0.493 |
| F1-Score | 0.290 |

### Skoring ABCD2

| Item | Nilai |
|---|---|
| Tipe | Rule-based (bukan ML) |
| Komponen otomatis | Age, Blood Pressure, Diabetes |
| Komponen manual | Clinical Features, Duration |
| Skor range | 0 – 7 |
| Referensi | Johnston et al., 2007 |

---

*Dihasilkan dari kode sumber ANTARAGA - `api/ml.py`, `model/train.py`,
`model/train_ppg_vitals.py`, `model/ppg_features.py`, `model/abcd2.py`,
`api/fcm.py`, `api/simulator.py`*
