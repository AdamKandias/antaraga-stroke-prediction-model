# LOGBOOK KEGIATAN HARIAN
## PKM-KC: ANTARAGA - Smartband Deteksi Risiko Stroke Berbasis PPG dan Kecerdasan Buatan

| | |
|---|---|
| **Nama** | Adam Kandias |
| **Peran dalam Tim** | Software Developer · AI/ML Engineer · UI/UX Designer · Cloud Engineer |
| **Periode** | 23 Mei 2026 - 24 September 2026 |
| **Target Jam/Minggu** | 900 menit (15 jam) |
| **Hari Kerja** | Rabu · Kamis · Jumat · Sabtu · Minggu |
| **Durasi per Hari** | 180 menit (3 jam) |

---

> **Catatan Format Logbook**
> Setiap entri berisi:
> - **Kegiatan** - penjelasan detail pekerjaan yang dilakukan
> - **Hasil** - output konkret yang dihasilkan
> - 📸 **Bukti** - deskripsi foto/screenshot yang perlu dilampirkan sebagai bukti

---

## FASE 1 - PERENCANAAN & ARSITEKTUR SISTEM
*(23 Mei - 7 Juni 2026)*

---

### Minggu ke-1 (Parsial) - 23–24 Mei 2026

---

**Sabtu, 23 Mei 2026 - 180 menit**

**Kegiatan:**
Hari pertama pengerjaan PKM-KC ANTARAGA. Melakukan studi literatur tentang sistem deteksi risiko stroke berbasis wearable device dan membuat desain arsitektur sistem secara keseluruhan. Menentukan komponen utama: smartband (XIAO ESP32-S3), backend server (FastAPI/Python), aplikasi mobile (Flutter), dan model AI (XGBoost + MLP).

Arsitektur yang dirancang:
- Layer 1: Hardware (sensor PPG MAX30102 + SEN0203 pada XIAO ESP32-S3)
- Layer 2: Backend (FastAPI, SQLAlchemy, SQLite)
- Layer 3: AI/ML (XGBoost untuk deteksi risiko stroke, MLP untuk estimasi vital dari PPG)
- Layer 4: Mobile App (Flutter - monitoring real-time)
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

**Minggu, 24 Mei 2026 - 180 menit**

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

### Minggu ke-2 - 27–31 Mei 2026

---

**Rabu, 27 Mei 2026 - 180 menit**

**Kegiatan:**
Merancang skema database sistem ANTARAGA. Mengidentifikasi entitas yang dibutuhkan: User (akun keluarga), Profile (data lansia yang dipantau), VitalReading (pembacaan sensor), PredictionLog (log prediksi AI). Membuat Entity-Relationship Diagram (ERD) dan mendefinisikan semua kolom beserta tipe datanya menggunakan SQLAlchemy ORM.

Tabel yang dirancang:
- `users` - akun login (email/phone, password hash, FCM token)
- `profiles` - data lansia (nama, gender, tanggal lahir, kondisi medis)
- `vital_readings` - tekanan darah, detak jantung, SpO2, gula darah
- `prediction_logs` - log setiap prediksi AI (input, output, latency)

**Hasil:**
- ERD lengkap dengan relasi antar tabel
- File `api/models_db.py` dengan semua model SQLAlchemy

📸 **Bukti yang perlu dilampirkan:**
- Screenshot ERD yang sudah dibuat (draw.io atau dbdiagram.io)
- Screenshot kode `models_db.py` di VSCode
- Screenshot terminal: `python -c "from api.models_db import *; print('OK')"` berhasil

---

**Kamis, 28 Mei 2026 - 180 menit**

**Kegiatan:**
Membuat fondasi project FastAPI: struktur modul, konfigurasi environment (`.env`), koneksi database SQLite menggunakan SQLAlchemy, dan endpoint dasar `/health`. Menyusun file `config.py` untuk manajemen environment variable (DATABASE_URL, JWT_SECRET, DEV_MODE).

**Hasil:**
- File `api/main.py` - aplikasi FastAPI berjalan
- File `api/config.py` - konfigurasi terpusat
- File `api/database.py` - session factory SQLAlchemy
- Endpoint `GET /health` mengembalikan `{"status": "ok"}`
- Server bisa dijalankan dengan `uvicorn api.main:app --reload`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal: server uvicorn berjalan tanpa error
- Screenshot browser: `http://localhost:8000/docs` menampilkan Swagger UI
- Screenshot browser: `http://localhost:8000/health` menampilkan JSON response
- Screenshot kode `main.py` dan `config.py` di VSCode

---

**Jumat, 29 Mei 2026 - 180 menit**

**Kegiatan:**
Implementasi sistem autentikasi JWT (JSON Web Token) untuk keamanan API. Menggunakan library `bcrypt` untuk hashing password dan `PyJWT` untuk membuat/memverifikasi token. Membuat endpoint `POST /auth/register` dan `POST /auth/login`. Token yang dihasilkan memiliki masa berlaku 30 hari dan menyimpan `user_id` sebagai klaim `sub`.

**Hasil:**
- File `api/auth.py` - fungsi create/verify token + dependency `get_current_user_id`
- File `api/security.py` - hash_password dan verify_password
- Endpoint `/auth/register` - daftar akun baru
- Endpoint `/auth/login` - login dan dapatkan access token
- Endpoint `/auth/me` - cek identitas dari token

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: endpoint `/auth/register` dan `/auth/login`
- Screenshot Postman/curl: test register berhasil → response berisi `access_token`
- Screenshot Postman/curl: test login dengan credential yang salah → 401 Unauthorized
- Screenshot kode `auth.py` di VSCode

---

**Sabtu, 30 Mei 2026 - 180 menit**

**Kegiatan:**
Membuat endpoint manajemen profil lansia. Satu akun bisa memiliki beberapa profil (multi-lansia). Mengimplementasikan: `GET /profiles`, `POST /profiles`, `GET /profiles/{id}`, `PUT /profiles/{id}`, `GET /profiles/active` (profil terakhir yang dilihat). Membuat `api/schemas.py` dengan model Pydantic untuk validasi request/response.

Data profil yang tersimpan: nama, gender, tanggal lahir, berat badan, tinggi badan, status merokok, riwayat penyakit jantung, diabetes, tipe tempat tinggal.

**Hasil:**
- File `api/schemas.py` - semua schema Pydantic
- Endpoint CRUD profil lengkap
- Validasi input (gender enum, birthday format, dll)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: section "profiles" dengan semua endpoint
- Screenshot Postman: test `POST /profiles` berhasil → profil tersimpan
- Screenshot database viewer (DB Browser for SQLite) menampilkan tabel `profiles`
- Screenshot kode `schemas.py` di VSCode

---

**Minggu, 31 Mei 2026 - 180 menit**

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

### Minggu ke-3 - 3–7 Juni 2026

---

**Rabu, 3 Juni 2026 - 180 menit**

**Kegiatan:**
Preprocessing data untuk training model XGBoost. Tahapan: (1) isi missing value kolom BMI dengan median, (2) encoding kategorikal (gender, smoking_status, ever_married, work_type, Residence_type) menggunakan Label Encoding, (3) split data train/test (80:20, stratified by label), (4) simpan mapping encoding untuk dipakai saat inference.

**Hasil:**
- Script `model/preprocess.py` - fungsi preprocessing reproducible
- Data train dan test siap (X_train, X_test, y_train, y_test)
- Mapping label encoding tersimpan

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode preprocessing di VSCode
- Screenshot terminal: output info shape data `X_train.shape`, `X_test.shape`
- Screenshot notebook: distribusi data sebelum dan sesudah preprocessing

---

**Kamis, 4 Juni 2026 - 180 menit**

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

**Jumat, 5 Juni 2026 - 180 menit**

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

**Sabtu, 6 Juni 2026 - 180 menit**

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

**Minggu, 7 Juni 2026 - 180 menit**

**Kegiatan:**
Integrasi model XGBoost ke dalam FastAPI backend. Membuat file `api/ml.py` yang memuat model dari artifact `.joblib` saat server pertama kali dijalankan (lazy loading). Membuat endpoint `POST /predict/stroke-risk` yang menerima data vital + profil pasien, menjalankan prediksi, dan mengembalikan probabilitas + level risiko (LOW/MEDIUM/HIGH).

**Hasil:**
- File `api/ml.py` - fungsi `predict_stroke_risk(features)`
- Endpoint `/predict/stroke-risk` aktif dan dapat dipanggil
- Response: `{probability, risk_level, threshold, model_name}`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot Swagger UI: endpoint `/predict/stroke-risk` dengan schema input/output
- Screenshot Postman: test prediksi dengan data pasien → response berisi `risk_level: "LOW"`
- Screenshot kode `api/ml.py` di VSCode

---

## FASE 2 - UI/UX DESIGN & FLUTTER APP
*(10 Juni - 26 Juli 2026)*

---

### Minggu ke-4 - 10–14 Juni 2026

---

**Rabu, 10 Juni 2026 - 180 menit**

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

**Kamis, 11 Juni 2026 - 180 menit**

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

**Jumat, 12 Juni 2026 - 180 menit**

**Kegiatan:**
Desain high-fidelity mockup Dashboard Screen - layar utama yang menampilkan data vital real-time. Merancang komponen: kartu sambutan (nama + tanggal), kartu statistik harian, kartu monitoring vital (tekanan darah, detak jantung, gula darah, SpO2), kartu risiko stroke AI, tombol assessment ABCD2.

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

**Sabtu, 13 Juni 2026 - 180 menit**

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

**Minggu, 14 Juni 2026 - 180 menit**

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

### Minggu ke-5 - 17–21 Juni 2026

---

**Rabu, 17 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi tema dan routing aplikasi Flutter. Membuat sistem tema (light/dark mode) menggunakan `AppColors` class dengan warna-warna dari desain Figma. Setup routing: splash → login → dashboard. Implementasi Splash Screen dengan animasi logo. Konfigurasi `flutter_screenutil` untuk responsive UI.

**Hasil:**
- File `lib/core/theme/app_colors.dart` - semua konstanta warna
- File `lib/main.dart` - MaterialApp dengan tema dan routing
- Splash Screen berfungsi dengan animasi, auto-navigate ke login setelah 2 detik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Splash Screen dengan logo ANTARAGA
- Screenshot kode `app_colors.dart` di VSCode
- Screenshot kode `main.dart` (routing setup)
- Video pendek (GIF/MP4): animasi splash screen

---

**Kamis, 18 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi Login Screen dan Register Screen di Flutter. Membuat form dengan validasi input (email format, password minimum 6 karakter). Membuat `AuthService` yang menyimpan JWT token ke `SharedPreferences`. Membuat `ApiService` - centralized HTTP client yang membaca `API_BASE_URL` dari `.env`.

**Hasil:**
- File `lib/screens/login_screen.dart`
- File `lib/services/auth_service.dart` - login, logout, token management
- File `lib/services/api_service.dart` - HTTP client ke backend

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Login Screen tampak di HP
- Screenshot emulator: Register Screen tampak di HP
- Screenshot emulator: validasi error saat password kurang dari 6 karakter
- Screenshot kode `auth_service.dart` di VSCode

---

**Jumat, 19 Juni 2026 - 180 menit**

**Kegiatan:**
Membuat model data Flutter: `UserProfile` (data lansia) dan `VitalData` (pembacaan sensor). Implementasi `fromJson()` dan `toJson()` untuk serialisasi/deserialisasi dari API. Integrasi Profile Form Screen dengan API - memanggil `POST /profiles` saat user submit form pertama kali.

**Hasil:**
- File `lib/models/user_profile.dart` - model profil dengan fromJson/toJson
- File `lib/models/vital_data.dart` - model data vital
- Profile Form terhubung ke API, data tersimpan di database backend

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Profile Form Screen diisi dengan data lansia
- Screenshot emulator: setelah submit → navigasi ke dashboard
- Screenshot DB Browser (SQLite): tabel `profiles` berisi data yang baru diinput
- Screenshot Postman: GET /profiles menampilkan profil yang sudah dibuat

---

**Sabtu, 20 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi Dashboard Screen utama di Flutter. Membuat kartu-kartu vital: tekanan darah sistolik/diastolik, detak jantung, SpO2, gula darah. Setiap kartu menampilkan nilai, satuan, dan indikator status (normal/waspada/bahaya) berdasarkan range nilai normal medis. Implementasi `VitalRanges` class untuk logika status.

**Hasil:**
- File `lib/screens/dashboard_screen.dart` - screen utama
- File `lib/core/constants/vital_ranges.dart` - range normal tiap vital
- Dashboard menampilkan data vital dengan color-coded status

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: Dashboard Screen tampak penuh
- Screenshot emulator: zoom-in kartu tekanan darah
- Screenshot emulator: kartu dengan status "Waspada" (warna kuning)
- Screenshot kode `vital_ranges.dart` di VSCode

---

**Minggu, 21 Juni 2026 - 180 menit**

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

### Minggu ke-6 - 24–28 Juni 2026

---

**Rabu, 24 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi ABCD2 Scoring System di backend. ABCD2 adalah skor klinis untuk menilai risiko TIA (Transient Ischemic Attack) yang berkembang menjadi stroke dalam 2, 7, dan 90 hari. Membuat file `model/abcd2.py` dengan logika scoring berdasarkan Johnston et al. (2007): usia, tekanan darah, gejala klinis, durasi TIA, diabetes.

**Hasil:**
- File `model/abcd2.py` - implementasi ABCD2 (skor 0-7)
- Endpoint `POST /assessment/abcd2` di backend
- Response: skor, urgensi, rekomendasi, dan persentase risiko 2/7/90 hari

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `abcd2.py` di VSCode
- Screenshot Swagger UI: endpoint `/assessment/abcd2`
- Screenshot Postman: test ABCD2 dengan skor tinggi → respons "SEGERA KE UGD"
- Screenshot: jurnal Johnston et al. 2007 sebagai referensi

---

**Kamis, 25 Juni 2026 - 180 menit**

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

**Jumat, 26 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi Daily Stats Screen di Flutter - menampilkan riwayat pembacaan vital dalam sehari sebagai grafik garis. Menggunakan `fl_chart` library untuk membuat grafik interaktif. Sumbu X adalah waktu (jam), sumbu Y adalah nilai vital. Bisa scroll ke tanggal sebelumnya.

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

**Sabtu, 27 Juni 2026 - 180 menit**

**Kegiatan:**
Implementasi PPG Signal Processing Pipeline - modul Python untuk mengekstrak fitur morfologi dari sinyal PPG mentah. Mengimplementasikan: (1) Bandpass filter Butterworth order 3 (0.5–8 Hz) untuk isolasi gelombang jantung, (2) Peak detection (deteksi puncak sistol), (3) Ekstraksi fitur per-pulsa: amplitudo, crest time, pulse width.

**Hasil:**
- File `model/ppg_features.py` - pipeline PWA lengkap
- Fungsi `extract_pwa_features()` menghasilkan 20+ fitur morfologi
- Diuji dengan sinyal sintetis: berhasil deteksi 10+ puncak pada sinyal 10 detik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `ppg_features.py` di VSCode
- Screenshot notebook: visualisasi sinyal PPG sebelum dan sesudah bandpass filter
- Screenshot notebook: sinyal terfilter dengan peak markers
- Screenshot terminal: `python -c "from model.ppg_features import *; print('OK')"` berhasil

---

**Minggu, 28 Juni 2026 - 180 menit**

**Kegiatan:**
Merancang arsitektur MLP (Multi-Layer Perceptron) untuk estimasi vital dari sinyal PPG. MLP akan memetakan fitur morfologi PPG → [tekanan sistolik, tekanan diastolik, gula darah]. Arsitektur: input (23 fitur + usia) → hidden(16, tanh) → hidden(8, tanh) → output(3). Membuat file `model/train_ppg_vitals.py` sebagai training script yang siap dipakai saat data kalibrasi tersedia.

**Hasil:**
- File `model/train_ppg_vitals.py` - training pipeline MLP
- File `api/ml_vitals.py` - inference wrapper (menunggu artifact)
- Arsitektur MLP terdokumentasi di `alur_model.md`

📸 **Bukti yang perlu dilampirkan:**
- Screenshot kode `train_ppg_vitals.py` di VSCode
- Screenshot diagram arsitektur MLP (bisa di notebook atau draw.io)
- Screenshot kode `ml_vitals.py` di VSCode
- Screenshot: dokumentasi parameter MLP yang akan digunakan

---

### Minggu ke-7 - 1–5 Juli 2026

---

**Rabu, 1 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi simulator hardware di backend (`api/simulator.py`) untuk pengembangan dan testing tanpa perangkat fisik. Simulator membangkitkan data vital secara acak (dalam range normal dengan sesekali anomali), lalu memanggil pipeline prediksi stroke risk setiap 20 detik untuk semua user yang aktif. Berjalan sebagai background asyncio task saat `DEV_MODE=true`.

**Hasil:**
- File `api/simulator.py` - simulasi data sensor
- Backend otomatis menghasilkan data vital saat DEV_MODE aktif
- Dashboard Flutter menampilkan data yang berubah tanpa hardware fisik

📸 **Bukti yang perlu dilampirkan:**
- Screenshot terminal backend: log simulator berjalan setiap 20 detik
- Screenshot emulator Flutter: dashboard menampilkan data vital yang terus berubah
- Screenshot kode `simulator.py` di VSCode
- Screenshot: `DEV_MODE=true` di file `.env`

---

**Kamis, 2 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi logging dan monitoring prediksi AI. Setiap panggilan ke endpoint prediksi (stroke risk, ABCD2, vitals from PPG) dicatat ke tabel `prediction_logs` - termasuk input payload, output, latency, dan level risiko. Membuat endpoint `GET /logs` untuk melihat riwayat prediksi dari testing dashboard.

**Hasil:**
- Fungsi `log_prediction()` di `api/logging_utils.py`
- Semua prediksi tercatat otomatis di database
- Endpoint `GET /logs` untuk inspeksi dari luar

📸 **Bukti yang perlu dilampirkan:**
- Screenshot DB Browser: tabel `prediction_logs` dengan data
- Screenshot Postman: `GET /logs` menampilkan riwayat prediksi
- Screenshot kode `logging_utils.py` di VSCode

---

**Jumat, 3 Juli 2026 - 180 menit**

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

**Sabtu, 4 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi Firebase Cloud Messaging (FCM) di Flutter. Membuat `FcmService` class: (1) minta izin notifikasi dari user, (2) buat Android notification channel "antaraga_high_risk", (3) ambil FCM token dan kirim ke backend (`POST /device/register-token`), (4) handle 3 skenario notifikasi: foreground, background, killed state.

**Hasil:**
- File `lib/services/fcm_service.dart` - FCM service singleton
- Endpoint `POST /device/register-token` di backend
- Notifikasi tampil saat app di foreground (menggunakan `flutter_local_notifications`)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot emulator: dialog izin notifikasi saat app pertama dibuka
- Screenshot: push notification muncul di notification bar Android
- Screenshot Firebase Console: dapat mengirim test notification ke token device
- Screenshot kode `fcm_service.dart` di VSCode

---

**Minggu, 5 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi FCM di backend (Python). Menginstall `firebase-admin` SDK. Membuat `api/fcm.py` dengan inisialisasi Firebase Admin SDK menggunakan service account key. Membuat fungsi `send_high_risk_notification()` yang mengirim push notification dengan judul "⚠️ Risiko Stroke Tinggi Terdeteksi" beserta deeplink ke Assessment ABCD2. Mengintegrasikan trigger FCM ke simulator: setiap kali `risk_level == "HIGH"`, kirim notifikasi (dengan cooldown 5 menit).

**Hasil:**
- File `api/fcm.py` - Firebase Admin lazy init + send notification
- Cooldown system (tidak spam: max 1 notifikasi per 5 menit per user)
- Backend berhasil trigger push notification ke device Flutter

📸 **Bukti yang perlu dilampirkan:**
- Screenshot notifikasi "Risiko Stroke Tinggi" muncul di HP Android
- Screenshot: mengetuk notifikasi → app terbuka langsung ke form ABCD2
- Screenshot Firebase Console: activity log notifikasi terkirim
- Screenshot kode `fcm.py` di VSCode

---

### Minggu ke-8 - 8–12 Juli 2026

---

**Rabu, 8 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi deeplink navigasi dari notifikasi FCM ke AssessmentFormScreen. Menggunakan `ValueNotifier<bool> openAssessmentRequest` di `FcmService` sebagai event bus. `DashboardScreen` mendengarkan notifier ini dan membuka form ABCD2 melalui `addPostFrameCallback` untuk menghindari crash saat frame sedang build. Tiga skenario dihandle: foreground, background-tap, killed-tap.

**Hasil:**
- Deeplink berfungsi di ketiga skenario (foreground, background, killed state)
- File `lib/screens/dashboard_screen.dart` - listener FCM ditambahkan

📸 **Bukti yang perlu dilampirkan:**
- Video (GIF/MP4): tap notifikasi → app langsung buka form ABCD2
- Screenshot kode listener FCM di `dashboard_screen.dart`
- Screenshot: test dari Firebase Console → kirim notif → form terbuka

---

**Kamis, 9 Juli 2026 - 180 menit**

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

**Jumat, 10 Juli 2026 - 180 menit**

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

**Sabtu, 11 Juli 2026 - 180 menit**

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

**Minggu, 12 Juli 2026 - 180 menit**

**Kegiatan:**
Pembuatan sensor monitor desktop untuk tim hardware - aplikasi Python GUI menggunakan tkinter + matplotlib. Fitur: auto-detect port serial dan baud rate, grafik real-time multi-channel yang scrolling, pause/resume, export data ke CSV dan gambar (PNG/PDF). Hardware team dapat melihat sinyal PPG secara visual tanpa Arduino IDE.

**Hasil:**
- File `scripts/sensor_monitor.py` - aplikasi GUI standalone
- Mendukung format data: `key=value`, CSV, plain comma-separated
- Export CSV menyimpan semua histori (bukan hanya yang terlihat)

📸 **Bukti yang perlu dilampirkan:**
- Screenshot: `sensor_monitor.py` berjalan menampilkan grafik sinyal PPG
- Screenshot: dropdown auto-detect COM ports
- Screenshot: grafik setelah pause (menunjukkan data terkumpul)
- Screenshot: file CSV yang berhasil diexport

---

### Minggu ke-9 - 15–19 Juli 2026

---

**Rabu, 15 Juli 2026 - 180 menit**

**Kegiatan:**
Membuat dokumentasi sistem alur data lengkap di `alur.md`. Dokumen ini menjelaskan perjalanan data dari penerimaan di backend hingga notifikasi: endpoint ingest, pipeline PWA, parameter XGBoost, hasil training, ABCD2 scoring, sampai FCM. Dilengkapi diagram alur teks dan tabel parameter model.

**Hasil:**
- File `alur.md` - dokumentasi alur sistem lengkap (800+ kata)
- Tabel parameter XGBoost beserta maknanya
- Diagram alur end-to-end sistem ANTARAGA

📸 **Bukti yang perlu dilampirkan:**
- Screenshot file `alur.md` terbuka di VSCode (preview markdown)
- Screenshot: tabel parameter XGBoost di markdown preview
- Screenshot: diagram alur di markdown preview

---

**Kamis, 16 Juli 2026 - 180 menit**

**Kegiatan:**
Membuat dokumentasi konsep algoritma AI di `alur_model.md` untuk keperluan laporan PKM. Menjelaskan: (1) MLP - forward pass, backpropagation, fungsi aktivasi tanh, regularisasi L2; (2) XGBoost - gradient boosting algorithm, histogram approximation, scale_pos_weight, semua parameter dan artinya. Dilengkapi contoh perhitungan dan perbandingan kedua model.

**Hasil:**
- File `alur_model.md` - penjelasan konsep AI yang komprehensif (1200+ kata)
- Diagram struktur MLP (16→8→3) dalam format teks
- Perbandingan tabel MLP vs XGBoost

📸 **Bukti yang perlu dilampirkan:**
- Screenshot file `alur_model.md` di VSCode preview
- Screenshot: diagram MLP (layer input → hidden → output)
- Screenshot: tabel perbandingan MLP vs XGBoost

---

**Jumat, 17 Juli 2026 - 180 menit**

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

**Sabtu, 18 Juli 2026 - 180 menit**

**Kegiatan:**
Implementasi endpoint `POST /v1/ingest` di backend - menerima batch data PPG mentah dari firmware setiap 500ms. Pipeline: (1) terima batch JSON, (2) coba estimasi vital dari PPG via MLP (fallback ke DB jika model belum ada), (3) prediksi stroke risk via XGBoost, (4) simpan VitalReading, (5) trigger FCM jika risiko HIGH dengan cooldown.

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

**Minggu, 19 Juli 2026 - 180 menit**

**Kegiatan:**
Mengevaluasi model XGBoost final pada data uji yang belum pernah dipelajari model, baik saat pelatihan maupun saat penentuan ambang. Ambang yang dipakai adalah F1 terbaik (0,705), yaitu titik di mana presisi dan recall paling seimbang.

**Hasil:**
- Data uji 1.533 sampel, 75 di antaranya kasus stroke
- ROC-AUC **0,823** · Akurasi 0,882 · Presisi 0,206 · F1 0,290
- Recall **0,493** - matriks konfusi TP=37 · FN=38 · FP=143 · TN=1315
- **Recall 0,493 berarti lebih dari separuh penderita stroke tidak terdeteksi (38 dari 75).** Untuk alat deteksi risiko stroke, ini yang menjadi persoalan: seseorang yang berisiko justru tidak menerima peringatan apa pun, padahal keterlambatan penanganan stroke berakibat disabilitas permanen atau kematian
- Disimpulkan dibutuhkan metode lain agar tingkat recall-nya tinggi

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_evaluasi model pada ambang F1.png` - notebook `model/eval_19juli_ambang_f1.ipynb` bagian 3, metrik lengkap dan matriks konfusi
- `ADAM_grafik matriks konfusi dan kurva ROC.png` - notebook yang sama, grafik tiga panel
- `ADAM_pencarian ambang F1 out of fold.png` - notebook yang sama bagian 2

---

**Senin, 21 Juli 2026 - 180 menit**

**Kegiatan:**
Mencari cara menaikkan recall. Percobaan pertama paling sederhana: menurunkan ambang sampai seluruh penderita tertangkap. Percobaan ini gagal, sehingga dilanjutkan dengan menghitung berapa salah positif yang harus dibayar untuk setiap penderita tambahan, lalu menetapkan aturan pemilihan ambang yang dapat dipertanggungjawabkan.

**Hasil:**
- **Percobaan recall 1,0 gagal.** Ambang harus turun ke 0,0245, dan pada titik itu model menandai **seluruh 1.458 orang sehat** sebagai berisiko. Tidak satu pun lolos. Presisinya 0,0489 - sama persis dengan proporsi penderita di populasi, artinya keluaran model tidak lagi membawa informasi apa pun
- Analisis harga tiap penderita tambahan menunjukkan biaya relatif stabil sampai 73 penderita, lalu melonjak tajam: dari 73 ke 75 dibutuhkan tambahan **lebih dari 500 salah positif hanya untuk 2 penderita**
- Disadari bahwa mencari ambang langsung dari data uji keliru secara metodologi - ambangnya ikut menyesuaikan jawaban sehingga evaluasi tampak lebih baik daripada kenyataan
- Ambang dipindah pencariannya ke prediksi **out-of-fold pada data latih**, dan ditemukan pola bahwa recall di data uji selalu lebih rendah daripada di out-of-fold, sehingga targetnya perlu diberi margin:

| Target OOF | Recall OOF | Recall uji | Selisih | TP uji |
|---|---|---|---|---|
| 0,93 | 0,931 | 0,840 | +0,091 | 63 |
| 0,95 | 0,954 | 0,853 | +0,101 | 64 |
| 0,97 | 0,971 | 0,880 | +0,091 | 66 |
| **0,98** | **0,983** | **0,973** | **+0,009** | **73** |

- Ditetapkan `TARGET_RECALL = 0,98` pada prediksi out-of-fold, dan ditulis fungsi `recall_target_threshold()` di `model/train.py` yang mengambil ambang **tertinggi** yang recall-nya masih memenuhi target - karena setiap penurunan di luar itu hanya menambah salah positif tanpa manfaat

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_percobaan gagal recall satu penuh.png` - notebook `model/percobaan_ambang_21juli.ipynb` bagian 1, hasil percobaan menandai seluruh orang sehat
- `ADAM_analisis harga tiap penderita tambahan.png` - notebook yang sama bagian 2, tabel TP berbanding FP
- `ADAM_grafik kurva biaya dan harga per penderita.png` - notebook yang sama, grafik dua panel
- `ADAM_pemilihan target recall out of fold.png` - notebook yang sama bagian 3, tabel target OOF berbanding hasil data uji

---

**Rabu, 22 Juli 2026 - 180 menit**

**Kegiatan:**
Menerapkan aturan ambang yang ditetapkan kemarin, lalu mengujinya pada data uji. Setelah hasilnya keluar, ditemukan masalah lanjutan pada label risiko yang tampil di aplikasi, sehingga perlu diperbaiki di hari yang sama.

**Hasil:**
- Ambang deteksi turun dari 0,705 menjadi **0,042**
- **Penderita terdeteksi naik dari 37 menjadi 73 dari 75 (recall 0,973)**, yang terlewat turun dari 38 menjadi 2

| | 19 Juli | 22 Juli | Perubahan |
|---|---|---|---|
| Penderita terdeteksi | 37 | **73** | +36 |
| Penderita terlewat | 38 | **2** | −36 |
| Salah positif | 143 | 905 | +762 |
| Recall | 0,493 | **0,973** | +0,480 |
| Presisi | 0,206 | 0,075 | −0,131 |

- **Ditemukan masalah lanjutan**: label risiko di aplikasi ikut rusak. Karena batas "sedang" dihitung sebagai setengah ambang deteksi, setelah ambang turun ke 0,042 batas sedang jatuh ke 0,021 - akibatnya **tidak seorang pun memperoleh label "rendah"** dan 63,8% pengguna langsung berlabel risiko tinggi
- Diperbaiki dengan memisahkan dua ambang berfungsi berbeda: **deteksi 0,042** untuk menentukan perlu tindak lanjut, dan **risiko tinggi 0,705** untuk label di aplikasi. Sebaran kembali wajar: tinggi 11,7%, sedang 52,1%, rendah 36,2%
- Sempat dipertimbangkan memakai F2-score sebagai pembenaran, namun setelah dihitung **F2 justru masih memenangkan ambang lama** (0,385 berbanding 0,286); baru pada F3 ambang baru unggul. Karena itu pembenaran revisi tidak bersandar pada metrik gabungan, melainkan pada pertimbangan klinis bahwa biaya melewatkan penderita jauh lebih besar daripada biaya satu kali pemeriksaan tambahan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_hasil penerapan ambang baru.png` - notebook `model/hasil_ambang_22juli.ipynb` bagian 2, tabel perbandingan 19 Juli berbanding 22 Juli
- `ADAM_masalah label risiko rusak.png` - notebook yang sama bagian 3, sebaran label saat masih satu ambang
- `ADAM_perbaikan dua ambang terpisah.png` - notebook yang sama bagian 4, sebaran setelah dipisah
- `ADAM_grafik hasil revisi ambang.png` - notebook yang sama, grafik tiga panel
- `ADAM_perbandingan metrik f1 f2 f3.png` - notebook yang sama bagian 5

---

**Kamis, 23 Juli 2026 - 180 menit**

**Kegiatan:**
Memvalidasi model setelah perubahan ambang dengan menganalisis kontribusi tiap fitur terhadap keputusan. Tujuannya memastikan model mempelajari pola yang masuk akal secara medis, bukan korelasi semu yang kebetulan muncul di data latih.

**Hasil:**
- Peringkat kepentingan (gain): Usia **0,502** · IMT 0,086 · Hipertensi 0,079 · Jenis kelamin 0,078 · Glukosa rata-rata 0,076 · Penyakit jantung 0,076
- Peringkat terbawah justru fitur yang secara medis kurang berkaitan: tipe tempat tinggal 0,059, status merokok 0,044, status bekerja **0,000**
- Total kontribusi faktor risiko klinis **81,9%**, sehingga model dinilai tidak bertumpu pada korelasi semu
- Dicatat sebagai catatan pengembangan: dominasi usia 0,502 perlu diwaspadai karena model berisiko sekadar menebak dari umur; hal ini menjadi pertimbangan komposisi subjek saat pengumpulan data kalibrasi nanti

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_peringkat kepentingan fitur model.png` - notebook `model/kepentingan_fitur_23juli.ipynb` bagian 1
- `ADAM_grafik kepentingan fitur dan porsi klinis.png` - notebook yang sama bagian 2

---

**Sabtu, 25 Juli 2026 - 180 menit**

**Kegiatan:**
Membangun artefak model final untuk dipakai server. Menyimpan modelnya saja tidak cukup: bila urutan fitur atau daftar nilai kategori berbeda antara pelatihan dan inferensi, prediksinya salah tanpa memunculkan galat apa pun. Untuk membuktikannya dilakukan uji dengan sengaja menukar posisi dua fitur.

**Hasil:**
- Artefak `model/artifacts/stroke_risk_model.joblib` (147 KB) memuat model, urutan sembilan fitur, daftar nilai kategori, jenis pengodean, serta **kedua ambang** (deteksi 0,042 dan risiko tinggi 0,705) beserta target recall
- Uji penukaran fitur `age` ↔ `is_working`: selisih probabilitas rerata **0,249**, maksimum **0,787**
- Sebanyak **555 dari 1.533 sampel berubah keputusan** akibat penukaran itu, tanpa satu pun pesan galat
- Disimpulkan `feature_order` wajib disimpan di dalam artefak dan dipakai ulang saat inferensi
- Berkas metrik `metrics.json` ikut disimpan sebagai catatan performa versi model ini

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_isi artefak model dan metadata.png` - notebook `model/artefak_model_25juli.ipynb` bagian 1
- `ADAM_uji pengaruh urutan fitur tertukar.png` - notebook yang sama bagian 2
- `ADAM_grafik prediksi bergeser tanpa galat.png` - notebook yang sama bagian 3
- `ADAM_berkas artefak model tersimpan.png` - terminal `ls -lh model/artifacts/`

---

**Senin, 27 Juli 2026 - 240 menit**

**Kegiatan:**
Mengintegrasikan model ke lapisan API sebagai endpoint prediksi risiko stroke, sehingga aplikasi mobile dapat memanggilnya. Endpoint menerima data profil pengguna, memetakannya ke sembilan fitur model sesuai urutan yang tersimpan di artefak, lalu mengembalikan probabilitas beserta tingkat risiko.

**Hasil:**
- Endpoint `POST /predict/stroke-risk` berjalan dan mengembalikan `probability`, `risk_level`, `threshold`, dan `model_name`
- Fungsi `predict_stroke_risk()`, `_build_row()`, dan `_risk_level()` di `api/ml.py`
- Pemetaan profil pengguna ke fitur model lewat `profile_to_features()` di `api/profile_utils.py` - hipertensi diturunkan dari pembacaan tekanan darah terakhir karena aplikasi tidak punya medan diagnosis terpisah
- Tingkat risiko memakai dua ambang yang tersimpan di artefak, bukan angka yang ditulis langsung di kode
- Setiap prediksi dicatat ke tabel `prediction_logs` untuk keperluan audit dan riwayat pengguna

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_kode fungsi predict stroke risk.png` - `api/ml.py` di VSCode, fungsi `predict_stroke_risk()` dan `_risk_level()`
- `ADAM_swagger endpoint prediksi risiko stroke.png` - Swagger UI `/docs`, endpoint beserta skema permintaan
- `ADAM_respons json prediksi risiko.png` - hasil uji endpoint menampilkan keempat medan keluaran
- `ADAM_tabel prediction logs terisi.png` - DB Browser menampilkan isi tabel `prediction_logs`

---

### Minggu ke-11 - 29 Juli – 2 Agustus 2026

---

**Rabu, 29 Juli 2026 - 240 menit**

**Kegiatan:**
  Menghosting backend ke cloud VPS, membeli domain, serta melakukan konfigurasi Cloudflare. Menyiapkan pengemasan aplikasi dengan Docker dan reverse proxy nginx agar backend dapat diakses publik lewat domain, sekaligus alur penerapan otomatis dari repositori.

**Hasil:**
- Backend berjalan di VPS dan dapat diakses lewat **www.antaraga.web.id**
- `Dockerfile` dan `docker-compose.prod.yml` dengan empat named volume agar data bertahan melewati pembaruan: `antaraga-db`, `antaraga-models`, `antaraga-ota`, `antaraga-logs`
- Port dibatasi ke `127.0.0.1:8089` agar hanya dapat diakses lewat reverse proxy, tidak terbuka langsung ke internet
- Konfigurasi nginx di `scripts/nginx_antaraga.conf`: domain utama untuk halaman muka dan dashboard, subdomain `api.` untuk seluruh endpoint
- Cloudflare mode Flexible; pengalihan HTTP ke HTTPS sengaja tidak dipasang di nginx untuk menghindari `ERR_TOO_MANY_REDIRECTS`
- Alur penerapan otomatis lewat GitHub Actions (`.github/workflows/deploy.yml`)
- Fitur pembaruan firmware jarak jauh (OTA) ditambahkan agar smartband dapat diperbarui tanpa kabel

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_halaman muka antaraga web id di peramban.png` - situs terbuka lewat domain, sorot ikon kunci HTTPS
- `ADAM_container antaraga berstatus healthy.png` - terminal `docker compose ps`
- `ADAM_konfigurasi nginx reverse proxy.png` - `scripts/nginx_antaraga.conf` di VSCode
- `ADAM_dasbor cloudflare domain antaraga.png` - panel Cloudflare menampilkan catatan DNS
- `ADAM_github actions penerapan berhasil.png` - riwayat workflow dengan tanda centang hijau

---

**Kamis, 30 Juli 2026 - 180 menit**

**Kegiatan:**
Menguji ketahanan endpoint terhadap masukan tidak lengkap dan kategori di luar daftar pelatihan, karena data dari aplikasi mobile tidak selalu lengkap. Selain itu membangun sistem pencatatan akses dan galat agar kendala di lapangan dapat ditelusuri tanpa harus masuk ke VPS.

**Hasil:**
- **Ditemukan bug**: masukan yang kolomnya benar-benar hilang membuat server melempar `KeyError`, yang akan merusak aplikasi di tangan pengguna
- Diperbaiki dengan mengubah `_build_row()` agar kolom yang tidak dikirim diperlakukan sebagai nilai hilang; kolom numerik dipaksa bertipe angka agar `None` menjadi `NaN`
- Setelah perbaikan: **6 dari 6 skenario ditangani tanpa galat** (semula 5 dari 6)
- Uji pengaruh IMT: nilai kosong tetap memberi probabilitas wajar tanpa nilai ekstrem, memanfaatkan penanganan data hilang bawaan XGBoost
- Modul `api/logging_utils.py` dengan dua berkas terpisah: `access.log` dan `api.log`
- Endpoint `GET /v1/access-log` beserta aliran langsung, sehingga catatan dapat dibaca dari dashboard

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_uji enam skenario masukan bermasalah.png` - notebook `model/uji_ketahanan_endpoint_30juli.ipynb` bagian 1
- `ADAM_grafik ketahanan endpoint dan nilai kosong.png` - notebook yang sama
- `ADAM_perbaikan penanganan kolom hilang.png` - `api/ml.py` fungsi `_build_row()` yang sudah diperbaiki
- `ADAM_tab log akses realtime dashboard.png` - dashboard tab Log Akses

---

**Minggu, 2 Agustus 2026 - 180 menit**
*Lokasi: Kopi Kenangan*

**Kegiatan:**
Membangun dashboard web pemantauan untuk kemudahan riset. Memindahkan algoritma analisis sinyal dari firmware hardware (ESP32) ke server, agar bentuk gelombang dan BPM ketiga kanal sensor multiwavelength dapat dipantau langsung lewat web tanpa perlu menyambungkan kabel mikrokontroler ke laptop.

**Hasil:**
- Dashboard web di `/dashboard` dengan pembaruan tiap 1 detik
- Modul `api/ppg_analysis.py`: pembuangan garis dasar dengan bandpass Butterworth 0,5–5 Hz zero-phase, penghitungan BPM lewat autokorelasi FFT beserta nilai periodisitas
- Ketiga kanal diproses terpisah: hijau 525 nm, merah 660 nm, inframerah 880 nm
- Panel statistik menampilkan DC, AC puncak-ke-puncak, dan perfusi permil tiap kanal
- Pilihan lebar jendela tampilan 5 sampai 60 detik
- Nilai periodisitas di bawah 0,30 ditandai sebagai derau agar angka BPM tidak dibaca sebagai hasil sah
- Port algoritma BPM firmware ke Python di `api/bpm_engine.py` sebagai pembanding, seluruh konstanta disamakan dengan `Firmware/include/config.h`
- Penilaian mutu sinyal (SQI) berlapis: penanda dari perangkat digabung pemeriksaan di server, batch bermutu buruk dibuang sebelum dianalisis
- **Estimasi SpO2 diuji lalu dibatalkan.** Perhitungan rasio-of-ratios memerlukan kalibrasi terhadap pulse oximeter medis yang belum tersedia, sehingga nilainya berisiko menyesatkan. Fitur dilepas agar tidak ada angka yang tidak dapat dipertanggungjawabkan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_dashboard web pemantauan realtime.png` - tampilan penuh dashboard dengan grafik berjalan
- `ADAM_grafik ppg tiga kanal multiwavelength.png` - gelombang ketiga kanal berdampingan
- `ADAM_panel statistik dc ac perfusi.png` - tabel statistik jendela
- `ADAM_penilaian mutu sinyal sqi.png` - skor SQI beserta penandanya
- `ADAM_kode analisis sinyal ppg server.png` - `api/ppg_analysis.py`

---

### Minggu ke-12 - 5–9 Agustus 2026

---

**Selasa, 5 Agustus 2026 - 240 menit**
*Lokasi: Ruang Kerja Pribadi Tim*

**Kegiatan:**
Membangun antarmuka kalibrasi di dashboard untuk perekaman sesi berpasangan antara sinyal PPG sensor dan nilai alat medis. Sebelumnya perekaman hanya dapat dilakukan lewat terminal, yang menyulitkan saat pengambilan data di lapangan bersama subjek lansia. Kegiatan ini menyiapkan sarana pengumpulan data; perancangan modelnya dilakukan setelah datanya terkumpul.

**Hasil:**
- Formulir perekaman sesi kalibrasi: sinyal PPG diambil otomatis dari penyangga 10 detik terakhir, nilai alat invasif diisi manual peneliti
- Tiga kondisi pengukuran dapat dipilih: puasa, dua jam setelah makan, dan sewaktu
- Tabel dataset kalibrasi beserta penyuntingan, penghapusan, dan ekspor CSV
- Ringkasan statistik dataset: jumlah sesi, jumlah subjek, dan rentang tiap parameter
- Endpoint `POST /v1/calibrate`, `GET /v1/calibrate`, `PATCH /v1/calibrate/{id}`, dan `GET /v1/calibrate/export.csv`
- Sinyal mentah ketiga kanal ikut disimpan, sehingga nilai turunan dapat dihitung ulang bila kelak ditemukan kesalahan pemrosesan
- Dokumen `docs/protokol_kalibrasi.md` disusun sebagai panduan pengambilan data di lapangan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_formulir perekaman sesi kalibrasi.png` - dashboard tab Kalibrasi
- `ADAM_tabel dataset kalibrasi.png` - tabel dataset dengan baris yang sudah terekam
- `ADAM_ekspor csv dataset kalibrasi.png` - berkas CSV hasil ekspor terbuka
- `ADAM_dokumen protokol kalibrasi.png` - `docs/protokol_kalibrasi.md`

---

**Rabu, 6 Agustus 2026 - 360 menit**
*Waktu: 10:00 – 16:00*

**Kegiatan:**
Pengujian smartband ANTARAGA secara menyeluruh bersama tim hardware. Menguji alur data dari sensor sampai tersimpan di server, sekaligus memeriksa kewajaran nilai yang terbaca.

**Hasil:**
- Alur pengiriman data berjalan: firmware mengirim batch tiap 500 ms, server menerima dan memproses ketiga kanal
- **Ditemukan lonjakan BPM tidak wajar**: pembacaan stabil di 80 bpm tiba-tiba melompat ke 40 bpm selama beberapa detik lalu kembali normal. Polanya tepat setengah, yang merupakan ciri *octave error* - detektor melewatkan satu dari dua denyut
- Dibuat penyaring di `api/bpm_filter.py` dengan empat lapis: gerbang periodisitas, koreksi kesalahan oktaf, batas laju fisiologis 20%, dan median bergulir
- Nilai terakhir yang baik ditahan maksimum 15 detik saat sinyal hilang, agar layar tidak menampilkan tanda hubung berkedip
- Mekanisme pemulihan ditambahkan: bila delapan pembacaan berturut-turut konsisten, penyaring menganggap detak memang berpindah level
- **Ditemukan BPM kanal hijau terkunci di sekitar 60 bpm.** Penelusuran menunjukkan sinyal SEN0203 sudah AC-coupled di perangkat (perfusi terukur 1.719‰, padahal PPG normal 0,02–2%), dan penggabungan batch tanpa pemeriksaan kesinambungan menimbulkan lompatan periodik tepat 1 Hz yang dikunci autokorelasi
- Kartu BPM siap-tampil dialihkan bersumber dari kanal inframerah yang perfusinya stabil
- **Ditemukan kesalahan oktaf pada jalur analisis PWA**: `bpm_from_spectrum()` melaporkan 157,5 bpm padahal ketiga kanal sepakat di sekitar 78 bpm. Diperbaiki dengan penjaga sub-harmonik dan interpolasi parabola

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_pengujian smartband bersama tim.png` - foto pengujian dengan alat terpasang
- `ADAM_lonjakan bpm sebelum disaring.png` - dashboard menampilkan lonjakan 80 ke 40 bpm
- `ADAM_uji empat skenario penyaring bpm.png` - hasil uji penyaring, nilai 40 dikoreksi jadi 80
- `ADAM_kartu bpm tersaring di dashboard.png` - kartu BPM Tersaring beserta nilai mentahnya
- `ADAM_analisis artefak kanal hijau.png` - perhitungan periode terdeteksi sama dengan panjang batch
- `ADAM_perbaikan kesalahan oktaf pwa.png` - tabel perbandingan tujuh detak, versi lama berbanding baru

---

**Sabtu, 9 Agustus 2026 - 360 menit**

**Kegiatan:**
Proses pembuatan berkas pendaftaran Hak Kekayaan Intelektual untuk komponen perangkat lunak dan model kecerdasan buatan ANTARAGA. Menyusun dokumentasi struktur kode beserta rentang baris tiap fitur agar dapat dilampirkan sebagai bukti ciptaan.

**Hasil:**
- Dokumen `HKI.md` tersusun dengan lima bagian: backend API, dashboard web, model AI, firmware smartband, dan aplikasi mobile
- Tiap fitur dipetakan ke berkas dan rentang barisnya, sehingga pemeriksa dapat menelusuri langsung ke kodenya
- Lampiran ringkasan delapan fitur unggulan yang menjadi inti kebaruan ciptaan
- Catatan penyusunan lampiran: kredensial pada `Firmware/include/config.h` dan `.env` harus disamarkan, dataset pihak ketiga tidak dilampirkan, artefak model biner tidak disertakan karena yang diklaim adalah kode pelatihannya
- Total baris kode yang didokumentasikan: backend dan dashboard di repositori utama, serta 4.785 baris aplikasi Flutter pada 23 berkas

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_dokumen hki lima bagian.png` - `HKI.md` di VSCode, daftar isi kelima bagian
- `ADAM_pemetaan fitur ke baris kode.png` - tabel pemetaan berkas dan rentang baris
- `ADAM_lampiran fitur unggulan ciptaan.png` - tabel delapan fitur unggulan

---

**Minggu, 10 Agustus 2026 - 180 menit**

**Kegiatan:**
Mengunjungi dokter spesialis saraf untuk validasi pendekatan sistem ANTARAGA, terutama pemilihan parameter risiko, penetapan ambang keputusan, dan cara penyampaian hasil kepada keluarga.

**Hasil:**
*(Bagian ini perlu diisi sesuai hasil kunjungan yang sebenarnya - nama dan institusi dokter, masukan yang diberikan, serta tindak lanjut yang disepakati.)*

Hal-hal yang disiapkan untuk ditanyakan:
- Kelayakan ambang deteksi 0,042 yang mengutamakan recall (73 dari 75 penderita terdeteksi, dengan konsekuensi 62% orang sehat ikut tertandai)
- Kesesuaian sembilan parameter masukan model dengan faktor risiko stroke pada praktik klinis
- Ketepatan penggunaan skor ABCD² sebagai asesmen lanjutan, dan penegasan bahwa ANTARAGA berperan sebagai penyaring awal, bukan alat diagnosis
- Cara penyampaian tingkat risiko kepada keluarga agar tidak menimbulkan kepanikan maupun rasa aman yang keliru

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_kunjungan validasi dokter saraf.png` - foto bersama dokter saat konsultasi
- `ADAM_catatan masukan dokter.png` - catatan hasil konsultasi
- `ADAM_surat keterangan validasi.png` - dokumen validasi bila tersedia

---

### Minggu ke-13 - 12–16 Agustus 2026

---

**Kamis, 14 Agustus 2026 - 180 menit**

**Kegiatan:**
Proses penyerahan berkas HKI ke sentra HKI kampus PENS. Melengkapi lampiran kode sumber dan memastikan seluruh kredensial sudah disamarkan sebelum dokumen diserahkan.

**Hasil:**
- Berkas lampiran kode sumber disiapkan sesuai urutan dokumen: backend, dashboard, model AI, firmware, aplikasi mobile
- Kredensial WiFi pada `Firmware/include/config.h`, kunci perangkat, dan isi `.env` diganti tanda bintang pada salinan lampiran
- Berkas `serviceAccountKey.json` dan kunci API pada `lib/firebase_options.dart` dikecualikan
- Dataset publik `healthcare-dataset-stroke-data.csv` tidak dilampirkan karena bukan bagian dari ciptaan
- Artefak model biner tidak disertakan; yang diklaim adalah kode pelatihannya
- Berkas diserahkan ke sentra HKI PENS

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_berkas hki siap serah.png` - tumpukan dokumen lampiran
- `ADAM_kredensial disamarkan pada lampiran.png` - perbandingan berkas asli dan salinan
- `ADAM_penyerahan berkas ke sentra hki.png` - foto saat penyerahan

---

**Sabtu, 16 Agustus 2026 - 450 menit**
*Kegiatan tim: pengujian 4 smartband ANTARAGA*

**Kegiatan:**
Merancang model MLP untuk kalibrasi sensor PPG, lalu menerapkannya ke kode pelatihan dan menyambungkannya ke dashboard. Model XGBoost yang sudah selesai memprediksi risiko stroke dari nilai vital, tetapi nilai-nilai itu masih harus diukur dengan alat invasif. Tugas MLP adalah menerjemahkan sinyal optik sensor menjadi nilai vital, sehingga pengguna tidak perlu ditusuk jarum atau dipasangi manset.

**Hasil - perancangan model:**
- **Ditetapkan MLP, bukan regresi linier.** Diuji pada data yang meniru dua sifat nyata: perfusi merupakan rasio AC/DC (pembagian, tidak dapat dinyatakan sebagai penjumlahan berbobot) dan efeknya dimodulasi kekakuan pembuluh yang meningkat seiring usia. Hasilnya regresi linier R² 0,868 sedangkan MLP 0,946
- **Ditetapkan lima model terpisah**, bukan satu model lima keluaran, karena ketersediaan data tiap parameter berbeda dan skala nilainya jauh berbeda (gula darah 70–280 mg/dL berbanding asam urat 2–9,5 mg/dL)
- **Ditetapkan aturan penskalaan kapasitas**: n<10 memakai lapisan (4,) alpha 1,0; 10≤n<30 memakai (16,8) alpha 0,1; n≥30 memakai (64,32) alpha 0,01. MLP (64,32) memiliki 2.625 parameter - memaksakannya ke 5 baris sama saja mencari 2.625 nilai dari 5 persamaan
- **Ditetapkan pengelompokan validasi silang per subjek.** Diuji pada 6 subjek × 5 rekaman: LeaveOneOut biasa menghasilkan R² 0,720 sedangkan pengelompokan per subjek menghasilkan −4,737. Selisih 5,5 itulah kebocoran tersembunyi - model hanya mengenali sidik optik lalu menyalin nilai dari rekaman lain milik orang yang sama

**Hasil - penerapan dan pelatihan:**
- Endpoint `POST /v1/calibrate/train` dengan tiga mode: data asli, data demo, atau keduanya
- Dua tombol pelatihan terpisah di dashboard, sehingga pelatihan tidak perlu lewat terminal lagi
- Laporan pelatihan dapat diunduh sebagai HTML lengkap dengan scatter plot dan penjelasan awam
- Tiap target membawa status keterandalan: **TIDAK VALID** di bawah 10 subjek, **LEMAH** pada 10–29 subjek, **MEMADAI** pada 30 subjek ke atas
- **Hasil pelatihan pada data yang terkumpul belum layak dipakai.** Dibandingkan tolok ukur menebak nilai rata-rata tanpa memakai sensor sama sekali, MLP kalah pada 3 dari 5 parameter:

| Parameter | MAE MLP | MAE tebak rata-rata | R² MLP |
|---|---|---|---|
| Gula Darah | 45,09 | **37,20** | −1,565 |
| Kolesterol | 51,51 | **25,40** | −3,723 |
| Asam Urat | **0,46** | 0,70 | +0,055 |
| Sistolik | 22,30 | **15,80** | −1,321 |
| Diastolik | **6,00** | 8,60 | +0,297 |

- Sebabnya jelas: tujuh fitur dilatih dari lima baris data, sehingga persamaannya lebih sedikit daripada variabel yang dicari
- Tiga persoalan komposisi dicatat untuk pengujian smartband berikutnya: belum ada subjek berkolesterol di bawah 200 mg/dL, usia berhimpit dengan kondisi penyakit, dan jumlah subjek masih 5 dari target 30
- Angka di atas **tidak dilaporkan sebagai capaian**, melainkan sebagai penanda bahwa pengumpulan data harus dilanjutkan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_perbandingan mlp dan regresi linier.png` - notebook `model/mlp_rancangan_15agustus.ipynb` bagian 1
- `ADAM_aturan penskalaan kapasitas mlp.png` - notebook yang sama bagian 3
- `ADAM_uji kebocoran validasi silang.png` - notebook yang sama bagian 4
- `ADAM_tombol pelatihan mlp di dashboard.png` - kartu Pelatihan MLP dengan dua tombol
- `ADAM_perbandingan mlp dengan tebakan rata rata.png` - notebook `model/pelatihan_mlp_16agustus.ipynb`
- `ADAM_status keterandalan tiap target.png` - hasil pelatihan menampilkan status TIDAK VALID

---

### Minggu ke-14 - 19–23 Agustus 2026

---

**Sabtu, 23 Agustus 2026 - 360 menit**
*Kegiatan tim: Workshop Internal Teknis Pengajuan Hak Cipta*

**Kegiatan:**
Memastikan integrasi aplikasi mobile Flutter dengan API backend secara menyeluruh, sehingga data yang diproses server benar-benar sampai ke layar keluarga. Menelusuri sebab beberapa kartu vital yang masih kosong di aplikasi. Selain itu membangun fitur agar berkas APK dapat diunduh langsung dari halaman muka situs ANTARAGA, beserta pengelolaan unggah dan hapus dari dashboard.

**Hasil - integrasi aplikasi mobile:**
- Lapisan `ApiService` menyambung ke sembilan endpoint: pendaftaran, masuk, profil, pemasangan perangkat, vital terbaru, riwayat vital, prediksi risiko, asesmen ABCD², dan pendaftaran token notifikasi
- **Ditemukan bug**: pipeline penerimaan data hanya memeriksa artefak `ppg_vitals_model.joblib` yang tidak pernah dibuat, sehingga MLP kalibrasi yang sudah dilatih tidak pernah terpakai dan seluruh tahap hilir dilewati. Diperbaiki dengan menambahkan cabang yang memakai `mlp_calibration.joblib`, dengan usia dan jenis kelamin diambil dari profil yang di-pair lewat aplikasi
- **Ditemukan bug kedua**: penulisan f-string yang tidak sah membuat penghitungan penanda risiko melempar galat setiap kali tekanan darah tinggi, dan tab MLP diam-diam berubah menjadi tidak tersedia tanpa pesan apa pun
- **Ditemukan bug ketiga**: kartu Detak Jantung tetap menampilkan tanda hubung. Kolom `heart_rate_bpm` sudah ada di tabel `vital_readings` tetapi tidak pernah diisi saat penyimpanan. Diperbaiki dengan mengisinya dari BPM yang sudah lewat penyaring lonjakan
- **Ditemukan bug keempat**: tab XGBoost di dashboard tersangkut pada tulisan "Menunggu data" padahal server mengembalikan hasil dengan benar. Sebabnya keenam fungsi penggambar dipanggil berderet tanpa pengaman - bila satu melempar galat, seluruh fungsi sesudahnya tidak pernah dijalankan. Diperbaiki dengan membungkus tiap penggambar secara terisolasi
- Notifikasi FCM diuji untuk tiga keadaan: aplikasi terbuka, di latar belakang, dan tertutup

**Hasil - distribusi APK:**
- Modul `api/apk.py`: unggah APK, riwayat versi, penghapusan, dan pengaturan tautan toko aplikasi
- Tautan unduh publik `/download/app.apk` dibuat tetap tanpa nomor versi, sehingga tautan yang sudah tersebar di proposal atau kode QR tidak perlu diganti setiap rilis
- Ketiga tombol di halaman muka dilayani satu sumber: Unduh Gratis dan Google Play mengunduh APK bila tautan toko belum tersedia, sedangkan App Store dinonaktifkan karena iOS tidak dapat memasang berkas Android
- **Ditemukan kendala**: unggahan ditolak dengan galat `413 Request Entity Too Large`. Batas bawaan nginx hanya 1 MB, sehingga berkas ditolak sebelum permintaannya sampai ke aplikasi. Diperbaiki dengan `client_max_body_size 350M`, perpanjangan tenggat waktu, dan mematikan penampungan permintaan
- Modal progres unggah memakai `XMLHttpRequest` karena `fetch()` belum mendukung pelaporan progres unggah
- Volume `antaraga-apk` ditambahkan agar berkas bertahan melewati pembaruan container
- Diuji dengan berkas 45 MB: terunggah dan terunduh kembali dengan SHA-256 identik

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_aplikasi mobile menampilkan vital lengkap.png` - layar dashboard aplikasi dengan ketiga kartu terisi
- `ADAM_alur ujung ke ujung mlp dan xgboost.png` - respons endpoint dengan kedua tahap tersedia
- `ADAM_perbaikan isolasi galat penggambar.png` - fungsi pembungkus di dashboard
- `ADAM_notifikasi fcm diterima di ponsel.png` - tangkapan layar notifikasi
- `ADAM_kartu pengelolaan apk di dashboard.png` - dashboard tab Firmware
- `ADAM_tombol unduh di halaman muka.png` - halaman muka dengan ketiga tombol
- `ADAM_perbaikan batas unggah nginx.png` - `scripts/nginx_antaraga.conf`

---

### Minggu ke-15 - 26–30 Agustus 2026

---

**Selasa, 26 Agustus 2026 - 180 menit**
*Kegiatan tim: Workshop Teknik Presentasi PKP2*

**Kegiatan:**
Mengikuti Workshop Teknik Presentasi PKP2 yang diselenggarakan PKM Center PENS, sekaligus menyiapkan kerangka bagian teknis yang akan dibawakan.

**Hasil:**
- Memahami struktur presentasi yang diharapkan penilai: latar belakang, kebaruan, metode, capaian terukur, dan rencana lanjutan
- Kerangka bagian teknis disusun dengan penekanan pada capaian yang dapat diangkakan: ROC-AUC 0,823, recall 0,973, dan dua belas fitur aplikasi mobile yang berjalan
- Disiapkan antisipasi pertanyaan tersulit: alasan presisi 0,075, jumlah data kalibrasi yang masih 5 subjek, dan pembeda dengan penelitian terdahulu
- Catatan dari pemateri: setiap klaim harus dapat ditunjukkan buktinya saat sesi tanya jawab, sehingga seluruh angka disiapkan bersama notebook pendukungnya

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_workshop teknik presentasi pkp2.png` - foto saat mengikuti workshop
- `ADAM_kerangka presentasi bagian teknis.png` - kerangka yang disusun

---

**Kamis, 28 Agustus 2026 - 360 menit**
*Kegiatan tim: Asistensi laporan kemajuan ke dosen pendamping*

**Kegiatan:**
Menyusun bagian perangkat lunak dan kecerdasan buatan pada laporan kemajuan, lalu mengasistensikannya ke dosen pendamping.

**Hasil:**
- Rangkuman capaian model XGBoost: ROC-AUC 0,823, recall 0,973 (73 dari 75 penderita terdeteksi), ambang deteksi 0,042 yang ditetapkan lewat target recall pada prediksi out-of-fold
- Rangkuman aplikasi mobile: dua belas fitur berjalan, tersambung ke sembilan endpoint
- Rangkuman infrastruktur: backend daring di www.antaraga.web.id, penerapan otomatis, dashboard pemantauan, pembaruan firmware jarak jauh
- Daftar dua belas kendala beserta solusinya disusun dalam bentuk rantai masalah sampai penyelesaian
- Dinyatakan terus terang bahwa model MLP kalibrasi **belum layak dilaporkan sebagai capaian** karena baru terkumpul 5 dari 30 subjek yang dibutuhkan
- Perbandingan dengan skor klinis ABCD² disiapkan sebagai pembelaan atas presisi rendah: ABCD² yang dirujuk pedoman AHA bekerja pada sensitivitas 0,89 dengan PPV 0,08, sedangkan ANTARAGA 0,973 dengan PPV 0,075

*(Catatan hasil asistensi perlu dilengkapi sesuai masukan yang sebenarnya diberikan dosen pendamping.)*

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_bagian software laporan kemajuan.png` - dokumen laporan bagian perangkat lunak
- `ADAM_daftar kendala dan solusi.png` - tabel dua belas kendala
- `ADAM_asistensi laporan ke dosen pendamping.png` - foto saat asistensi

---

**Jumat, 29 Agustus 2026 - 300 menit**
*Kegiatan tim: finalisasi dan pengunggahan Pengiklanan Konten Medsos 3*

**Kegiatan:**
Menyiapkan bahan teknis untuk konten media sosial ketiga, berupa peragaan sistem ANTARAGA yang sedang berjalan, lalu membantu proses finalisasi dan pengunggahannya.

**Hasil:**
- Rekaman layar dashboard pemantauan dengan sinyal PPG tiga kanal berjalan
- Rekaman layar aplikasi mobile menampilkan kartu vital dan tingkat risiko
- Peragaan alur peringatan dini: sinyal masuk, model memprediksi, notifikasi sampai ke ponsel keluarga
- Bahan diserahkan ke anggota tim yang menangani konten, lalu ikut memeriksa hasil suntingan agar penjelasan teknisnya tidak keliru
- Dipastikan tidak ada kredensial, alamat server internal, maupun data subjek yang ikut terekam dalam tayangan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_rekaman layar dashboard untuk konten.png` - cuplikan rekaman dashboard
- `ADAM_rekaman layar aplikasi mobile.png` - cuplikan rekaman aplikasi
- `ADAM_konten medsos 3 terunggah.png` - unggahan di media sosial

---

**Sabtu, 30 Agustus 2026 - 300 menit**
*Kegiatan tim: pengujian 5 smartband ANTARAGA*

**Kegiatan:**
Mengikuti pengujian smartband kelima untuk menambah data kalibrasi, dengan prioritas komposisi subjek yang memperbaiki tiga persoalan yang tercatat pada 16 Agustus.

**Hasil:**
- Perekaman mengikuti `docs/protokol_kalibrasi.md`: subjek duduk tenang, lengan setinggi jantung, tidak bicara dan tidak menggerakkan tangan selama perekaman
- Prioritas subjek yang dicari: berkolesterol di bawah 200 mg/dL, usia di bawah 50 tahun, serta lansia bertekanan darah normal - untuk memutus keterkaitan usia dengan kondisi penyakit
- Verifikasi sebelum menyimpan tiap rekaman: menunggu 15 detik setelah sinyal stabil, membandingkan BPM tersaring dengan nadi manual, dan memeriksa perfusi inframerah berada di rentang 0,5–3,0‰
- Dataset diekspor sebagai cadangan di akhir sesi

*(Jumlah subjek yang berhasil direkam beserta rentang nilainya perlu dilengkapi sesuai hasil sesi.)*

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_sesi pengujian 5 smartband.png` - foto perekaman bersama subjek
- `ADAM_dataset kalibrasi bertambah.png` - tabel dataset dengan jumlah subjek terbaru
- `ADAM_verifikasi bpm sebelum simpan.png` - kartu BPM Tersaring saat perekaman

---

### Minggu ke-16 - 2–6 September 2026

> **Catatan:** entri mulai bagian ini adalah **rencana kerja**, bukan kegiatan yang sudah terlaksana. Kolom Hasil perlu diperbarui sesuai kenyataan setelah kegiatannya berlangsung.

---

**Rabu, 2 September 2026 - 300 menit**
*Kegiatan tim: pengujian 6 smartband ANTARAGA*

**Kegiatan:**
Pengujian smartband keenam untuk melanjutkan pengumpulan data kalibrasi, sekaligus melatih ulang model MLP dengan data yang sudah bertambah.

**Rencana hasil:**
- Penambahan subjek dengan komposisi yang masih kurang, terutama subjek berkolesterol normal dan usia di bawah 50 tahun
- Pelatihan ulang lewat dashboard dengan mode data asli; kapasitas jaringan otomatis menyesuaikan jumlah data
- Perbandingan terhadap tolok ukur menebak nilai rata-rata untuk memastikan model benar-benar memberi tambahan informasi
- Pemeriksaan status keterandalan tiap parameter, dilaporkan apa adanya bila masih TIDAK VALID atau LEMAH
- Bila jumlah subjek melewati 30, validasi silang otomatis beralih ke 5-fold dan metriknya mulai dapat dilaporkan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_sesi pengujian 6 smartband.png` - foto perekaman
- `ADAM_hasil pelatihan ulang mlp.png` - kartu Pelatihan MLP dengan metrik terbaru
- `ADAM_perbandingan metrik sebelum sesudah.png` - perbandingan dengan hasil 16 Agustus

---

**Minggu, 6 September 2026 - 600 menit**
*Kegiatan tim: pembuatan laporan akhir dan pengujian 7 smartband ANTARAGA*

**Kegiatan:**
Pengujian smartband ketujuh sekaligus memulai penyusunan laporan akhir bagian perangkat lunak dan kecerdasan buatan.

**Rencana hasil - pengujian:**
- Sesi perekaman terakhir sebelum penilaian kemajuan, dengan target melengkapi komposisi subjek
- Pelatihan ulang final dan penetapan artefak model yang akan dilaporkan
- Pemeriksaan bahwa artefak di server sama dengan yang dilaporkan

**Rencana hasil - laporan akhir:**
- Bagian metode: alur pengembangan model XGBoost dan MLP beserta dasar tiap keputusan
- Bagian hasil: metrik final, capaian aplikasi mobile, dan infrastruktur yang berjalan
- Bagian pembahasan: alasan pengutamaan recall pada alat skrining, disertai perbandingan dengan skor klinis ABCD²
- Bagian keterbatasan ditulis apa adanya: jumlah data kalibrasi, presisi rendah, dan kendala penyambungan WiFi pada firmware

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_sesi pengujian 7 smartband.png` - foto perekaman
- `ADAM_artefak model final.png` - daftar berkas artefak beserta metriknya
- `ADAM_laporan akhir bagian software.png` - dokumen laporan akhir

---

### Minggu ke-17 - 9–13 September 2026

---

**Jumat, 12 September 2026 - 450 menit**

**Kegiatan:**
Melanjutkan penyusunan laporan akhir, sekaligus menyiapkan demonstrasi sistem untuk Penilaian Kemajuan Program PKM (PKP2).

**Rencana hasil:**
- Penyelesaian bagian hasil dan pembahasan laporan akhir
- Skenario peragaan tersusun: dari memasang smartband sampai notifikasi sampai ke ponsel keluarga
- Simulator perangkat keras disiapkan sebagai cadangan bila alat bermasalah saat demo
- Data demo disiapkan agar dashboard tetap menampilkan hasil bila jaringan bermasalah
- Bahan tanya jawab teknis disiapkan, terutama untuk pertanyaan soal presisi rendah dan jumlah data kalibrasi
- Pemeriksaan seluruh layanan: backend daring, dashboard, aplikasi mobile, dan notifikasi

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_skenario demonstrasi pkp2.png` - dokumen skenario peragaan
- `ADAM_pemeriksaan seluruh layanan.png` - daftar periksa kesiapan sistem
- `ADAM_bahan tanya jawab teknis.png` - catatan antisipasi pertanyaan penilai

---

### Minggu ke-18 - 14–20 September 2026

---

**14–19 September 2026 - 450 menit**
*Pelaksanaan Penilaian Kemajuan Program PKM (PKP2)*

**Kegiatan:**
Mengikuti rangkaian PKP2 sesuai jadwal penyelenggara, membawakan bagian teknis perangkat lunak dan kecerdasan buatan.

**Rencana hasil:**
*(Diisi setelah pelaksanaan: hasil penilaian, pertanyaan yang diajukan penilai, serta masukan yang diberikan.)*

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_pelaksanaan pkp2.png` - foto saat presentasi
- `ADAM_catatan masukan penilai.png` - catatan pertanyaan dan masukan

---

**Sabtu, 20 September 2026 - 450 menit**

**Kegiatan:**
Finalisasi laporan akhir berdasarkan masukan penilai PKP2, sekaligus menerapkan perbaikan pada sisi perangkat lunak.

**Rencana hasil:**
- Rangkuman pertanyaan dan masukan penilai
- Penyesuaian cara penyajian metrik bila penilai menilai kurang jelas
- Penambahan bukti pendukung untuk klaim yang dipertanyakan
- Perbaikan tampilan atau alur yang mendapat catatan

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_perbaikan berdasarkan masukan penilai.png` - perbandingan sebelum dan sesudah
- `ADAM_daftar tindak lanjut pkp2.png` - daftar prioritas perbaikan

---

### Minggu ke-19 - 23–25 September 2026

---

**Selasa, 23 September 2026 - 300 menit**

**Kegiatan:**
Finalisasi seluruh komponen perangkat lunak: pemeriksaan menyeluruh, pembersihan kode, dan penyiapan arsip repositori.

**Rencana hasil:**
- Pemeriksaan menyeluruh seluruh layanan berjalan tanpa galat
- Pembersihan kode yang tidak terpakai dan pemutakhiran dokumentasi
- Penandaan versi rilis pada repositori
- Cadangan basis data, artefak model, dan dataset kalibrasi

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_pemeriksaan akhir seluruh layanan.png` - daftar periksa lengkap
- `ADAM_penandaan versi rilis repositori.png` - riwayat git dengan penanda versi

---

**Rabu, 24 September 2026 - 450 menit**
*Kegiatan tim: pembuatan laporan akhir dan asistensi ke dosen pendamping*

**Kegiatan:**
Menyelesaikan laporan akhir bagian perangkat lunak dan kecerdasan buatan, lalu mengasistensikannya ke dosen pendamping untuk pemeriksaan akhir.

**Rencana hasil:**
- Seluruh bagian laporan akhir terselesaikan beserta lampiran bukti
- Angka yang dilaporkan diverifikasi ulang terhadap artefak model yang berjalan di server
- Asistensi ke dosen pendamping dan penerapan revisi yang diminta

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_laporan akhir lengkap.png` - dokumen laporan akhir
- `ADAM_asistensi laporan akhir.png` - foto saat asistensi

---

**Kamis, 25 September 2026 - 300 menit**

**Kegiatan:**
Penyerahan laporan akhir dan pengarsipan seluruh dokumentasi teknis proyek.

**Rencana hasil:**
- Laporan akhir diserahkan sesuai ketentuan
- Seluruh notebook, kode, dan dokumentasi diarsipkan di repositori
- Logbook diperiksa kelengkapannya beserta bukti dokumentasi tiap entri
- Serah terima akses server, domain, dan repositori kepada tim
- Catatan pengembangan lanjutan disusun: pengumpulan data kalibrasi sampai 30 subjek, pelatihan ulang MLP, perbaikan penyambungan WiFi pada firmware, dan penambahan estimasi SpO2 setelah alat pembanding tersedia

📸 **Bukti yang perlu dilampirkan:**
- `ADAM_penyerahan laporan akhir.png` - bukti penyerahan
- `ADAM_arsip repositori lengkap.png` - struktur repositori final
- `ADAM_catatan pengembangan lanjutan.png` - dokumen rencana lanjutan

---

## REKAP TOTAL

| Komponen | Total Minggu | Total Menit |
|---|---|---|
| Minggu ke-1 (parsial) | - | 360 menit |
| Minggu ke-2 s/d ke-18 (penuh) | 17 minggu | 15.300 menit |
| Minggu ke-19 (parsial) | - | 360 menit |
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
