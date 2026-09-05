# LOGBOOK KEGIATAN HARIAN
## PKM-KC: ANTARAGA - Smartband Deteksi Risiko Stroke Berbasis PPG dan Kecerdasan Buatan

| | |
|---|---|
| **Nama** | Ally |
| **Peran dalam Tim** | Hardware Engineer · Firmware Developer · Signal Processing |
| **Periode** | 23 Mei 2026 - 25 September 2026 |

---

> **Catatan:** berkas ini memuat entri yang **belum terisi** pada logbook tim (CSV).
> Entri yang sudah terisi di CSV tidak diulang di sini.

---

## 6 Agustus 2026 - Pengujian 2 Smartband ANTARAGA

**Kegiatan:**
Mendampingi pengujian smartband kedua terhadap relawan, dengan fokus pada sisi perangkat keras: memastikan sensor terpasang benar, kualitas sinyal memadai, dan perangkat mengirim data tanpa terputus selama sesi berlangsung.

**Hasil:**
- Pemasangan smartband pada dua relawan, dengan penyesuaian kekencangan tali agar sensor menempel rapat tanpa menekan pembuluh darah
- Pemantauan kualitas sinyal secara langsung lewat dashboard: memeriksa perfusi inframerah berada di rentang wajar dan penanda SQI tidak menunjukkan artefak gerak
- Pengamatan daya tahan baterai selama sesi perekaman berlangsung
- **Kendala yang ditemukan**: sinyal kanal hijau kerap terganggu bila posisi pergelangan berubah, sehingga posisi perekaman perlu dijaga tetap selama akuisisi
- Diperoleh 2 data kalibrasi yang lolos pemeriksaan mutu sinyal
- Catatan diteruskan ke tim untuk penyempurnaan protokol pengambilan data

📸 **Bukti yang perlu dilampirkan:**
- `ALLY_pemasangan smartband pada relawan.png` - foto pemasangan alat
- `ALLY_pemantauan kualitas sinyal saat perekaman.png` - dashboard saat sesi berlangsung
- `ALLY_kondisi perangkat setelah sesi.png` - kondisi alat dan sisa daya baterai

---

# AGUSTUS 2026

---

## 2 Agustus 2026 - Pengujian Pembacaan BPM dan Analisis Sinyal (180 menit)

**Kegiatan:**
Menguji pembacaan BPM pada perangkat dan menganalisis mutu sinyal ketiga kanal, bersamaan dengan pemindahan algoritma analisis ke sisi server.

**Hasil:**
- Pengujian pembacaan BPM firmware dibandingkan hasil perhitungan di server, untuk memastikan keduanya sepakat
- Analisis mutu sinyal ketiga kanal: perfusi, amplitudo denyut, dan tingkat derau
- **Kendala**: kanal hijau menunjukkan perfusi jauh di atas rentang wajar, menandakan sinyalnya sudah AC-coupled di perangkat sehingga nilai DC-nya tidak mencerminkan penyerapan cahaya
- Temuan diteruskan ke tim perangkat lunak sebagai bahan penelusuran lanjutan
- Penyesuaian lebar pita filter untuk menekan artefak gerakan

📸 `ALLY_pengujian pembacaan bpm.png`, `ALLY_analisis mutu tiga kanal.png`

---

## 5 Agustus 2026 - Penyiapan Perangkat untuk Sesi Kalibrasi (180 menit)

**Kegiatan:**
Menyiapkan smartband agar siap dipakai perekaman sesi kalibrasi, mencakup pemeriksaan sensor, pengisian daya, dan penyesuaian firmware agar pengiriman data stabil selama sesi berlangsung.

**Hasil:**
- Pemeriksaan ketiga kanal sensor: MAX30102 (merah dan inframerah) serta SEN0203 (hijau) membaca normal
- Pengisian daya penuh dan pengukuran sisa kapasitas setelah pemakaian percobaan
- Penyesuaian firmware agar batch tetap terkirim saat sinyal WiFi melemah, dengan penyimpanan sementara di penyangga
- Penyiapan dua unit smartband agar sesi dapat berjalan paralel bila ada dua subjek sekaligus
- **Kendala**: tali pengikat terlalu longgar pada pergelangan berukuran kecil, sehingga disiapkan pengganjal agar sensor tetap menempel rapat

📸 `ALLY_pemeriksaan tiga kanal sensor.png`, `ALLY_penyiapan dua unit smartband.png`

---

## 14 Agustus 2026 - Dokumentasi Teknis Perangkat Keras untuk Berkas HKI (180 menit)

**Kegiatan:**
Menyusun dokumentasi teknis sisi perangkat keras untuk melengkapi berkas pendaftaran HKI, mencakup skematik rangkaian, tata letak PCB, dan rancangan casing.

**Hasil:**
- Penyusunan gambar skematik rangkaian beserta keterangan tiap blok fungsi: catu daya, sensor, mikrokontroler, dan indikator
- Penyusunan gambar tata letak PCB dengan penandaan jalur utama
- Dokumentasi rancangan casing beserta ukuran dan bahan yang dipakai
- Penyusunan daftar komponen lengkap beserta spesifikasinya
- Berkas diserahkan ke penanggung jawab penyusunan dokumen HKI

📸 `ALLY_skematik rangkaian untuk hki.png`, `ALLY_tata letak pcb.png`, `ALLY_rancangan casing.png`

---

## 16 Agustus 2026 - Analisis Sinyal Empat Sesi dan Penyusunan Bagian Hardware (450 menit)

**Kegiatan:**
Mengolah data hasil empat sesi pengujian yang sudah terkumpul dari sisi perangkat keras, lalu menyusun bagian perangkat keras pada laporan kemajuan. Hari ini tidak ada perekaman baru; seluruh waktu dipakai menelaah rekaman yang sudah ada dan menuliskan temuannya.

**Hasil - karakterisasi sinyal antar sesi:**
- Peninjauan mutu sinyal seluruh rekaman dari sesi pertama sampai keempat: perfusi inframerah, amplitudo denyut, dan tingkat derau tiap subjek
- Pembandingan perilaku sensor pada subjek dengan usia dan kondisi kulit berbeda
- **Temuan**: perfisi inframerah tiap subjek berkisar 0,74 sampai 1,77 permil, seluruhnya di rentang PPG normal, sehingga mutu rekaman merah dan inframerah dinyatakan memadai
- **Temuan kedua**: satu rekaman menunjukkan rasio merah terhadap inframerah menyimpang jauh dari subjek lain, menandakan posisi atau kontak sensor berbeda saat perekaman itu; direkomendasikan diulang pada sesi berikutnya

**Hasil - analisis ketahanan daya:**
- Penggabungan catatan penurunan daya baterai dari keempat sesi menjadi satu grafik
- Perhitungan perkiraan lama pakai pada pengiriman data berkelanjutan
- Pencatatan pengaruh kekuatan sinyal jaringan terhadap konsumsi daya

**Hasil - penyusunan laporan:**
- Penulisan bagian perangkat keras pada laporan kemajuan: rancangan rangkaian, analisis manajemen daya, dan hasil karakterisasi sinyal
- Penyusunan daftar kendala perangkat keras dalam bentuk rantai masalah sampai penyelesaian, mulai dari kegagalan step down sampai penggantian mikrokontroler
- Penyiapan gambar skematik dan tata letak PCB dengan keterangan agar dapat dibaca pemeriksa non-teknis

📸 `ALLY_karakterisasi sinyal empat sesi.png`, `ALLY_temuan rasio merah inframerah menyimpang.png`, `ALLY_grafik ketahanan baterai.png`, `ALLY_laporan bagian hardware.png`

---

## 20 Agustus 2026 - Workshop Internal Teknis Pengajuan Hak Cipta (450 menit)

**Kegiatan:**
Mengikuti Workshop Internal Teknis Pengajuan Hak Cipta, dengan perhatian pada bagian perlindungan atas rancangan perangkat keras.

**Hasil:**
- Memahami pembedaan perlindungan: hak cipta untuk program komputer, sedangkan rancangan rangkaian dan bentuk produk memakai jalur perlindungan berbeda
- Pencatatan berkas yang perlu disiapkan dari sisi perangkat keras
- Penetapan bagian rancangan yang layak ditonjolkan sebagai kebaruan: penggabungan tiga kanal panjang gelombang dalam satu perangkat pergelangan

📸 `ALLY_workshop hak cipta.png`, `ALLY_catatan perlindungan rancangan hardware.png`

---

## 23 Agustus 2026 - Finalisasi Perangkat Keras dan Penyusunan Laporan Bagian Hardware (360 menit)

**Kegiatan:**
Merapikan perangkat keras ke kondisi siap peragaan dan menyusun bagian perangkat keras pada laporan kemajuan.

**Hasil:**
- Perapian penyolderan dan pengencangan sambungan agar perangkat tidak terganggu saat dibawa berpindah
- Pemeriksaan menyeluruh: sensor, indikator, tombol, port pengisian daya, dan penyambungan WiFi
- Penyusunan bagian laporan: rancangan rangkaian, analisis manajemen daya, hasil karakterisasi sinyal, dan kendala yang ditemui beserta penyelesaiannya
- Pendataan kendala perangkat keras berbentuk rantai masalah sampai penyelesaian, mulai dari kegagalan step down sampai penggantian mikrokontroler

📸 `ALLY_perangkat keras siap peragaan.png`, `ALLY_laporan bagian hardware.png`

---

## 26 Agustus 2026 - Workshop Teknik Presentasi PKP2 (180 menit)

**Kegiatan:**
Mengikuti Workshop Teknik Presentasi PKP2 dan menyiapkan bagian perangkat keras yang akan dibawakan.

**Hasil:**
- Penyusunan kerangka pemaparan sisi perangkat keras: rancangan, pengujian, dan hasil karakterisasi
- Penyiapan alat peraga fisik yang akan dibawa saat penilaian
- Catatan dari pemateri: peragaan perangkat lebih meyakinkan daripada sekadar gambar, sehingga alat disiapkan dalam kondisi siap nyala

📸 `ALLY_workshop presentasi.png`, `ALLY_alat peraga disiapkan.png`

---

## 28 Agustus 2026 - Asistensi Laporan Kemajuan Bagian Perangkat Keras (360 menit)

**Kegiatan:**
Mengasistensikan bagian perangkat keras pada laporan kemajuan ke dosen pendamping.

**Hasil:**
- Pemaparan capaian sisi perangkat keras beserta bukti pengujian
- Pembahasan cara menyajikan kendala teknis agar terbaca sebagai proses perbaikan, bukan kegagalan
- Penerapan revisi yang diminta pada bagian analisis manajemen daya

*(Catatan masukan dosen perlu dilengkapi sesuai asistensi yang sebenarnya.)*

📸 `ALLY_asistensi bagian hardware.png`

---

## 29 Agustus 2026 - Penyiapan Bahan Visual Perangkat untuk Konten (300 menit)

**Kegiatan:**
Menyiapkan bahan visual sisi perangkat keras untuk konten media sosial ketiga.

**Hasil:**
- Pemotretan perangkat dari berbagai sudut dalam kondisi terpasang lengkap
- Perekaman peragaan pemakaian: memasang smartband di pergelangan sampai indikator menyala
- Penyiapan gambar perbandingan purwarupa awal dengan perangkat versi akhir
- Bahan diserahkan ke penanggung jawab konten

📸 `ALLY_pemotretan perangkat untuk konten.png`, `ALLY_peragaan pemakaian smartband.png`

---

## 30 Agustus 2026 - Pendampingan Pengujian 5 Smartband (300 menit)

**Kegiatan:**
Mendampingi pengujian smartband kelima dari sisi perangkat keras.

**Hasil:**
- Penyiapan perangkat sebelum sesi: pemeriksaan sensor, pengisian daya penuh, pemeriksaan sambungan jaringan di lokasi
- Pemantauan mutu sinyal tiap perekaman
- Pencatatan perilaku perangkat selama sesi berlangsung

*(Jumlah subjek dan kendala yang ditemukan perlu dilengkapi sesuai hasil sesi.)*

📸 `ALLY_penyiapan perangkat sesi kelima.png`, `ALLY_pemantauan sinyal sesi kelima.png`

---

## 2 September 2026 - Pendampingan Pengujian 5 Smartband (- menit)

**Kegiatan:**
Mendampingi pengujian smartband kelima dari sisi perangkat keras.

**Narasi & Indikator Capaian:**
Mendampingi jalannya pengujian kelima smartband ANTARAGA dari sisi perangkat keras, memastikan sensor terpasang dengan benar pada relawan baru, memeriksa mutu sinyal ketiga kanal selama perekaman, serta memantau kondisi baterai agar pengiriman data tidak terputus di tengah sesi. Hasil pemeriksaan menunjukkan sinyal merah dan inframerah tetap berada pada rentang perfusi normal, konsisten dengan sesi-sesi sebelumnya.

Indikator capaian: terverifikasinya mutu sinyal perangkat keras pada pengujian kelima, serta terjaminnya kelengkapan sinyal mentah tiga kanal untuk keperluan pelatihan model MLP.

📸 `ALLY_pendampingan pengujian kelima.png`, `ALLY_pemantauan mutu sinyal sesi kelima.png`

---

## 5 September 2026 - Pendampingan Penambahan Data Kalibrasi (- menit)

**Kegiatan:**
Mendampingi penambahan dua data kalibrasi dari pengujian laboratorium dan alat pembanding terstandar, sekaligus menyempurnakan bagian perangkat keras pada laporan kemajuan.

**Narasi & Indikator Capaian:**
Mendampingi sesi tambahan pengujian keenam yang menghasilkan dua data kalibrasi baru, satu dari hasil pemeriksaan laboratorium dan satu dari alat ukur pembanding terstandar, guna memastikan mutu sinyal tetap terjaga pada penambahan data di luar jadwal reguler. Selain itu, menyempurnakan bagian perangkat keras pada draf laporan kemajuan berdasarkan masukan tim.

Indikator capaian: bertambahnya dua data kalibrasi yang terverifikasi mutu sinyalnya, serta tersempurnakannya bagian perangkat keras pada laporan kemajuan.

📸 `ALLY_penambahan data kalibrasi lab dan standar.png`, `ALLY_penyempurnaan bagian hardware laporan.png`

---
