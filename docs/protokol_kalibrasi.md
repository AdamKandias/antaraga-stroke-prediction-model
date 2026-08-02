# Protokol Pengambilan Data Kalibrasi ANTARAGA

> Dokumen ini menjelaskan prosedur teknis pengumpulan data kalibrasi untuk melatih model MLP
> prediksi vital sign non-invasif pada sistem ANTARAGA.

---

## Daftar Isi

1. [Tujuan dan Prinsip Dasar](#1-tujuan-dan-prinsip-dasar)
2. [Peralatan yang Dibutuhkan](#2-peralatan-yang-dibutuhkan)
3. [Persiapan Sebelum Sesi](#3-persiapan-sebelum-sesi)
4. [Prosedur Langkah demi Langkah](#4-prosedur-langkah-demi-langkah)
5. [Teknis Pengambilan Setiap Parameter](#5-teknis-pengambilan-setiap-parameter)
6. [Kondisi Pengukuran (Kondisi)](#6-kondisi-pengukuran-kondisi)
7. [Jadwal dan Ukuran Sampel](#7-jadwal-dan-ukuran-sampel)
8. [Manajemen Data](#8-manajemen-data)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Tujuan dan Prinsip Dasar

Kalibrasi dilakukan untuk membuat pasangan data:

```
Sinyal PPG sensor ANTARAGA  ←→  Nilai referensi alat invasif/medis standar
```

Model MLP belajar dari pasangan ini agar dapat **memprediksi nilai vital sign
tanpa alat invasif** setelah model dilatih.

**Prinsip utama:**  
Pengukuran PPG sensor dan pengukuran alat referensi **harus dilakukan bersamaan**
atau dalam selisih waktu ≤ 2 menit (kondisi fisiologis subjek belum berubah signifikan).

---

## 2. Peralatan yang Dibutuhkan

| Peralatan | Fungsi | Akurasi minimum |
|---|---|---|
| Jam ANTARAGA (dipakai di pergelangan tangan) | Sensor PPG 3 kanal | — |
| Glucometer + strip uji | Gula darah kapiler | ±15 mg/dL atau ±15% |
| Tensimeter digital (sfigmomanometer) | Sistolik + Diastolik | ±3 mmHg |
| Lancet + kapas alkohol | Tusukan jari untuk glukosa | steril, sekali pakai |
| Laptop/HP dengan dashboard ANTARAGA | Rekam + simpan data | — |
| Formulir atau buku catatan | Backup pencatatan | — |

Opsional (untuk proposal PKM):
- Alat kolesterol (Cholesterol Analyzer, mis. Accutrend Plus)
- Alat asam urat (mis. Nesco MultiCheck)

---

## 3. Persiapan Sebelum Sesi

### 3.1 Kondisi Subjek

- Subjek **duduk tenang selama 5–10 menit** sebelum pengukuran dimulai.
- Tidak merokok 30 menit sebelum pengukuran.
- Tidak berolahraga 1 jam sebelum pengukuran.
- Buang air kecil sebelum sesi jika diperlukan (tekanan darah dapat berubah).
- Jika pengukuran kondisi **puasa**: subjek tidak makan/minum selain air putih selama minimal **8 jam**.
- Jika pengukuran kondisi **2 jam setelah makan**: catat makanan yang dikonsumsi.

### 3.2 Kondisi Sensor

- Bersihkan sensor ANTARAGA dengan tisu alkohol, biarkan kering.
- Pastikan firmware terbaru ter-upload dan perangkat terhubung ke server (LED hijau stabil / device terdeteksi di dashboard).
- Pastikan baterai penuh atau disambungkan ke charger.

### 3.3 Posisi Pemasangan

- Pasang ANTARAGA di **pergelangan tangan** seperti jam tangan, sensor menghadap ke bawah (sisi kulit).
- Posisi terbaik: sisi bagian dalam pergelangan (sisi arteri radial / nadi) — sinyal PPG lebih kuat di sini.
- **Kencangkan tali** hingga pas: sensor harus menempel rapat tanpa menekan pembuluh darah.
  - Terlalu longgar → sinyal noise karena sensor bergerak.
  - Terlalu ketat → aliran darah terhambat, sinyal melemah.
- Pastikan **tidak ada celah** antara sensor dan kulit; rambut di bawah sensor dapat menurunkan kualitas sinyal — bersihkan area jika perlu.
- Minta subjek agar **lengan diletakkan di atas meja, posisi rileks**, tidak bergerak selama akuisisi.

---

## 4. Prosedur Langkah demi Langkah

```
LANGKAH 1  Pasang ANTARAGA di pergelangan tangan seperti jam tangan (sensor ke dalam, sisi kulit)
LANGKAH 2  Buka dashboard → pilih device dari dropdown → pastikan sinyal real-time terlihat
LANGKAH 3  Tunggu sinyal stabil (biasanya 15–30 detik); minta subjek diam, lengan di atas meja
LANGKAH 4  Ukur tekanan darah di lengan BERLAWANAN dari yang memakai ANTARAGA
LANGKAH 5  Ukur gula darah (dan kolesterol / asam urat jika tersedia) — jari tangan mana saja
LANGKAH 6  Di dashboard → tab "Kalibrasi" → isi form identitas + nilai alat
LANGKAH 7  Klik "Simpan Sesi Kalibrasi" → server otomatis ambil buffer PPG 10 detik terakhir
LANGKAH 8  Verifikasi baris baru muncul di tabel dataset
LANGKAH 9  Bersihkan area tusukan, istirahatkan subjek, lanjut ke subjek berikutnya
```

---

## 5. Teknis Pengambilan Setiap Parameter

### 5.1 Gula Darah (Glucometer)

1. Gunakan jari tangan mana saja — ANTARAGA ada di pergelangan tangan, tidak ada konflik dengan tusukan jari.
2. Bersihkan ujung jari dengan kapas alkohol, biarkan **benar-benar kering** (alkohol basah mengencerkan darah → hasil melenceng).
3. Tusuk sisi ujung jari (bukan tepat di tengah — lebih sedikit saraf).
4. Usap tetes pertama (darah pertama mengandung cairan jaringan → buang).
5. Tempelkan strip pada tetes darah kedua.
6. Baca hasil setelah ±5 detik.
7. **Catat nilai (mg/dL)** dan masukkan ke field "Gula Darah" di dashboard.

> Waktu ideal: dalam ±60 detik dari saat sensor ANTARAGA sedang merekam stabil.

### 5.2 Tekanan Darah Sistolik / Diastolik (Tensimeter Digital)

1. Pasang manset di lengan yang **tidak memakai ANTARAGA** (lengan berlawanan), setinggi jantung.
   - Alasan: manset tensimeter menghentikan aliran darah sementara — jika dipasang di lengan yang sama dengan ANTARAGA, sinyal PPG akan hilang selama pengukuran.
2. Subjek rileks, tidak bicara, tidak menggerakkan kedua lengan.
3. Tekan start — tunggu otomatis mengembang dan membaca.
4. Catat **sistolik (angka atas)** dan **diastolik (angka bawah)** dalam mmHg.
5. Jika pembacaan pertama terasa tidak wajar, tunggu 2 menit dan ulang sekali.
6. Masukkan kedua nilai ke field "Sistolik" dan "Diastolik" di dashboard.

> Pengukuran tekanan darah sebaiknya dilakukan **sebelum** tusukan jari (rasa sakit
> dari tusukan dapat menaikkan tekanan darah sementara).

**Urutan ideal:**
```
Pasang ANTARAGA (pergelangan kiri) → Tensimeter (lengan kanan) → Glucometer → Klik Simpan
```

### 5.3 Kolesterol dan Asam Urat (Opsional)

- Gunakan Accutrend Plus atau Nesco MultiCheck sesuai protokol alat.
- Dapat menggunakan tetes darah yang sama dari tusukan glucometer (konsultasi panduan alat).
- Masukkan nilai ke field "Kolesterol" dan "Asam Urat" di dashboard.
- Jika tidak tersedia alat, biarkan field kosong — sistem akan melatih model hanya untuk target yang memiliki data.

---

## 6. Kondisi Pengukuran (Kondisi)

Pilih kondisi yang sesuai di dropdown "Kondisi pengukuran":

| Kode | Kondisi | Kapan Mengukur | Rentang Gula Darah Normal |
|---|---|---|---|
| `puasa` | Puasa | Pagi, min. 8 jam tidak makan | 70–100 mg/dL |
| `2j_setelah_makan` | 2 jam setelah makan | 2 jam setelah selesai makan | < 140 mg/dL |
| `sewaktu` | Sewaktu / acak | Kapan saja | < 200 mg/dL |

**Rekomendasi untuk PKM:** Kumpulkan data dengan kondisi **bervariasi** dari tiap subjek untuk
mendapatkan cakupan rentang gula darah yang lebih luas. Minimal: 1 sesi puasa + 1 sesi sewaktu per subjek.

---

## 7. Jadwal dan Ukuran Sampel

### Ukuran Sampel Minimum

| Target | N minimum (rekomendasi) | Catatan |
|---|---|---|
| Proof-of-concept | 20 subjek | Model bisa dilatih, LOO CV |
| Laporan PKM | 30–50 subjek | Beralih ke 5-fold CV |
| Publikasi ilmiah | ≥ 50 subjek | |

Setiap subjek dapat diukur beberapa kali (kondisi berbeda), sehingga jumlah **baris** lebih banyak
dari jumlah **subjek unik**.

### Satu Sesi per Subjek ≈ 10 Menit

```
5  menit  — persiapan & istirahat
2  menit  — akuisisi PPG + pengukuran alat
3  menit  — pencatatan + pembersihan
```

### ID Subjek

Gunakan format **anonim**: `S001`, `S002`, dst. Jangan gunakan nama atau NIK.  
Simpan pemetaan identitas nyata ↔ kode subjek di dokumen terpisah yang dikunci.

---

## 8. Manajemen Data

### 8.1 Melihat Dataset

Dashboard → tab **Kalibrasi** → tabel "Dataset Kalibrasi"

- Tombol **✎** (edit): koreksi nilai yang salah diinput
- Tombol **✕** (hapus): hapus baris jika pengambilan data gagal/tidak valid
- Tombol **↺ Refresh**: muat ulang dari server
- Tombol **⬇ Export CSV**: unduh dataset sebagai file CSV untuk analisis eksternal

### 8.2 Backup

Setelah setiap sesi pengumpulan, ekspor CSV dan simpan ke:
- Google Drive / OneDrive (backup cloud)
- Folder `data/calibration/` di repositori

### 8.3 Melatih Model

Setelah terkumpul ≥ 20 baris data:

```bash
python model/train_mlp_calibration.py
```

Output tersimpan di:
- `model/artifacts/mlp_calibration.joblib` — model terlatih
- `model/artifacts/mlp_calibration_metrics.json` — metrik (R², MAE, Akurasi)
- `reports/kalibrasi/scatter_*.png` — scatter plot prediksi vs referensi

Muat hasil pelatihan di dashboard: tab **Kalibrasi** → card "Hasil Pelatihan MLP Terakhir" → klik **↺ Muat Laporan**.

---

## 9. Troubleshooting

| Masalah | Kemungkinan Penyebab | Solusi |
|---|---|---|
| Sinyal PPG tidak muncul di dashboard | Sensor tidak terhubung / device salah | Periksa dropdown device, restart firmware |
| "Hubungkan perangkat dulu" saat klik Simpan | Device ID belum dipilih | Pilih device di dropdown bagian atas |
| Sinyal terlalu noise, tidak stabil | Jam terlalu longgar / subjek bergerak | Kencangkan tali ANTARAGA, minta subjek diam, lengan di atas meja |
| Nilai gula darah jauh dari normal | Tusukan gagal / strip kotor / alkohol belum kering | Ulangi dengan strip baru setelah alkohol kering |
| `sesi_ts` (waktu sesi) di tabel berbeda jauh | Server dan perangkat timezone berbeda | Server menggunakan UTC — tampilan dikonversi otomatis |

---

*Dokumen ini adalah bagian dari proposal PKM-KC ANTARAGA — Non-Invasive Early Stroke Detection Smartband.*
