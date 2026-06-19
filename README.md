# ANTARAGA — Stroke Risk Model & API

Backend untuk aplikasi mobile ANTARAGA: model machine learning untuk estimasi
risiko stroke iskemik + skoring ABCD2, dibungkus jadi API (FastAPI) yang
dipanggil dari app Flutter, plus dashboard internal untuk testing model dan
melihat log prediksi.

## Struktur Folder

```
model/        Training script, logika ABCD2, dan artifact model terlatih
api/          FastAPI app (endpoint yang dipanggil dari Flutter)
dashboard/    Dashboard Streamlit untuk testing & lihat log
notebooks/    Notebook eksplorasi data (EDA) lama, bukan bagian dari sistem produksi
```

## 1. Setup Awal

Butuh Python 3.11+ (disarankan pakai virtual environment).

```bash
cd stroke-prediction-model
python3 -m venv .venv && source .venv/bin/activate   # opsional tapi disarankan
pip install -r requirements.txt
cp .env.example .env   # lalu sesuaikan isinya, lihat penjelasan di bawah
```

### Isi `.env`

| Variabel | Default | Keterangan |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./antaraga.db` | Satu database untuk semuanya: users, profiles, dan log prediksi. SQLite lokal sudah cukup; ganti ke Postgres kalau perlu skala lebih besar. |
| `DEV_MODE` | `true` | `true` = simulator hardware otomatis jalan + endpoint bisa dites tanpa token (dianggap `dev-user`). `false` = wajib kirim Bearer token dari `/auth/login`, simulator mati. **Set `false` sebelum deploy ke production.** |
| `JWT_SECRET` | (insecure default) | Secret untuk menandatangani access token kita sendiri (bukan dari pihak ketiga). Generate dengan `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`. **Wajib diganti sebelum production** — siapa pun yang tahu ini bisa membuat token palsu untuk user manapun. |
| `JWT_EXPIRE_DAYS` | `30` | Berapa lama access token berlaku sebelum user harus login ulang. |
| `SIMULATOR_INTERVAL_SECONDS` | `20` | Seberapa sering simulator hardware bikin data palsu saat `DEV_MODE=true`. |

## 2. Latih Model

```bash
python3 model/train.py
```

Script ini akan:
- Load `healthcare-dataset-stroke-data.csv`
- Coba 2 algoritma (HistGradientBoosting & XGBoost) dengan hyperparameter
  tuning + 5-fold cross-validation, pilih yang terbaik
- Simpan model terlatih ke `model/artifacts/stroke_risk_model.joblib`
- Simpan ringkasan metrik ke `model/artifacts/metrics.json`

Jalankan ulang **hanya** kalau dataset, daftar fitur, atau kode training
diubah — tidak perlu setiap hari. API dan dashboard akan otomatis memuat
artifact yang sudah tersimpan tanpa perlu training ulang.

## 3. Jalankan API

```bash
python3 -m uvicorn api.main:app --reload --port 8000
```

### Cara lain: API + ngrok bersamaan (biar tidak perlu cek-cek IP LAN)

```bash
./scripts/dev.sh
```

Script ini menjalankan `uvicorn` **dan** `ngrok` sekaligus, lalu otomatis
mengisi `API_BASE_URL_DEV` di `.env` app Flutter (`../antaraga/.env`) dengan
URL ngrok yang baru didapat. Keuntungannya dibanding IP LAN manual:
- Device fisik/emulator tidak perlu satu WiFi dengan komputer — ngrok URL
  bisa diakses dari internet manapun.
- Tidak perlu beda config untuk Android emulator (`10.0.2.2`) vs device fisik
  vs iOS simulator — satu URL ngrok buat semua.
- Setelah script ini jalan, cukup **hot-restart** (bukan hot-reload) app
  Flutter supaya `.env` yang baru terbaca.

Butuh `ngrok` terpasang dan sudah login (`brew install ngrok` lalu
`ngrok config add-authtoken <token>` dari dashboard ngrok, sekali saja).
URL ngrok gratis berubah setiap restart — itu sebabnya di-auto-update,
bukan ditulis manual.

Ctrl+C di script ini akan mematikan API dan ngrok sama-sama.

- Dokumentasi interaktif (Swagger): http://localhost:8000/docs
- Endpoint auth (tidak butuh token):
  - `POST /auth/register` — body: `{ "email": "...", "phone": "...", "password": "..." }` (isi salah satu `email`/`phone`, boleh keduanya). Tanpa verifikasi email. Balasan: `{ "access_token", "user_id" }`.
  - `POST /auth/login` — body: `{ "identifier": "email atau no HP", "password": "..." }`. Balasan sama seperti register.
- Endpoint lain (semua butuh header `Authorization: Bearer <access_token>` kecuali `DEV_MODE=true`):
  - `GET /auth/me` — info user yang login
  - `POST /profile` — upsert profil lansia yang dipantau (body sama dengan `UserProfile.toJson()` di app Flutter, minus `id`)
  - `GET /profile` — ambil profil yang sudah disimpan
  - `POST /predict/stroke-risk` — body **cuma vital** (`VitalData.toJson()`), profil diambil otomatis dari yang sudah disimpan lewat `POST /profile`
  - `POST /assessment/abcd2` — body sama persis dengan `AssessmentResult.toJson()`
  - `POST /estimate/vitals-from-ppg` — estimasi tekanan darah & gula darah dari sinyal PPG mentah. **503** sampai model dilatih (lihat bagian 3b).
  - `GET /logs` — riwayat prediksi terakhir
  - `GET /health` — cek server hidup (tidak butuh token)

Auth ini murni buatan sendiri (password di-hash dengan bcrypt, token JWT
ditandatangani dengan `JWT_SECRET` kita sendiri) — tidak ada Supabase Auth
atau provider pihak ketiga lain yang dilibatkan. Semua data (users, profiles,
log prediksi) hidup di satu database yang sama (`DATABASE_URL`).

### Mode Development (`DEV_MODE=true`)

- Endpoint bisa dipanggil **tanpa** header `Authorization` (otomatis dianggap
  `dev-user`) — supaya gampang dites lewat curl/dashboard tanpa perlu login.
- Background simulator (`api/simulator.py`) otomatis jalan: setiap
  `SIMULATOR_INTERVAL_SECONDS`, dia berpura-pura jadi smartband yang baru
  selesai membaca vital 2 user demo (`dev-user-budi`, `dev-user-siti`),
  lempar ke model, dan catat hasilnya ke log — supaya kelihatan seperti ada
  hardware asli yang terus mengirim data, tanpa perlu alat fisik atau app
  Flutter menyala. Cek hasilnya lewat tab **Log Riwayat** di dashboard atau
  `GET /logs`.
- **Matikan (`DEV_MODE=false`) sebelum deploy ke production** — kalau tidak,
  siapapun bisa memanggil API tanpa token.

## 3b. Pipeline PPG -> Vitals (Tekanan Darah & Gula Darah) — belum dilatih

Sesuai proposal, tekanan darah dan gula darah tidak dipakai langsung dari
pembacaan mentah hardware — keduanya harus lewat estimasi MLP dari sinyal
PPG dulu (mirip pendekatan Gusti et al., 2025, tapi mereka cuma menutupi gula
darah/kolesterol/asam urat, bukan tekanan darah). Detak jantung TIDAK lewat
jalur ini — itu langsung dihitung dari deteksi puncak sinyal PPG
(`model/ppg_features.py`), tidak perlu model.

Status saat ini: **pipeline-nya sudah jadi, modelnya belum dilatih** —
sengaja, karena belum ada data kalibrasi asli dari prototipe ANTARAGA.
Bagian-bagiannya:

- `model/ppg_features.py` — ekstraksi fitur Pulse Wave Analysis (filter
  bandpass, deteksi pulsa, amplitude/crest time/lebar pulsa per channel
  warna, rasio antar-channel). Tidak ada parameter yang dilatih, jadi sudah
  bisa dipakai & diuji sekarang dengan sinyal sintetis.
- `model/train_ppg_vitals.py` — script training `MLPRegressor` multi-output
  (sistolik, diastolik, gula darah). **Akan berhenti dengan pesan jelas**
  kalau `data/calibration/calibration_data.csv` belum ada — lihat
  `data/calibration/README.md` untuk format kolom yang diharapkan saat
  pengujian alat fisik nanti.
- `data/external_reference/` — 30 baris data Tabel 2 dari jurnal Gusti et
  al. (2025) untuk *sanity-check saja*, BUKAN dataset training (beda
  hardware, populasi, dan tidak ada data tekanan darah sama sekali — lihat
  README di folder itu untuk alasan lengkapnya).
- `POST /estimate/vitals-from-ppg` — endpoint sudah ada di API, tapi
  mengembalikan **503** sampai `model/artifacts/ppg_vitals_model.joblib`
  ada (hasil training di atas). Body: `{ "fs_hz": ..., "green": [...], "red": [...], "infrared": [...] }`
  (isi minimal satu channel).

Begitu prototipe fisik selesai dan tahap "Pengujian Alat" mengumpulkan data
kalibrasi nyata (PPG + ground truth dari tensimeter/alat gula darah), jalankan:

```bash
python3 -m model.train_ppg_vitals
```

## 4. Jalankan Dashboard Testing

```bash
streamlit run dashboard/app.py
```

Otomatis terbuka di browser (http://localhost:8501). Dashboard ini membaca
model & log langsung dari disk, **tidak perlu** API menyala bersamaan.

3 tab yang tersedia:
- **Coba Prediksi** — form manual untuk uji model risiko stroke & skor ABCD2
- **Metrics Model** — AUC, F1, confusion matrix, feature importance dari
  training terakhir
- **Log Riwayat** — semua prediksi yang pernah dibuat (dari dashboard maupun
  dari API)

## Troubleshooting

- **`FileNotFoundError: Model artifact not found`** → jalankan `python3 model/train.py` dulu.
- **Port sudah dipakai** (`address already in use`) → cari proses lama lalu matikan:
  ```bash
  lsof -ti:8000 | xargs kill -9   # untuk API
  lsof -ti:8501 | xargs kill -9   # untuk dashboard
  ```
- **Mau reset log lokal** → hapus file `antaraga.db` di root project, akan
  otomatis dibuat ulang kosong saat API/dashboard jalan lagi.
