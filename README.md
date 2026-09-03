# ANTARAGA

Smartband berbasis PPG dan AI untuk deteksi risiko stroke iskemik secara real-time. Terdiri dari firmware XIAO ESP32-S3, backend FastAPI, model XGBoost, dan aplikasi mobile Flutter.

**Produksi:** `https://antaraga.web.id` · `https://api.antaraga.web.id`

---

## Struktur Proyek

```
api/          FastAPI backend (auth, profil, prediksi, ingest firmware)
model/        Model XGBoost + MLP, script training, fitur PPG
Firmware/     Program XIAO ESP32-S3 (sensor PPG, WiFi, HTTP ingest)
scripts/      Setup VPS, konfigurasi nginx, dev helpers
assets/       Ikon dan aset visual
notebooks/    Eksplorasi data (EDA), bukan bagian sistem produksi
```

---

## Koneksi ke API

**Base URL produksi:** `https://api.antaraga.web.id`

Semua endpoint butuh header `Authorization: Bearer <token>` kecuali endpoint auth dan ingest firmware. Untuk test lokal gunakan `http://localhost:8000`.

---

## Untuk Firmware (XIAO ESP32-S3)

Firmware mengirim data sensor tanpa login - identitasnya berdasarkan `DEVICE_ID` unik yang sudah di-pair ke akun pengguna lewat mobile app.

### Konfigurasi `config.h`

```cpp
#define CLOUD_HOST        "api.antaraga.web.id"
#define CLOUD_PORT        443
#define CLOUD_USE_HTTPS   true
#define DEVICE_ID         "antaraga-001"          // unik per perangkat
#define CLOUD_API_KEY     "antaraga-hw-2026-01"   // dari .env DEVICE_INGEST_KEY
```

### Endpoint Ingest

```
POST /v1/ingest
```

Dikirim setiap batch (default 500ms). **Tidak perlu Authorization header** - autentikasi via `id` + `key` di body.

**Request body:**
```json
{
  "id":     "antaraga-001",
  "key":    "antaraga-hw-2026-01",
  "seq":    142,
  "ts":     1722000000000,
  "fs_ppg": 200,
  "fs_max": 400,
  "ppg":    [52341, 52400, 52389],
  "red":    [18200, 18250, 18230],
  "ir":     [94100, 94200, 94150],
  "bpm":    76.3,
  "spo2":   98.1
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `id` | string | `DEVICE_ID` dari config.h - harus sudah di-pair ke akun |
| `key` | string | `DEVICE_INGEST_KEY` dari .env server |
| `seq` | int | Nomor urut batch (untuk deteksi packet loss) |
| `ts` | int | Unix timestamp milliseconds |
| `fs_ppg` | float | Sample rate sinyal hijau SEN0203 (Hz), biasanya 200 |
| `fs_max` | float | Sample rate RED/IR MAX30102 (Hz), biasanya 400 |
| `ppg` | int[] | Sinyal hijau mentah dari SEN0203 |
| `red` | int[] | Sinyal merah mentah dari MAX30102 |
| `ir` | int[] | Sinyal infrared mentah dari MAX30102 |
| `bpm` | float | BPM yang sudah dihitung di firmware (opsional) |
| `spo2` | float | SpO2 dari MAX30102 (opsional) |

**Response:**
```json
{ "ok": true, "seq": 142 }
```

Pipeline server setelah menerima batch: PPG → Pulse Wave Analysis (filter Butterworth 0.5–12 Hz, ekstrak 23+ fitur morfologi) → estimasi vital MLP → prediksi stroke XGBoost → simpan ke DB → kirim FCM jika risiko HIGH.

---

## Untuk Mobile App (Flutter)

### 1. Autentikasi

#### Register
```
POST /auth/register
```
```json
{
  "email":    "user@example.com",
  "phone":    "08123456789",
  "password": "rahasia123"
}
```
`email` atau `phone` isi salah satu, boleh keduanya. Langsung aktif tanpa verifikasi email.

**Response:**
```json
{
  "access_token": "eyJ...",
  "user_id":      "a1b2c3d4"
}
```

#### Login
```
POST /auth/login
```
```json
{
  "identifier": "user@example.com",
  "password":   "rahasia123"
}
```
`identifier` bisa email atau nomor HP.

#### Info User Aktif
```
GET /auth/me
Authorization: Bearer <token>
```

---

### 2. Manajemen Profil Lansia

Satu akun bisa punya banyak profil (untuk beberapa anggota keluarga yang dipantau).

#### Buat Profil Baru
```
POST /profiles
Authorization: Bearer <token>
```
```json
{
  "name":             "Mama",
  "birthday":         "1955-03-12",
  "gender":           "F",
  "hypertension":     false,
  "heart_disease":    false,
  "ever_married":     true,
  "work_type":        "Self-employed",
  "residence_type":   "Urban",
  "smoking_status":   "never smoked"
}
```

`smoking_status`: `"never smoked"`, `"formerly smoked"`, `"smokes"`, atau `"Unknown"`

#### Daftar Semua Profil
```
GET /profiles
Authorization: Bearer <token>
```

#### Profil Aktif (yang sedang dipantau)
```
GET /profiles/active
Authorization: Bearer <token>
```
404 jika belum ada profil → arahkan ke form isi profil.

#### Ganti Profil Aktif
```
POST /profiles/{profile_id}/select
Authorization: Bearer <token>
```

#### Update Profil
```
PUT /profiles/{profile_id}
Authorization: Bearer <token>
```

---

### 3. Pairing Perangkat

Setelah smartband dirakit, `DEVICE_ID` dari config.h harus di-pair ke akun agar data ingest diarahkan ke profil yang benar.

```
POST /device/pair
Authorization: Bearer <token>
```
```json
{ "device_key": "antaraga-001" }
```

#### Cek Status Pairing
```
GET /device/status
Authorization: Bearer <token>
```
```json
{ "paired": true, "device_key": "antaraga-001" }
```

---

### 4. Data Vital & Prediksi

#### Vital Terbaru + Skor Risiko
```
GET /vitals/latest
Authorization: Bearer <token>
```
```json
{
  "systolic_bp":         128,
  "diastolic_bp":        82,
  "blood_glucose_mg_dl": 110.5,
  "heart_rate_bpm":      74.2,
  "spo2_percent":        98.0,
  "stroke_risk_score":   0.18,
  "risk_level":          "LOW",
  "recorded_at":         "2026-07-29T10:30:00Z"
}
```

#### Riwayat Vital
```
GET /vitals/history?limit=50&offset=0
Authorization: Bearer <token>
```

#### Prediksi Manual (tanpa firmware)
```
POST /predict/stroke-risk
Authorization: Bearer <token>
```
```json
{
  "systolic_bp":         130,
  "diastolic_bp":        85,
  "blood_glucose_mg_dl": 115.0,
  "heart_rate_bpm":      78,
  "spo2_percent":        97.5
}
```

**Response:**
```json
{
  "risk_score": 0.23,
  "risk_level": "LOW",
  "threshold":  0.705,
  "latency_ms": 12.4
}
```

`risk_level` bisa `LOW` atau `HIGH`. HIGH memicu push notification FCM ke semua device yang terdaftar di akun ini.

---

### 5. Penilaian ABCD2

Digunakan setelah episode TIA untuk menilai risiko stroke penuh dalam 2, 7, dan 90 hari.

```
POST /assessment/abcd2
Authorization: Bearer <token>
```
```json
{
  "age_gte_60":        true,
  "bp_gte_140_90":     true,
  "clinical_features": "unilateral_weakness",
  "duration_minutes":  65,
  "diabetes":          false
}
```

`clinical_features`: `"speech_only"`, `"unilateral_weakness"`, atau `"other"`

**Response:**
```json
{
  "score":          5,
  "risk_2d":        "High",
  "risk_7d":        "High",
  "risk_90d":       "High",
  "recommendation": "Rujuk segera ke IGD untuk evaluasi stroke"
}
```

---

### 6. Push Notification (FCM)

Daftarkan FCM token agar app menerima push notification saat skor risiko HIGH.

```
POST /device/register-token
Authorization: Bearer <token>
```
```json
{ "fcm_token": "dJe8K..." }
```

Panggil setiap kali app mendapat FCM token baru (biasanya saat pertama buka app atau token refresh).

---

### 7. Estimasi Vital dari PPG *(coming soon)*

Endpoint sudah ada tapi mengembalikan `503` sampai model MLP selesai dilatih dengan data kalibrasi nyata dari prototipe fisik.

```
POST /estimate/vitals-from-ppg
Authorization: Bearer <token>
```
```json
{
  "fs_hz":    200,
  "green":    [52341, 52400, 52389],
  "red":      [18200, 18250, 18230],
  "infrared": [94100, 94200, 94150]
}
```

---

### 8. Riwayat Log Prediksi

```
GET /logs?limit=20
Authorization: Bearer <token>
```

---

## Fitur di Web (`antaraga.web.id`)

| URL | Keterangan |
|---|---|
| `/` | Landing page produk - cara kerja, fitur, metrik model AI, 3D device visualization |
| `/dashboard` | Monitoring real-time - sinyal PPG mentah & setelah filter, BPM, vital, gauge risiko stroke. Update setiap detik dari ingest firmware terakhir |
| `/docs` | Swagger UI - dokumentasi interaktif, bisa langsung coba semua endpoint dari browser |
| `/health` | Health check server |

### Dashboard (`/dashboard`)

Diakses lewat browser tanpa login. Menampilkan:
- Grafik sinyal PPG hijau, merah, IR secara real-time
- Sinyal setelah bandpass filter (0.5–12 Hz Butterworth orde 4)
- BPM dari Welch PSD (lebih akurat dari peak counting)
- Estimasi tekanan darah dan gula darah dari MLP (jika model tersedia)
- Gauge risiko stroke 0–1 dari XGBoost (threshold 0.705)
- Timestamp ingest terakhir dari firmware

---

## Setup Lokal

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit sesuai kebutuhan
python3 model/train.py          # latih model XGBoost (sekali saja)
python3 -m uvicorn api.main:app --reload --port 8000
```

Buka `http://localhost:8000` untuk homepage, `/docs` untuk Swagger, `/dashboard` untuk monitoring.

### Variabel `.env` Penting

| Variabel | Keterangan |
|---|---|
| `DATABASE_URL` | `sqlite:///./antaraga.db` lokal · `sqlite:////app/data/antaraga.db` di Docker |
| `DEV_MODE` | `true` = auth dilewati + simulator jalan. **Wajib `false` di production** |
| `JWT_SECRET` | Secret untuk sign access token. Wajib diganti sebelum deploy |
| `DEVICE_INGEST_KEY` | Harus cocok dengan `CLOUD_API_KEY` di firmware |
| `FCM_SERVICE_ACCOUNT_PATH` | Path ke `serviceAccountKey.json` Firebase. Kosong = FCM dinonaktifkan |

---

## Deploy (VPS + Docker + GitHub Actions)

Setup pertama kali: jalankan [`scripts/vps_first_setup.sh`](scripts/vps_first_setup.sh) di VPS.

CI/CD otomatis: setiap `push` ke `main` pada path `api/**`, `model/**`, `Dockerfile`, dll. akan trigger deploy via SSH. Lihat [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

**GitHub Secrets yang harus diset:**

| Secret | Nilai |
|---|---|
| `VPS_HOST` | IP VPS |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | Private key SSH |
| `VPS_PORT` | `22` |
| `VPS_DEPLOY_PATH` | `/root/antaraga/antaraga-stroke-prediction-model` |

Konfigurasi nginx: [`scripts/nginx_antaraga.conf`](scripts/nginx_antaraga.conf)

---

## Model AI

| Model | File artifact | Status |
|---|---|---|
| XGBoost stroke risk | `model/artifacts/stroke_risk_model.joblib` | ✅ AUC-ROC 0.823 |
| MLP vital dari PPG | `model/artifacts/ppg_vitals_model.joblib` | ⏳ Menunggu data kalibrasi fisik |

```bash
python3 model/train.py            # latih ulang XGBoost
python3 -m model.train_ppg_vitals # latih MLP (butuh data/calibration/*.csv)
```
