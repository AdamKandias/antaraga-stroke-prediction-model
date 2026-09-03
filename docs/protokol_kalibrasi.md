# Protokol Pengambilan Data Kalibrasi ANTARAGA

> Dokumen ini menjelaskan prosedur teknis pengumpulan data kalibrasi untuk melatih model MLP
> prediksi vital sign non-invasif pada sistem ANTARAGA.

---

## Daftar Isi

1. [Tujuan dan Prinsip Dasar](#1-tujuan-dan-prinsip-dasar)
2. [Peralatan yang Dibutuhkan](#2-peralatan-yang-dibutuhkan)
3. [Persiapan Sebelum Sesi](#3-persiapan-sebelum-sesi)
4. [Prosedur Langkah demi Langkah](#4-prosedur-langkah-demi-langkah)
   - [4.1 ATURAN SELAMA AKUISISI - bacakan ke subjek](#41-aturan-selama-akuisisi--bacakan-ke-subjek)
   - [4.2 Verifikasi Sebelum Menekan Simpan](#42-verifikasi-sebelum-menekan-simpan)
5. [Teknis Pengambilan Setiap Parameter](#5-teknis-pengambilan-setiap-parameter)
6. [Kondisi Pengukuran (Kondisi)](#6-kondisi-pengukuran-kondisi)
7. [Jadwal dan Ukuran Sampel](#7-jadwal-dan-ukuran-sampel)
8. [Manajemen Data](#8-manajemen-data)
9. [Troubleshooting](#9-troubleshooting)
10. [Kartu Pengingat Ringkas](#10-kartu-pengingat-ringkas)

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
| Jam ANTARAGA (dipakai di pergelangan tangan) | Sensor PPG 3 kanal | - |
| Glucometer + strip uji | Gula darah kapiler | ±15 mg/dL atau ±15% |
| Tensimeter digital (sfigmomanometer) | Sistolik + Diastolik | ±3 mmHg |
| Lancet + kapas alkohol | Tusukan jari untuk glukosa | steril, sekali pakai |
| Laptop/HP dengan dashboard ANTARAGA | Rekam + simpan data | - |
| Formulir atau buku catatan | Backup pencatatan | - |

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
- Posisi terbaik: sisi bagian dalam pergelangan (sisi arteri radial / nadi) - sinyal PPG lebih kuat di sini.
- **Kencangkan tali** hingga pas: sensor harus menempel rapat tanpa menekan pembuluh darah.
  - Terlalu longgar → sinyal noise karena sensor bergerak.
  - Terlalu ketat → aliran darah terhambat, sinyal melemah.
- Pastikan **tidak ada celah** antara sensor dan kulit; rambut di bawah sensor dapat menurunkan kualitas sinyal - bersihkan area jika perlu.
- Minta subjek agar **lengan diletakkan di atas meja, posisi rileks**, tidak bergerak selama akuisisi.

### 3.4 Ketinggian Tangan - Jangan Diabaikan

Ini sumber kesalahan yang paling sering terlewat dan paling merusak data.

**Untuk lengan yang dipasangi tensimeter: WAJIB setinggi jantung.**

Darah punya berat. Kalau manset berada di bawah level jantung, tekanan kolom darah
ikut terbaca dan hasilnya **lebih tinggi dari yang sebenarnya**:

```
Setiap 1 cm di bawah jantung  →  +0,77 mmHg
        10 cm di bawah        →  +7,7 mmHg
        20 cm di bawah        →  +15,4 mmHg   ← cukup untuk mengubah
                                                "normal" menjadi "hipertensi"
```

Kalau lengan menggantung di sisi badan saat pengukuran, nilai sistolik yang Anda
catat sebagai *ground truth* bisa meleset belasan mmHg. Model akan belajar dari
angka yang salah, dan kesalahan itu tidak bisa diperbaiki belakangan.

**Cara memastikan:** titik tengah manset sejajar dengan puting/ujung tulang dada.
Sangga lengan dengan bantal atau tumpukan buku bila meja terlalu rendah - jangan
biarkan subjek menahan sendiri lengannya (otot menegang → tekanan darah naik).

**Untuk pergelangan yang memakai ANTARAGA:**

Menaruh tangan sedikit lebih rendah memang memperkuat sinyal PPG (darah lebih
terkumpul, perfusi naik). Tapi yang jauh lebih penting adalah **konsisten**:
posisi yang sama untuk semua subjek, di semua sesi.

Kalau tinggi tangan berubah-ubah antar subjek, perfusi ikut berubah karena posisi
- bukan karena kondisi fisiologis. Model akan mengira variasi itu bermakna, padahal
hanya artefak cara memegang.

> **Aturan praktis:** kedua lengan di atas meja, telapak menghadap ke atas,
> setinggi jantung, disangga. Sama untuk semua orang, setiap kali.

---

## 4. Prosedur Langkah demi Langkah

```
LANGKAH 1  Pasang ANTARAGA di pergelangan tangan seperti jam tangan (sensor ke dalam, sisi kulit)
LANGKAH 2  Buka dashboard → pilih device dari dropdown → pastikan sinyal real-time terlihat
LANGKAH 3  Tunggu sinyal stabil (biasanya 15–30 detik); minta subjek diam, lengan di atas meja
LANGKAH 4  Ukur tekanan darah di lengan BERLAWANAN dari yang memakai ANTARAGA
LANGKAH 5  Ukur gula darah (dan kolesterol / asam urat jika tersedia) - jari tangan mana saja
LANGKAH 6  Di dashboard → tab "Kalibrasi" → isi form identitas + nilai alat
LANGKAH 7  Klik "Simpan Sesi Kalibrasi" → server otomatis ambil buffer PPG 10 detik terakhir
LANGKAH 8  Verifikasi baris baru muncul di tabel dataset
LANGKAH 9  Bersihkan area tusukan, istirahatkan subjek, lanjut ke subjek berikutnya
```

---

### 4.1 ATURAN SELAMA AKUISISI - bacakan ke subjek

Sampaikan **sebelum** perekaman dimulai, bukan di tengah jalan. Menegur subjek saat
sinyal sedang direkam justru membuat mereka bergerak dan bicara.

> **"Selama sekitar satu menit ke depan, mohon:"**
>
> 1. **Duduk tenang** - punggung bersandar, kaki menapak lantai, jangan disilangkan
> 2. **Jangan bicara** - termasuk menjawab pertanyaan; cukup anggukan bila perlu
> 3. **Jangan menggerakkan tangan** - jari, pergelangan, maupun lengan
> 4. **Jangan menggenggam atau mengepal** - telapak dibiarkan terbuka dan rileks
> 5. **Bernapas biasa** - jangan menahan napas, jangan menarik napas dalam-dalam
> 6. **Jangan melihat layar HP** atau menoleh ke sana-sini
> 7. **Jangan batuk, tertawa, atau bersin** bila bisa ditahan - kalau terpaksa,
>    beri tahu petugas agar perekaman diulang

**Mengapa tiap aturan itu ada:**

| Larangan | Akibat pada data bila dilanggar |
|---|---|
| Bicara | Getaran dada + perubahan pola napas → baseline PPG bergelombang |
| Gerak tangan | Artefak gerak jauh lebih besar dari sinyal denyut (AC hanya ~1‰ dari DC) |
| Mengepal | Otot menekan pembuluh → perfusi turun drastis, sinyal nyaris hilang |
| Napas dalam | Modulasi napas menguat → tekanan darah dan periodisitas ikut bergeser |
| Kaki disilangkan | Sistolik naik 2–8 mmHg → nilai referensi jadi salah |
| Punggung tidak bersandar | Sistolik naik 5–10 mmHg |

Enam dari tujuh larangan di atas merusak **sinyal sensor**; dua terakhir merusak
**nilai referensi**. Keduanya sama-sama fatal, karena model belajar dari pasangan
keduanya.

**Tugas petugas selama akuisisi:**

- Berdiri di samping, **jangan mengajak bicara**
- Pantau grafik PPG di dashboard - bentuk gelombang harus berulang teratur
- Perhatikan **SQI** di dashboard: tunggu sampai ≥ 70/100 dan tanpa flag merah
- Bila muncul flag `MOTION` atau `FLAT`, tunggu hingga hilang sebelum menyimpan

---

### 4.2 Verifikasi Sebelum Menekan Simpan

Jangan langsung menekan Simpan begitu sinyal muncul. Empat hal wajib dicek:

**1. Tunggu minimal 15 detik setelah sinyal stabil**

Server menyaring lonjakan BPM dengan membandingkan terhadap pembacaan sebelumnya.
Bila Simpan ditekan seketika, penyaring belum punya acuan dan nilai pertama
diterima apa adanya - termasuk bila nilai itu salah.

**2. Periksa BPM masuk akal**

Bandingkan kartu **"BPM · Tersaring"** dengan nadi yang Anda hitung manual
(raba pergelangan, hitung 15 detik × 4). Bila selisihnya lebih dari ±10 bpm,
ulangi perekaman.

Waspadai khusus angka yang **tepat setengah atau tepat dua kali lipat** dari nadi
manual - misal terbaca 42 padahal nadi 84. Itu *octave error*: detektor melewatkan
satu dari dua denyut. Jangan disimpan.

**3. Periksa perfusi wajar**

Di tabel statistik dashboard, kolom **PERFUSI** kanal IR harus berada di rentang
**0,5–3,0‰**. Di luar itu artinya sensor kurang menempel atau terlalu ketat.

**4. Periksa kartu BPM tidak berstatus "ditahan"**

Bila kartu berwarna kuning bertuliskan *ditahan*, artinya sinyal sedang buruk dan
yang tampil adalah nilai lama. Tunggu sampai kembali hijau.

---

## 5. Teknis Pengambilan Setiap Parameter

### 5.1 Gula Darah (Glucometer)

1. Gunakan jari tangan mana saja - ANTARAGA ada di pergelangan tangan, tidak ada konflik dengan tusukan jari.
2. Bersihkan ujung jari dengan kapas alkohol, biarkan **benar-benar kering** (alkohol basah mengencerkan darah → hasil melenceng).
3. Tusuk sisi ujung jari (bukan tepat di tengah - lebih sedikit saraf).
4. Usap tetes pertama (darah pertama mengandung cairan jaringan → buang).
5. Tempelkan strip pada tetes darah kedua.
6. Baca hasil setelah ±5 detik.
7. **Catat nilai (mg/dL)** dan masukkan ke field "Gula Darah" di dashboard.

> Waktu ideal: dalam ±60 detik dari saat sensor ANTARAGA sedang merekam stabil.

### 5.2 Tekanan Darah Sistolik / Diastolik (Tensimeter Digital)

1. Pasang manset di lengan yang **tidak memakai ANTARAGA** (lengan berlawanan), setinggi jantung.
   - Alasan: manset tensimeter menghentikan aliran darah sementara - jika dipasang di lengan yang sama dengan ANTARAGA, sinyal PPG akan hilang selama pengukuran.
   - **Ketinggian manset wajib sejajar jantung** - lihat [3.4](#34-ketinggian-tangan--jangan-diabaikan). Lengan 20 cm terlalu rendah menaikkan sistolik ±15 mmHg.
   - Manset menempel langsung di kulit, bukan di atas lengan baju yang digulung (gulungan menekan lengan).
2. Subjek rileks, tidak bicara, tidak menggerakkan kedua lengan.
3. Tekan start - tunggu otomatis mengembang dan membaca.
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
- Jika tidak tersedia alat, biarkan field kosong - sistem akan melatih model hanya untuk target yang memiliki data.

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
| Sekadar bisa dilatih | 5 subjek | Metrik **tidak valid** - jangan dilaporkan |
| Proof-of-concept | 20 subjek | Model bisa dilatih, LOO CV |
| Laporan PKM | 30–50 subjek | Beralih ke 5-fold CV, metrik mulai bermakna |
| Publikasi ilmiah | ≥ 50 subjek | ~10 sampel per fitur (7 fitur) |

### Mengapa 5 Subjek Belum Cukup - Hasil Uji Nyata

Diuji pada 5 subjek pertama ANTARAGA, dibandingkan dengan tolok ukur paling
sederhana: **menebak nilai rata-rata, tanpa memakai sensor sama sekali**.

| Target | MLP | Tebak rata-rata |
|---|---|---|
| Gula Darah | 67,1% | **71,0%** ← tebakan menang |
| Kolesterol | 82,0% | **88,9%** ← tebakan menang |
| Sistolik | 86,2% | **89,1%** ← tebakan menang |
| Asam Urat | **92,7%** | 86,7% |
| Diastolik | **93,4%** | 90,3% |

Pada 3 dari 5 target, model kalah dari tebakan buta. Itu arti nyata dari R² negatif:
sensornya belum memberi informasi apa pun yang bisa dipakai.

> **Hati-hati membaca persentase akurasi.** Pada Asam Urat, "akurasi 92,7%" terlihat
> bagus padahal rentang nilainya sempit (4,5–6,3) sehingga menebak konstanta saja
> sudah dapat ~87%. **Gunakan R², bukan persentase**, saat melaporkan hasil.

### Komposisi Lebih Penting daripada Jumlah

Menambah baris dari orang yang sama **tidak** memperbaiki model. Yang dihitung
adalah jumlah **subjek unik**. Sistem mengelompokkan validasi silang per subjek,
sehingga 50 baris dari 5 orang tetap dinilai sebagai 5 titik data.

Tiga jebakan komposisi yang ditemukan pada 5 subjek pertama:

| Masalah | Kondisi awal | Yang dikejar |
|---|---|---|
| Tidak ada subjek sehat | Kolesterol 5/5 di atas 200 mg/dL | ≥ 10 subjek dengan kolesterol < 200 |
| Usia berhimpit dengan penyakit | Satu-satunya orang muda juga satu-satunya yang sehat | ≥ 8 subjek usia < 50 |
| Rentang usia sempit | 4 dari 5 berusia ≥ 55 | Sebar merata 20–80 tahun |

Jebakan kedua paling berbahaya. Bila semua yang tua kebetulan sakit dan semua yang
muda kebetulan sehat, model cukup menebak dari **umur** saja dan tetap terlihat
akurat - sensornya tidak berperan sama sekali. Yang memutus ini: cari **lansia
dengan tekanan darah normal** dan **orang muda dengan tekanan darah tinggi**.

Setiap subjek dapat diukur beberapa kali (kondisi berbeda), sehingga jumlah **baris** lebih banyak
dari jumlah **subjek unik**.

### Satu Sesi per Subjek ≈ 10 Menit

```
5  menit  - persiapan & istirahat
2  menit  - akuisisi PPG + pengukuran alat
3  menit  - pencatatan + pembersihan
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

**Cara termudah - lewat dashboard** (tidak perlu terminal):

Tab **Kalibrasi** → card "Pelatihan MLP":

| Tombol | Fungsi |
|---|---|
| 🏥 **Latih dari Data Asli** | Melatih dari rekaman subjek sungguhan saja |
| ⚡ **Latih dari Demo Data** | Melatih dari data sintetis - untuk menguji alur, **bukan** untuk klaim akurasi |
| ⬇ **Unduh Laporan HTML** | Laporan lengkap: scatter plot, R², MAE, jumlah data |

Setiap target menampilkan status **keterandalan**:

- `TIDAK VALID` - di bawah 10 subjek; angkanya hasil undian sampel, jangan dilaporkan
- `LEMAH` - 10–29 subjek; masih sangat goyah
- `MEMADAI` - ≥ 30 subjek; boleh dilaporkan

**Alternatif lewat terminal:**

```bash
python model/train_mlp_calibration.py
```

Output tersimpan di:
- `model/artifacts/mlp_calibration.joblib` - model terlatih
- `model/artifacts/mlp_calibration_metrics.json` - metrik (R², MAE, Akurasi)
- `reports/kalibrasi/scatter_*.png` - scatter plot prediksi vs referensi

### 8.4 Memeriksa Ulang BPM yang Terlanjur Tersimpan

Bila ada baris dengan BPM mencurigakan (tepat setengah atau dua kali lipat dari
yang seharusnya), nilai itu bisa dihitung ulang dari sinyal mentah yang tetap
tersimpan:

```bash
# 1. Lihat dulu - tidak menulis apa pun
curl -X POST "https://antaraga.web.id/v1/calibrate/recompute-bpm"

# 2. Bila setuju, baru terapkan
curl -X POST "https://antaraga.web.id/v1/calibrate/recompute-bpm?apply=true"
```

**Yang tidak tersentuh:** nilai alat ukur medis (gula darah, kolesterol, asam urat,
sistolik, diastolik) dan sinyal mentah. Hanya kolom `bpm` - yang memang hasil
hitung server, bukan hasil ukur alat - yang diperbarui, dan hanya bila selisihnya
memang berpola kesalahan oktaf. Perubahan tercatat di `logs/api.log`.

---

## 9. Troubleshooting

| Masalah | Kemungkinan Penyebab | Solusi |
|---|---|---|
| Sinyal PPG tidak muncul di dashboard | Sensor tidak terhubung / device salah | Periksa dropdown device, restart firmware |
| "Hubungkan perangkat dulu" saat klik Simpan | Device ID belum dipilih | Pilih device di dropdown bagian atas |
| Sinyal terlalu noise, tidak stabil | Jam terlalu longgar / subjek bergerak | Kencangkan tali ANTARAGA, minta subjek diam, lengan di atas meja |
| Nilai gula darah jauh dari normal | Tusukan gagal / strip kotor / alkohol belum kering | Ulangi dengan strip baru setelah alkohol kering |
| `sesi_ts` (waktu sesi) di tabel berbeda jauh | Server dan perangkat timezone berbeda | Server menggunakan UTC - tampilan dikonversi otomatis |
| BPM terbaca **tepat setengah** dari nadi manual (mis. 42 vs 84) | *Octave error* - detektor melewatkan satu dari dua denyut | Jangan disimpan; tunggu sinyal membaik. Bila terlanjur, lihat [8.4](#84-memeriksa-ulang-bpm-yang-terlanjur-tersimpan) |
| BPM mentok di angka ~60 dan tidak berubah | Kanal hijau terkunci pada artefak sambungan batch | Gunakan kartu **BPM · Tersaring** (bersumber dari IR), bukan angka kanal hijau |
| Kartu BPM kuning terus bertuliskan "ditahan" | Sinyal buruk berkepanjangan - sensor longgar / subjek bergerak | Perbaiki pemasangan; setelah 15 detik nilai dilepas jadi "-" |
| Perfusi IR di luar 0,5–3,0‰ | Sensor kurang menempel atau terlalu ketat | Sesuaikan kekencangan tali |
| Sistolik semua subjek terasa tinggi | Lengan tensimeter di bawah level jantung | Lihat [3.4](#34-ketinggian-tangan--jangan-diabaikan) - tiap 10 cm menambah ±7,7 mmHg |

---

## 10. Kartu Pengingat Ringkas

> Cetak dan tempel di meja pengambilan data.

```
┌────────────────────────────────────────────────────────────┐
│  ANTARAGA - PENGINGAT SESI KALIBRASI                       │
├────────────────────────────────────────────────────────────┤
│  SEBELUM                                                   │
│   □ Subjek duduk tenang 5–10 menit                         │
│   □ Tidak merokok 30 menit / olahraga 1 jam sebelumnya     │
│   □ Sensor bersih, tali pas (tidak longgar, tidak ketat)   │
│   □ Kedua lengan di meja, SETINGGI JANTUNG, disangga       │
│   □ Punggung bersandar, kaki menapak, tidak disilangkan    │
│                                                            │
│  BACAKAN KE SUBJEK                                         │
│   "Selama 1 menit ke depan, mohon:                         │
│      1. Duduk tenang                                       │
│      2. Jangan bicara                                      │
│      3. Jangan menggerakkan tangan                         │
│      4. Jangan mengepal - telapak terbuka rileks           │
│      5. Bernapas biasa, jangan menahan napas               │
│      6. Jangan melihat HP / menoleh                        │
│      7. Bila ingin batuk atau bersin, beri tahu dulu"      │
│                                                            │
│  URUTAN                                                    │
│   1. Pasang ANTARAGA (pergelangan kiri)                    │
│   2. Tunggu sinyal stabil - SQI ≥ 70, tanpa flag merah     │
│   3. Tensimeter (lengan kanan, setinggi jantung)           │
│   4. Glucometer (+ kolesterol / asam urat)                 │
│   5. Isi form → cek 4 hal di bawah → Simpan                │
│                                                            │
│  CEK SEBELUM SIMPAN                                        │
│   □ Sudah ≥ 15 detik sejak sinyal stabil                   │
│   □ BPM tersaring ±10 bpm dari nadi manual                 │
│   □ BPM bukan setengah / dua kali nadi manual              │
│   □ Perfusi IR 0,5–3,0‰                                    │
│   □ Kartu BPM hijau, bukan kuning "ditahan"                │
│                                                            │
│  SESUDAH                                                   │
│   □ Baris baru muncul di tabel dataset                     │
│   □ Bersihkan area tusukan                                 │
│   □ Export CSV di akhir sesi (backup)                      │
└────────────────────────────────────────────────────────────┘
```

---

*Dokumen ini adalah bagian dari proposal PKM-KC ANTARAGA - Non-Invasive Early Stroke Detection Smartband.*
