# Alur Model ANTARAGA — Teknis & Parameter

> Dokumen ini menjelaskan arsitektur lengkap pipeline prediksi risiko stroke,
> dari sinyal PPG sensor hingga skor akhir, beserta bobot, parameter, dan
> sumber data setiap komponen.

---

## Gambaran Umum Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    SENSOR ANTARAGA                       │
│   MAX30102 (IR 880nm + RED 660nm)  +  SON1303 (525nm)   │
│   18-bit / 400Hz                   +  12-bit / 200Hz    │
└────────────────────┬────────────────────────────────────┘
                     │  sinyal PPG mentah (buffer 10 detik)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  SQI FILTERING                           │
│   Saring paket buruk (NO_FINGER | SATURATED |           │
│   FLAT | MOTION) sebelum analisis                        │
└────────────────────┬────────────────────────────────────┘
                     │  sinyal bersih
                     ▼
┌─────────────────────────────────────────────────────────┐
│              TAHAP 1: EKSTRAKSI FITUR PPG               │
│                                                         │
│  ir_dc_mean   — rata-rata komponen DC kanal IR          │
│  ir_ac_p2p    — amplitudo AC puncak-ke-lembah IR        │
│  red_dc_mean  — rata-rata komponen DC kanal RED         │
│  red_ac_p2p   — amplitudo AC puncak-ke-lembah RED       │
│  bpm          — detak jantung (autocorrelation)         │
└────────────────────┬────────────────────────────────────┘
                     │  + age_years, gender_code (dari profil)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              TAHAP 2: MLP KALIBRASI                     │
│         (MLPRegressor per target, solver=lbfgs)         │
│                                                         │
│  Input (7 fitur):                                       │
│    ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p,     │
│    bpm, age_years, gender_code                          │
│                                                         │
│  Output (5 prediksi vital sign):                        │
│    gula_darah_mg_dl   → avg_glucose_level (XGBoost)    │
│    sistolik_mmhg      → derivasi flag hypertension      │
│    diastolik_mmhg     → derivasi flag hypertension      │
│    kolesterol_mg_dl   → (belum dipakai di XGBoost)     │
│    asam_urat_mg_dl    → (belum dipakai di XGBoost)     │
└────────────────────┬────────────────────────────────────┘
                     │  + data profil dari mobile app
                     ▼
┌─────────────────────────────────────────────────────────┐
│              TAHAP 3: XGBOOST STROKE RISK               │
│         XGBClassifier — 8 fitur — threshold 0.705       │
│                                                         │
│  Output: probabilitas risiko stroke 0.0–1.0             │
│  Klasifikasi: LOW (<0.705) / HIGH (≥0.705)              │
└─────────────────────────────────────────────────────────┘
```

---

## Tahap 1: Ekstraksi Fitur PPG

| Fitur | Sumber | Deskripsi |
|---|---|---|
| `ir_dc_mean` | Buffer IR 880nm | Rata-rata amplitudo sinyal DC (komponen statis) |
| `ir_ac_p2p` | Buffer IR 880nm | Amplitudo pulsasi AC (puncak ke lembah) |
| `red_dc_mean` | Buffer RED 660nm | Rata-rata amplitudo DC kanal merah |
| `red_ac_p2p` | Buffer RED 660nm | Amplitudo pulsasi AC kanal merah |
| `bpm` | IR (autocorrelation) | Detak jantung dihitung dari frekuensi pulsasi |

---

## Tahap 2: MLP Kalibrasi

### Arsitektur

```
Input layer: 7 neuron
Hidden layer 1: 64 neuron (ReLU)
Hidden layer 2: 32 neuron (ReLU)
Output layer: 1 neuron (nilai kontinu per model)

Solver: lbfgs (optimal untuk dataset kecil <200 baris)
Regularisasi alpha: 0.01
Cross-validation: LOO jika n<30, 5-fold jika n≥30
```

### Fitur Input MLP

| Fitur | Sumber | Tipe |
|---|---|---|
| `ir_dc_mean` | Sensor (MAX30102 IR) | Float |
| `ir_ac_p2p` | Sensor (MAX30102 IR) | Float |
| `red_dc_mean` | Sensor (MAX30102 RED) | Float |
| `red_ac_p2p` | Sensor (MAX30102 RED) | Float |
| `bpm` | Dihitung dari IR | Float |
| `age_years` | Profil mobile (ulang tahun) | Float |
| `gender_code` | Profil mobile (L=1, P=0) | Binary |

### Output MLP → Vital Sign yang Diprediksi

| Target | Satuan | Dipakai Tahap Selanjutnya |
|---|---|---|
| `gula_darah_mg_dl` | mg/dL | ✓ → `avg_glucose_level` ke XGBoost |
| `sistolik_mmhg` | mmHg | ✓ → derivasi flag `hypertension` |
| `diastolik_mmhg` | mmHg | ✓ → derivasi flag `hypertension` |
| `kolesterol_mg_dl` | mg/dL | (belum dipakai di XGBoost saat ini) |
| `asam_urat_mg_dl` | mg/dL | (belum dipakai di XGBoost saat ini) |

**Derivasi hypertension:**
```
hypertension = 1  jika  sistolik ≥ 140  ATAU  diastolik ≥ 90
hypertension = 0  jika  keduanya di bawah ambang
```

---

## Tahap 3: XGBoost Stroke Risk Classifier

### Parameter Model Terpilih

```
model:          XGBClassifier (menang vs HistGradientBoosting)
n_estimators:   100
max_depth:      4
learning_rate:  0.03
min_child_weight: 5
subsample:      1.0
colsample_bytree: 1.0
reg_lambda:     1.0
scale_pos_weight: 19.56  (kompensasi class imbalance — rasio negatif/positif)
tree_method:    hist
eval_metric:    aucpr
```

### Fitur Input dan Bobot (Feature Importance)

| Fitur | Bobot (%) | Sumber | Keterangan |
|---|---|---|---|
| `age` | **50.2%** | Profil mobile (birthday) | Faktor risiko terbesar |
| `bmi` | 8.6% | Profil mobile (BB ÷ TB²) | Dihitung otomatis |
| `hypertension` | 7.9% | Derived dari MLP (sistolik/diastolik) | 0 atau 1 |
| `gender` | 7.8% | Profil mobile | Male/Female/Other |
| `avg_glucose_level` | 7.6% | **MLP ANTARAGA** (gula darah) | mg/dL |
| `heart_disease` | 7.6% | Profil mobile | 0 atau 1 |
| `residence_type` | 5.9% | Profil mobile | Urban/Rural |
| `smoking_status` | 4.4% | Profil mobile | 3 kategori |

> **Catatan:** Dari 8 fitur XGBoost, **3 fitur dinamis** berasal dari sensor
> ANTARAGA (via MLP): gula darah, sistolik, diastolik. Sisanya 5 fitur statis
> dari profil yang diisi sekali oleh pengguna.

### Threshold dan Metrik Model

| Metrik | Nilai |
|---|---|
| **Threshold keputusan** | 0.705 |
| **AUC-ROC** | 0.823 |
| **Precision (positif)** | 20.6% |
| **Recall (sensitivitas)** | 49.3% |
| **F1 Score** | 0.290 |
| **Akurasi total** | 88.2%* |

*Akurasi total menyesatkan karena dataset sangat tidak seimbang (4.9% positif).
Metrik yang lebih relevan secara klinis adalah Recall dan Precision.

### Interpretasi Confusion Matrix (Test Set, n=1533)

```
                    Prediksi: RENDAH   Prediksi: TINGGI
Aktual: RENDAH          1315               143    ← False Positive
Aktual: TINGGI            38                37    ← True Positive

False Positive Rate: 143 dari 180 prediksi TINGGI = 79.4% false alarm
Sensitivity (Recall): 37 dari 75 kasus nyata terdeteksi = 49.3%
```

### Fitur yang Dihapus dari Dataset Asli

| Fitur | Alasan Dihapus |
|---|---|
| `ever_married` | Tidak relevan untuk target lansia (diasumsikan menikah) |
| `work_type` | 5-kategori asli tidak kompatibel; digantikan `is_working` di profil tapi belum masuk model |

---

## Mapping Data: Mobile App → Model

### Data dari Profil Mobile (sekali isi)

| Field di Flutter | Dipakai oleh | Mapped ke |
|---|---|---|
| `birthday` | XGBoost | `age` |
| `gender` (L/P) | MLP + XGBoost | `gender_code` (MLP), `gender` (XGBoost) |
| `weight_kg` + `height_cm` | XGBoost | `bmi = weight / (height/100)²` |
| `heartDisease` (bool) | XGBoost | `heart_disease` (0/1) |
| `residenceType` (Urban/Rural) | XGBoost | `residence_type` |
| `smokingStatus` (3 pilihan) | XGBoost | `smoking_status` |
| `hasDiabetes` (bool) | — | Dikumpulkan, belum dipakai di model |
| `isWorking` (bool) | — | Dikumpulkan, belum dipakai di model |

### Data dari Sensor ANTARAGA (setiap pengukuran)

| Komponen | Menghasilkan | Dipakai oleh |
|---|---|---|
| MAX30102 IR + RED → MLP | `gula_darah_mg_dl` | XGBoost `avg_glucose_level` |
| MAX30102 IR + RED → MLP | `sistolik_mmhg` + `diastolik_mmhg` | XGBoost `hypertension` (derived) |
| MAX30102 IR → PPG analysis | `bpm` | MLP input + tampilan dashboard |

---

## Parameter Belum Dipakai di XGBoost

| Data yang Dikumpulkan | Status | Potensi |
|---|---|---|
| `kolesterol_mg_dl` (dari MLP) | Belum di XGBoost | Perlu dataset publik yang mencantumkan kolesterol + stroke |
| `asam_urat_mg_dl` (dari MLP) | Belum di XGBoost | Hubungan asam urat-stroke ada tapi tidak sekuat gula darah |
| `isWorking` (dari profil) | Belum di XGBoost | Bisa dimasukkan jika retrain dengan data yang memiliki fitur ini |
| `hasDiabetes` (dari profil) | Belum di XGBoost | Berkorelasi kuat dengan avg_glucose_level — perlu uji multikolinearitas |

**Rekomendasi:** Untuk PKM saat ini, kolesterol dan asam urat lebih bernilai sebagai
output informatif ke pengguna (dashboard) daripada fitur tambahan XGBoost — karena
dataset publik yang dipakai untuk pelatihan tidak memuat kedua variabel tersebut.

---

## Pertanyaan: Data Dari Berapa Periode?

Saat ini XGBoost menggunakan **satu sesi pengukuran** (snapshot tunggal).
Opsi ke depan:

| Pendekatan | Keterangan |
|---|---|
| **Snapshot (sekarang)** | Nilai dari sesi terakhir langsung dikirim ke XGBoost |
| **Rolling average (7 hari)** | Rata-rata 7 hari terakhir untuk gula darah & TD — mengurangi noise pengukuran tunggal |
| **Tren (slope)** | Apakah gula darah naik atau turun dalam N hari terakhir — fitur tambahan yang lebih informatif |

Implementasi rolling average membutuhkan tabel riwayat vital reading dan query per profil.

---

*Dokumen ini adalah bagian dari proposal PKM-KC ANTARAGA.*
