# DETAILING TIM TEKNIS - ALLY

**Peran:** Hardware Engineer · Firmware Developer · Signal Processing
**Periode:** 27 Mei 2026 sampai 2 September 2026
**Program:** PKM-KC ANTARAGA - Smartband Deteksi Risiko Stroke Berbasis PPG dan Kecerdasan Buatan

> **Cara memeriksa bukti:** seluruh tangkapan layar dan foto dokumentasi tersimpan di Google Drive tim, tertata dalam folder menurut tanggal pengerjaan. Tiap bagian di bawah mencantumkan tanggal foldernya.

---

## Daftar Isi

1. [Tahap 1 - Studi Sinyal dan Rancangan Awal](#tahap-1--studi-sinyal-dan-rancangan-awal)
2. [Tahap 2 - Manajemen Daya](#tahap-2--manajemen-daya)
3. [Tahap 3 - Pengujian Sensor dan Kendala Komponen](#tahap-3--pengujian-sensor-dan-kendala-komponen)
4. [Tahap 4 - Penggantian Mikrokontroler](#tahap-4--penggantian-mikrokontroler)
5. [Tahap 5 - Fabrikasi PCB](#tahap-5--fabrikasi-pcb)
6. [Tahap 6 - Desain dan Cetak Casing](#tahap-6--desain-dan-cetak-casing)
7. [Tahap 7 - Firmware Utama dan Konektivitas](#tahap-7--firmware-utama-dan-konektivitas)
8. [Tahap 8 - Kalibrasi dan Pengujian Lapangan](#tahap-8--kalibrasi-dan-pengujian-lapangan)
9. [Ringkasan Kendala dan Penyelesaiannya](#ringkasan-kendala-dan-penyelesaiannya)
10. [Kesimpulan Capaian](#kesimpulan-capaian)

---

# Tahap 1 - Studi Sinyal dan Rancangan Awal

**Periode: 27 Mei sampai 7 Juni 2026**

## 27 Mei 2026 - Studi Literatur Pengolahan Sinyal

Studi literatur difokuskan pada sisi pengolahan sinyal sensor, mencakup teknik prapemrosesan, algoritma Signal Quality Index, dan ekstraksi fitur PWA dari data wearable berbasis PPG multi panjang gelombang.

**Hasil - rantai pengolahan sinyal yang ditetapkan:**

| Tahap | Metode | Alasan pemilihan |
|---|---|---|
| Prapemrosesan | Bandpass Butterworth 0,5 sampai 5 Hz | Membuang pergeseran garis dasar dan derau frekuensi tinggi |
| Penilaian mutu | Signal Quality Index | Menolak rekaman yang tidak layak sebelum diolah |
| Ekstraksi fitur | Analisis PWA lewat turunan kedua (APG) | Titik a sampai e pada APG membawa informasi kekakuan pembuluh |

**Keputusan penting:** sensor dipilih tiga panjang gelombang sekaligus (hijau 525 nm, merah 660 nm, inframerah 880 nm), bukan satu. Tiap panjang gelombang menembus kedalaman jaringan yang berbeda, sehingga informasinya saling melengkapi.

> 📎 **Bukti:** `ALLY_ringkasan studi literatur pengolahan sinyal.png`, `ALLY_rancangan rantai pemrosesan sinyal.png`
> 🗂️ **Google Drive:** folder tanggal **27 Mei 2026**

## 31 Mei 2026 - Penyiapan Perkakas

Instalasi perangkat lunak pendukung: CAD untuk desain mekanik, EDA untuk skematik dan PCB, serta dependensi firmware.

> 📎 **Bukti:** `ALLY_perkakas cad eda terpasang.png`
> 🗂️ **Google Drive:** folder tanggal **31 Mei 2026**

## 5 Juni 2026 - Skematik dan Algoritma Firmware Awal

Perumusan rancangan arsitektur dasar perangkat keras: skematik rangkaian dan algoritma firmware awal.

> 📎 **Bukti:** `ALLY_skematik rangkaian versi awal.png`, `ALLY_diagram alur firmware awal.png`
> 🗂️ **Google Drive:** folder tanggal **5 Juni 2026**

---

# Tahap 2 - Manajemen Daya

**Periode: 7 Juni sampai 2 Juli 2026**

Bagian ini memuat tiga percobaan berurutan. Dua percobaan pertama gagal memenuhi syarat, dan justru kegagalan itu yang mengarahkan rancangan akhir.

## 7 Juni 2026 - Perancangan Manajemen Daya

**Kebutuhan yang dihitung:** konsumsi daya mikrokontroler dan ketiga sensor, untuk menentukan kapasitas baterai dan jenis pengatur tegangan.

**Kendala mendasar:** baterai LiPo 1 sel bekerja pada rentang 3,0 sampai 4,2 V, sedangkan sensor membutuhkan tegangan tetap. Artinya dibutuhkan pengatur tegangan yang tetap stabil sepanjang rentang itu.

> 📎 **Bukti:** `ALLY_perhitungan kebutuhan daya.png`
> 🗂️ **Google Drive:** folder tanggal **7 Juni 2026**

## 11 Juni 2026 - Percobaan 1: Buck Converter Mini360

**Percobaan:** pengujian performa daya keluaran buck converter tipe Mini360 milik lab, memakai power supply sebagai simulasi tegangan baterai LiPo 1 sel.

**Hasil: GAGAL.** Terjadi kondisi shutdown pada tegangan keluaran buck converter.

**Analisis kegagalan:** buck converter menurunkan tegangan, sehingga membutuhkan tegangan masukan yang lebih tinggi daripada keluarannya. Ketika baterai turun mendekati 3,0 V, selisih tegangan tidak lagi mencukupi dan modul berhenti bekerja. Padahal rentang bawah itu masih menyimpan energi yang seharusnya terpakai.

**Kesimpulan percobaan:** topologi buck tidak cocok untuk baterai LiPo 1 sel.

> 📎 **Bukti:** `ALLY_uji buck converter mini360.png`, `ALLY_kondisi shutdown tegangan rendah.png`
> 🗂️ **Google Drive:** folder tanggal **11 Juni 2026**

## 21 Juni 2026 - Percobaan 2: Boost Converter Keluaran Tetap 5V

**Percobaan:** buck converter diganti boost converter dengan keluaran tetap 5 V, lalu diuji pembebanan 500 mA konstan memakai power supply.

**Hasil: BERHASIL.** Seluruh rentang tegangan baterai 3,0 sampai 4,2 V dapat dipakai tanpa modul berhenti bekerja.

**Alasan berhasil:** boost converter menaikkan tegangan, sehingga justru bekerja paling baik pada tegangan masukan rendah. Sifat ini berlawanan dengan buck, dan itulah yang dibutuhkan.

| Aspek | Buck Mini360 | Boost 5V tetap |
|---|---|---|
| Rentang baterai terpakai | terbatas, mati di tegangan rendah | **3,0 sampai 4,2 V penuh** |
| Uji beban 500 mA | shutdown | stabil |
| Keputusan | ditolak | **dipakai** |

> 📎 **Bukti:** `ALLY_uji boost converter beban 500mA.png`, `ALLY_perbandingan buck dan boost.png`
> 🗂️ **Google Drive:** folder tanggal **21 Juni 2026**

## 27 Juni sampai 2 Juli 2026 - Percobaan 3: Linear Regulator Ultra LDO

**Latar belakang:** boost converter menyelesaikan masalah rentang tegangan, tetapi sensor PPG sangat peka terhadap riak tegangan. Riak dari converter jenis switching dapat muncul sebagai derau pada sinyal optik.

**Percobaan:** pencarian dan penelaahan datasheet linear regulator ultra LDO 3,3 V yang tersedia di pasaran, lalu pembelian **RT9013-33GB**.

**Hasil:** ditetapkan rancangan daya dua tingkat.

```
Baterai LiPo 1s (3,0 sampai 4,2 V)
        |
        v
  Boost converter 5V tetap     <- memastikan seluruh rentang baterai terpakai
        |
        v
  RT9013-33GB LDO 3,3V         <- menekan riak agar sensor bersih
        |
        v
  Mikrokontroler dan sensor
```

**Alasan bertingkat:** boost mengurus jangkauan tegangan, LDO mengurus kebersihan tegangan. Satu komponen saja tidak dapat memenuhi keduanya sekaligus.

Pada 2 Juli dilakukan revisi skematik dan analisis manajemen daya lanjutan untuk memperkirakan durasi efektif sistem bekerja.

> 📎 **Bukti:** `ALLY_datasheet rt9013 ldo.png`, `ALLY_skematik daya dua tingkat.png`, `ALLY_revisi skematik.png`
> 🗂️ **Google Drive:** folder tanggal **27 Juni 2026** dan **2 Juli 2026**

## 14 Juli 2026 - Pengujian Charge Discharge Baterai

**Percobaan:** pengujian pengisian dan pengosongan baterai LiPo 1 sel berkapasitas tertulis 950 mAh, dengan pembebanan arus 500 mA konstan.

**Hasil:**

| Aspek | Nilai |
|---|---|
| Kapasitas tertulis di baterai | 950 mAh |
| Waktu discharge terukur | **97 menit 35 detik** |
| Kapasitas efektif terhitung | **813 mAh** |
| Persentase terhadap klaim | **85,6%** |

**Temuan:** kapasitas nyata baterai hanya sekitar 86% dari yang tertulis. Selisih ini penting dicatat, karena perkiraan lama pakai perangkat harus memakai angka terukur, bukan angka di label.

> 📎 **Bukti:** `ALLY_uji charge discharge baterai.png`, `ALLY_kurva penurunan tegangan baterai.png`
> 🗂️ **Google Drive:** folder tanggal **14 Juli 2026**

---

# Tahap 3 - Pengujian Sensor dan Kendala Komponen

**Periode: 17 Juni sampai 12 Juli 2026**

Tahap ini memuat tiga kerusakan komponen berturut-turut. Ketiganya berbeda gejala dan berbeda cara mendeteksinya.

## 17 Juni 2026 - Pengujian Awal Sensor dan Kendala Stok

**Kendala pengadaan:** penjual kehabisan stok komponen TP5000, sehingga dilakukan prosedur pengembalian dana dari marketplace dan pencarian komponen pengganti.

**Pengujian:** sensor MAX30102 tipe SEN0518 diuji memakai pustaka bawaan.

> 📎 **Bukti:** `ALLY_prosedur refund komponen tp5000.png`, `ALLY_uji sensor sen0518.png`
> 🗂️ **Google Drive:** folder tanggal **17 Juni 2026**

## 7 Juli 2026 - Firmware SON1303 dan Temuan Derau 50 Hz

**Percobaan:** pembuatan dan pengujian firmware sensor SON1303, termasuk analisis sinyal memakai metode bandpass, FFT, dan perhitungan BPM.

**Hasil: DITEMUKAN MASALAH.** Terjadi derau 50 Hz pada sinyal analog PPG hijau.

**Analisis:** frekuensi 50 Hz adalah frekuensi jala listrik PLN. Karena SON1303 mengeluarkan sinyal analog, jalurnya rentan menangkap induksi dari jaringan listrik sekitar. Sinyal PPG sendiri berada di bawah 5 Hz, sehingga derau 50 Hz jauh di atas pita yang diinginkan tetapi tetap merusak pembacaan karena amplitudonya besar.

**Penyelesaian:** revisi skematik dengan penambahan **ferrite bead** pada jalur catu sensor, dibeli pada pembelian tahap 3.

> 📎 **Bukti:** `ALLY_derau 50hz pada ppg hijau.png`, `ALLY_spektrum fft sebelum perbaikan.png`
> 🗂️ **Google Drive:** folder tanggal **7 Juli 2026**

## 10 Juli 2026 - Kerusakan Sensor Pertama

**Pembelian tahap 3:** filamen PETG, ferrite bead, MOSFET kanal P, dan sensor MAX30102.

**Percobaan:** pengujian sensor MAX30102 yang baru dibeli.

**Hasil: SENSOR RUSAK.** Alamat I2C tidak terbaca sama sekali.

**Analisis:** alamat I2C yang tidak terbaca berarti mikrokontroler tidak dapat berkomunikasi dengan sensor pada tingkat paling dasar. Ini menandakan kerusakan pada sensor itu sendiri, bukan pada program.

> 📎 **Bukti:** `ALLY_alamat i2c tidak terbaca.png`, `ALLY_hasil pemindaian i2c.png`
> 🗂️ **Google Drive:** folder tanggal **10 Juli 2026**

## 11 Juli 2026 - Kerusakan Sensor Kedua

**Tindakan:** pembelian sensor MAX30102 cadangan.

**Hasil: RUSAK JUGA, tetapi gejalanya berbeda.** LED inframerah internal mengalami kerusakan, ditandai LED inframerah tidak menyala dan munculnya derau ADC.

**Perbandingan dua kerusakan:**

| | Sensor 10 Juli | Sensor 11 Juli |
|---|---|---|
| Alamat I2C | tidak terbaca | terbaca normal |
| LED inframerah | tidak sempat diuji | tidak menyala |
| Gejala tambahan | tidak ada komunikasi | derau ADC |
| Letak kerusakan | antarmuka komunikasi | bagian optik |

**Pelajaran yang diambil:** sensor yang alamat I2C-nya terbaca belum tentu berfungsi. Pemeriksaan wajib berlanjut sampai LED benar-benar menyala dan nilainya wajar. Prosedur pemeriksaan sensor kemudian diperbarui mengikuti temuan ini.

> 📎 **Bukti:** `ALLY_led inframerah tidak menyala.png`, `ALLY_derau adc sensor rusak.png`
> 🗂️ **Google Drive:** folder tanggal **11 Juli 2026**

## 12 Juli 2026 - Firmware MAX30102 dan Ekstraksi Fitur PWA

**Percobaan:** pembuatan dan pengujian firmware sensor MAX30102, termasuk analisis sinyal memakai bandpass dan APG untuk mengekstrak fitur PWA.

**Hasil:** sinyal PPG merah dan inframerah paling optimal dibandingkan kanal hijau.

**Analisis:** panjang gelombang merah 660 nm dan inframerah 880 nm menembus jaringan lebih dalam sehingga menangkap denyut arteri dengan lebih baik. Kanal hijau 525 nm terserap kuat di lapisan permukaan, sehingga lebih cocok untuk penghitungan denyut ketimbang analisis bentuk gelombang.

**Dampak keputusan ini pada sisi perangkat lunak:** temuan ini kemudian menjadi dasar pemilihan kanal inframerah sebagai sumber BPM siap tampil di dashboard, setelah pada 6 Agustus ditemukan bahwa kanal hijau menghasilkan pembacaan yang tidak wajar.

> 📎 **Bukti:** `ALLY_perbandingan mutu tiga kanal.png`, `ALLY_ekstraksi fitur pwa apg.png`
> 🗂️ **Google Drive:** folder tanggal **12 Juli 2026**

---

# Tahap 4 - Penggantian Mikrokontroler

**Periode: 17 Juli 2026**

**Kendala:** diskusi tim menyimpulkan adanya keterbatasan pada mikrokontroler rancangan awal.

**Dua batasan yang ditemukan pada XIAO ESP32-C3:**

| Batasan | Akibat |
|---|---|
| Kapasitas SRAM terbatas | Penyangga sinyal tiga kanal tidak muat sekaligus |
| Kemampuan komputasi protokol cloud | Pengiriman berkelanjutan ke server tersendat |

**Keputusan:** mengganti XIAO ESP32-C3 dengan **XIAO ESP32-S3**.

**Konsekuensi:** skematik dan tata letak PCB harus dirancang ulang, karena tata letak pin dan dimensi kedua modul berbeda.

**Catatan:** penggantian ini diambil sebelum PCB difabrikasi, sehingga tidak ada papan yang terbuang. Kalau ditemukan setelah pencetakan, seluruh proses fabrikasi harus diulang dari awal.

> 📎 **Bukti:** `ALLY_perbandingan esp32 c3 dan s3.png`, `ALLY_skematik setelah penggantian mikrokontroler.png`
> 🗂️ **Google Drive:** folder tanggal **17 Juli 2026**

---

# Tahap 5 - Fabrikasi PCB

**Periode: 16 Juli sampai 21 Juli 2026**

## 16 Juli 2026 - Desain Tata Letak PCB

Perancangan tata letak PCB memakai EasyEDA.

**Pertimbangan tata letak:** jalur sensor analog dipisahkan sejauh mungkin dari jalur switching boost converter, mengikuti temuan derau 50 Hz pada 7 Juli.

> 📎 **Bukti:** `ALLY_layout pcb easyeda.png`, `ALLY_penempatan jalur analog dan switching.png`
> 🗂️ **Google Drive:** folder tanggal **16 Juli 2026**

## 19 Juli 2026 - Fabrikasi Mandiri

**Tahapan yang dikerjakan sendiri:**

| Urutan | Proses |
|---|---|
| 1 | Pencetakan desain |
| 2 | Etching |
| 3 | Pemberian lapisan masking |
| 4 | Pengeboran lubang |
| 5 | Penyolderan komponen |

**Catatan:** fabrikasi dikerjakan mandiri, tidak dipesan ke pabrik. Cara ini memangkas waktu tunggu sehingga revisi dapat dilakukan dalam hitungan hari, bukan minggu.

> 📎 **Bukti:** `ALLY_proses etching pcb.png`, `ALLY_pcb setelah pengeboran.png`, `ALLY_pcb setelah penyolderan.png`
> 🗂️ **Google Drive:** folder tanggal **19 Juli 2026**

## 21 Juli 2026 - Inspeksi dan Troubleshooting

**Pemeriksaan yang dilakukan:** pengecekan konektivitas jalur, perbaikan jalur, dan pembersihan PCB dari kotoran solder.

**Alasan pembersihan penting:** sisa solder yang tertinggal dapat membentuk hubungan tak sengaja antar jalur. Pada rangkaian dengan jalur berdekatan, hubungan sekecil apa pun berpotensi merusak sensor saat pertama kali dialiri daya.

> 📎 **Bukti:** `ALLY_inspeksi konektivitas jalur.png`, `ALLY_pcb setelah dibersihkan.png`
> 🗂️ **Google Drive:** folder tanggal **21 Juli 2026**

---

# Tahap 6 - Desain dan Cetak Casing

**Periode: 22 Juli sampai 25 Juli 2026**

## 22 Juli 2026 - Desain 3D

Perancangan casing ANTARAGA memakai Fusion 360.

> 📎 **Bukti:** `ALLY_desain 3d casing fusion360.png`
> 🗂️ **Google Drive:** folder tanggal **22 Juli 2026**

## 23 Juli 2026 - Penyesuaian Dimensi dan Pencetakan

**Kendala:** dimensi rancangan tidak sepenuhnya cocok dengan dimensi komponen asli, sehingga desain perlu disesuaikan sebelum dicetak.

**Bahan yang dipilih:** PETG.

**Alasan pemilihan PETG dibandingkan PLA:** PETG lebih tahan panas dan lebih liat, sehingga tidak melengkung saat perangkat dipakai menempel di kulit dan tidak mudah retak saat casing dibuka tutup untuk perawatan.

> 📎 **Bukti:** `ALLY_penyesuaian dimensi casing.png`, `ALLY_hasil cetak casing petg.png`
> 🗂️ **Google Drive:** folder tanggal **23 Juli 2026**

## 25 Juli 2026 - Integrasi Komponen dan Kendala Pengisian Daya

**Pekerjaan:** penyambungan kabel konektor, pemasangan tombol, port charger, baterai, sensor, dan PCB ke dalam casing.

**Kendala yang ditemukan:** terdapat penurunan tegangan pada saat pengujian pengisian daya perangkat.

**Analisis:** penurunan tegangan saat pengisian umumnya berasal dari hambatan pada jalur atau konektor. Arus pengisian yang melewati jalur berhambatan akan menimbulkan rugi tegangan, sehingga tegangan yang benar-benar sampai ke baterai lebih rendah daripada yang dikirim.

> 📎 **Bukti:** `ALLY_integrasi komponen ke casing.png`, `ALLY_kendala drop tegangan pengisian.png`, `ALLY_perangkat terpasang lengkap.png`
> 🗂️ **Google Drive:** folder tanggal **25 Juli 2026**

---

# Tahap 7 - Firmware Utama dan Konektivitas

**Periode: 27 Juli sampai 30 Juli 2026**

## 27 Juli 2026 - Pembuatan Firmware Utama

**Enam modul yang disusun:**

| Modul | Fungsi |
|---|---|
| Program sensor SON1303 | Pembacaan kanal hijau 525 nm |
| Program sensor MAX30102 | Pembacaan kanal merah 660 nm dan inframerah 880 nm |
| Program pembacaan kapasitas baterai | Pemantauan sisa daya |
| Program kalkulasi SQI | Penilaian mutu sinyal di perangkat |
| Program inisiasi WiFi | Penyambungan ke jaringan |
| Program konektivitas cloud | Pengiriman data berkelanjutan ke server |

**Keputusan perancangan:** penilaian SQI dihitung di perangkat, bukan di server. Dengan begitu rekaman yang mutunya buruk dapat ditandai sejak awal, sehingga tidak membebani jaringan dan tidak mencemari dataset.

> 📎 **Bukti:** `ALLY_struktur firmware utama.png`, `ALLY_modul kalkulasi sqi.png`
> 🗂️ **Google Drive:** folder tanggal **27 Juli 2026**

## 29 Juli 2026 - Unggah Firmware dan Kerusakan Sensor Ketiga

**Percobaan:** unggah firmware utama ke perangkat, lalu uji komunikasi dan pengiriman data ke server.

**Kendala:** sensor MAX30102 tidak dapat membaca nilai inframerah karena kerusakan LED inframerah, sehingga dilakukan penggantian.

**Ini kerusakan sensor ketiga.** Pola yang sama dengan 11 Juli: alamat I2C terbaca, tetapi bagian optiknya mati.

**Kesimpulan dari tiga kerusakan berturut-turut:** mutu sensor MAX30102 di pasaran sangat beragam. Pemeriksaan sebelum pemasangan menjadi prosedur wajib, dan pengadaan komponen cadangan diperlakukan sebagai kebutuhan, bukan pilihan.

### Temuan beban komputasi dan keputusan memindahkan pengolahan sinyal

Setelah firmware utama terpasang dan pengiriman ke server berjalan, dilakukan pengukuran beban kerja mikrokontroler saat seluruh proses berjalan bersamaan.

**Dua temuan:**

| # | Temuan | Akibat |
|---|---|---|
| 1 | Penapisan bandpass dan perhitungan FFT tiga kanal menuntut prosesor bekerja pada laju penuh sepanjang waktu | Perangkat tidak sempat masuk kondisi hemat daya di sela pencuplikan |
| 2 | Penyangga float ketiga kanal menyita SRAM | Jendela pencuplikan tidak dapat diperpanjang |

**Analisis:** penggantian mikrokontroler ke XIAO ESP32-S3 pada 17 Juli sudah menambah kelapangan SRAM, tetapi belum menghilangkan beban komputasinya. Selama penapisan dan FFT tetap dikerjakan di perangkat, prosesor akan terus bekerja penuh berapa pun kapasitas mikrokontrolernya.

**Pertimbangan yang menentukan keputusan:** radio WiFi memang harus menyala terus-menerus, karena perangkat ini dari awal dirancang mengirim data ke server. Radio tidak dapat dimatikan apa pun yang terjadi. Karena radio sudah menyala, mengirim data mentah yang jumlah bytenya lebih besar hampir tidak menambah biaya pengiriman. Sebaliknya, mengolah sinyal di perangkat menjadi beban tambahan tanpa penghematan yang sepadan.

**Keputusan:** diambil bersama tim perangkat lunak, pengolahan sinyal dipindahkan ke server, sedangkan firmware cukup mengirim data mentah.

> 📎 **Bukti:** `ALLY_uji komunikasi firmware ke server.png`, `ALLY_kerusakan led inframerah ketiga.png`, `ALLY_pengukuran beban komputasi firmware.png`
> 🗂️ **Google Drive:** folder tanggal **29 Juli 2026**

## 30 Juli 2026 - Pelaksanaan Pemindahan dan Kalibrasi Ulang Sampling

**Pekerjaan:** pelaksanaan pemindahan pengolahan sinyal ke server sesuai keputusan sehari sebelumnya, disertai kalibrasi ulang pencuplikan data mentah ketiga sinyal PPG.

**Perubahan peran firmware:**

| Fungsi | Sebelum 30 Juli | Sesudah 30 Juli |
|---|---|---|
| Pencuplikan sensor | di perangkat | **tetap di perangkat** |
| Penapisan bandpass | di perangkat | dipindah ke server |
| Perhitungan FFT dan BPM | di perangkat | dipindah ke server |
| Perhitungan SQI | di perangkat | **tetap di perangkat** |
| Penyusunan dan pengiriman batch | di perangkat | **tetap di perangkat** |

**Alasan SQI tetap dipertahankan di perangkat:** bebannya ringan, hanya berupa penilaian periodisitas, dan berguna menandai rekaman bermutu buruk sebelum dikirim. Dengan begitu jaringan tidak terpakai untuk mengirim data yang memang tidak layak diolah.

**Kalibrasi ulang pencuplikan:** laju cuplik dan ukuran batch disesuaikan dengan kebutuhan pengolahan di sisi server. Laju cuplik menentukan ketelitian penghitungan denyut, karena laju yang terlalu rendah membuat puncak sistolik terlewat, sedangkan yang terlalu tinggi membebani penyangga memori dan jaringan.

> 📎 **Bukti:** `ALLY_firmware setelah pemindahan pengolahan.png`, `ALLY_kalibrasi ulang laju sampling.png`, `ALLY_bentuk gelombang tiga kanal.png`
> 🗂️ **Google Drive:** folder tanggal **30 Juli 2026**

---

# Tahap 8 - Kalibrasi dan Pengujian Lapangan

**Periode: 2 Agustus sampai 2 September 2026**

## 2 Agustus 2026 - Pengujian BPM terhadap Alat Ukur Terstandar

**Percobaan:** pengujian pembacaan BPM dan analisis galatnya dibandingkan oximeter dan tensimeter.

**Alasan pengujian:** BPM hasil perhitungan sendiri tidak berarti apa pun sebelum dibandingkan dengan alat yang sudah terstandar. Tanpa pembanding, tidak ada cara mengetahui apakah nilai yang terbaca benar.

**Temuan yang diteruskan ke tim perangkat lunak:** ditemukan pola pembacaan yang sesekali menyimpang jauh, yang kemudian ditindaklanjuti dengan pembuatan penyaring lonjakan BPM di sisi server pada 6 Agustus.

**Pengukuran konsumsi daya setelah pemindahan:** dilakukan pengukuran konsumsi daya perangkat sesudah pengolahan sinyal dipindahkan ke server, lalu dibandingkan dengan pengukuran sebelum pemindahan. Pengukuran dilakukan pada kondisi pengiriman data berkelanjutan agar mewakili pemakaian sebenarnya. Hasil pembandingan dipakai memperbarui perkiraan lama pakai perangkat dalam sekali pengisian daya.

*(angka hasil pengukuran perlu dilengkapi sesuai catatan pengujian)*

> 📎 **Bukti:** `ALLY_perbandingan bpm dengan oximeter.png`, `ALLY_analisis galat pembacaan bpm.png`, `ALLY_konsumsi daya sebelum dan sesudah pemindahan.png`
> 🗂️ **Google Drive:** folder tanggal **2 Agustus 2026**

## 5 Agustus 2026 - Penyiapan Perangkat untuk Sesi Kalibrasi

Pemeriksaan sensor, pengisian daya, dan penyesuaian firmware agar pengiriman data stabil selama sesi berlangsung.

> 📎 **Bukti:** `ALLY_pemeriksaan perangkat sebelum sesi.png`
> 🗂️ **Google Drive:** folder tanggal **5 Agustus 2026**

## 6 Agustus 2026 - Pendampingan Pengujian Kedua

Pendampingan pengujian terhadap relawan dari sisi perangkat keras: memastikan sensor terpasang benar, mutu sinyal memadai, dan perangkat mengirim data tanpa terputus.

> 📎 **Bukti:** `ALLY_pemasangan sensor pada relawan.png`, `ALLY_pemantauan mutu sinyal saat sesi.png`
> 🗂️ **Google Drive:** folder tanggal **6 Agustus 2026**

## 16 Agustus 2026 - Karakterisasi Sinyal Empat Sesi

**Pekerjaan:** peninjauan mutu sinyal seluruh rekaman dari sesi pertama sampai keempat, mencakup perfusi inframerah, amplitudo denyut, dan tingkat derau tiap subjek.

**Temuan 1:** perfusi inframerah tiap subjek berkisar **0,74 sampai 1,77 permil**, seluruhnya berada di rentang PPG normal. Mutu rekaman kanal merah dan inframerah dinyatakan memadai.

**Temuan 2:** satu rekaman menunjukkan rasio merah terhadap inframerah menyimpang jauh dari subjek lain, menandakan posisi atau kontak sensor berbeda saat perekaman itu. Direkomendasikan diulang pada sesi berikutnya.

**Analisis ketahanan daya:** penggabungan catatan penurunan daya baterai dari keempat sesi menjadi satu grafik, beserta perhitungan perkiraan lama pakai pada pengiriman data berkelanjutan.

> 📎 **Bukti:** `ALLY_karakterisasi sinyal empat sesi.png`, `ALLY_temuan rasio merah inframerah menyimpang.png`, `ALLY_grafik ketahanan baterai.png`, `ALLY_laporan bagian hardware.png`
> 🗂️ **Google Drive:** folder tanggal **16 Agustus 2026**

## 23 Agustus sampai 2 September 2026 - Peragaan, Laporan, dan Sesi Lanjutan

| Tanggal | Kegiatan |
|---|---|
| 23 Agustus | Merapikan perangkat ke kondisi siap peragaan dan menyusun bagian perangkat keras laporan kemajuan |
| 26 Agustus | Workshop Teknik Presentasi PKP2, penyiapan bagian perangkat keras yang dibawakan |
| 28 Agustus | Asistensi bagian perangkat keras ke dosen pendamping |
| 29 Agustus | Penyiapan bahan visual perangkat keras untuk konten media sosial ketiga |
| 30 Agustus | Pendampingan pengujian smartband kelima |
| 2 September | Pendampingan pengujian smartband keenam |

> 📎 **Bukti:** `ALLY_perangkat siap peragaan.png`, `ALLY_asistensi bagian hardware.png`, `ALLY_pengujian kelima.png`, `ALLY_pengujian keenam.png`
> 🗂️ **Google Drive:** folder tanggal **23 Agustus 2026**, **28 Agustus 2026**, **30 Agustus 2026**, dan **2 September 2026**

---

# Ringkasan Kendala dan Penyelesaiannya

| # | Kendala | Penyelesaian |
|---|---|---|
| 1 | Buck converter Mini360 shutdown di tegangan baterai rendah | Diganti boost converter keluaran tetap 5 V, seluruh rentang 3,0 sampai 4,2 V terpakai |
| 2 | Riak switching berpotensi mengotori sinyal sensor | Ditambah LDO RT9013-33GB sebagai tingkat kedua |
| 3 | Stok komponen TP5000 habis di penjual | Prosedur pengembalian dana dan pencarian komponen pengganti |
| 4 | Derau 50 Hz pada sinyal analog PPG hijau | Revisi skematik dengan penambahan ferrite bead |
| 5 | Sensor MAX30102 pertama, alamat I2C tidak terbaca | Sensor diganti, prosedur pemeriksaan diperbarui |
| 6 | Sensor MAX30102 kedua, LED inframerah mati | Pemeriksaan diperluas sampai LED benar-benar menyala |
| 7 | Sensor MAX30102 ketiga rusak saat unggah firmware | Penggantian, pengadaan cadangan dijadikan prosedur tetap |
| 8 | XIAO ESP32-C3 terbatas SRAM dan komputasi protokol cloud | Diganti XIAO ESP32-S3, skematik dan tata letak dirancang ulang sebelum fabrikasi |
| 9 | Penapisan dan FFT di perangkat membuat prosesor bekerja penuh terus-menerus | Pengolahan sinyal dipindahkan ke server, firmware cukup mengirim data mentah |
| 10 | Jalur PCB perlu diperiksa setelah fabrikasi mandiri | Inspeksi konektivitas, perbaikan jalur, pembersihan sisa solder |
| 11 | Dimensi casing tidak cocok dengan komponen asli | Penyesuaian desain sebelum pencetakan |
| 12 | Penurunan tegangan pada pengisian daya perangkat | Ditelusuri ke hambatan jalur dan konektor |
| 13 | Kapasitas baterai hanya 86% dari klaim label | Perkiraan lama pakai memakai angka terukur 813 mAh |
| 14 | Pembacaan BPM sesekali menyimpang jauh | Dilaporkan ke tim perangkat lunak, ditangani penyaring lonjakan di server |
| 15 | Kanal hijau bermutu rendah untuk analisis bentuk gelombang | Kanal merah dan inframerah dijadikan sumber utama |

---

# Kesimpulan Capaian

## Yang sudah selesai

### 1. Perangkat smartband berfungsi penuh

| Komponen | Spesifikasi |
|---|---|
| Mikrokontroler | XIAO ESP32-S3 |
| Sensor optik | MAX30102 (merah 660 nm, inframerah 880 nm) dan SON1303 (hijau 525 nm) |
| Catu daya | Boost converter 5 V tetap, LDO RT9013-33GB 3,3 V |
| Baterai | LiPo 1 sel, kapasitas efektif terukur 813 mAh |
| Casing | Cetak 3D bahan PETG |
| PCB | Fabrikasi mandiri, sudah lewat inspeksi |

### 2. Firmware lengkap

Enam modul berjalan: dua pembacaan sensor, pemantauan baterai, kalkulasi SQI, inisiasi WiFi, dan konektivitas cloud dengan pengiriman berkelanjutan.

Sejak 30 Juli 2026, peran firmware sengaja dipersempit menjadi pencuplik dan pengirim data mentah. Penapisan bandpass, perhitungan FFT, dan penghitungan BPM dipindahkan ke server, sehingga prosesor tidak lagi bekerja penuh sepanjang waktu dan SRAM-nya terbebas. Perhitungan SQI tetap dipertahankan di perangkat karena bebannya ringan dan berguna menyaring rekaman bermutu buruk sebelum dikirim.

### 3. Karakterisasi sinyal terverifikasi

Perfusi inframerah seluruh subjek berada di rentang PPG normal 0,74 sampai 1,77 permil. Kanal merah dan inframerah terbukti paling andal untuk analisis bentuk gelombang.

### 4. Data ketahanan daya terukur

Waktu discharge 97 menit 35 detik pada beban 500 mA konstan, dengan kapasitas efektif 85,6% dari klaim label.

## Yang belum selesai

| Hal | Kondisi | Yang dibutuhkan |
|---|---|---|
| Penyambungan ulang WiFi | Sebab kegagalan sudah didiagnosis bersama tim perangkat lunak | Penerapan perbaikan di firmware |
| Penurunan tegangan pengisian | Sudah ditelusuri | Perbaikan jalur atau penggantian konektor |
| Rekaman dengan rasio menyimpang | Teridentifikasi pada satu subjek | Pengulangan perekaman |
| Perangkat untuk sesi paralel | Baru tersedia terbatas | Penggandaan unit agar sesi dapat berjalan serentak |

## Catatan penutup

Sisi perangkat keras ANTARAGA dibangun lewat rangkaian perbaikan yang seluruhnya berawal dari kegagalan terukur, bukan dari rancangan yang langsung jadi. Tiga contoh yang paling menentukan:

1. **Kegagalan buck converter** justru yang mengarahkan ke topologi boost, yang sifatnya berlawanan dan tepat sesuai kebutuhan baterai LiPo 1 sel.
2. **Tiga kerusakan sensor berturut-turut** mengubah prosedur pemeriksaan komponen: alamat I2C terbaca ternyata belum cukup sebagai bukti sensor berfungsi.
3. **Keterbatasan mikrokontroler yang ditemukan sebelum fabrikasi** menyelamatkan seluruh proses pencetakan PCB dari pengulangan.

Seluruh keputusan rancangan dapat ditelusuri ke hasil pengukuran yang tercatat, termasuk keputusan untuk mengganti komponen yang sudah terlanjur dibeli.

---

*Dokumen ini merupakan bagian dari Laporan Kemajuan PKM-KC ANTARAGA 2026.*
