# DETAILING TIM TEKNIS - KADEK SAVITA DYUTIANAYA

**Peran:** Ketua Tim Riset · Koordinator Pelaksanaan · Penanggung Jawab Perizinan dan Etik
**Periode:** 24 Mei 2026 sampai 2 September 2026
**Program:** PKM-KC ANTARAGA - Smartband Deteksi Risiko Stroke Berbasis PPG dan Kecerdasan Buatan

> **Cara memeriksa bukti:** seluruh tangkapan layar dan foto dokumentasi tersimpan di Google Drive tim, tertata dalam folder menurut tanggal pengerjaan. Tiap bagian di bawah mencantumkan tanggal foldernya.

---

## Daftar Isi

1. [Tahap 1 - Perencanaan dan Pembagian Kerja](#tahap-1--perencanaan-dan-pembagian-kerja)
2. [Tahap 2 - Pemantauan Progres Tim](#tahap-2--pemantauan-progres-tim)
3. [Tahap 3 - Pengadaan Alat Ukur Terstandar](#tahap-3--pengadaan-alat-ukur-terstandar)
4. [Tahap 4 - Perizinan dan Ethical Clearance](#tahap-4--perizinan-dan-ethical-clearance)
5. [Tahap 5 - Koordinasi Pengujian Lapangan](#tahap-5--koordinasi-pengujian-lapangan)
6. [Tahap 6 - Peninjauan Dataset dan Arah Pengumpulan Data](#tahap-6--peninjauan-dataset-dan-arah-pengumpulan-data)
7. [Tahap 7 - Koordinasi HKI dan Laporan Kemajuan](#tahap-7--koordinasi-hki-dan-laporan-kemajuan)
8. [Ringkasan Kendala dan Penyelesaiannya](#ringkasan-kendala-dan-penyelesaiannya)
9. [Kesimpulan Capaian](#kesimpulan-capaian)

---

# Tahap 1 - Perencanaan dan Pembagian Kerja

**Periode: 24 Mei sampai 31 Mei 2026**

## 24 Mei 2026 - Penyusunan Draf Timeline dan Jobdesk (240 menit)

Penyusunan draf timeline kegiatan tim ANTARAGA untuk beberapa bulan ke depan berdasarkan jadwal pelaksanaan terbaru, sekaligus draf pembagian tugas tiap anggota.

**Hasil - pembagian tugas menurut kompetensi:**

| Anggota | Bidang tanggung jawab |
|---|---|
| Adam | Backend, kecerdasan buatan, aplikasi mobile, infrastruktur server |
| Ally | Perangkat keras, firmware, pengolahan sinyal |
| Kadek | Koordinasi, perizinan, etik penelitian, pengadaan |
| Tiwi | Administrasi, laporan, media sosial |
| Zeven | Desain visual, dokumentasi, materi presentasi |

**Pertimbangan penyusunan:** pembagian dibuat agar tidak ada dua anggota mengerjakan hal yang sama, sekaligus memastikan tiap bidang punya satu penanggung jawab yang jelas ketika ada kendala.

> 📎 **Bukti:** `KADEK_draf timeline kegiatan tim.png`, `KADEK_draf pembagian jobdesk.png`
> 🗂️ **Google Drive:** folder tanggal **24 Mei 2026**

## 31 Mei 2026 - Pemantauan Pelaksanaan Awal

Pemantauan terhadap pelaksanaan jobdesk awal tiap anggota, mencakup progres inisialisasi proyek dan perkakas pengembangan, serta pembuatan desain frame story dan konten "coming soon".

> 📎 **Bukti:** `KADEK_catatan pemantauan progres awal.png`
> 🗂️ **Google Drive:** folder tanggal **31 Mei 2026**

---

# Tahap 2 - Pemantauan Progres Tim

**Periode: 5 Juni sampai 17 Juli 2026**

Peran koordinasi di sini bukan sekadar menanyakan progres, melainkan memastikan hasil kerja tiap anggota saling cocok. Perangkat keras dan perangkat lunak dikerjakan terpisah, sehingga keduanya harus diperiksa kesesuaiannya sejak awal.

## 5 Juni 2026 - Peninjauan Rancangan Perangkat Keras

Peninjauan rancangan arsitektur perangkat keras, pemberian masukan teknis terkait integrasi komponen, serta validasi awal kelayakan desain.

> 📎 **Bukti:** `KADEK_review rancangan hardware.png`
> 🗂️ **Google Drive:** folder tanggal **5 Juni 2026**

## 7 Juni dan 11 Juni 2026 - Pemantauan Dua Jalur Pengerjaan

| Tanggal | Yang dipantau |
|---|---|
| 7 Juni | Pengembangan awal backend (Adam) dan desain skematik rangkaian (Ally) |
| 11 Juni | Pengembangan API (Adam) dan firmware sensor MAX30102 (Ally) |

**Tujuan pemantauan:** memastikan pengerjaan sesuai desain arsitektur yang telah disepakati dan sesuai target mingguan hasil weekly meeting.

**Alasan pemantauan dua jalur ini penting:** format data yang dikirim firmware harus persis sama dengan yang diharapkan backend. Kalau baru diperiksa setelah keduanya jadi, salah satu pihak harus membongkar ulang pekerjaannya.

> 📎 **Bukti:** `KADEK_pemantauan progres backend dan hardware.png`, `KADEK_catatan target mingguan.png`
> 🗂️ **Google Drive:** folder tanggal **7 Juni 2026** dan **11 Juni 2026**

## 17 Juli 2026 - Memimpin Daily Meeting

Persiapan bahan pembahasan dan memimpin jalannya daily meeting.

**Hasil pertemuan ini:** disepakati penggantian XIAO ESP32-C3 dengan versi S3, menindaklanjuti laporan keterbatasan SRAM dan komputasi protokol cloud dari sisi perangkat keras.

> 📎 **Bukti:** `KADEK_notulen daily meeting.png`
> 🗂️ **Google Drive:** folder tanggal **17 Juli 2026**

---

# Tahap 3 - Pengadaan Alat Ukur Terstandar

**Periode: 19 Juni 2026 (300 menit)**

**Pekerjaan:** pengambilan alat pengukur gula darah dan tekanan darah digital dari kampus, lalu pengetesan fungsionalitasnya.

**Alasan pengetesan dilakukan sebelum dipakai:** alat ukur ini menjadi acuan kebenaran bagi seluruh data kalibrasi. Kalau alatnya sendiri tidak akurat, seluruh dataset yang dibangun di atasnya ikut salah, dan kesalahannya tidak akan terdeteksi karena tidak ada pembanding lain.

**Konteks:** pengecekan dilakukan sebagai persiapan pemeriksaan kepada lansia pada keesokan harinya.

> 📎 **Bukti:** `KADEK_alat ukur gula darah dan tensimeter.png`, `KADEK_pengetesan fungsionalitas alat.png`
> 🗂️ **Google Drive:** folder tanggal **19 Juni 2026**

---

# Tahap 4 - Perizinan dan Ethical Clearance

**Periode: 2 Juli sampai 14 Juli 2026**

Ini bagian yang menentukan apakah penelitian boleh berjalan atau tidak. Tanpa persetujuan etik, seluruh data yang dikumpulkan tidak dapat dipakai untuk publikasi maupun dipertanggungjawabkan.

## 2 Juli 2026 - Izin Pengujian Alat

Penyusunan dan pengajuan dokumen permohonan izin pengujian alat kepada administrasi PENS, untuk memastikan kesiapan operasional pengujian di lapangan.

> 📎 **Bukti:** `KADEK_dokumen permohonan izin pengujian.png`
> 🗂️ **Google Drive:** folder tanggal **2 Juli 2026**

## 8 Juli 2026 - Riset Lokasi Pengajuan Ethical Clearance (300 menit)

**Percobaan:** penelusuran lembaga mana yang dapat menerbitkan ethical clearance beserta dokumen persyaratannya.

**Hasil:** ditetapkan lokasi pengajuan di **KEPK FKM Universitas Airlangga**.

**Alasan pemilihan:** PENS sebagai institut teknologi tidak memiliki komisi etik penelitian kesehatan sendiri. Karena ANTARAGA melibatkan subjek manusia lansia dengan pengambilan sampel darah, persetujuan etik dari komisi berkualifikasi kesehatan menjadi keharusan.

**Tindak lanjut hari itu juga:** tim langsung melengkapi dokumen yang dibutuhkan, tidak menunda ke hari berikutnya.

> 📎 **Bukti:** `KADEK_riset lokasi pengajuan etik.png`, `KADEK_daftar persyaratan kepk unair.png`
> 🗂️ **Google Drive:** folder tanggal **8 Juli 2026**

## 13 Juli 2026 - Peninjauan Cakupan Subjek (240 menit)

Diskusi bersama Tiwi terkait kelengkapan daftar lokasi dan calon naracoba yang telah disusun, untuk memastikan kesesuaiannya dengan cakupan penelitian yang diajukan pada berkas ethical clearance.

**Alasan pemeriksaan ini penting:** cakupan subjek yang tertulis di berkas etik mengikat pelaksanaan di lapangan. Merekrut subjek di luar cakupan yang disetujui berarti melanggar persetujuan yang sudah diberikan.

**Hasil hari itu:** berkas dikirimkan ke KEPK FKM Universitas Airlangga.

> 📎 **Bukti:** `KADEK_daftar lokasi dan calon naracoba.png`, `KADEK_bukti pengiriman berkas etik.png`
> 🗂️ **Google Drive:** folder tanggal **13 Juli 2026**

## 14 Juli 2026 - Pengarsipan Proses Pengajuan

Pengarsipan dan pendokumentasian proses pengajuan yang telah dikirimkan, termasuk penyimpanan salinan berkas dan bukti pengiriman sebagai rujukan.

**Alasan pengarsipan:** bukti pengiriman diperlukan bila kelak ditanyakan status pengajuan, dan salinan berkas diperlukan bila komisi meminta revisi.

> 📎 **Bukti:** `KADEK_arsip berkas dan bukti kirim.png`
> 🗂️ **Google Drive:** folder tanggal **14 Juli 2026**

---

# Tahap 5 - Koordinasi Pengujian Lapangan

**Periode: 30 Juli sampai 6 Agustus 2026**

## 30 Juli 2026 - Persiapan Pengujian Pertama

Pengoordinasian persiapan pengujian smartband terhadap relawan, mencakup tiga hal sekaligus.

| Aspek | Yang dipastikan |
|---|---|
| Kesiapan perangkat | Sensor berfungsi, daya terisi, pengiriman data stabil |
| Kelengkapan dokumen | Berkas perizinan dan persetujuan tersedia |
| Penjadwalan | Waktu sesi disepakati dengan subjek dan keluarganya |

**Alasan ketiganya harus siap serentak:** subjek lansia tidak dapat diminta datang berulang kali. Satu komponen yang tidak siap berarti sesi batal dan harus dijadwalkan ulang dari awal.

> 📎 **Bukti:** `KADEK_daftar periksa kesiapan pengujian.png`
> 🗂️ **Google Drive:** folder tanggal **30 Juli 2026**

## 2 Agustus 2026 - Memimpin Rapat Mingguan

Peninjauan progres tiap anggota dan evaluasi capaian terhadap target.

> 📎 **Bukti:** `KADEK_notulen rapat mingguan.png`
> 🗂️ **Google Drive:** folder tanggal **2 Agustus 2026**

## 5 Agustus dan 6 Agustus 2026 - Koordinasi Sesi Pengujian

| Tanggal | Kegiatan |
|---|---|
| 5 Agustus | Pengoordinasian persiapan: perangkat, alat medis terstandar, dokumen, penjadwalan |
| 6 Agustus | Pengoordinasian jalannya pengujian smartband kedua terhadap relawan |

> 📎 **Bukti:** `KADEK_persiapan sesi pengujian.png`, `KADEK_jalannya pengujian kedua.png`
> 🗂️ **Google Drive:** folder tanggal **5 Agustus 2026** dan **6 Agustus 2026**

---

# Tahap 6 - Peninjauan Dataset dan Arah Pengumpulan Data

**Periode: 16 Agustus 2026 (450 menit)**

Bagian ini yang paling menentukan arah pengumpulan data selanjutnya. Peninjauan dilakukan terhadap data hasil empat sesi pengujian yang telah terkumpul dari 6 relawan.

## Peninjauan komposisi dataset

Peninjauan dilakukan terhadap tiga target yang ditetapkan tim kecerdasan buatan: jumlah subjek, sebaran usia, dan sebaran nilai klinis.

**Tiga persoalan yang ditemukan:**

| # | Persoalan | Kondisi saat ditinjau | Akibat pada model |
|---|---|---|---|
| 1 | Tidak ada subjek sehat | Kolesterol seluruh subjek di atas 200 mg/dL | Model tidak punya contoh kondisi normal untuk dipelajari |
| 2 | Usia berhimpit dengan kondisi penyakit | Subjek muda yang terekam kebetulan juga yang paling sehat | Model berisiko sekadar menebak dari umur, bukan membaca sensor |
| 3 | Jumlah subjek | 6 dari target 30 | Fitur yang dipelajari lebih banyak daripada barisnya |

**Persoalan kedua paling perlu diwaspadai.** Kalau tiap subjek muda selalu sehat dan tiap subjek tua selalu sakit, model tidak punya cara membedakan mana yang benar-benar berpengaruh. Ia akan tampak akurat, padahal yang dipelajarinya hanya umur.

## Prioritas pencarian subjek yang ditetapkan

Berdasarkan temuan di atas, ditetapkan prioritas komposisi subjek untuk sesi kelima:

| Prioritas | Kriteria subjek | Persoalan yang diperbaiki |
|---|---|---|
| 1 | Lansia bertekanan darah normal | Memutus keterkaitan usia dengan penyakit |
| 2 | Orang muda bertekanan darah tinggi | Memutus keterkaitan usia dengan penyakit |
| 3 | Subjek berkolesterol di bawah 200 mg/dL | Menyediakan contoh kondisi normal |

**Catatan:** prioritas ini bukan sekadar menambah jumlah, melainkan sengaja mencari subjek yang polanya berlawanan dengan yang sudah terkumpul. Menambah sepuluh subjek dengan pola serupa tidak akan memperbaiki apa pun.

Dilakukan pula pemeriksaan kelengkapan berkas informed consent seluruh subjek terhadap data yang tersimpan.

## Koordinasi laporan kemajuan

Penetapan pembagian bagian laporan beserta tenggat internal tiap anggota, disertai pemeriksaan bahwa tiap capaian yang akan diklaim disertai bukti pendukung.

**Kendala:** sebagian anggota menuliskan capaian tanpa angka, sehingga diminta melengkapi dengan data terukur.

> 📎 **Bukti:** `KADEK_peninjauan komposisi dataset.png`, `KADEK_prioritas subjek sesi kelima.png`, `KADEK_pembagian bagian laporan.png`, `KADEK_pemeriksaan bukti pendukung.png`
> 🗂️ **Google Drive:** folder tanggal **16 Agustus 2026**

---

# Tahap 7 - Koordinasi HKI dan Laporan Kemajuan

**Periode: 9 Agustus sampai 2 September 2026**

## 9 Agustus dan 14 Agustus 2026 - Pendaftaran HKI

| Tanggal | Kegiatan |
|---|---|
| 9 Agustus | Pengurusan berkas administrasi pendaftaran HKI |
| 14 Agustus | Pengoordinasian penyerahan berkas ke sentra HKI kampus, memastikan seluruh lampiran lengkap sebelum diserahkan |

**Alasan pemeriksaan kelengkapan sebelum penyerahan:** berkas yang kurang lampiran akan dikembalikan, dan proses harus diulang dari awal.

> 📎 **Bukti:** `KADEK_berkas administrasi hki.png`, `KADEK_penyerahan berkas ke sentra hki.png`
> 🗂️ **Google Drive:** folder tanggal **9 Agustus 2026** dan **14 Agustus 2026**

## 23 Agustus sampai 2 September 2026 - Penyelesaian Laporan dan Sesi Lanjutan

| Tanggal | Kegiatan |
|---|---|
| 23 Agustus | Penyusunan dan pengoordinasian laporan kemajuan, memastikan tiap bagian tergarap dan seragam gaya penulisannya |
| 26 Agustus | Workshop Teknik Presentasi PKP2, penyusunan rencana pembagian peran saat penilaian |
| 28 Agustus | Memimpin asistensi laporan kemajuan ke dosen pendamping bersama seluruh anggota |
| 29 Agustus | Pengoordinasian finalisasi dan pengunggahan konten media sosial ketiga |
| 30 Agustus | Pengoordinasian pengujian smartband kelima |
| 2 September | Pengoordinasian pengujian smartband keenam |

**Catatan pada sesi kelima dan keenam:** komposisi subjek mengikuti prioritas yang ditetapkan pada 16 Agustus, bukan sekadar menerima siapa pun yang bersedia.

> 📎 **Bukti:** `KADEK_koordinasi laporan kemajuan.png`, `KADEK_asistensi ke dosen pendamping.png`, `KADEK_koordinasi pengujian kelima.png`, `KADEK_koordinasi pengujian keenam.png`
> 🗂️ **Google Drive:** folder tanggal **23 Agustus 2026**, **28 Agustus 2026**, **30 Agustus 2026**, dan **2 September 2026**

---

# Ringkasan Kendala dan Penyelesaiannya

| # | Kendala | Penyelesaian |
|---|---|---|
| 1 | PENS tidak memiliki komisi etik penelitian kesehatan | Pengajuan diarahkan ke KEPK FKM Universitas Airlangga |
| 2 | Cakupan subjek harus sesuai berkas etik | Peninjauan bersama daftar lokasi dan calon naracoba sebelum berkas dikirim |
| 3 | Alat ukur belum tentu akurat | Pengetesan fungsionalitas dilakukan sebelum dipakai mengambil data |
| 4 | Subjek lansia tidak dapat diminta datang berulang | Kesiapan perangkat, dokumen, dan jadwal dipastikan serentak sebelum sesi |
| 5 | Perangkat keras dan perangkat lunak dikerjakan terpisah | Pemantauan dua jalur agar format data cocok sejak awal |
| 6 | Keterbatasan mikrokontroler rancangan awal | Diputuskan penggantian ke XIAO ESP32-S3 pada daily meeting 17 Juli |
| 7 | Dataset tidak punya subjek berkondisi normal | Ditetapkan prioritas subjek berkolesterol di bawah 200 mg/dL |
| 8 | Usia berhimpit dengan kondisi penyakit | Ditetapkan prioritas lansia sehat dan orang muda bertekanan tinggi |
| 9 | Sebagian anggota menulis capaian tanpa angka | Diminta melengkapi dengan data terukur sebelum masuk laporan |
| 10 | Berkas HKI berisiko dikembalikan bila kurang lampiran | Pemeriksaan kelengkapan sebelum diserahkan ke sentra HKI |

---

# Kesimpulan Capaian

## Yang sudah selesai

### 1. Perizinan dan etik penelitian

- Izin pengujian alat dari administrasi PENS terbit
- Berkas ethical clearance terkirim ke KEPK FKM Universitas Airlangga pada 13 Juli 2026
- Salinan berkas dan bukti pengiriman terarsip
- Informed consent seluruh subjek terperiksa kelengkapannya

### 2. Pengadaan alat ukur terstandar

Alat pengukur gula darah dan tekanan darah digital tersedia dan telah lolos pengetesan fungsionalitas sebelum dipakai.

### 3. Koordinasi enam sesi pengujian

Enam sesi terlaksana, dengan sesi kelima dan keenam memakai komposisi subjek yang sengaja diarahkan untuk memperbaiki persoalan dataset.

### 4. Arah pengumpulan data yang terukur

Tiga persoalan komposisi dataset teridentifikasi beserta prioritas perbaikannya, bukan sekadar target menambah jumlah subjek.

### 5. Berkas HKI terserahkan

Seluruh lampiran terperiksa lengkap sebelum diserahkan ke sentra HKI kampus pada 14 Agustus 2026.

## Yang belum selesai

| Hal | Kondisi | Yang dibutuhkan |
|---|---|---|
| Status ethical clearance | Berkas sudah terkirim | Menunggu keputusan KEPK FKM Unair |
| Jumlah subjek | 6 dari target 30 | Sesi pengujian lanjutan |
| Subjek berkolesterol normal | Belum ada | Perekrutan sesuai prioritas 16 Agustus |
| Sebaran usia | Masih berhimpit dengan kondisi penyakit | Minimal 8 subjek berusia di bawah 50 tahun |
| Hasil kunjungan dokter | Kunjungan sudah dilakukan | Pendokumentasian hasil |

## Catatan penutup

Peran koordinasi pada ANTARAGA tidak berhenti pada penjadwalan. Dua keputusan yang paling berdampak justru bersifat teknis:

1. **Pengarahan pengajuan etik ke lembaga berkualifikasi kesehatan** memastikan data yang dikumpulkan dapat dipertanggungjawabkan, bukan sekadar terkumpul.
2. **Penetapan prioritas komposisi subjek pada 16 Agustus** mengubah cara perekrutan dari sekadar menambah jumlah menjadi sengaja mencari pola yang berlawanan, karena menambah subjek berpola serupa tidak memperbaiki kemampuan model.

Pemantauan dua jalur pengerjaan sejak Juni juga terbukti mencegah pembongkaran ulang: format data firmware dan backend dicocokkan sejak keduanya masih dalam pengembangan, bukan setelah keduanya jadi.

---

*Dokumen ini merupakan bagian dari Laporan Kemajuan PKM-KC ANTARAGA 2026.*
