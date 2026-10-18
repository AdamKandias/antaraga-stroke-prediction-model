## 0. CATATAN UNTUK TIM (jangan ikut disalin ke Word)

### 0.1 Ringkasan temuan

Saya membandingkan file ini dengan **dua sumber**: draf Word yang sudah Anda ekspor (`Draf Laporan Akhir ANTARAGA.pdf`, 90 halaman, metadata masih bertuliskan "Laporan Kemajuan" — jadi file itu memang hasil duplikasi laporan kemajuan) dan **Pedoman PKM 2026** resmi (`PKM-KC-2026_fix.pdf`, diunduh dari simbelmawa.kemdiktisaintek.go.id hari ini). Saya juga mengambil **bobot penilaian laporan akhir** langsung dari Lampiran 10 pedoman tersebut, karena itulah yang menjelaskan kenapa Anda diminta fokus ke "poin 3" dan subbab 4.8:

| No. | Kriteria penilaian laporan akhir | Bobot |
|---|---|---|
| 1 | Pendahuluan | 15 |
| 2 | Tinjauan pustaka | 15 |
| **3** | **Tahap Pelaksanaan (Konstruksi dari Inspirasi)** | **25** |
| 4 | **Hasil yang dicapai dan potensi khusus** (memuat subbab 4.8) | **30** |
| 5 | Penutup | 10 |
| 6 | Daftar Pustaka | 5 |

**"Poin 3" yang Anda maksud kemungkinan besar adalah kriteria No. 3 di atas** (Tahap Pelaksanaan, BAB 3), bukan nomor BAB secara umum — bobotnya 25, kedua tertinggi setelah BAB 4 (30) yang memuat subbab 4.8. Gabungan BAB 3 + BAB 4 = 55% dari nilai laporan akhir, jadi wajar itu yang paling perlu diperkuat. Saya fokus ke keduanya, tapi tetap menulis ulang seluruh Bagian Inti (Ringkasan sampai Daftar Pustaka) seperti yang Anda minta.

### 0.2 Temuan struktural (sebelum isi) — ini yang paling penting

1. **File `.md` ini sebelumnya tidak punya RINGKASAN, DAFTAR ISI, DAFTAR GAMBAR, DAFTAR TABEL, DAFTAR LAMPIRAN.** Padahal PDF Anda sudah punya semuanya (halaman i–vii) — jadi bukan hilang dari laporan Anda, hanya belum ikut tersalin ke `.md` ini. Saya tambahkan di bawah, disalin dari PDF.
2. **Ringkasan di PDF Anda menampilkan nomor halaman "i" di bagian bawah**, padahal pedoman eksplisit menulis "RINGKASAN (tanpa nomor halaman)". Di Word, cek apakah itu field nomor halaman asli atau cuma teks "i" yang diketik manual — kalau field asli, hapus nomor halaman khusus di page Ringkasan (section break + "different first page" atau style serupa).
3. **BAB 3 di Daftar Isi Anda menjanjikan subbab "3.1 Alat dan Bahan" dan "3.2 Realisasi Pelaksanaan Program"**, tapi isi BAB 3 yang sebenarnya (baik di PDF maupun di `.md` lama) **tidak punya heading subbab sama sekali** — cuma satu paragraf pembuka lalu daftar 8 tahapan. **3.1 Alat dan Bahan belum pernah ditulis isinya.** Ini saya perbaiki di bawah: saya tambahkan 3.1 (tabel alat dan bahan, disusun dari yang sudah disebut di BAB 1, BAB 4, dan Lampiran 1–3) dan beri heading 3.2 pada paragraf yang sudah ada.
4. **Kutipan silang yang salah** di Lampiran 1.2, Tabel L.2, baris "Model Gradient Boosting → XGBoost": tertulis "(Tabel 4.3, Subbab 4.4.1)" untuk angka Average Precision 0,2313 vs 0,2281. Subbab 4.4.1 **tidak ada** (BAB 4 cuma sampai 4.8, dan grouping HistGradientBoosting itu ada di **4.3.1**, bukan 4.4.1), dan Tabel 4.3 isinya "Median Data Hasil Pengujian Relawan" — tidak ada hubungannya dengan Average Precision. Saya ganti rujukannya ke **Subbab 4.3.1** dan ke **Gambar L.30–L.32** (yang memang berisi perbandingan dengan/tanpa pembobotan), lalu saya tambahkan angka 0,2313 vs 0,2281 itu langsung ke teks 4.3.1 supaya tidak menggantung.
5. **Tabel 4.2 vs Tabel 4.3 memakai definisi akurasi yang berbeda** tapi disandingkan tanpa penjelasan: Tabel 4.2 melaporkan akurasi per-parameter dari evaluasi Leave-One-Out (75,5–90,6%), sedangkan Tabel 4.3 melaporkan kecocokan **median** alat vs prediksi pada 11 relawan (91,3–95,8%) — angka yang jauh lebih tinggi karena median jauh lebih stabil daripada estimasi per-orang. Reviewer bisa bertanya "yang mana akurasi sebenarnya?". Saya tambahkan satu kalimat penghubung di 4.3.3 yang menjelaskan bedanya, supaya terlihat disengaja, bukan tidak konsisten.
6. **Kalimat berulang** di akhir 4.3.3: "Dokumentasi pengujian selengkapnya dapat ditinjau melalui Video Luaran ANTARAGA. Dokumentasi pengujian dapat ditinjau melalui: Video Luaran ANTARAGA." — dua kalimat yang sama persis berturutan, dan "Video Luaran ANTARAGA" tidak jelas apakah itu tautan aktif atau cuma teks. Saya satukan jadi satu kalimat; **mohon pastikan ada hyperlink asli di Word-nya** (teks ekstraksi PDF tidak menunjukkan URL tersemat).
7. **Lampiran 9 (Draf Artikel Ilmiah) sudah ketinggalan satu revisi.** Saya render halaman pertamanya: isinya masih menulis "48 candidates (12 model families × 4 feature subsets)" untuk estimator fisiologis. Draf artikel terbaru di `artikel-jaee.md` (yang kita perbaiki bersama hari ini, menyusul koreksi Tabel 2 Anda) sudah memakai "12 candidates (three model configurations × 4 feature subsets: SVR linear, SVR RBF, XGBoost)" — konsisten dengan Tabel 4.2 di laporan ini. **Ekspor ulang `artikel-jaee.md` ke PDF dan tempel ulang ke Lampiran 9** sebelum submit, supaya tidak ada dua versi berbeda dari model yang sama di satu berkas.
8. **Kutipan dan Daftar Pustaka sudah konsisten dan memenuhi gaya Harvard pedoman** (semua nama penulis dicantumkan lengkap di Daftar Pustaka, tanpa "dkk."/"et al.", terurut alfabetis) — saya cek silang, 9 sitasi di teks (Feigin, Capirossi, Potisopha, Spampinato, Gutierrez-Martinez, Jeon, Fan, Blok, Kim & Baek) semuanya ada padanannya di Daftar Pustaka dan sebaliknya. **Tidak perlu diubah.**
9. **Cek jumlah halaman Bagian Inti.** Pedoman membatasi Bagian Inti (Pendahuluan s.d. Daftar Pustaka) maksimum **10 halaman**, Times New Roman 12, spasi 1,15. Versi PDF Anda saat ini pas 10 halaman (hlm. 1–10 dokumen = halaman cetak 8–17 PDF). **Tambahan saya di 3.1 dan 4.8 akan menambah panjang** — setelah ditempel ke Word, cek ulang apakah masih muat 10 halaman; kalau lebih, kandidat paling aman dipotong adalah rincian "Alasan/Implikasi" di beberapa butir 3.2 yang sudah terwakili di Lampiran 1.2.

### 0.3 Yang TIDAK saya tulis ulang

Lampiran (mulai "LAMPIRAN" di bawah Daftar Pustaka) **saya biarkan seperti aslinya** — isinya dokumentasi, tabel keuangan, dan bukti kegiatan yang sudah benar dan tidak bisa saya perbaiki tanpa melihat sumber aslinya (foto, screenshot, bukti transfer). Saya hanya menandai dua titik yang perlu diperbaiki (poin 4 dan 7 di atas); selebihnya silakan cek sendiri saat menempel ke Word. Saya **tidak** mengubah angka Tabel 4.2 (Gula Darah 75,50%, dst.) — itu angka resmi laporan Anda; diskusi soal data S010 lama/baru sudah kita bahas terpisah untuk `artikel-jaee.md` dan tidak saya ulangi paksakan ke sini.

---

====================================================================================================
# ISI LAPORAN AKHIR — mulai dari sini disalin ke Word (gaya: Times New Roman 12, spasi 1,15, rata kiri-kanan)
====================================================================================================

RINGKASAN *(tanpa nomor halaman — lihat catatan 0.2 poin 2)*

Stroke iskemik merupakan penyebab disabilitas neurologis dan kematian global yang penanganannya berpacu dengan waktu. Keterlambatan penanganan sering terjadi pada fase prarumah sakit akibat kurangnya kewaspadaan keluarga dalam mengenali gejala awal, seperti Transient Ischemic Attack (TIA). Di sisi lain, perangkat wearable komersial saat ini telah memiliki kemampuan yang baik dalam memantau berbagai parameter kebugaran secara berkala. Namun, perangkat tersebut pada umumnya didesain untuk pemantauan kesehatan secara umum dan belum difokuskan pada pemodelan prediktif spesifik untuk peringatan dini risiko stroke iskemik.

Berangkat dari permasalahan tersebut, dikembangkan inovasi ANTARAGA yang merupakan sistem peringatan dini prarumah sakit berbasis smartband dan Artificial Intelligence (AI). Tahapan pengembangan mencakup tiga fase utama. Pertama, perancangan hardware untuk akuisisi sinyal menggunakan sensor Photoplethysmography (PPG) multi-wavelength (kanal hijau 525 nm, merah 660 nm, dan inframerah 880 nm) yang dikendalikan oleh mikrokontroler ESP32-S3. Kedua, estimasi parameter fisiologis (tekanan darah sistolik, diastolik, glukosa, kolesterol, dan asam urat) melalui pra-pemrosesan data di server cloud menggunakan model Support Vector Regression (SVR) dan eXtreme Gradient Boosting (XGBoost). Ketiga, pemodelan klasifikasi tingkat risiko menggunakan metode Cost-Sensitive XGBoost, yang diterapkan untuk menangani masalah class imbalance pada dataset medis penderita stroke.

Pelaksanaan program ini telah menghasilkan prototipe fungsional smartband ANTARAGA beserta sistem yang terintegrasi. Secara teknis, fungsi alat ini telah divalidasi melalui pengujian awal terhadap 11 relawan, di mana data peringatan berhasil dikirimkan dan dipantau melalui aplikasi mobile Android secara real-time. Target luaran program juga telah dicapai, meliputi publikasi edukasi di media sosial, perolehan pencatatan Hak Cipta Program Komputer, serta penyusunan draf artikel ilmiah yang disesuaikan dengan pedoman Journal of Applied Electrical Engineering (JAEE). Kehadiran prototipe ANTARAGA diharapkan dapat menjadi instrumen peringatan dini yang membantu keluarga memantau kondisi pasien pada kondisi prarumah sakit. Melalui peringatan tersebut, sistem ini berpotensi mendukung pengambilan keputusan medis yang lebih cepat, sehingga berkontribusi pada upaya meminimalisir keterlambatan penanganan stroke iskemik di masa depan.

DAFTAR ISI

RINGKASAN .......................................................................................................... i
DAFTAR GAMBAR .............................................................................................. ii
DAFTAR TABEL ................................................................................................... v
DAFTAR LAMPIRAN .......................................................................................... vi
BAB 1. PENDAHULUAN ......................................................................................1
&nbsp;&nbsp;1.1 Latar Belakang .............................................................................................. 1
&nbsp;&nbsp;1.2 Tujuan dan Relevansi dengan Tema PKM 2026........................................... 2
&nbsp;&nbsp;1.3 Inovasi Karsa Cipta dan Kemutakhirannya................................................... 2
&nbsp;&nbsp;1.4 Target dan Capaian Luaran ........................................................................... 3
BAB 2. TINJAUAN PUSTAKA .............................................................................4
&nbsp;&nbsp;2.1 Perkembangan Teknologi Pemantauan Risiko Stroke .................................. 4
&nbsp;&nbsp;2.2 Landasan Teknologi Pendukung ANTARAGA ........................................... 4
BAB 3. TAHAP PELAKSANAAN.........................................................................5
&nbsp;&nbsp;3.1 Alat dan Bahan .............................................................................................. 5
&nbsp;&nbsp;3.2 Realisasi Pelaksanaan Program ..................................................................... 6
BAB 4. HASIL YANG DICAPAI DAN POTENSI KHUSUS ...............................7
&nbsp;&nbsp;4.1 Spesifikasi Prototipe ANTARAGA .............................................................. 7
&nbsp;&nbsp;4.2 Spesifikasi Aplikasi Mobile ANTARAGA ................................................... 8
&nbsp;&nbsp;4.3 Hasil Pelatihan dan Pengujian ....................................................................... 8
&nbsp;&nbsp;4.4 Dampak Pengiklanan Media Sosial ............................................................ 10
&nbsp;&nbsp;4.5 Potensi Prototipe Berdampak ...................................................................... 11
&nbsp;&nbsp;4.6 Potensi Hak Kekayaan Intelektual .............................................................. 11
&nbsp;&nbsp;4.7 Potensi Artikel Ilmiah ................................................................................. 11
&nbsp;&nbsp;4.8 Potensi Pengembangan Prototipe ................................................................ 11
BAB 5. PENUTUP ................................................................................................12
&nbsp;&nbsp;5.1 Kesimpulan ................................................................................................. 12
&nbsp;&nbsp;5.2 Rekomendasi ............................................................................................... 12
DAFTAR PUSTAKA ............................................................................................13
LAMPIRAN ...........................................................................................................14

*(Nomor halaman di atas perkiraan setelah penambahan 3.1 dan 4.8 — sesuaikan dengan hasil akhir di Word, termasuk Daftar Gambar/Tabel/Lampiran di bawah yang mengikuti pola penomoran PDF lama; geser sesuai posisi gambar/tabel final.)*

DAFTAR GAMBAR

Gambar 1. 1 Smartband ANTARAGA ................................................................... 1
Gambar 4. 1 Prototipe ANTARAGA ....................................................................... 7
Gambar 4. 2 Flowchart Pengiriman Data Alat ke Aplikasi ..................................... 8
*(Gambar L.1–L.82 pada Lampiran 1 tetap mengikuti urutan dan judul yang sudah ada — lihat Lampiran untuk daftar lengkap, tidak diulang di sini.)*

DAFTAR TABEL

Tabel 2. 1 Perbandingan ANTARAGA dengan Teknologi Sebelumnya ............... 4
Tabel 3. 1 Alat dan Bahan Pengembangan Prototipe ANTARAGA ...................... 5
Tabel 4. 1 Spesifikasi Hardware Smartband ANTARAGA .................................... 7
Tabel 4. 2 Evaluasi Model SVR dan XGBoost Estimasi Data Fisiologis per Parameter (LOO, n=11 subjek) ............................................................................... 8
Tabel 4. 3 Median Data Hasil Pengujian Relawan ................................................. 9
Tabel 4. 4 Metrik Evaluasi Performa Model Data Uji dan Pembacaan Alat .......... 9
Tabel 4. 5 Rekapitulasi Metrik Capaian Pengiklanan Media Sosial Instagram .... 10
*(Tabel L.1–L.27 pada Lampiran tetap mengikuti urutan dan judul yang sudah ada.)*

DAFTAR LAMPIRAN

Lampiran 1. Dokumentasi Pengembangan dan Pengujian ANTARAGA
Lampiran 2. Tabel Penggunaan Dana Belmawa
Lampiran 3. Tabel Penggunaan Dana In Kind dari PENS
Lampiran 4. Sampling Bukti Pengeluaran
Lampiran 5. Bukti Logbook Kegiatan
Lampiran 6. Sertifikat Hak Cipta
Lampiran 7. Ethical Clearance
Lampiran 8. Informed Consent
Lampiran 9. Draft Artikel Ilmiah

BAB 1. PENDAHULUAN

1.1 Latar Belakang

Stroke merupakan salah satu masalah kesehatan dengan dampak kematian dan kecacatan neurologis yang tinggi. Global Stroke Fact Sheet 2025 melaporkan sekitar 6,7 juta kematian akibat stroke setiap tahun (Feigin dkk., 2025). Sekitar 87% kasus merupakan stroke iskemik yang sangat sensitif terhadap waktu, sehingga keterlambatan penanganan dapat memperburuk luaran pasien (Capirossi dkk., 2023).

Salah satu hambatan penting terjadi pada fase prarumah sakit ketika keluarga terlambat mengenali urgensi gejala dan mengambil keputusan menuju fasilitas kesehatan (Potisopha dkk., 2023). Kondisi ini semakin sulit ketika keluhan menyerupai Transient Ischaemic Attack (TIA) yang dapat hilang timbul (Spampinato dkk., 2022). Meskipun kampanye Face dropping, Arm weakness, Speech difficulty, Time to call emergency (FAST) membantu pengenalan gejala, keputusan keluarga masih dapat dipengaruhi keraguan, kepanikan, atau anggapan bahwa kondisi telah membaik (Potisopha dkk., 2023).

Kondisi tersebut menunjukkan perlunya sarana pemantauan yang dapat memberikan informasi risiko secara lebih objektif kepada keluarga. Perkembangan perangkat wearable, Photoplethysmography (PPG), Internet of Things (IoT), dan AI membuka peluang untuk memenuhi kebutuhan tersebut. Namun, perangkat wearable kesehatan umumnya masih berorientasi pada pemantauan kebugaran, belum terintegrasi dengan mekanisme penilaian risiko dan tindak lanjut keluarga.

Menjawab urgensi tersebut, ANTARAGA dikembangkan sebagai "Smartband Berbasis Multi-Wavelength PPG dengan Artificial Intelligence Terintegrasi Aplikasi Mobile untuk Deteksi Dini Risiko Stroke Iskemik pada Lansia". Dalam pengembangannya, ANTARAGA menghadapi tantangan untuk mengolah sinyal PPG yang rentan gangguan dan profil risiko dengan kelas stroke minoritas menjadi peringatan yang sensitif, tanpa menjadikannya sebagai diagnosis klinis. Sistem mengolah indikator fisiologis dan faktor risiko menjadi informasi risiko, peringatan, serta asesmen Age, Blood Pressure, Clinical Features, Duration, dan Diabetes (ABCD2) bagi keluarga menuju evaluasi medis pada fase prarumah sakit.

(a)     (b)

Gambar 1. 1 Smartband (a) dan Aplikasi ANTARAGA (b)

1.2 Tujuan dan Relevansi dengan Tema PKM 2026

Tujuan pengembangan ANTARAGA adalah menyediakan instrumen peringatan dini risiko stroke iskemik untuk meminimalisir keterlambatan penanganan prarumah sakit sesuai prinsip "time is brain". Hal ini relevan dengan tema PKM 2026 "Kesehatan dan Gizi Masyarakat" melalui pemanfaatan teknologi untuk meningkatkan kewaspadaan kesehatan lansia secara mandiri di rumah.

1.3 Inovasi Karsa Cipta dan Kemutakhirannya

Inovasi ANTARAGA mengintegrasikan teknologi mutakhir berikut:

Akuisisi Sinyal PPG Multi-Wavelength

ANTARAGA menggunakan sensor SON1303 (525 nm) dan MAX30102 (660 nm & 880 nm) memanfaatkan perbedaan penetrasi cahaya jaringan untuk menghasilkan data fisiologis yang lebih akurat (Kim dan Baek, 2023).

Pengolahan Sinyal Terdistribusi antara ANTARAGA dan Server

Smartband berfokus pada akuisisi data dan penilaian Signal Quality Index (SQI), sementara server mengeksekusi komputasi filtering Butterworth 0,5-5 Hz, FFT, dan beats per minute (BPM) guna menghemat daya mikrokontroler.

Penilaian Risiko Stroke Menggunakan XGBoost

XGBoost menilai risiko berdasarkan sembilan faktor profil pengguna. Ketidakseimbangan kelas stroke sebesar 4,87% ditangani melalui scale_pos_weight, sedangkan ambang keputusan dievaluasi menggunakan prediksi out-of-fold dan kurva precision–recall.

Estimasi Parameter Fisiologis Menggunakan Kombinasi Support Vector Regression (SVR) dan XGBoost

Lima parameter fisiologis (sistolik, diastolik, glukosa, kolesterol, dan asam urat) diestimasi menggunakan SVR dan XGBoost. Algoritma dipilih berdasarkan akurasi tertinggi melalui validasi Leave-One-Subject-Out (LOSO). Model terintegrasi di server untuk memudahkan pelatihan ulang.

Integrasi Peringatan Risiko dan Asesmen ABCD2 pada Aplikasi Mobile

Hasil pemantauan terintegrasi dengan aplikasi mobile keluarga. Ketika sistem mendeteksi peningkatan risiko, aplikasi memberikan peringatan dan mengaktifkan asesmen ABCD2 untuk membantu menentukan tingkat urgensi (Spampinato dkk., 2022). Integrasi ini mendukung keluarga dalam mengambil keputusan evaluasi medis lebih cepat pada fase prarumah sakit.

1.4 Target dan Capaian Luaran

Pelaksanaan program ini telah diselesaikan dengan capaian 100% pada seluruh target luaran yang direncanakan, meliputi:

Laporan Kemajuan (Capaian 100%)

Laporan Akhir (Capaian 100%)

Prototipe ANTARAGA (Capaian 100%)

Akun dan Konten Media Sosial ANTARAGA (Capaian 100%)

Aplikasi Mobile ANTARAGA (Capaian 100%)

Video simulasi animasi cara kerja dan pengujian prototipe ANTARAGA (Capaian 100%)

Hak Cipta Program Komputer (Capaian 100%)

BAB 2. TINJAUAN PUSTAKA

2.1 Perkembangan Teknologi Pemantauan Risiko Stroke

Teknologi terkait pemantauan risiko dan kondisi stroke dikembangkan melalui beragam pendekatan. Gutierrez-Martinez dkk. (2024) menggunakan near-infrared spectroscopy (NIRS) untuk memantau oksigenasi otak pasien stroke, sedangkan Jeon dkk. (2023) memanfaatkan akselerometer pada kedua pergelangan tangan dan deep learning untuk mendeteksi stroke saat tidur. Pada pemantauan irama jantung, Fan dkk. (2019) menguji PPG melalui smartphone dan smartband untuk mendeteksi fibrilasi atrium. Blok dkk. (2025) mengevaluasi smartband berbasis PPG dan kecerdasan buatan dengan elektrokardiogram (ECG) sebagai pembanding. Perbandingan fitur disajikan pada Tabel 2.1.

Tabel 2. 1 Perbandingan ANTARAGA dengan Teknologi Sebelumnya

| Pendekatan | Pemantauan Berkala Wearable | Notifikasi Otomatis | Rekomendasi Tindakan Terintegrasi Keluarga |
|---|---|---|---|
| fNIRS/NIRS monitoring oksigenasi otak pascastroke (Gutierrez-Martinez dkk., 2024) | ✔ | - | - |
| Wristband accelerometer dan deep learning deteksi stroke saat tidur (Jeon dkk., 2023) | ✔ | ✔ | - |
| Smart medis PPG dan AI untuk deteksi AF tervalidasi ECG (Blok dkk., 2025) | ✔ | ✔ | - |
| Smartphone fingertip PPG untuk deteksi AF (Fan dkk., 2019) | - | - | ✔ |
| ANTARAGA | ✔ | ✔ | ✔ |

Pendekatan terdahulu memiliki sasaran berbeda, sehingga validasi oksigenasi otak, pola gerak, atau fibrilasi atrium tidak langsung membuktikan kemampuan penilaian risiko stroke iskemik. Selain itu, integrasi notifikasi dan rekomendasi tindakan kedaruratan bagi keluarga belum dilaporkan pada literatur tersebut. Oleh karena itu, kebaruan ANTARAGA diposisikan pada integrasi fungsional antara pemantauan parameter, pemodelan prediksi risiko, dan informasi tindak lanjut prarumah sakit melalui aplikasi keluarga.

2.2 Landasan Teknologi Pendukung ANTARAGA

PPG multi-wavelength (SON1303, MAX30102) pada ANTARAGA memanfaatkan perbedaan penetrasi cahaya untuk meredam artefak gerak (Kim dan Baek, 2023). Sinyal ini mengestimasi lima parameter fisiologis menggunakan SVR dan XGBoost melalui validasi leave-one-subject-out.

Tantangan intelektual utama proyek ini adalah class imbalance pada data klinis. Algoritma standar bias terhadap kelas mayoritas. Untuk mengatasinya tanpa resampling sintetik, ANTARAGA menerapkan class-weighted loss function pada algoritma XGBoost. Keputusan ini memprioritaskan sensitivitas deteksi (recall), karena kegagalan mendeteksi risiko sangat fatal pada fase prarumah sakit. Model risiko ini diintegrasikan dengan aplikasi mobile keluarga yang memuat asesmen ABCD2 untuk mendukung urgensi medis (Spampinato dkk., 2022).

BAB 3. TAHAP PELAKSANAAN

3.1 Alat dan Bahan

Pengembangan prototipe dan sistem ANTARAGA menggunakan alat dan bahan berikut, dikelompokkan menurut fungsinya. Rincian pembelian lengkap beserta tanggal dan nilai nominal tercantum pada Lampiran 2 dan Lampiran 3.

Tabel 3. 1 Alat dan Bahan Pengembangan Prototipe ANTARAGA

| Kelompok | Alat/Bahan | Fungsi dalam Pengembangan |
|---|---|---|
| Perangkat keras utama | Mikrokontroler XIAO ESP32-S3 (dual-core Xtensa LX7, Wi-Fi & Bluetooth 5.0 BLE) | Akuisisi sinyal, perhitungan SQI, dan transmisi data ke server |
| Perangkat keras utama | Sensor PPG SON1303 (hijau 525 nm) | Perekaman sinyal denyut nadi kanal hijau |
| Perangkat keras utama | Sensor PPG MAX30102 (merah 660 nm & inframerah 880 nm) | Perekaman sinyal denyut nadi dan estimasi parameter fisiologis |
| Catu daya | Baterai Li-Po 1S 950 mAh, modul charger TP5000, regulator LDO RT9013-33GB | Pasokan daya portabel dan stabil bagi smartband |
| Mekanik | PCB custom (fabrikasi mandiri), casing 3D print bahan PETG | Integrasi elektronik dan pelindung fisik komponen |
| Infrastruktur cloud | Virtual Private Server (VPS), domain dan hosting (www.antaraga.web.id) | Menjalankan backend FastAPI, filtering sinyal, dan model AI |
| Perangkat lunak pengembangan | Arduino/PlatformIO (firmware), FastAPI dan Python (backend & model AI), Flutter (aplikasi mobile), Docker Compose (deployment) | Pengembangan dan penyebaran firmware, server, dan aplikasi |
| Instrumen pembanding/kalibrasi | Tensimeter digital, alat cek 3-in-1 Elvasense (glukosa, kolesterol, asam urat), oksimeter jari | Rujukan nilai aktual saat kalibrasi dan pengujian pada relawan |
| Alat uji teknis | Osiloskop/multimeter untuk pengukuran tegangan keluaran dan derau regulator daya | Analisis kestabilan catu daya (buck/boost converter) pada Lampiran 1.3 |
| Bahan habis pakai | Komponen SMD (resistor, kapasitor, ferrite bead), strip lancet, perekat/mounting | Perakitan PCB dan kebutuhan pengujian pada relawan |

*(Baris "Alat uji teknis": mohon dikonfirmasi alat ukur yang benar-benar dipakai — saya menuliskan osiloskop/multimeter berdasarkan jenis pengujian yang didokumentasikan pada Gambar L.8–L.10, bukan dari spesifikasi alat yang saya lihat langsung.)*

3.2 Realisasi Pelaksanaan Program

Seluruh rangkaian pelaksanaan ANTARAGA telah direalisasikan 100% sesuai target. Dokumentasi pelaksanaan seluruh kegiatan disajikan pada Lampiran 1, dengan dua ringkasan evidensi utama: Tabel L.1 (realisasi prototipe dan ekosistem) dan Tabel L.2 (perbandingan rancangan pada proposal dengan realisasi akhir). Rincian tahapan beserta pertimbangan teknis di dalamnya adalah sebagai berikut:

1. Studi Literatur: Tahap studi literatur telah diselesaikan sepenuhnya (100%) dengan mengkaji referensi terkait parameter fisiologis, sinyal PPG, penanganan class imbalance, serta parameter klinis ABCD2. Hasil dari tahap ini menjadi fondasi utama dalam perancangan arsitektur ANTARAGA.
2. Perancangan Sistem: Perancangan sistem telah mencapai target 100%, meliputi pembuatan skematik, tata letak PCB, optimalisasi manajemen daya, basis data, aplikasi, hingga arsitektur model AI. Arsitektur sistem terdistribusi dipilih agar beban komputasi AI dapat dipindahkan ke server. Hasil tahap ini berupa desain mekanik, alur software, dan rancangan sistem hardware.
3. Pembuatan Prototipe: Pembuatan fisik alat telah terealisasi 100%. Prosesnya meliputi fabrikasi PCB custom, pencetakan casing 3D berbahan PETG, serta perakitan komponen. Pada tahap ini, mikrokontroler diganti dari XIAO ESP32-C3 menjadi ESP32-S3 karena kebutuhan prosesor dual-core dan SRAM yang memadai untuk membaca sensor, menghitung SQI, dan mengirim data ke cloud secara bersamaan. Sinyal diakuisisi lewat sensor SON1303 (hijau) dan MAX30102 (merah & inframerah), dengan dukungan baterai Li-Po 950 mAh, modul charger TP5000, serta regulator LDO RT9013-33GB. Hasil akhirnya adalah prototipe fisik smartband ANTARAGA.
4. Integrasi Sistem: Tahap integrasi telah terselesaikan 100% dengan menghubungkan firmware, modul Wi-Fi, cloud server (VPS), dan aplikasi Flutter. Agar daya smartband tidak cepat habis, pemrosesan sinyal seperti filtering bandpass Butterworth, FFT, dan kalkulasi BPM dipindah ke server, sementara perhitungan SQI tetap dieksekusi di perangkat. Hasilnya, sistem sudah tersinkronisasi dari perangkat wearable ke smartphone keluarga.
5. Pengembangan Model AI: Pengembangan model AI telah diselesaikan 100%. Algoritma XGBoost dituning menggunakan threshold spesifik untuk deteksi stroke. Pembobotan keputusan ini sengaja diterapkan untuk mengutamakan sensitivitas deteksi (recall) karena penggunaannya sebagai instrumen prarumah sakit. Selain itu, lima model estimasi fisiologis (SVR/XGBoost) juga telah dilatih menggunakan data kalibrasi. Hasilnya berupa model AI utuh yang telah terpasang di server.
6. Pengujian dan Validasi: Pengujian dan validasi subsistem telah tuntas 100% lewat 11 sesi uji coba bersama relawan dan konsultasi bersama dokter spesialis saraf. Evaluasi pembacaan parameter dibandingkan langsung dengan alat ukur terstandar berupa tensimeter dan glukometer digital. Untuk memastikan akurasi AI dievaluasi secara objektif pada pengguna baru, metode leave-one-subject-out (LOSO) diterapkan.
7. Pelaporan dan Publikasi: Pelaporan telah terselesaikan 100% melalui penyusunan Laporan Kemajuan, dokumentasi evaluasi alat, serta penyusunan Laporan Akhir dan draf artikel ilmiah. Selain keperluan administratif dan akademis, pengiklanan program juga direalisasikan lewat tiga konten utama (pengenalan, edukasi, pengujian) yang dipublikasikan di media sosial.
8. Pengajuan HKI: Pengajuan HKI telah tercapai 100%. Surat Pencatatan Hak Cipta untuk kategori Program Komputer telah diterbitkan oleh Kementerian Hukum dan HAM dengan nomor 001449089 (terlampir pada Lampiran 6).

BAB 4. HASIL YANG DICAPAI DAN POTENSI KHUSUS

4.1 Spesifikasi Prototipe ANTARAGA

Realisasi pembuatan smartband ANTARAGA telah mencapai 100% dengan spesifikasi hardware smartband ANTARAGA langsung disajikan pada Tabel 4.1.

Gambar 4. 1 Prototipe ANTARAGA: (a) tampak atas, (b) tampak dalam, (c) tampak bawah, (d) susunan komponen

Tabel 4. 1 Spesifikasi Hardware Smartband ANTARAGA

| No | Komponen | Spesifikasi Teknis | Fungsi & Hasil Pengujian |
|---|---|---|---|
| 1 | Mikrokontroler | XIAO ESP32-S3, dual-core Xtensa LX7 32-bit | Pusat kendali perangkat, transmisi Wi-Fi, dan firmware penilaian SQI. |
| 2 | Sensor PPG Hijau | SON1303 (Spektrum Hijau 525 nm) | Merekam dinamika denyut nadi, dilengkapi ferrite bead untuk reduksi noise 50 Hz. |
| 3 | Sensor PPG Merah/IR | MAX30102 (Spektrum Merah 660 nm & Inframerah 880 nm) | Sumber data utama Pulse Wave Analysis (PWA) dan ekstraksi indikator fisiologis. |
| 4 | Manajemen Power Supply | Baterai LiPo 1S, LDO RT9013-33GB | Pasokan daya bebas noise dengan durasi pasokan baterai terukur. |
| 5 | PCB | PCB Fabrikasi Mandiri | Pondasi dari seluruh komponen elektronik |
| 6 | Enclosure | PETG 3D Printing | Casing pelindung komponen dari keringat serta benturan. |

Realisasi integrasi hardware dan firmware telah mencapai 100%, didukung oleh pasokan daya yang stabil dengan kapasitas baterai efektif 813 mAh (durasi ~97 menit pada beban 500 mA). Agar kinerja sistem optimal, beban komputasi pemrosesan sinyal dialihkan ke VPS sehingga mikrokontroler dapat berfokus pada akuisisi data dan penilaian SQI, yang hasilnya kemudian ditransmisikan langsung ke aplikasi mobile melalui antarmuka FastAPI (www.antaraga.web.id).

4.2 Spesifikasi Aplikasi Mobile ANTARAGA

Aplikasi dikembangkan menggunakan Flutter yang terhubung ke backend melalui API. Fitur utamanya mencakup manajemen multiprofil ID dan autentikasi, statistik harian, serta dashboard pemantauan yang menyajikan status koneksi, parameter fisiologis, hasil prediksi risiko AI, dan grafik timeline kondisi. Sebagai pelengkap sistem peringatan dini, asesmen ABCD2 terintegrasi secara otomatis untuk memberikan penilaian awal dan estimasi risiko stroke jangka pendek (2, 7, dan 90 hari) berdasarkan kohort klinis yang tervalidasi (Spampinato dkk., 2022).

Gambar 4. 2 Flowchart Pengiriman Data Alat ke Aplikasi

4.3 Hasil Pelatihan dan Pengujian

4.3.1 Hasil Pelatihan Model XGBoost

Dataset model risiko memiliki class imbalance dengan kelas stroke sekitar 4,87%. Karena akurasi dapat menyesatkan pada kondisi tersebut, evaluasi menggunakan Average Precision dan recall. XGBoost dengan scale_pos_weight 19,55 dibandingkan dengan HistGradientBoosting melalui RandomizedSearchCV dan StratifiedKFold lima lipatan; XGBoost unggul dengan Average Precision 0,2313 berbanding 0,2281 pada HistGradientBoosting (dokumentasi lengkap pada Gambar L.30–L.32). Empat puluh kombinasi parameter melalui lima validasi silang menghasilkan 200 proses pelatihan.

Threshold awal 0,705 dipilih berdasarkan F1-score terbaik sebesar 0,2946. Optimasi berikutnya memprioritaskan sensitivitas sistem peringatan dan menghasilkan threshold 0,042 dengan recall 0,973 (97,3%), yaitu 73 dari 75 kasus stroke pada data uji berhasil terdeteksi. Detailnya terlampir pada Lampiran 1.

4.3.2 Hasil Pelatihan Model Estimasi Parameter Fisiologis Menggunakan Kombinasi SVR dan XGBoost

Cakupan parameter fisiologis diperluas mencakup asam urat, tekanan darah, gula darah, dan kolesterol. Model kombinasi SVR dan XGBoost terintegrasi dengan dashboard untuk mendukung pelatihan ulang secara berkala. Kapasitas model diskalakan otomatis sesuai jumlah subjek kalibrasi (1 lapisan dengan 4 neuron untuk <10 subjek, dan 2 lapisan untuk jumlah lebih besar) untuk menghindari overfitting. Evaluasi kuantitatif menggunakan MAE, RMSE, MAPE, dan R² melalui skema validasi LOO, di mana setiap subjek diuji oleh model yang belum pernah dilatih menggunakan datanya. Performa akurasi dari masing-masing model untuk setiap parameter disajikan pada Tabel 4.2.

Tabel 4. 2 Evaluasi Model SVR dan XGBoost Estimasi Data Fisiologis per Parameter (LOO, n=11 subjek)

| Parameter | N | R² | Akurasi (%) |
|---|---|---|---|
| Gula Darah | 11 | -0,065 | 75,50% |
| Kolesterol | 11 | -0,071 | 89,33% |
| Asam Urat | 11 | -0,001 | 85,21% |
| Sistolik | 11 | -0,081 | 90,61% |
| Diastolik | 11 | 0,134 | 88,80% |

4.3.3 Hasil Pengujian Prototipe pada Relawan

Pengujian pada 11 relawan dilakukan untuk memvalidasi fungsi alat secara menyeluruh. Akurasi pembacaan ANTARAGA divalidasi terhadap instrumen medis eksisting (glukometer Elvasense dan tensimeter digital) serta hasil uji laboratorium aktual, yang memastikan margin error prototipe sejalan dengan alat pembanding tersebut. Perbandingannya disajikan pada Tabel 4.3 berikut:

Tabel 4. 3 Median Data Hasil Pengujian Relawan

| Parameter | Sumber Pembacaan | Median Stroke (n=2) | Median Non Stroke (n=9) | Akurasi Keseluruhan |
|---|---|---|---|---|
| Sistolik (mmHg) | Alat Medis Terstandar | 149,5 | 151 | 94,98% |
| Sistolik (mmHg) | Prediksi ANTARAGA | 148,6 | 142,9 | |
| Diastolik (mmHg) | Alat Medis Terstandar | 72 | 86 | 95,78% |
| Diastolik (mmHg) | Prediksi ANTARAGA | 76,2 | 88,9 | |
| Gula Darah (mg/dL) | Alat Medis Terstandar | 168 | 121 | 91,34% |
| Gula Darah (mg/dL) | Prediksi ANTARAGA | 150,6 | 131 | |
| Kolesterol (mg/dL) | Alat Medis Terstandar | 268,5 | 232 | 91,63% |
| Kolesterol (mg/dL) | Prediksi ANTARAGA | 250 | 225 | |
| Asam Urat (mg/dL) | Alat Medis Terstandar | 6 | 5 | 94,21% |
| Asam Urat (mg/dL) | Prediksi ANTARAGA | 5,7 | 5,2 | |

Angka akurasi pada Tabel 4.3 dihitung dari kedekatan nilai median gabungan 11 relawan antara alat referensi dan prediksi ANTARAGA, berbeda dengan Tabel 4.2 yang melaporkan akurasi evaluasi Leave-One-Out per subjek — median jauh lebih stabil terhadap pencilan dibanding estimasi pada satu orang, sehingga kedua angka ini saling melengkapi, bukan saling menggantikan: Tabel 4.2 menggambarkan performa model pada tiap individu, sedangkan Tabel 4.3 menggambarkan kecenderungan pembacaan alat pada populasi uji.

Sistem AI dikembangkan menggunakan model XGBoost untuk prediksi risiko stroke, serta model SVR dan XGBoost untuk kalibrasi sinyal PPG (training model). Metrik evaluasi disajikan pada Tabel 4.4.

Tabel 4. 4 Metrik Evaluasi Performa Model Data Uji dan Pembacaan Alat

| Parameter Evaluasi | Target | Hasil Realisasi | Status |
|---|---|---|---|
| Recall (Sensitivitas) XGBoost | > 90% | 97,3% (73/75 kasus terdeteksi) | Sangat Baik |
| Skor ROC-AUC XGBoost | > 0,80 | 0,823 | Memenuhi Standar |
| Ambang Keputusan (Threshold) | Out-of-Fold Margin | 0,042 (Deteksi) / 0,705 (Risiko Tinggi) | Sesuai Standar AHA ABCD2 |
| Perfusi Inframerah (PPG) | 0,02 – 2,00 ‰ | 0,74 – 1,77 ‰ | Sinyal Normal |
| Latensi Transmisi Sistem | < 3 Detik | < 2 Detik (Cloud ke aplikasi mobile) | Sangat Cepat |

Pengujian fungsional pada 11 relawan (selengkapnya pada Lampiran 1) menunjukkan pembacaan sinyal PPG stabil pada rentang indeks perfusi normal (0,74–1,77‰) dan tangguh terhadap gerakan berkat penyaring lonjakan BPM 4 lapis pada backend. Seperti yang telah dijabarkan sebelumnya, penyesuaian threshold dan optimasi model berhasil mencapai sensitivitas 97,3% guna meminimalkan risiko bahaya yang terlewat (false negative). Seluruh parameter risiko dan asesmen ABCD2 pada aplikasi telah divalidasi bersama dokter spesialis saraf pada 7 Agustus 2026. Hal ini mengonfirmasi batasan operasional ANTARAGA murni sebagai sistem deteksi dini prarumah sakit pendukung keputusan, bukan alat diagnosis medis. Dokumentasi pengujian selengkapnya dapat ditinjau melalui Video Luaran ANTARAGA.

4.4 Dampak Pengiklanan Media Sosial

Hingga saat penulisan laporan ini, aktivitas publikasi dan edukasi melalui akun @pkmkc.antaraga telah menghasilkan 30 unggahan dengan 805 pengikut di platform Instagram, serta 5 unggahan dengan 24 pengikut di TikTok, serta 2 unggahan dengan 20 subscriber di YouTube. Untuk memaksimalkan jangkauan informasi, tiga konten utama program telah diiklankan pada platform Instagram. Rekapitulasi metrik capaian pengiklanan tersebut disajikan pada Tabel 4.5.

Tabel 4. 5 Rekapitulasi Metrik Capaian Pengiklanan Media Sosial Instagram

| Metrik Capaian | Iklan 1 (Pengenalan) | Iklan 2 (Edukasi Tanda Risiko) | Iklan 3 (Pengujian) | Total Capaian |
|---|---|---|---|---|
| Jangkauan | 10.358 | 11.380 | 15.448 | 37.186 |
| Tayangan | 12.403 | 15.332 | 26.629 | 54.364 |
| Interaksi | 2.336 | 4.237 | 4.530 | 11.103 |
| Kunjungan Profil | 291 | 281 | 436 | 1.008 |
| Pengikut Baru | 6 | 9 | 15 | 30 |

Peningkatan tren metrik ini mengonfirmasi bahwa penyajian konten yang lebih informatif efektif meningkatkan visibilitas serta keterlibatan audiens.

4.5 Potensi Prototipe Berdampak

Secara strategis, ANTARAGA memberikan informasi risiko stroke iskemik untuk mempercepat keputusan rujukan medis keluarga pada fase prarumah sakit guna memaksimalkan golden period. Penanganan dini ini penting untuk mencegah kecacatan neurologis permanen. Secara keekonomian, intervensi ini berkontribusi menurunkan tingginya beban pembiayaan katastropik pasca-stroke.

4.6 Potensi Hak Kekayaan Intelektual

Inovasi ini telah memperoleh perlindungan hukum berupa Sertifikat Hak Cipta Program Komputer dari Kementerian Hukum dengan nomor pencatatan 001449089. Sertifikat Hak Cipta terlampir pada Lampiran 6.

4.7 Potensi Artikel Ilmiah

Potensi luaran artikel ilmiah berjudul "A Pre-Hospital Early Warning System for Ischemic Stroke Risk Based on Multi-Wavelength PPG and an XGBoost Algorithm" telah disusun menyesuaikan pedoman Journal of Applied Electrical Engineering (JAEE) pada Lampiran 9.

4.8 Potensi Pengembangan Prototipe

Pengembangan ANTARAGA selanjutnya dirancang bertahap, dari penguatan bukti ilmiah jangka pendek hingga kesiapan komersialisasi jangka panjang, dengan masing-masing tahap disusun berdasarkan keterbatasan nyata yang teridentifikasi dari pengujian 11 relawan dan evaluasi model saat ini.

Jangka Pendek (Tahun Pertama)

Prioritas utama adalah memperluas kohort kalibrasi dari 11 menjadi minimal 30 relawan dengan rentang usia, tekanan darah, dan kadar metabolik yang lebih lebar, karena evaluasi saat ini menunjukkan performa estimator tekanan darah, glukosa, kolesterol, dan asam urat masih sangat bergantung pada sempitnya sebaran data 11 relawan. Validasi juga akan diperluas dengan skema Leave-One-Subject-Out bertingkat (nested LOSO) pada kohort yang lebih besar untuk memastikan performa tidak hanya optimis pada data pelatihan. Berbekal ethical clearance dan validasi dokter spesialis saraf yang telah diperoleh, pengembangan lain pada tahap ini mencakup:

- Pelatihan ulang model deteksi risiko stroke dan model estimasi fisiologis begitu kohort kalibrasi bertambah, termasuk menyinkronkan artefak model di server dengan data kalibrasi terbaru agar tidak terjadi selisih antara model yang berjalan dan model yang dilaporkan.
- Perpanjangan durasi akuisisi sinyal PPG menjadi minimal 10 detik secara konsisten pada setiap sesi pengukuran, karena rekaman yang lebih pendek terbukti meningkatkan risiko salah baca detak jantung dua kali lipat (kesalahan oktaf) pada autokorelasi sinyal mentah.
- Efisiensi daya dengan mengevaluasi pemanfaatan Bluetooth Low Energy (BLE) 5.0 — kapabilitas yang sudah tersedia pada mikrokontroler ESP32-S3 namun belum dimanfaatkan karena transmisi data saat ini masih melalui Wi-Fi — untuk transfer data jarak dekat yang lebih hemat daya dibanding Wi-Fi pada pemakaian berkala.
- Stabilitas sistem real-time dan pengujian keandalan sensor pada kondisi dinamis (gerakan, variasi suhu kulit, dan variasi warna kulit), serta evaluasi lanjutan nilai spesifisitas dan sensitivitas alat pada kohort yang diperluas.

Jangka Menengah (1–3 Tahun ke Depan)

Fokus bergeser pada kesiapan perangkat untuk pemakaian harian di luar sesi pengujian terkontrol:

- Peningkatan kenyamanan perangkat (wearability), termasuk evaluasi desain casing dan tali yang lebih ergonomis untuk pemakaian jangka panjang oleh lansia.
- Penambahan titik pengukuran kedua (misalnya pada jari atau pergelangan tangan yang berlawanan) untuk fitur pulse transit time, yang berpotensi memperbaiki akurasi estimasi tekanan darah tanpa kalibrasi manset manual.
- Penerapan enkripsi data dan autentikasi yang lebih ketat untuk melindungi data kesehatan pengguna, mengingat data fisiologis dan profil risiko tergolong data pribadi yang bersifat sensitif.
- Evaluasi operasional lanjutan bersama tenaga kesehatan (dokter spesialis saraf, perawat, atau puskesmas mitra) untuk menilai kesesuaian alur peringatan dan asesmen ABCD2 dalam praktik nyata, bukan hanya pada simulasi pengujian internal.

Jangka Panjang

Pengkajian Tingkat Kesiapan Teknologi (TKT) sebagai prasyarat utama komersialisasi produk secara luas, mencakup uji klinis terstruktur pada populasi berisiko stroke yang lebih besar dan beragam (termasuk penderita hipertensi, diabetes, dan penyakit jantung terdiagnosis), sertifikasi alat kesehatan sesuai regulasi yang berlaku, serta kemitraan strategis dengan penyedia layanan kesehatan (rumah sakit, puskesmas, atau klinik) untuk jalur distribusi dan model bisnis keberlanjutan produk.

BAB 5. PENUTUP

5.1 Kesimpulan

Berdasarkan pelaksanaan program, prototipe smartband ANTARAGA telah berfungsi secara penuh dalam melakukan akuisisi sinyal multi-wavelength PPG non-invasif untuk mengestimasi parameter fisiologis pengguna. Integrasi algoritma Class-weighted XGBoost dan asesmen ABCD2 pada aplikasi mobile juga telah tervalidasi mampu mendeteksi anomali risiko stroke secara dini melalui uji coba fungsional pada 11 relawan. Secara keseluruhan, kinerja sistem yang dilengkapi fitur notifikasi real-time ke smartphone keluarga ini telah berhasil menjawab tujuan utama program, yakni menyediakan instrumen peringatan dini prarumah sakit guna meminimalkan keterlambatan penanganan medis (time is brain).

5.2 Rekomendasi

Pengembangan ANTARAGA ke depan perlu difokuskan pada pengujian lanjutan terhadap sampel medis spesifik (hipertensi, diabetes, dan penyakit jantung) guna mengukur tingkat sensitivitas serta spesifisitas alat secara komprehensif, dengan jumlah relawan yang diperluas hingga minimal 30 subjek agar hasil evaluasi tidak lagi dibatasi oleh sempitnya sebaran data saat ini. Aplikasi juga perlu dilengkapi panduan rekomendasi tindakan pertama pada sistem notifikasi. Selain itu, evaluasi stabilitas perangkat, kalibrasi sensor lanjutan, dan wearability smartband menjadi langkah penting untuk menunjang pengkajian Tingkat Kesiapan Teknologi (TKT) menuju tahapan komersialisasi.

DAFTAR PUSTAKA

Blok, S., Gielen, W., Piek, M.A., Hoeksema, W.F., Tulevski, I., Somsen, A.A. dan Winter, M.M. (2025) 'Performance of a medical smartband with photoplethysmography technology and artificial intelligence algorithm to detect atrial fibrillation', mHealth, 11, hlm. 5. Tersedia di: https://doi.org/10.21037/mhealth-24-10 (Diakses 18 Maret 2026).

Capirossi, C., Laiso, A., Renieri, L., Capasso, F. dan Limbucci, N. (2023) 'Epidemiology, organization, diagnosis and treatment of acute ischemic stroke', European Journal of Radiology Open, 11, hlm. 100527. Tersedia di: https://doi.org/10.1016/j.ejro.2023.100527 (Diakses 12 Maret 2026).

Fan, Y.Y., Li, Y.G., Li, J., Cheng, W.K., Shan, Z.L., Wang, Y.T. dan Guo, Y.T. (2019) 'Diagnostic performance of a smart device with photoplethysmography technology for atrial fibrillation detection: pilot study (Pre-mAFA II registry)', JMIR mHealth and uHealth, 7(3), hlm. e11437. Tersedia di: https://doi.org/10.2196/11437 (Diakses 16 Maret 2026).

Feigin, V.L., Brainin, M., Norrving, B., Martins, S.O., Pandian, J., Lindsay, P., Grupper, M.F. dan Rautalin, I. (2025) 'World Stroke Organization: global stroke fact sheet 2025', International Journal of Stroke, 20(2), hlm. 132–144. Tersedia di: https://doi.org/10.1177/17474930241308142 (Diakses 12 Maret 2026).

Gutierrez-Martinez, J., Vega-Martinez, G., Toledo-Peral, C.L., Mercado-Gutierrez, J.A. dan Quinzaños-Fresnedo, J. (2024) 'A NIRS-based technique for monitoring brain tissue oxygenation in stroke patients', Sensors, 24(24), hlm. 8175. Tersedia di: https://doi.org/10.3390/s24248175 (Diakses 18 Maret 2026).

Jeon, S., Lee, Y.S. dan Son, S.H. (2023) 'Cascade windows-based multi-stream convolutional neural networks framework for early detecting in-sleep stroke using wristbands', IEEE Access, 11, hlm. 84944–84956. Tersedia di: https://doi.org/10.1109/ACCESS.2023.3301872 (Diakses 18 Maret 2026).

Kim, K.B. dan Baek, H.J. (2023) 'Photoplethysmography in wearable devices: a comprehensive review of technological advances, current challenges, and future directions', Electronics, 12(13), hlm. 2923. Tersedia di: https://doi.org/10.3390/electronics12132923 (Diakses 16 Maret 2026).

Potisopha, W., Vuckovic, K.M., DeVon, H.A., Park, C.G., Phutthikhamin, N. dan Hershberger, P.E. (2023) 'Decision delay is a significant contributor to prehospital delay for stroke symptoms', Western Journal of Nursing Research, 45(1), hlm. 55–66. Tersedia di: https://doi.org/10.1177/01939459221105827 (Diakses 12 Maret 2026).

Spampinato, M.D., Covino, M., Passaro, A., Guarino, M., Marziani, B., Ghirardi, C., Ricciardelli, A., Fabbri, I.S., Strada, A., Gasbarrini, A., Franceschi, F. dan De Giorgio, R. (2022) 'ABCD2, ABCD2-I, and OTTAWA scores for stroke risk assessment: a direct retrospective comparison', Internal and Emergency Medicine, 17(8), hlm. 2391–2401. Tersedia di: https://doi.org/10.1007/s11739-022-03074-x (Diakses 12 Maret 2026).

LAMPIRAN 

Lampiran 1. Dokumentasi Pengembangan dan Pengujian ANTARAGA 

Lampiran 1. 1 Dokumentasi Prototipe ANTARAGA 

Tabel L. 1 Realisasi Prototipe dan Ekosistem ANTARAGA 

No 

Keterangan 

Dokumentasi 

1 

Prototipe final tampak depan, samping, belakang 

 

Gambar L. 1 Prototipe Tampak Depan 

 

 

Gambar L. 2 Prototipe Tampak Samping 

 

 

Gambar L. 3 Prototipe Tampak Belakang 

2 

Smartband ketika digunakan 

 

Gambar L. 4 Prototipe Ketika Dipakai 

3 

PCB final 

 

Gambar L. 5 PCB Terintegrasi Komponen Elektronik 

 

4 

Casing PETG 

 

Gambar L. 6 Foto Hasil Cetak Casing PETG 

 

5 

Tampilan aplikasi mobile. Fitur dan tampilan selengkapnya dapat dilihat pada Lampiran 1.6 

 

Gambar L. 7 Tampilan Dashboard Aplikasi Mobile ANTARAGA 

Lampiran 1. 2 Perubahan dan Penyempurnaan Desain 

Tabel L. 2 Perbandingan Aspek Proposal dan Realisasi Sistem 

Aspek Proposal 

Realisasi 

Alasan/Implikasi 

XIAO ESP32-C3 

XIAO ESP32-S3 

Keterbatasan jumlah core pemrosesan dan SRAM yang tidak cukup untuk eksekusi seluruh firmware. 

Baterai 900 mAh 

Li-Po 1S 950 mAh pada prototipe uji 

Penyesuaian kapasitas sumber daya dan dimensi. 

Pemrosesan sinyal pada perangkat 

Pemrosesan utama pada server 

Mengurangi beban pemrosesan perangkat dan memudahkan pembaruan algoritma. 

Model Gradient Boosting 

XGBoost untuk prediksi risiko 

XGBoost dipilih dari perbandingan langsung dengan HistGradientBoosting (Subbab 4.3.1; dokumentasi pada Gambar L.30–L.32): Average Precision lebih tinggi (0,2313 vs 0,2281) dan mendukung scale_pos_weight bawaan untuk menangani class imbalance (kelas stroke ~4,87%) tanpa perlu resampling data medis yang jumlahnya terbatas. 

Model MLP (Multi Layer Perceptron) untuk estimasi data fisiologis (tekanan darah, gula darah, kolesterol, dan asam urat) 

Menggunakan kombinasi model Support Vector Regression (SVR) dan XGBoost untuk estimasi data fisiologis (tekanan darah, gula darah, kolesterol, dan asam urat) 

Setelah melakukan training dengan data subjek dan membaca persentase nya, model MLP tidak cocok untuk menangani kasus dengan jumlah data kecil, sehingga dibutuhkan model lain yang mampu lebih baik menangani data kecil seperti SVR dan XGBoost. 

Dari hasil percobaan, didapatkan bahwa model terbaik adalah SVR untuk estimasi asam urat, tekanan darah sistolik, dan tekanan darah diastolik.⁠ Sedangkan XGBoost baik dalam mengestimasi gula darah dan kolesterol. 

 

Lampiran 1. 3 Pengujian Teknis Prototipe 

Tabel L. 3 Dokumentasi Pengujian Teknis Hardware Prototipe 

No 

Pengujian 

Dokumentasi 

1 

Manajemen sistem daya 

 

Gambar L. 8 Analisis Output Ketika Menggunakan Buck Converter 

 

 

Gambar L. 9 Analisis Noise Ketika Menggunakan Boost Converter 

 

 

Gambar L. 10 Datasheet Regulator LDO RT9013-33GB 

 

2 

Pengujian SON1303 

 

Gambar L. 11 Interfensi Noise 50Hz pada Sinyal Output Sensor SON1303 

 

 

Gambar L. 12 Sinyal Output Sensor SON1303 Setelah Optimalisasi 

3 

Pengujian MAX30102 

 

Gambar L. 13 Sensor MAX30102 Rusak Karena Cacat Pabrik 

 

 

 

Gambar L. 14 Malfungsi LED Channel IR pada Sensor MAX30102 

 

 

 

Gambar L. 15 Sensor Baru MAX30102 dan Berhasil Berfungsi 

 

 

 

Gambar L. 16 Sinyal Output Sensor MAX30102 pada Channel RED Dan IR Setelah Optimalisasi 

 

Gambar L. 17 Perbandingan Pembacaan Sensor MAX30102 dan Oximeter Terstandar dengan Selisih 1 BPM 

4 

Charge-discharge baterai 

 

Gambar L. 18 Uji Discharge Baterai LiPo 1s dengan Beban 500mA 

5 

Desain Layout PCB 

 

Gambar L. 19 Dokumentasi Desain Layout PCB 

6 

Inspeksi PCB 

 

Gambar L. 20 Sinyal Output Sensor SON1303 Setelah Optimalisasi 

7 

Pengujian casing 

 

Gambar L. 21 Casing Tidak Bisa Menutup Rapat 

 

 

Gambar L. 22 Hasil Casing Setelah Penyesuaian 

8 

Pengiriman data dan dashboard server 

Gambar L. 23 Memastikan Data Dari Perangkat Bisa 

 

Lampiran 1. 4 Pengujian pada Relawan 

Enam kegiatan pengujian tercatat pada logbook sampai 7 September 2026. Sebelas kode subjek (S001-S011) relawan telah dilakukan pengujian menggunakan smartband ANTARAGA. Bagian ini menyajikan tiga hal per relawan: data profil, perbandingan alat medis vs prediksi MLP, dan hasil deteksi risiko stroke. 

Tabel L. 4 Data Profil Relawan (S001-S004) 

Field 

S001 

S002 

S003 

S004 

Usia 

20 

57 

75 

70 

Gender 

Laki-laki 

Perempuan 

Perempuan 

Perempuan 

Kondisi Pengambilan 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Merokok 

Tidak 

Tidak 

Tidak 

Tidak 

Riwayat Penyakit Jantung 

Tidak 

Tidak 

Tidak 

Tidak 

Status Bekerja 

Ya (Mahasiswa) 

Tidak (Sudah Pensiun) 

Tidak (Sudah Pensiun) 

Tidak (Sudah Pensiun) 

Tipe Tempat Tinggal 

Kota 

Kota 

Kota 

Kota 

Riwayat Diabetes 

Tidak 

Tidak 

Tidak 

Tidak 

Riwayat Stroke Keluarga 

Tidak 

Tidak 

Tidak 

Tidak 

Riwayat Stroke Pribadi 

Tidak 

Tidak 

Tidak 

Ya 

Tanggal Pengujian 

3 Agustus 2026 

6 Agustus 2026 

6 Agustus 2026 

10 Agustus 2026 

Tabel L. 5 Data Profil Relawan (S005-S008) 

Field 

S005 

S006 

S007 

S008 

Usia 

76 

75 

75 

62 

Gender 

Laki-laki 

Perempuan 

Laki-laki 

Laki-laki 

Kondisi Pengambilan 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Merokok 

Tidak 

Tidak 

Ya 

Tidak 

Riwayat Penyakit Jantung 

Tidak 

Tidak 

Tidak 

Tidak 

Status Bekerja 

Sudah Pensiun (Tidak) 

Sudah Pensiun (Tidak) 

Sudah Pensiun (Tidak) 

Sudah Pensiun (Tidak) 

Tipe Tempat Tinggal 

Kota 

Kota 

Kota 

Kota 

Riwayat Diabetes 

Tidak 

Tidak 

Tidak 

Tidak 

Riwayat Stroke Keluarga 

Tidak 

Tidak 

Ya 

Tidak 

Riwayat Stroke Pribadi 

Tidak 

Tidak 

Ya 

Tidak 

Tanggal Pengujian 

10 Agustus 2026 

14 Agustus 2026 

2 September 2026 

2 September 2026 

 

Tabel L. 6 Data Profil Relawan (S009-S011) 

Field 

S009 

S010 

S011 

Usia 

62 

63 

80 

Gender 

Perempuan 

Laki-laki 

Perempuan 

Kondisi Pengambilan 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Sewaktu (tidak puasa) 

Merokok 

Tidak 

Tidak 

Tidak 

Riwayat Penyakit Jantung 

Tidak 

Tidak 

Tidak 

Status Bekerja 

Sudah Pensiun (Tidak) 

Sudah Pensiun (Tidak) 

Sudah Pensiun (Tidak) 

Tipe Tempat Tinggal 

Kota 

Kota 

Kota 

Riwayat Diabetes 

Tidak 

Tidak 

Tidak 

Riwayat Stroke Keluarga 

Tidak 

Tidak 

Tidak 

Riwayat Stroke Pribadi 

Tidak 

Tidak 

Tidak 

Tanggal Pengujian 

2 September 2026 

7 September 2026 

7 September 2026 

 

Tabel L. 7 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S001 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S001 

Tensimeter (Tekanan Darah Sistolilk) 

125,0 mmHg 

130,3 mmHg 

95.8% 

Tensimeter (Tekanan Darah Diastolik) 

77,0 mmHg 

79,9 mmHg 

96.2% 

Elvasense 3in1 EMS10 (Gula Darah) 

119,0 mg/dL 

128,7 mg/dL 

91.9% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

212,0 mg/dL 

220,7 mg/dL 

95.9% 

Elvasense 3in1 EMS10 (Asam Urat) 

6,3 mg/dL 

6,2 mg/dL 

98.4% 

Link detail PDF data relawan subjek S001: Data Relawan S001 

 

Tabel L. 8 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S002 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S002 

Tensimeter (Tekanan Darah Sistolilk) 

173,0 mmHg 

154,3 mmHg 

89.2% 

Tensimeter (Tekanan Darah Diastolik) 

102,0 mmHg 

94,9 mmHg 

93.0% 

Elvasense 3in1 EMS10 (Gula Darah) 

101,0 mg/dL 

103,9 mg/dL 

97.2% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

200,0 mg/dL 

220,7 mg/dL 

89.7% 

Elvasense 3in1 EMS10 (Asam Urat) 

4,6 mg/dL 

4.7 mg/dL 

97.8% 

Link detail PDF data relawan subjek S002: Data Relawan S002 

 

Tabel L. 9 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S003 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S003 

Tensimeter (Tekanan Darah Sistolilk) 

153,0 mmHg 

153,1 mmHg 

99.9% 

Tensimeter (Tekanan Darah Diastolik) 

94,0 mmHg 

93,9 mmHg 

99.9% 

Elvasense 3in1 EMS10 (Gula Darah) 

183,0 mg/dL 

146,7 mg/dL 

80.1% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

232,0 mg/dL 

249,7 mg/dL 

92.4% 

Elvasense 3in1 EMS10 (Asam Urat) 

4,5 mg/dL 

5,1 mg/dL 

86.3% 

Link detail PDF data relawan subjek S003: Data Relawan S003 

 

Tabel L. 10 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S004 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S004 

Tensimeter (Tekanan Darah Sistolilk) 

157,0 mmHg 

155,3 mmHg 

98.9% 

Tensimeter (Tekanan Darah Diastolik) 

88,0 mmHg 

88,2 mmHg 

99.8% 

Elvasense 3in1 EMS10 (Gula Darah) 

153,0 mg/dL 

154,5 mg/dL 

99.9% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

269,0 mg/dL 

250,2 mg/dL 

93.0% 

Elvasense 3in1 EMS10 (Asam Urat) 

4,8 mg/dL 

4.9 mg/dL 

97.9% 

Link detail PDF data relawan subjek S004: Data Relawan S004 

 

Tabel L. 11 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S005 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S005 

Tensimeter (Tekanan Darah Sistolilk) 

166,0 mmHg 

136,1 mmHg 

82.0% 

Tensimeter (Tekanan Darah Diastolik) 

86,0 mmHg 

86,1 mmHg 

99.9% 

Elvasense 3in1 EMS10 (Gula Darah) 

98,0 mg/dL 

111,2 mg/dL 

86.5% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

244,0 mg/dL 

242,6 mg/dL 

99.4% 

Elvasense 3in1 EMS10 (Asam Urat) 

5,3 mg/dL 

5,3 mg/dL 

99.3% 

Link detail PDF data relawan subjek S005: Data Relawan S005 

 

Tabel L. 12 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S006 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S006 

Tensimeter (Tekanan Darah Sistolilk) 

145,0 mmHg 

148,53 mmHg 

97.6% 

Tensimeter (Tekanan Darah Diastolik) 

78,0 mmHg 

91,0 mmHg 

83.4% 

Elvasense 3in1 EMS10 (Gula Darah) 

94,0 mg/dL 

98,7 mg/dL 

95.0% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

269,0 mg/dL 

249,7 mg/dL 

92.8% 

Elvasense 3in1 EMS10 (Asam Urat) 

6,3 mg/dL 

5,9 mg/dL 

94.4% 

Link detail PDF data relawan subjek S006: Data Relawan S006 

 

Tabel L. 13 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S007 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S007 

Tensimeter (Tekanan Darah Sistolilk) 

142,0 mmHg 

141,9 mmHg 

99.9% 

Tensimeter (Tekanan Darah Diastolik) 

56,0 mmHg 

64,1 mmHg 

85.5% 

Elvasense 3in1 EMS10 (Gula Darah) 

183,0 mg/dL 

146,7 mg/dL 

80.1% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

268,0 mg/dL 

249,7 mg/dL 

93.2% 

Elvasense 3in1 EMS10 (Asam Urat) 

7,2 mg/dL 

6,4 mg/dL 

89.5% 

Link detail PDF data relawan subjek S007: Data Relawan S007 

 

Tabel L. 14 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S008 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S008 

Tensimeter (Tekanan Darah Sistolilk) 

131,0 mmHg 

142,6 mmHg 

91.1% 

Tensimeter (Tekanan Darah Diastolik) 

91,0 mmHg 

88,9 mmHg 

97.7% 

Elvasense 3in1 EMS10 (Gula Darah) 

171,0 mg/dL 

157,6 mg/dL 

92.2% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

261,0 mg/dL 

225,0 mg/dL 

86.2% 

Elvasense 3in1 EMS10 (Asam Urat) 

5,0 mg/dL 

5,1 mg/dL 

98.0% 

Link detail PDF data relawan subjek S008: Data Relawan S008 

 

Tabel L. 15 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S009 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S009 

Tensimeter (Tekanan Darah Sistolilk) 

121,0 mmHg 

123,0 mmHg 

98.3% 

Tensimeter (Tekanan Darah Diastolik) 

71,0 mmHg 

70,9 mmHg 

99.9% 

Elvasense 3in1 EMS10 (Gula Darah) 

157,0 mg/dL 

151,6 mg/dL 

99.6% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

206,0 mg/dL 

225,0 mg/dL 

90.8% 

Elvasense 3in1 EMS10 (Asam Urat) 

3,7 mg/dL 

3,9 mg/dL 

95.3% 

Link detail PDF data relawan subjek S009: Data Relawan S009 

 

Tabel L. 16 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S010 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model 

Akurasi (%) 

S010 

Tensimeter (Tekanan Darah Sistolilk) 

155,0 mmHg 

142,9 mmHg 

92.2% 

Tensimeter (Tekanan Darah Diastolik) 

85,0 mmHg 

86,4 mmHg 

98.4% 

Elvasense 3in1 EMS10 (Gula Darah) 

175,0 mg/dL 

158,7 mg/dL 

90.7% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

151,0 mg/dL 

177,4 mg/dL 

82.5% 

Elvasense 3in1 EMS10 (Asam Urat) 

4,8 mg/dL 

5,7 mg/dL 

81.3% 

Link detail PDF data relawan subjek S010: Data Relawan S010 

 

Tabel L. 17 Data Hasil Pengujian Lab vs Prediksi SVR/XGBoost Relawan S010 

Alat 

Pengujian Lab 

Hasil Prediksi Model 

Akurasi (%) 

S010 

Tensimeter (Tekanan Darah Sistolilk) 

 150,0 mmHg 

142,9 mmHg 

95.2% 

Tensimeter (Tekanan Darah Diastolik) 

 80,0 mmHg 

86,4 mmHg 

92.0% 

Elvasense 3in1 EMS10 (Gula Darah) 

 178,0 mg/dL 

158,7 mg/dL 

89.2% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

154,0 mg/dL 

183,6 mg/dL 

80.8% 

Elvasense 3in1 EMS10 (Asam Urat) 

4,6 mg/dL 

5,7 mg/dL 

76.1% 

Link detail PDF data relawan subjek S010: Data Relawan S010 

Link hasil pengujian lab S010 di Klinik Parahita: Data Relawan S010 

 

Tabel L. 18 Data Alat Medis vs Prediksi SVR/XGBoost Relawan S011 

Alat 

Alat Terstandar (Aktual) 

Hasil Prediksi Model MLP 

Akurasi (%) 

S011 

Tensimeter (Tekanan Darah Sistolilk) 

151,0 mmHg 

150,9 mmHg 

99.9% 

Tensimeter (Tekanan Darah Diastolik) 

89,0 mmHg 

88,9 mmHg 

99.9% 

Elvasense 3in1 EMS10 (Gula Darah) 

121,0 mg/dL 

131.3 mg/dL 

91.5% 

Elvasense 3in1 EMS10 (Kolesterol Total) 

245,0 mg/dL 

242,6 mg/dL 

99.0% 

Elvasense 3in1 EMS10 (Asam Urat) 

5,3 mg/dL 

5,2 mg/dL 

98.1% 

Link detail PDF data relawan subjek S011: Data Relawan S011 

 

Tabel L. 19 Hasil Deteksi Risiko Stroke per Relawan 

Subjek 

Faktor Risiko Terpenuhi 

Kategori Risiko 

S001 

Kolesterol Total Tinggi 

Rendah 

S002 

Hipertensi dan Kolesterol Total Tinggi 

Rendah 

S003 

Hipertensi, Kolesterol Total Tinggi, dan usia 75 tahun (≥ 75 tahun) 

Sedang 

S004 

Hipertensi, Kolesterol Total Tinggi, dan Riwayat Stroke Pribadi 

Tinggi 

S005 

Hipertensi, Kolesterol Total Tinggi, dan usia 

76 tahun (≥ 75 tahun) 

Sedang 

S006 

Hipertensi, Kolesterol Total Tinggi, dan usia 

75 tahun (≥ 75 tahun) 

Sedang 

S007 

Hipertensi, Kolesterol Total Tinggi, Asam Urat, Riwayat Stroke Keluarga, dan Riwayat Stroke Pribadi 

Tinggi 

S008 

Hipertensi dan Kolesterol Total Tinggi 

Rendah 

S009 

Hipertensi, Kolesterol Total Tinggi, dan usia 

80 tahun (≥ 75 tahun) 

Sedang 

S010 

Hipertensi 

Rendah 

S011 

Hipertensi, Kolesterol Total Tinggi, dan usia 80 tahun (≥ 75 tahun) 

Sedang 

 
Lampiran 1. 5 Pengembangan dan Evaluasi Model AI 

Tabel L. 20 Model Klasifikasi Prediksi Risiko Stroke (XGBoost) 

Keterangan 

Dokumentasi 

Dokumentasi saat pengembangan model AI 

 

Gambar L. 24 Dokumentasi Saat Pengembangan Model AI 

Melakukan studi dataset dan preprocessing untuk pembangunan model baseline deteksi risiko stroke. Ditemukan adanya class imbalance sehingga diperlukan penyesuaian metode atau parameter pelatihan untuk meningkatkan performa model. 

 

Gambar L. 25 Proses Data Preprocessing Untuk Model AI Gradient Boosting 

 

 

Gambar L. 26 Problem Imbalance Data pada Dataset 

Mempelajari dan menerapkan XGBoost untuk menangani class imbalance pada dataset deteksi risiko stroke. Digunakan parameter scale_pos_weight sebesar 19,52 berdasarkan proporsi kelas stroke sebesar 4,87% untuk memberikan pembobotan pada proses training. 

 

Gambar L. 27 Bukti Problem Rasio Sebaran Kelas dan Proporsi Dataset 

 

 

Gambar L. 28 Persiapan Library Xtreme Gradient Boosting (Xgboost) dan Persiapan Dataset 

 

Gambar L. 29 Rasio Pembobotan 1:19,52 Berdasarkan Proporsi Kasus Stroke 4,87% 

Menguji model tanpa pembobotan kelas dan menemukan bahwa akurasi sekitar 95% dapat memberikan gambaran menyesatkan karena model tidak mampu mendeteksi kasus stroke. Evaluasi kemudian difokuskan pada Average Precision (PR-AUC), dengan ROC-AUC, recall, dan precision sebagai metrik pendukung. Hasil menunjukkan performa deteksi kasus stroke masih kurang baik tanpa pembobotan kelas. 

 

Gambar L. 30 Hasil Prediksi Model Tanpa Algoritma Pembobotan 

Mengimplementasikan pembobotan kelas pada algoritma XGBoost menggunakan parameter scale_pos_weight untuk meningkatkan kemampuan model dalam mendeteksi kelas minoritas. Hasil pengujian menunjukkan bahwa pembobotan dengan nilai scale_pos_weight yang sesuai meningkatkan recall kelas stroke dan menghasilkan performa prediksi yang lebih baik dibandingkan model tanpa pembobotan. 

 

Gambar L. 31 Testing Algoritma Parameter dengan Pembobotan dan Tanpa Pembobotan 

 

Gambar L. 32 Grafik Hasil Perbandingan Pembobotan dan Tanpa Pembobotan 

Membandingkan performa XGBoost dan HistGradientBoosting melalui hyperparameter tuning menggunakan 5-fold cross-validation. Hasil evaluasi menunjukkan XGBoost memperoleh Average Precision lebih tinggi (0,2313) dibandingkan HistGradientBoosting (0,2281), sehingga memperkuat bahwa XGBoost dipilih sebagai algoritma model utama yang akan digunakan. 

 

Gambar L. 33 Kode dan Hasil Hyperparaneter Tuning Untuk Optimalisasi Algoritma Model 

Melakukan validasi akhir pemilihan model dengan membandingkan XGBoost dan HistGradientBoosting menggunakan validasi silang 5-fold. XGBoost memperoleh Average Precision sebesar 0,2313, lebih tinggi dibandingkan HistGradientBoosting sebesar 0,2281. XGBoost juga mendukung pembobotan kelas melalui parameter scale_pos_weight=19,55 untuk menangani class imbalance, sehingga  mulai saat ini XGBooost ditetapkan sebagai algoritma utama model deteksi risiko stroke. 

 

Gambar L. 34 Ringkasan Hasil Pemilihan Model XGBoost Untuk Deteksi Risiko Stroke 

Melakukan penyetelan threshold keputusan model menggunakan prediksi out-of-fold karena threshold bawaan 0,5 belum tentu optimal setelah penerapan scale_pos_weight. Hasil tuning memperoleh threshold optimal sebesar 0,705 dengan F1-score 0,2946. 

 

Gambar L. 35 Kode dan Grafik Penentuan Ambang Batas (Threshold) dari Model Keputusan 

Melakukan evaluasi model XGBoost  menggunakan threshold F1 terbaik sebesar 0,705. Hasil evaluasi menunjukkan recall sebesar 0,493, sehingga 38 dari 75 kasus stroke tidak terdeteksi. Kondisi tersebut menunjukkan bahwa threshold berbasis F1 belum cukup baik untuk kebutuhan deteksi risiko stroke, sehingga diperlukan optimasi lebih lanjut dengan fokus pada peningkatan recall. 

 

 
Gambar L. 36 Kode dan Grafik Hasil Evaluasi Model dengan F1 Terbaik. 

Melakukan optimasi threshold pada model XGBoost untuk meningkatkan recall deteksi risiko stroke. Setelah percobaan penurunan threshold awal menghasilkan false positive yang tinggi, dilakukan analisis hubungan recall dan false positive untuk menentukan threshold yang optimal. Diperoleh threshold 0,042 dengan peningkatan deteksi dari 37 menjadi 73 dari 75 kasus stroke, sehingga recall mencapai 97,3%. 

Gambar L. 37 Pencarian Threshold Optimal Untuk Meningkatkan Precision-RecallGambar L. 38 Grafik Pencarian Threshold Optimal Untuk Meningkatkan Presisi dan Recall 

Melakukan evaluasi akhir model XGBoost menggunakan threshold 0,042. Hasil pengujian menunjukkan bahwa model berhasil mendeteksi 73 dari 75 kasus stroke, dengan recall sebesar 97,33%, sehingga kemampuan model dalam mendeteksi kasus stroke meningkat dibandingkan evaluasi sebelumnya. 

Gambar L. 39 Hasil Deteksi Model AI: 73 dari 75 Kasus Stroke Terdeteksi dxengan Recall 97,33% 

 

 

Tabel L. 21 Model Estimasi Data Fisiologis dari Sensor Sinyal PPG Hardware (Kombinasi SVR dan XGBoost) 

No 

Keterangan 

Dokumentasi 

1 

Merancang model MLP untuk deteksi gula darah, kolesterol, asam urat, sistolik, diastolik menggunakan fitur input dari sensor yakni berupa ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p, bpm, usia, dan jenis kelamin. Merancang dan mengimplementasikan model MLP untuk mengestimasi nilai fisiologis dari sinyal PPG sebagai alternatif pengukuran invasif. Model dilatih menggunakan data kalibrasi yang tersedia. Hasilnya menunjukkan akurasi 64,1% untuk gula darah, 77,7% untuk kolesterol, dan 84,9% untuk sistolik. Performa yang masih rendah akibat keterbatasan data mendorong studi model alternatif seperti SVR dan XGBoost untuk meningkatkan estimasi pada dataset terbatas. 

 

Gambar L. 40 Hasil Pelatihan MLP pada 6 Subjek Relawan 

Gambar L. 41 Studi Literatur: SVM Lebih Unggul daripada MLP Pada Data Terbatas 

 

Gambar L. 42 Studi Literatur: SVM Lebih Unggul daripada MLP pada Data Terbatas 

 

Melakukan pengujian langsung terhadap model MLP, SVR, dan XGBoost untuk membandingkan performa estimasi lima parameter fisiologis berdasarkan data kalibrasi yang tersedia. Pengujian dilakukan terhadap kombinasi model dan set fitur pada masing-masing parameter. Hasil perbandingan menunjukkan bahwa model MLP terbaik masih memiliki performa di bawah model SVR dan XGBoost pada seluruh parameter. Berdasarkan hasil tersebut, dilanjutkan evaluasi terhadap SVR dan XGBoost sebagai kandidat model pengganti MLP dengan pendekatan pemilihan model berdasarkan masing-masing parameter fisiologis. 

Gambar L. 43 Kode Perbandingan MLP vs SVR VS XGBoost Per Parameter 

 

Gambar L. 44 Hasil Perbandingan MLP VS SVR vs XGBoost Per Parameter. 

3 

Diperolehnya hasil evaluasi model SVR dan XGBoost pada masing-masing parameter fisiologis serta tersusunnya konfigurasi model akhir berdasarkan performa training dan validasi. Ditetapkannya SVR dan XGBoost sebagai kandidat utama pengganti MLP pada sistem estimasi data fisiologis ANTARAGA. 

Gambar L. 45 Konfigurasi Akhir Model SVR dan XGBoost Pengganti MLP 

4 

Diperolehnya 3 data kalibrasi tambahan (S007–S009) sehingga jumlah subjek kalibrasi bertambah dari 6 menjadi 9 subjek. Data tambahan telah digunakan untuk training ulang model SVR dan XGBoost. 

Gambar L. 46 Kode Re-training Model Estimasi Data Fisiologis Setelah 3 Data Baru 

Gambar L. 47 Hasil Akhir Setelah Re-training 3 Data Pengujian Baru 

5 

Model estimasi data vital (SVR/XGBoost) dilatih ulang dengan menggunakan 2 data baru (total 11 subjek kalibrasi) yang terkumpul sampai 7 september 2026. Hasil menunjukkan persentase model sangat membaik dengan akurasi akhir saat ini adalah 90.61% untuk tekanan darah sistolik, 88.80% untuk tekanan darah diastolik, 89.33% untuk kolesterol, 85.21% untuk asam urat, dan 75.40% untuk gula darah. 

 

Gambar L. 48 Kode Retraining Model Estimasi Data Fisiologis (SVR/XGBoost) 

Gambar L. 49 Hasil Akhir Training Model 

 

 

Lampiran 1. 6 Integrasi Aplikasi dan Server 

Tabel L. 22 Pengembangan Backend Server (API), Cloud, dan Mobile App 

No 

Keterangan 

Dokumentasi 

1 

Dokumentasi saat pengembangan aplikasi dan server ANTARAGA. 

 

Gambar L. 50 Dokumentasi Saat Pengembangan Aplikasi dan Server ANTARAGA 

 

2 

Inisialisasi proyek untuk backend server (API). 

Gambar L. 51 Inisialisasi proyek 

3 

Desain arsitektur untuk sistem database (ERD) 

Gambar L. 52 Desain Arsitektur Untuk Sistem Database (ERD) 

4 

Membuat awalan modul API (Backend) dengan Python FastAPI: struktur modul, konfigurasi, koneksi database SQLite, dan endpoint dasar 

Gambar L. 53 Pembuatan Awalan Modul API dan Koneksi Database 

5 

Melanjutkan pengembangan API backend dengan implementasi autentikasi JWT meliputi register, login, dan otorisasi, serta pengembangan fitur manajemen profil lansia berbasis CRUD dengan validasi data, dan API lain yang dibutuhkan sudah siap pakai. 

Gambar L. 54 Kode Saat Pengembangan Fitur 

 

Gambar L. 55 Hasil Fitur yang Siap Dipakai 

6 

Melakukan inisialisasi aplikasi mobile ANTARAGA berbasis Flutter, meliputi konfigurasi proyek, instalasi dependency, penyusunan struktur modul, serta penerapan tema dan palet warna sesuai rancangan pada proposal. 

Gambar L. 56 Inisialisasi Project Flutter 

 

Gambar L. 57 Menyesuaikan Tema Aplikasi dan Warna Sesuai Desain Awal 

7 

Melakukan pengembangan antarmuka aplikasi mobile ANTARAGA dengan membangun halaman login, registrasi, profil awal, dan dashboard sesuai rancangan sistem. 

Gambar L. 58 Kode Pengembangan Halaman Antarmuka Berbagai Halaman 

8 

Melanjutkan pengembangan antarmuka aplikasi mobile ANTARAGA dengan mengimplementasikan halaman Hubungkan Perangkat, Detail Statistik Jam, Detail Statistik Harian, dan Assessment ABCD2 sesuai rancangan sistem. Seluruh antarmuka aplikasi mobile telah diselesaikan dan siap diintegrasikan dengan backend server. 

 

Gambar L. 59 Proses Koding (Pengembangan Aplikasi Lanjutan) 

9 

Mengintegrasikan model AI ke API sebagai endpoint prediksi risiko stroke agar dapat diakses aplikasi mobile, serta menyiapkan deployment menggunakan Docker. Endpoint menerima data profil pengguna dan mengembalikan probabilitas serta tingkat risiko, sedangkan Dockerfile, docker-compose, dan named volume disiapkan untuk menjaga artefak model dan database saat pembaruan serta mendukung hosting pada cloud VPS. 

Gambar L. 60 Kode Mengimplementasikan Model AI dalam API Server (backend) 

 

Gambar L. 61 Kode Docker Compose dan Dockerfile Yang Sudah Siap Untuk Deployment dan Hosting Aplikasi Keseluruhan 

10 

Menghosting backend (API) ANTARAGA pada cloud VPS, melakukan pembelian dan konfigurasi domain melalui Cloudflare, serta menyiapkan Docker dan reverse proxy Nginx agar backend dapat diakses secara publik melalui domain www.antaraga.web.id  

Gambar L. 62 Konfigurasi Cloud VPS Server dan Hosting Aplikasi 

 

Gambar L. 63 Konfigurasi Cloud Server Untuk Keamanan Data dan Server 

11 

Menguji ketahanan endpoint server terhadap input tidak lengkap dan kategori di luar data training, serta membangun sistem logging untuk mencatat akses dan kesalahan. Selain itu, menyiapkan endpoint penerimaan batch, penyangga sinyal, dan penyimpanan data mentah tiga kanal beserta nilai turunannya. 

 

Gambar L. 64 Hasil Pengujian Ketahanan Endpoint Server (API) terhadap Input Tidak Lengkap (Endpoint Berhasil Menangani Input Tidak Lengkap) 

 

 

 

Tabel L. 23 Tangkapan Layar Aplikasi Mobile ANTARAGA 

Gambar L. 65 Ikon Aplikasi ANTARAGA Ketika Terinstall di Mobile Phone 

Gambar L. 66 Splash Screen 

 

Gambar L. 67 Halaman Masuk ke Akun ANTARAGA 

 

Gambar L. 68 Halaman Daftar Akun ANTARAGA 

 

Gambar L. 69 Halaman Pengisian Data Profil Lansia (1) 

  

Gambar L. 70 Halaman Pengisian Data Profil Lansia (2) 

 

 
Gambar L. 71 Halaman Menghubungkan Lansia ke Perangkat ANTARAGA Melalui Kode Perangkat 

Gambar L. 72 Halaman Dashboard (1) 

Gambar L. 73 Halaman Dashboard (2) 

 
 

Gambar L. 74 Halaman Statistik Harian (1) 
 

Gambar L. 75 Halaman Statistik Harian (2) 
 

Gambar L. 76 Halaman Detail Statistik Harian 

 

Gambar L. 77 Halaman Detail Statistik Harian 

Gambar L. 78 Halaman Untuk Menampilkan Daftar Orang Tua yang Dipantau 

Gambar L. 79 Notifikasi Aplikasi ANTARAGA Berhasil Masuk (Lock Screen) 

 
Gambar L. 80 Notifikasi Aplikasi ANTARAGA Berhasil Masuk (Notification Panel) 

Gambar L. 81 Halaman Assesment ABCD2 (Setelah Dapat Peringatan Risiko Normal dan Tinggi) 

Gambar L. 82 Halaman Daftar Hasil Estimasi Berdasarkan Pengisian 

 

 

Lampiran 2. Tabel Penggunaan Dana Belmawa 

Rincian penggunaan dana Belmawa yang telah direalisasikan sepenuhnya untuk operasional program disajikan pada tabel berikut, dengan sisa saldo akhir sebesar Rp0. 

Tabel L. 24 Rincian Penggunaan Dana Belmawa 

BAHAN HABIS PAKAI (MAKS 60%) 

 
No 

Tanggal 

Uraian 

Jumlah Pembeli-an 

Harga Satuan (Rp) 

Satuan 

Jumlah 

 
 

1 

12 Juni 2026 

PPG Heart Rate Monitor Sensor for Arduino Analog/Digital Gravity 

2 

Rp323.000 

pcs 

Rp646.000 

 

2 

12 Juni 2026 

20mm 22mm Silicone Strap for Huawei GT 2 3 4 Samsung Galaxy Watch 7 6 5 4 Amazfit Garmin Sport Breathable Strap 

2 

Rp20.300 

pcs 

Rp40.600 

 

3 

13 Juni 2026 

Seed Studio XIAO ESP32-C3 Development Board Mini WiFi Bluetooth BLE RISC-V Type-C 
Module 

2 

Rp199.000 

pcs 

Rp398.000 

 

4 

13 Juni 2026 

Kabel Extra Soft Silicone AWG High Temperature Kabel AWG Lentur 14AWG - 30AWG AWG 14 16 18 20 22 24 2 Putih 

2 

Rp5.000 

pcs 

Rp10.000 

 

5 

13 Juni 2026 

Kabel Extra Soft Silicone AWG High Temperature, Kabel AWG Lentur 14AWG–30AWG (AWG 14/16/18/20/22/24), Merah 

2 

Rp5.000 

pcs 

Rp10.000 

 

6 

13 Juni 2026 

MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 1) 

1 

Rp575.000 

pcs 

Rp575.000 

 

7 

13 Juni 2026 

MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (pembelian 2) 

1 

Rp575.000 

pcs 

Rp575.000 

 

8 

13 Juni 2026 

Battery Li-Polymer 3.7V 950mAH 

3 

Rp90.000 

pcs 

Rp270.000 

 

9 

28 Juni 2026 

JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell Variasi 4P 

10 

Rp2.000 

pcs 

Rp20.000 

 

10 

28 Juni 2026 

JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell Variasi 2P 

10 

Rp2.000 

pcs 

Rp20.000 

 

11 

28 Juni 2026 

JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell Variasi 3P 

10 

Rp2.000 

pcs 

Rp20.000 

 

12 

2 Juli 2026 

USB Type-C Female Soket Power Charger Port Waterproof Kabel 10cm Socket PH2.0 

2 

Rp11.900 

pcs 

Rp23.800 

 

13 

2 Juli 2026 

Mini Switch Toggle Switch On/Off Saklar Senter High Quality Bahan Tembaga Murni Ujung Kaki Oval (Bukan Kotak) 

10 

Rp1.500 

pcs 

Rp15.000 

 

14 

2 Juli 2026 

TP5000 3.6V / 4.2V 1A DC 4.5V-9V Lithium Battery Charger Module 

1 

Rp20.000 

pcs 

Rp20.000 

 

15 

2 Juli 2026 

RT9013-33GB Fixed 3.3V 500mA Linear Voltage Regulators LDO SOT-23-5 WJ Richtek Technology 

5 

Rp3.405 

pcs 

Rp17.025 

 

16 

10 Juli 2026 

MAX30102 Pulse Oximeter and Heart Rate Sensor Detak Jantung Sensor 

1 

Rp27.200 

pcs 

Rp27.200 

 

17 

10 Juli 2026 

eSUN PETG Basic 3D Filament Cost Effective High Strength 3D Printing Filament - White 

2 

Rp250.000 

kg 

Rp500.000 

 

18 

10 Juli 2026 

DIODES DMP2130L-7 Mosfet P-Channel SMD3A 20V LG EBK61913701 mark MP1 

5 

Rp2.500 

pcs 

Rp12.500 

 

19 

10 Juli 2026 

SAMWHA Ferrite Bead 1000 Ohm 1K SMD 0805 CB2012GM102E Beads 

10 

Rp250 

pcs 

Rp2.500 

 

20 

10 Juli 2026 

SAMSUNG Ferrite Bead 60 Ohm SMD 1210 CIB32P600NE Beads 

10 

Rp250 

pcs 

Rp2.500 

 

21 

17 Juli 2026 

XIAO ESP32S3 Original Board IoT Development Kit - Dual Core WiFi Bluetooth 5.0 BLE Microcontroller 

1 

Rp259.000 

pcs 

Rp259.000 

 

22 

18 Juli 2026 

Resistor 0805 1M 

5 

Rp100 

pcs 

Rp500 

 

23 

18 Juli 2026 

Resistor 0805 100K 

5 

Rp100 

pcs 

Rp500 

 

24 

18 Juli 2026 

Resistor 0805 10K 

5 

Rp100 

pcs 

Rp500 

 

25 

18 Juli 2026 

Resistor 0805 6KB 

5 

Rp100 

pcs 

Rp500 

 

26 

18 Juli 2026 

AVX Type A 10µF 16V 

4 

Rp1.500 

pcs 

Rp6.000 

 

27 

18 Juli 2026 

10µF 35V SMD Capacitor 

4 

Rp1.000 

pcs 

Rp4.000 

 

28 

18 Juli 2026 

LED 3mm Diffused (Green) 

5 

Rp200 

pcs 

Rp1.000 

 

29 

29 Juli 2026 

Pembelian Hosting VPS 

4 

Rp180.000 

bulan 

Rp720.000 

 

30 

10 Agustus 2026 

Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat) Bundling 3 Box + Lancet 

1 

Rp427.635 

paket 

Rp427.635 

 

31 

2 September 

Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat) CHOL 10'S 

1 

Rp174.985 

box 

Rp174.985 

 

SubTotal (Rp) 

 

 

 

Rp4.799.745 

 

SEWA DAN JASA (MAKS 15%) 

 

No 

Tanggal 

Uraian 

Jumlah Pembeli-an 

Harga Satuan (Rp) 

Satuan 

Jumlah 

 

 

1 

22 Juli 2026 

3D Print Base Casing 

4 

Rp30.000 

pcs 

120.000 

 

2 

22 Juli 2026 

3D Print Cover Casing 

4 

Rp45.000 

pcs 

180.000 

 

3 

23 Juli 2026 

3D Print Base Casing 

2 

Rp30.000 

pcs 

60.000 

 

4 

23 Juli 2026 

3D Print Cover Casing 

2 

Rp45.000 

pcs 

90.000 

 

5 

29 Juli 2026 

Domain Registration - antaraga.web.id 

1 

Rp13.078 

paket 

13.078 

 

6 

29 Agustus 2026 

Biaya Pembuatan Akun untuk Register Aplikasi @$25 

1 

Rp452.166 

paket 

452.166 

 

SubTotal (Rp) 

 

 

 

915.244 

 

TRANSPORTASI LOKAL (MAKS 30%) 

 

No 

Tanggal Pengeluaran 

Uraian 

Jumlah Pembeli-an 

Harga Satuan (Rp) 

Satuan 

Jumlah 

 

 

1 

12 Juni 2026 

Biaya Ongkos Kirim - PPG Heart Rate Monitor Sensor for Arduino Analog/Digital Gravity 

1 

Rp21.000 

transaksi 

Rp21.000 

 

2 

12 Juni 2026 

Biaya Asuransi Pengiriman - PPG Heart Rate Monitor Sensor for Arduino Analog/Digital Gravity 

1 

Rp2.300 

transaksi 

Rp2.300 

 

3 

12 Juni 2026 

Biaya Jasa Aplikasi - PPG Heart Rate Monitor Sensor for Arduino Analog/Digital Gravity 

1 

Rp1.000 

transaksi 

Rp1.000 

 

4 

12 Juni 2026 

Biaya Layanan - PPG Heart Rate Monitor Sensor for Arduino Analog/Digital Gravity 

1 

Rp1.000 

transaksi 

Rp1.000 

 

5 

12 Juni 2026 

Biaya Ongkos Kirim - 20mm 22mm Silicone Strap for Huawei GT 2 3 4 Samsung Galaxy Watch 7 6 5 4 Amazfit Garmin Sport Breathable Strap 

1 

Rp6.500 

transaksi 

Rp6.500 

 

6 

12 Juni 2026 

Biaya Layanan - 20mm 22mm Silicone Strap for Huawei GT 2 3 4 Samsung Galaxy Watch 7 6 5 4 Amazfit Garmin Sport Breathable Strap 

1 

Rp2.000 

transaksi 

Rp2.000 

 

7 

13 Juni 2026 

Biaya Layanan pada pembelian Seeed Studio XIAO ESP32-C3 Development Board Mini WiFi Bluetooth BLE RISC-V Type-C Module, dan Kabel Extra Soft Silicone AWG High Temperature, Kabel AWG Lentur 14AWG–30AWG (AWG 14/16/18/20/22/24), Hitam dan Merah 

1 

Rp2.786 

transaksi 

Rp2.786 

 

8 

13 Juni 2026 

Biaya Ongkir (Ongkos Kirim) pada pembelian DFRobot Fermion: MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 1) 

1 

Rp29.500 

transaksi 

Rp29.500 

 

9 

13 Juni 2026 

Biaya Asuransi Pembelian - MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 1) 

1 

Rp3.700 

transaksi 

Rp3.700 

 

10 

13 Juni 2026 

Biaya Layanan - MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 1) 

1 

Rp1.000 

transaksi 

Rp1.000 

 

11 

13 Juni 2026 

Biaya Ongkir (Ongkos Kirim) pada pembelian DFRobot Fermion: MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 2) 

1 

Rp29.500 

transaksi 

Rp29.500 

 

12 

13 Juni 2026 

Biaya Asuransi Pembelian - MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 2) 

1 

Rp3.700 

transaksi 

Rp3.700 

 

13 

13 Juni 2026 

Biaya Layanan dalam Pembelian MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 2) 

1 

Rp1.000 

transaksi 

Rp1.000 

 

14 

13 Juni 2026 

Biaya Ongkos Kirim - Baterai Li-Po 3,7V 950mAh, 063443a 

1 

Rp8.000 

transaksi 

Rp8.000 

 

15 

13 Juni 2026 

Asuransi Pengiriman pada Pembelian Baterai Li-Po 3,7V 950mAh 

1 

Rp600 

transaksi 

Rp600 

 

16 

13 Juni 2026 

Biaya Layanan - Baterai Li-Po 3,7V 950mAh, 063443 

1 

Rp1.000 

transaksi 

Rp1.000 

 

17 

28 Juni 2026 

Biaya Ongkir (Ongkos Kirim) pembelian JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell 

1 

Rp8.000 

transaksi 

Rp8.000 

 

18 

28 Juni 2026 

Biaya Layanan pada Pembelian JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell 

1 

Rp2.000 

transaksi 

Rp2.000 

 

19 

2 Juli 2026 

Biaya Ongkir (Ongkos Kirim) dalam Pembelian USB Type-C Female Soket Power Charger Port Waterproof Kabel 10cm Socket PH2.0 

1 

Rp8.000 

transaksi 

Rp8.000 

 

20 

2 Juli 2026 

Biaya Layanan dalam Pembelian USB Type-C Female Soket Power Charger Port Waterproof Kabel 10cm Socket PH2.0 

1 

Rp2.000 

transaksi 

Rp2.000 

 

21 

2 Juli 2026 

Biaya Ongkos Kirim - Mini Switch/Toggle Switch On/Off Saklar Senter, High Quality, Bahan Tembaga Murni, Ujung Kaki Oval (Bukan Kotak) 

1 

Rp8.000 

transaksi 

Rp8.000 

 

22 

2 Juli 2026 

Biaya Layanan dalam Pembelian Mini Switch/Toggle Switch On/Off Saklar Senter, High Quality, Bahan Tembaga Murni, Ujung Kaki Oval (Bukan Kotak) 

1 

Rp2.000 

transaksi 

Rp2.000 

 

23 

2 Juli 2026 

Biaya Ongkir (Ongkos Kirim) dalam Pembelian TP5000 3,6V/4,2V 1A DC 4,5V–9V Lithium Battery Charger Module 

1 

Rp8.000 

transaksi 

Rp8.000 

 

24 

2 Juli 2026 

Biaya Layanan dalam Pembelian TP5000 3,6V/4,2V 1A DC 4,5V–9V Lithium Battery Charger Module 

1 

Rp2.000 

transaksi 

Rp2.000 

 

25 

2 Juli 2026 

Biaya Layanan - RT9013-33GB Fixed Linear Voltage Regulator 3,3V 500mA, LDO, SOT-23-5, WJ Richtek Technology 

1 

Rp2.000 

transaksi 

Rp2.000 

 

26 

10 Juli 2026 

Biaya Layanan - MAX30102 Pulse Oximeter and Heart Rate Sensor 

1 

Rp2.000 

transaksi 

Rp2.000 

 

27 

10 Juli 2026 

Biaya Ongkos Kirim - eSUN PETG Basic 3D Printing Filament, Cost Effective, High Strength 

1 

Rp31.000 

transaksi 

Rp31.000 

 

28 

10 Juli 2026 

Biaya Layanan - eSUN PETG Basic 3D Printing Filament, Cost Effective, High Strength 

1 

Rp1.000 

transaksi 

Rp1.000 

 

29 

10 Juli 2026 

Biaya Layanan Paket Diodes DMP2130L-7 MOSFET P-Channel SMD 3A 20V, LG EBK61913701, Mark MP1 + Samwha Ferrite Bead 1000 Ohm (1K), SMD 0805, CB2012GM102E + Samsung Ferrite Bead 60 Ohm, SMD 1210, CIB32P600NE 

1 

Rp1.500 

transaksi 

Rp1.500 

 

30 

13 Juli 2026 

Biaya Observasi Lapangan dan Pengujian Alat - Ethical Clearance di FKM Rumah Sakit Airlangga 

1 

Rp100.000 

paket 

Rp100.000 

 

31 

17 Juli 2026 

Biaya Ongkos Kirim - XIAO ESP32S3 Original Board IoT Development Kit - Dual Core WiFi Bluetooth 5.0 BLE Microcontroller 

1 

Rp21.500 

transaksi 

Rp21.500 

 

32 

17 Juli 2026 

Biaya Asuransi Pengiriman - XIAO ESP32S3 Original Board IoT Development Kit - Dual Core WiFi Bluetooth 5.0 BLE Microcontroller 

1 

Rp1.700 

transaksi 

Rp1.700 

 

33 

17 Juli 2026 

Biaya Layanan - XIAO ESP32S3 Original Board IoT Development Kit - Dual Core WiFi Bluetooth 5.0 BLE Microcontroller 

1 

Rp1.000 

transaksi 

Rp1.000 

 

34 

18 Juli 2026 

Biaya Transportasi Pengiriman Filament ke Jasa 3D Print Auto Forge menggunakan Gosend 

1 

Rp42.000 

transaksi 

Rp42.000 

 

35 

22 Juli 2026 

Biaya Transportasi Pengiriman Hasil 3D Print dari Jasa 3D Print Auto Forge menuju PENS menggunakan GoSend 

1 

Rp41.500 

transaksi 

Rp41.500 

 

36 

23 Juli 2026 

Biaya Transportasi Pengiriman Hasil 3D Print Terbaru (yang telah direvisi dimensi desainnya) dari Jasa 3D Print Auto Forge menuju PENS menggunakan GoSend 

1 

Rp42.300 

transaksi 

Rp42.300 

 

37 

29 Juli 2026 

Biaya Layanan - MAX30102 Pulse Oximeter and Heart Rate Sensor 

1 

Rp2.000 

transaksi 

Rp2.000 

 

38 

6 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 2 dari PENS menuju Lokasi Relawan (Relawan 2 & 3 berada di satu tempat) 

1 

Rp28.500 

transaksi 

Rp28.500 

 

39 

6 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 2 dari Lokasi Relawan (Relawan 2 & 3 berada di satu tempat) menuju PENS 

1 

Rp31.000 

transaksi 

Rp31.000 

 

40 

10 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 3 dari PENS menuju Lokasi Relawan 4 

1 

Rp29.500 

transaksi 

Rp29.500 

 

41 

10 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 3 dari Lokasi Relawan 4 menuju Lokasi Relawan 5 

1 

Rp34.500 

transaksi 

Rp34.500 

 

42 

10 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 2 dari Lokasi Relawan 5 menuju PENS 

1 

Rp28.500 

transaksi 

Rp28.500 

 

43 

10 Agustus 2026 

Biaya Ongkos Kirim - Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat) Bundling 3 Box + Lancet 

1 

Rp35.000 

transaksi 

Rp35.000 

 

44 

10 Agustus 2026 

Biaya Layanan Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat) Bundling 3 Box + Lancet 

1 

Rp4.000 

transaksi 

Rp4.000 

 

45 

14 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 4 dari PENS menuju Lokasi Relawan 6 

1 

Rp37.000 

transaksi 

Rp37.000 

 

46 

14 Agustus 2026 

Biaya Transportasi Pengujian ANTARAGA 4 dari Lokasi Relawan 6 menuju PENS 

1 

Rp35.000 

transaksi 

Rp35.000 

 

47 

2 September 

Biaya Transportasi Pengujian ANTARAGA 5 dari PENS menuju Lokasi Relawan 7 

1 

Rp23.000 

transaksi 

Rp23.000 

 

48 

2 September 

Biaya Transportasi Pengujian ANTARAGA 5 dari Lokasi Relawan 7 menuju PENS 

1 

Rp23.500 

transaksi 

Rp23.500 

 

49 

2 September 

Biaya Layanan - Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat), CHOL 10's 

1 

Rp1.000 

transaksi 

Rp1.000 

 

50 

2 September 

Biaya Ongkir - Strip Alat Cek 3-in-1 Elvasense (Gula Darah/Kolesterol/Asam Urat), CHOL 10's 

1 

Rp21.000 

transaksi 

Rp21.000 

 

51 

7 September 

Cek Lab Lansia di Klinik Parahita 

1 

Rp353.000 

transaksi 

Rp353.000 

 

52 

7 September 

Biaya Transportasi Cek Lab Lansia (Lokasi Relawan 11 ke Klinik Parahita) 

1 

Rp31.500 

transaksi 

Rp31.500 

 

53 

7 September 

Biaya Transportasi Cek Lab Lansia (Klinik Parahita ke Lokasi Relawan 11) 

1 

Rp32.000 

transaksi 

Rp32.000 

 

SubTotal (Rp) 

 

 

 

Rp1.192.086 

 

LAIN-LAIN (MAKS 15%) 

 

No 

Tanggal 

Uraian 

Jumlah Pembeli-an 

Harga Satuan (Rp) 

Satuan 

Jumlah 

 

 

1 

6 Juni 2026 

Periklanan Konten 1 

1 

Rp166.500 

paket 

166.500 

 

2 

4 Juli 2026 

Periklanan Konten 2 

1 

Rp165.482 

paket 

165.482 

 

3 

29 Juli 2026 

Kerusakan Komponen - MAX30102 Pulse Oximeter and Heart Rate Sensor Detak Jantung Sensor 

2 

Rp27.200 

pcs 

54.400 

 

4 

4 Agustus 2026 

Pencetakan Protokol Ethical Clearance dan Informed Consent 

1 

Rp40.500 

paket 

40.500 

 

5 

29 Agustus 2026 

Periklanan Konten 3 

1 

Rp166.043 

paket 

166.043 

 

SubTotal (Rp) 

 

 

 

592.925 

 

Total Keseluruhan (Rp) 

 

 

 

7.500.000 

 

Jumlah Pendanaan (Rp) 

 

 

 

7.500.000 

 

Saldo (Rp) 

 

 

 

0 

 

 

Lampiran 3. Tabel Penggunaan Dana In Kind dari PENS 

Tabel berikut memuat rincian penggunaan dana tambahan (in kind) senilai Rp2.000.000 yang difasilitasi oleh Politeknik Elektronika Negeri Surabaya (PENS) untuk mendukung optimalisasi riset dan pengembangan. 

Tabel L. 25 Penggunaan Dana In Kind 

SEWA DAN JASA 

 
No 

Uraian 

Jumlah Pembeli-an 

Harga Satuan (Rp) 

Jumlah 

Dokumentasi 

 
 

1 

Penggunaan Lab IT C306* 

4 

Rp450.000 

Rp1.800.000 

 

 

SubTotal (Rp) 

 

 

1.800.000 

 

 

LAIN-LAIN 

 

No. 

Uraian 

Jumlah Pembelian 

Harga Satuan (Rp.) 

Jumlah 

Dokumentasi 

 

1 

Pengajuan Hak Cipta* 

1 

Rp200.000 

Rp200.000 

 

 

SubTotal (Rp) 

Rp200.000 

 

 

Total Keseluruhan (Rp) 

Rp2.000.000 

 

 

Lampiran 4. Sampling Bukti Pengeluaran 

Seluruh rekam jejak pelaksanaan kegiatan yang telah dilakukan secara berkala dirangkum selengkapnya pada tabel catatan harian berikut. 

Tabel L. 26 Bukti Pengeluaran (Sampling) 

Tanggal 

Keterang- 

an 

Harga Satuan 

Jumlah 

Total 

Bukti 

6 Juni 2026 

Periklanan Konten 1 

Rp166.500 

1 

Rp166.500 

 

13 Juni 2026 

MAX30102 Heart Rate and Oximeter Sensor (Breakout) - SEN0518 (Pembelian 1) 

Rp575.000 

1 

Rp575.000 

 

28 Juni 2026 

JST SH 1mm 1.0mm Head Connector Konektor Pin Leads Housing Shell Variasi 4P, 3P, 2P 

Rp2.000 

30 

Rp60.000 

 

13 Juli 2026 

Biaya Pengajuan Ethical Clearance di FKM Rumah Sakit Airlangga 

Rp100.000 

1 

Rp100.000 

 

29 Juli 2026 

Biaya Pembuatan Akun untuk Register Aplikasi @$25 

Rp452.166 

1 

Rp452.166 

 

 

29 Agustus 2026 

Periklanan Konten 3 

Rp166.043 

1 

Rp166.043 

 

 

Lampiran 5. Bukti Logbook Kegiatan 

Seluruh rekam jejak pelaksanaan kegiatan yang telah dilakukan secara berkala dirangkum selengkapnya pada tabel catatan harian berikut. 

Tabel L. 27 Rekam Jejak Pelaksanaan Kegiatan (Sampling) 

Tanggal Pelaksanaan 

Kegiatan 

Waktu Pelaksanaan (menit) 

Dokumentasi 

23 Mei 2026 

Rapat Perdana dan Briefing Awal setelah Pengumuman Lolos Pendanaan 

180 

 

17 Juni 2026 

Weekly Meeting dengan Dosen Pendamping 

300 

 

12 Juli 2026 

Pengujian Performa Hardware Multi-Sensor, Migrasi Mikrokontroler ke XIAO ESP32-S3, Implementasi Parameter XGBoost, Finalisasi Fitur Aplikasi Mobile, dan Pemetaan Lokasi Kunjungan 

240 

 

25 Juli 2026 

Integrasi Komponen Hardware ke Casing 3D & Perbaikan Modul Charging TP5000, Uji Ketahanan (Robustness) & Error Handling API Prediksi AI, serta Revisi Draf Laporan Kemajuan Pasca-Monev Internal 2 

240 

 

6 Agustus 2026 

Pengujian Kedua Smartband ANTARAGA Terhadap Relawan, Pengujian Alur Data End-to-End, dan Pengumpulan Data Sinyal 

180 

 

7 Agustus 2026 

Konsultasi dan Validasi Pendekatan Sistem ANTARAGA Bersama Dokter Spesialis Saraf 

120 

 

7 September 2026 

Melanjutkan Pembuatan Laporan Kemajuan dan Pengujian 6 

420 

 

 

 

Lampiran 6. Sertifikat Hak Cipta 

Sebagai bentuk pelindungan kekayaan intelektual atas inovasi yang telah dikembangkan, berikut dilampirkan Surat Pencatatan Ciptaan yang diterbitkan oleh Kementerian Hukum dengan Nomor Permohonan EC002026157207 tanggal 28 Agustus 2026 dan Nomor Pencatatan 001449089 sebagai bukti perolehan Hak Cipta (HKI) untuk program komputer ANTARAGA. 

 

 

 

Lampiran 7. Ethical Clearance 

Berikut adalah sertifikat Ethical Clearance yang diterbitkan oleh KEPK FKM Universitas Airlangga pada 23 Juli 2026 lalu sebagai bukti kelayakan etik atas prosedur pengujian prototipe ANTARAGA yang melibatkan partisipasi relawan manusia. 

 

Lampiran 8. Informed Consent 

Sebagai bukti pemenuhan etika pengujian, berikut dilampirkan salah satu dokumen Informed Consent yang telah disetujui dan ditandatangani oleh relawan. Dokumen Informed Consent selengkapnya dari seluruh subjek uji dapat diakses melalui tautan berikut: Informed Consent Seluruh Relawan 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

Lampiran 9. Draft Artikel Ilmiah 

Berikut merupakan draf artikel ilmiah hasil pengembangan prototipe ANTARAGA yang berjudul “A Pre-Hospital Early Warning System for Ischemic Stroke Risk Based on Multi-Wavelength PPG and an XGBoost Algorithm”. [CATATAN TIM: ekspor ulang dari `artikel-jaee.md` versi terbaru sebelum submit — lihat 0.2 poin 7 di atas berkas ini.] Draf naskah ini telah disusun dan disesuaikan dengan pedoman penulisan dari Journal of Applied Electrical Engineering (JAEE). 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 

 