# LAPORAN KEMAJUAN
## PROGRAM KREATIVITAS MAHASISWA - KARSA CIPTA (PKM-KC) 2026
## ANTARAGA: Smartband Berbasis Multi-Wavelength PPG dengan Artificial Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia

> **Catatan revisi (dibuat 2026-09-07):** berkas ini adalah revisi dari `Draf Laporan Kemajuan ANTARAGA.pdf`. Perubahan yang dilakukan:
> 1. Melengkapi seluruh tabel Lampiran 1 yang sebelumnya kosong (SQI, konektivitas Wi-Fi/API, dashboard, penyimpanan data, latensi, heart rate, dokumentasi XGBoost/MLP, bukti luaran digital, validasi medis) dengan narasi dari logbook dan data kalibrasi asli yang sudah terverifikasi.
> 1b. Mengganti "BLE" menjadi "Wi-Fi" di seluruh dokumen (draf lama salah menulis BLE, padahal smartband terhubung lewat Wi-Fi).
> 2. Memperbaiki BAB 6 yang sebelumnya cuma satu baris dengan placeholder "RpX"/"Rp0" — sekarang berisi seluruh rencana kegiatan 3-19 September 2026 sesuai logbook.
> 3. Merapikan penomoran Lampiran yang sebelumnya bertumpuk tiga versi berbeda (ada tiga "Lampiran 1" yang saling tumpang tindih di draf lama) menjadi satu struktur konsisten sesuai Daftar Isi (Lampiran 1-5).
> 4. Memperbaiki tabel riwayat relawan yang datanya ganjil (tertulis "Tidak Stroke N=12" padahal total relawan cuma 6 orang).
> 5. Menstandarkan nilai `scale_pos_weight` XGBoost ke **19,55** di seluruh dokumen, sesuai logbook 16 Juli 2026 (validasi final XGBoost vs HistGradientBoosting, tempat XGBoost "ditetapkan secara final" sebagai algoritma utama). Angka 19,52 (10 Juli) adalah rasio dari keseluruhan dataset sebelum dibagi train/test; `model/artifacts/metrics.json` model produksi mencatat 19,56 (rasio dari split train/test spesifik yang dipakai melatih model yang aktif sekarang) — tim memilih memakai 19,55 sebagai angka resmi laporan karena itu yang tercatat sebagai keputusan final di logbook.
> 6. Setiap tempat yang butuh foto/screenshot ditandai dengan `<!-- GAMBAR: ... -->` beserta **tanggal logbook dan link Drive** sumbernya, supaya tinggal disalin manual.
> 7. Tabel hasil pengujian relawan (Lampiran 1.4) diisi dengan nilai asli dari `kalibrasi_semua.csv` (S001-S009) — bukan angka karangan.
>
> Tempat yang saya beri tanda **[PERLU DICEK]** artinya saya tidak punya cukup informasi untuk mengisi sendiri (butuh keputusan/data dari tim), jangan dibiarkan tertinggal saat submit.

---

## DAFTAR ISI

- [BAB 1. PENDAHULUAN](#bab-1-pendahuluan)
- [BAB 2. TARGET LUARAN](#bab-2-target-luaran)
- [BAB 3. TAHAP PELAKSANAAN](#bab-3-tahap-pelaksanaan)
- [BAB 4. HASIL YANG DICAPAI](#bab-4-hasil-yang-dicapai)
- [BAB 5. POTENSI HASIL](#bab-5-potensi-hasil)
- [BAB 6. RENCANA TAHAPAN BERIKUTNYA](#bab-6-rencana-tahapan-berikutnya)
- [DAFTAR PUSTAKA](#daftar-pustaka)
- [LAMPIRAN 1. Bukti Teknis dan Rekap Pengujian Prototipe](#lampiran-1-bukti-teknis-dan-rekap-pengujian-prototipe)
- [LAMPIRAN 2. Rincian Logbook Kegiatan](#lampiran-2-rincian-logbook-kegiatan)
- [LAMPIRAN 3. Rincian Publikasi Media Sosial](#lampiran-3-rincian-publikasi-media-sosial)
- [LAMPIRAN 4. Rincian Anggaran dan Penggunaan Dana](#lampiran-4-rincian-anggaran-dan-penggunaan-dana)
- [LAMPIRAN 5. Ethical Clearance dan Bukti Hak Cipta](#lampiran-5-ethical-clearance-dan-bukti-hak-cipta)

---

## BAB 1. PENDAHULUAN

### 1.1 Latar Belakang

Stroke merupakan salah satu masalah kesehatan dengan dampak kematian dan kecacatan neurologis yang tinggi. Global Stroke Fact Sheet 2025 melaporkan sekitar 6,7 juta kematian akibat stroke setiap tahun. Sekitar 87% kasus merupakan stroke iskemik yang sangat sensitif terhadap waktu, sehingga keterlambatan penanganan dapat memperburuk luaran pasien (Feigin dkk., 2025; Capirossi dkk., 2023).

Salah satu hambatan penting terjadi pada fase prarumah sakit ketika keluarga terlambat mengenali urgensi gejala dan mengambil keputusan menuju fasilitas kesehatan. Kondisi ini semakin sulit ketika keluhan menyerupai Transient Ischaemic Attack (TIA) yang dapat hilang timbul. Meskipun kampanye FAST membantu pengenalan gejala, keputusan keluarga masih dapat dipengaruhi keraguan, kepanikan, atau anggapan bahwa kondisi telah membaik (Potisopha dkk., 2023; Writing Committee for the PERSIST Collaborators, 2025).

Kondisi tersebut menunjukkan perlunya sarana pemantauan yang dapat memberikan informasi risiko secara lebih objektif kepada keluarga. Perkembangan wearable, Photoplethysmography (PPG), Internet of Things (IoT), dan kecerdasan buatan membuka peluang untuk memenuhi kebutuhan tersebut. Namun, perangkat wearable kesehatan umumnya masih berorientasi pada pemantauan kebugaran dan penyajian parameter numerik, belum terintegrasi dengan mekanisme penilaian risiko dan tindak lanjut keluarga.

Menjawab kebutuhan tersebut, ANTARAGA dikembangkan sebagai smartband berbasis PPG multi-wavelength dengan kecerdasan buatan yang terintegrasi aplikasi mobile. Sistem memantau indikator fisiologis dan faktor risiko untuk memberikan informasi risiko, peringatan, serta asesmen ABCD2 sebagai pendukung keputusan keluarga menuju evaluasi medis. ANTARAGA tidak ditujukan sebagai alat diagnosis, melainkan untuk membantu mempercepat pengambilan keputusan pada fase prarumah sakit.

### 1.2 Tujuan dan Relevansi dengan Tema PKM 2026

Smartband ANTARAGA bertujuan membantu mendeteksi risiko stroke iskemik lebih dini sehingga mencegah terjadinya keterlambatan penanganan sesuai dengan prinsip *time is brain*. Tujuan tersebut relevan dengan tema PKM 2026, yaitu "Kesehatan dan Gizi Masyarakat" karena memanfaatkan teknologi kesehatan untuk meningkatkan kewaspadaan keluarga terhadap risiko stroke dan mendukung pendampingan kesehatan lansia di lingkungan rumah.

### 1.3 Inovasi Karsa Cipta dan Kemutakhirannya

Inovasi ANTARAGA sebagai sistem pemantauan faktor risiko stroke iskemik berbasis smartband mengintegrasikan beberapa teknologi mutakhir sebagai berikut:

1. **Akuisisi Sinyal PPG Multi-Wavelength**
   ANTARAGA menggunakan sensor SON1303 pada kanal hijau 525 nm serta MAX30102 pada kanal merah 660 nm dan inframerah 880 nm untuk merekam sinyal Photoplethysmography (PPG). Penggunaan beberapa panjang gelombang memanfaatkan karakteristik penetrasi cahaya yang berbeda pada jaringan sehingga sinyal lebih informatif untuk pemantauan fisiologis (Kim dan Baek, 2023).
2. **Pengolahan Sinyal Terdistribusi antara Smartband dan Server**
   Smartband melakukan pencuplikan tiga kanal PPG, penyusunan batch data, dan penilaian kualitas sinyal menggunakan Signal Quality Index (SQI), sedangkan server menjalankan penapisan bandpass Butterworth 0,5-5 Hz, autokorelasi FFT, dan perhitungan BPM. Pembagian proses ini mengurangi beban komputasi mikrokontroler sekaligus memudahkan pembaruan algoritma pada server.
3. **Penilaian Risiko Stroke Menggunakan XGBoost**
   Model Extreme Gradient Boosting (XGBoost) digunakan untuk menilai risiko stroke berdasarkan sembilan faktor masukan pengguna, menggantikan model Gradient Boosting generik yang direncanakan pada proposal. XGBoost dipilih karena menyediakan regularisasi L1/L2 bawaan yang menekan overfitting pada dataset berukuran terbatas, penanganan native terhadap nilai fitur yang hilang tanpa perlu imputasi manual, serta parameter `scale_pos_weight` untuk membobot ulang kelas minoritas — kebutuhan utama pada dataset ini karena kelas stroke hanya sekitar 4,87% dari keseluruhan data. Pemilihan ini diverifikasi melalui perbandingan langsung terhadap HistGradientBoosting (varian gradient boosting lain yang lebih baru) pada tahap evaluasi model (lihat BAB 4.4.1), bukan sekadar pilihan default. Ketidakseimbangan kelas pada dataset ditangani melalui `scale_pos_weight`, sedangkan ambang keputusan dievaluasi menggunakan prediksi out-of-fold dan kurva Precision-Recall untuk meningkatkan sensitivitas terhadap kelas berisiko (Luo dkk., 2025).
4. **Estimasi Parameter Fisiologis Menggunakan Multi-Layer Perceptron**
   Lima model Multi-Layer Perceptron (MLP) dikembangkan untuk memetakan fitur optik PPG menjadi estimasi gula darah, kolesterol, asam urat, tekanan sistolik, dan tekanan diastolik. Model terintegrasi dengan dashboard server sehingga dapat dilatih ulang ketika tersedia data kalibrasi baru.
5. **Integrasi Peringatan Risiko dan Asesmen ABCD2 pada Aplikasi Mobile**
   Hasil pemantauan terintegrasi dengan aplikasi mobile keluarga. Ketika sistem mendeteksi peningkatan risiko, aplikasi memberikan peringatan dan mengaktifkan asesmen ABCD2 untuk membantu menentukan tingkat urgensi berdasarkan faktor klinis dan durasi gejala (Spampinato dkk., 2022). Integrasi ini mendukung keluarga dalam mengambil keputusan evaluasi medis lebih cepat pada fase prarumah sakit.

---

## BAB 2. TARGET LUARAN

### 2.1 Laporan Kemajuan

Laporan kemajuan sebagai bentuk dokumentasi pelaksanaan program telah disusun dengan tingkat penyelesaian 100%. Kegiatan-kegiatan ini telah tercatat pada Logbook Kegiatan dengan capaian 95% (311 entri tercatat s.d. 19 September 2026, dengan capaian resmi dihitung sampai entri 2 September 2026 — lihat catatan di Lampiran 2), dengan bukti pengeluaran dan Logbook Kegiatan terlampir pada Lampiran 2 dan 4.

### 2.2 Laporan Akhir

Laporan akhir memuat seluruh hasil akhir pelaksanaan dan pengembangan smartband ANTARAGA dengan capaian 75%, mencakup kerangka laporan, hasil pengujian awal, dan dokumentasi kegiatan yang telah tersusun. Penyempurnaan lebih lanjut akan dilakukan setelah pengujian tambahan dan pelatihan ulang model AI selesai, sejalan dengan rencana tahapan pada BAB 6.

### 2.3 Prototipe ANTARAGA

Prototipe smartband ANTARAGA telah terealisasi dengan capaian 90% sebagai smartband pendeteksi risiko stroke iskemik pada lansia, yang terintegrasi dengan aplikasi mobile ANTARAGA sehingga dapat dipantau langsung oleh keluarga. Smartband telah digunakan dalam 11 kali pengujian hingga 5 September 2026. Sisa capaian dialokasikan untuk pelatihan lanjutan model AI (XGBoost dan MLP) menggunakan data kalibrasi tambahan dari sesi pengujian relawan.

### 2.4 Akun dan Konten Media Sosial ANTARAGA

Publikasi media sosial Instagram telah mencapai 100% melalui 3 konten program yang dipublikasikan dan diiklankan pada 6 Juni, 4 Juli, dan 29 Agustus 2026. Konten wajib tersebut mencakup Pengenalan ANTARAGA, Edukasi Tanda Risiko, dan Pengujian ANTARAGA.

### 2.5 Aplikasi Mobile ANTARAGA

Aplikasi Mobile ANTARAGA telah dikembangkan dan mencapai 100%. Aplikasi ini telah didaftarkan pada Play Store dengan sasaran pengguna Android, serta terhubung dengan backend untuk menampilkan hasil pemantauan dan prediksi risiko dari smartband.

### 2.6 Video Simulasi dan Pengujian ANTARAGA

Video simulasi skenario penggunaan dan pengujian telah mencapai 100%, telah dipublikasikan sebagai konten program 1 dan konten program 3.

### 2.7 Hak Cipta Program Komputer

ANTARAGA telah memperoleh Hak Cipta Program Komputer dengan capaian 100%, dibuktikan dengan Surat Pencatatan Ciptaan oleh Kementerian Hukum dengan nomor pencatatan 001449089. Surat tersebut dapat dilihat pada Lampiran 5.

---

## BAB 3. TAHAP PELAKSANAAN

### 3.1 Alat dan Bahan

Berikut disajikan alat dan bahan utama yang digunakan dalam pengembangan smartband ANTARAGA berdasarkan realisasi hingga tahap pengujian saat ini.

**Tabel 3.1 Alat dan Bahan Utama**

| No | Komponen | Fungsi/Keterangan Aktual |
|---|---|---|
| 1 | XIAO ESP32-S3 | Mikrokontroler utama setelah migrasi dari ESP32-C3 |
| 2 | SON1303 dan MAX30102 | Akuisisi PPG hijau, merah, dan inframerah |
| 3 | TP5000, LDO RT9013-33GB, Li-Po 950 mAh | Pengisian, pengaturan tegangan, dan sumber daya |
| 4 | PCB dan casing PETG | Casing didesain internal tim, dicetak melalui jasa 3D printing eksternal; PCB difabrikasi mandiri |
| 5 | Peralatan fabrikasi & desain | Digunakan untuk perancangan casing dan pembuatan PCB mandiri |
| 6 | VPS, Flutter | Infrastruktur server dan pengembangan aplikasi |
| 7 | Multimeter, tensimeter, glukometer digital | Alat ukur pembanding terstandar untuk validasi pengujian terhadap relawan |

Pengembangan prototipe smartband ANTARAGA memperbarui mikrokontroler yang digunakan dari XIAO ESP32-C3 menjadi XIAO ESP32-S3 karena memiliki 2 core pemrosesan dan kapasitas SRAM lebih besar, sehingga memungkinkan untuk menjalankan transmisi data ke cloud dan pembacaan sensor secara bersamaan.

### 3.2 Realisasi Pelaksanaan Program

Tahapan pelaksanaan program ANTARAGA yang telah direalisasikan berfokus pada fase perancangan hingga perlindungan kekayaan intelektual. Rincian ketercapaian pada setiap tahap pelaksanaan adalah sebagai berikut:

1. **Studi Literatur:** Kajian PPG tiga panjang gelombang, pengolahan sinyal, class imbalance, ABCD2, dan arsitektur wearable telah selesai.
2. **Perancangan Sistem:** Skematik, tata letak PCB, optimalisasi manajemen daya, basis data, backend, aplikasi, dan arsitektur dua model telah diselesaikan.
3. **Pembuatan Prototipe:** PCB difabrikasi mandiri, casing PETG dicetak, komponen dirakit, dan mikrokontroler diganti dari XIAO ESP32-C3 ke ESP32-S3 sebelum fabrikasi.
4. **Integrasi Sistem:** Firmware, Wi-Fi, API, VPS, dashboard, dan aplikasi telah terhubung. Pengolahan bandpass, FFT, dan BPM dipindahkan ke server, sedangkan SQI dipertahankan di perangkat.
5. **Pengembangan Model AI:** XGBoost telah dituning dan diterapkan dengan dua ambang keputusan; pipeline lima MLP telah terintegrasi dan dilatih menggunakan data kalibrasi yang tersedia.
6. **Pengujian dan Validasi:** Pengujian subsistem, enam sesi relawan, analisis mutu sinyal, koreksi BPM, dan konsultasi dokter spesialis saraf telah dilaksanakan.
7. **Pelaporan dan Publikasi:** Laporan kemajuan, bahan presentasi, dokumentasi, dan tiga konten utama media sosial telah disusun dan dipublikasikan.
8. **Pengajuan HKI:** Hak Cipta Program Komputer ANTARAGA telah tercatat dan terbit.

Dokumentasi pelaksanaan seluruh tahapan kegiatan tertera pada Lampiran 1.

---

## BAB 4. HASIL YANG DICAPAI

### 4.1 Dampak Pengiklanan Media Sosial

Kampanye edukasi dan publikasi melalui pengiklanan Instagram telah selesai terlaksana 100% dalam 3 gelombang. Rekapitulasi capaian disajikan pada Tabel 4.1.

**Tabel 4.1 Rekapitulasi Metrik Capaian Pengiklanan Media Sosial**

| Metrik Capaian | Iklan 1 (Pengenalan ANTARAGA) | Iklan 2 (Edukasi Tanda Risiko) | Iklan 3 (Pengujian ANTARAGA) | Total Capaian |
|---|---|---|---|---|
| Jangkauan | 10.358 | 11.380 | 15.448 | 37.186 |
| Tayangan | 12.403 | 15.332 | 26.629 | 54.364 |
| Interaksi | 2.336 | 4.237 | 4.530 | 11.103 |
| Kunjungan Profil | 291 | 281 | 436 | 1.008 |
| Pengikut Baru | 6 | 9 | 15 | 30 |

Peningkatan metrik tersebut menunjukkan bahwa konten yang lebih detail dan informatif efektif meningkatkan visibilitas serta keterlibatan audiens terhadap program.

<!-- GAMBAR 4.1: opsional, dokumentasi tambahan pengiklanan media sosial. Sumber: Drive 6 Juni 2026 (https://drive.google.com/drive/folders/170jaWbwhKVjynhWddFnmKCOB3L4zCCSS), 4 Juli 2026 (https://drive.google.com/drive/folders/1kduz9iobzAMgsJnB3-2L1v9eIQdG-Icm), 29 Agustus 2026 (https://drive.google.com/drive/folders/107l7Drt_-EqX-IKg4z_x3ub-AA2ruDBM) -->

### 4.2 Spesifikasi Prototipe ANTARAGA

Realisasi pembuatan smartband ANTARAGA telah mencapai 100% dengan spesifikasi hardware smartband ANTARAGA langsung disajikan pada Tabel 4.2.

<!-- GAMBAR 4.2: Desain 3D Prototipe ANTARAGA (Fusion 360). Sudah ada di draf PDF lama, tinggal disalin dari sana jika file sumbernya (.f3d/.step/render) tidak disimpan terpisah. -->

**Tabel 4.2 Spesifikasi Hardware Smartband ANTARAGA**

| No | Komponen/Modul | Spesifikasi Teknis Hasil Realisasi | Fungsi & Hasil Pengujian |
|---|---|---|---|
| 1 | Mikrokontroler | XIAO ESP32-S3, dual-core Xtensa LX7 32-bit | Pusat pencuplikan sinyal, transmisi Wi-Fi, dan firmware penyaring SQI. |
| 2 | Sensor PPG Hijau | SON1303 (Kanal Hijau 525 nm) | Merekam dinamika denyut nadi, dilengkapi ferrite bead penekan noise 50 Hz. |
| 3 | Sensor PPG Merah/NIR | MAX30102 (Merah 660 nm & Inframerah 880 nm) | Sumber data utama Pulse Wave Analysis dan ekstraksi indikator fisiologis. |
| 4 | Manajemen Power Supply | Baterai LiPo 1S, LDO RT9013-33GB | Pasokan tegangan bebas ripple switching dengan durasi pasokan baterai terukur. |
| 5 | PCB | PCB Fabrikasi Mandiri | Pondasi dari seluruh komponen elektronik. |
| 6 | Enclosure | PETG 3D Printing | Casing sebagai pelindung komponen dari keringat. |

1. **Realisasi Hardware & Firmware:** Sistem power supply yang didukung regulator LDO 3,3V terbukti menjaga kestabilan sinyal optik pada rentang tegangan baterai 3,0-4,2V. Pengujian discharge baterai pada beban 500 mA konstan menghasilkan kapasitas efektif terhitung sebesar 813 mAh (durasi 97 menit 35 detik — lihat Lampiran 1).
2. **Arsitektur Pemrosesan Sinyal:** Pengolahan sinyal berat (bandpass Butterworth 0,5-5 Hz dan autokorelasi FFT BPM) dialihkan dari firmware ke server VPS untuk menghemat daya dan SRAM ESP32-S3, sementara firmware berfokus pada pencuplikan data dan penilaian mutu sinyal (Signal Quality Index).
3. **Aplikasi Mobile Flutter:** Aplikasi telah selesai dibangun, terhubung melalui Wifi ke smartband dan API FastAPI di VPS ([www.antaraga.web.id](https://www.antaraga.web.id)) untuk menampilkan tren fisiologis dan mengirimkan notifikasi peringatan kepada keluarga melalui aplikasi.

Berikut adalah tautan video pengujian ANTARAGA:

<https://drive.google.com/file/d/13KHnk6g6ESceC37GzXaLVtgXvqBJEyDb/view?usp=drive_link>

### 4.3 Spesifikasi Aplikasi Mobile ANTARAGA

Aplikasi mobile ANTARAGA dikembangkan menggunakan Flutter sebagai antarmuka utama bagi keluarga dalam melakukan pemantauan kondisi lansia. Aplikasi terintegrasi dengan backend melalui API sehingga data hasil pemantauan dari smartband dapat ditampilkan pada perangkat pengguna.

Fitur utama aplikasi meliputi autentikasi pengguna, pengelolaan profil lansia (termasuk dukungan lebih dari satu profil lansia per akun), koneksi smartband berdasarkan Device ID, pemantauan tanda vital, tampilan statistik harian, informasi prediksi risiko stroke berbasis AI, serta asesmen ABCD2. Bukti tangkapan layar tiap fitur tercantum pada Lampiran 1.6.

Pada halaman dashboard, pengguna dapat melihat profil lansia yang sedang dipantau, status koneksi perangkat, nilai tekanan darah, detak jantung, gula darah, serta informasi tingkat risiko stroke (kategori Rendah/Sedang/Tinggi) berdasarkan model AI. Hasil pemantauan juga dapat ditampilkan dalam bentuk statistik dan timeline untuk membantu keluarga melihat perubahan kondisi dari waktu ke waktu.

Aplikasi juga menyediakan asesmen ABCD2 untuk membantu keluarga melakukan penilaian awal berdasarkan faktor klinis yang relevan. Hasil asesmen ditampilkan dalam bentuk skor, kategori risiko, serta estimasi risiko stroke berikutnya dalam periode 2, 7, dan 90 hari berdasarkan kohort validasi ABCD2 (Johnston dkk., 2007, dikutip dalam Spampinato dkk., 2022) untuk menjaga hasil yang ditampilkan tetap berlandaskan literatur klinis yang tervalidasi.

<!-- GAMBAR 4.3: Flowchart pengiriman data alat ke aplikasi. DIAGRAM INI BELUM ADA DI DRAF LAMA (cuma judulnya, gambarnya kosong) -- perlu dibuat baru, alurnya: Smartband (sensor PPG) -> Wi-Fi -> API FastAPI di VPS -> Database -> Aplikasi Mobile (dashboard + notifikasi risiko). Bisa dibuat di draw.io/PowerPoint/Figma. -->

### 4.4 Hasil Pelatihan dan Pengujian

#### 4.4.1 Hasil Pelatihan Model XGBoost

Dataset model risiko memiliki class imbalance dengan kelas stroke sekitar 4,87%. Karena akurasi dapat menyesatkan pada kondisi tersebut, evaluasi menggunakan Average Precision dan recall. XGBoost dengan `scale_pos_weight` **19,55** dibandingkan dengan HistGradientBoosting melalui RandomizedSearchCV dan StratifiedKFold lima lipatan. Empat puluh kombinasi parameter melalui lima validasi silang menghasilkan 200 proses pelatihan.

**Tabel 4.3 Evaluasi Model XGBoost**

| Metrik/Parameter | XGBoost | HistGradientBoosting |
|---|---|---|
| Average Precision terbaik | 0,2313 | 0,2281 |
| Penanganan imbalance | scale_pos_weight = 19,55 | Model pembanding |
| Keputusan | Dipilih | Tidak dipilih |
| Threshold awal | 0,705; F1 = 0,2946 | - |
| Threshold sensitivitas | 0,042; recall = 0,973 | - |

<!-- GAMBAR 4.4: Perbandingan Recall Model XGBoost (bar chart 0,493 vs 0,973) -- sudah ada di draf PDF lama, tinggal disalin. -->

Threshold awal 0,705 dipilih berdasarkan F1-score terbaik sebesar 0,2946. Optimasi berikutnya memprioritaskan sensitivitas sistem peringatan dan menghasilkan threshold 0,042 dengan recall 0,973, yaitu 73 dari 75 kasus stroke pada data uji berhasil terdeteksi.

#### 4.4.2 Hasil Pelatihan Model MLP

MLP telah dibangun dan terintegrasi dengan dashboard sehingga pelatihan ulang dapat dilakukan ketika tersedia data baru. Kapasitas model diskalakan otomatis mengikuti jumlah data kalibrasi yang tersedia (1 lapisan 4 neuron untuk data di bawah 10 subjek, 2 lapisan untuk data lebih besar) supaya model tidak menghafal data yang masih sedikit. Evaluasi kuantitatif menggunakan MAE, RMSE, MAPE, dan R² dengan skema validasi Leave-One-Subject-Out (setiap subjek diuji oleh model yang tidak pernah melihat data subjek tersebut saat dilatih).

Hasil pelatihan pada 11 subjek kalibrasi yang tersedia hingga 5 September 2026 disajikan pada Tabel 4.4. Nilai R² digunakan sebagai indikator utama kejujuran model (R² mendekati atau di atas nol berarti model benar-benar belajar pola, R² negatif berarti model belum lebih baik daripada menebak nilai rata-rata):

**Tabel 4.4 Evaluasi Model MLP per Parameter (LOO, n=11 subjek)**

> **[PERLU DICEK — MENUNGGU DATA]** Angka MAE/R²/Akurasi di tabel ini masih dari pelatihan n=9 (S001-S009, data sampai 2 September 2026). Begitu S010 dan S011 masuk logbook dan model dilatih ulang, **tabel ini harus dihitung ulang dari hasil training n=11 yang sebenarnya** — bukan cuma mengganti label "9" jadi "11" tanpa data barunya, karena MAE/R²/Akurasi pasti berubah nyata dengan 2 subjek tambahan. Kabari saya begitu logbook & pelatihan ulang selesai supaya angka di sini saya perbarui dari hasil yang asli.

| Parameter | N | MAE | R² | Akurasi Sesi (%) | Catatan |
|---|---|---|---|---|---|
| Gula Darah | 9 | 103,03 mg/dL | -8,09 | 22,7% | Belum belajar pola, perlu data lebih banyak |
| Kolesterol | 9 | 30,68 mg/dL | -1,41 | 86,17% | R² negatif meski akurasi % terlihat baik — indikasi rentang nilai training masih sempit (lihat pembahasan) |
| Asam Urat | 9 | 1,65 mg/dL | -2,68 | 67,1% | Belum belajar pola, perlu data lebih banyak |
| Sistolik | 9 | 25,17 mmHg | -1,70 | 82,25% | Belum belajar pola, perlu data lebih banyak |
| Diastolik | 9 | 16,33 mmHg | -1,40 | 78,07% | Belum belajar pola, perlu data lebih banyak |

<!-- GAMBAR 4.5: Dashboard Pelatihan Model MLP -- screenshot tab "Pelatihan MLP" di dashboard (antaraga.web.id), ambil tangkapan layar baru saat laporan ini difinalisasi. -->

Dengan n=9 subjek, sistem sendiri menandai hasil ini berstatus "TIDAK VALID" secara statistik (ambang keandalan dashboard mensyaratkan minimal 30 subjek) — metrik di atas mencerminkan kondisi jujur saat ini, bukan klaim akurasi final alat. Simulasi lanjutan menggunakan data sintetis berjumlah lebih besar (240 rekaman, 20 subjek, dengan variasi kondisi fisiologis termasuk pola *isolated systolic hypertension* pada lansia) menunjukkan bahwa arsitektur dan skema validasi ini **mampu belajar pola nyata ketika data cukup**: parameter Sistolik dan Diastolik mencapai R² 0,52 dan 0,56, sementara Gula Darah, Kolesterol, dan Asam Urat tetap lemah karena nilainya di dunia nyata dipengaruhi variabel yang belum menjadi fitur model (misalnya kondisi pengambilan puasa/sewaktu, dan riwayat penyakit yang tidak tercermin langsung pada sinyal optik pergelangan tangan). Penambahan jumlah subjek kalibrasi dan fitur kondisi pengambilan menjadi prioritas pada tahapan berikutnya (lihat BAB 6).

#### 4.4.3 Hasil Pengujian Prototipe pada Relawan

Pengujian relawan dimulai pada 3 Agustus 2026 untuk memvalidasi SOP, konektivitas, kenyamanan, kualitas sinyal, dan alur penyimpanan data. Empat sesi sampai 14 Agustus telah menghasilkan data dari enam relawan, ditambah tiga relawan lagi pada sesi 2 September 2026 sehingga total sembilan subjek terekam hingga laporan ini disusun.

**Tabel 4.5 Rekapitulasi Riwayat Kesehatan Relawan (N=9)**

| Riwayat Relawan | N | Keterangan |
|---|---|---|
| Riwayat stroke pribadi/keluarga | **[PERLU DICEK]** | Klasifikasi ini butuh konfirmasi tim dari data profil masing-masing relawan — jangan ditebak dari nilai vital saja |
| Tidak ada riwayat stroke | **[PERLU DICEK]** | idem |

> Catatan: tabel di draf lama menulis "Tidak Stroke N=12" padahal total relawan cuma 6 (lalu 9 setelah sesi 2 September) — angka itu tidak konsisten dan saya hapus daripada diteruskan salah. Isi ulang dari catatan riwayat kesehatan relawan yang sebenarnya, bukan dari sensor.

**Tabel 4.6 Data Alat Medis vs Prediksi MLP per Relawan (nilai asli dari data kalibrasi, S001-S009)**

| Subjek | Usia | Gender | TD Alat (mmHg) | Gula Alat (mg/dL) | Kolesterol Alat (mg/dL) | Asam Urat Alat (mg/dL) | Prediksi MLP | Tanggal |
|---|---|---|---|---|---|---|---|---|
| S001 | 20 | L | 125/77 | 119 | 212 | 6,3 | *(lihat catatan)* | 3 Agu 2026 |
| S002 | 57 | P | 173/102 | 101 | 200 | 4,6 | *(lihat catatan)* | 6 Agu 2026 |
| S003 | 75 | P | 153/94 | 183 | 232 | 4,5 | *(lihat catatan)* | 6 Agu 2026 |
| S004 | 70 | P | 157/88 | 153 | 269 | 4,8 | *(lihat catatan)* | 10 Agu 2026 |
| S005 | 76 | L | 166/86 | 98 | 244 | 5,3 | *(lihat catatan)* | 10 Agu 2026 |
| S006 | 75 | P | 145/78 | 94 | 269 | 6,3 | *(lihat catatan)* | 14 Agu 2026 |
| S007 | 75 | L | 142/56 | 183 | 268 | 7,2 | *(lihat catatan)* | 2 Sep 2026 |
| S008 | 62 | L | 131/91 | 171 | 261 | 5,0 | *(lihat catatan)* | 2 Sep 2026 |
| S009 | 62 | L | 121/71 | 157 | 206 | 3,7 | *(lihat catatan)* | 2 Sep 2026 |

> Catatan kolom "Prediksi MLP": nilai prediksi sensor per subjek sudah bisa dicetak apa adanya (tanpa direkayasa) lewat dashboard kalibrasi — buka `https://antaraga.web.id/v1/calibrate/{id}/laporan.html` untuk tiap subjek, salin angka "Prediksi Sensor (MLP)" dari tabel "Model MLP - Estimasi Vital dari Sinyal Optik" ke sini. Saya tidak mengisi kolom ini di sini karena angkanya perlu ditarik langsung dari model yang sedang aktif saat laporan difinalisasi, bukan dari ingatan percakapan sebelumnya.

Sistem kecerdasan buatan dikembangkan menggunakan model XGBoost untuk prediksi risiko stroke dan Multi-Layer Perceptron (MLP) untuk kalibrasi sinyal PPG. Metrik hasil evaluasi realisasi model disajikan pada Tabel 4.7.

**Tabel 4.7 Metrik Evaluasi Performa Model AI dan Pembacaan Alat**

| Parameter Evaluasi | Target/Standar | Hasil Realisasi | Status Ketercapaian |
|---|---|---|---|
| Recall (Sensitivitas) XGBoost | > 90% | 97,3% (73/75 kasus terdeteksi) | Sangat Baik |
| Skor ROC-AUC XGBoost | > 0,80 | 0,823 | Memenuhi Standar |
| Ambang Keputusan (Threshold) | Out-of-Fold Margin | 0,042 (Deteksi) / 0,705 (Risiko Tinggi) | Sesuai Standar AHA ABCD² |
| Perfusi Inframerah (PPG) | 0,02-2,00 ‰ | 0,74-1,77 ‰ | Sinyal Normal |
| Latensi Transmisi Sistem | < 3 Detik | < 2 Detik (Wi-Fi ke VPS) | Sangat Cepat |

1. **Pengujian Prototipe pada Relawan:** Pengujian fungsional telah dilakukan kepada 9 relawan (6 relawan sampai 14 Agustus, ditambah 3 relawan pada sesi 2 September) untuk mengukur tingkat kenyamanan dan akurasi pembacaan sinyal PPG saat digunakan pada pergelangan tangan. Hasil pengujian menunjukkan sinyal optik tetap berada pada indeks perfusi normal (0,74-1,77 ‰) tanpa terdistorsi signifikan oleh gerakan ringan pengguna, dengan tingkat kepuasan relawan mencapai 100%. Rekapitulasi hasil pengujian ANTARAGA dapat dilihat pada Lampiran 1.
2. **Metode Pemilihan Ambang Batas (Decision Threshold):** Nilai threshold standar (0,50) diganti melalui evaluasi Out-of-Fold (OOF) dan kurva Precision-Recall akibat imbalans data. Batas 0,042 ditetapkan sebagai titik potong deteksi biner dan 0,705 untuk kategori risiko tinggi.
3. **Rasionalitas Klinis dan Penanganan Imbalans:** Penurunan threshold ke 0,042 beserta penyeimbangan bobot (`scale_pos_weight` = 19,55) berhasil mendongkrak Recall hingga 97,3%. Kebijakan ini selaras dengan standar AHA/ASA (skor ABCD²), di mana alat penapisan awal memprioritaskan minimalisasi false negative agar tidak ada potensi penderita stroke yang terlewat.
4. **Model Kalibrasi MLP & Pemrosesan Sinyal:** Backend menggunakan penyaring lonjakan BPM 4 lapis untuk menekan artefak gerak dari relawan, serta 5 model MLP untuk mengomposisi data PPG menjadi estimasi indikator kesehatan harian.
5. **Validasi Klinis:** Alur kuesioner kualitatif ABCD2 dan skenario rujukan prarumah sakit telah divalidasi melalui konsultasi langsung bersama Dokter Spesialis Saraf pada 7 Agustus 2026.

<!-- GAMBAR 4.6: Pengujian Prototipe terhadap Relawan. Sumber: Drive 3 Agustus 2026 (https://drive.google.com/drive/folders/1Ip028EM2JdmyEAB0pAkubcext93cWIls), 6 Agustus (https://drive.google.com/drive/folders/1XH7KT0_ipywCmSMgaCirbHuqas9Hk1S9), 10 Agustus (https://drive.google.com/drive/folders/1LGwUxSZxJROtwaCzh_AVwce974jbjxLK), 14 Agustus (https://drive.google.com/drive/folders/1ALXkwO0ZEoPyC5bhK8cftIiJmAKYwmN9), 2 September (https://drive.google.com/drive/folders/1eWuvVkrpi9rPY_dh9udZMzdHIeaJJE4N) -->
<!-- GAMBAR 4.7: Konsultasi Dokter Spesialis Saraf. Sumber: Drive 7 Agustus 2026 (https://drive.google.com/drive/folders/1UYXTJKVpZ3HNQOO_8uhBzX8KD5Xf1NDC) -->
<!-- GAMBAR 4.8: Capaian Media Sosial ANTARAGA (screenshot Instagram Insight). Sumber: Drive 6 Juni, 4 Juli, 29 Agustus 2026 (link sama seperti Gambar 4.1) -->

---

## BAB 5. POTENSI HASIL

### 5.1 Potensi Prototipe ANTARAGA Berdampak

ANTARAGA memiliki potensi menjadi sistem pendukung pemantauan faktor risiko stroke pada lansia di lingkungan keluarga melalui integrasi wearable, analisis data, dan aplikasi mobile. Informasi yang dihasilkan dapat membantu keluarga memantau kondisi secara lebih terstruktur dan mendorong evaluasi medis ketika ditemukan kondisi yang membutuhkan perhatian. Sistem tetap diposisikan sebagai pendukung keputusan, bukan alat diagnosis.

### 5.2 Potensi Hak Kekayaan Intelektual

Tim ANTARAGA telah memperoleh Hak Cipta untuk jenis ciptaan Program Komputer berjudul "ANTARAGA: Smartband Berbasis Multi-Wavelength PPG dengan Artificial Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia" sebagai bentuk perlindungan terhadap karya yang dikembangkan. Sertifikat Hak Cipta ANTARAGA tercantum pada Lampiran 5.

### 5.3 Potensi Pengembangan Prototipe ANTARAGA

<!-- GAMBAR 5.1: Tahapan Pengembangan ANTARAGA (timeline 3 fase: <=1 tahun, 1-3 tahun, >3 tahun) -- sudah ada di draf PDF lama, tinggal disalin. -->

Pengembangan ANTARAGA dilakukan secara bertahap, dimulai dari penambahan data kalibrasi, peningkatan performa model AI, penyempurnaan integrasi real-time, serta evaluasi error, latensi, dan daya tahan baterai pada 1 tahun pertama. Pada periode 1 sampai 3 tahun, pengembangan diarahkan pada validasi terhadap populasi lansia yang lebih representatif, peningkatan kenyamanan dan kestabilan perangkat, penguatan keamanan data, evaluasi bersama tenaga kesehatan, serta kajian regulasi. Setelah kesiapan teknis dan regulasi terpenuhi, pengembangan dapat diarahkan pada kajian kelayakan produksi dan komersialisasi ANTARAGA.

---

## BAB 6. RENCANA TAHAPAN BERIKUTNYA

Untuk mencapai target pelaksanaan sebesar 100% dengan sisa anggaran sebesar **Rp652.450** (dari total sisa dana Rp659.985 per 2 September 2026 — lihat Lampiran 4), kegiatan yang akan dilakukan disajikan pada Tabel 6.1. Tabel ini disusun dari entri logbook tanggal 3-19 September 2026 yang sebelumnya dicatat sebagai rencana (belum termasuk hitungan capaian resmi).

**Tabel 6.1 Rencana Tahapan Berikutnya**

| No. | Kegiatan | PIC | Dana | Waktu Pelaksanaan |
|---|---|---|---|---|
| 1 | Finalisasi Laporan Kemajuan PKM 2026 | Adam | - | 3 September 2026 |
| 2 | Pengujian keenam smartband ANTARAGA (1 data pengujian laboratorium dan 1 data pengujian alat terstandar) sekaligus melanjutkan penyusunan laporan kemajuan | Adam | Rp326.225 *[PERLU DICEK: pembagian dana antara kegiatan 2 dan 5, saya bagi rata dari total Rp652.450 untuk strip kolesterol + pemeriksaan lab + transportasi]* | 5 September 2026 |
| 3 | Technical Meeting dan simulasi presentasi PKP2 | Seluruh tim | - | 10-11 September 2026 |
| 4 | Pelaksanaan Penilaian Kemajuan Program PKM (PKP2) | Adam | - | 15 September 2026 |
| 5 | Pengujian ketujuh smartband ANTARAGA bersamaan dengan pengujian laboratorium, sekaligus melatih ulang model AI (XGBoost dan MLP) dengan data kalibrasi terbaru | Adam, Ally | Rp326.225 *[lihat catatan No. 2]* | 16 September 2026 |
| 6 | Finalisasi laporan akhir dan asistensi ke dosen pendamping | Adam | - | 19 September 2026 |
| **Total** | | | **Rp652.450** | |

---

## DAFTAR PUSTAKA

Capirossi, C., Laiso, A., Renieri, L., Capasso, F. dan Limbucci, N. (2023) "Epidemiology, organization, diagnosis and treatment of acute ischemic stroke", *European Journal of Radiology Open*, 11, 100527. https://doi.org/10.1016/j.ejro.2023.100527.

El-Hajj, C. dan Kyriacou, P.A. (2021) "Cuffless blood pressure estimation from PPG signals and its derivatives using deep learning models", *Biomedical Signal Processing and Control*, 70, 102984. https://doi.org/10.1016/j.bspc.2021.102984.

Feigin, V.L., Brainin, M., Norrving, B., Martins, S.O., Pandian, J., Lindsay, P., Grupper, M.F. dan Rautalin, I. (2025) "World Stroke Organization: Global Stroke Fact Sheet 2025", *International Journal of Stroke*, 20(2), 132-144. https://doi.org/10.1177/17474930241308142.

Kim, K.B. dan Baek, H.J. (2023) "Photoplethysmography in wearable devices: a comprehensive review of technological advances, current challenges, and future directions", *Electronics*, 12(13), 2923. https://doi.org/10.3390/electronics12132923.

Luo, J., Yuan, Y. dan Xu, S. (2025) "Improving GBDT performance on imbalanced datasets: An empirical study of class-balanced loss functions", *Neurocomputing*, 634, 129896. https://doi.org/10.1016/j.neucom.2025.129896.

Potisopha, W., Vuckovic, K.M., DeVon, H.A., Park, C.G., Phutthikhamin, N. dan Hershberger, P.E. (2023) "Decision delay is a significant contributor to prehospital delay for stroke symptoms", *Western Journal of Nursing Research*, 45(1), 55-66. https://doi.org/10.1177/01939459221105827.

Spampinato, M.D. dkk. (2022) "ABCD2, ABCD2-I, and OTTAWA scores for stroke risk assessment: a direct retrospective comparison", *Internal and Emergency Medicine*, 17(8), 2391-2401. https://doi.org/10.1007/s11739-022-03074-x.

Writing Committee for the PERSIST Collaborators (2025) "Long-term risk of stroke after transient ischemic attack or minor stroke: a systematic review and meta-analysis", *JAMA*, 333(17), 1508-1519. https://doi.org/10.1001/jama.2025.2033.

---

## LAMPIRAN 1. Bukti Teknis dan Rekap Pengujian Prototipe

### 1.1 Realisasi Prototipe dan Ekosistem ANTARAGA

**Tabel L.1 Realisasi Prototipe dan Ekosistem ANTARAGA**

| No | Keterangan | Sumber Gambar (Drive) |
|---|---|---|
| L.1 | Foto prototipe tampak depan | *(sudah ada di draf lama, salin ulang)* |
| L.2 | Foto prototipe tampak samping | *(sudah ada di draf lama, salin ulang)* |
| L.3 | Foto prototipe tampak belakang | *(sudah ada di draf lama, salin ulang)* |
| L.4 | Foto prototipe ketika dipakai | *(sudah ada di draf lama, salin ulang)* |
| L.5 | Foto PCB terintegrasi komponen elektronik | *(sudah ada di draf lama, salin ulang)* |
| L.6 | Foto hasil cetak casing PETG | *(sudah ada di draf lama, salin ulang)* |
| L.7 | Tampilan aplikasi mobile (halaman login, dashboard, statistik harian, ABCD2) | <!-- GAMBAR: screenshot aplikasi terbaru, ambil langsung dari HP/emulator saat finalisasi laporan --> |
| L.8 | Diagram arsitektur aktual smartband-server-aplikasi | <!-- GAMBAR: buat baru -- Smartband (SON1303+MAX30102) -> Wi-Fi -> FastAPI VPS -> SQLite/Model AI -> Aplikasi Mobile Flutter --> |

### 1.2 Perubahan dan Penyempurnaan Desain

**Tabel L.2 Perubahan dan Penyempurnaan Desain (Proposal vs Realisasi)**

| Aspek Proposal | Realisasi | Alasan/Implikasi |
|---|---|---|
| XIAO ESP32-C3 | XIAO ESP32-S3 | Keterbatasan SRAM dan beban komunikasi/pemrosesan |
| Pemrosesan sinyal pada perangkat | Pemrosesan utama pada server | Mengurangi beban perangkat dan memudahkan pembaruan algoritma |
| Model Gradient Boosting/MLP tunggal | XGBoost untuk risiko; MLP untuk kalibrasi | XGBoost dipilih dari perbandingan langsung dengan HistGradientBoosting (Tabel 4.3, BAB 4.4.1): Average Precision lebih tinggi (0,2313 vs 0,2281) dan mendukung `scale_pos_weight` bawaan untuk menangani class imbalance (kelas stroke ~4,87%) tanpa perlu resampling data medis yang jumlahnya terbatas. MLP dipisah khusus untuk kalibrasi karena tersedianya data pasangan sinyal PPG-alat invasif dari pengujian relawan. |
| Baterai 900 mAh | Li-Po 1S 950 mAh pada prototipe uji | Penyesuaian kapasitas sumber daya |
| Rancangan aplikasi keluarga | Flutter + dashboard distribusi APK | Integrasi backend dan sinkronisasi data |

### 1.3 Pengujian Teknis Subsistem

**Tabel L.3 Pengujian Teknis Prototipe**

| No | Pengujian | Keterangan | Sumber Gambar/Dokumentasi (Drive) |
|---|---|---|---|
| 1 | Manajemen sistem daya | Analisis output tegangan buck converter dan boost converter; regulator LDO RT9013-33GB terbukti menjaga stabilitas pada rentang 3,0-4,2V | *(sudah ada di draf lama: hasil ukur multimeter 160,3 + osiloskop + datasheet RT9013)* |
| 2 | Charge-discharge baterai | Uji discharge baterai LiPo 1S beban 500 mA -> kapasitas efektif 813 mAh, durasi 97 menit 35 detik | *(sudah ada di draf lama)* |
| 3 | Pengujian SON1303 | Interferensi noise 50 Hz teridentifikasi pada sinyal mentah, diperbaiki dengan penambahan ferrite bead | *(sudah ada di draf lama: grafik adc_raw + foto tim menganalisis di layar)* |
| 4 | Pengujian MAX30102 | Ditemukan unit cacat pabrik (LED IR tidak menyala) pada satu sensor, diganti dengan unit backup; sinyal channel RED & IR normal setelah optimalisasi | *(sudah ada di draf lama)* |
| 5 | Desain layout & inspeksi PCB | PCB difabrikasi dan diinspeksi jalurnya di bawah mikroskop digital sebelum perakitan komponen | *(sudah ada di draf lama)* |
| 6 | Pengujian casing | Revisi dimensi casing PETG karena percobaan cetak pertama tidak bisa menutup rapat | *(sudah ada di draf lama: foto casing tidak menutup rapat)* |
| 7 | SQI (Signal Quality Index) | Firmware menilai kualitas sinyal PPG sebelum data dikirim ke server, memfilter batch dengan kontak sensor buruk sebelum diproses lebih lanjut | <!-- GAMBAR: screenshot log firmware/dashboard yang menampilkan nilai SQI. Sumber: Drive 2 Agustus 2026 (https://drive.google.com/drive/folders/1wQFfujfRy92qY0tw745Bu_1Rl8RG64Am) --> |
| 8 | Konektivitas (Wi-Fi/API) | Pengujian transmisi data dari smartband ke server VPS melalui Wi-Fi dan API FastAPI, termasuk pengujian ulang koneksi setelah pemindahan algoritma sinyal ke server | <!-- GAMBAR: screenshot log koneksi/uji API. Sumber: Drive 2 Agustus 2026 (link sama seperti baris SQI) --> |
| 9 | Dashboard pemantauan | Dashboard web menampilkan bentuk gelombang PPG tiga kanal dan BPM secara real-time | <!-- GAMBAR: screenshot dashboard pemantauan sinyal. Sumber: Drive 2 Agustus 2026 (link sama seperti baris SQI) --> |
| 10 | Penyimpanan data | Data kalibrasi dan hasil pengujian tersimpan di database server (SQLite via SQLAlchemy) dan dapat diekspor sebagai CSV untuk keperluan pelatihan ulang model | <!-- GAMBAR: screenshot tabel/export data di dashboard --> |
| 11 | Latensi transmisi | Diukur < 2 detik dari Wi-Fi smartband ke VPS, memenuhi target < 3 detik | <!-- GAMBAR: dokumentasi pengukuran latensi. Sumber: Drive 2 Agustus 2026 --> |
| 12 | Pembacaan Heart Rate (BPM) | BPM dihitung server via autokorelasi FFT pada sinyal inframerah setelah penyaring lonjakan 4 lapis; dikoreksi manual pada 2 dari 6 kasus awal yang mengalami kesalahan oktaf (lihat Tabel L.3b) | <!-- GAMBAR: grafik perbandingan BPM tersimpan vs hitung ulang --> |

**Tabel L.3b Verifikasi Perhitungan Ulang BPM (Koreksi Oktaf) -- Seluruh 11 Subjek**

| Subjek | BPM Tersimpan (Awal) | BPM Hitung Ulang | Rasio | Tindakan |
|---|---|---|---|---|
| S001 | 70,1 | 70,3 | 1,003 | Tidak diubah |
| S002 | 93,6 | 91,4 | 0,977 | Tidak diubah |
| S003 | 42,9 | 84,0 | 1,959 | Diperbaiki -> 84,0 (kesalahan oktaf) |
| S004 | 103,1 | 104,4 | 1,012 | Tidak diubah |
| S005 | 63,9 | 65,2 | 1,020 | Tidak diubah |
| S006 | 40,9 | 82,6 | 2,020 | Diperbaiki -> 82,6 (kesalahan oktaf) |
| S007 | 81,6 | 43,0 | 0,527 | **Tidak diubah** -- hasil hitung ulang gagal lolos verifikasi (confidence metode autokorelasi 0,177, di bawah ambang 0,30 sistem sendiri); nilai lama tetap dipakai |
| S008 | 88,4 | -- | -- | Tidak bisa diverifikasi -- sinyal tersimpan cuma ~2 detik (di bawah minimum 4 detik yang dibutuhkan algoritme manapun) |
| S009 | 51,2 | 60,9 | 1,189 | Belum diputuskan -- bukan pola oktaf yang bersih (rasio jauh dari 2,0/0,5), butuh alat pembanding untuk memastikan |
| S010 | 81,0 | 82,1 | 1,014 | Tidak diubah |
| S011 | 42,7 | 45,0 (endpoint recompute) / **83,7** (puncak spektrum murni tanpa gerbang oktaf) | 1,054 (menyesatkan) | **Diperbaiki -> 83,7** -- dikonfirmasi lewat alat pembanding (oximeter/tensimeter, ~83 bpm) yang dicatat operator saat sesi; endpoint recompute otomatis TIDAK menandai ini karena nilai lama dan hasil hitung ulangnya kebetulan sama-sama salah dengan cara yang mirip (lihat pembahasan) |

Dua pembacaan (S003, S006) yang mendekati setengah nilai kanal lain diperbaiki melalui koreksi oktaf otomatis. S007 dan S011 ternyata **tidak bisa diandalkan lewat perbandingan rasio otomatis saja**: S007 karena sinyal aslinya sendiri terlalu bising untuk metode apa pun (confidence rendah di dua algoritme independen), dan S011 karena nilai lama dan hasil hitung ulang endpoint kebetulan sama-sama terjebak di frekuensi setengahnya, sehingga rasionya terlihat "wajar" (1,054) padahal keduanya meleset -- baru ketahuan setelah dicek silang terhadap puncak spektrum murni dan alat pembanding sungguhan. Mekanisme server juga dilengkapi gerbang periodisitas, batas perubahan fisiologis, dan median bergulir untuk menekan lonjakan sesaat.

### 1.4 Pengujian Terintegrasi pada Relawan

Enam kegiatan pengujian tercatat pada logbook sampai 5 September 2026. Sebelas kode subjek (S001-S011) [PERLU DICEK: sesuaikan setelah logbook diperbarui sore ini] telah dipakai pada sesi kalibrasi. Identitas subjek disamarkan untuk menjaga kerahasiaan. Bagian ini menyajikan tiga hal per relawan: data profil, perbandingan alat medis vs prediksi MLP, dan hasil deteksi risiko stroke — persis seperti yang sudah ditampilkan di laporan cetak per-subjek (`https://antaraga.web.id/v1/calibrate/{id}/laporan.html`), cuma direkap jadi satu tabel untuk semua relawan sekaligus.

**Tabel L.4a Data Profil Relawan** (field jadi baris, subjek jadi kolom, dikelompokkan maksimal 4 subjek per tabel supaya tetap 5 kolom dan enak dicetak A4)

**Tabel L.4a.1 -- Subjek S001 s.d. S004**

| Field | S001 | S002 | S003 | S004 |
|---|---|---|---|---|
| Usia | 20 | 57 | 75 | 70 |
| Gender | L | P | P | P |
| Kondisi Pengambilan | Sewaktu | Sewaktu | Sewaktu | Sewaktu |
| Merokok | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Penyakit Jantung | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Status Bekerja | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Tipe Tempat Tinggal | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Diabetes | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Stroke Keluarga | Belum tercatat | Belum tercatat | Belum tercatat | Belum tercatat |
| Riwayat Stroke Pribadi | Belum tercatat | Belum tercatat | Belum tercatat | Belum tercatat |
| Tanggal Pengujian | 3 Agustus 2026 | 6 Agustus 2026 | 6 Agustus 2026 | 10 Agustus 2026 |

**Tabel L.4a.2 -- Subjek S005 s.d. S008**

| Field | S005 | S006 | S007 | S008 |
|---|---|---|---|---|
| Usia | 76 | 75 | 75 | 62 |
| Gender | L | P | L | L |
| Kondisi Pengambilan | Sewaktu | Sewaktu | Sewaktu | Sewaktu |
| Merokok | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Penyakit Jantung | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Status Bekerja | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Tipe Tempat Tinggal | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Diabetes | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Stroke Keluarga | Belum tercatat | Belum tercatat | Belum tercatat | Belum tercatat |
| Riwayat Stroke Pribadi | Belum tercatat | Belum tercatat | Belum tercatat | Belum tercatat |
| Tanggal Pengujian | 10 Agustus 2026 | 14 Agustus 2026 | 2 September 2026 | 2 September 2026 |

**Tabel L.4a.3 -- Subjek S009 s.d. S011**

| Field | S009 | S010 | S011 |
|---|---|---|---|
| Usia | 62 | — [PERLU DIISI, sore ini] | — [PERLU DIISI, sore ini] |
| Gender | L | — [PERLU DIISI, sore ini] | — [PERLU DIISI, sore ini] |
| Kondisi Pengambilan | Sewaktu | — [PERLU DIISI, sore ini] | — [PERLU DIISI, sore ini] |
| Merokok | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Penyakit Jantung | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Status Bekerja | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Tipe Tempat Tinggal | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Diabetes | [PERLU DIISI] | [PERLU DIISI] | [PERLU DIISI] |
| Riwayat Stroke Keluarga | Belum tercatat | Belum tercatat | Belum tercatat |
| Riwayat Stroke Pribadi | Belum tercatat | Belum tercatat | Belum tercatat |
| Tanggal Pengujian | 2 September 2026 | [PERLU DIISI, sore ini] | [PERLU DIISI, sore ini] |

> **Penting, ini bukan cuma sel kosong biasa:** kolom Merokok, Riwayat Penyakit Jantung, Status Bekerja, Tipe Tempat Tinggal, dan Riwayat Diabetes **memang tidak pernah ditanyakan/dicatat di sistem kalibrasi** (`CalibrationRecord` tidak punya kolom untuk field-field ini sama sekali — beda dari Profil di aplikasi mobile produksi yang memang punya field itu). Kalau tim punya catatan ini dari formulir informed consent/wawancara relawan, isi manual dari situ. Kolom Riwayat Stroke Keluarga/Pribadi *sudah ada* kolomnya di database, cuma belum pernah diisi untuk kesembilan relawan ini — isi lewat tombol edit di dashboard kalibrasi (✎), bukan ditebak.

**Tabel L.4b Data Alat Medis vs Prediksi MLP per Relawan**

*(Sama dengan Tabel 4.6 di BAB 4.4.3 — dirujuk ke sana supaya tidak duplikat. Kolom "Prediksi MLP" di sana yang perlu ditarik dari laporan cetak per-subjek, sesuai catatan di bawah tabel itu.)*

**Tabel L.4c Hasil Deteksi Risiko Stroke per Relawan**

Kategori di bawah dihitung dari aturan klinis manual yang sama dengan yang dipakai laporan cetak per-subjek (lihat catatan `_kategori_klinis_manual()` di Lampiran 1.5) — bukan probabilitas mentah XGBoost. Dijalankan langsung dari data asli S001-S009 pada `kalibrasi_semua.csv`.

| Subjek | Faktor Risiko Terpenuhi | Kategori Risiko | Alasan |
|---|---|---|---|
| S001 | Kolesterol Total Tinggi | Rendah | 1 faktor risiko terpenuhi |
| S002 | Hipertensi, Kolesterol Total Tinggi | Rendah | 2 faktor risiko terpenuhi |
| S003 | Hipertensi, Kolesterol Total Tinggi | Sedang | 2 faktor risiko terpenuhi; usia 75 tahun (≥ 75 tahun) |
| S004 | Hipertensi, Kolesterol Total Tinggi, Aritmia | Sedang | 3 faktor risiko terpenuhi; usia 70 tahun (≥ 60 tahun) |
| S005 | Hipertensi, Kolesterol Total Tinggi | Sedang | 2 faktor risiko terpenuhi; usia 76 tahun (≥ 75 tahun) |
| S006 | Hipertensi, Kolesterol Total Tinggi | Sedang | 2 faktor risiko terpenuhi; usia 75 tahun (≥ 75 tahun) |
| S007 | Hipertensi, Kolesterol Total Tinggi, Hiperurisemia | Sedang | 3 faktor risiko terpenuhi; usia 75 tahun (≥ 75 tahun) |
| S008 | Hipertensi, Kolesterol Total Tinggi | Rendah | 2 faktor risiko terpenuhi; usia 62 tahun (≥ 60 tahun) |
| S009 | Kolesterol Total Tinggi, Aritmia | Rendah | 2 faktor risiko terpenuhi; usia 62 tahun (≥ 60 tahun) |
| S010, S011 | — | — | [PERLU DIISI setelah data masuk sore ini] |

> **Catatan penting:** kategori di atas dihitung dengan asumsi Riwayat Stroke Keluarga/Pribadi = "Tidak/kosong" untuk semua, karena memang belum ada satu pun yang tercatat (lihat Tabel L.4a). Kalau nanti field itu diisi dan ternyata ada relawan dengan riwayat stroke pribadi, kategorinya **otomatis naik jadi "Tinggi"** untuk relawan itu (aturan sistem: riwayat pribadi memicu langsung Tinggi) — tabel ini wajib dihitung ulang setelah Tabel L.4a lengkap, bukan dipakai sebagai final.

### 1.5 Evaluasi Model AI dan Pemrosesan Sinyal

Dipisah jadi tiga tabel per topik, tiap tabel diurutkan sesuai tanggal kejadian di logbook (bukan cuma dikelompokkan per topik) supaya dokumentasi yang ditempel di kolom kanan mengikuti alur pengerjaan sungguhan.

**Tabel L.5a Pemrosesan Sinyal (Sensor -> Server)**

| No | Kegiatan | Tanggal | Dokumentasi |
|---|---|---|---|
| 1 | Pengembangan firmware akuisisi sinyal sensor SON1303 (kanal hijau) | 7 Juli 2026 | <!-- GAMBAR: cuplikan kode/log firmware akuisisi --> |
| 2 | Pengujian sensor MAX30102 -- ditemukan alamat I2C tidak terbaca (cacat pabrik) | 10 Juli 2026 | *(sudah ada di draf lama: foto sensor + serial monitor)* |
| 3 | Pembelian dan pengujian sensor MAX30102 pengganti | 11 Juli 2026 | <!-- GAMBAR: foto sensor pengganti + hasil uji --> |
| 4 | Perbaikan interferensi noise 50 Hz pada SON1303 (penambahan ferrite bead) | *[PERLU DICEK: tanggal spesifik di logbook]* | *(sudah ada di draf lama: grafik adc_raw sebelum/sesudah)* |
| 5 | Pemindahan algoritma pemrosesan sinyal (bandpass Butterworth 0,5-5 Hz, autokorelasi FFT untuk BPM) dari firmware ke server; dirilisnya dashboard web pemantauan sinyal tiga kanal secara real-time | 2 Agustus 2026 | <!-- GAMBAR: screenshot dashboard pemantauan sinyal. Drive: https://drive.google.com/drive/folders/1wQFfujfRy92qY0tw745Bu_1Rl8RG64Am --> |
| 6 | Pengujian BPM dan analisis error terhadap oximeter/tensimeter sebagai alat pembanding | 2 Agustus 2026 | *(link Drive sama seperti baris 5)* |
| 7 | Verifikasi ulang BPM dari sinyal mentah tersimpan (koreksi kesalahan oktaf) | berkelanjutan, terbaru 7-8 September 2026 | Lihat Tabel L.3b |

**Tabel L.5b Model XGBoost (Prediksi Risiko Stroke)**

| No | Kegiatan | Tanggal | Dokumentasi |
|---|---|---|---|
| 1 | Studi dataset dan model baseline XGBoost | 7 Juli 2026 | <!-- GAMBAR: cuplikan notebook studi awal --> |
| 2 | Studi penanganan class imbalance; rasio pembobotan awal dihitung 1:19,52 dari keseluruhan dataset | 10 Juli 2026 | <!-- GAMBAR: cuplikan perhitungan rasio kelas --> |
| 3 | Pengujian model tanpa pembobotan -- membuktikan kelemahan akibat class imbalance (recall sangat rendah) | 11 Juli 2026 | <!-- GAMBAR: metrik model tanpa pembobotan --> |
| 4 | Penyetelan hiperparameter dan komparasi XGBoost vs HistGradientBoosting | 13-14 Juli 2026 | <!-- GAMBAR: cuplikan RandomizedSearchCV --> |
| 5 | Validasi akhir: XGBoost ditetapkan final (AP 0,2313 vs 0,2281 HistGradientBoosting), `scale_pos_weight`=19,55 | 16 Juli 2026 | <!-- GAMBAR: Gambar 4.4 (bar chart perbandingan) --> |
| 6 | Evaluasi performa recall model final pada data uji | 18 Juli 2026 | <!-- GAMBAR: hasil evaluasi recall --> |
| 7 | Optimasi threshold klasifikasi -- ditetapkan 0,042 (deteksi) dan 0,705 (risiko tinggi) | 21 Juli 2026 | <!-- GAMBAR: kurva Precision-Recall --> |
| 8 | Confusion matrix, ROC-AUC, dan parameter tuning final model produksi | -- (rangkuman `model/artifacts/metrics.json`) | Data uji (n=1.533): TN=553, FP=905, FN=2, TP=73; ROC-AUC=0,823; `n_estimators`=100, `max_depth`=4, `learning_rate`=0,03, `min_child_weight`=5, `subsample`=1,0, `colsample_bytree`=1,0, `reg_lambda`=1,0 <!-- GAMBAR: visualisasikan confusion matrix sebagai heatmap --> |
| 9 | Kategori risiko per-relawan yang ditampilkan di laporan kalibrasi (Tabel L.4c) | -- | Bukan probabilitas mentah dari model produksi di atas -- laporan kalibrasi per-subjek memakai aturan klinis manual (jumlah faktor risiko + usia; riwayat stroke pribadi otomatis "Tinggi") supaya kategorinya bisa dijelaskan alasannya tanpa membocorkan angka probabilitas. Lihat `_kategori_klinis_manual()` di `api/calib_report.py`. |

**Tabel L.5c Model MLP (Estimasi Vital dari Sinyal PPG)**

| No | Kegiatan | Tanggal | Dokumentasi |
|---|---|---|---|
| 1 | Pengembangan antarmuka kalibrasi dashboard, untuk merekam pasangan sinyal PPG dan nilai alat invasif | 5 Agustus 2026 | <!-- GAMBAR: screenshot antarmuka kalibrasi --> |
| 2 | Rancangan pipeline lima model MLP (satu `MLPRegressor` per parameter: gula darah, kolesterol, asam urat, sistolik, diastolik), fitur input: ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p, bpm, usia, kode gender | pertengahan Agustus 2026 | <!-- GAMBAR: diagram pipeline / cuplikan notebook rancangan --> |
| 3 | Pelatihan awal model dari data kalibrasi yang terkumpul | 16 Agustus 2026 | <!-- GAMBAR: screenshot dashboard pelatihan --> |
| 4 | Evaluasi kuantitatif (Leave-One-Subject-Out: MAE, RMSE, R²), diperbarui tiap penambahan data kalibrasi baru | berkelanjutan, terbaru 2-7 September 2026 (9-11 subjek) | Lihat Tabel 4.4 (BAB 4.4.2) -- unduh laporan HTML lengkap lewat dashboard untuk grafik scatter prediksi vs aktual |

### 1.6 Bukti Luaran Digital ANTARAGA

**Tabel L.6a Aplikasi Mobile**

| No | Kegiatan | Tanggal | Dokumentasi |
|---|---|---|---|
| 1 | Inisialisasi aplikasi mobile Flutter | 21 Juni 2026 | <!-- GAMBAR: screenshot commit/scaffold awal --> |
| 2 | Penyelesaian antarmuka aplikasi mobile (login, registrasi, profil, dashboard) | 2 Juli 2026 | <!-- GAMBAR: screenshot halaman login/registrasi/dashboard --> |
| 3 | Integrasi aplikasi mobile dengan backend dan pengembangan fitur distribusi APK | 23 Agustus 2026 | <!-- GAMBAR: screenshot statistik harian & asesmen ABCD2 --> |
| 4 | Persiapan akun Google Play Console dan pembayaran biaya pendaftaran | 29 Agustus 2026 | <!-- GAMBAR: screenshot Google Play Console (sensor/crop email & info sensitif sebelum ditempel) -- nama aplikasi ANTARAGA, status pendaftaran/rilis, tanggal publikasi jika sudah tercantum. Drive: https://drive.google.com/drive/folders/107l7Drt_-EqX-IKg4z_x3ub-AA2ruDBM --> |

**Tabel L.6b Video Simulasi dan Media Sosial**

| No | Kegiatan | Tanggal | Dokumentasi |
|---|---|---|---|
| 1 | Video simulasi dan pengujian ANTARAGA | -- | <https://drive.google.com/file/d/13KHnk6g6ESceC37GzXaLVtgXvqBJEyDb/view?usp=drive_link> |
| 2 | Publikasi media sosial (4 unggahan) | 1 Juni, 6 Juni, 4 Juli, 29 Agustus 2026 | <!-- GAMBAR: screenshot semua konten -- link Drive per tanggal ada di Lampiran 3 -->

### 1.7 Validasi Medis dan Kepatuhan Etik

**Ethical Clearance**

Diproses melalui KEPK FKM Universitas Airlangga, No. 235/EA/KEPK/2026, terbit 23 Juli 2026, berlaku 23 Juli 2026 - 23 Juli 2027. Judul protokol: "ANTARAGA: Smartband Berbasis Multi-Wavelength PPG dengan Artificial Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia". Peneliti utama: Kadek Savita Dyutianaya. Sertifikat pada Lampiran 5.

**Informed Consent**

Digunakan pada setiap sesi pengambilan data untuk memastikan persetujuan dan pemahaman relawan terhadap prosedur pengujian. *[PERLU DICEK: lampirkan salinan kosong/teranonimisasi formulir informed consent yang dipakai]*

**Konsultasi Dokter Spesialis Saraf**

Dilaksanakan 7 Agustus 2026 untuk memvalidasi alur kuesioner ABCD2 dan skenario rujukan prarumah sakit (Drive: https://drive.google.com/drive/folders/1UYXTJKVpZ3HNQOO_8uhBzX8KD5Xf1NDC).

*[PERLU DICEK: tambahkan ringkasan 2-3 kalimat hasil konsultasi/masukan dokter, kalau ada catatan tertulisnya]*

---

## LAMPIRAN 2. Rincian Logbook Kegiatan

Lampiran ini merangkum seluruh entri kegiatan yang telah dicatat sampai 2 September 2026 sebagai capaian resmi. Entri setelah tanggal tersebut (3-19 September 2026) diperlakukan sebagai rencana dan disajikan pada BAB 6, bukan tabel capaian ini. Logbook lengkap (311 entri, kolom kegiatan/tanggal/waktu/lokasi/PIC/dana/dokumentasi) tersimpan di `DRAFT LOGBOOK ANTARAGA 2026 - FIX LOGBOOK.csv` dan Google Sheet tim (kolom "LINK LOGBOOK").

**Tabel L.6 Rekapitulasi Indikator Kinerja Jangka Pendek (IKJP) per Minggu**

| Minggu | Rentang Tanggal | Persentase Capaian | Ringkasan IKJP |
|---|---|---|---|
| 1 | 23 Mei 2026 | 1% | Akun media sosial Instagram & TikTok terbentuk dan publik; garis besar rencana 4 bulan tersusun; konsep awal pengenalan program & tim. |
| 2 | 30 Mei 2026 | 1% | Pembagian jobdesk tim dan jadwal kegiatan tersusun sesuai master timeline PKM dan arahan dosen pembimbing. |
| 3 | 6 Juni 2026 | 1% | Konten pengenalan ANTARAGA (logo, judul, story behind, tim, program) terpublikasi + iklan berbayar Rp166.500. |
| 4 | 13 Juni 2026 | 2% | Strategi infrastruktur server & domain ditetapkan; komponen MAX30102 dan baterai lipo dibeli dan dicatat pada laporan keuangan. |
| 5 | 20 Juni 2026 | 2% | Konten video edukasi (demonstrasi cek gula darah & tekanan darah pada lansia) diproduksi dengan persetujuan subjek. |
| 6 | 27 Juni 2026 | 3% | Antarmuka aplikasi mobile (login, registrasi, profil, dashboard) berkembang; referensi LDO 3,3V diperoleh. |
| 7 | 4 Juli 2026 | 2% | Konten mingguan + konten #2 terpublikasi dan diiklankan di Instagram. |
| 8 | 11 Juli 2026 | 2% | Kelemahan model tanpa pembobotan terbukti lewat PR-AUC/ROC-AUC/recall/precision; kerusakan backup sensor MAX30102 teridentifikasi. |
| 9 | 17 Juli 2026 | 1% | Revisi skematik/PCB & migrasi ke XIAO ESP32-S3 disetujui; threshold awal 0,705 (F1 0,2946) diperoleh; draf BAB 1-2 laporan dimulai. |
| 10 | 25 Juli 2026 | 1% | Integrasi modul hardware ke casing 3D selesai (50 g dengan strap); kendala drop tegangan TP5000 teratasi; artefak model final tersusun. |
| 11 | 2 Agustus 2026 | 1% | Algoritma sinyal (bandpass, autokorelasi FFT BPM) dipindah ke server; dashboard web pemantauan tersedia; pengujian BPM vs oximeter/tensimeter dilakukan. |
| 12 | 9 Agustus 2026 | 1% | Berkas awal pendaftaran HKI disusun; struktur kode & rentang baris fitur didokumentasikan; template buku manual selesai. |
| 13-14* | 10-27 Agustus 2026 | *[PERLU DICEK]* | Pengujian relawan ketiga & keempat (10, 14 Agustus); finalisasi & penyerahan berkas HKI ke Sentra HKI PENS (13-14 Agustus); rekap 4 sesi/6 relawan (16 Agustus); workshop laporan kemajuan & akhir (20 Agustus); integrasi aplikasi mobile & fitur distribusi APK (23 Agustus); workshop teknik presentasi PKP2 (26 Agustus). |
| 15 | 29 Agustus 2026 | 2% | Konten media sosial ketiga difinalisasi, diunggah, dan diiklankan; akun Google Play Console disiapkan. |

*Catatan: baris "13-14" digabung karena entri logbook pada rentang tanggal tersebut tidak diberi nomor MINGGU KE- yang konsisten pada berkas sumber — perlu dicek ulang ke logbook asli kalau ingin dipisah per minggu kalender.*

---

## LAMPIRAN 3. Rincian Publikasi Media Sosial

**Tabel L.7 Rincian Publikasi Media Sosial**

| Tanggal | Konten | Status | Keterangan |
|---|---|---|---|
| 1 Juni 2026 | Coming soon | Terpublikasi | Unggahan dan promosi awal |
| 6 Juni 2026 | Pengenalan program dan tim | Terpublikasi + iklan | Biaya iklan Rp166.500/3 hari |
| 4 Juli 2026 | Konten program #2 + weekly content | Terpublikasi + iklan | Publikasi program |
| 29 Agustus 2026 | Konten program #3/perkembangan produk | Terpublikasi + iklan | Peragaan sistem aktual |

---

## LAMPIRAN 4. Rincian Anggaran dan Penggunaan Dana

Anggaran proposal ANTARAGA berjumlah Rp10.000.000, terdiri atas Rp8.000.000 dari Belmawa dan Rp2.000.000 dari perguruan tinggi. Penggunaan dana dilaksanakan sesuai kebutuhan aktual kegiatan dan ketentuan PKM.

**Tabel L.8 Rencana Penggunaan Dana (Proposal)**

| Jenis Pengeluaran | Belmawa (Rp) | Perguruan Tinggi (Rp) | Total Rencana (Rp) |
|---|---|---|---|
| Bahan habis pakai | 4.800.000 | - | 4.800.000 |
| Sewa dan jasa | 1.200.000 | 650.000 | 1.850.000 |
| Transportasi lokal | 1.300.000 | - | 1.300.000 |
| Lain-lain | 700.000 | 1.350.000 | 2.050.000 |
| **Jumlah** | **8.000.000** | **2.000.000** | **10.000.000** |

**Tabel L.9 Rekapitulasi Realisasi Penggunaan Dana (per 2 September 2026)**

| Keterangan | Nominal (Rp) | Terhadap Dana Disetujui |
|---|---|---|
| Dana disetujui | 7.500.000 | 100,00% |
| Realisasi sampai 2 September | 6.840.015 | 91,20% |
| Sisa dana | 659.985 | 8,80% |
| Rencana setelah 2 September | 652.450 | 8,70% |
| Saldo setelah rencana | 7.535 | 0,10% |

Realisasi dana terdiri atas bahan habis pakai Rp4.624.760, sewa dan jasa Rp915.244, transportasi lokal Rp707.086, dan lain-lain Rp592.925. Rencana penggunaan sisa dana Rp652.450 diarahkan untuk strip kolesterol, pemeriksaan laboratorium relawan, dan transportasi pengujian (lihat rincian kegiatan pada BAB 6).

> **[PERLU DICEK]** Terdapat selisih antara "Dana disetujui" pada tabel realisasi (Rp7.500.000) dengan total anggaran proposal (Rp10.000.000). Ini kemungkinan karena baru sebagian termin dana yang cair — mohon dikonfirmasi dan diberi satu kalimat penjelas di laporan final supaya tidak terlihat seperti salah ketik.

Bukti pengeluaran terlampir sebagai dokumen terpisah (nota, kuitansi, dan bukti transfer) sesuai format pelaporan keuangan Belmawa.

---

## LAMPIRAN 5. Ethical Clearance dan Bukti Hak Cipta

### 5.1 Ethical Clearance

Ethical clearance diproses melalui KEPK FKM Universitas Airlangga sebagai dasar pelaksanaan pengujian relawan. Dokumen terbit pada 23 Juli 2026 dengan Nomor 235/EA/KEPK/2026, berlaku sampai dengan 23 Juli 2027. Informed consent digunakan pada setiap sesi pengambilan data untuk memastikan persetujuan dan pemahaman relawan terhadap prosedur pengujian.

<!-- GAMBAR: Surat Keterangan Layak Etik KEPK FKM Unair -- sudah ada di draf PDF lama (halaman sertifikat), tinggal disalin. -->

### 5.2 Sertifikat Hak Kekayaan Intelektual

Penyusunan berkas dimulai pada 9 Agustus 2026, meliputi dokumentasi struktur kode, buku manual, dan administrasi. Setelah berkas diserahkan kepada Sentra HKI PENS pada 14 Agustus 2026, Surat Pencatatan Ciptaan diterbitkan untuk ANTARAGA. Dokumen tersebut mencatat ciptaan berjenis Program Komputer dengan judul "ANTARAGA: Smartband Berbasis Multi-Wavelength PPG dengan Artificial Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia".

Pencipta yang tercantum adalah Agrippina Waya Rahmaning Gusti, Kadek Savita Dyutianaya, Kalyana Daeva Ali, Adam Kandias, Jonzeven La Royba, dan Ni Komang Diah Pratiwi. Pemegang Hak Cipta adalah Politeknik Elektronika Negeri Surabaya. Ciptaan pertama kali diumumkan pada 3 Agustus 2026 di Kota Surabaya.

**Tabel L.10 Rincian Dokumen Etik dan HKI**

| Dokumen | Status | Keterangan |
|---|---|---|
| Ethical clearance | Diproses melalui KEPK FKM Unair | Dasar pelaksanaan pengujian relawan |
| Informed consent | Digunakan | Persetujuan relawan pada pengambilan data |
| Buku manual HKI | Selesai | Dokumen pendukung program komputer |
| Surat Pencatatan Ciptaan | Telah terbit | No. Permohonan EC002026157207; terbit 28 Agustus 2026 |
| Nomor Pencatatan | 001449089 | Jenis ciptaan: Program Komputer |
| Jangka pelindungan | 50 tahun | Sejak pertama diumumkan 3 Agustus 2026 |

<!-- GAMBAR: Surat Pencatatan Ciptaan ANTARAGA -- sudah ada di draf PDF lama (2 halaman sertifikat), tinggal disalin. -->

---

**Catatan penutup untuk Adam:** semua tanda `[PERLU DICEK]` dan `<!-- GAMBAR: ... -->` di atas sengaja tidak saya isi sendiri karena butuh data/keputusan dari tim atau file (foto/screenshot) yang cuma ada di Drive/HP kalian. Setelah semua itu diisi, tinggal dikonversi jadi PDF/Word (bisa pakai Pandoc: `pandoc "Laporan Kemajuan ANTARAGA (Revisi).md" -o "Laporan Kemajuan ANTARAGA.docx"`) lalu dirapikan formatnya sesuai template resmi Belmawa.
