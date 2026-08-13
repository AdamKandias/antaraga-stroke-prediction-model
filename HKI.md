# PETA SOURCE CODE — DOKUMEN HKI ANTARAGA

**Judul Ciptaan:** ANTARAGA: Smartband Berbasis Multi-Wavelength PPG dengan Artificial
Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia
(Program Komputer)

**Program:** Program Kreativitas Mahasiswa — Karsa Cipta (PKM-KC) 2026
**Institusi:** Politeknik Elektronika Negeri Surabaya (PENS)

**Pencipta:** Agrippina Waya Rahmaning Gusti, S.T., M.T. · Kadek Savita Dyutianaya ·
Kalyana Daeva Ali · Adam Kandias · Jonzeven La Royba · Ni Komang Diah Pratiwi

---

## CARA MEMBACA DOKUMEN INI

Dokumen ini adalah **peta source code** untuk lampiran HKI. Setiap baris tabel menunjuk ke
satu fitur atau halaman, lengkap dengan nama berkas, rentang baris, dan penjelasan fungsinya.

Nomor baris mengacu pada kondisi repositori saat dokumen ini disusun. Bila kode berubah,
rentangnya ikut bergeser — cara memperbaruinya ada di [Lampiran B](#lampiran-b--memperbarui-nomor-baris).

**Ruang lingkup:** dokumen ini mencakup **dua repositori**:

| Repositori | Isi | Ditulis di |
|---|---|---|
| `stroke-prediction-model/` | Backend, web dashboard, model AI, firmware | Bagian A–D |
| `antaraga/` | Aplikasi mobile Flutter | [Bagian E](#bagian-e--aplikasi-mobile-flutter) |

Rujukan berkas pada Bagian A–D relatif terhadap `stroke-prediction-model/`, sedangkan
pada Bagian E relatif terhadap `antaraga/`.

---

## RINGKASAN ARSITEKTUR

Ekosistem ANTARAGA terdiri atas lima komponen perangkat lunak yang saling terhubung:

| # | Komponen | Lokasi | Bahasa | Baris |
|---|---|---|---|---|
| 1 | **Backend / Server API** | `api/` | Python (FastAPI) | ±4.700 |
| 2 | **Web App (Dashboard Riset)** | `api/static/dashboard.html` | HTML/CSS/JavaScript | 2.503 |
| 3 | **Model AI** | `model/` | Python (scikit-learn, XGBoost) | ±1.050 |
| 4 | **Firmware Smartband** | `Firmware/` | C++ (Arduino/ESP-IDF) | ±1.850 |
| 5 | **Aplikasi Mobile** | `antaraga/lib/` | Dart (Flutter) | 4.531 |

Alur data lengkapnya:

```
Smartband (XIAO ESP32-S3)                 Backend (FastAPI)                 Aplikasi Mobile
─────────────────────────                 ─────────────────                 ───────────────
 Sensor PPG 3 kanal                        POST /v1/ingest
 (hijau / merah / inframerah)   ─Wi-Fi──▶  ├─ Pulse Wave Analysis
 + penilaian mutu sinyal (SQI)             ├─ MLP  → tekanan darah, gula darah
                                           ├─ Gradient Boosting → risiko stroke
                                           ├─ Simpan ke basis data
                                           └─ Push notification (FCM) ──────▶ Peringatan dini
                                                                                    │
                                           POST /assessment/abcd2  ◀─────────── Assessment ABCD2
                                           └─ Stratifikasi rendah/sedang/tinggi ──▶ Rekomendasi
                                                                                    │
                                           GET /vitals/latest, /vitals/history ──▶ Dashboard & Statistik

                              Web Dashboard (internal tim riset)
                              ──────────────────────────────────
                              /login → /dashboard
                              Monitoring sinyal mentah, kalibrasi sensor,
                              pelatihan model, manajemen firmware OTA
```

---

## PETA REPOSITORI

```
stroke-prediction-model/
├── api/                          BACKEND — server FastAPI
│   ├── main.py             2.548 Seluruh endpoint HTTP & WebSocket
│   ├── calib_report.py       736 Laporan hasil pemeriksaan siap cetak (PDF)
│   ├── bpm_engine.py         291 Perhitungan denyut jantung (deteksi puncak)
│   ├── ota.py                276 Pembaruan firmware jarak jauh
│   ├── hw_simulator.py       250 Simulator sinyal sensor untuk pengujian
│   ├── ppg_analysis.py       248 Pengolahan sinyal PPG
│   ├── schemas.py            231 Kontrak data permintaan & tanggapan
│   ├── bpm_filter.py         177 Penyaring lonjakan nilai denyut
│   ├── firmware.py           169 Kompilasi & flashing firmware dari web
│   ├── models_db.py          156 Skema basis data
│   ├── dashboard_auth.py     140 Sesi login dashboard
│   ├── simulator.py          127 Simulator data vital mode pengembangan
│   ├── profile_utils.py      115 Turunan profil & penanda risiko
│   ├── ml_calibration.py     110 Inferensi model MLP kalibrasi
│   ├── fcm.py                 96 Push notification Firebase
│   ├── ml.py                  90 Inferensi model risiko stroke
│   ├── auth.py                88 Token akses aplikasi mobile
│   ├── logging_utils.py       78 Pencatatan akses & prediksi
│   ├── login_page.py          76 Halaman login dashboard
│   ├── ingest_buffer.py       64 Penyangga sinyal di memori
│   ├── pwa_config.py          43 Konfigurasi parameter analisis
│   ├── database.py            20 Koneksi basis data
│   ├── security.py             9 Hashing kata sandi
│   └── static/
│       ├── dashboard.html  2.503 WEB APP — dashboard riset
│       └── index.html      1.220 Halaman publik (landing page)
│
├── model/                        MODEL AI
│   ├── train_mlp_calibration.py  295 Pelatihan MLP estimasi vital
│   ├── train.py                  286 Pelatihan Gradient Boosting risiko stroke
│   ├── ppg_features.py           230 Ekstraksi fitur Pulse Wave Analysis
│   ├── train_ppg_vitals.py       142 Pelatihan awal estimasi vital
│   └── abcd2.py                   98 Skoring ABCD2
│
├── Firmware/                     FIRMWARE SMARTBAND (XIAO ESP32-S3)
│   ├── src/cloud.cpp             594 Wi-Fi, TLS, pengiriman data, OTA
│   ├── src/sensors.cpp           464 Driver MAX30102 & SON1303
│   ├── src/sqi.cpp               267 Penilaian mutu sinyal
│   ├── src/main.cpp              270 Alur utama perangkat
│   ├── include/config.h          276 Parameter yang dapat disetel
│   └── include/antaraga.h        182 Definisi pin & struktur data
│
└── assets/icon-antaraga.png      Logo untuk laporan & halaman login
```

Repositori aplikasi mobile (`antaraga/`):

```
antaraga/
├── lib/
│   ├── main.dart                       214 Titik masuk & penentuan halaman awal
│   ├── screens/                            HALAMAN APLIKASI
│   │   ├── dashboard_screen.dart     1.158 Dashboard Utama + Hubungkan Perangkat
│   │   ├── daily_stats_screen.dart     642 Statistik Harian
│   │   ├── profile_form_screen.dart    456 Profil Orang Tua/Lansia
│   │   ├── vital_detail_screen.dart    338 Detail per parameter (BPM, dll.)
│   │   ├── assessment_form_screen.dart 230 Assessment ABCD2
│   │   ├── login_screen.dart           223 Daftar Akun Keluarga & Masuk
│   │   └── splash_screen.dart          107 Layar pembuka
│   ├── services/                           PENGHUBUNG KE BACKEND
│   │   ├── api_service.dart            226 Seluruh pemanggilan API
│   │   ├── demo_service.dart           183 Mode demo tanpa perangkat keras
│   │   ├── fcm_service.dart            125 Penerimaan peringatan dini
│   │   ├── auth_service.dart           109 Pendaftaran, masuk, penyimpanan token
│   │   ├── risk_service.dart            79 Penilaian risiko lokal
│   │   └── profile_service.dart         44 Penyimpanan profil di perangkat
│   ├── models/                             STRUKTUR DATA
│   │   ├── user_profile.dart           137 Profil lansia
│   │   ├── api_results.dart             78 Hasil prediksi & asesmen dari server
│   │   ├── assessment.dart              64 Hasil skoring ABCD2
│   │   └── vital_data.dart              50 Satu pembacaan vital
│   └── core/
│       ├── constants/vital_ranges.dart  76 Ambang & indikator warna vital
│       ├── constants/app_constants.dart 21 Alamat server & mode aplikasi
│       ├── theme/app_theme.dart        113 Tema aplikasi
│       └── theme/app_colors.dart        44 Palet warna
└── assets/                                 Logo & ikon aplikasi
```

---

# BAGIAN A — BACKEND / SERVER API

Berkas: `api/`. Kerangka kerja FastAPI, basis data SQLAlchemy (SQLite/PostgreSQL).

## A.1 Titik Masuk & Konfigurasi Server

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/main.py` | 1–50 | Impor & pendaftaran modul | Menyatukan seluruh modul: autentikasi, basis data, model AI, notifikasi, OTA. |
| `api/main.py` | 41–50 | Siklus hidup aplikasi | `lifespan()` — menyalakan simulator perangkat keras saat mode pengembangan dan mematikannya saat server berhenti. |
| `api/main.py` | 52–66 | Inisialisasi & CORS | Pembuatan objek aplikasi dan izin lintas-asal agar aplikasi mobile dapat memanggil API. |
| `api/main.py` | 93–147 | Pencatatan akses | Middleware yang mencatat setiap permintaan: IP, metode, jalur, kode status, dan lama proses. |
| `api/config.py` | 1–60 | Konfigurasi terpusat | Seluruh pengaturan dibaca sekali dari berkas `.env`: koneksi basis data, kunci token, kunci perangkat keras, akun dashboard. |
| `api/database.py` | 1–20 | Koneksi basis data | Pembuatan mesin SQLAlchemy dan penyedia sesi per permintaan. |
| `api/logging_utils.py` | 1–78 | Pencatatan prediksi | Menyimpan setiap panggilan model AI beserta masukan, keluaran, dan lama proses ke tabel `prediction_logs`. |

## A.2 Autentikasi & Keamanan

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/security.py` | 1–9 | Pengamanan kata sandi | Hashing bcrypt — kata sandi tidak pernah disimpan dalam bentuk asli. |
| `api/auth.py` | 25–33 | Penerbitan token akses | `create_access_token()` — membuat JWT bertanda tangan berisi identitas pengguna dan masa berlaku. |
| `api/auth.py` | 35–66 | Verifikasi token | `get_current_user_id()` — memeriksa keaslian dan masa berlaku token pada setiap permintaan aplikasi mobile. |
| `api/auth.py` | 68–88 | Autentikasi perangkat keras | `get_ingest_user_id()` — menerima kunci statis firmware yang tidak dapat memperbarui JWT sendiri. |
| `api/main.py` | 173–195 | **Halaman Daftar Akun Keluarga** | `POST /auth/register` — pendaftaran dengan email **atau** nomor HP, memeriksa duplikasi, langsung menerbitkan token. |
| `api/main.py` | 198–212 | **Halaman Masuk (Login)** | `POST /auth/login` — verifikasi kredensial dan penerbitan token akses. |
| `api/main.py` | 215–222 | Identitas pengguna aktif | `GET /auth/me` — mengembalikan data akun pemilik token. |

## A.3 Skema Basis Data

| Berkas | Baris | Entitas | Penjelasan |
|---|---|---|---|
| `api/models_db.py` | 9–49 | `User` | Akun keluarga: email/telepon, kata sandi terenkripsi, token notifikasi, dan perangkat yang dipasangkan. |
| `api/models_db.py` | 52–77 | `Profile` | Data lansia yang dipantau: demografi, riwayat penyakit jantung, diabetes, riwayat keluarga stroke, status merokok. Satu akun dapat memantau beberapa lansia. |
| `api/models_db.py` | 79–96 | `VitalReading` | Riwayat pembacaan vital: tekanan darah, denyut jantung, gula darah, beserta waktu pengukuran. |
| `api/models_db.py` | 98–137 | `CalibrationRecord` | Sesi kalibrasi: sinyal PPG mentah tiga kanal berdampingan dengan nilai alat medis rujukan. |
| `api/models_db.py` | 139–156 | `PredictionLog` | Jejak audit setiap pemanggilan model AI. |
| `api/schemas.py` | 1–231 | Kontrak data | Validasi seluruh permintaan dan tanggapan HTTP; menolak data di luar rentang wajar sebelum masuk ke logika inti. |

## A.4 Endpoint Aplikasi Mobile

Setiap baris di bawah ini melayani satu halaman pada aplikasi mobile.

| Berkas | Baris | Halaman Mobile | Penjelasan |
|---|---|---|---|
| `api/main.py` | 238–271 | **Halaman Profil Orang Tua/Lansia** | `POST /profiles` — menyimpan data lansia dan menghitung usia otomatis dari tanggal lahir. Profil pertama menjadi profil aktif. |
| `api/main.py` | 225–235 | Daftar lansia dipantau | `GET /profiles` — seluruh profil milik satu akun keluarga. |
| `api/main.py` | 274–296 | Pemilihan profil aktif | `GET /profiles/active` dan `GET /profiles/{id}` — menentukan lansia yang sedang ditampilkan. |
| `api/main.py` | 299–324 | Penyuntingan profil | `PUT /profiles/{id}` — pembaruan sebagian data tanpa menghapus kolom lain. |
| `api/main.py` | 327–343 | Pergantian profil | `POST /profiles/{id}/select` — berpindah lansia yang dipantau. |
| `api/main.py` | 661–688 | **Halaman Hubungkan Perangkat** | `POST /device/pair` — memasangkan Device ID smartband (mis. `antaraga-001`) ke akun keluarga. |
| `api/main.py` | 691–700 | Status perangkat | `GET /device/status` — menampilkan perangkat yang sedang terhubung. |
| `api/main.py` | 1031–1050 | Validasi Device ID | `GET /v1/devices/{id}/check` — memastikan perangkat benar-benar ada sebelum dipasangkan. |
| `api/main.py` | 382–427 | **Halaman Dashboard Utama** | `GET /vitals/latest` — kartu tekanan darah, denyut jantung, dan gula darah terbaru beserta indikator status warna. |
| `api/main.py` | 430–463 | **Halaman Statistik Harian** & **Detak Jantung (BPM)** | `GET /vitals/history` — riwayat pembacaan untuk grafik tren dan linimasa per jam. |
| `api/main.py` | 346–379 | **Prediksi Risiko (AI)** | `POST /predict/stroke-risk` — menggabungkan profil dan data vital, menjalankan model Gradient Boosting, mengembalikan tingkat risiko beserta penanda faktor risiko. |
| `api/main.py` | 466–497 | **Halaman Assessment ABCD2** | `POST /assessment/abcd2` — skoring lima kategori (usia, tekanan darah, fitur klinis, durasi gejala, diabetes), menghasilkan stratifikasi rendah/sedang/tinggi beserta rekomendasi tindakan. |
| `api/main.py` | 500–545 | Estimasi vital dari PPG | `POST /estimate/vitals-from-ppg` — mengubah sinyal PPG mentah menjadi estimasi vital melalui model MLP. |
| `api/main.py` | 160–170 | Pendaftaran notifikasi | `POST /device/register-token` — menyimpan token FCM perangkat agar dapat menerima peringatan dini. |
| `api/profile_utils.py` | 15–115 | Logika pendukung profil | Perhitungan usia dari tanggal lahir (15–21), penurunan status hipertensi (22–27), pemilihan profil aktif (28–48), penyimpanan pembacaan vital (49–73), penyusunan fitur untuk model AI (74–90), dan penentuan penanda risiko (91–115). |

## A.5 Penerimaan Data Smartband — Alur Inti Peringatan Dini

Blok ini merupakan **mekanisme inti ANTARAGA**: dari sinyal mentah smartband hingga
push notification ke aplikasi keluarga, seluruhnya berjalan dalam satu permintaan.

| Berkas | Baris | Tahap | Penjelasan |
|---|---|---|---|
| `api/main.py` | 703–730 | Penerimaan batch | `POST /v1/ingest` — menerima kiriman sinyal dari firmware, mencari akun pemilik perangkat, menyimpan ke penyangga memori. |
| `api/main.py` | 731–808 | Tahap 1 — Estimasi vital | Pulse Wave Analysis atas sinyal PPG, lalu inferensi MLP menghasilkan tekanan darah dan gula darah tidak puasa. |
| `api/main.py` | 809–816 | Tahap 2 — Prediksi risiko | Estimasi vital digabung dengan profil lansia, dijalankan melalui model Gradient Boosting. |
| `api/main.py` | 817–851 | Tahap 3 — Penyimpanan | Hasil disimpan sebagai `VitalReading` sehingga muncul di Dashboard Utama dan Statistik Harian aplikasi. |
| `api/main.py` | 852–869 | Tahap 4 — Peringatan dini | Bila risiko **HIGH**, push notification dikirim ke aplikasi keluarga. Dilengkapi jeda antar-notifikasi agar tidak mengirim berulang-ulang. |
| `api/main.py` | 872–932 | Penyaring mutu sinyal | Batch bermutu buruk (jari bergerak, perfusi lemah, sensor lepas) dibuang sebelum dianalisis, agar estimasi tidak tercemar data sampah. |
| `api/ingest_buffer.py` | 1–64 | Penyangga sinyal | Menyimpan sinyal beberapa detik terakhir di memori untuk analisis real-time tanpa membebani basis data. |
| `api/fcm.py` | 23–96 | Pengiriman notifikasi | Integrasi Firebase Cloud Messaging; sistem tetap berjalan normal walau notifikasi tidak dikonfigurasi. |

## A.6 Pengolahan Sinyal PPG

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/ppg_analysis.py` | 18–37 | Rerata bergerak | `movavg()` — penghalusan sinyal dengan jendela terpangkas di tepi, mencegah kerusakan sinyal di ujung rekaman. |
| `api/ppg_analysis.py` | 39–41 | Penghilangan tren | `detrend()` — memisahkan komponen denyut dari pergeseran garis dasar. |
| `api/ppg_analysis.py` | 43–71 | Penapis pita | `ac_signal()` — Butterworth 0,5–5 Hz zero-phase: membuang drift termal dan modulasi napas di bawahnya, derau di atasnya, tanpa menggeser posisi puncak. |
| `api/ppg_analysis.py` | 74–130 | Denyut via autokorelasi | `bpm_autocorr()` — perhitungan denyut jantung melalui autokorelasi berbasis FFT beserta ukuran keyakinannya. |
| `api/ppg_analysis.py` | 150–191 | Statistik kanal | `channel_stats()` — komponen DC, amplitudo AC, dan indeks perfusi tiap kanal warna. |
| `api/ppg_analysis.py` | 193–219 | Estimasi regresi linier | `compute_linreg_vitals()` — estimasi awal gula darah, kolesterol, dan asam urat sebelum model terkalibrasi tersedia. |
| `api/bpm_engine.py` | 68–291 | Mesin denyut jantung | `compute_bpm()` — deteksi puncak dan median interval antar-denyut; port algoritma yang sama dengan firmware agar hasil server dan perangkat konsisten. |
| `api/bpm_filter.py` | 45–177 | Penyaring lonjakan denyut | Menolak lompatan nilai tidak wajar (*octave error*) dan menahan nilai terakhir yang sahih, sehingga angka denyut tidak berkedip-kedip. |
| `api/main.py` | 1140–1207 | Pulse Wave Analysis | `_compute_pwa()` — ekstraksi fitur morfologi gelombang denyut untuk masukan model MLP. |
| `api/main.py` | 1209–1258 | Analisis multi-kanal | `_compute_ppg_analysis()` — menjalankan analisis atas ketiga kanal warna sekaligus. |

## A.7 Inferensi Model AI

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/ml.py` | 22–28 | Pemuatan model | `load_artifact()` — memuat model Gradient Boosting terlatih beserta pra-pemrosesnya. |
| `api/ml.py` | 30–55 | Penentuan tingkat risiko | `_risk_level()` — mengubah probabilitas menjadi kategori rendah/sedang/tinggi berdasarkan ambang hasil pelatihan. |
| `api/ml.py` | 57–74 | Penyusunan fitur | `_build_row()` — menyusun fitur profil dan vital sesuai urutan yang dipakai saat pelatihan. |
| `api/ml.py` | 76–90 | Prediksi risiko stroke | `predict_stroke_risk()` — antarmuka utama model Gradient Boosting. |
| `api/ml_calibration.py` | 30–43 | Ketersediaan model | Memeriksa apakah model MLP hasil kalibrasi sudah dilatih. |
| `api/ml_calibration.py` | 45–80 | Prediksi vital | `predict_vitals()` — estimasi gula darah, kolesterol, asam urat, sistolik, dan diastolik dari fitur sinyal PPG. |
| `api/ml_calibration.py` | 82–110 | Penanda risiko dari vital | `compute_risk_flags_from_vitals()` — menandai nilai yang melewati ambang klinis. |
| `api/main.py` | 1275–1329 | Orkestrasi MLP | `_compute_mlp()` — menjalankan model kalibrasi atas sinyal terkini untuk ditampilkan di dashboard. |
| `api/main.py` | 1331–1374 | Orkestrasi Gradient Boosting | `_compute_xgboost()` — mengambil prediksi risiko terakhir dan menggabungkannya dengan penanda risiko profil. |

## A.8 Pembaruan Firmware Jarak Jauh (OTA)

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/ota.py` | 42–71 | Katalog firmware | Penyimpanan metadata dan status penyebaran tiap versi firmware. |
| `api/ota.py` | 73–126 | Pustaka firmware | Daftar dan unggah berkas firmware baru dari dashboard. |
| `api/ota.py` | 128–165 | Pengelolaan versi | Penyuntingan keterangan dan penghapusan versi lama. |
| `api/ota.py` | 167–214 | Penyebaran & status | Menetapkan versi yang harus dipasang perangkat, serta memantau perangkat yang sudah menerimanya. |
| `api/ota.py` | 216–276 | Endpoint perangkat | `/v1/ota/check`, `/v1/ota/firmware`, `/v1/ota/ack` — dipanggil smartband untuk memeriksa, mengunduh, dan mengonfirmasi pembaruan. |
| `api/firmware.py` | 35–169 | Kompilasi dari web | Pembacaan dan penulisan `config.h` (35–76), daftar program (102–150), serta kompilasi dan flashing dengan keluaran langsung ke layar (151–169). |

## A.9 Simulator & Perkakas Pengembangan

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/hw_simulator.py` | 50–119 | Sinyal PPG sintetis | Pembangkitan gelombang denyut tiruan beserta derau realistis, untuk menguji seluruh alur tanpa perangkat keras. |
| `api/simulator.py` | 35–127 | Simulator data vital | Pengiriman data vital berkala ke akun yang sedang aktif selama mode pengembangan. |
| `api/main.py` | 547–571 | Kendali simulator | `/v1/sim/start`, `/v1/sim/stop`, `/v1/sim/status` — menyalakan dan mematikan simulator dari dashboard. |
| `api/main.py` | 2484–2548 | Monitor serial | `GET /serial/ports` dan WebSocket `/serial/ws` — membaca keluaran serial smartband langsung dari peramban. |

---

# BAGIAN B — WEB APP (DASHBOARD RISET)

Berkas utama: `api/static/dashboard.html` (2.503 baris) — satu berkas mandiri berisi struktur,
gaya, dan logika. Dashboard ini **alat internal tim riset**, terpisah dari aplikasi mobile keluarga.

## B.1 Halaman Login & Pengamanan Akses

| Berkas | Baris | Halaman/Fitur | Penjelasan |
|---|---|---|---|
| `api/login_page.py` | 1–76 | **Halaman Login Dashboard** | Formulir masuk berlogo ANTARAGA, mengikuti tema terang/gelap perangkat. Logo ditanam langsung ke halaman sehingga tidak bergantung berkas luar. |
| `api/dashboard_auth.py` | 36–70 | Token sesi | Pembuatan dan verifikasi cookie sesi bertanda tangan HMAC-SHA256 — cookie tidak dapat dipalsukan pengunjung. |
| `api/dashboard_auth.py` | 72–77 | Pemeriksaan kredensial | Perbandingan waktu-tetap agar kata sandi tidak bocor melalui perbedaan waktu proses. |
| `api/dashboard_auth.py` | 79–106 | Pembatas percobaan login | Maksimum 8 kegagalan per alamat IP dalam 5 menit, menahan penebakan kata sandi otomatis. |
| `api/dashboard_auth.py` | 108–140 | Cakupan halaman terlindungi | Daftar jalur yang wajib login. Jalur perangkat keras sengaja dikecualikan karena firmware tidak dapat menyimpan cookie. |
| `api/main.py` | 68–90 | Penjaga sesi | Middleware yang menutup seluruh permukaan dashboard: navigasi peramban diarahkan ke halaman login, panggilan data dibalas kode 401. |
| `api/main.py` | 949–1022 | Alur masuk & keluar | Penyaring alamat tujuan agar halaman login tidak dapat disalahgunakan mengarahkan ke situs lain (952–967), penampilan formulir (970–976), pemrosesan masuk (979–1015), dan keluar (1018–1022). |
| `api/static/dashboard.html` | 876–892 | Penanganan sesi kedaluwarsa | Bila sesi habis saat tab dibiarkan terbuka, halaman otomatis kembali ke formulir login alih-alih membeku tanpa penjelasan. |

## B.2 Kerangka Dashboard

| Berkas | Baris | Bagian | Penjelasan |
|---|---|---|---|
| `api/static/dashboard.html` | 8–191 | Sistem gaya | Definisi warna, tipografi, kartu, tabel, dan lencana status untuk seluruh halaman. |
| `api/static/dashboard.html` | 196–219 | Kepala halaman | Judul, pemilih perangkat, tombol simulator, dan tombol keluar. |
| `api/static/dashboard.html` | 221–238 | Bilah status | Status koneksi, nomor urut paket, daya baterai, waktu pembaruan terakhir, dan jumlah cuplikan sinyal. |
| `api/static/dashboard.html` | 240–250 | Navigasi tab | Delapan tab: Data Asli, PWA, MLP, XGBoost, Firmware, PWA Settings, Kalibrasi, Log Akses. |
| `api/static/dashboard.html` | 252–287 | Panel statistik | Ringkasan mutu sinyal yang tetap tampil di seluruh tab. |
| `api/static/dashboard.html` | 898–1000 | Pabrik grafik | Konfigurasi dasar seluruh grafik sinyal: sumbu, warna, dan kinerja penggambaran. |
| `api/static/dashboard.html` | 1001–1090 | Manajemen perangkat | Pemilihan perangkat, penyambungan, dan kendali simulator perangkat keras. |
| `api/static/dashboard.html` | 1091–1109 | Pengambilan berkala | Penarikan data terbaru dari server secara periodik. |
| `api/static/dashboard.html` | 1964–1978 | Perpindahan tab | Penampilan panel sesuai tab yang dipilih. |
| `api/static/dashboard.html` | 2332–2348 | Inisialisasi | Penyiapan grafik dan pemuatan daftar perangkat saat halaman dibuka. |

## B.3 Halaman-Halaman Dashboard

### Tab 1 — Data Asli (Sinyal Mentah)

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 289–329 | Struktur halaman: tiga grafik sinyal mentah (hijau, merah, inframerah) beserta panel mutu sinyal. |
| `api/static/dashboard.html` | 1213–1286 | `renderRaw()` — penggambaran sinyal mentah apa adanya dari sensor, tanpa pengolahan. |
| `api/static/dashboard.html` | 1142–1212 | `renderStats()` dan `renderSqi()` — statistik kanal dan penerjemahan kode mutu sinyal menjadi keterangan yang dapat dibaca. |

### Tab 2 — Setelah PWA (Pulse Wave Analysis)

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 330–355 | Struktur halaman: sinyal setelah penapisan beserta fitur morfologi hasil ekstraksi. |
| `api/static/dashboard.html` | 1287–1386 | `renderPwa()` — penggambaran sinyal terfilter, penandaan puncak denyut, dan penampilan fitur gelombang. |

### Tab 3 — Setelah MLP (Estimasi Vital)

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 356–418 | Struktur halaman: kartu estimasi gula darah, kolesterol, asam urat, tekanan darah, beserta penanda risiko. |
| `api/static/dashboard.html` | 1859–1917 | `renderMlp()` dan `tile()` — penampilan hasil estimasi model kalibrasi beserta status warnanya. |

### Tab 4 — Setelah XGBoost (Prediksi Risiko Stroke)

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 419–426 | Struktur halaman prediksi risiko akhir. |
| `api/static/dashboard.html` | 1918–1963 | `renderXgb()` — penampilan tingkat risiko, probabilitas, dan daftar faktor risiko yang terdeteksi. |

### Tab 5 — Firmware Manager

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 427–544 | Struktur halaman: pustaka firmware, panel unggah, panel penyebaran, editor konfigurasi, dan terminal keluaran. |
| `api/static/dashboard.html` | 1988–2065 | Pemuatan dan penampilan pustaka firmware yang tersimpan di server. |
| `api/static/dashboard.html` | 2066–2115 | Unggah berkas firmware baru beserta indikator kemajuan. |
| `api/static/dashboard.html` | 2116–2191 | Penyebaran versi ke perangkat, penyuntingan keterangan, dan penghapusan versi. |
| `api/static/dashboard.html` | 2192–2245 | Penyuntingan `config.h` langsung dari peramban. |
| `api/static/dashboard.html` | 2246–2270 | Kompilasi dan flashing dengan keluaran langsung ke terminal di halaman. |

### Tab 6 — PWA Settings

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 545–560 | Struktur halaman penyetelan parameter analisis sinyal. |
| `api/static/dashboard.html` | 2271–2331 | Pemuatan, penyimpanan, dan pengembalian parameter ke nilai bawaan. |

### Tab 7 — Kalibrasi Sensor

Tab terpenting untuk validasi ilmiah: merekam sinyal sensor berdampingan dengan
nilai alat medis rujukan, lalu melatih model dari data tersebut.

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/static/dashboard.html` | 561–571 | Ringkasan dataset | Jumlah sesi, jumlah subjek, dan rentang tiap parameter. |
| `api/static/dashboard.html` | 573–637 | Formulir rekam sesi | Identitas subjek (ID, usia, jenis kelamin, kondisi pengambilan) dan nilai alat invasif: gula darah, kolesterol, asam urat, sistolik, diastolik. |
| `api/static/dashboard.html` | 639–666 | Tabel dataset | Daftar seluruh rekaman beserta tombol cetak laporan, sunting, dan hapus per baris. |
| `api/static/dashboard.html` | 668–683 | Pembangkit data demo | Pembuatan data sintetis berkorelasi fisiologis untuk menguji alur pelatihan tanpa data nyata. |
| `api/static/dashboard.html` | 685–706 | Panel pelatihan MLP | Pelatihan model dari data asli maupun data demo, beserta unduhan laporan hasil pelatihan. |
| `api/static/dashboard.html` | 708–743 | Uji prediksi acak | Pengambilan 20 sampel acak, inferensi model, dan perbandingan terhadap nilai rujukan. |
| `api/static/dashboard.html` | 744–813 | Jendela sunting rekaman | Perbaikan nilai yang salah masuk tanpa harus merekam ulang. |
| `api/static/dashboard.html` | 1390–1450 | Pemuatan & penampilan | `calibLoad()`, `renderCalibSummary()`, `renderCalibTable()`. |
| `api/static/dashboard.html` | 1451–1512 | Simpan, hapus, cetak, ekspor | `calibSave()`, `calibDelete()`, `calibPrint()`, `calibExport()`. |
| `api/static/dashboard.html` | 1513–1590 | Penyuntingan rekaman | `calibEdit()` dan `calibSaveEdit()`. |
| `api/static/dashboard.html` | 1591–1682 | Laporan & data demo | Pemuatan laporan pelatihan serta pembuatan dan penghapusan data demo. |
| `api/static/dashboard.html` | 1683–1751 | Pelatihan model | `calibRunTrain()` dan `_renderTrainingReport()` — menjalankan pelatihan dan menampilkan metrik akurasi tiap target. |
| `api/static/dashboard.html` | 1752–1858 | Pengujian model | `calibRunTest()`, `_renderTestResults()`, `calibExportTest()`. |

### Tab 8 — Log Akses

| Berkas | Baris | Penjelasan |
|---|---|---|
| `api/static/dashboard.html` | 814–874 | Struktur halaman: penyaring per perangkat, per kode status, dan kotak keluaran langsung. |
| `api/static/dashboard.html` | 2349–2500 | Aliran log langsung melalui Server-Sent Events, beserta penguraian, penyaringan, dan penggambaran ulang baris log. |
| `api/main.py` | 574–630 | `GET /v1/access-log` dan `/v1/access-log/stream` — sumber data log di sisi server. |
| `api/main.py` | 633–659 | `GET /logs` — pembacaan berkas log historis. |

## B.4 Laporan Hasil Pemeriksaan Siap Cetak (PDF)

Modul yang menghasilkan laporan medis A4 per subjek, dapat disimpan sebagai PDF
melalui dialog cetak peramban.

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/calib_report.py` | 36–52 | Logo laporan | Penanaman logo ANTARAGA ke dalam berkas laporan sebagai data mandiri. |
| `api/calib_report.py` | 54–81 | Pustaka ikon | Ikon garis-tunggal (jantung, manometer, tetesan, labu, molekul, gelombang) yang tetap tajam pada berbagai resolusi cetak. |
| `api/calib_report.py` | 86–110 | Klasifikasi tekanan darah | Penggolongan mengikuti pedoman hipertensi: optimal hingga derajat 3, memakai kategori tertinggi antara sistolik dan diastolik. |
| `api/calib_report.py` | 111–131 | Klasifikasi denyut jantung | Bradikardia, normal sinus, hingga takikardia. |
| `api/calib_report.py` | 133–163 | Klasifikasi gula darah | Ambang berbeda menurut kondisi pengambilan: puasa, dua jam setelah makan, atau sewaktu. |
| `api/calib_report.py` | 165–188 | Klasifikasi kolesterol & asam urat | Kolesterol mengikuti NCEP ATP III; asam urat dibedakan rentang pria dan wanita. |
| `api/calib_report.py` | 190–216 | Format lokal Indonesia | Koma desimal, titik pemisah ribuan, dan penulisan tanggal panjang berbahasa Indonesia. |
| `api/calib_report.py` | 220–279 | Strip gelombang denyut | Penggambaran sinyal PPG tersimpan di atas kertas berpetak, menyerupai strip rekaman pada laporan klinik. |
| `api/calib_report.py` | 283–311 | Komponen laporan | Lencana status, baris parameter, pasangan label-nilai, dan kartu ringkas. |
| `api/calib_report.py` | 313–484 | Tata letak cetak A4 | Gaya kop surat, tabel hasil, dan pengaturan pemenggalan halaman agar tidak ada elemen terpotong. |
| `api/calib_report.py` | 488–736 | Penyusun laporan | Perakitan laporan lengkap: kop surat berlogo, nomor laporan, kode verifikasi, data subjek, kartu tanda vital, tabel hasil beserta nilai rujukan, strip gelombang, parameter teknis sensor, interpretasi, faktor risiko stroke, dan blok tanda tangan. |
| `api/main.py` | 1508–1527 | Endpoint laporan | `GET /v1/calibrate/{id}/laporan.html` — penyajian laporan per rekaman. |

## B.5 Endpoint Pendukung Dashboard

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `api/main.py` | 1053–1138 | Analisis real-time | `GET /v1/ingest/latest` — pipeline empat tahap (mentah → PWA → MLP → prediksi risiko) yang mengisi seluruh grafik dashboard dalam satu panggilan. |
| `api/main.py` | 1379–1449 | Perekaman kalibrasi | `POST /v1/calibrate` — menyimpan sinyal PPG sepuluh detik terakhir bersama nilai alat invasif. |
| `api/main.py` | 1452–1505 | Pengelolaan dataset | Pembacaan, penyuntingan, dan penghapusan rekaman kalibrasi. |
| `api/main.py` | 1542–1608 | Ekspor dataset | `GET /v1/calibrate/export.csv` — pengunduhan dataset untuk analisis lanjutan. |
| `api/main.py` | 1611–1713 | Perhitungan ulang denyut | Pembaruan nilai denyut seluruh rekaman ketika algoritma diperbaiki. |
| `api/main.py` | 1716–1770 | Ringkasan statistik | Rerata, minimum, dan maksimum tiap parameter dalam dataset. |
| `api/main.py` | 1772–1892 | Data demo | Pembangkitan dan penghapusan data sintetis berkorelasi fisiologis. |
| `api/main.py` | 1894–2100 | Pelatihan model | `POST /v1/calibrate/train` — pelatihan MLP langsung dari server beserta validasi silang dan penilaian keandalan menurut jumlah subjek. |
| `api/main.py` | 2102–2387 | Laporan pelatihan | `GET /v1/calibrate/report.html` — laporan lengkap berisi diagram sebar prediksi terhadap rujukan, metrik akurasi, dan interpretasinya. |
| `api/main.py` | 2389–2482 | Uji prediksi | `POST /v1/calibrate/predict-test` — pengujian model atas sampel acak beserta persentase galat tiap target. |

## B.6 Halaman Publik (Landing Page)

| Berkas | Baris | Bagian | Penjelasan |
|---|---|---|---|
| `api/static/index.html` | 856–867 | Navigasi | Bilah navigasi menuju tiap bagian halaman. |
| `api/static/index.html` | 868–906 | Bagian utama | Judul, penjelasan singkat, dan ajakan bertindak. |
| `api/static/index.html` | 907–925 | Statistik | Angka-angka kunci mengenai stroke dan urgensi deteksi dini. |
| `api/static/index.html` | 926–970 | Cara kerja | Penjelasan alur sistem dari sensor hingga peringatan dini. |
| `api/static/index.html` | 971–1026 | Fitur | Daftar kemampuan utama ekosistem ANTARAGA. |
| `api/static/index.html` | 1027–1068 | Teknologi AI | Penjelasan model MLP dan Gradient Boosting yang digunakan. |
| `api/static/index.html` | 1069–1092 | Unduhan | Tautan memperoleh aplikasi. |
| `api/static/index.html` | 1093–1221 | Kaki halaman | Identitas tim, institusi, dan keterangan program. |

---

# BAGIAN C — MODEL AI

## C.1 Model Multi-Layer Perceptron (MLP) — Estimasi Tekanan Darah & Gula Darah

Mengolah fitur hasil Pulse Wave Analysis dari sinyal PPG untuk mengestimasi indikator
tekanan darah tanpa manset dan gula darah tidak puasa.

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `model/train_mlp_calibration.py` | 46–54 | Definisi fitur masukan | Tujuh fitur: DC dan AC kanal inframerah, DC dan AC kanal merah, denyut jantung, usia, dan jenis kelamin. |
| `model/train_mlp_calibration.py` | 56–90 | Pemuatan dari basis data | Pengambilan data kalibrasi hasil rekaman sensor nyata. |
| `model/train_mlp_calibration.py` | 91–104 | Pemuatan dari berkas | Alternatif membaca dataset dari berkas CSV. |
| `model/train_mlp_calibration.py` | 105–116 | Penyiapan data | Pembersihan baris tidak lengkap dan penyandian jenis kelamin. |
| `model/train_mlp_calibration.py` | 117–161 | **Pelatihan model** | `train_one()` — arsitektur MLP dua lapisan tersembunyi (64 → 32 neuron, aktivasi ReLU), normalisasi StandardScaler, regularisasi L2. Solver dipilih menurut ukuran data: L-BFGS untuk data kecil, Adam dengan early stopping untuk data besar. Satu model terpisah per parameter vital. |
| `model/train_mlp_calibration.py` | 162–194 | Diagram validasi | Pembuatan diagram sebar prediksi terhadap nilai rujukan beserta metrik akurasi. |
| `model/train_mlp_calibration.py` | 195–295 | Alur pelatihan | Validasi silang, perhitungan MAE, RMSE, R², dan penyimpanan model terlatih. |
| `model/train_ppg_vitals.py` | 41–142 | Pelatihan awal | Versi terdahulu yang melatih estimasi vital langsung dari sinyal mentah. |

## C.2 Model Gradient Boosting — Klasifikasi Risiko Stroke

Mengolah data profil pengguna dan hasil pemantauan untuk menghasilkan klasifikasi
tingkat risiko stroke.

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `model/train.py` | 56–70 | Definisi fitur | Fitur numerik (usia, kadar glukosa rerata, indeks massa tubuh) dan kategorikal (jenis kelamin, tipe tempat tinggal, status merokok). |
| `model/train.py` | 71–89 | Pemuatan dataset | Pembacaan dataset stroke beserta pembersihan nilai kosong. |
| `model/train.py` | 90–121 | **Penentuan ambang** | `best_f1_threshold()` dan `recall_target_threshold()` — pemilihan ambang klasifikasi yang mengutamakan sensitivitas, karena pada kasus stroke kegagalan mendeteksi jauh lebih berbahaya daripada peringatan berlebih. |
| `model/train.py` | 122–147 | Penyetelan HistGradientBoosting | Pencarian hiperparameter dengan validasi silang. |
| `model/train.py` | 148–191 | Penyetelan XGBoost | Penyandian ordinal fitur kategorikal dan pencarian hiperparameter. |
| `model/train.py` | 192–286 | Alur pelatihan | Pembandingan kedua algoritma, pemilihan model terbaik, dan penyimpanan artefak beserta ambangnya. |
| `model/xgboost_stroke_training.ipynb` | — | Buku kerja analisis | Eksplorasi data dan pembandingan model dalam bentuk notebook. |

## C.3 Skoring ABCD2

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `model/abcd2.py` | 23–28 | Tingkat urgensi | Kategori rendah, sedang, dan tinggi. |
| `model/abcd2.py` | 29–61 | Struktur hasil | Skor total, tingkat urgensi, perkiraan risiko, dan rekomendasi tindakan. |
| `model/abcd2.py` | 62–98 | **Perhitungan skor** | `calculate_abcd2()` — penjumlahan lima komponen: **A**ge (usia ≥60), **B**lood pressure (≥140/90), **C**linical features (kelemahan satu sisi atau gangguan bicara), **D**uration (durasi gejala), dan **D**iabetes. Skor 0–7 diterjemahkan menjadi perkiraan risiko stroke dalam 2–90 hari setelah gejala TIA. |

## C.4 Ekstraksi Fitur Pulse Wave Analysis

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `model/ppg_features.py` | 40–47 | Struktur denyut | `PulseEvent` — representasi satu siklus denyut beserta titik-titik pentingnya. |
| `model/ppg_features.py` | 48–56 | Penapis pita | Butterworth 0,5–12 Hz untuk mengisolasi komponen denyut. |
| `model/ppg_features.py` | 57–104 | Denyut via spektrum | Perhitungan denyut jantung melalui analisis spektral. |
| `model/ppg_features.py` | 105–162 | **Deteksi denyut** | `detect_pulses()` — penentuan titik awal, puncak sistolik, dan notch dikrotik tiap siklus. |
| `model/ppg_features.py` | 163–195 | Fitur per kanal | Amplitudo, lebar setengah amplitudo, waktu naik, dan luas area gelombang. |
| `model/ppg_features.py` | 196–230 | **Penyusunan fitur** | `extract_pwa_features()` — menghasilkan 23+ fitur morfologi gelombang yang menjadi masukan model MLP. |

---

# BAGIAN D — FIRMWARE SMARTBAND

Perangkat: Seeed Studio XIAO ESP32-S3. Sensor: MAX30102 (merah + inframerah) dan
SON1303 (hijau).

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `Firmware/include/antaraga.h` | 26–35 | Pemetaan pin | Penetapan pin sensor, I²C, LED indikator, dan pembagi tegangan baterai. |
| `Firmware/include/antaraga.h` | 36–58 | Parameter pencuplikan | Laju cuplik dan panjang batch, dilengkapi pemeriksaan saat kompilasi agar keduanya selalu konsisten. |
| `Firmware/include/antaraga.h` | 59–120 | Struktur data | Definisi `Batch` dan `Sqi` — format data yang dikirim ke server. |
| `Firmware/include/config.h` | 12–45 | Konfigurasi jaringan | Kredensial Wi-Fi, alamat server, kunci perangkat, dan sinkronisasi waktu. |
| `Firmware/include/config.h` | 47–120 | Konfigurasi sensor | Laju cuplik PPG, oversampling ADC, dan arus LED merah serta inframerah. |
| `Firmware/src/main.cpp` | 56–74 | Mesin status | Pengelolaan status perangkat: menyalakan, menyambung, merekam, mengirim. |
| `Firmware/src/main.cpp` | 106–158 | Indikator LED | Pola nyala LED yang menandakan status perangkat kepada pengguna. |
| `Firmware/src/main.cpp` | 202–270 | Alur utama | `setup()` dan `loop()` — inisialisasi sensor dan siklus rekam-kirim berkelanjutan. |
| `Firmware/src/sensors.cpp` | 94–106 | Pembacaan ADC | Oversampling untuk menekan derau pembacaan sensor analog. |
| `Firmware/src/sensors.cpp` | 107–185 | Register MAX30102 | Definisi register dan fungsi baca-tulis I²C. |
| `Firmware/src/sensors.cpp` | 186–464 | Driver sensor | Inisialisasi, konfigurasi arus LED, pembacaan FIFO, dan pencuplikan berkala tiga kanal warna. |
| `Firmware/src/sqi.cpp` | 64–123 | Statistik kanal | Perhitungan rerata, simpangan, dan pendeteksian pencuplikan yang jenuh. |
| `Firmware/src/sqi.cpp` | 124–161 | Ukuran mutu | Tortuositas sinyal dan penilaian berbasis rentang. |
| `Firmware/src/sqi.cpp` | 162–267 | **Penilaian mutu sinyal** | `sqiEvaluate()` — penilaian mutu tiap batch sebelum dikirim, menandai jari bergerak, perfusi lemah, atau sensor lepas. Server memakai penanda ini untuk membuang data sampah. |
| `Firmware/src/cloud.cpp` | 61–114 | Penyusunan JSON | Perakitan payload sinyal beserta metadata mutu. |
| `Firmware/src/cloud.cpp` | 115–196 | Wi-Fi, waktu, & TLS | Penyambungan jaringan, sinkronisasi waktu NTP, dan penyiapan koneksi terenkripsi. |
| `Firmware/src/cloud.cpp` | 197–231 | Pembacaan tanggapan | Penguraian tanggapan server tanpa pustaka JSON, menghemat memori perangkat. |
| `Firmware/src/cloud.cpp` | 232–433 | **Pembaruan jarak jauh** | Pemeriksaan versi baru, pengunduhan, pemasangan, serta mekanisme pengembalian otomatis bila firmware baru gagal berjalan. |
| `Firmware/src/cloud.cpp` | 434–594 | Pengiriman data | `cloudPost()` — pengiriman batch ke server beserta penanganan kegagalan jaringan. |

---

# BAGIAN E — APLIKASI MOBILE (FLUTTER)

> **Catatan penting:** source code aplikasi mobile **tidak berada di repositori ini**.
> Repositori ini memuat backend, web dashboard, model AI, dan firmware. Aplikasi mobile
> dibangun dengan Flutter (Dart) dan disimpan pada repositori terpisah.

Kerangka kerja: Flutter (Dart). Total 4.785 baris kode pada 23 berkas di dalam `lib/`.
Seluruh rentang baris di bawah mengacu pada repositori aplikasi mobile.

## E.1 Halaman Aplikasi

| Halaman Aplikasi | Berkas Flutter | Baris | Penjelasan | Endpoint Backend Terkait |
|---|---|---|---|---|
| Halaman Pembuka | `lib/screens/splash_screen.dart` | 1–107 | Layar pembuka beranimasi sekaligus jeda pemeriksaan sesi masuk. | — |
| Halaman Daftar Akun Keluarga | `lib/screens/login_screen.dart` | 24, 47–68, 144–187 | Formulir email/No. HP, kata sandi, dan konfirmasi kata sandi. Satu layar melayani dua moda lewat penanda `_isRegisterMode`. | `POST /auth/register` — `api/main.py` 173–195 |
| Halaman Masuk (Login) | `lib/screens/login_screen.dart` | 36–68, 69–223 | Formulir masuk bagi akun terdaftar, dengan tombol alih ke moda pendaftaran. | `POST /auth/login` — `api/main.py` 198–212 |
| Halaman Profil Orang Tua/Lansia | `lib/screens/profile_form_screen.dart` | 115–343 | Pengisian data demografis dan riwayat kesehatan lansia. | `POST /profiles` — `api/main.py` 238–271 |
| — pilihan berbentuk kancing | `lib/screens/profile_form_screen.dart` | 344–455 | Kancing pilihan untuk jenis kelamin, penyakit jantung, diabetes, riwayat keluarga, status bekerja, tempat tinggal, dan kebiasaan merokok. | — |
| Halaman Hubungkan Perangkat | `lib/screens/dashboard_screen.dart` | 176–254 | Pemasangan Device ID smartband ke akun, didahului pemeriksaan keberadaan perangkat. | `POST /device/pair` — `api/main.py` 661–688 |
| Halaman Dashboard Utama | `lib/screens/dashboard_screen.dart` | 268–475 | Kerangka utama: sapaan, kartu vital, kartu risiko, dan ringkasan asesmen. | `GET /vitals/latest` — `api/main.py` 382–427 |
| — kartu vital | `lib/screens/dashboard_screen.dart` | 596–621, 966–1158 | Kartu tiga parameter vital dengan denyut animasi saat data baru masuk. | — |
| — keterangan nilai rujukan | `lib/screens/dashboard_screen.dart` | 622–756 | Jendela penjelasan rentang normal tiap parameter bagi keluarga yang awam. | — |
| — kartu prediksi risiko | `lib/screens/dashboard_screen.dart` | 757–899 | Penampilan hasil prediksi risiko beserta warna tingkat dan faktor penyumbangnya. | `POST /predict/stroke-risk` — `api/main.py` 330–379 |
| Halaman Detak Jantung (BPM) | `lib/screens/vital_detail_screen.dart` | 10, 73–314 | Grafik denyut harian beserta nilai rerata, minimum, dan maksimum. Satu layar melayani tiga parameter lewat `enum VitalType`. | `GET /vitals/history` — `api/main.py` 430–463 |
| — ringkasan statistik | `lib/screens/vital_detail_screen.dart` | 315–338 | Baris ringkasan nilai terendah, tertinggi, dan rerata. | — |
| Halaman Statistik Harian | `lib/screens/daily_stats_screen.dart` | 233–507 | Tren tiga parameter vital dan linimasa 24 jam. | `GET /vitals/history` — `api/main.py` 430–463 |
| — grafik ringkas | `lib/screens/daily_stats_screen.dart` | 508–636 | Grafik mini per parameter dan kancing linimasa per jam. | — |
| — rincian per jam | `lib/screens/daily_stats_screen.dart` | 86–232, 637–642 | Pengelompokan pembacaan ke dalam ember per jam beserta rinciannya. | — |
| Halaman Assessment ABCD2 | `lib/screens/assessment_form_screen.dart` | 46–113 | Pengisian lima kategori asesmen dan penampilan hasil stratifikasi. | `POST /assessment/abcd2` — `api/main.py` 466–497 |
| — pilihan gejala klinis | `lib/screens/assessment_form_screen.dart` | 141–229 | Pilihan gejala klinis dan lama gejala sesuai komponen baku ABCD². | — |
| — ringkasan hasil | `lib/screens/dashboard_screen.dart` | 900–965 | Ringkasan skor dan kategori kegawatan pada dashboard setelah asesmen diisi. | — |
| Penerimaan Peringatan Dini | `lib/services/fcm_service.dart` | 39–84 | Perizinan notifikasi, saluran notifikasi Android, dan pendaftaran token perangkat. | `POST /device/register-token` — `api/main.py` 160–170 |
| — notifikasi saat aplikasi tertutup | `lib/services/fcm_service.dart` | 9–24 | Penangan pesan latar belakang, berjalan di isolate terpisah. | — |
| — notifikasi saat aplikasi terbuka | `lib/services/fcm_service.dart` | 91–125 | Penampilan notifikasi lokal dan pengarahan ke halaman asesmen saat diketuk. | — |

## E.2 Lapisan Layanan dan Data

| Berkas | Baris | Fitur | Penjelasan |
|---|---|---|---|
| `lib/main.dart` | 22–38 | Titik masuk aplikasi | Penyiapan Firebase, layanan notifikasi, penyimpanan lokal, dan pelokalan bahasa Indonesia. |
| `lib/main.dart` | 61–161 | **Pengarah alur** | Penentuan halaman tujuan berdasarkan status masuk dan kelengkapan profil: pembuka → masuk → profil → dashboard. |
| `lib/services/api_service.dart` | 26–44 | Klien HTTP | Penyusun alamat dan penyisip token wewenang pada setiap permintaan. |
| `lib/services/api_service.dart` | 45–103 | Pengelolaan profil | Pengambilan, pembuatan, penyuntingan, dan pemilihan profil lansia aktif. |
| `lib/services/api_service.dart` | 104–152 | Vital dan risiko | Permintaan prediksi risiko, pengambilan vital terbaru, dan riwayat harian. |
| `lib/services/api_service.dart` | 169–226 | Perangkat dan asesmen | Pemeriksaan keberadaan perangkat, pemasangan, dan pengiriman asesmen ABCD². |
| `lib/services/auth_service.dart` | 39–77 | Penyimpanan sesi | Penyimpanan token dan identitas pengguna secara lokal serta pemulihannya saat aplikasi dibuka kembali. |
| `lib/services/auth_service.dart` | 78–109 | Pendaftaran dan masuk | Pendaftaran akun keluarga, masuk, dan keluar. |
| `lib/services/risk_service.dart` | 21–79 | **Penilaian risiko sisi aplikasi** | Penilaian cadangan berbasis aturan dari vital, profil, dan skor ABCD² — dipakai saat sambungan ke server terputus. |
| `lib/services/profile_service.dart` | 12–44 | Simpanan profil lokal | Penyimpanan profil dan penanda selesai pengenalan awal. |
| `lib/services/demo_service.dart` | 12–183 | Moda peragaan | Pembangkitan data vital tiruan untuk peragaan tanpa perangkat keras maupun sambungan server. |
| `lib/models/user_profile.dart` | 2–137 | Model profil | Struktur data lansia beserta penyandian ke dan dari JSON. |
| `lib/models/vital_data.dart` | 2–50 | Model vital | Struktur satu pembacaan tekanan darah, detak jantung, dan gula darah. |
| `lib/models/assessment.dart` | 3–64 | Model asesmen | Struktur jawaban ABCD² beserta perhitungan skornya. |
| `lib/models/api_results.dart` | 4–78 | Model tanggapan | Struktur hasil prediksi risiko, hasil ABCD², dan cuplikan vital terbaru. |
| `lib/core/constants/vital_ranges.dart` | 6–76 | **Nilai rujukan klinis** | Ambang normal, penamaan status, dan pewarnaan untuk tekanan darah, detak jantung, dan gula darah. |
| `lib/core/constants/app_constants.dart` | 3–21 | Konfigurasi lingkungan | Alamat server, saklar moda pengembangan, dan saklar moda peragaan. |
| `lib/core/theme/app_colors.dart` | 4–44 | Palet warna | Warna tingkat risiko dan warna tiap parameter vital. |
| `lib/core/theme/app_theme.dart` | 7–113 | Tema tampilan | Tema menyeluruh: huruf, kartu, kancing, dan medan isian. |

Kontrak data lengkap tiap endpoint beserta contoh permintaan dan tanggapannya
terdokumentasi di `README.md` bagian **"Untuk Mobile App (Flutter)"** (mulai baris 92).

> **Perhatian saat menyiapkan lampiran:** berkas `serviceAccountKey.json` pada akar
> proyek Flutter memuat kunci layanan Firebase, dan `lib/firebase_options.dart` memuat
> kunci API tiap peron. Keduanya **jangan dilampirkan apa adanya** — samarkan nilainya
> atau kecualikan dari berkas lampiran.

---

# LAMPIRAN A — RINGKASAN FITUR UNGGULAN

Delapan bagian kode yang paling layak ditonjolkan sebagai inti kebaruan ciptaan:

| # | Fitur | Lokasi | Alasan |
|---|---|---|---|
| 1 | **Alur peringatan dini otomatis** | `api/main.py` 703–869 | Rantai lengkap dalam satu permintaan: sinyal mentah → estimasi vital → prediksi risiko → penyimpanan → push notification ke keluarga. |
| 2 | **Estimasi vital tanpa manset & tanpa tusuk jarum** | `model/train_mlp_calibration.py` 117–161 | Model MLP per parameter yang mengubah fitur optik PPG menjadi estimasi tekanan darah dan gula darah. |
| 3 | **Ekstraksi fitur Pulse Wave Analysis** | `model/ppg_features.py` 105–230 | Deteksi titik penting gelombang denyut dan penyusunan 23+ fitur morfologi sebagai masukan model. |
| 4 | **Klasifikasi risiko berorientasi sensitivitas** | `model/train.py` 90–121 | Ambang klasifikasi dipilih mengutamakan sensitivitas — pada stroke, luput mendeteksi jauh lebih berbahaya daripada peringatan berlebih. |
| 5 | **Stratifikasi ABCD2 terintegrasi** | `model/abcd2.py` 62–98 | Asesmen klinis baku yang dijalankan otomatis ketika sistem mendeteksi kondisi menyimpang. |
| 6 | **Penilaian mutu sinyal berlapis** | `Firmware/src/sqi.cpp` 162–267 + `api/main.py` 872–932 | Penyaringan dua tingkat di perangkat dan di server, mencegah data bermutu buruk mencemari estimasi. |
| 7 | **Alur kalibrasi sensor terhadap alat medis** | `api/static/dashboard.html` 561–743 + `api/main.py` 1379–2100 | Perekaman, pengelolaan, pelatihan, dan pengujian model dalam satu antarmuka — dasar validasi ilmiah alat. |
| 8 | **Laporan hasil pemeriksaan siap cetak** | `api/calib_report.py` 1–736 | Laporan medis A4 berlogo lengkap dengan nilai rujukan klinis, strip gelombang denyut, dan kode verifikasi dokumen. |

---

# LAMPIRAN B — MEMPERBARUI NOMOR BARIS

Nomor baris bergeser setiap kali kode disunting. Untuk memverifikasi atau memperbarui
rentang pada dokumen ini:

**Melihat isi rentang tertentu:**
```bash
sed -n '703,869p' api/main.py
```

**Mencari ulang posisi seluruh endpoint backend:**
```bash
grep -n "^@app\." api/main.py
```

**Mencari ulang posisi seluruh halaman dashboard:**
```bash
grep -n '<div id="p-' api/static/dashboard.html
```

**Mencari ulang posisi seluruh fungsi dashboard:**
```bash
grep -n "^function \|^async function " api/static/dashboard.html
```

**Menyalin satu rentang ke berkas terpisah untuk dilampirkan:**
```bash
sed -n '703,869p' api/main.py > lampiran_alur_peringatan_dini.txt
```

---

# LAMPIRAN C — CATATAN PENYUSUNAN LAMPIRAN HKI

Beberapa hal yang perlu diperhatikan saat menyiapkan berkas lampiran:

1. **Kredensial harus disamarkan.** Berkas `Firmware/include/config.h` baris 12–13 memuat
   nama dan kata sandi Wi-Fi asli, dan baris 27 memuat kunci perangkat. Berkas `.env`
   memuat kunci penanda tangan token serta kata sandi dashboard. Ganti nilainya dengan
   `***` pada salinan yang dilampirkan.

2. **Berkas `.env` tidak perlu dilampirkan** — isinya konfigurasi lingkungan, bukan ciptaan.
   Cukup lampirkan `.env.example` yang sudah tidak memuat nilai asli.

3. **Dataset pihak ketiga sebaiknya tidak dilampirkan.** Berkas
   `healthcare-dataset-stroke-data.csv` adalah dataset publik untuk pelatihan model,
   bukan bagian dari ciptaan.

4. **Artefak model** (`model/artifacts/`) berupa berkas biner hasil pelatihan. Yang
   dilampirkan cukup kode pelatihannya, bukan berkas modelnya.

5. **Urutan lampiran yang disarankan** mengikuti urutan dokumen ini: backend, web app,
   model AI, firmware, lalu aplikasi mobile — sesuai alur data dari sensor hingga
   sampai ke tangan keluarga.
