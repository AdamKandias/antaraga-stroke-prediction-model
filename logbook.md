# LOGBOOK KEGIATAN HARIAN
## PKM-KC: ANTARAGA — Smartband Deteksi Risiko Stroke Berbasis PPG dan Kecerdasan Buatan

| | |
|---|---|
| **Nama** | Adam Kandias |
| **Peran dalam Tim** | Software Developer · AI/ML Engineer · UI/UX Designer · Cloud Engineer |
| **Periode** | 23 Mei 2026 — 24 September 2026 |
| **Target Jam/Minggu** | 900 menit (15 jam) |
| **Hari Kerja** | Rabu · Kamis · Jumat · Sabtu · Minggu |
| **Durasi per Hari** | 180 menit (3 jam) |

---

> **Catatan Format Logbook**
> Setiap entri berisi:
> - **Kegiatan** — penjelasan detail pekerjaan yang dilakukan
> - **Hasil** — output konkret yang dihasilkan
> - 📸 **Bukti** — deskripsi foto/screenshot yang perlu dilampirkan sebagai bukti

---

## FASE 1 — PERENCANAAN & ARSITEKTUR SISTEM
*(23 Mei — 7 Juni 2026)*

---

### Minggu ke-1 (Parsial) — 23–24 Mei 2026

---

**Sabtu, 23 Mei 2026 — 180 menit**

**Kegiatan:**
Hari pertama pengerjaan PKM-KC ANTARAGA. Melakukan studi literatur tentang sistem deteksi risiko stroke berbasis wearable device dan membuat desain arsitektur sistem secara keseluruhan. Menentukan komponen utama: smartband (XIAO ESP32-S3), backend server (FastAPI/Python), aplikasi mobile (Flutter), dan model AI (XGBoost + MLP).

Arsitektur yang dirancang:
- Layer 1: Hardware (sensor PPG MAX30102 + SEN0203 pada XIAO ESP32-S3)
- Layer 2: Backend (FastAPI, SQLAlchemy, SQLite)
- Layer 3: AI/ML (XGBoost untuk deteksi risiko stroke, MLP untuk estimasi vital dari PPG)
- Layer 4: Mobile App (Flutter — monitoring real-time)
- Layer 5: Cloud/Notifikasi (Firebase Cloud Messaging)

**Hasil:**
- Diagram arsitektur sistem ANTARAGA (end-to-end)
- Daftar teknologi yang akan digunakan beserta justifikasi pilihan
- Pembagian tugas antar anggota tim

📸 **Bukti yang perlu dilampirkan:**
- Foto diagram arsitektur sistem yang sudah digambar (di kertas/whiteboard atau di aplikasi draw.io/Figma)
- Screenshot dokumen perencanaan teknologi (Google Docs/Notion)
- Foto rapat tim hari pertama

---

**Minggu, 24 Mei 2026 — 180 menit**

**Kegiatan:**
Setup lingkungan pengembangan di komputer lokal. Instalasi seluruh tools yang dibutuhkan: Python 3.12, Flutter SDK, Git, VSCode beserta extensions (Python, Flutter, Dart). Membuat repository GitHub untuk project dan menyusun struktur folder awal.

Struktur repository yang dibuat:
```
antaraga/          ← Flutter mobile app
stroke-prediction-model/
  api/             ← FastAPI backend
  model/           ← AI/ML models
  data/            ← dataset
  scripts/         ← utility scripts
```

**Hasil:**
- Repository GitHub terbuat dan terhubung ke lokal
- Lingkungan development siap (Python venv, Flutter doctor clean)
- File `.gitignore` dan `README.md` awal

📸 **Bukti yang perlu dilampirkan:**
- Screenshot GitHub repository yang baru dibuat
- Screenshot terminal: `flutter doctor` menampilkan semua ✓
- Screenshot terminal: `python --version` dan `pip list` environment
- Screenshot struktur folder project di VSCode Explorer

---

### Minggu ke-2 — 27–31 Mei 2026

---

**Rabu, 27 Mei 2026 — 180 menit**

**Kegiatan:**
Merancang skema database sistem ANTARAGA. Mengidentifikasi entitas yang dibutuhkan: User (akun keluarga), Profile (data lansia yang dipantau), VitalReading (pembacaan sensor), PredictionLog (log prediksi AI). Membuat Entity-Relationship Diagram (ERD) dan mendefinisikan semua kolom beserta tipe datanya menggunakan SQLAlchemy ORM.

Tabel yang dirancang:
- `users` — akun login (email/phone, password hash, FCM token)
- `profiles` — data lansia (nama, gender, tanggal lahir, kondisi medis)
- `vital_readings` — tekanan darah, detak jantung, SpO2, gula darah
- `prediction_logs` — log setiap prediksi AI (input, output, latency)

**Hasil:**
- ERD lengkap dengan relasi antar tabel
- File `api/models_db.py` dengan semua model SQLAlchemy

📸 **Bukti yang perlu dilampirkan:**
- Screenshot ERD yang sudah dibuat (draw.io atau dbdiagram.io)
- Screenshot kode `models_db.py` di VSCode
- Screenshot terminal: `python -c "from api.models_db import *; print('OK')"` berhasil

---

**Kamis, 28 Mei 2026 — 180 menit**

**Kegiatan:**
Membuat fondasi project FastAPI: struktur modul, konfigurasi environment (`.env`), koneksi database SQLite menggunakan SQLAlchemy, dan endpoint dasar `/health`. Menyusun file `config.py` untuk manajemen environment variable (DATABASE_URL, JWT_SECRET, DEV_MODE).

**Hasil:**
- File `api/main.py` — aplikasi FastAPI berjalan
- File `api/config.py` — konfigurasi terpusat
- File `api/database.py` — session factory SQLAlchemy
- Endpoint `GET /health` mengembalikan `{"status": "ok"}`
- Server bisa dijalankan dengan `uvicorn api.main:app --reload`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: server uvicorn berjalan tanpa error
- Screenshot browser: `http://localhost:8000/docs` menampilkan Swagger UI
- Screenshot browser: `http://localhost:8000/health` menampilkan JSON response
- Screenshot kode `main.py` dan `config.py` di VSCode

---

**Jumat, 29 Mei 2026 — 180 menit**

**Kegiatan:**
Implementasi sistem autentikasi JWT (JSON Web Token) untuk keamanan API. Menggunakan library `bcrypt` untuk hashing password dan `PyJWT` untuk membuat/memverifikasi token. Membuat endpoint `POST /auth/register` dan `POST /auth/login`. Token yang dihasilkan memiliki masa berlaku 30 hari dan menyimpan `user_id` sebagai klaim `sub`.

**Hasil:**
- File `api/auth.py` — fungsi create/verify token + dependency `get_current_user_id`
- File `api/security.py` — hash_password dan verify_password
- Endpoint `/auth/register` — daftar akun baru
- Endpoint `/auth/login` — login dan dapatkan access token
- Endpoint `/auth/me` — cek identitas dari token

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: endpoint `/auth/register` dan `/auth/login`
- Screenshot Postman/curl: test register berhasil → response berisi `access_token`
- Screenshot Postman/curl: test login dengan credential yang salah → 401 Unauthorized
- Screenshot kode `auth.py` di VSCode

---

**Sabtu, 30 Mei 2026 — 180 menit**

**Kegiatan:**
Membuat endpoint manajemen profil lansia. Satu akun bisa memiliki beberapa profil (multi-lansia). Mengimplementasikan: `GET /profiles`, `POST /profiles`, `GET /profiles/{id}`, `PUT /profiles/{id}`, `GET /profiles/active` (profil terakhir yang dilihat). Membuat `api/schemas.py` dengan model Pydantic untuk validasi request/response.

Data profil yang tersimpan: nama, gender, tanggal lahir, berat badan, tinggi badan, status merokok, riwayat penyakit jantung, diabetes, tipe tempat tinggal.

**Hasil:**
- File `api/schemas.py` — semua schema Pydantic
- Endpoint CRUD profil lengkap
- Validasi input (gender enum, birthday format, dll)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: section "profiles" dengan semua endpoint
- Screenshot Postman: test `POST /profiles` berhasil → profil tersimpan
- Screenshot database viewer (DB Browser for SQLite) menampilkan tabel `profiles`
- Screenshot kode `schemas.py` di VSCode

---

**Minggu, 31 Mei 2026 — 180 menit**

**Kegiatan:**
Studi dataset untuk model AI deteksi stroke. Mengunduh dataset Stroke Prediction dari Kaggle (5110 records, 11 fitur). Melakukan Exploratory Data Analysis (EDA): distribusi label (stroke vs non-stroke), statistik deskriptif tiap fitur, cek missing value, visualisasi. Menemukan ketidakseimbangan kelas yang signifikan: ~95% non-stroke, ~5% stroke.

**Hasil:**
- Notebook EDA lengkap dengan visualisasi
- Pemahaman tentang class imbalance → akan digunakan `scale_pos_weight` di XGBoost
- Daftar fitur yang relevan: usia, tekanan darah, gula darah, BMI, hipertensi, penyakit jantung, status merokok, gender, tipe tempat tinggal

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook Jupyter: visualisasi distribusi kelas (pie chart/bar chart)
- Screenshot notebook: heatmap korelasi fitur
- Screenshot notebook: statistik deskriptif (df.describe())
- Screenshot folder dataset di file explorer

---

### Minggu ke-3 — 3–7 Juni 2026

---

**Rabu, 3 Juni 2026 — 180 menit**

**Kegiatan:**
Preprocessing data untuk training model XGBoost. Tahapan: (1) isi missing value kolom BMI dengan median, (2) encoding kategorikal (gender, smoking_status, ever_married, work_type, Residence_type) menggunakan Label Encoding, (3) split data train/test (80:20, stratified by label), (4) simpan mapping encoding untuk dipakai saat inference.

**Hasil:**
- Script `model/preprocess.py` — fungsi preprocessing reproducible
- Data train dan test siap (X_train, X_test, y_train, y_test)
- Mapping label encoding tersimpan

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode preprocessing di VSCode
- Screenshot terminal: output info shape data `X_train.shape`, `X_test.shape`
- Screenshot notebook: distribusi data sebelum dan sesudah preprocessing

---

**Kamis, 4 Juni 2026 — 180 menit**

**Kegiatan:**
Training model XGBoost pertama kali (baseline). Menggunakan `XGBClassifier` dengan parameter awal: `n_estimators=100`, `max_depth=4`, `learning_rate=0.1`, `scale_pos_weight=19.56` (rasio kelas negatif/positif). Evaluasi menggunakan AUC-ROC dan Average Precision karena dataset sangat imbalanced.

**Hasil:**
- Model XGBoost baseline terlatih
- AUC-ROC baseline: ~0.79
- Pemahaman bahwa threshold default 0.5 tidak optimal untuk kasus imbalanced

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: output training XGBoost
- Screenshot notebook: kurva AUC-ROC baseline
- Screenshot kode training di VSCode
- Screenshot: nilai metrik (classification report)

---

**Jumat, 5 Juni 2026 — 180 menit**

**Kegiatan:**
Hyperparameter tuning model XGBoost menggunakan grid search manual. Mencoba kombinasi: `learning_rate` (0.03, 0.05, 0.1), `max_depth` (3, 4, 5), `min_child_weight` (3, 5, 7), `reg_lambda` (0.5, 1.0, 2.0). Memilih kombinasi terbaik berdasarkan AUC-PR (Area Under Precision-Recall Curve) karena lebih relevan untuk dataset imbalanced.

**Hasil:**
- Parameter terbaik: `learning_rate=0.03`, `max_depth=4`, `min_child_weight=5`, `reg_lambda=1.0`
- AUC-ROC meningkat ke ~0.82

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook: tabel hasil grid search
- Screenshot grafik: perbandingan AUC-ROC setiap kombinasi parameter
- Screenshot kode hyperparameter tuning

---

**Sabtu, 6 Juni 2026 — 180 menit**

**Kegiatan:**
Optimasi threshold klasifikasi XGBoost. Threshold default (0.5) menghasilkan recall yang sangat rendah untuk kelas stroke. Menganalisis kurva Precision-Recall dan memilih threshold optimal yang menyeimbangkan sensitivitas dengan false positive rate yang masih diterima. Threshold optimal ditemukan: **0.705** dengan AUC-ROC final: **0.823**.

**Hasil:**
- Threshold optimal: 0.705
- Recall pada kelas stroke: 49.3%
- Model disimpan sebagai `model/artifacts/stroke_model.joblib`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook: kurva Precision-Recall dengan threshold yang dipilih ditandai
- Screenshot notebook: confusion matrix pada threshold 0.705
- Screenshot terminal: `joblib.dump()` berhasil menyimpan model
- Screenshot folder `model/artifacts/` di file explorer

---

**Minggu, 7 Juni 2026 — 180 menit**

**Kegiatan:**
Integrasi model XGBoost ke dalam FastAPI backend. Membuat file `api/ml.py` yang memuat model dari artifact `.joblib` saat server pertama kali dijalankan (lazy loading). Membuat endpoint `POST /predict/stroke-risk` yang menerima data vital + profil pasien, menjalankan prediksi, dan mengembalikan probabilitas + level risiko (LOW/MEDIUM/HIGH).

**Hasil:**
- File `api/ml.py` — fungsi `predict_stroke_risk(features)`
- Endpoint `/predict/stroke-risk` aktif dan dapat dipanggil
- Response: `{probability, risk_level, threshold, model_name}`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: endpoint `/predict/stroke-risk` dengan schema input/output
- Screenshot Postman: test prediksi dengan data pasien → response berisi `risk_level: "LOW"`
- Screenshot kode `api/ml.py` di VSCode

---

## FASE 2 — UI/UX DESIGN & FLUTTER APP
*(10 Juni — 26 Juli 2026)*

---

### Minggu ke-4 — 10–14 Juni 2026

---

**Rabu, 10 Juni 2026 — 180 menit**

**Kegiatan:**
Memulai desain UI/UX aplikasi Flutter ANTARAGA menggunakan Figma. Melakukan riset competitor app (health monitoring apps: Google Fit, Samsung Health, Withings). Membuat user flow diagram dari alur penggunaan: register → buat profil → pasang smartband → monitoring real-time → dapat notifikasi. Menentukan color palette (biru medis #2A78D6 sebagai primary, background gelap/terang).

**Hasil:**
- User flow diagram lengkap di Figma
- Color palette dan typography system
- Komponen dasar: tombol, kartu, input field

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Figma: user flow diagram
- Screenshot Figma: color palette dan typography system
- Screenshot Figma: komponen UI library (button, card, input)

---

**Kamis, 11 Juni 2026 — 180 menit**

**Kegiatan:**
Desain wireframe dan high-fidelity mockup untuk Splash Screen dan Login/Register Screen. Mendesain animasi transisi antar halaman. Splash screen menampilkan logo ANTARAGA dengan animasi. Login screen dengan input email/nomor HP dan password, plus tombol ke register.

**Hasil:**
- Mockup Splash Screen (light + dark mode)
- Mockup Login Screen
- Mockup Register Screen
- Flow animasi: splash → login → dashboard

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Figma: mockup Splash Screen
- Screenshot Figma: mockup Login Screen (tampak penuh)
- Screenshot Figma: mockup Register Screen
- Screenshot Figma: prototype mode menampilkan transisi antar screen

---

**Jumat, 12 Juni 2026 — 180 menit**

**Kegiatan:**
Desain high-fidelity mockup Dashboard Screen — layar utama yang menampilkan data vital real-time. Merancang komponen: kartu sambutan (nama + tanggal), kartu statistik harian, kartu monitoring vital (tekanan darah, detak jantung, gula darah, SpO2), kartu risiko stroke AI, tombol assessment ABCD2.

**Hasil:**
- Mockup Dashboard Screen lengkap
- Komponen kartu vital dengan color coding (normal=hijau, waspada=kuning, bahaya=merah)
- Layout responsive untuk berbagai ukuran layar HP

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Figma: Dashboard Screen tampak penuh
- Screenshot Figma: zoom-in kartu monitoring vital
- Screenshot Figma: kartu risiko stroke dengan indikator visual
- Screenshot Figma: perbandingan tampilan normal vs risiko tinggi

---

**Sabtu, 13 Juni 2026 — 180 menit**

**Kegiatan:**
Desain Profile Form Screen (form input data lansia) dan Daily Stats Screen (grafik riwayat vital). Profile form memiliki field: nama, gender, tanggal lahir, berat badan, tinggi badan, status merokok, kondisi medis. Daily stats menampilkan grafik garis tekanan darah dan gula darah per jam.

**Hasil:**
- Mockup Profile Form Screen
- Mockup Daily Stats Screen dengan grafik
- Mockup Assessment ABCD2 Form Screen

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Figma: Profile Form Screen
- Screenshot Figma: Daily Stats Screen dengan grafik
- Screenshot Figma: ABCD2 Assessment Form Screen
- Screenshot Figma: seluruh flow di Figma (semua layar terhubung)

---

**Minggu, 14 Juni 2026 — 180 menit**

**Kegiatan:**
Setup project Flutter ANTARAGA. Membuat project baru dengan `flutter create antaraga`. Konfigurasi pubspec.yaml dengan semua dependency yang dibutuhkan: `http`, `flutter_dotenv`, `shared_preferences`, `intl`, `flutter_screenutil`, `google_fonts`. Membuat struktur folder: `lib/models`, `lib/services`, `lib/screens`, `lib/core`.

**Hasil:**
- Project Flutter berhasil dibuat dan berjalan di emulator
- Semua dependency terinstall (`flutter pub get`)
- Struktur folder modular siap
- App berjalan menampilkan layar kosong tanpa error

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: `flutter create antaraga` dan `flutter pub get` berhasil
- Screenshot emulator: aplikasi Flutter pertama kali berjalan
- Screenshot VSCode: struktur folder project Flutter
- Screenshot `pubspec.yaml` di VSCode

---

### Minggu ke-5 — 17–21 Juni 2026

---

**Rabu, 17 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi tema dan routing aplikasi Flutter. Membuat sistem tema (light/dark mode) menggunakan `AppColors` class dengan warna-warna dari desain Figma. Setup routing: splash → login → dashboard. Implementasi Splash Screen dengan animasi logo. Konfigurasi `flutter_screenutil` untuk responsive UI.

**Hasil:**
- File `lib/core/theme/app_colors.dart` — semua konstanta warna
- File `lib/main.dart` — MaterialApp dengan tema dan routing
- Splash Screen berfungsi dengan animasi, auto-navigate ke login setelah 2 detik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Splash Screen dengan logo ANTARAGA
- Screenshot kode `app_colors.dart` di VSCode
- Screenshot kode `main.dart` (routing setup)
- Video pendek (GIF/MP4): animasi splash screen

---

**Kamis, 18 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi Login Screen dan Register Screen di Flutter. Membuat form dengan validasi input (email format, password minimum 6 karakter). Membuat `AuthService` yang menyimpan JWT token ke `SharedPreferences`. Membuat `ApiService` — centralized HTTP client yang membaca `API_BASE_URL` dari `.env`.

**Hasil:**
- File `lib/screens/login_screen.dart`
- File `lib/services/auth_service.dart` — login, logout, token management
- File `lib/services/api_service.dart` — HTTP client ke backend

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Login Screen tampak di HP
- Screenshot emulator: Register Screen tampak di HP
- Screenshot emulator: validasi error saat password kurang dari 6 karakter
- Screenshot kode `auth_service.dart` di VSCode

---

**Jumat, 19 Juni 2026 — 180 menit**

**Kegiatan:**
Membuat model data Flutter: `UserProfile` (data lansia) dan `VitalData` (pembacaan sensor). Implementasi `fromJson()` dan `toJson()` untuk serialisasi/deserialisasi dari API. Integrasi Profile Form Screen dengan API — memanggil `POST /profiles` saat user submit form pertama kali.

**Hasil:**
- File `lib/models/user_profile.dart` — model profil dengan fromJson/toJson
- File `lib/models/vital_data.dart` — model data vital
- Profile Form terhubung ke API, data tersimpan di database backend

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Profile Form Screen diisi dengan data lansia
- Screenshot emulator: setelah submit → navigasi ke dashboard
- Screenshot DB Browser (SQLite): tabel `profiles` berisi data yang baru diinput
- Screenshot Postman: GET /profiles menampilkan profil yang sudah dibuat

---

**Sabtu, 20 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi Dashboard Screen utama di Flutter. Membuat kartu-kartu vital: tekanan darah sistolik/diastolik, detak jantung, SpO2, gula darah. Setiap kartu menampilkan nilai, satuan, dan indikator status (normal/waspada/bahaya) berdasarkan range nilai normal medis. Implementasi `VitalRanges` class untuk logika status.

**Hasil:**
- File `lib/screens/dashboard_screen.dart` — screen utama
- File `lib/core/constants/vital_ranges.dart` — range normal tiap vital
- Dashboard menampilkan data vital dengan color-coded status

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Dashboard Screen tampak penuh
- Screenshot emulator: zoom-in kartu tekanan darah
- Screenshot emulator: kartu dengan status "Waspada" (warna kuning)
- Screenshot kode `vital_ranges.dart` di VSCode

---

**Minggu, 21 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi polling data vital dari backend setiap 5 detik di Dashboard. Membuat method `ApiService.fetchLatestVital()` yang memanggil `GET /vitals/latest`. Mengimplementasikan logic: jika timestamp data baru berbeda dari yang terakhir ditampilkan, update UI dengan animasi. Menambahkan endpoint `GET /vitals/latest` di backend.

**Hasil:**
- Dashboard auto-refresh vital setiap 5 detik
- Endpoint `GET /vitals/latest` di backend
- Endpoint `GET /vitals/history` untuk riwayat harian

📸 **Bukti yang perlu dilampirkan:**
- Video pendek: dashboard menampilkan data yang berubah setiap beberapa detik
- Screenshot terminal backend: log `GET /vitals/latest` yang berulang tiap 5 detik
- Screenshot Swagger UI: endpoint `/vitals/latest` dengan response schema

---

### Minggu ke-6 — 24–28 Juni 2026

---

**Rabu, 24 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi ABCD2 Scoring System di backend. ABCD2 adalah skor klinis untuk menilai risiko TIA (Transient Ischemic Attack) yang berkembang menjadi stroke dalam 2, 7, dan 90 hari. Membuat file `model/abcd2.py` dengan logika scoring berdasarkan Johnston et al. (2007): usia, tekanan darah, gejala klinis, durasi TIA, diabetes.

**Hasil:**
- File `model/abcd2.py` — implementasi ABCD2 (skor 0-7)
- Endpoint `POST /assessment/abcd2` di backend
- Response: skor, urgensi, rekomendasi, dan persentase risiko 2/7/90 hari

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `abcd2.py` di VSCode
- Screenshot Swagger UI: endpoint `/assessment/abcd2`
- Screenshot Postman: test ABCD2 dengan skor tinggi → respons "SEGERA KE UGD"
- Screenshot: jurnal Johnston et al. 2007 sebagai referensi

---

**Kamis, 25 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi Assessment Form Screen di Flutter untuk pengisian skor ABCD2. Form menampilkan 5 komponen: (A) Usia ≥60 tahun, (B) Tekanan darah sistolik ≥140 mmHg, (C) Gejala klinis (unilateral weakness/speech), (D) Durasi TIA, (D2) Diabetes. Hasil skor ditampilkan di kartu ringkasan dengan rekomendasi tindakan.

**Hasil:**
- File `lib/screens/assessment_form_screen.dart`
- Form ABCD2 dengan 5 pertanyaan klinis
- Halaman hasil menampilkan skor, urgensi, dan rekomendasi dokter

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Assessment Form Screen (tampak penuh)
- Screenshot emulator: hasil skor ABCD2 setelah submit
- Screenshot emulator: kartu rekomendasi "SEGERA KE UGD" untuk skor tinggi
- Screenshot kode `assessment_form_screen.dart` di VSCode

---

**Jumat, 26 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi Daily Stats Screen di Flutter — menampilkan riwayat pembacaan vital dalam sehari sebagai grafik garis. Menggunakan `fl_chart` library untuk membuat grafik interaktif. Sumbu X adalah waktu (jam), sumbu Y adalah nilai vital. Bisa scroll ke tanggal sebelumnya.

**Hasil:**
- File `lib/screens/daily_stats_screen.dart`
- Grafik riwayat tekanan darah dan gula darah per jam
- Dapat memilih tanggal via date picker

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Daily Stats Screen dengan grafik
- Screenshot emulator: grafik tekanan darah sepanjang hari
- Screenshot emulator: date picker untuk pilih tanggal historis
- Screenshot kode grafik `fl_chart` di VSCode

---

**Sabtu, 27 Juni 2026 — 180 menit**

**Kegiatan:**
Implementasi PPG Signal Processing Pipeline — modul Python untuk mengekstrak fitur morfologi dari sinyal PPG mentah. Mengimplementasikan: (1) Bandpass filter Butterworth order 3 (0.5–8 Hz) untuk isolasi gelombang jantung, (2) Peak detection (deteksi puncak sistol), (3) Ekstraksi fitur per-pulsa: amplitudo, crest time, pulse width.

**Hasil:**
- File `model/ppg_features.py` — pipeline PWA lengkap
- Fungsi `extract_pwa_features()` menghasilkan 20+ fitur morfologi
- Diuji dengan sinyal sintetis: berhasil deteksi 10+ puncak pada sinyal 10 detik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `ppg_features.py` di VSCode
- Screenshot notebook: visualisasi sinyal PPG sebelum dan sesudah bandpass filter
- Screenshot notebook: sinyal terfilter dengan peak markers
- Screenshot terminal: `python -c "from model.ppg_features import *; print('OK')"` berhasil

---

**Minggu, 28 Juni 2026 — 180 menit**

**Kegiatan:**
Merancang arsitektur MLP (Multi-Layer Perceptron) untuk estimasi vital dari sinyal PPG. MLP akan memetakan fitur morfologi PPG → [tekanan sistolik, tekanan diastolik, gula darah]. Arsitektur: input (23 fitur + usia) → hidden(16, tanh) → hidden(8, tanh) → output(3). Membuat file `model/train_ppg_vitals.py` sebagai training script yang siap dipakai saat data kalibrasi tersedia.

**Hasil:**
- File `model/train_ppg_vitals.py` — training pipeline MLP
- File `api/ml_vitals.py` — inference wrapper (menunggu artifact)
- Arsitektur MLP terdokumentasi di `alur_model.md`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `train_ppg_vitals.py` di VSCode
- Screenshot diagram arsitektur MLP (bisa di notebook atau draw.io)
- Screenshot kode `ml_vitals.py` di VSCode
- Screenshot: dokumentasi parameter MLP yang akan digunakan

---

### Minggu ke-7 — 1–5 Juli 2026

---

**Rabu, 1 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi simulator hardware di backend (`api/simulator.py`) untuk pengembangan dan testing tanpa perangkat fisik. Simulator membangkitkan data vital secara acak (dalam range normal dengan sesekali anomali), lalu memanggil pipeline prediksi stroke risk setiap 20 detik untuk semua user yang aktif. Berjalan sebagai background asyncio task saat `DEV_MODE=true`.

**Hasil:**
- File `api/simulator.py` — simulasi data sensor
- Backend otomatis menghasilkan data vital saat DEV_MODE aktif
- Dashboard Flutter menampilkan data yang berubah tanpa hardware fisik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal backend: log simulator berjalan setiap 20 detik
- Screenshot emulator Flutter: dashboard menampilkan data vital yang terus berubah
- Screenshot kode `simulator.py` di VSCode
- Screenshot: `DEV_MODE=true` di file `.env`

---

**Kamis, 2 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi logging dan monitoring prediksi AI. Setiap panggilan ke endpoint prediksi (stroke risk, ABCD2, vitals from PPG) dicatat ke tabel `prediction_logs` — termasuk input payload, output, latency, dan level risiko. Membuat endpoint `GET /logs` untuk melihat riwayat prediksi dari testing dashboard.

**Hasil:**
- Fungsi `log_prediction()` di `api/logging_utils.py`
- Semua prediksi tercatat otomatis di database
- Endpoint `GET /logs` untuk inspeksi dari luar

📸 **Bukti yang perlu dilampirkan:**
- Screenshot DB Browser: tabel `prediction_logs` dengan data
- Screenshot Postman: `GET /logs` menampilkan riwayat prediksi
- Screenshot kode `logging_utils.py` di VSCode

---

**Jumat, 3 Juli 2026 — 180 menit**

**Kegiatan:**
Setup Firebase untuk push notification. Membuat project Firebase `antaraga-563c1` di Firebase Console. Mengunduh `google-services.json` untuk Android dan mengonfigurasi Android project. Menambahkan dependency: `firebase_core: ^3.6.0`, `firebase_messaging: ^15.1.4`. Mengaktifkan Cloud Messaging di Firebase Console.

**Hasil:**
- Project Firebase `antaraga-563c1` aktif
- File `google-services.json` terpasang di `android/app/`
- File `firebase_options.dart` tergenerasi dengan `flutterfire configure`
- Flutter app berhasil initialize Firebase tanpa error

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Firebase Console: project `antaraga-563c1` dashboard
- Screenshot Firebase Console: Cloud Messaging enabled
- Screenshot terminal: `flutterfire configure` berhasil
- Screenshot kode `firebase_options.dart` tergenerasi

---

**Sabtu, 4 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi Firebase Cloud Messaging (FCM) di Flutter. Membuat `FcmService` class: (1) minta izin notifikasi dari user, (2) buat Android notification channel "antaraga_high_risk", (3) ambil FCM token dan kirim ke backend (`POST /device/register-token`), (4) handle 3 skenario notifikasi: foreground, background, killed state.

**Hasil:**
- File `lib/services/fcm_service.dart` — FCM service singleton
- Endpoint `POST /device/register-token` di backend
- Notifikasi tampil saat app di foreground (menggunakan `flutter_local_notifications`)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: dialog izin notifikasi saat app pertama dibuka
- Screenshot: push notification muncul di notification bar Android
- Screenshot Firebase Console: dapat mengirim test notification ke token device
- Screenshot kode `fcm_service.dart` di VSCode

---

**Minggu, 5 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi FCM di backend (Python). Menginstall `firebase-admin` SDK. Membuat `api/fcm.py` dengan inisialisasi Firebase Admin SDK menggunakan service account key. Membuat fungsi `send_high_risk_notification()` yang mengirim push notification dengan judul "⚠️ Risiko Stroke Tinggi Terdeteksi" beserta deeplink ke Assessment ABCD2. Mengintegrasikan trigger FCM ke simulator: setiap kali `risk_level == "HIGH"`, kirim notifikasi (dengan cooldown 5 menit).

**Hasil:**
- File `api/fcm.py` — Firebase Admin lazy init + send notification
- Cooldown system (tidak spam: max 1 notifikasi per 5 menit per user)
- Backend berhasil trigger push notification ke device Flutter

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notifikasi "Risiko Stroke Tinggi" muncul di HP Android
- Screenshot: mengetuk notifikasi → app terbuka langsung ke form ABCD2
- Screenshot Firebase Console: activity log notifikasi terkirim
- Screenshot kode `fcm.py` di VSCode

---

### Minggu ke-8 — 8–12 Juli 2026

---

**Rabu, 8 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi deeplink navigasi dari notifikasi FCM ke AssessmentFormScreen. Menggunakan `ValueNotifier<bool> openAssessmentRequest` di `FcmService` sebagai event bus. `DashboardScreen` mendengarkan notifier ini dan membuka form ABCD2 melalui `addPostFrameCallback` untuk menghindari crash saat frame sedang build. Tiga skenario dihandle: foreground, background-tap, killed-tap.

**Hasil:**
- Deeplink berfungsi di ketiga skenario (foreground, background, killed state)
- File `lib/screens/dashboard_screen.dart` — listener FCM ditambahkan

📸 **Bukti yang perlu dilampirkan:**
- Video (GIF/MP4): tap notifikasi → app langsung buka form ABCD2
- Screenshot kode listener FCM di `dashboard_screen.dart`
- Screenshot: test dari Firebase Console → kirim notif → form terbuka

---

**Kamis, 9 Juli 2026 — 180 menit**

**Kegiatan:**
Mengatasi error build Android: `flutter_local_notifications` memerlukan core library desugaring (Java 8+ API). Menambahkan konfigurasi di `android/app/build.gradle.kts`: `isCoreLibraryDesugaringEnabled = true` dan dependency `coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")`. Mengupdate `android/app/build.gradle.kts` ke `JavaVersion.VERSION_17`.

**Hasil:**
- Build Android berhasil tanpa error desugaring
- APK dapat di-install di device fisik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: `flutter build apk` berhasil (no errors)
- Screenshot: APK terinstall di HP Android
- Screenshot kode `build.gradle.kts` setelah perubahan

---

**Jumat, 10 Juli 2026 — 180 menit**

**Kegiatan:**
Mengatasi error SQLite migration: tambah kolom `fcm_token` dan `last_notified_at` ke tabel `users` yang sudah ada. SQLAlchemy `create_all()` tidak menambah kolom ke tabel yang sudah ada, jadi perlu manual SQL `ALTER TABLE`. Membuat script migrasi `scripts/migrate_db.py` untuk dijalankan sekali.

**Hasil:**
- Script `scripts/migrate_db.py` untuk migrasi database
- Database berhasil dimigrasikan dengan kolom baru
- Model `User` diperbarui di `models_db.py`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: script migrasi berjalan berhasil
- Screenshot DB Browser: tabel `users` menampilkan kolom `fcm_token` dan `last_notified_at`
- Screenshot kode migrasi di VSCode

---

**Sabtu, 11 Juli 2026 — 180 menit**

**Kegiatan:**
Setup development server dengan ngrok untuk ekspose localhost ke internet (dibutuhkan untuk testing di device fisik dan hardware). Membuat `scripts/dev.sh` yang otomatis: (1) jalankan uvicorn, (2) jalankan ngrok, (3) ambil URL ngrok, (4) update `API_BASE_URL_DEV` di `.env` Flutter, (5) tampilkan instruksi hot-restart.

**Hasil:**
- Script `scripts/dev.sh` berfungsi sepenuhnya
- URL ngrok otomatis terupdate di `.env` Flutter setiap kali dev.sh dijalankan
- Device fisik dapat terhubung ke backend local via ngrok

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: `dev.sh` berjalan, menampilkan URL ngrok
- Screenshot browser: `https://xxxx.ngrok-free.app/docs` menampilkan Swagger
- Screenshot HP Android: aplikasi Flutter terhubung ke backend via ngrok
- Screenshot kode `dev.sh` di VSCode

---

**Minggu, 12 Juli 2026 — 180 menit**

**Kegiatan:**
Pembuatan sensor monitor desktop untuk tim hardware — aplikasi Python GUI menggunakan tkinter + matplotlib. Fitur: auto-detect port serial dan baud rate, grafik real-time multi-channel yang scrolling, pause/resume, export data ke CSV dan gambar (PNG/PDF). Hardware team dapat melihat sinyal PPG secara visual tanpa Arduino IDE.

**Hasil:**
- File `scripts/sensor_monitor.py` — aplikasi GUI standalone
- Mendukung format data: `key=value`, CSV, plain comma-separated
- Export CSV menyimpan semua histori (bukan hanya yang terlihat)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: `sensor_monitor.py` berjalan menampilkan grafik sinyal PPG
- Screenshot: dropdown auto-detect COM ports
- Screenshot: grafik setelah pause (menunjukkan data terkumpul)
- Screenshot: file CSV yang berhasil diexport

---

### Minggu ke-9 — 15–19 Juli 2026

---

**Rabu, 15 Juli 2026 — 180 menit**

**Kegiatan:**
Membuat dokumentasi sistem alur data lengkap di `alur.md`. Dokumen ini menjelaskan perjalanan data dari penerimaan di backend hingga notifikasi: endpoint ingest, pipeline PWA, parameter XGBoost, hasil training, ABCD2 scoring, sampai FCM. Dilengkapi diagram alur teks dan tabel parameter model.

**Hasil:**
- File `alur.md` — dokumentasi alur sistem lengkap (800+ kata)
- Tabel parameter XGBoost beserta maknanya
- Diagram alur end-to-end sistem ANTARAGA

📸 **Bukti yang perlu dilampirkan:**
- Screenshot file `alur.md` terbuka di VSCode (preview markdown)
- Screenshot: tabel parameter XGBoost di markdown preview
- Screenshot: diagram alur di markdown preview

---

**Kamis, 16 Juli 2026 — 180 menit**

**Kegiatan:**
Membuat dokumentasi konsep algoritma AI di `alur_model.md` untuk keperluan laporan PKM. Menjelaskan: (1) MLP — forward pass, backpropagation, fungsi aktivasi tanh, regularisasi L2; (2) XGBoost — gradient boosting algorithm, histogram approximation, scale_pos_weight, semua parameter dan artinya. Dilengkapi contoh perhitungan dan perbandingan kedua model.

**Hasil:**
- File `alur_model.md` — penjelasan konsep AI yang komprehensif (1200+ kata)
- Diagram struktur MLP (16→8→3) dalam format teks
- Perbandingan tabel MLP vs XGBoost

📸 **Bukti yang perlu dilampirkan:**
- Screenshot file `alur_model.md` di VSCode preview
- Screenshot: diagram MLP (layer input → hidden → output)
- Screenshot: tabel perbandingan MLP vs XGBoost

---

**Jumat, 17 Juli 2026 — 180 menit**

**Kegiatan:**
Mengkaji firmware XIAO ESP32-S3 yang dibuat tim hardware (`Firmware/`). Memahami: dual-core FreeRTOS (Core 0 = WiFi/HTTPS, Core 1 = sensor), kontrak payload JSON yang dikirim setiap 500ms, pola LED indikator, output serial `[STAT]`. Merancang endpoint `POST /v1/ingest` untuk menerima batch data dari firmware.

**Hasil:**
- Pemahaman penuh tentang firmware payload contract
- Design endpoint `/v1/ingest` dengan schema sesuai payload firmware
- Dokumentasi koneksi firmware ↔ backend di `Firmware/README.md`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode firmware `cloud.cpp` di VSCode (payload builder)
- Screenshot `Firmware/include/config.h` (konfigurasi cloud)
- Screenshot: section "Koneksi ke Backend ANTARAGA" di README firmware

---

**Sabtu, 18 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi endpoint `POST /v1/ingest` di backend — menerima batch data PPG mentah dari firmware setiap 500ms. Pipeline: (1) terima batch JSON, (2) coba estimasi vital dari PPG via MLP (fallback ke DB jika model belum ada), (3) prediksi stroke risk via XGBoost, (4) simpan VitalReading, (5) trigger FCM jika risiko HIGH dengan cooldown.

**Hasil:**
- Endpoint `/v1/ingest` berjalan dan menerima data firmware
- Pipeline prediksi otomatis setiap batch masuk
- Notifikasi FCM ter-trigger saat `risk_level == "HIGH"`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: `POST /v1/ingest 200 OK` berulang dari firmware
- Screenshot Swagger UI: endpoint `/v1/ingest` dengan payload schema
- Screenshot DB Browser: `vital_readings` bertambah setiap batch
- Screenshot kode endpoint `/v1/ingest` di VSCode

---

**Minggu, 19 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi sistem autentikasi khusus untuk firmware (`DEVICE_INGEST_KEY`) — key statis yang tidak expire, berbeda dengan JWT user. Backend menerima `Authorization: Bearer antaraga-hw-2026-01` dari firmware. Ketika device key cocok, backend otomatis menggunakan user yang paling terakhir aktif (most recently seen). Menambahkan `DEVICE_INGEST_KEY` ke `.env` backend.

**Hasil:**
- Fungsi `get_ingest_user_id()` di `auth.py`
- Firmware dapat mengirim data tanpa JWT yang expire
- Konfigurasi: `DEVICE_INGEST_KEY=antaraga-hw-2026-01`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: firmware mengirim dengan key → backend menerima 200 OK (bukan 401)
- Screenshot `.env` backend menampilkan `DEVICE_INGEST_KEY`
- Screenshot kode `get_ingest_user_id()` di VSCode

---

### Minggu ke-10 — 22–26 Juli 2026

---

**Rabu, 22 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi sistem pairing perangkat — menghubungkan `DEVICE_ID` firmware ke akun user tertentu. Menambahkan kolom `device_key` ke tabel `users`. Membuat endpoint `POST /device/pair` (user masukkan kode perangkat dari app) dan `GET /device/status`. Firmware yang mengirim batch dengan `"id": "antaraga-001"` akan otomatis terhubung ke akun yang sudah pairing.

**Hasil:**
- Endpoint `POST /device/pair` dan `GET /device/status`
- Kolom `device_key` di tabel `users` (migration SQLite)
- Endpoint `/v1/ingest` mengutamakan lookup user dari `device_key`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: migrasi `ALTER TABLE users ADD COLUMN device_key` berhasil
- Screenshot DB Browser: kolom `device_key` di tabel `users`
- Screenshot Swagger UI: endpoint `/device/pair`
- Screenshot Postman: `POST /device/pair` dengan `{"device_key": "antaraga-001"}` berhasil

---

**Kamis, 23 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi UI pairing perangkat di Dashboard Screen Flutter. Menambahkan ikon jam (watch) di AppBar — abu-abu jika belum terhubung, hijau jika terhubung. Saat ikon di-tap, muncul dialog untuk memasukkan `DEVICE_ID` (contoh: `antaraga-001`). Setelah pairing berhasil, snackbar muncul dengan konfirmasi. Tambah method `pairDevice()` dan `getDeviceStatus()` ke `ApiService`.

**Hasil:**
- Ikon device di AppBar dengan indikator status (abu-abu/hijau)
- Dialog pairing dengan input DEVICE_ID
- `ApiService.pairDevice()` dan `ApiService.getDeviceStatus()`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: ikon jam abu-abu di AppBar (belum pairing)
- Screenshot emulator: dialog "Hubungkan Perangkat" dengan input field
- Screenshot emulator: setelah pairing → ikon berubah hijau + snackbar "Berhasil"
- Screenshot emulator: tooltip ikon menampilkan "Perangkat: antaraga-001"

---

**Jumat, 24 Juli 2026 — 180 menit**

**Kegiatan:**
Testing integrasi lengkap: firmware → backend → mobile app. Menjalankan `dev.sh`, mengupdate `CLOUD_HOST` di `config.h` firmware sesuai URL ngrok, flash firmware ke XIAO ESP32-S3, melakukan pairing di mobile app, memantau log server. Berhasil melihat `POST /v1/ingest 200 OK` terus-menerus dari firmware. Data vital masuk ke database dan tampil di dashboard Flutter.

**Hasil:**
- Integrasi end-to-end berhasil: data mengalir dari sensor → backend → HP
- LED firmware denyut 1x/detik (streaming normal)
- Dashboard Flutter menampilkan data real dari sensor

📸 **Bukti yang perlu dilampirkan:**
- Foto smartband XIAO ESP32-S3 yang sudah terpasang sensor dan terhubung WiFi
- Screenshot terminal: `POST /v1/ingest 200 OK` berulang dengan latency ~10ms
- Screenshot emulator: dashboard Flutter menampilkan data real dari sensor
- Video singkat: LED smartband berdenyut saat streaming aktif

---

**Sabtu, 25 Juli 2026 — 180 menit**

**Kegiatan:**
Debugging masalah "dashboard tidak update" di Flutter. Menemukan root cause: backend mengirim `heart_rate_bpm: null` dan `spo2_percent: null` (belum dihitung karena MLP belum dilatih), menyebabkan `VitalData.fromJson()` crash di `(null as num).round()`. Exception tertelan oleh `catch (_)` sehingga `setState()` tidak pernila dipanggil. Fix: gunakan `?? 0` sebagai fallback di `fromJson()`.

**Hasil:**
- Fix di `lib/models/vital_data.dart`: `(json['heart_rate_bpm'] as num?)?.round() ?? 0`
- Kartu "Detak Jantung" menampilkan `--` saat nilai 0 (belum tersedia dari sensor)
- Dashboard sekarang update setiap ada data baru dari firmware

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: dashboard menampilkan `--` untuk detak jantung
- Screenshot emulator: data vital lain (tekanan darah, gula) ter-update dari sensor
- Screenshot kode `vital_data.dart` setelah fix di VSCode
- Screenshot terminal: tidak ada lagi error 500 di backend log

---

**Minggu, 26 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi hardware monitoring dashboard di browser — diakses via `GET /dashboard` di backend. Menggunakan Chart.js untuk visualisasi sinyal PPG real-time. Empat tab: (1) Data Asli: grafik PPG, RED, IR; (2) Setelah PWA: sinyal terfilter + peak detection; (3) Setelah MLP: vital tiles; (4) Setelah XGBoost: gauge risiko stroke. Polling setiap 1 detik, auto-connect jika hanya 1 device.

**Hasil:**
- File `api/static/dashboard.html` — dashboard monitoring lengkap
- Endpoint `GET /dashboard`, `GET /v1/devices`, `GET /v1/ingest/latest`
- File `api/ingest_buffer.py` — ring buffer per device (10 detik window)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot browser: Dashboard tab "Data Asli" menampilkan grafik PPG
- Screenshot browser: tab "Setelah PWA" dengan peak markers kuning
- Screenshot browser: tab "Setelah XGBoost" dengan gauge risiko
- Screenshot browser: status bar aktif (dot hijau, SEQ terus bertambah)

---

## FASE 3 — PENGUJIAN, ASSEMBLY & DOKUMENTASI
*(29 Juli — 24 September 2026)*

---

### Minggu ke-11 — 29 Juli – 2 Agustus 2026

---

**Rabu, 29 Juli 2026 — 180 menit**

**Kegiatan:**
Implementasi WebSocket serial monitor di backend — memungkinkan memantau serial UART firmware dari browser tanpa Arduino IDE. Endpoint `GET /serial/ports` menampilkan daftar port serial, `WebSocket /serial/ws?port=...&baud=115200` meneruskan data serial secara real-time. Digunakan tim hardware untuk debug tanpa laptop tambahan.

**Hasil:**
- Endpoint `GET /serial/ports` — list port serial
- WebSocket `/serial/ws` — stream data serial real-time
- `pyserial` ditambahkan ke `requirements.txt`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot browser: `http://localhost:8000/serial/ports` → list port tersedia
- Screenshot: WebSocket test menggunakan wscat atau Postman WebSocket
- Screenshot: data serial [STAT] firmware terbaca dari browser

---

**Kamis, 30 Juli 2026 — 180 menit**

**Kegiatan:**
Performance testing: mengukur latency pipeline `/v1/ingest` dari penerimaan hingga prediksi. Menggunakan log `latency_ms` di prediction_logs. Target: total latency < BATCH_MS (500ms) agar tidak menahan koneksi keep-alive firmware. Mengoptimasi query database (menambahkan index pada `profile_id` dan `created_at`).

**Hasil:**
- Latency rata-rata: ~10-15ms per prediksi (jauh di bawah 500ms target)
- Index database ditambahkan untuk mempercepat query
- Benchmark hasil terdokumentasi

📸 **Bukti yang perlu dilampirkan:**
- Screenshot DB Browser: tabel `prediction_logs` dengan kolom `latency_ms`
- Screenshot terminal: query latency rata-rata
- Screenshot: grafik distribusi latency (histogram)

---

**Jumat, 31 Juli 2026 — 180 menit**

**Kegiatan:**
Security review backend API. Memverifikasi: (1) semua endpoint sensitif dilindungi JWT, (2) password tersimpan sebagai bcrypt hash (bukan plaintext), (3) `serviceAccountKey.json` ada di `.gitignore`, (4) JWT secret tidak hardcoded (diambil dari `.env`), (5) CORS dikonfigurasi. Memperbaiki beberapa temuan kecil.

**Hasil:**
- Checklist security review selesai
- `.gitignore` diverifikasi — credential files tidak di-commit
- JWT expiry dikonfigurasi via environment variable

📸 **Bukti yang perlu dilampirkan:**
- Screenshot `.gitignore` menampilkan `serviceAccountKey.json` terdaftar
- Screenshot terminal: `git log --all -- api/serviceAccountKey.json` menampilkan tidak pernah di-commit
- Screenshot `.env` (sensor area sensitif ditutup/blur) menampilkan struktur
- Screenshot: endpoint tanpa token → 401 Unauthorized

---

**Sabtu, 1 Agustus 2026 — 180 menit**

**Kegiatan:**
Persiapan pengumpulan data kalibrasi untuk training model MLP. Membuat protokol kalibrasi: pengguna memakai smartband sambil mengukur tekanan darah dengan tensimeter standar dan gula darah dengan glucometer. Data disimpan secara terstruktur di `data/calibration/`. Membuat template CSV dan dokumentasi prosedur kalibrasi.

**Hasil:**
- Folder `data/calibration/` dengan template CSV
- Dokumen prosedur kalibrasi (kapan, posisi, berapa pengulangan)
- Script `scripts/record_calibration.py` untuk merekam data sesi kalibrasi

📸 **Bukti yang perlu dilampirkan:**
- Screenshot folder `data/calibration/` di file explorer
- Screenshot template CSV di spreadsheet
- Foto: tensimeter standar dan glucometer yang akan digunakan kalibrasi
- Screenshot kode `record_calibration.py` di VSCode

---

**Minggu, 2 Agustus 2026 — 180 menit**

**Kegiatan:**
Memulai pengumpulan data kalibrasi bersama tim hardware. Sesi pertama: memasang smartband ke relawan, merekam sinyal PPG selama 30 detik per sesi, mencatat tekanan darah dan gula darah secara bersamaan menggunakan alat standar. Menganalisis kualitas sinyal PPG pertama dari perangkat nyata.

**Hasil:**
- Data kalibrasi sesi pertama: beberapa rekaman PPG + ground truth vital
- Analisis kualitas sinyal: peak-to-peak ratio, SNR
- Catatan penyesuaian hardware (posisi sensor, kekencangan tali)

📸 **Bukti yang perlu dilampirkan:**
- Foto: relawan memakai smartband ANTARAGA + tensimeter di lengan lain
- Screenshot: sinyal PPG dari sensor_monitor.py selama sesi kalibrasi
- Foto: layar glucometer dan tensimeter saat pengukuran
- Screenshot: file CSV data kalibrasi tersimpan

---

### Minggu ke-12 — 5–9 Agustus 2026

---

**Rabu, 5 Agustus 2026 — 180 menit**

**Kegiatan:**
Analisis data kalibrasi yang sudah terkumpul. Memverifikasi kualitas sinyal PPG: deteksi apakah ada noise berlebih, motion artifact, atau saturasi sensor. Memvisualisasikan sinyal sebelum dan sesudah bandpass filter. Menghitung korelasi awal antara fitur morfologi PPG dengan nilai vital ground truth.

**Hasil:**
- Laporan kualitas sinyal kalibrasi
- Grafik perbandingan sinyal raw vs filtered
- Korelasi Pearson fitur PPG vs vital (tekanan darah, gula darah)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook: sinyal PPG dari sensor nyata (raw + filtered)
- Screenshot notebook: heatmap korelasi fitur PPG vs vital
- Screenshot: grafik scatter plot fitur terbaik vs tekanan darah

---

**Kamis, 6 Agustus 2026 — 180 menit**

**Kegiatan:**
Lanjutan pengumpulan data kalibrasi — sesi kedua dengan lebih banyak relawan. Target: minimal 30 rekaman per relawan × 5 relawan = 150 titik data. Memperhatikan variasi: posisi sensor, kondisi cahaya, aktivitas sebelum pengukuran. Menyimpan metadata sesi kalibrasi.

**Hasil:**
- Data kalibrasi bertambah
- Metadata sesi: nama relawan (anonim), kondisi, waktu
- Dataset kalibrasi dalam proses akumulasi

📸 **Bukti yang perlu dilampirkan:**
- Foto: sesi kalibrasi dengan relawan berbeda
- Screenshot: file CSV data kalibrasi di folder `data/calibration/`
- Screenshot: jumlah total rekaman yang terkumpul
- Foto: tim sedang melakukan pengambilan data

---

**Jumat, 7 Agustus 2026 — 180 menit**

**Kegiatan:**
Training model MLP untuk estimasi vital dari PPG menggunakan data kalibrasi yang sudah terkumpul. Menjalankan `python -m model.train_ppg_vitals`. Evaluasi dengan cross-validation 5-fold. Menganalisis error per output: Mean Absolute Error untuk tekanan sistolik, diastolik, dan gula darah.

**Hasil:**
- Model MLP `ppg_vitals_model.joblib` berhasil dilatih
- MAE tekanan sistolik: ±X mmHg, diastolik: ±Y mmHg, gula darah: ±Z mg/dL
- Model artifact tersimpan di `model/artifacts/`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: training MLP selesai dengan metrik
- Screenshot notebook: learning curve (loss vs epoch)
- Screenshot: tabel MAE per output
- Screenshot file `ppg_vitals_model.joblib` terbuat di `model/artifacts/`

---

**Sabtu, 8 Agustus 2026 — 180 menit**

**Kegiatan:**
Validasi model MLP end-to-end: memasang smartband ke relawan, merekam sinyal PPG, mengirimkan ke endpoint `/estimate/vitals-from-ppg`, membandingkan output model dengan pengukuran alat standar. Mendokumentasikan akurasi pada data unseen (test set).

**Hasil:**
- Tabel validasi: prediksi MLP vs ground truth untuk setiap relawan
- Analisis error: apakah error sistematis atau acak
- Rekomendasi fine-tuning jika error melebihi ambang klinis

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: tabel perbandingan prediksi vs ground truth
- Screenshot Postman: `/estimate/vitals-from-ppg` dengan data nyata
- Foto: pengukuran bersamaan (smartband + alat standar)
- Screenshot: response API dengan nilai estimasi vital

---

**Minggu, 9 Agustus 2026 — 180 menit**

**Kegiatan:**
Review dan refactoring kode backend secara menyeluruh. Memastikan tidak ada hardcoded value, semua konfigurasi melalui environment variable, error handling konsisten, dan kode terdokumentasi. Memverifikasi semua endpoint di Swagger UI masih berjalan setelah perubahan.

**Hasil:**
- Kode backend lebih bersih dan konsisten
- Semua endpoint terverifikasi di Swagger UI
- Tidak ada secret/credential di dalam kode

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: semua endpoint berwarna hijau (tidak ada error)
- Screenshot: `git log --oneline` menampilkan riwayat commit yang rapi
- Screenshot kode setelah refactoring di VSCode

---

### Minggu ke-13 — 12–16 Agustus 2026

---

**Rabu, 12 Agustus 2026 — 180 menit**

**Kegiatan:**
Testing skenario notifikasi FCM secara lengkap dengan device fisik. Skenario 1: user aktif menggunakan app saat risiko HIGH → notifikasi muncul in-app. Skenario 2: app di background → notifikasi di notification bar, tap → buka form ABCD2. Skenario 3: app killed → notifikasi di bar, tap → app restart langsung ke ABCD2.

**Hasil:**
- Ketiga skenario FCM berfungsi dengan benar
- Cooldown 5 menit mencegah spam notifikasi
- Bug ditemukan dan diperbaiki: notifikasi terkadang double

📸 **Bukti yang perlu dilampirkan:**
- Screenshot HP: notifikasi "Risiko Stroke Tinggi" di notification bar
- Video: tap notifikasi → app buka form ABCD2
- Screenshot: kode handler notifikasi untuk ketiga skenario

---

**Kamis, 13 Agustus 2026 — 180 menit**

**Kegiatan:**
Pengujian performa dashboard browser. Mengukur: (1) waktu load initial Chart.js dari CDN, (2) lag saat update chart setiap 1 detik, (3) penggunaan memory browser setelah 30 menit berjalan. Mengoptimasi: mengurangi jumlah data yang dikirim dari endpoint, memakai `chart.update('none')` untuk skip animasi.

**Hasil:**
- Dashboard stabil setelah 30 menit tanpa memory leak
- Update chart < 50ms per cycle
- Sinyal PPG terlihat jelas di semua 4 tab

📸 **Bukti yang perlu dilampirkan:**
- Screenshot dashboard berjalan: semua 4 tab aktif menampilkan data
- Screenshot browser DevTools (Performance tab): tidak ada memory leak
- Video singkat: dashboard update real-time selama 30 detik

---

**Jumat, 14 Agustus 2026 — 180 menit**

**Kegiatan:**
UI polish dan bug fixing aplikasi Flutter berdasarkan feedback internal tim. Memperbaiki: padding yang tidak konsisten, teks yang terpotong di layar kecil, animasi loading yang terlalu lama. Menambahkan empty state yang informatif saat belum ada data vital. Mengecek responsivitas di berbagai ukuran layar (kecil dan besar).

**Hasil:**
- UI lebih konsisten dan polish
- Empty state informatif di semua layar
- App berjalan mulus di layar 5" hingga 6.7"

📸 **Bukti yang perlu dilampirkan:**
- Screenshot sebelum dan sesudah fix (before/after comparison)
- Screenshot di berbagai ukuran layar (emulator 5" dan 6.7")
- Screenshot empty state yang informatif

---

**Sabtu, 15 Agustus 2026 — 180 menit**

**Kegiatan:**
Membuat user guide singkat untuk pengguna sistem ANTARAGA: cara pertama kali setup (register → buat profil → pasang smartband → pairing), cara membaca dashboard, kapan harus ke dokter berdasarkan skor ABCD2. Disusun dalam format yang mudah dipahami orang awam (tidak teknis).

**Hasil:**
- Dokumen user guide (PDF/Word) untuk pengguna akhir
- Panduan visual dengan screenshot aplikasi
- FAQ 10 pertanyaan umum

📸 **Bukti yang perlu dilampirkan:**
- Screenshot halaman user guide yang sudah selesai
- Screenshot: user guide dibuka di HP (format PDF)
- Foto: caregiver lansia membaca dan menggunakan panduan

---

**Minggu, 16 Agustus 2026 — 180 menit**

**Kegiatan:**
Testing aksesibilitas aplikasi Flutter. Memverifikasi: label semantik untuk screen reader, kontras warna yang cukup (AA standard), ukuran touch target minimal 48×48dp, teks yang bisa diperbesar hingga 200% tanpa layout rusak. Membuat laporan aksesibilitas.

**Hasil:**
- Laporan aksesibilitas: daftar issue dan status perbaikan
- Touch target diperbaiki untuk komponen yang kurang dari 48dp
- Kontras warna diverifikasi untuk semua teks penting

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: Flutter accessibility inspector menampilkan semantic labels
- Screenshot: app dengan ukuran teks 200% masih terbaca
- Screenshot: laporan aksesibilitas

---

### Minggu ke-14 — 19–23 Agustus 2026

---

**Rabu, 19 Agustus 2026 — 180 menit**

**Kegiatan:**
Persiapan demo sistem ANTARAGA untuk penilaian PKM. Membuat script demo: urutan langkah yang akan ditunjukkan, data dummy yang menarik (menunjukkan notifikasi HIGH risk), penjelasan tiap komponen sistem. Memastikan semua komponen berjalan tanpa bug saat demo.

**Hasil:**
- Script demo yang telah dilatih
- Data test yang menarik untuk demo (profile dengan risiko tinggi)
- Checklist pra-demo (semua service running, HP terhubung, dll)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot script demo yang sudah disiapkan
- Screenshot sistem berjalan lengkap saat dry run demo
- Foto: setup demo (laptop + HP + smartband)

---

**Kamis, 20 Agustus 2026 — 180 menit**

**Kegiatan:**
Assembly sistem ANTARAGA — menggabungkan semua komponen: smartband (hardware), HP Android (Flutter app), laptop (backend server). Memastikan semua kabel, power supply, dan koneksi rapi. Menguji sistem dalam kondisi seperti deployment nyata: smartband terpasang di pergelangan tangan, data mengalir ke HP secara wireless.

**Hasil:**
- Sistem ANTARAGA berjalan lengkap sebagai satu kesatuan
- Latency end-to-end: <1 detik dari sensor ke dashboard HP
- Dokumentasi assembly tersempurna

📸 **Bukti yang perlu dilampirkan:**
- Foto: setup sistem lengkap (smartband + HP + laptop server)
- Foto: smartband terpasang di pergelangan tangan pengguna
- Screenshot: data mengalir dari sensor ke dashboard Flutter secara live
- Foto: close-up smartband XIAO ESP32-S3 dengan sensor PPG

---

**Jumat, 21 Agustus 2026 — 180 menit**

**Kegiatan:**
Pengujian sistem dengan pengguna nyata (caregiver lansia). Melakukan observasi: apakah caregiver bisa setup app sendiri, apakah notifikasi mudah dipahami, apakah rekomendasi ABCD2 bisa diikuti. Mengumpulkan feedback kualitatif melalui wawancara singkat setelah penggunaan.

**Hasil:**
- Laporan user testing dengan 3 caregiver
- Feedback: tombol "Hubungkan Perangkat" kurang jelas → perlu label teks
- Feedback: notifikasi bahasa Indonesia sudah tepat

📸 **Bukti yang perlu dilampirkan:**
- Foto: caregiver lansia menggunakan aplikasi ANTARAGA di HP mereka
- Screenshot: app dibuka oleh pengguna nyata (bukan developer)
- Foto: sesi wawancara pasca penggunaan
- Dokumen: catatan feedback dari user testing

---

**Sabtu, 22 Agustus 2026 — 180 menit**

**Kegiatan:**
Implementasi perbaikan berdasarkan feedback user testing. Menambahkan label teks "Perangkat" di bawah ikon jam di AppBar. Memperjelas pesan empty state: "Belum ada data vital — hubungkan smartband terlebih dahulu". Memperbaiki wording notifikasi agar lebih mudah dipahami orang awam.

**Hasil:**
- Label teks di ikon perangkat (AppBar)
- Empty state yang lebih informatif
- Wording notifikasi disederhanakan

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: ikon "Perangkat" dengan label teks di AppBar
- Screenshot emulator: empty state baru yang informatif
- Screenshot: notifikasi dengan wording yang sudah diperbaiki

---

**Minggu, 23 Agustus 2026 — 180 menit**

**Kegiatan:**
Membuat video demonstrasi sistem ANTARAGA untuk dokumentasi PKM. Video menunjukkan: (1) smartband di pergelangan tangan, (2) data mengalir ke app Flutter, (3) dashboard monitoring di browser, (4) simulasi notifikasi risiko tinggi, (5) pengguna mengisi ABCD2 dan mendapat rekomendasi. Durasi video: ~3 menit.

**Hasil:**
- Video demonstrasi sistem ANTARAGA (MP4, ~3 menit)
- Narasi audio menjelaskan tiap komponen
- Subtitle dalam bahasa Indonesia

📸 **Bukti yang perlu dilampirkan:**
- Screenshot frame-frame kunci dari video demonstrasi
- Screenshot: timeline edit video di software editing
- Link/thumbnail video demonstrasi

---

### Minggu ke-15 — 26–30 Agustus 2026

---

**Rabu, 26 Agustus 2026 — 180 menit**

**Kegiatan:**
Penulisan laporan PKM bagian software/AI. Mendeskripsikan: arsitektur sistem, teknologi yang digunakan (FastAPI, Flutter, XGBoost, MLP, Firebase), metodologi pengembangan (iterative), hasil pengujian, dan keterbatasan sistem. Memastikan penjelasan teknis dapat dipahami oleh reviewer non-teknis.

**Hasil:**
- Draft laporan bagian 3 (Metode Pelaksanaan) selesai
- Draft laporan bagian 4 (Hasil dan Pembahasan) selesai
- Tabel hasil evaluasi model AI

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: dokumen laporan PKM yang sedang ditulis
- Screenshot: tabel evaluasi model di laporan
- Screenshot: diagram arsitektur sistem di laporan

---

**Kamis, 27 Agustus 2026 — 180 menit**

**Kegiatan:**
Membuat slide presentasi PKM untuk reviewer. Slide mencakup: latar belakang masalah (angka stroke di Indonesia), solusi ANTARAGA (arsitektur + alur data), hasil demo sistem, model AI (XGBoost AUC 0.823, MLP), rencana masa depan (deployment cloud, data kalibrasi lebih banyak).

**Hasil:**
- Slide presentasi PKM (~15 slide)
- Visualisasi data yang menarik di setiap slide
- Speaker notes untuk setiap slide

📸 **Bukti yang perlu dilampirkan:**
- Screenshot slide presentasi (beberapa slide kunci)
- Screenshot: slide demo dengan screenshot app
- Screenshot: slide hasil model AI dengan grafik AUC-ROC

---

**Jumat, 28 Agustus 2026 — 180 menit**

**Kegiatan:**
Dry run presentasi PKM bersama seluruh anggota tim. Mempraktikkan demo live sistem: menjalankan backend, menyambungkan HP, menyambungkan smartband, menunjukkan data mengalir, mengirim notifikasi. Memperbaiki timing dan bagian yang kurang lancar.

**Hasil:**
- Timing presentasi: 15 menit paparan + 5 menit demo + 10 menit Q&A
- Daftar pertanyaan yang kemungkinan muncul + jawabannya
- Setup demo dipercepat (script otomatis start semua service)

📸 **Bukti yang perlu dilampirkan:**
- Foto: tim saat latihan presentasi
- Screenshot: script otomatis start semua service
- Foto: setup demo yang sudah dioptimasi

---

**Sabtu, 29 Agustus 2026 — 180 menit**

**Kegiatan:**
Deployment backend ke cloud server (Railway/Render) untuk versi production. Mengonfigurasi environment variables, mengganti SQLite ke PostgreSQL, mengatur domain custom. Testing bahwa app Flutter (dengan `API_BASE_URL_PROD`) bisa terhubung ke backend production.

**Hasil:**
- Backend ANTARAGA berjalan di cloud server
- Database PostgreSQL production aktif
- Flutter app terhubung ke endpoint production

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: dashboard Railway/Render menampilkan backend running
- Screenshot: URL production (e.g., `https://antaraga-api.onrender.com/docs`)
- Screenshot: Flutter app terhubung ke backend production
- Screenshot: database PostgreSQL dengan data di cloud

---

**Minggu, 30 Agustus 2026 — 180 menit**

**Kegiatan:**
Pengujian sistem di lingkungan production (cloud). Memverifikasi: latency endpoint lebih tinggi dari lokal tapi masih acceptable, notifikasi FCM berjalan dari server cloud, firmware bisa terhubung ke URL production. Membuat monitoring sederhana dengan log rotation.

**Hasil:**
- Sistem production berjalan stabil
- Latency endpoint: <200ms dari Indonesia
- Notifikasi FCM berfungsi dari server production

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: uptime monitoring server production
- Screenshot: latency endpoint dari Postman (ke server cloud)
- Screenshot: notifikasi FCM masuk dari server production

---

### Minggu ke-16 — 2–6 September 2026

---

**Rabu, 2 September 2026 — 180 menit**

**Kegiatan:**
Pembuatan dokumentasi teknis lengkap: API Documentation (Swagger), README repository, panduan setup untuk developer baru yang ingin berkontribusi. Mendokumentasikan semua environment variable yang dibutuhkan, langkah-langkah instalasi, dan cara menjalankan test.

**Hasil:**
- README.md yang komprehensif (setup, instalasi, cara menjalankan)
- `Firmware/README.md` — cara konfigurasi dan flash firmware
- Semua dokumentasi dalam bahasa Indonesia

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: README.md di GitHub repository
- Screenshot: Firmware README.md di GitHub
- Screenshot: Swagger UI (dokumentasi API otomatis)

---

**Kamis, 3 September 2026 — 180 menit**

**Kegiatan:**
Pengujian robustness sistem: apa yang terjadi jika koneksi internet putus saat firmware streaming? Backend down? HP habis battery lalu restart? Memverifikasi bahwa setiap komponen memiliki graceful degradation. Mendokumentasikan behavior sistem di kondisi edge case.

**Hasil:**
- Firmware: buffer data saat WiFi putus (hingga 2.5 detik)
- Flutter: tampilkan data terakhir yang cached, tidak crash
- Backend: auto-restart dengan uvicorn supervisor

📸 **Bukti yang perlu dilampirkan:**
- Video: simulasi WiFi putus → LED firmware ganda (NET_LOST) → WiFi kembali → LED normal
- Screenshot: Flutter app tetap menampilkan data terakhir saat backend unreachable
- Screenshot: kode error handling di masing-masing komponen

---

**Jumat, 4 September 2026 — 180 menit**

**Kegiatan:**
Sesi pengambilan data kalibrasi tambahan untuk meningkatkan akurasi model MLP. Target: total 200+ titik data dari 10+ relawan dengan rentang usia 40-80 tahun. Menganalisis distribusi data: apakah sudah mewakili populasi target (lansia Indonesia).

**Hasil:**
- Data kalibrasi bertambah signifikan
- Distribusi usia dan kondisi medis relawan terdokumentasi
- Re-training MLP dengan dataset yang lebih besar

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: total rekaman di folder `data/calibration/`
- Foto: beragam relawan (usia 40-80 tahun)
- Screenshot: distribusi usia relawan (histogram)
- Screenshot terminal: re-training MLP berhasil dengan metrik lebih baik

---

**Sabtu, 5 September 2026 — 180 menit**

**Kegiatan:**
Analisis komparatif model: membandingkan performa XGBoost dengan model alternatif (Random Forest, Logistic Regression) menggunakan dataset yang sama. Mendokumentasikan mengapa XGBoost dipilih sebagai model utama ANTARAGA (AUC tertinggi, handling imbalance terbaik).

**Hasil:**
- Tabel perbandingan: XGBoost vs RF vs LR (AUC, Recall, Precision)
- Visualisasi: kurva ROC ketiga model di grafik yang sama
- Justifikasi pilihan XGBoost yang terdokumentasi

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook: grafik ROC curve ketiga model
- Screenshot notebook: tabel perbandingan metrik
- Screenshot: kode training ketiga model

---

**Minggu, 6 September 2026 — 180 menit**

**Kegiatan:**
Latihan presentasi ANTARAGA dengan audiens terbatas (5-7 orang, termasuk yang awam teknologi). Mengumpulkan feedback: apakah penjelasan mudah dipahami, apakah demo berjalan lancar, apakah ada pertanyaan yang tidak bisa dijawab. Memperbaiki penjelasan berdasarkan feedback.

**Hasil:**
- Feedback dari audiens terbatas terdokumentasi
- Penjelasan dipersingkat di beberapa bagian yang terlalu teknis
- Demo dipercepat dengan shortcut keyboard

📸 **Bukti yang perlu dilampirkan:**
- Foto: sesi presentasi dengan audiens
- Screenshot: slide yang direvisi berdasarkan feedback
- Foto: Q&A session

---

### Minggu ke-17 — 9–13 September 2026

---

**Rabu, 9 September 2026 — 180 menit**

**Kegiatan:**
Final integration testing — pengujian sistem secara menyeluruh dari awal hingga akhir tanpa intervensi developer. Skenario: (1) user baru install app → register → buat profil → pasang smartband → pairing, (2) monitoring selama 30 menit, (3) simulasi notifikasi HIGH, (4) assessment ABCD2, (5) cek riwayat di daily stats.

**Hasil:**
- Semua skenario berjalan tanpa bug
- Waktu setup pertama kali: <5 menit
- Tidak ada crash selama 30 menit monitoring

📸 **Bukti yang perlu dilampirkan:**
- Screenshot timeline integrasi test (semua step berhasil)
- Video: demo lengkap selama 5 menit
- Screenshot: app setelah 30 menit monitoring (data history terisi)

---

**Kamis, 10 September 2026 — 180 menit**

**Kegiatan:**
Membuat poster ilmiah PKM-KC ANTARAGA. Poster berisi: judul, abstrak, latar belakang, metodologi (dengan diagram), hasil utama (AUC model, demo screenshot), kesimpulan. Desain poster menggunakan template PKM yang sesuai dengan panduan DIKTI.

**Hasil:**
- Poster ilmiah PKM-KC ukuran A1 (sesuai panduan)
- File PDF poster siap cetak
- Versi digital untuk presentasi online

📸 **Bukti yang perlu dilampirkan:**
- Screenshot poster ANTARAGA tampak penuh
- Foto: poster dicetak dan dipasang
- Screenshot: detail diagram sistem di poster

---

**Jumat, 11 September 2026 — 180 menit**

**Kegiatan:**
Finalisasi laporan PKM-KC ANTARAGA. Review seluruh laporan: abstrak, bab pendahuluan, tinjauan pustaka, metode, hasil pembahasan, kesimpulan, daftar pustaka. Memastikan format sesuai panduan DIKTI 2026, semua referensi lengkap, dan tidak ada plagiarisme.

**Hasil:**
- Laporan PKM-KC ANTARAGA final (siap submit)
- Cek plagiarisme: <15% (aman)
- Format dan citasi sesuai panduan DIKTI

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: laporan PKM dibuka (halaman judul)
- Screenshot: hasil cek plagiarisme
- Screenshot: daftar pustaka yang lengkap

---

**Sabtu, 12 September 2026 — 180 menit**

**Kegiatan:**
Persiapan final demo untuk penilaian PKM. Menginstall app Flutter di HP yang akan dipakai demo (bukan emulator). Memverifikasi semua komponen berjalan dari satu tempat: server lokal + ngrok, smartband charged dan terpasang firmware terbaru, HP dengan app versi terbaru.

**Hasil:**
- APK terbaru terinstall di HP demo
- Firmware terbaru terflash ke smartband
- Checklist demo: semua ✓

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: APK versi final terinstall di HP (Settings → Apps)
- Foto: smartband dalam kondisi charged dan siap
- Screenshot: checklist demo semua ✓
- Foto: setup demo lengkap di meja presentasi

---

**Minggu, 13 September 2026 — 180 menit**

**Kegiatan:**
Membuat video profile produk ANTARAGA yang lebih profesional untuk dokumentasi PKM dan media sosial. Video 1.5 menit menampilkan: problem statement (stroke di Indonesia), produk ANTARAGA (close-up hardware dan app), cara kerja singkat, manfaat untuk caregiver lansia.

**Hasil:**
- Video profile produk ANTARAGA (MP4, 1.5 menit)
- Thumbnail video
- Caption untuk media sosial

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: frame kunci dari video profile
- Foto: behind the scenes pengambilan video
- Screenshot: video sudah diupload ke YouTube/Drive

---

### Minggu ke-18 — 16–20 September 2026

---

**Rabu, 16 September 2026 — 180 menit**

**Kegiatan:**
Pengujian final sistem di berbagai kondisi: WiFi lemah (hotspot jauh), HP dengan baterai rendah, server production (bukan localhost). Mendokumentasikan performa sistem di kondisi tidak ideal. Mengidentifikasi dan mencatat batasan sistem yang perlu disebutkan di laporan.

**Hasil:**
- Tabel performa di berbagai kondisi
- Batasan sistem terdokumentasi: latency meningkat di WiFi lemah, akurasi MLP tergantung kualitas sensor
- Rekomendasi pengembangan berikutnya

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: sistem berjalan dengan WiFi lemah (speed test + app masih running)
- Screenshot: tabel kondisi vs performa
- Screenshot: log latency saat kondisi berbeda

---

**Kamis, 17 September 2026 — 180 menit**

**Kegiatan:**
Benchmarking model AI ANTARAGA menggunakan dataset validasi eksternal (berbeda dari training set). Menghitung AUC-ROC, sensitivity, specificity, positive predictive value, negative predictive value. Membandingkan dengan threshold klinis ABCD2 sebagai baseline.

**Hasil:**
- Tabel metrik evaluasi komprehensif model XGBoost
- Perbandingan ANTARAGA vs metode konvensional (hanya ABCD2)
- Kesimpulan: ANTARAGA mendeteksi lebih awal dengan akurasi yang comparable

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notebook: confusion matrix pada dataset validasi
- Screenshot: tabel metrik komprehensif
- Screenshot grafik: kurva ROC dengan AUC pada validation set

---

**Jumat, 18 September 2026 — 180 menit**

**Kegiatan:**
Finalisasi semua file repository sebelum submission PKM. Membuat tag Git `v1.0.0-pkm-submission`. Memastikan: tidak ada credential di repository, semua dependency terdokumentasi di `requirements.txt` dan `pubspec.yaml`, README lengkap dan akurat.

**Hasil:**
- Tag Git `v1.0.0-pkm-submission` dibuat
- Repository bersih dan terorganisir
- README.md diverifikasi terakhir kali

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: GitHub repository dengan tag `v1.0.0-pkm-submission`
- Screenshot: commit terakhir sebelum submission
- Screenshot: GitHub repository tampak publik (README tampil)

---

**Sabtu, 19 September 2026 — 180 menit**

**Kegiatan:**
Mempersiapkan seluruh berkas submission PKM-KC: laporan utama, logbook, video demo, poster, bukti keuangan, surat pernyataan. Mengorganisir semua file dalam folder terstruktur sesuai format yang diminta DIKTI. Double-check semua file dapat dibuka dengan benar.

**Hasil:**
- Folder submission terstruktur sesuai format DIKTI
- Semua file berhasil dibuka dan kontennya benar
- Backup di Google Drive dan hardisk eksternal

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: struktur folder submission
- Screenshot: semua file terbuka (laporan, poster, video)
- Screenshot: folder backup di Google Drive

---

**Minggu, 20 September 2026 — 180 menit**

**Kegiatan:**
Rehearsal final presentasi PKM bersama seluruh tim. Simulasi kondisi penilaian sesungguhnya: timer ketat, ada juri yang bertanya. Membagi peran: siapa yang presentasi slide, siapa yang demo live system, siapa yang jawab pertanyaan teknis. Melatih kelancaran dan transisi antar bagian.

**Hasil:**
- Presentasi berjalan lancar dalam 15 menit
- Demo live tidak ada bug
- Semua anggota tim siap menjawab pertanyaan di bidangnya

📸 **Bukti yang perlu dilampirkan:**
- Foto: seluruh tim saat rehearsal presentasi
- Screenshot: slide presentasi final
- Foto: setup demo saat rehearsal

---

### Minggu ke-19 (Parsial) — 23–24 September 2026

---

**Rabu, 23 September 2026 — 180 menit**

**Kegiatan:**
Final system check sehari sebelum submission. Menjalankan seluruh sistem dari awal: server production, smartband, app Flutter. Memverifikasi setiap komponen berfungsi: login → pairing → monitoring → notifikasi → ABCD2 → riwayat. Mendokumentasikan versi final setiap komponen.

**Hasil:**
- Semua komponen terverifikasi berfungsi
- Versi final terdokumentasi: Flutter v1.0.0, Backend v1.0.0, Firmware v1.0.0
- Sistem siap untuk penilaian

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: final system status (semua komponen running)
- Screenshot: versi app Flutter (`About` page atau build info)
- Video singkat: system check terakhir berjalan sempurna

---

**Kamis, 24 September 2026 — 180 menit**

**Kegiatan:**
Submission PKM-KC ANTARAGA dan finalisasi logbook. Mengupload seluruh berkas ke sistem Simbelmawa sesuai deadline. Melakukan final review logbook — memverifikasi konsistensi tanggal, kelengkapan bukti foto, dan keakuratan deskripsi kegiatan. Merefleksikan perjalanan pengembangan sistem ANTARAGA dari Mei hingga September 2026.

**Hasil:**
- Semua berkas PKM berhasil di-submit ke Simbelmawa
- Logbook lengkap dengan semua bukti foto terlampir
- Sistem ANTARAGA berhasil dikembangkan: dari arsitektur → backend → AI model → mobile app → hardware integration → dashboard → production deployment

**Refleksi:**
Selama 4 bulan pengembangan, ANTARAGA berhasil menjadi sistem monitoring risiko stroke yang komprehensif. Tantangan terbesar adalah integrasi hardware-software (firmware ↔ backend ↔ mobile) dan penanganan class imbalance pada model XGBoost. Pencapaian terbesar: AUC-ROC 0.823 pada model XGBoost, latency prediksi <15ms, dan sistem notifikasi FCM yang berfungsi di ketiga skenario (foreground/background/killed state).

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: konfirmasi submission berhasil di sistem Simbelmawa
- Screenshot: logbook final semua halaman terisi
- Foto: tim ANTARAGA bersama (foto penutup kegiatan PKM)
- Screenshot: repository GitHub final (commit terakhir)

---

## REKAP TOTAL

| Komponen | Total Minggu | Total Menit |
|---|---|---|
| Minggu ke-1 (parsial) | — | 360 menit |
| Minggu ke-2 s/d ke-18 (penuh) | 17 minggu | 15.300 menit |
| Minggu ke-19 (parsial) | — | 360 menit |
| **Total** | **≈18.5 minggu** | **16.020 menit** |

## RINGKASAN CAPAIAN

| Bidang | Capaian |
|---|---|
| **Backend** | FastAPI + SQLAlchemy + JWT auth + 15+ endpoint |
| **AI/ML** | XGBoost (AUC 0.823), MLP architecture siap, PWA pipeline |
| **Mobile** | Flutter app (6 screens) + FCM push notification + device pairing |
| **Cloud** | Ngrok dev server + production deployment (Railway/Render) |
| **Dashboard** | Web monitoring real-time (4-tab, Chart.js, polling 1 detik) |
| **Hardware Integration** | Firmware XIAO ESP32-S3 ↔ Backend via HTTPS keep-alive |
| **UI/UX** | Figma mockup + responsive Flutter app |
| **Dokumentasi** | alur.md, alur_model.md, README, user guide, logbook |

---

*Logbook ini merupakan dokumentasi kegiatan pengembangan perangkat lunak dan AI dalam proyek PKM-KC ANTARAGA. Semua kegiatan dilaksanakan sesuai dengan rencana kerja dan target yang ditetapkan tim.*
