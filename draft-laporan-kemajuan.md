DAFTAR ISI
DAFTAR ISI ............................................................................................................ i
DAFTAR GAMBAR ............................................................................................. iii
DAFTAR TABEL .................................................................................................. iv
DAFTAR LAMPIRAN .......................................................................................... iv
BAB 1. PENDAHULUAN ..................................................................................... 1
1.1 Latar Belakang .............................................................................................. 1
1.2 Tujuan dan Relevansi dengan Tema PKM 2026........................................... 1
1.3 Inovasi Karsa Cipta dan Kemutakhirannya................................................... 2
BAB 2. TARGET LUARAN .................................................................................. 2
2.1 Laporan Kemajuan ........................................................................................ 2
2.2 Laporan Akhir ............................................................................................... 2
2.3 Prototipe ANTARAGA ................................................................................. 2
2.4 Akun dan Konten Media Sosial ANTARAGA ............................................. 3
2.5 Aplikasi Mobile ANTARAGA ..................................................................... 3
2.6 Video Simulasi dan Pengujian ANTARAGA ............................................... 3
2.7 Hak Cipta Program Komputer ...................................................................... 3
BAB 3. TAHAP PELAKSANAAN ........................................................................ 3
3.1 Alat dan Bahan .............................................................................................. 3
3.2 Realisasi Pelaksanaan Program ..................................................................... 4
BAB 4. HASIL YANG DICAPAI .......................................................................... 4
4.1 Dampak Pengiklanan Media Sosial .............................................................. 4
4.1 Perkembangan Hardware dan Software Terintegrasi ................................... 5
4.2 Hasil Pengembangan Model AI dan Validasi Pengujian .............................. 7
BAB 5. POTENSI HASIL ...................................................................................... 8
5.1 Potensi Dampak ANTARAGA ..................................................................... 8
5.2 Potensi Pengembangan ................................................................................. 8
5.3 Perolehan HKI ............................................................................................... 8
BAB 6. RENCANA TAHAPAN BERIKUTNYA ................................................. 8
DAFTAR PUSTAKA ............................................................................................. 9
LAMPIRAN .......................................................................................................... 10

i

DAFTAR GAMBAR
Gambar 2.1 Prototipe Fisik Smartband ANTARAGA ............................................ 2
Gambar 2.2 Publikasi Media Sosial ANTARAGA ................................................. 3
Gambar 2.3 Tampilan Aplikasi Mobile ANTARAGA ............................................ 3
Gambar 2.4 Dokumentasi Video Simulasi dan Pengujian ....................................... 3
Gambar 2.5 Surat Pencatatan Ciptaan ANTARAGA .............................................. 3
Gambar 3.1 Tahap Pelaksanaan Program ANTARAGA ......................................... 4
Gambar 4.1 Pengembangan Perangkat Keras ANTARAGA ................................... 5
Gambar 4.2 Arsitektur Aktual Smartband-Server-Aplikasi ..................................... 6
Gambar 4.3 Dashboard Pemantauan Sinyal PPG .................................................... 6
Gambar 4.4 Perbandingan Recall Model XGBoost ................................................. 7
Gambar 4.5 Dashboard Pelatihan Model MLP ........................................................ 7
Gambar 4.6 Pengujian Prototipe terhadap Relawan ................................................ 8
Gambar 4.7 Konsultasi Dokter Spesialis Saraf ........................................................ 8
Gambar 4.8 Capaian Media Sosial ANTARAGA ................................................... 8

ii

DAFTAR TABEL
Tabel 3.1 Alat dan Bahan Utama ............................................................................. 3
Tabel 4.1 Spesifikasi Aktual Prototipe ANTARAGA ............................................. 5
Tabel 4.2 Evaluasi Model XGBoost ........................................................................ 7
Tabel 4.3 Rekap Pengujian Relawan ....................................................................... 8
Tabel 6.1 Rencana Tahapan Berikutnya .................................................................. 9

iii

DAFTAR LAMPIRAN
Lampiran 1. Bukti Teknis dan Rekap Pengujian Prototipe .................................... 11
Lampiran 2. Rincian Logbook Kegiatan ................................................................ 12
Lampiran 3. Rincian Publikasi Media Sosial ......................................................... 22
Lampiran 4. Rincian Anggaran dan Penggunaan Dana ......................................... 23
Lampiran 5. Ethical Clearance dan Bukti Hak Cipta ............................................. 24

iv

1

BAB 1. PENDAHULUAN
1.1 Latar Belakang

 Stroke merupakan salah satu masalah kesehatan dengan dampak kematian dan
kecacatan  neurologis  yang  tinggi.  Global  Stroke  Fact  Sheet  2025  melaporkan
sekitar 6,7 juta kematian akibat stroke setiap tahun. Sekitar 87% kasus merupakan
stroke  iskemik  yang  sangat  sensitif  terhadap  waktu,  sehingga  keterlambatan
penanganan dapat memperburuk luaran pasien (Feigin dkk., 2025; Capirossi dkk.,
2023).

 Salah satu hambatan penting terjadi pada fase prarumah sakit ketika keluarga
terlambat  mengenali  urgensi  gejala  dan  mengambil  keputusan  menuju  fasilitas
kesehatan.  Kondisi  ini  semakin  sulit  ketika  keluhan  menyerupai  Transient
Ischaemic  Attack  (TIA)  yang  dapat  hilang  timbul.  Meskipun  kampanye  FAST
membantu  pengenalan  gejala,  keputusan  keluarga  masih  dapat  dipengaruhi
keraguan,  kepanikan,  atau  anggapan  bahwa  kondisi  telah  membaik  (Potisopha
dkk., 2023; Writing Committee for the PERSIST Collaborators, 2025).

risiko

secara

informasi

 Kondisi  tersebut  menunjukkan  perlunya  sarana  pemantauan  yang  dapat
memberikan
lebih  objektif  kepada  keluarga.
Perkembangan wearable, Photoplethysmography (PPG), Internet of Things (IoT),
dan  kecerdasan  buatan  membuka  peluang  untuk  memenuhi  kebutuhan  tersebut.
Namun,  perangkat  wearable  kesehatan  umumnya  masih  berorientasi  pada
pemantauan  kebugaran  dan  penyajian  parameter  numerik,  belum  terintegrasi
dengan mekanisme penilaian risiko dan tindak lanjut keluarga.

 Menjawab  kebutuhan

tersebut,  ANTARAGA  dikembangkan

sebagai
smartband  berbasis  PPG  multi-wavelength  dengan  kecerdasan  buatan  yang
terintegrasi  aplikasi  mobile.  Sistem  memantau  indikator  fisiologis  dan  faktor
risiko  untuk  memberikan  informasi  risiko,  peringatan,  serta  asesmen  ABCD2
sebagai  pendukung  keputusan  keluarga  menuju  evaluasi  medis.  ANTARAGA
tidak  ditujukan  sebagai  alat  diagnosis,  melainkan  untuk  membantu  mempercepat
pengambilan keputusan pada fase prarumah sakit.

Gambar 1.1 Smartband dan Aplikasi ANTARAGA

1.2 Tujuan dan Relevansi dengan Tema PKM 2026

 Smartband  ANTARAGA  bertujuan  membantu  mendeteksi  risiko  stroke
iskemik  lebih  dini  sehingga  mencegah  terjadinya  keterlambatan  penanganan
sesuai  dengan  prinsip  time  is  brain.  Tujuan  tersebut  relevan  dengan  tema  PKM
2026,  yaitu  “Kesehatan  dan  Gizi  Masyarakat”  karena  memanfaatkan  teknologi

2

kesehatan  untuk  meningkatkan  kewaspadaan  keluarga  terhadap  risiko  stroke  dan
mendukung pendampingan kesehatan lansia di lingkungan rumah.
1.3 Inovasi Karsa Cipta dan Kemutakhirannya

 Inovasi ANTARAGA sebagai sistem pemantauan faktor risiko stroke iskemik
berbasis  smartband  mengintegrasikan  beberapa  teknologi  mutakhir  sebagai
berikut:
1.  Akuisisi Sinyal PPG Multi-Wavelength

ANTARAGA menggunakan sensor SON1303 pada kanal hijau 525 nm serta
MAX30102  pada  kanal  merah  660  nm  dan  inframerah  880  nm  untuk
(PPG).  Penggunaan  beberapa
merekam  sinyal  Photoplethysmography
panjang  gelombang  memanfaatkan  karakteristik  penetrasi  cahaya  yang
berbeda  pada  jaringan  sehingga  sinyal  lebih  informatif  untuk  pemantauan
fisiologis (Kim dan Baek, 2023).

2.  Pengolahan Sinyal Terdistribusi antara Smartband dan Server

Smartband  melakukan  pencuplikan  tiga  kanal  PPG,  penyusunan  batch  data,
dan  penilaian  kualitas  sinyal  menggunakan  Signal  Quality  Index  (SQI),
sedangkan  server  menjalankan  penapisan  bandpass  Butterworth  0,5–5  Hz,
autokorelasi  FFT,  dan  perhitungan  BPM.  Pembagian  proses  ini  mengurangi
beban  komputasi  mikrokontroler  sekaligus  memudahkan  pembaruan
algoritma pada server.

3.  Penilaian Risiko Stroke Menggunakan XGBoost

tanpa  perlu

imputasi  manual,

Model Extreme Gradient Boosting (XGBoost) digunakan untuk menilai risiko
stroke berdasarkan sembilan faktor masukan pengguna, menggantikan model
Gradient  Boosting  generik  yang  direncanakan  pada  proposal.  XGBoost
dipilih  karena  menyediakan  regularisasi  L1/L2  bawaan  yang  menekan
overfitting pada dataset berukuran terbatas, penanganan native terhadap nilai
fitur  yang  hilang
serta  parameter
scale_pos_weight  untuk  membobot  ulang  kelas  minoritas.  Kebutuhan  utama
pada  dataset  ini  karena  kelas  stroke  hanya  sekitar  4,87%  dari  keseluruhan
data.  Pemilihan  ini  diverifikasi  melalui  perbandingan  langsung  terhadap
HistGradientBoosting  (varian  gradient  boosting  lain  yang  lebih  baru)  pada
tahap  evaluasi  model  (lihat  BAB  4.4.1),  bukan  sekadar  pilihan  default.
Ketidakseimbangan  kelas  pada  dataset  ditangani  melalui  scale_pos_weight,
sedangkan  ambang  keputusan  dievaluasi  menggunakan  prediksi  out-of-fold
dan  kurva  Precision-Recall  untuk  meningkatkan  sensitivitas  terhadap  kelas
berisiko (Luo dkk., 2025).

4.  Estimasi Parameter Fisiologis Menggunakan Multi-Layer Perceptron

Lima model Multi-Layer Perceptron (MLP) dikembangkan untuk memetakan
fitur  optik  PPG  menjadi  estimasi  gula  darah,  kolesterol,  asam  urat,  tekanan
sistolik,  dan  tekanan  diastolik.  Model  terintegrasi  dengan  dashboard  server
sehingga dapat dilatih ulang ketika tersedia data kalibrasi baru.

5.  Integrasi Peringatan Risiko dan Asesmen ABCD2 pada Aplikasi Mobile

3

Hasil pemantauan terintegrasi dengan aplikasi mobile keluarga. Ketika sistem
mendeteksi  peningkatan
risiko,  aplikasi  memberikan  peringatan  dan
mengaktifkan asesmen ABCD2 untuk membantu menentukan tingkat urgensi
berdasarkan faktor klinis dan durasi gejala (Spampinato dkk., 2022). Integrasi
ini  mendukung  keluarga  dalam  mengambil  keputusan  evaluasi  medis  lebih
cepat pada fase prarumah sakit.

BAB 2. TARGET LUARAN
2.1 Laporan Kemajuan

Laporan  kemajuan  sebagai  bentuk  dokumentasi  pelaksanaan  program  telah
disusun  dengan  tingkat  penyelesaian  100%.  Kegiatan-kegiatan  ini  telah  tercatat
pada  Logbook  Kegiatan  dengan  capaian  95%,  dengan  bukti  pengeluaran  dan
Logbook Kegiatan terlampir pada Lampiran 3 dan 6.
2.2 Laporan Akhir

Laporan  akhir  memuat  seluruh  hasil  akhir  pelaksanaan  dan  pengembangan
smartband ANTARAGA dengan capaian 75%, mencakup kerangka laporan, hasil
pengujian  awal,  dan  dokumentasi  kegiatan  yang  telah  tersusun.  Penyempurnaan
lebih lanjut akan dilakukan setelah pengujian tambahan dan pelatihan ulang model
AI selesai, sejalan dengan rencana tahapan pada BAB 6.
2.3 Prototipe ANTARAGA

Prototipe  smartband  ANTARAGA  telah  terealisasi  dengan  capaian  90%
sebagai smartband pendeteksi risiko stroke iskemik pada lansia, yang terintegrasi
dengan  aplikasi  mobile  ANTARAGA  sehingga  dapat  dipantau  langsung  oleh
keluarga. Smartband telah digunakan dalam 11 kali pengujian hingga 5 September
2026. Sisa capaian dialokasikan untuk pelatihan lanjutan model AI (XGBoost dan
MLP) menggunakan data kalibrasi tambahan dari sesi pengujian relawan.
2.4 Akun dan Konten Media Sosial ANTARAGA

Publikasi  media  sosial  Instagram  telah  mencapai  100%  melalui  3  konten
program yang dipublikasikan dan diiklankan pada 6 Juni, 4 Juli, dan 29 Agustus
2026. Konten wajib tersebut mencakup Pengenalan ANTARAGA, Edukasi Tanda
Risiko, dan Pegujian ANTARAGA.
2.5 Aplikasi Mobile ANTARAGA

Aplikasi  Mobile  ANTARAGA  telah  dikembangkan  dan  mencapai  100%.
Aplikasi ini telah didaftarkan pada Play Store dengan sasaran pengguna Android,
serta  terhubung  dengan  backend  untuk  menampilkan  hasil  pemantauan  dan
prediksi risiko dari smartband.
2.6 Video Simulasi dan Pengujian ANTARAGA

Video simulasi skenario penggunaan dan pengujian telah  mencapai 100%, da

telah dipublikasikan sebagai konten program 1 dan konten program 3.
2.7 Hak Cipta Program Komputer

ANTARAGA  telah  memperoleh  Hak  Cipta  Program  Komputer  dengan
capaian  100%,  dibuktikan  dengan  Surat  Pencatatan  Ciptaan  oleh  Kementerian

4

Hukum  dengan  nomor  pencatatan  001449089.  Surat  tersebut  dapat  dilihat  pada
Lampiran X.
BAB 3. TAHAP PELAKSANAAN
3.1 Alat dan Bahan

 Berikut disajikan alat dan bahan utama yang digunakan dalam pengembangan

smartband ANTARAGA berdasarkan realisasi hingga tahap pengujian saat ini.

Tabel 3.1 Alat dan Bahan Utama

No

Komponen

Fungsi/Keterangan Aktual

1  XIAO ESP32-S3

Mikrokontroler utama setelah migrasi dari
ESP32-C3

2  SON1303 dan MAX30102  Akuisisi PPG hijau, merah, dan inframerah

3

TP5000, LDO RT9013-
33GB, Li-Po 950 mAh

Pengisian, pengaturan tegangan, dan sumber
daya

4  PCB dan casing PETG

Casing didesain internal tim, dicetak melalui
jasa 3D printing eksternal; PCB difabrikasi
mandiri

5

Peralatan fabrikasi &
desain

Digunakan untuk perancangan casing dan
pembuatan PCB mandiri

6  VPS, Flutter

Infrastruktur server dan pengembangan
aplikasi

7

Multimeter, tensimeter,
glukometer digital

Alat ukur pembanding terstandar untuk
validasi pengujian terhadap relawan.

prototipe

Pengembangan

smartband  ANTARAGA  memperbarui
mikrokontroler  yang  digunakan  dari  XIAO  ESP32-C3  menjadi  XIAO  ESP32-S3
karena  memiliki  2  core  pemrosesan  dan  kapasitas  SRAM  lebih  besar,  sehingga
memungkinkan untuk menjalankan transmisi data ke cloud dan pembacaan sensor
secara bersamaan.
3.2 Realisasi Pelaksanaan Program

Tahapan  pelaksanaan  program  ANTARAGA  yang

telah  direalisasikan
berfokus  pada  fase  perancangan  hingga  perlindungan  kekayaan  intelektual.
Rincian ketercapaian pada setiap tahap pelaksanaan adalah sebagai berikut:
1.  Studi  Literatur:  Kajian  PPG  tiga  panjang  gelombang,  pengolahan  sinyal,

class imbalance, ABCD2, dan arsitektur wearable telah selesai.

2.  Perancangan  Sistem:  Skematik,  tata  letak  PCB,  optimalisasi  manajemen
daya,  basis  data,  backend,  aplikasi,  dan  arsitektur  dua  model  telah
diselesaikan.

5

3.  Pembuatan  Prototipe:  PCB  difabrikasi  mandiri,  casing  PETG  dicetak,
komponen  dirakit,  dan  mikrokontroler  diganti  dari  XIAO  ESP32-C3  ke
ESP32-S3 sebelum fabrikasi.

4.  Integrasi Sistem: Firmware, Wi-Fi, API, VPS, dashboard, dan aplikasi telah
terhubung.  Pengolahan  bandpass,  FFT,  dan  BPM  dipindahkan  ke  server,
sedangkan SQI dipertahankan di perangkat.

5.  Pengembangan  Model  AI:  XGBoost  telah  dituning  dan  diterapkan  dengan
dua  ambang  keputusan;  pipeline  lima  MLP  telah  terintegrasi  dan  dilatih
menggunakan data kalibrasi yang tersedia.

6.  Pengujian  dan  Validasi:  Pengujian  subsistem,  enam  sesi  relawan,  analisis
mutu  sinyal,  koreksi  BPM,  dan  konsultasi  dokter  spesialis  saraf  telah
dilaksanakan.

7.  Pelaporan  dan  Publikasi:  Laporan  kemajuan,  bahan  presentasi,
dokumentasi,  dan  tiga  konten  utama  media  sosial  telah  disusun  dan
dipublikasikan.

8.  Pengajuan  HKI:  Hak Cipta Program Komputer ANTARAGA telah tercatat

dan terbit.

Dokumentasi pelaksanaan seluruh tahapan kegiatan tertera pada Lampiran 1.
BAB 4. HASIL YANG DICAPAI
4.1 Dampak Pengiklanan Media Sosial

Kampanye edukasi dan publikasi melalui pengiklanan Instagram telah selesai
terlaksana  100%  dalam  3  gelombang.  Rekapitulasi  capaian  disajikan  pada  Tabel
4.1.

Tabel 4.1 Rekapitulasi Metrik Capaian Pengiklanan Media Sosial

Metrik Capaian

Jangkauan
Tayangan
Interaksi
Kunjungan Profil
Pengikut Baru

Iklan 1
(Pengenalan
ANTARAGA)
10,358
12,403
2,336
291
6

Iklan 2
(Edukasi
Tanda Risiko)
11,380
15,332
4,237
281
9

Iklan 3
(Pengujian
ANTARAGA)
15,448
26,629
4,530
436
15

Total
Capaian

37.186
54.364
11.103
1.008
30

Peningkatan metrik tersebut menunjukkan bahwa konten yang lebih detail dan
informatif  efektif  meningkatkan  visibilitas  serta  keterlibatan  audiens  terhadap
program.
4.2 Spesifikasi Prototipe ANTARAGA

Realisasi  pembuatan  smartband  ANTARAGA  telah  mencapai  100%  dengan
spesifikasi hardware smartband ANTARAGA langsung disajikan pada Tabel 4.1.

6

Gambar 4.2 Desain Prototipe ANTARAGA
Tabel 4.2 Spesifikasi Hardware Smartband ANTARAGA

2

3

4

No

Komponen
/Modul

Spesifikasi Teknis
Hasil Realisasi

1  Mikrokontroler

ESP32-S3,
XIAO
dual-core Xtensa LX7
32-bit

Sensor
Hijau

PPG

SON1303/SEN0203
(Kanal Hijau 525 nm)

Fungsi & Hasil Pengujian

sinyal,
pencuplikan
Pusat
transmisi  Wi-Fi,  dan  firmware
penyaring SQI.
Merekam  dinamika  denyut  nadi,
dilengkapi  ferrite  bead  penekan
noise 50 Hz.

Sensor
Merah/NIR

PPG

(Merah
MAX30102
660 nm & Inframerah
880 nm)

Sumber  data  utama  Pulse  Wave
Analysis  dan  ekstraksi  indikator
fisiologis.

Manajemen
Power Supply

Baterai  LiPo
LDO RT9013-33GB

1S,

5

PCB

PCB
Mandiri

Fabrikasi

6

Enclosure

PETG 3D Printing

Pasokan  tegangan  bebas  ripple
switching dengan durasi pasokan
baterai terukur.
Pondasi  dari  seluruh  komponen
elektronik
Casing
komponen
pengguna serta benturan.

pelindung
keringat

sebagai
dari

1.  Realisasi  Hardware  &  Firmware:  Sistem  power  supply  yang  didukung
regulator  LDO  3,3V  terbukti  menjaga  kestabilan  sinyal  optik  pada  rentang
tegangan  baterai  3,0-4,2V.  Pengujian  discharge  baterai  pada  beban  500  mA
konstan  menghasilkan  kapasitas  efektif  terhitung  sebesar  813  mAh  (durasi  97
menit 35 detik — lihat Lampiran 1).

2.  Arsitektur  Pemrosesan  Sinyal:  dialihkan  dari  firmware  ke  server  VPS  untuk
menghemat  daya  dan  SRAM  ESP32-S3,  sementara  firmware  berfokus  pada
pencuplikan data dan penilaian mutu sinyal (Signal Quality Index).

3.  Aplikasi telah selesai dibangun, terhubung melalui Wifi ke smartband dan API
FastAPI di VPS (www.antaraga.web.id) untuk menampilkan tren fisiologis dan
mengirimkan notifikasi peringatan kepada keluarga melalui aplikasi.

Berikut adalah tautan video pengujian ANTARAGA: Video Luaran ANTARAGA

7

4.3 Spesifikasi Aplikasi Mobile ANTARAGA

Aplikasi  mobile  ANTARAGA  dikembangkan  menggunakan  Flutter  sebagai
antarmuka  utama  bagi  keluarga  dalam  melakukan  pemantauan  kondisi  lansia.
Aplikasi terintegrasi dengan backend melalui API sehingga data hasil pemantauan
dari smartband dapat ditampilkan pada perangkat pengguna.

 Fitur  utama  aplikasi  meliputi  autentikasi  pengguna,  pengelolaan  profil  lansia
(termasuk  dukungan  lebih  dari  satu  profil  lansia  per  akun),  koneksi  smartband
berdasarkan  Device  ID,  pemantauan  tanda  vital,  tampilan  statistik  harian,
informasi prediksi risiko stroke berbasis AI, serta asesmen ABCD2.

 Pada  halaman  dashboard,  pengguna  dapat  melihat  profil  lansia  yang  sedang
dipantau, status koneksi perangkat, nilai tekanan darah, detak jantung, gula darah,
serta informasi tingkat risiko stroke (kategori Rendah/Sedang/Tinggi) berdasarkan
model  AI.  Hasil  pemantauan  juga  dapat  ditampilkan  dalam  bentuk  statistik  dan
timeline  untuk  membantu  keluarga  melihat  perubahan  kondisi  dari  waktu  ke
waktu.

 Aplikasi  juga  menyediakan  asesmen  ABCD2  untuk  membantu  keluarga
melakukan penilaian awal berdasarkan faktor klinis yang relevan.  Hasil asesmen
ditampilkan  dalam  bentuk  skor,  kategori  risiko,  serta  estimasi  risiko  stroke
berikutnya  dalam  periode  2,  7,  dan  90  hari  berdasarkan  kohort  validasi  ABCD2
(Spampinato  dkk.,  2022)  untuk  menjaga  hasil  yang  ditampilkan
tetap
berlandaskan literatur klinis yang tervalidasi.

Gambar 4.3 Flowchart Pengiriman Data Alat ke Aplikasi

4.4 Hasil Pelatihan dan Pengujian
4.4.1 Hasil Pelatihan Model XGBoost

Dataset  model  risiko  memiliki  class  imbalance  dengan  kelas  stroke  sekitar
4,87%.  Karena  akurasi  dapat  menyesatkan  pada  kondisi  tersebut,  evaluasi
menggunakan  Average  Precision  dan  recall.  XGBoost  dengan  scale_pos_weight
19,55 dibandingkan dengan HistGradientBoosting melalui RandomizedSearchCV
dan StratifiedKFold lima lipatan. Empat puluh kombinasi parameter melalui lima
validasi silang menghasilkan 200 proses pelatihan.

Tabel 4.3 Evaluasi Model XGBoost

Metrik/Parameter

XGBoost

HistGradientBoosting

Average Precision terbaik

0,2313

0,2281

Penanganan imbalance

scale_pos_weight =
19,55

Model pembanding

Keputusan

Dipilih

Tidak dipilih

Threshold awal

0,705; F1 = 0,2946

Threshold sensitivitas

0,042; recall = 0,973

-

-

8

Gambar 4.4 Perbandingan Recall Model XGBoost

Threshold  awal  0,705  dipilih  berdasarkan  F1-score  terbaik  sebesar  0,2946.
Optimasi  berikutnya  memprioritaskan  sensitivitas  sistem  peringatan  dan
menghasilkan threshold 0,042 dengan recall 0,973,  yaitu 73 dari 75 kasus stroke
pada data uji berhasil terdeteksi.
4.4.2 Hasil Pelatihan Model MLP

MLP  telah  dibangun  dan  terintegrasi  dengan  dashboard  sehingga  pelatihan
ulang  dapat  dilakukan  ketika  tersedia  data  baru.  Kapasitas  model  diskalakan
otomatis mengikuti jumlah data kalibrasi yang tersedia (1 lapisan 4 neuron untuk
data  di  bawah  10  subjek,  2  lapisan  untuk  data  lebih  besar)  supaya  model  tidak
menghafal  data  yang  masih  sedikit.  Evaluasi  kuantitatif  menggunakan  MAE,
RMSE,  MAPE,  dan  R²  dengan  skema  validasi  Leave-One-Subject-Out  (setiap
subjek  diuji  oleh  model  yang  tidak  pernah  melihat  data  subjek  tersebut  saat
dilatih).

Hasil  pelatihan  pada  11  subjek  kalibrasi  yang  tersedia  hingga  5  September
2026  disajikan  pada  Tabel  4.4.  Nilai  R²  digunakan  sebagai  indikator  utama
kejujuran model (R² mendekati atau di atas nol berarti model benar-benar belajar
pola, R² negatif berarti model belum lebih baik daripada menebak nilai rata-rata).

[DOKUMENTASI Hasil Training dan akurasi model MLP]

9

Tabel 4.4 Evaluasi Model MLP per Parameter (LOO, n=11 subjek)

Parameter  N  MAE

R²

Akurasi Sesi (%)

Catatan

Gula Darah  11

Kolesterol

11

Asam Urat

11

Sistolik

11

Diastolik

11

47.2
mg/dL

27.08
mg/dL

1.14
mg/dL

41.5
mmHg

20.27
mmHg

-1.9879

59.97%

Perlu Data Lebih

-0.3043

86,17%

Baik

-1.6326

78.96%

Cukup

-8.8337

71.7%

Cukup

-5.7345

76.02%

Cukup

4.4.3 Hasil Pengujian Prototipe pada Relawan

Pengujian  relawan  dimulai  pada  3  Agustus  2026  untuk  memvalidasi  SOP,
konektivitas, kenyamanan, kualitas sinyal, dan alur penyimpanan data. Enam sesi
sampai 5 September 2026 telah menghasilkan data dari sebelas relawan.

Tabel 4.5

Alat Medis

Prediksi

Akurasi (%)

TD
(m
m
Hg
)

ren
tan
g

GL
U
(mg/
Dl)

rent
ang

C
H
OL
(m
g/d
L)

ren
dan
g

UA
(m
g/d
L)

TD
(m
mH
g)

ren
tan
g

rent
ang

GL
U
(m
g/
Dl)

ren
tan
g

C
H
OL
(m
g/d
L)

ren
tan
g

UA
(m
g/d
L)

TD
(m
mH
g)

rent
ang

ren
tan
g

GL
U
(m
g/
Dl)

ren
tan
g

C
H
OL
(m
g/d
L)

ren
tan
g

UA
(m
g/d
L)

ren
tan
g

Riwa
yat
Relaw
an

N

Stroke  2

Tidak
Stroke

9

10

Sistem  kecerdasan  buatan  dikembangkan  menggunakan  model  XGBoost
untuk  prediksi  risiko  stroke  dan  Multi-Layer  Perceptron  (MLP)  untuk  kalibrasi
sinyal PPG. Metrik hasil evaluasi realisasi model disajikan pada Tabel 4.6.

Tabel 4.6 Metrik Evaluasi Performa Model AI Terhadap Data Training dan
Pembacaan Alat

Parameter Evaluasi

Recall (Sensitivitas)
XGBoost

Skor ROC-AUC
XGBoost

Target /
Standar

> 90%

Hasil Realisasi

97,3% (73/75 kasus
terdeteksi)

> 0,80

0,823

Status
Ketercapaian

Sangat Baik

Memenuhi
Standar

Ambang Keputusan
(Threshold)

Out-of-Fold
Margin

0,042 (Deteksi) / 0,705
(Risiko Tinggi)

Sesuai Standar
AHA ABCD²

Perfusi Inframerah
(PPG)

0,02 – 2,00
‰

0,74 – 1,77 ‰

Sinyal Normal

Latensi Transmisi
Sistem

< 3 Detik

< 2 Detik (Wifi ke
VPS)

Sangat Cepat

Pengujian  fungsional  pada  11  relawan  (selengkapnya  pada  Lampiran  1)
menunjukkan tingkat kepuasan 100%, dengan pembacaan sinyal optik PPG yang
stabil  pada  indeks  perfusi  normal  (0,74-1,77‰)  dan  tangguh  terhadap  gerakan
ringan. Dalam pengembangan model AI, nilai threshold standar (0,50) disesuaikan
menjadi  0,042  (deteksi  biner)  dan  0,705  (risiko  tinggi)  melalui  evaluasi  Out-of-
Fold (OOF) serta kurva Precision-Recall guna mengatasi ketidakseimbangan data.
Kombinasi  penurunan  threshold  dan  penyeimbangan  bobot  (scale_pos_weight  =
19,55)  sukses  mendongkrak  sensitivitas  (Recall)  hingga  97,3%,  selaras  dengan
standar klinis AHA/ASA (skor ABCD²) yang memprioritaskan minimalisasi false
negative agar tidak ada penderita stroke yang terlewat. Untuk pemrosesan sinyal,
sistem  backend  menggunakan  penyaring  lonjakan  BPM  4  lapis  guna  menekan
artefak gerak, serta memanfaatkan 5 model Multi-Layer Perceptron (MLP) untuk
menyusun  estimasi  indikator  kesehatan  harian.  Sebagai  penguatan  akhir,  seluruh
alur kuesioner kualitatif, instrumen ABCD2, dan skenario rujukan prarumah sakit
telah  melalui  tahapan  validasi  klinis  secara  langsung  bersama  Dokter  Spesialis
Saraf pada 7 Agustus 2026.
1.  .
BAB 5. POTENSI HASIL
5.1 Potensi Prototipe ANTARAGA Berdampak

ANTARAGA memiliki potensi menjadi sistem pendukung pemantauan faktor
risiko  stroke  pada  lansia  di  lingkungan  keluarga  melalui  integrasi  wearable,
analisis  data,  dan  aplikasi  mobile.  Informasi  yang  dihasilkan  dapat  membantu

11

keluarga  memantau  kondisi  secara  lebih  terstruktur  dan  mendorong  evaluasi
medis  ketika  ditemukan  kondisi  yang  membutuhkan  perhatian.  Sistem  tetap
diposisikan sebagai pendukung keputusan, bukan alat diagnosis.
5.2 Potensi Hak Kekayaan Intelektual

Tim ANTARAGA telah  memperoleh Hak Cipta untuk jenis ciptaan Program
Komputer  berjudul  "ANTARAGA:  Smartband  Berbasis  Multi-Wavelength  PPG
dengan  Artificial  Intelligence  Terintegrasi  Aplikasi  Mobile  untuk  Deteksi  Dini
Risiko Stroke Iskemik pada Lansia" sebagai bentuk perlindungan  terhadap karya
yang dikembangkan. Sertifikat Hak Cipta ANTARAGA tercantum pada Lampiran
5.
5.3 Potensi Pengembangan Prototipe ANTARAGA

Gambar 5.1 Tahapan Pengembangan ANTARAGA

lansia  yang

terhadap  populasi

secara  bertahap,  dimulai  dari
Pengembangan  ANTARAGA  dilakukan
penambahan  data  kalibrasi,  peningkatan  performa  model  AI,  penyempurnaan
integrasi  real-time,  serta  evaluasi  error,  latensi,  dan  daya  tahan  baterai  pada  1
tahun  pertama.  Pada  periode  1  sampai  3  tahun,  pengembangan  diarahkan  pada
representatif,  peningkatan
validasi
kenyamanan  dan  kestabilan  perangkat,  penguatan  keamanan  data,  evaluasi
bersama  tenaga  kesehatan,  serta  kajian  regulasi.  Setelah  kesiapan  teknis  dan
regulasi  terpenuhi,  pengembangan  dapat  diarahkan  pada  kajian  kelayakan
produksi dan komersialisasi ANTARAGA.
BAB 6. RENCANA TAHAPAN BERIKUTNYA
target  pelaksanaan  hingga  mencapai  100%,
Sebagai  upaya  menuntaskan
serangkaian  kegiatan  lanjutan  telah  dijadwalkan  untuk  sisa  masa  pelaksanaan
program, dengan rincian pada tabel 6.1.

lebih

Tabel 6.1 Rencana Anggaran Berikutnya

No

Kegiatan

PIC

Dana

Waktu
Pelaksanaan

1

2

Penyusunan Bahan PPT &
Simulasi PKP PKM

Pengujian 7 &
Penyempurnaan Model AI

Kadek, Zeven

Rp0

Bulan ke-4

Kadek, Adam, Ally

Rp0

Bulan ke-4

No

Kegiatan

PIC

Dana

12

Waktu
Pelaksanaan

3  Penyusunan Artikel Ilmiah

Tiwi, Zeven

Rp0

Bulan ke-4

4  Penyusunan Laporan Akhir  Seluruh Anggota Tim  Rp0

Bulan ke-4

DAFTAR PUSTAKA
Capirossi,  C.,  Laiso,  A.,  Renieri,  L.,  Capasso,  F.  dan  Limbucci,  N.  (2023)
“Epidemiology,  organization,  diagnosis  and  treatment  of  acute  ischemic
stroke”,  European
100527.
https://doi.org/10.1016/j.ejro.2023.100527.

of  Radiology  Open,

Journal

11,

El-Hajj,  C.  dan  Kyriacou,  P.A.  (2021)  “Cuffless  blood  pressure  estimation  from
PPG  signals  and  its  derivatives  using  deep  learning  models”,  Biomedical
Signal
102984.
https://doi.org/10.1016/j.bspc.2021.102984.

Processing

Control,

and

70,

Feigin,  V.L.,  Brainin,  M.,  Norrving,  B.,  Martins,  S.O.,  Pandian,  J.,  Lindsay,  P.,
Grupper,  M.F.  dan  Rautalin,  I.  (2025)  “World  Stroke  Organization:  Global
Stroke  Fact  Sheet  2025”,  International  Journal  of  Stroke,  20(2),  132-144.
https://doi.org/10.1177/17474930241308142.

Kim, K.B. dan Baek, H.J. (2023) “Photoplethysmography in wearable devices: a
comprehensive  review  of  technological  advances,  current  challenges,  and
2923.
future
https://doi.org/10.3390/electronics12132923.

Electronics,

directions”,

12(13),

Luo,  J.,  Yuan,  Y.  dan  Xu,  S.  (2025)  “Improving  GBDT  performance  on
imbalanced  datasets:  An  empirical  study  of  class-balanced  loss  functions”,
Neurocomputing,
129896.
634,
https://doi.org/10.1016/j.neucom.2025.129896.

Potisopha, W., Vuckovic, K.M., DeVon, H.A., Park, C.G., Phutthikhamin, N. dan
Hershberger,  P.E.  (2023)  “Decision  delay  is  a  significant  contributor  to
prehospital  delay  for  stroke  symptoms”,  Western  Journal  of  Nursing
Research, 45(1), 55-66. https://doi.org/10.1177/01939459221105827.

Spampinato,  M.D.  dkk.  (2022)  “ABCD2,  ABCD2-I,  and  OTTAWA  scores  for
stroke  risk  assessment:  a  direct  retrospective  comparison”,  Internal  and
Emergency  Medicine,  17(8),  2391-2401.  https://doi.org/10.1007/s11739-022-
03074-x.

Writing  Committee  for  the  PERSIST  Collaborators  (2025)  “Long-term  risk  of
stroke after transient ischemic attack or minor stroke: a systematic review and
1508-1519.
meta-analysis”,
https://doi.org/10.1001/jama.2025.2033.

333(17),

JAMA,

13

LAMPIRAN
Lampiran 1. Dokumentasi Pengembangan dan Pengujian ANTARAGA
L.1.1 Realisasi Prototipe dan Ekosistem ANTARAGA

No

Tabel L.1 Realisasi Prototipe dan Ekosistem ANTARAGA
Keterangan
Prototipe final tampak
depan, belakang,
samping

Dokumentasi

Gambar L.1 foto prototipe tampak depan

Gambar L.2 foto prototipe tampak samping

14

Gambar L.3 foto prototipe tampak belakang

Smartband ketika
digunakan

PCB final

Gambar L.4 foto prototipe ketika dipakai

Gambar L.5 foto PCB terintegrasi komponen
elektronik

Casing PETG

15

Gambar L.6 foto hasil cetak casing PETG

Tampilan aplikasi
mobile

Gambar L.7 foto tampilan dashboard aplikasi
mobile ANTARAGA

Diagram arsitektur
aktual smartband–
server–aplikasi bila
diperlukan.

L.1.2 Perubahan dan Penyempurnaan Desain

Aspek Proposal

Realisasi

Alasan/Implikasi

XIAO ESP32-C3

XIAO ESP32-S3

Keterbatasan SRAM dan
beban komunikasi/pemrosesan

Aspek Proposal

Realisasi

Alasan/Implikasi

16

Pemrosesan sinyal
pada perangkat

Pemrosesan utama
pada server

Model Gradient
Boosting/MLP
tunggal

XGBoost untuk risiko;
MLP untuk kalibrasi

Mengurangi beban perangkat
dan memudahkan pembaruan
algoritma

XGBoost dipilih dari
perbandingan langsung dengan
HistGradientBoosting (Tabel
4.3, BAB 4.4.1): Average
Precision lebih tinggi (0,2313
vs 0,2281) dan mendukung
scale_pos_weight bawaan
untuk menangani class
imbalance (kelas stroke
~4,87%) tanpa perlu
resampling data medis yang
jumlahnya terbatas. MLP
dipisah khusus untuk kalibrasi
karena tersedianya data
pasangan sinyal PPG-alat
invasif dari pengujian relawan.

Baterai 900 mAh

Li-Po 1S 950 mAh
pada prototipe uji

Penyesuaian kapasitas sumber
daya

1.3 Pengujian Teknis Prototipe
No

Pengujian
Manajemen
sistem daya

Dokumentasi

Gambar L.9 Analisis output ketika menggunakan buck
converter

17

Gambar L.10 Analisis noise ketika menggunakan boost
converter

Gambar L.11 Datasheet Regulator LDO RT9013-33GB

Pengujian
SON1303

Gambar L.12 Interfensi noise 50Hz pada sinyal output
sensor SON1303

18

Gambar L.13 Sinyal output sensor SON1303 setelah
optimalisasi

Pengujian
MAX30102

Gambar L.14 Sensor MAX30102 rusak karena cacat pabrik

Gambar L.15 Malfungsi LED channel IR pada Sensor
MAX30102

Gambar L.16 Sensor baru MAX30102 dan berhasil
berfungsi

19

Gambar L.17 Sinyal output sensor MAX30102 pada channel
RED dan IR setelah optimalisasi

Gambar L.17 Perbandingan hasil pembacaan sensor
MAX30102 dengan alat oximeter terstandar (oximeter
mendeteksi 80bpm, sedangkan di sensor log pada monitor
terdeteksi 79bpm, yang artinya error hanya terpaut 1 bpm)

Charge-
discharge
baterai

Gambar L.17 Uji discharge baterai lipo 1s dengan beban
500mA

Desain
Layout PCB

20

Gambar L.18 Dokumentasi desain layout PCB

Inspeksi PCB

Gambar L.19 Sinyal output sensor SON1303 setelah
optimalisasi

Pengujian
casing

Gambar L.20 casing tidak bisa menutup rapat

21

Gambar L.21 hasil casing setelah penyesuaian

Pengiriman
data dan
dashboard
server

Gambar L.22 Memastikan data dari perangkat bisa
terkirim dan terbaca dengan baik di server

L.1.4 Pengujian Terintegrasi pada Relawan

subjek

Enam kegiatan pengujian tercatat pada logbook sampai 5 September 2026.
Sebelas  kode
telah  dilakukan  pengujian
menggunakan  ANTARAGA.  Identitas  subjek  disamarkan  untuk  menjaga
kerahasiaan. Bagian ini menyajikan tiga hal per relawan: data profil, perbandingan
alat medis vs prediksi MLP, dan hasil deteksi risiko stroke.

(S001-S011)

relawan

Field
Usia
Gender
Kondisi
Pengambilan
Heart Rate
(Oximeter)
Heart Rate
(Pembacaan
Sensor
ANTARAGA)
Merokok
Riwayat
Penyakit

S001
20
Laki-laki
Sewaktu
(tidak puasa)

S002

S003

S004

57

75

70

Perempuan
Sewaktu
(tidak puasa)

Perempuan
Sewaktu
(tidak puasa)

Perempuan
Sewaktu
(tidak puasa)

70bpm

Tidak
Tidak

Tidak
Tidak

Tidak
Tidak

Tidak
Tidak

Jantung

Status Bekerja  Ya

(Mahasiswa)
Kota

22

Tidak (Sudah
Pensiun)
Kota

Tidak (Sudah
Pensiun)
Kota

Tidak (Sudah
Pensiun)
Kota

Tipe Tempat
Tinggal
Riwayat
Diabetes
Riwayat
Stroke
Keluarga
Riwayat
Stroke Pribadi
Tanggal
Pengujian

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Ya

3 Agustus
2026

6 Agustus
2026

6 Agustus
2026

10 Agustus
2026

S005
76
Laki-laki
Sewaktu
(tidak puasa)
Tidak
Tidak

Field
Usia
Gender
Kondisi
Pengambilan
Merokok
Riwayat
Penyakit
Jantung
Status Bekerja  Mahasiswa

(Ya)

Kota

S006

S007

S008

75

75

62

Perempuan
Sewaktu
(tidak puasa)
Tidak
Tidak

Laki-laki
Sewaktu
(tidak puasa)
Ya
Tidak

Laki-laki
Sewaktu
(tidak puasa)
Tidak
Tidak

Sudah
Pensiun
(Tidak)
Kota

Sudah
Pensiun
(Tidak)
Kota

Sudah
Pensiun
(Tidak)
Kota

Tipe Tempat
Tinggal
Riwayat
Diabetes
Riwayat
Stroke
Keluarga
Riwayat
Stroke Pribadi

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Ya

Tidak

Tidak

Ys

Ya

Ys

Tanggal
Pengujian

10 Agustus
2026

14 Agustus
2026

2 September
2026

2 September
2026

Field

S009

S010

S011

23

Usia
Gender
Kondisi
Pengambilan
Merokok
Riwayat Penyakit
Jantung

62
Perempuan
Sewaktu (tidak
puasa)
Tidak
Tidak

Status Bekerja

Mahasiswa (Ya)

Kota

Tipe Tempat
Tinggal
Riwayat Diabetes  Tidak
Tidak
Riwayat Stroke
Keluarga
Riwayat Stroke
Pribadi

Tidak

63

80

Laki-laki
Sewaktu (tidak
puasa)
Tidak
Tidak

Perempuan
Sewaktu (tidak
puasa)
Ya
Tidak

Sudah Pensiun
(Tidak)
Kota

Sudah Pensiun
(Tidak)
Kota

Tidak
Tidak

Tidak

Tidak
Ya

Ys

Tanggal
Pengujian

2 September 2026  5 September 2026  5 September 2026

Tabel L.4b Data Alat Medis vs Prediksi MLP per Relawan (ada di PDF report per
subjek)

Alat

Alat
Terstandar
(Aktual)

Hasil Prediksi
Model MLP

Akurasi (%)

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Elvasense 3in1 EMS10 (Gula
Darah)

S001

125,0 mmHg  142,9 mmHg

77,0 mmHg

97,4 mmHg

119,0 mg/dL  149,7 mg/dL

Elvasense 3in1 EMS10
(Kolesterol Total)

212,0 mg/dL  245,0 mg/dL

85.7%

73.6%

74.2%

84.4%

24

6,3 mg/dL

7,4 mg/dL

82.8%

Subjek

S001:

Elvasense 3in1 EMS10 (Asam
Urat)

Detail

Link
https://drive.google.com/file/d/1CS2o-
9yniulSWwVkuIPutbpHx98RcJ2O/view?usp=sharing

Data

PDF

Relawan

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Elvasense 3in1 EMS10 (Gula
Darah)

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP
S002

173,0 mmHg

167,3 mmHg

102,0 mmHg

94,5 mmHg

119,0 mg/dL

149,7 mg/dL

Elvasense 3in1 EMS10
(Kolesterol Total)

Elvasense 3in1 EMS10 (Asam
Urat)

200,0 mg/dL

210,3 mg/dL

4,6 mg/dL

5,1 mg/dL

Akurasi (%)

96.7%

92.7%

74.2%

94.9%

89.5%

Detail

Link
Relawan
https://drive.google.com/file/d/1pCLOfgnhJuSrb7YcqY-
Ls1ApIT3PKDxy/view?usp=sharing

Data

PDF

Subjek

S002:

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Elvasense 3in1 EMS10 (Gula
Darah)

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

S003

153,0 mmHg

116,8 mmHg

94,0 mmHg

98,9 mmHg

183,0 mg/dL

177,5 mg/dL

Akurasi (%)

76.4%

94.8%

97.0%

25

Elvasense 3in1 EMS10 (Kolesterol
Total)

Elvasense 3in1 EMS10 (Asam
Urat)

232,0 mg/dL

210,6 mg/dL

4,5 mg/dL

4,8 mg/dL

90.8%

94.8%

Detail

Link
https://drive.google.com/file/d/1RwDgYkxOT3l3_dqCboQhms6eUHkYhgox/vie
w?usp=sharing

Relawan

Subjek

Data

PDF

S003:

Alat

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

Akurasi
(%)

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

S004

157,0 mmHg  125,8

88,0 mmHg

mmHg

103,2
mmHg

Elvasense 3in1 EMS10 (Gula Darah)  153,0 mg/dL  194,2
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

269,0 mg/dL  229,5
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

4,8 mg/dL

5,6 mg/dL

76.4%

94.8%

73.1%

85.3%

82.4%

Detail

Link
S004:
https://drive.google.com/file/d/19AeuPuwaMgBLVGEPcYWqU70AzM9Q2dn5/v
iew?usp=sharing

Relawan

Subjek

Data

PDF

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

Akurasi
(%)

S005

166,0 mmHg  157,0

mmHg

92.6%

26

Tensimeter (Tekanan Darah
Diastolik)

86,0 mmHg

Elvasense 3in1 EMS10 (Gula Darah)  98,0 mg/dL

108,2
mmHg

111,1
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

244,0 mg/dL  283,5
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

5,3 mg/dL

5,9 mg/dL

74.2%

86.6%

83.8%

88.9%

Detail

Link
S005:
https://drive.google.com/file/d/1sIM8ZUv5oE53P0_TElQoTLvETSeYVfxE/view
?usp=sharing

Relawan

Subjek

Data

PDF

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

Akurasi
(%)

S006

157,0 mmHg  114,3

mmHg

78.9%

88,0 mmHg

95,7 mmHg

Elvasense 3in1 EMS10 (Gula Darah)  94,0 mg/dL

102,0
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

269,0 mg/dL  210,7
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

6,3 mg/dL

5,8 mg/dL

77.3%

91.4%

78.3%

92.6%

Detail

Link
https://drive.google.com/file/d/1kYKsTTWkAKno88tQp5D-
rT9K8m389G8r/view?usp=sharing

Relawan

Data

PDF

Subjek

S006:

Alat

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

Akurasi
(%)

S007

27

142,0 mmHg  144,9

mmHg

97.9%

56,0 mmHg

69,0 mmHg

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Elvasense 3in1 EMS10 (Gula Darah)  183,0 mg/dL  187,0
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

268,0 mg/dL  282,9
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

7,2 mg/dL

8,0 mg/dL

76.9%

97.8%

94.4%

88.6%

Detail

Link
https://drive.google.com/file/d/1KiY25FzykeTv-
SikBYk39FXuU_7AJk99/view?usp=sharing

Data

PDF

Relawan

Subjek

S007:

Alat

Alat
Terstandar
(Aktual)

Hasil
Prediksi
Model MLP

Akurasi
(%)

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

S008

131,0 mmHg  140,2

91,0 mmHg

mmHg

115,1
mmHg

Elvasense 3in1 EMS10 (Gula Darah)  171,0 mg/dL  185,5
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

261,0 mg/dL  263,8
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

5,0 mg/dL

5,8 mg/dL

93.0%

73.5%

91.5%

98.9%

83.7%

Detail

Link
https://drive.google.com/file/d/1r6m8oggO5Z2teOi6PX9c14SJiKlntxds/view?usp
=sharing

Relawan

Subjek

Data

PDF

S008:

Alat

Alat
Terstandar

Hasil
Prediksi

Akurasi
(%)

28

(Aktual)   Model MLP

S009

121,0 mmHg  115,9

mmHg

95.8%

71,0 mmHg

86,8 mmHg

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Elvasense 3in1 EMS10 (Gula Darah)  157,0 mg/dL  151,7
mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

206,0 mg/dL  201,2
mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

3,7 mg/dL

4,1 mg/dL

77.8%

96.6%

97.7%

89.8%

Detail

Link
https://drive.google.com/file/d/1J6LQEDrSukw5q0sGJcLys-Q_O2KC1n-
F/view?usp=sharing

Relawan

Subjek

Data

PDF

S009:

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

Alat
Terstandar
(Aktual)

Hasil Prediksi
Model MLP

Akurasi
(%)

S010

163,0 mmHg

137,9 mmHg

97,0 mmHg

114,4 mmHg

Elvasense 3in1 EMS10 (Gula Darah)  198,0 mg/dL

183,9 mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

194,0 mg/dL

213,1 mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

5,8 mg/dL

6,3 mg/dL

84.6%

82.1%

92.9%

90.1%

90.8%

Detail

Link
https://drive.google.com/file/d/1l3XjZoZv5FgH9UwvuxK18TGLEu29mdGp/vie
w?usp=sharing

Relawan

Subjek

Data

PDF

S010:

29

Alat
Terstandar
(Aktual)

Hasil Prediksi
Model MLP

Akurasi
(%)

S011

151,0 mmHg

123,2 mmHg

89,0 mmHg

104,3 mmHg

Alat

Tensimeter (Tekanan Darah
Sistolilk)

Tensimeter (Tekanan Darah
Diastolik)

81.6%

82.8%

92.9%

89.5%

83.7%

Elvasense 3in1 EMS10 (Gula Darah)  121,0 mg/dL

129,6 mg/dL

Elvasense 3in1 EMS10 (Kolesterol
Total)

245,0 mg/dL

219,3 mg/dL

Elvasense 3in1 EMS10 (Asam Urat)

5,3 mg/dL

6,2 mg/dL

Detail

Link
https://drive.google.com/file/d/10cKU4L39VlXMZpee0YtHYg6OaRdyub_V/vie
w?usp=sharing

Relawan

Subjek

Data

PDF

S011:

Tabel  L.4c  Hasil  Deteksi  Risiko  Stroke  per  Relawan  (ada  di  PDF  report  per
subjek)
Subjek
S001
S002
S003

Kategori Risiko
Rendah
Rendah
Sedang

Faktor Risiko Terpenuhi
Kolesterol Total Tinggi
Hipertensi dan Kolesterol Total Tinggi
Hipertensi, Kolesterol Total Tinggi, dan usia 75
tahun (≥ 75 tahun)
Hipertensi, Kolesterol Total Tinggi, dan
Riwayat Stroke Pribadi
Hipertensi, Kolesterol Total Tinggi, dan usia
76 tahun (≥ 75 tahun)
Hipertensi, Kolesterol Total Tinggi, dan usia
75 tahun (≥ 75 tahun)
Hipertensi, Kolesterol Total Tinggi, Asam Urat,
Riwayat Stroke Keluarga, dan Riwayat Stroke
Pribadi
Hipertensi dan Kolesterol Total Tinggi
Hipertensi, Kolesterol Total Tinggi, dan usia
80 tahun (≥ 75 tahun)
Hipertensi

Tinggi

Sedang

Sedang

Tinggi

Rendah
Sedang

Rendah

S004

S005

S006

S007

S008
S009

S010

S011

Hipertensi, Kolesterol Total Tinggi, dan usia 80
tahun (≥ 75 tahun)

Sedang

30

1.5 Evaluasi Model AI dan Pemrosesan Sinyal
XGBoost
No  Keterangan

Dokumentasi

confusion matrix
Precision-Recall curve
ROC curve jika digunakan
hasil cross-validation
Perbandingan model
threshold 0,042
threshold 0,705
recall 97,3%
parameter/tuning penting

MLP
No  Keterangan

Dokumentasi

Pipeline lima model
screenshot dashboard pelatihan
Data kalibrasi
Grafik training bila relevan
MAE/RMSE/MAPE/R² hanya jika memang
sudah tersedia.

1.6 Bukti Luaran Digital ANTARAGA
Aplikasi mobile
No  Keterangan

Dokumentasi

Pendaftaran google play
•  screenshot Google Play Console;
•  nama aplikasi ANTARAGA;
•  status pendaftaran/rilis;
•  tanggal publikasi jika memang tercantum;
•  sensor/crop email dan informasi sensitif.

Video Simulasi dan Pengujian

31

Media Sosial
Screenshoot smua konten

1.7 Validasi Medis dan Kepatuhan Etik
Ethical Clearance

informed consent kosong/teranonimisasi

dokumentasi konsultasi dokter spesialis saraf

ringkasan hasil konsultasi/validasi

bukti validasi alur ABCD2 jika tersedia

Lampiran 1. Dokumentasi Pengembangan dan Pengujian ANTARAGA
1.1 Dokumentasi Prototipe ANTARAGA
Foto prototipe final, PCB,  casing, sensor, prototipe  saat digunakan,  aplikasi, dan
dashboard.
1.2 Perubahan dan Penyempurnaan Desain
Matriks proposal vs realisasi, misalnya ESP32-C3 → ESP32-S3, perubahan lokasi
pemrosesan sinyal, baterai, arsitektur AI, dan integrasi aplikasi. Matriks semacam
ini sebenarnya sudah ada di draftmu.
1.3 Pengujian Subsistem
Pengujian  daya,  baterai,  SON1303,  MAX30102,  PCB,  casing,  konektivitas,
dashboard, kualitas sinyal, latensi, dan penyimpanan data.
1.4 Pengujian Relawan
Dokumentasi  sesi,  kode  subjek  anonim,  data  alat  medis  pembanding,  hasil
ANTARAGA,  error/selisih,  dan  catatan  hasil  pengujian.  Drafmu  sudah  punya
enam kode subjek serta penghitungan ulang BPM yang bisa dijadikan dasar.
1.5 Pengembangan dan Evaluasi Model AI
XGBoost,
perbandingan model, serta dokumentasi pelatihan MLP.
1.6 Integrasi Aplikasi dan Server
Tampilan  aplikasi,  dashboard,  API,  alur  pengiriman  data,  notifikasi  risiko,  dan
asesmen ABCD2.

confusion  matrix,  ROC/Precision-Recall,

threshold,

recall,

32

Lampiran 2. Tabel Penggunaan Dana Belmawa

Rincian  penggunaan  dana  Belmawa  yang  telah  direalisasikan  sepenuhnya
untuk  operasional  program  disajikan  pada  tabel  berikut,  dengan  sisa  saldo  akhir
sebesar Rp0.

BAHAN HABIS PAKAI (MAKS 60%)

No.

Tanggal
Pengeluaran

Uraian

Jumlah
Pembelian

Harga
Satuan
(Rp.)

Satuan
(Lembar,
Buah, dll)

Jumlah

1  12 Juni 2026

PPG Heart Rate Monitor Sensor for
Arduino Analog/Digital Gravity

2  12 Juni 2026

3  13 Juni 2026

4  13 Juni 2026

5  13 Juni 2026

6  13 Juni 2026

7  13 Juni 2026

20mm 22mm Silicone Strap for
Huawei GT 2 3 4 Samsung Galaxy
Watch 7 6 5 4 Amazfit Garmin Sport
Breathable Strap

Seeed Studio XIAO ESP32-C3
Development Board Mini WiFi
Bluetooth BLE RISC-V Type-C
Module

KABEL EXTRA SOFT SILICON
AWG HIGH TEMPERATURE
KABEL AWG LENTUR 14AWG -
30AWG AWG 14 16 18 20 22 24 2
putih

KABEL EXTRA SOFT SILICON
AWG HIGH TEMPERATURE
KABEL AWG LENTUR 14AWG -
30AWG AWG 14 16 18 20 22 24 2
merah

MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (Pembelian 1)

MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (pembelian 2)

8  13 Juni 2026  Battery Li-Polymer 3.7V 950mAH

9  28 Juni 2026

10  28 Juni 2026

11  28 Juni 2026

12

2 Juli 2026

13

2 Juli 2026

JST SH 1mm 1.0mm Head
Connector Konektor Pin Leads
Housing Shell Variasi 4P

JST SH 1mm 1.0mm Head
Connector Konektor Pin Leads
Housing Shell Variasi 2P

JST SH 1mm 1.0mm Head
Connector Konektor Pin Leads
Housing Shell Variasi 3P

USB Type-C Female Soket Power
Charger Port Waterproof Kabel
10cm Socket PH2.0

MINI SWITCH TOGLE SWITCH
ON OFF SAKLAR SENTER HI
QUALITY BAHAN TEMBAGAA
MURNI UJUNG KAKI OVAL

2

2

Rp323.000

pcs

Rp646.000

Rp20.300

pasang

Rp40.600

2

Rp199.000

pcs

Rp398.000

2

Rp5.000

pcs

Rp10.000

2

Rp5.000

pcs

Rp10.000

1

1

3

Rp575.000

pcs

Rp575.000

Rp575.000

pcs

Rp575.000

Rp90.000

pcs

Rp270.000

10

Rp2.000

pcs

Rp20.000

10

Rp2.000

pcs

Rp20.000

10

Rp2.000

pcs

Rp20.000

2

Rp11.900

pcs

Rp23.800

10

Rp1.500

pcs

Rp15.000

(BUKAN KOTAK)

14

2 Juli 2026

TP5000 3.6V / 4.2V 1A DC 4.5V-
9V Lithium Battery Charger Module

15

2 Juli 2026

16  10 Juli 2026

17  10 Juli 2026

18  10 Juli 2026

19  10 Juli 2026

20  10 Juli 2026

21  17 Juli 2026

RT9013-33GB Fixed 3.3V 500mA
Linear Volta ge Regulators LDO
SOT-23-5 WJ Richtek Technology

MAX30102 Pulse Oximeter and
Heart Rate Sensor Detak Jantung
Sensor

eSUN PETG Basic 3D Filament
Cost Effective High Strength 3D
Printing Filament - White

DIODES DMP2130L-7 Mosfet P-
Channel SMD3A 20V LG
EBK61913701 mark MP1

SAMWHA Ferrite Bead 1000 Ohm
1K SMD 0805 CB2012GM102E
Beads

SAMSUNG Ferrite Bead 60 Ohm
SMD 1210 CIB32P600NE Beads

XIAO ESP32S3 Original Board IoT
Development Kit - Dual Core WiFi
Bluetooth 5.0 BLE Microcontroller

22  18 Juli 2026

Resistor 0805 1M

23  18 Juli 2026

Resistor 0805 100K

24  18 Juli 2026

Resistor 0805 10K

25  18 Juli 2026

Resistor 0805 6KB

26  18 Juli 2026

avx Type A 10uF 16V

27  18 Juli 2026

10uF 35V SMD Capacitor

28  18 Juli 2026

LED 3mm diffused (green)

29  29 Juli 2026

Pembelian Hosting VPS

30

10 Agustus
2026

31  2 September

Strip Alat Cek 3in1 Elvasense (Gula
Darah/Kolesterol/Asam Urat)
Bundling 3 Box + Lancet

Strip Alat Cek 3in1 Elvasense (Gula
Darah/Kolesterol/Asam Urat) CHOL
10'S

SubTotal (Rp)

SEWA DAN JASA (MAKS 15%)

No.

Tanggal
Pengeluaran

Uraian

1

2

3

4

22 Juli 2026

3D Print Base Casing

22 Juli 2026

3D Print Cover Casing

23 Juli 2026

3D Print Base Casing

23 Juli 2026

3D Print Cover Casing

33

1

5

1

2

5

10

10

1

5

5

5

5

4

4

5

4

1

1

Rp20.000

pcs

Rp20.000

Rp3.405

pcs

Rp17.025

Rp27.200

pcs

Rp27.200

Rp250.000

kg

Rp500.000

Rp2.500

pcs

Rp12.500

Rp250

pcs

Rp2.500

Rp250

pcs

Rp2.500

Rp259.000

pcs

Rp259.000

Rp100

Rp100

Rp100

Rp100

Rp1.500

Rp1.000

Rp200

pcs

pcs

pcs

pcs

pcs

pcs

pcs

Rp180.000

bulan

Rp500

Rp500

Rp500

Rp500

Rp6.000

Rp4.000

Rp1.000
Rp720.000

Rp427.635

paket

Rp427.635

Rp174.985

box

Rp174.985

Rp4.799.745

Jumlah
Pembelian

Harga
Satuan
(Rp.)

Satuan
(Lembar,
Buah, dll)

4

4

2

2

Rp30.000

Rp45.000

Rp30.000

Rp45.000

pcs

pcs

pcs

pcs

Jumlah

120.000

180.000

60.000

90.000

34

5

29 Juli 2026

Domain Registration -
antaraga.web.id

6

29 Agustus
2026

Biaya Pembuatan Akun untuk
Register Aplikasi @25dollar

1

1

Rp13.078

paket

13.078

Rp452.166

paket

452.166

SubTotal (Rp)

915.244

TRANSPORTASI LOKAL (MAKS 30%)

No.

Tanggal
Pengeluaran

Uraian

1  12 Juni 2026

2  12 Juni 2026

3  12 Juni 2026

4  12 Juni 2026

5  12 Juni 2026

6  12 Juni 2026

7  13 Juni 2026

8  13 Juni 2026

9  13 Juni 2026

10  13 Juni 2026

11  13 Juni 2026

Biaya Ongkos Kirim - PPG Heart
Rate Monitor Sensor for Arduino
Analog/Digital Gravity

Biaya Asuransi Pengiriman - PPG
Heart Rate Monitor Sensor for
Arduino Analog/Digital Gravity

Biaya Jasa Aplikasi - PPG Heart
Rate Monitor Sensor for Arduino
Analog/Digital Gravity

Biaya Layanan - PPG Heart Rate
Monitor Sensor for Arduino
Analog/Digital Gravity

Biaya Ongkos Kirim - 20mm 22mm
Silicone Strap for Huawei GT 2 3 4
Samsung Galaxy Watch 7 6 5 4
Amazfit Garmin Sport Breathable
Strap

Biaya Layanan - 20mm 22mm
Silicone Strap for Huawei GT 2 3 4
Samsung Galaxy Watch 7 6 5 4
Amazfit Garmin Sport Breathable
Strap

Biaya Layanan pada pembelian
Seeed Studio XIAO ESP32-C3
Development Board Mini WiFi
Bluetooth BLE RISC-V Type-C
Module, dan KABEL EXTRA SOFT
SILICON AWG HIGH
TEMPERATURE KABEL AWG
LENTUR 14AWG - 30 AWG AWG
14 16 18 20 22 24 2 hitam dan
merah

Biaya ongkir (ongkos kirim) pada
pembelian DFRobot Fermion :
MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (pembelian 1)

Biaya Asuransi Pembelian -
MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (Pembelian 1)

Biaya Layanan - MAX30102 Heart
Rate and Oximeter Sensor
(Breakout) - SEN0518 (Pembelian 1)

Biaya ongkir (ongkos kirim) pada
pembelian DFRobot Fermion :
MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -

Jumlah
Pembelian

Harga
Satuan
(Rp.)

Satuan
(Lembar,
Buah, dll)

Jumlah

1

1

1

1

Rp21.000

transaksi

Rp21.000

Rp2.300

transaksi

Rp2.300

Rp1.000

transaksi

Rp1.000

Rp1.000

transaksi

Rp1.000

1

Rp6.500

transaksi

Rp6.500

1

Rp2.000

transaksi

Rp2.000

1

Rp2.786

transaksi

Rp2.786

1

Rp29.500

transaksi

Rp29.500

1

1

1

Rp3.700

transaksi

Rp3.700

Rp1.000

transaksi

Rp1.000

Rp29.500

transaksi

Rp29.500

SEN0518 (pembelian 2)

Biaya Asuransi pembelian -
MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (Pembelian 2)

Biaya Layanan dalam pembelian
MAX30102 Heart Rate and
Oximeter Sensor (Breakout) -
SEN0518 (pembelian 2)

Biaya Ongkos Kirim - Battery Li-
Polimer 3.7V 900 mAH 063443

Asuransi Pengiriman pada
pembelian Battery Li-Polymer 3.7V
950mAH

Biaya Layanan - Battery Li-Polimer
3.7V 900 mAH 063443

Biaya ongkir (ongkos kirim)
pembelian JST SH 1mm 1.0mm
Head Connector Konektor Pin Leads
Housing Shell

Biaya layanan pada pembelian JST
SH 1mm 1.0mm Head Connector
Konektor Pin Leads Housing Shell

Biaya Ongkir (ongkos kirim) dalam
pembelian USB Type-C Female
Soket Power Charger Port
Waterproof Kabel 10cm Socket
PH2.0

Biaya layanan dalam pembelian
USB Type-C Female Soket Power
Charger Port Waterproof Kabel
10cm Socket PH2.0

Biaya Ongkos Kirim - MINI
SWITCH TOGLE SWITCH ON
OFF SAKLAR SENTER HI
QUALITY BAHAN TEMBAGAA
MURNI UJUNG KAKI OVAL
(BUKAN KOTAK)

Biaya Layanan dalam pembelian
MINI SWITCH TOGLE SWITCH
ON OFF SAKLAR SENTER HI
QUALITY BAHAN TEMBAGAA
MURNI UJUNG KAKI OVAL
(BUKAN KOTAK)

Biaya ongkir (ongkos kirim) dalam
pembelian TP5000 3.6V / 4.2V 1A
DC 4.5V-9V Lithium Battery
Charger Module

Biaya Layanan dalam pembelian
TP5000 3.6V / 4.2V 1A DC 4.5V-
9V Lithium Battery Charger Module

Biaya Layanan - RT9013-33GB
Fixed 3.3V 500mA Linear Volta ge
Regulators LDO SOT-23-5 WJ
Richtek Technology

Biaya Layanan - MAX30102 Pulse
Oximeter and Heart Rate Sensor
Detak Jantung Sensor

12  13 Juni 2026

13  13 Juni 2026

14  13 Juni 2026

15  13 Juni 2026

16  13 Juni 2026

17  28 Juni 2026

18  28 Juni 2026

19

2 Juli 2026

20

2 Juli 2026

21

2 Juli 2026

22

2 Juli 2026

23

2 Juli 2026

24

2 Juli 2026

25

2 Juli 2026

26  10 Juli 2026

35

1

Rp3.700

transaksi

Rp3.700

1

1

1

1

1

1

Rp1.000

transaksi

Rp1.000

Rp8.000

transaksi

Rp8.000

Rp600

transaksi

Rp600

Rp1.000

transaksi

Rp1.000

Rp8.000

transaksi

Rp8.000

Rp2.000

transaksi

Rp2.000

1

Rp8.000

transaksi

Rp8.000

1

Rp2.000

transaksi

Rp2.000

1

Rp8.000

transaksi

Rp8.000

1

Rp2.000

transaksi

Rp2.000

1

1

1

1

Rp8.000

transaksi

Rp8.000

Rp2.000

transaksi

Rp2.000

Rp2.000

transaksi

Rp2.000

Rp2.000

transaksi

Rp2.000

27  10 Juli 2026

28  10 Juli 2026

29  10 Juli 2026

30  13 Juli 2026

31  17 Juli 2026

32  17 Juli 2026

33  17 Juli 2026

34  18 Juli 2026

35  22 Juli 2026

36  23 Juli 2026

37  29 Juli 2026

38

6 Agustus
2026

39

6 Agustus
2026

40

10 Agustus
2026

41

10 Agustus
2026

Biaya Ongkos Kirim - eSUN PETG
Basic 3D Filament Cost Effective
High Strength 3D Printing Filament

Biaya Layanan - eSUN PETG Basic
3D Filament Cost Effective High
Strength 3D Printing Filament

Biaya layanan paket DIODES
DMP2130L-7 Mosfet P-Channel
SMD3A 20V LG EBK61913701
mark MP1 + SAMWHA Ferrite
Bead 1000 Ohm 1K SMD 08 05
CB2012GM102E Beads +
SAMSUNG Ferrite Bead 60 Ohm
SMD 1210 CI B32P600NE Beads

Biaya Observasi Lapangan dan
Pengujian Alat - Ethical Clearance di
FKM Rumah Sakit Airlangga

Biaya Ongkos Kirim - XIAO
ESP32S3 Original Board IoT
Development Kit - Dual Core Wifi
Bluetooth 5.0 BLE Microcontroller

Biaya Asuransi Pengiriman - XIAO
ESP32S3 Original Board IoT
Development Kit - Dual Core Wifi
Bluetooth 5.0 BLE Microcontroller

Biaya Layanan - XIAO ESP32S3
Original Board IoT Development Kit
- Dual Core Wifi Bluetooth 5.0 BLE
Microcontroller

Biaya Transportasi Pengiriman
Fillament ke Jasa 3D Print Auto
Forge menggunakan Gosend

Biaya Transportasi Pengiriman Hasil
3D Print dari Jasa 3D Print Auto
Forge menuju PENS menggunakan
Gosend

Biaya Transportasi Pengiriman Hasil
3D Print terbaru (yang telah direvisi
dimensi desainnya) dari Jasa 3D
Print Auto Forge menuju PENS
menggunakan Gosend

Biaya Layanan - MAX30102 Pulse
Oximeter and Heart Rate Sensor
Detak Jantung Sensor

Biaya Transportasi Pengujian
ANTARAGA 2 dari PENS menuju
lokasi relawan (relawan 2 & 3
berada di satu tempat)

Biaya Transportasi Pengujian
ANTARAGA 2 dari lokasi relawan
(relawan 2 & 3 berada di satu
tempat) menuju PENS

Biaya Transportasi Pengujian
ANTARAGA 3 dari PENS menuju
lokasi relawan 4

Biaya Transportasi Pengujian
ANTARAGA 3 dari lokasi relawan
4 menuju lokasi relawan 5

36

1

1

Rp31.000

transaksi

Rp31.000

Rp1.000

transaksi

Rp1.000

1

Rp1.500

transaksi

Rp1.500

1

Rp100.000

paket

Rp100.000

1

Rp21.500

transaksi

Rp21.500

1

Rp1.700

transaksi

Rp1.700

1

1

1

Rp1.000

transaksi

Rp1.000

Rp42.000

transaksi

Rp42.000

Rp41.500

transaksi

Rp41.500

1

Rp42.300

transaksi

Rp42.300

1

1

1

1

1

Rp2.000

transaksi

Rp2.000

Rp28.500

transaksi

Rp28.500

Rp31.000

transaksi

Rp31.000

Rp29.500

transaksi

Rp29.500

Rp34.500

transaksi

Rp34.500

42

10 Agustus
2026

43

10 Agustus
2026

Biaya Transportasi Pengujian
ANTARAGA 2 dari lokasi relawan
5 menuju PENS

Biaya Ongkos Kirim - Strip Alat Cek
3in1 Elvasense (Gula
Darah/Kolesterol/Asam Urat)
Bundling 3 Box + Lancet

44

10 Agustus
2026

45

46

14 Agustus
2026

14 Agustus
2026

47  2 September

48  2 September

49  2 September

50  2 September

Biaya Layanan Strip Alat Cek 3in1
Elvasense (Gula
Darah/Kolesterol/Asam Urat)
Bundling 3 Box + Lancet

Biaya Transportasi Pengujian
ANTARAGA 4 dari PENS menuju
lokasi relawan 6

Biaya Transportasi Pengujian
ANTARAGA 4 dari lokasi relawan
6 menuju PENS

Biaya Transportas Pengujian
ANTARAGA 5 dari PENS menuju
lokasi relawan 7

Biaya Transportas Pengujian
ANTARAGA 5 dari lokasi relawan
7 menuju PENS

Biaya Layanan - Strip Alat Cek 3in1
Elvasense (Gula
Darah/Kolesterol/Asam Urat) CHOL
10'S

Biaya Ongkir - Strip Alat Cek 3in1
Elvasense (Gula
Darah/Kolesterol/Asam Urat) CHOL
10'S

51  5 September  Cek Lab Lansia di Klinik Parahita

52  5 September

53  5 September

Biaya Transportasi Cek Lab Lansia
(lokasi relawan 11 to Klinik
Parahita)

Biaya Transportasi Cek Lab Lansia
(lokasi Klinik Parahita to lokasi
relawan 11)

SubTotal (Rp)

LAIN-LAIN (MAKS 15%)

No.

Tanggal
Pengeluaran

Uraian

37

Rp28.500

transaksi

Rp28.500

Rp35.000

transaksi

Rp35.000

Rp4.000

transaksi

Rp4.000

Rp37.000

transaksi

Rp37.000

Rp35.000

transaksi

Rp35.000

Rp23.000

transaksi

Rp23.000

Rp23.500

transaksi

Rp23.500

Rp1.000

transaksi

Rp1.000

Rp21.000

transaksi

Rp21.000

Rp353.000

transaksi  Rp353.000

Rp31.500

transaksi

Rp31.500

Rp32.000

transaksi

Rp32.000

Rp1.192.086

1

1

1

1

1

1

1

1

1

1

1

1

Jumlah
Pembelian

Harga
Satuan
(Rp.)

Satuan
(Lembar,
Buah, dll)

Jumlah

1

2

6 Juni 2026

Periklanan Konten 1

4 Juli 2026

Periklanan Konten 2

3

29 Juli 2026

4

5

4 Agustus
2026

29 Agustus
2026

Kerusakan Komponen - MAX30102
Pulse Oximeter and Heart Rate
Sensor Detak Jantung Sensor

Pencetakan Protokol Ethical
Clearance dan Informed Consent

Periklanan Konten 3

1

1

2

1

1

Rp166.500

paket

166.500

Rp165.482

paket

165.482

Rp27.200

pcs

54.400

Rp40.500

paket

40.500

Rp166.043

paket

166.043

SubTotal (Rp)

592.925

Total Keseluruhan (Rp)

Jumlah Pendanaan (Rp)

Saldo (Rp)

38

7.500.000

7.500.000

0

Lampiran 3. Tabel Penggunaan Dana In Kind dari PENS

Tabel berikut memuat rincian penggunaan dana tambahan (in kind) senilai
Rp2.000.000  yang  difasilitasi  oleh  Politeknik  Elektronika  Negeri  Surabaya
(PENS) untuk mendukung optimalisasi riset dan pengembangan.

SEWA DAN JASA (MAKS 15%)

No.

Uraian

1

Penggunaan Lab IT
C306*

SubTotal (Rp)

LAIN-LAIN (MAKS 15%)

No.

Uraian

Jumlah
Pembelian

Harga Satuan
(Rp.)

Satuan (Lembar, Buah,
dll)

Jumlah

4

Rp450.000

bulan

Rp1.800.000

1.800.000

Jumlah
Pembelian

Harga Satuan
(Rp.)

Satuan (Lembar, Buah,
dll)

Jumlah

1  Pengajuan Hak Cipta*

1

Rp200.000

unit

SubTotal (Rp)

Total Keseluruhan (Rp)

Rp200.000

Rp200.000

Rp2.000.000

Lampiran 4. Sampling Bukti Pengeluaran

Seluruh  rekam  jejak  pelaksanaan  kegiatan  yang  telah  dilakukan  secara

berkala dirangkum selengkapnya pada tabel catatan harian berikut.

Tanggal  Keterangan

Harga
Satuan

Jumlah

Total

Bukti

6 Juni
2026

Periklanan
Konten 1

Rp166.500

1

Rp166.500

39

13 Juni
2026

MAX30102
Heart Rate
and Oximeter
Sensor
(Breakout) -
SEN0518
(Pembelian
1)

28 Juni
2026

JST SH 1mm
1.0mm Head
Connector
Konektor Pin
Leads
Housing
Shell Variasi
4P, 3P, 2P

Rp575.000

1

Rp575.000

Rp2.000

30

Rp60.000

13 Juli
2026

Biaya
Pengajuan
Ethical
Clearance di
FKM Rumah
Sakit
Airlangga

Rp100.000

1

Rp100.000

40

29 Juli
2026

Biaya
Pembuatan
Akun untuk
Register
Aplikasi
@25dollar

Rp452.166

1

Rp452.166

29
Agustus
2026

Periklanan
Konten 3

Rp166.043

1

Rp166.043

Lampiran 5. Bukti Logbook Kegiatan

Rincian  rekapitulasi  bukti  transaksi  untuk  setiap  komponen  pengeluaran

selama pelaksanaan program dapat dilihat pada tabel di bawah ini.

Tanggal
Pelaksanaan

Kegiatan

Waktu
Pelaksanaan
(menit)

Dokumentasi

23 Mei 2026

Rapat perdana dan
briefing awal setelah
pengumuman lolos
pendanaan.

180

41

Weekly Meeting dengan
Dosen Pendamping

17 Juni 2026

300

12 Juli 2026

Pengujian
Performa
Hardware  Multi-Sensor,
Migrasi  Mikrokontroler
ke  XIAO  ESP32-S3,
Implemetasi  Parameter
XGBoost,
Finalisasi
Fitur  Aplikasi  Mobile,
dan  Pemetaan  Lokasi
Kunjungan

25 Juli 2026

Integrasi Komponen
Hardware ke Casing 3D
& Perbaikan Modul
Charging TP5000, Uji
Ketahanan (Robustness)
& Error Handling API
Prediksi AI, serta Revisi
Draf Laporan Kemajuan
Pasca-Monev Internal 2

6  Agustus
2026

Pengujian
Kedua
Smartband ANTARAGA
Terhadap
Relawan,
Pengujian  Alur  Data
dan
End-to-End,
Pengumpulan
Data
Sinyal

240

240

180

42

Lampiran 6 Sertifikat Hak Kekayaan Intelektual
Sebagai  bentuk  pelindungan  kekayaan  intelektual  atas  inovasi  yang  telah
dikembangkan,  berikut  dilampirkan  Surat  Pencatatan  Ciptaan  yang  diterbitkan
oleh Kementerian Hukum dengan Nomor Permohonan EC002026157207 tanggal
28 Agustus 2026 dan Nomor Pencatatan 001449089 sebagai bukti perolehan Hak
Cipta (HKI) untuk program komputer ANTARAGA.

43

Lampiran 7. Ethical Clearance

Berikut adalah sertifikat Ethical Clearance yang diterbitkan oleh KEPK FKM
Universitas  Airlangga  pada  23  Juli  2026  sebagai  bukti  kelayakan  etik  atas
prosedur  pengujian  prototipe  ANTARAGA  yang  melibatkan  partisipasi  relawan
manusia.

Gambar L

44

Lampiran 8. Informed Consent

Sebagai  bukti  pemenuhan  etika  pengujian,  berikut  dilampirkan  salah  satu
dokumen Informed Consent yang telah disetujui dan ditandatangani oleh relawan.
Dokumen  Informed  Consent  selengkapnya  dari  seluruh  subjek  uji  dapat  diakses
melalui tautan berikut: Informed Consent Seluruh Relawan

45

46

47

48


