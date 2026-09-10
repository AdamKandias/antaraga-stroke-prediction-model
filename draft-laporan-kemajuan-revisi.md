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
Gambar 4.5 Dashboard Pelatihan Model Estimasi Vital ............................................ 7
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

  (a)
Gambar 1.1 Smartband (a) dan Aplikasi (b) ANTARAGA

(b)

1.2 Tujuan dan Relevansi dengan Tema PKM 2026

 Smartband  ANTARAGA  bertujuan  membantu  mendeteksi  risiko  stroke
iskemik  lebih  dini  sehingga  mencegah  terjadinya  keterlambatan  penanganan
sesuai  dengan  prinsip  time  is  brain.  Tujuan  tersebut  relevan  dengan  tema  PKM

2

2026,  yaitu  “Kesehatan  dan  Gizi  Masyarakat”  karena  memanfaatkan  teknologi
kesehatan  untuk  meningkatkan  kewaspadaan  keluarga  terhadap  risiko  stroke  dan
mendukung pendampingan kesehatan lansia di lingkungan rumah.
1.3 Inovasi Karsa Cipta dan Kemutakhirannya

 Inovasi ANTARAGA sebagai sistem pemantauan faktor risiko stroke iskemik
berbasis  smartband  mengintegrasikan  beberapa  teknologi  mutakhir  sebagai
berikut:
1.  Akuisisi Sinyal PPG Multi-Wavelength

ANTARAGA menggunakan sensor SON1303 pada kanal hijau 525 nm serta
MAX30102  pada  kanal  merah  660  nm  dan  inframerah  880  nm  untuk
merekam  sinyal  Photoplethysmography
(PPG).  Penggunaan  beberapa
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
serta  parameter
fitur  yang  hilang
scale_pos_weight  untuk  membobot  ulang  kelas  minoritas.  Kebutuhan  utama
pada  dataset  ini  karena  kelas  stroke  hanya  sekitar  4,87%  dari  keseluruhan
data.  Pemilihan  ini  diverifikasi  melalui  perbandingan  langsung  terhadap
HistGradientBoosting  (varian  gradient  boosting  lain  yang  lebih  baru)  pada
tahap  evaluasi  model  (lihat  BAB  4.4.1),  bukan  sekadar  pilihan  default.
Ketidakseimbangan  kelas  pada  dataset  ditangani  melalui  scale_pos_weight,
sedangkan  ambang  keputusan  dievaluasi  menggunakan  prediksi  out-of-fold
dan  kurva  Precision-Recall  untuk  meningkatkan  sensitivitas  terhadap  kelas
berisiko (Luo dkk., 2025).

4.  Estimasi Parameter Fisiologis Menggunakan Model Estimasi Vital

Lima model estimasi tanda vital dikembangkan untuk memetakan fitur optik PPG
menjadi estimasi gula darah, kolesterol, asam urat, tekanan sistolik, dan tekanan
diastolik -- satu model terpisah per parameter. Algoritma tiap model dipilih otomatis
dari perbandingan beberapa keluarga model (MLP, SVR, KNN, Random Forest,
XGBoost, dan lainnya) berdasarkan R2 tertinggi lewat validasi silang Leave-One-
Subject-Out (LOSO); saat ini SVR dipakai untuk sistolik, diastolik, dan asam urat,
sedangkan XGBoost untuk gula darah dan kolesterol (lihat BAB 4.4.2). Model
terintegrasi dengan dashboard server sehingga dapat dilatih ulang ketika tersedia
data kalibrasi baru.

3

5.  Integrasi Peringatan Risiko dan Asesmen ABCD2 pada Aplikasi Mobile

Hasil pemantauan terintegrasi dengan aplikasi mobile keluarga. Ketika sistem
risiko,  aplikasi  memberikan  peringatan  dan
mendeteksi  peningkatan
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
2026. Sisa capaian dialokasikan untuk pelatihan lanjutan model AI (deteksi risiko
stroke berbasis XGBoost, dan estimasi tanda vital berbasis SVR/XGBoost) menggunakan
data kalibrasi tambahan dari sesi pengujian relawan.
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
Lampiran 6.
BAB 3. TAHAP PELAKSANAAN
3.1 Alat dan Bahan

 Pengembangan  smartband  ANTARAGA  didukung  oleh  sejumlah  komponen
utama perangkat keras, infrastruktur, dan alat ukur validasi. Mikrokontroler utama
menggunakan  XIAO  ESP32-S3  setelah  migrasi  dari  ESP32-C3,  yang  memiliki
dua  core  pemrosesan  dan  kapasitas  SRAM  lebih  besar  untuk  menjalankan
transmisi data ke cloud serta pembacaan sensor secara bersamaan. Akuisisi sinyal
PPG  memanfaatkan  sensor  SON1303  (hijau)  serta  MAX30102  (merah  dan
inframerah).  Sistem  catu  daya  dan  manajemen  energi  didukung  oleh  modul
pengisian  TP5000,  regulator  LDO  RT9013-33GB,  serta  baterai  Li-Po  950  mAh.
Selain  itu,  perangkat  fisik  menggunakan  PCB  fabrikasi  mandiri  serta  casing
berbahan  PETG  3D  printing.  Infrastruktur  perangkat  lunak  didukung  oleh
penggunaan  VPS  dan  kerangka  kerja  Flutter,  sementara  validasi  pengujian
relawan  menggunakan  alat  ukur  pembanding  terstandar  berupa  multitester,
tensimeter, dan glukometer digital.
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

3.  Pembuatan  Prototipe:  PCB  difabrikasi  mandiri,  casing  PETG  dicetak,
komponen  dirakit,  dan  mikrokontroler  diganti  dari  XIAO  ESP32-C3  ke
ESP32-S3 sebelum fabrikasi.

4.  Integrasi Sistem: Firmware, Wi-Fi, API, VPS, dashboard, dan aplikasi telah
terhubung.  Pengolahan  bandpass,  FFT,  dan  BPM  dipindahkan  ke  server,
sedangkan SQI dipertahankan di perangkat.

5.  Pengembangan Model AI: XGBoost telah dituning dan diterapkan dengan
dua ambang keputusan untuk deteksi risiko stroke; pipeline lima model estimasi
tanda vital (SVR/XGBoost per parameter, hasil perbandingan beberapa keluarga
model) telah terintegrasi dan dilatih menggunakan data kalibrasi yang tersedia.

6.  Pengujian  dan  Validasi:  Pengujian  subsistem,  enam  sesi  relawan,  analisis
mutu  sinyal,  koreksi  BPM,  dan  konsultasi  dokter  spesialis  saraf  telah
dilaksanakan.

7.  Pelaporan  dan  Publikasi:  Laporan  kemajuan,  bahan  presentasi,
dokumentasi,  dan  tiga  konten  utama  media  sosial  telah  disusun  dan
dipublikasikan.

5

8.  Pengajuan  HKI:  Hak Cipta Program Komputer ANTARAGA telah tercatat

dan terbit.

Dokumentasi pelaksanaan seluruh tahapan kegiatan tertera pada Lampiran 1.
BAB 4. HASIL YANG DICAPAI
4.1 Dampak Pengiklanan Media Sosial

Hingga  saat  penulisan  laporan  ini,  aktivitas  publikasi  dan  edukasi  melalui
akun @pkmkc.antaraga telah menghasilkan 29 unggahan dengan 800 pengikut di
platform  Instagram,  serta  5  unggahan  dengan  18  pengikut  di  TikTok.  Untuk
memaksimalkan jangkauan informasi, tiga konten utama program telah diiklankan
secara bertahap pada platform Instagram. Rekapitulasi metrik capaian pengiklanan
tersebut disajikan pada Tabel 4.1.

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

Peningkatan tren metrik tiga iklan ini mengonfirmasi bahwa penyajian konten

yang lebih informatif efektif mendongkrak visibilitas serta keterlibatan audiens.
4.2 Spesifikasi Prototipe ANTARAGA

Realisasi  pembuatan  smartband  ANTARAGA  telah  mencapai  100%  dengan
spesifikasi hardware smartband ANTARAGA langsung disajikan pada Tabel 4.1.

Gambar 4.2 Desain Prototipe ANTARAGA: (a) tampak atas, (b) tampak dalam,
(c) tampak bawah, (d) susunan komponen

Tabel 4.2 Spesifikasi Hardware Smartband ANTARAGA

No

Komponen
/Modul

Spesifikasi Teknis
Hasil Realisasi

1  Mikrokontroler

XIAO
ESP32-S3,
dual-core Xtensa LX7
32-bit

2

Sensor
Hijau

PPG

SON1303/SEN0203
(Kanal Hijau 525 nm)

Fungsi & Hasil Pengujian

Pusat
sinyal,
pencuplikan
transmisi  Wi-Fi,  dan  firmware
penyaring SQI.
Merekam  dinamika  denyut  nadi,
dilengkapi  ferrite  bead  penekan
noise 50 Hz.

6

3

4

5

6

Sensor
Merah/NIR

PPG

MAX30102
(Merah
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

PCB

PCB
Mandiri

Fabrikasi

Enclosure

PETG 3D Printing

Pasokan  tegangan  bebas  ripple
switching dengan durasi pasokan
baterai terukur.
Pondasi  dari  seluruh  komponen
elektronik
Casing pelindung komponen dari
keringat serta benturan.

Realisasi  perangkat  keras  dan  firmware  telah  terintegrasi  penuh.  Sistem
catu daya LDO 3,3V terbukti mampu menstabilkan sinyal optik, dengan kapasitas
efektif  baterai  terukur  sebesar  813  mAh  (durasi  operasional  ~97  menit)  pada
pengujian  beban  konstan  500  mA.  Untuk  efisiensi  kapasitas  SRAM  dan  daya,
beban  komputasi  pemrosesan  sinyal  telah  dialihkan  ke  server  VPS,  sehingga
mikrokontroler  dapat  difokuskan  murni  pada  akuisisi  data.  Saat  ini,  perangkat
sudah
antarmuka  FastAPI
(www.antaraga.web.id)  untuk  menampilkan  tren  fisiologis  dan  mengirimkan
notifikasi peringatan kepada keluarga.

aplikasi  mobile  melalui

terhubung

ke

Dokumentasi  pengujian  keseluruhan  sistem  dapat  ditinjau  melalui  tautan

berikut: Video Luaran ANTARAGA.
4.3 Spesifikasi Aplikasi Mobile ANTARAGA

lansia,  konektivitas  perangkat  via  Device

plikasi  mobile  ANTARAGA  dikembangkan  menggunakan  Flutter  yang
terintegrasi  dengan  backend  melalui  API.  Fitur  utamanya  meliputi  autentikasi,
pengelolaan  multi-profil
ID,
pemantauan tanda vital, statistik harian, prediksi risiko AI, serta asesmen ABCD2.
Dashboard  aplikasi  menyajikan  status  koneksi,  parameter  fisiologis  (tekanan
darah,  detak  jantung,  gula  darah),  tingkat  risiko  stroke,  serta  grafik  timeline
perubahan  kondisi.  Selain  itu,  asesmen  ABCD2  terintegrasi  untuk  memberikan
penilaian awal dan estimasi risiko jangka pendek (2, 7, dan 90 hari) berdasarkan
kohort validasi klinis yang tervalidasi (Spampinato dkk., 2022).

Gambar 4.3 Flowchart Pengiriman Data Alat ke Aplikasi

4.4 Hasil Pelatihan dan Pengujian
4.4.1 Hasil Pelatihan Model XGBoost

Dataset  model  risiko  memiliki  class  imbalance  dengan  kelas  stroke  sekitar
4,87%.  Karena  akurasi  dapat  menyesatkan  pada  kondisi  tersebut,  evaluasi
menggunakan  Average  Precision  dan  recall.  XGBoost  dengan  scale_pos_weight

7

19,55 dibandingkan dengan HistGradientBoosting melalui RandomizedSearchCV
dan StratifiedKFold lima lipatan. Empat puluh kombinasi parameter melalui lima
validasi silang menghasilkan 200 proses pelatihan.

Threshold  awal  0,705  dipilih  berdasarkan  F1-score  terbaik  sebesar  0,2946.
Optimasi  berikutnya  memprioritaskan  sensitivitas  sistem  peringatan  dan
menghasilkan threshold 0,042 dengan recall 0,973,  yaitu 73 dari 75 kasus stroke
pada data uji berhasil terdeteksi.
4.4.2 Hasil Pelatihan Model Estimasi Vital (kombinasi SVR dan XGBoost)

Model kombinasi SVR dan XGBoost telah dibangun dan terintegrasi dengan
dashboard  sehingga  pelatihan  ulang  dapat  dilakukan  ketika  tersedia  data  baru.
Kapasitas  model  diskalakan  otomatis  mengikuti  jumlah  data  kalibrasi  yang
tersedia (1 lapisan 4 neuron untuk data di bawah 10 subjek, 2 lapisan untuk data
lebih  besar)  supaya  model  tidak  menghafal  data  yang  masih  sedikit.  Evaluasi
kuantitatif  menggunakan  MAE,  RMSE,  MAPE,  dan  R²  dengan  skema  validasi
Leave-One-Subject-Out (setiap subjek diuji oleh model yang tidak pernah melihat
data subjek tersebut saat dilatih).

Hasil  pelatihan  pada  11  subjek  kalibrasi  yang  tersedia  hingga  5  September
2026  disajikan  pada  Tabel  4.4.  Nilai  R²  digunakan  sebagai  indikator  utama
kejujuran model (R² mendekati atau di atas nol berarti model benar-benar belajar
pola, R² negatif berarti model belum lebih baik daripada menebak nilai rata-rata).
Tabel 4.4 Evaluasi Model SVR dan XGBoost estimasi data vital per Parameter
(LOO, n=11 subjek)

Parameter  N

R²

Akurasi (%)

Catatan

Gula Darah  11

-0.065

75.50%

Perlu Data Lebih

Kolesterol

11

-0.071

89.33%

Asam Urat

11

-0.001

85.21%

Sistolik

11

-0.081

90.61%

Diastolik

11

0.134

88.80%

Baik

Baik

Baik

Baik

4.4.3 Hasil Pengujian Prototipe pada Relawan

Pengujian  relawan  dimulai  pada  3  Agustus  2026  untuk  memvalidasi  SOP,
konektivitas, kenyamanan, kualitas sinyal, dan alur penyimpanan data. Enam sesi
sampai 5 September 2026 telah menghasilkan data dari sebelas relawan.

8

Tabel 4.5 Rentang Data Hasil Pengujian Relawan

Alat Medis

Prediksi

Akurasi (%)

TD  GL  CH  UA  TD  GL  CH  UA  TD  GL  CH  UA

157/
88

R  N

Y  2

N  9

Keterangan:
R = Riwayat Stroke (Y=Yes, N=No)
N = Jumlah Relawan
TD = Tekanan Darah (mmHg)
Sistem  kecerdasan  buatan  dikembangkan  menggunakan  model  XGBoost
untuk  prediksi  risiko  stroke,  serta  model  SVR  (Support  Vector  Regression)  dan
XGBoost  untuk  kalibrasi  sinyal  PPG  (training  model).  Metrik  evaluasi  disajikan
pada Tabel 4.6.

GL = Gula Darah (mg/dL)
CH = Kolestrol Total (mg/dL)
UA = Asam Urat (mg/dL)

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

< 2 Detik (Cloud ke
aplikasi mobile)

Sangat Cepat

Pengujian  fungsional  pada  11  relawan  (selengkapnya  pada  Lampiran  1)
menunjukkan pembacaan sinyal optik PPG yang stabil pada indeks perfusi normal
(0,74-1,77‰) dan tangguh terhadap gerakan ringan. Dalam pengembangan model
AI,  nilai  threshold  standar  (0,50)  disesuaikan  menjadi  0,042  (deteksi  biner)  dan
0,705  (risiko  tinggi)  melalui  evaluasi  Out-of-Fold  (OOF)  serta  kurva  Precision-
Recall  guna  mengatasi  ketidakseimbangan  data.  Kombinasi  penurunan  threshold
dan  penyeimbangan  bobot  (scale_pos_weight  =  19,55)  sukses  mendongkrak
sensitivitas (Recall) hingga 97,3%, selaras dengan standar klinis AHA/ASA (skor
ABCD²)  yang  memprioritaskan  minimalisasi  false  negative  agar  tidak  ada
penderita  stroke  yang  terlewat.  Untuk  pemrosesan  sinyal,  sistem  backend

9

menggunakan penyaring lonjakan BPM 4 lapis guna menekan artefak gerak, serta
memanfaatkan 5 model estimasi tanda vital (SVR/XGBoost per parameter, dipilih
lewat perbandingan beberapa keluarga model berbasis R2 tervalidasi LOSO) untuk
menyusun estimasi indikator kesehatan harian.  Sebagai  penguatan  akhir,  seluruh  alur  kuesioner
kualitatif,  instrumen  ABCD2,  dan  skenario  rujukan  prarumah  sakit  telah  melalui
tahapan  validasi  klinis  secara  langsung  bersama  Dokter  Spesialis  Saraf  pada  7
Agustus 2026.
BAB 5. POTENSI HASIL
5.1 Potensi Prototipe ANTARAGA Berdampak

ANTARAGA memiliki potensi menjadi sistem pendukung pemantauan faktor
risiko  stroke  pada  lansia  di  lingkungan  keluarga  melalui  integrasi  wearable,
analisis  data,  dan  aplikasi  mobile.  Informasi  yang  dihasilkan  dapat  membantu
keluarga  memantau  kondisi  secara  lebih  terstruktur  dan  mendorong  evaluasi
medis  ketika  ditemukan  kondisi  yang  membutuhkan  perhatian.  Sistem  tetap
diposisikan sebagai pendukung keputusan, bukan alat diagnosis.
5.2 Potensi Hak Kekayaan Intelektual

Tim  ANTARAGA  telah  memperoleh  Hak  Cipta  Program  Komputer  dari
Kementerian  Hukum  dengan  nomor  pencatatan  001449089,  sebagai  bentuk
perlindungan  hukum  atas  inovasi  sistem  deteksi  dini  risiko  stroke  berbasis
smartband dan aplikasi mobile. Sertifikat Hak Cipta tercantum pada Lampiran 5.
5.3 Potensi Pengembangan Prototipe ANTARAGA

Pengembangan  prototipe  ANTARAGA  dipetakan  secara  bertahap.
Berbekal  izin  kelayakan  etik  (ethical  clearance)  dan  validasi  Dokter  Spesialis
Saraf, fokus tahun pertama diarahkan pada optimasi performa AI, stabilitas sistem
real-time, efisiensi daya, pengujian keandalan sensor secara dinamis pada lansia,
serta  submission  artikel  ilmiah  ke  Journal  of  Applied  Electrical  Engineering
(JAEE) untuk kelengkapan Laporan Akhir. Pada periode satu hingga tiga tahun ke
depan,  pengembangan  difokuskan  pada  peningkatan  kenyamanan  perangkat,
enkripsi  data,  dan  evaluasi  lanjutan  bersama  tenaga  kesehatan,  sebelum  dikaji
tingkat  kesiapan  teknologinya  agar  siap  dihilirisasi  menjadi  produk  teknologi
tepat guna.

BAB 6. RENCANA TAHAPAN BERIKUTNYA
Sebagai  upaya  menuntaskan
target  pelaksanaan  hingga  mencapai  100%,
serangkaian  kegiatan  lanjutan  telah  dijadwalkan  untuk  sisa  masa  pelaksanaan
program, dengan rincian pada tabel 6.1.

Tabel 6.1 Rencana Anggaran Berikutnya

No

Kegiatan

PIC

Dana  Pelaksanaan

1

Penyusunan Bahan PPT &
Simulasi PKP PKM

Kadek, Zeven

Rp0

Bulan ke-4

10

No

Kegiatan

PIC

Dana  Pelaksanaan

2

Pengujian 7 &
Penyempurnaan Model AI

Kadek, Adam, Ally

Rp0

Bulan ke-4

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
102984.
Signal
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
future
2923.
https://doi.org/10.3390/electronics12132923.

Electronics,

directions”,

12(13),

Luo,  J.,  Yuan,  Y.  dan  Xu,  S.  (2025)  “Improving  GBDT  performance  on
imbalanced  datasets:  An  empirical  study  of  class-balanced  loss  functions”,
129896.
634,
Neurocomputing,
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
meta-analysis”,
1508-1519.
https://doi.org/10.1001/jama.2025.2033.

333(17),

JAMA,

11

LAMPIRAN
Lampiran 1. Dokumentasi Pengembangan dan Pengujian ANTARAGA
L.1.1 Realisasi Prototipe dan Ekosistem ANTARAGA

No

Tabel L.1 Realisasi Prototipe dan Ekosistem ANTARAGA
Keterangan
Prototipe final tampak
depan, samping,
belakang

Dokumentasi

Gambar L.1 foto prototipe tampak depan

Gambar L.2 foto prototipe tampak samping

12

Gambar L.3 foto prototipe tampak belakang

Smartband ketika
digunakan

PCB final

Gambar L.4 foto prototipe ketika dipakai

Gambar L.5 foto PCB terintegrasi komponen
elektronik

Casing PETG

13

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

14

Aspek Proposal

Realisasi

Alasan/Implikasi

Baterai 900 mAh

Li-Po 1S 950 mAh
pada prototipe uji

Penyesuaian kapasitas sumber
daya

Pemrosesan sinyal
pada perangkat

Pemrosesan utama
pada server

Model Gradient
Boosting

XGBoost untuk
prediksi risiko

Model MLP (Multi
Layer Perceptron)
untuk estimasi data
vital (tekanan darah,
gula darah, kolesterol,
dan asam urat) --
kondisi awal

Menggunakan
kombinasi model
Support Vector
Regression (SVR) dan
XGBoost per parameter
untuk estimasi data
vital (tekanan darah,
gula darah, kolesterol,
dan asam urat) --
kondisi saat ini

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
jumlahnya terbatas.

Setelah dilatih dan dievaluasi
dengan validasi silang Leave-
One-Subject-Out (LOSO), model
MLP tunggal terbukti kurang
cocok untuk menangani jumlah
data subjek yang masih
terbatas (rata-rata akurasi
58,9% pada perbandingan 13
keluarga model, jauh di bawah
model lain -- lihat
model/test_loso.ipynb), sehingga
dibutuhkan model lain yang
lebih tahan terhadap data kecil
seperti SVR dan XGBoost.

<!-- GAMBAR: grafik perbandingan
akurasi 13 model dari
model/test_loso.ipynb bagian 1
(peringkat model) -->

Dari hasil perbandingan
tersebut, didapatkan bahwa
model terbaik adalah SVR
untuk estimasi asam urat,
tekanan darah sistolik, dan
tekanan darah diastolik,
sedangkan XGBoost lebih baik
dalam mengestimasi gula darah
dan kolesterol -- algoritma ini
yang kemudian diterapkan
sebagai model produksi per
parameter (lihat Tabel L.4b).

15

1.3 Pengujian Teknis Prototipe
No

Pengujian
Manajemen
sistem daya

Dokumentasi

Gambar L.9 Analisis output ketika menggunakan buck
converter

Gambar L.10 Analisis noise ketika menggunakan boost
converter

Gambar L.11 Datasheet Regulator LDO RT9013-33GB

16

Pengujian
SON1303

Gambar L.12 Interfensi noise 50Hz pada sinyal output
sensor SON1303

Gambar L.13 Sinyal output sensor SON1303 setelah
optimalisasi

Pengujian
MAX30102

Gambar L.14 Sensor MAX30102 rusak karena cacat pabrik

17

Gambar L.15 Malfungsi LED channel IR pada Sensor
MAX30102

Gambar L.16 Sensor baru MAX30102 dan berhasil
berfungsi

Gambar L.17 Sinyal output sensor MAX30102 pada channel
RED dan IR setelah optimalisasi

18

Gambar L.17 Perbandingan hasil pembacaan sensor
MAX30102 dengan alat oximeter terstandar (oximeter
mendeteksi 80bpm, sedangkan di sensor log pada monitor
terdeteksi 79bpm, yang artinya error hanya terpaut 1 bpm)

Gambar L.17 Uji discharge baterai lipo 1s dengan beban
500mA

Charge-
discharge
baterai

Desain
Layout PCB

Gambar L.18 Dokumentasi desain layout PCB

Inspeksi PCB

19

Gambar L.19 Sinyal output sensor SON1303 setelah
optimalisasi

Pengujian
casing

Gambar L.20 casing tidak bisa menutup rapat

Gambar L.21 hasil casing setelah penyesuaian

20

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
alat medis vs prediksi model estimasi vital, dan hasil deteksi risiko stroke.

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
Jantung

Status Bekerja

Tipe Tempat
Tinggal
Riwayat
Diabetes
Riwayat
Stroke

S001
20
Laki-laki
Sewaktu
(tidak puasa)

S002
57
Perempuan
Sewaktu
(tidak puasa)

S003
75
Perempuan
Sewaktu
(tidak puasa)

S004
70
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

Ya
(Mahasiswa)

Tidak (Sudah
Pensiun)

Tidak (Sudah
Pensiun)

Tidak (Sudah
Pensiun)

Kota

Kota

Kota

Kota

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

21

Keluarga
Riwayat
Stroke Pribadi
Tanggal
Pengujian

Field
Usia
Gender
Kondisi
Pengambilan
Merokok
Riwayat
Penyakit
Jantung

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

S006
75
Perempuan
Sewaktu
(tidak puasa)
Tidak

Tidak

S007
75
Laki-laki
Sewaktu
(tidak puasa)
Ya
Tidak

S008
62
Laki-laki
Sewaktu
(tidak puasa)
Tidak
Tidak

Status Bekerja

Mahasiswa
(Ya)

Sudah
Pensiun
(Tidak)

Sudah
Pensiun
(Tidak)

Sudah
Pensiun
(Tidak)

Tipe Tempat
Tinggal
Riwayat
Diabetes
Riwayat
Stroke
Keluarga

Riwayat
Stroke Pribadi

Kota

Kota

Kota

Kota

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Tidak

Ya

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

S009

S010

S011

Field

Usia
Gender
Kondisi
Pengambilan
Merokok

62
Perempuan
Sewaktu (tidak
puasa)
Tidak

Riwayat Penyakit
Jantung

Tidak

63
Laki-laki
Sewaktu (tidak
puasa)
Tidak

Tidak

80
Perempuan
Sewaktu (tidak
puasa)
Ya
Tidak

22

Status Bekerja

Mahasiswa (Ya)

Sudah Pensiun
(Tidak)

Sudah Pensiun
(Tidak)

Tipe Tempat
Tinggal
Riwayat Diabetes
Riwayat Stroke
Keluarga

Riwayat Stroke
Pribadi

Tanggal
Pengujian

Kota

Tidak

Tidak

Kota

Tidak

Tidak

Tidak

Tidak

Kota

Tidak

Ya

Ys

2 September 2026  5 September 2026  5 September 2026

Tabel L.4b Data Alat Medis vs Prediksi Model Estimasi Vital per Relawan (ada di PDF report per
subjek)

Prediksi dihasilkan model produksi saat ini per parameter -- SVR untuk Sistolik, Diastolik,
dan Asam Urat, XGBoost untuk Gula Darah dan Kolesterol (lihat BAB 4.4.2 dan model/test_loso.ipynb
untuk metodologi pemilihannya) -- dievaluasi dengan skema Leave-One-Subject-Out (LOSO): setiap
prediksi berasal dari model yang TIDAK pernah melihat data subjek tersebut selama pelatihan,
bukan prediksi dari model yang sudah menghafal datanya sendiri.

| Subjek | Parameter | Alat Terstandar (Aktual) | Prediksi Model | Akurasi (%) |
|---|---|---|---|---|
| S001 | Tensimeter (Tekanan Darah Sistolik) | 125,0 mmHg | 145,5 mmHg | 83,6% |
| S001 | Tensimeter (Tekanan Darah Diastolik) | 77,0 mmHg | 90,7 mmHg | 82,2% |
| S001 | Elvasense 3in1 EMS10 (Gula Darah) | 119,0 mg/dL | 133,3 mg/dL | 88,0% |
| S001 | Elvasense 3in1 EMS10 (Kolesterol Total) | 212,0 mg/dL | 226,1 mg/dL | 93,4% |
| S001 | Elvasense 3in1 EMS10 (Asam Urat) | 6,3 mg/dL | 5,4 mg/dL | 86,2% |
| S002 | Tensimeter (Tekanan Darah Sistolik) | 173,0 mmHg | 152,0 mmHg | 87,8% |
| S002 | Tensimeter (Tekanan Darah Diastolik) | 102,0 mmHg | 92,8 mmHg | 91,0% |
| S002 | Elvasense 3in1 EMS10 (Gula Darah) | 101,0 mg/dL | 139,6 mg/dL | 61,8% |
| S002 | Elvasense 3in1 EMS10 (Kolesterol Total) | 200,0 mg/dL | 229,3 mg/dL | 85,3% |
| S002 | Elvasense 3in1 EMS10 (Asam Urat) | 4,6 mg/dL | 5,1 mg/dL | 88,9% |
| S003 | Tensimeter (Tekanan Darah Sistolik) | 153,0 mmHg | 157,2 mmHg | 97,3% |
| S003 | Tensimeter (Tekanan Darah Diastolik) | 94,0 mmHg | 93,1 mmHg | 99,1% |
| S003 | Elvasense 3in1 EMS10 (Gula Darah) | 183,0 mg/dL | 139,5 mg/dL | 76,2% |
| S003 | Elvasense 3in1 EMS10 (Kolesterol Total) | 232,0 mg/dL | 250,9 mg/dL | 91,9% |
| S003 | Elvasense 3in1 EMS10 (Asam Urat) | 4,5 mg/dL | 5,4 mg/dL | 80,4% |
| S004 | Tensimeter (Tekanan Darah Sistolik) | 157,0 mmHg | 150,8 mmHg | 96,1% |
| S004 | Tensimeter (Tekanan Darah Diastolik) | 88,0 mmHg | 91,5 mmHg | 96,1% |
| S004 | Elvasense 3in1 EMS10 (Gula Darah) | 153,0 mg/dL | 157,9 mg/dL | 96,8% |
| S004 | Elvasense 3in1 EMS10 (Kolesterol Total) | 269,0 mg/dL | 227,6 mg/dL | 84,6% |
| S004 | Elvasense 3in1 EMS10 (Asam Urat) | 4,8 mg/dL | 4,9 mg/dL | 97,3% |
| S005 | Tensimeter (Tekanan Darah Sistolik) | 166,0 mmHg | 132,8 mmHg | 80,0% |
| S005 | Tensimeter (Tekanan Darah Diastolik) | 86,0 mmHg | 88,1 mmHg | 97,5% |
| S005 | Elvasense 3in1 EMS10 (Gula Darah) | 98,0 mg/dL | 151,2 mg/dL | 45,7% |
| S005 | Elvasense 3in1 EMS10 (Kolesterol Total) | 244,0 mg/dL | 248,1 mg/dL | 98,3% |
| S005 | Elvasense 3in1 EMS10 (Asam Urat) | 5,3 mg/dL | 5,3 mg/dL | 99,1% |
| S006 | Tensimeter (Tekanan Darah Sistolik) | 145,0 mmHg | 152,0 mmHg | 95,2% |
| S006 | Tensimeter (Tekanan Darah Diastolik) | 78,0 mmHg | 91,6 mmHg | 82,5% |
| S006 | Elvasense 3in1 EMS10 (Gula Darah) | 94,0 mg/dL | 161,4 mg/dL | 28,2% |
| S006 | Elvasense 3in1 EMS10 (Kolesterol Total) | 269,0 mg/dL | 243,5 mg/dL | 90,5% |
| S006 | Elvasense 3in1 EMS10 (Asam Urat) | 6,3 mg/dL | 5,2 mg/dL | 83,3% |
| S007 | Tensimeter (Tekanan Darah Sistolik) | 142,0 mmHg | 139,8 mmHg | 98,5% |
| S007 | Tensimeter (Tekanan Darah Diastolik) | 56,0 mmHg | 85,4 mmHg | 47,5% |
| S007 | Elvasense 3in1 EMS10 (Gula Darah) | 183,0 mg/dL | 137,0 mg/dL | 74,9% |
| S007 | Elvasense 3in1 EMS10 (Kolesterol Total) | 268,0 mg/dL | 243,7 mg/dL | 90,9% |
| S007 | Elvasense 3in1 EMS10 (Asam Urat) | 7,2 mg/dL | 5,5 mg/dL | 76,7% |
| S008 | Tensimeter (Tekanan Darah Sistolik) | 131,0 mmHg | 149,2 mmHg | 86,1% |
| S008 | Tensimeter (Tekanan Darah Diastolik) | 91,0 mmHg | 87,6 mmHg | 96,3% |
| S008 | Elvasense 3in1 EMS10 (Gula Darah) | 171,0 mg/dL | 153,1 mg/dL | 89,6% |
| S008 | Elvasense 3in1 EMS10 (Kolesterol Total) | 261,0 mg/dL | 215,9 mg/dL | 82,7% |
| S008 | Elvasense 3in1 EMS10 (Asam Urat) | 5,0 mg/dL | 5,3 mg/dL | 93,4% |
| S009 | Tensimeter (Tekanan Darah Sistolik) | 121,0 mmHg | 135,6 mmHg | 88,0% |
| S009 | Tensimeter (Tekanan Darah Diastolik) | 71,0 mmHg | 70,5 mmHg | 99,4% |
| S009 | Elvasense 3in1 EMS10 (Gula Darah) | 157,0 mg/dL | 157,1 mg/dL | 100,0% |
| S009 | Elvasense 3in1 EMS10 (Kolesterol Total) | 206,0 mg/dL | 232,5 mg/dL | 87,1% |
| S009 | Elvasense 3in1 EMS10 (Asam Urat) | 3,7 mg/dL | 5,6 mg/dL | 48,6% |
| S010 | Tensimeter (Tekanan Darah Sistolik) | 163,0 mmHg | 141,0 mmHg | 86,5% |
| S010 | Tensimeter (Tekanan Darah Diastolik) | 97,0 mmHg | 85,4 mmHg | 88,1% |
| S010 | Elvasense 3in1 EMS10 (Gula Darah) | 198,0 mg/dL | 149,4 mg/dL | 75,5% |
| S010 | Elvasense 3in1 EMS10 (Kolesterol Total) | 194,0 mg/dL | 235,6 mg/dL | 78,5% |
| S010 | Elvasense 3in1 EMS10 (Asam Urat) | 5,8 mg/dL | 5,3 mg/dL | 91,9% |
| S011 | Tensimeter (Tekanan Darah Sistolik) | 151,0 mmHg | 147,5 mmHg | 97,7% |
| S011 | Tensimeter (Tekanan Darah Diastolik) | 89,0 mmHg | 86,5 mmHg | 97,2% |
| S011 | Elvasense 3in1 EMS10 (Gula Darah) | 121,0 mg/dL | 137,3 mg/dL | 86,5% |
| S011 | Elvasense 3in1 EMS10 (Kolesterol Total) | 245,0 mg/dL | 243,1 mg/dL | 99,2% |
| S011 | Elvasense 3in1 EMS10 (Asam Urat) | 5,3 mg/dL | 4,8 mg/dL | 91,3% |

Rata-rata akurasi per parameter (evaluasi LOSO, 11 subjek):

| Parameter | Model | Rata-rata Akurasi (%) | R² (LOSO) |
|---|---|---|---|
| Gula Darah | XGBoost (reg. ketat) | 74,83% | -0.1025 |
| Kolesterol | XGBoost (reg. ketat) | 89,33% | -0.0392 |
| Asam Urat | SVR (rbf) | 85,20% | -0.0009 |
| Sistolik | SVR (linear) | 90,61% | -0.0809 |
| Diastolik | SVR (linear) | 88,80% | 0.1343 |

**Catatan kejujuran:** angka akurasi per sesi di atas dihitung apa adanya dari selisih
prediksi terhadap nilai alat invasif sungguhan, tanpa penyesuaian atau pembulatan ke atas
dalam bentuk apa pun. R² pada tabel ringkasan sebagian besar masih negatif kecuali Diastolik
(+0,13) -- artinya model belum terbukti secara statistik mengungguli sekadar menebak nilai
rata-rata untuk 4 dari 5 parameter pada 11 subjek yang tersedia saat ini, meskipun persentase
akurasi per sesi terlihat cukup tinggi. Keterbatasan ini dilaporkan apa adanya, konsisten
dengan evaluasi menyeluruh di model/test_loso.ipynb, dan menjadi dasar rencana penambahan
data kalibrasi pada BAB 6.

Link Detail PDF Data Relawan Subjek S001: [Data Relawan S001]

Link Detail PDF Data Relawan Subjek S002: [Data Relawan S002]

Link Detail PDF Data Relawan Subjek S003: [Data Relawan S003]

Link Detail PDF Data Relawan Subjek S004: [Data Relawan S004]

Link Detail PDF Data Relawan Subjek S005: [Data Relawan S005]

Link Detail PDF Data Relawan Subjek S006: [Data Relawan S006]

Link Detail PDF Data Relawan Subjek S007: [Data Relawan S007]

Link Detail PDF Data Relawan Subjek S008: [Data Relawan S008]

Link Detail PDF Data Relawan Subjek S009: [Data Relawan S009]

Link Detail PDF Data Relawan Subjek S010: [Data Relawan S0010]

Link Detail PDF Data Relawan Subjek S011: [Data Relawan S011]


Tabel  L.4c  Hasil  Deteksi  Risiko  Stroke  per  Relawan  (ada  di  PDF  report  per
subjek)

Subjek
S001
S002

S003

S004

S005

S006

S007

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

Kategori Risiko
Rendah
Rendah

Sedang

Tinggi

Sedang

Sedang

Tinggi

28

S008

S009

S010

S011

Hipertensi dan Kolesterol Total Tinggi
Hipertensi, Kolesterol Total Tinggi, dan usia
80 tahun (≥ 75 tahun)
Hipertensi
Hipertensi, Kolesterol Total Tinggi, dan usia 80
tahun (≥ 75 tahun)

Rendah

Sedang

Rendah

Sedang

1.5 Evaluasi Model AI

Tabel L.5a Model Estimasi Vital dari Sensor Sinyal PPG Hardware (kombinasi
SVR dan XGBoost)
No  Keterangan

Dokumentasi

Merancang model estimasi
tanda vital untuk gula
darah, kolesterol, asam
urat, sistolik, diastolik
menggunakan fitur input
dari sensor yakni berupa
ir_dc_mean, ir_ac_p2p,
red_dc_mean,
red_ac_p2p, bpm, usia,
dan jenis kelamin. Model
awal berbasis MLP
(Multi-Layer Perceptron),
dibandingkan dengan
metode regresi linear;
MLP terbukti lebih baik
pada perbandingan awal
ini. Pelatihan awal model
dari data kalibrasi yang
terkumpul.

Setelah data kalibrasi
bertambah, MLP tunggal
dibandingkan menyeluruh
terhadap 13 keluarga
model lain (SVR, KNN,
Random Forest, XGBoost,
dan lainnya) dengan
validasi silang Leave-One-
Subject-Out (LOSO: MAE,
RMSE, R2). SVR terbukti
lebih baik untuk asam
urat, sistolik, dan
diastolik, sedangkan
XGBoost lebih baik untuk
gula darah dan kolesterol
-- kombinasi ini kemudian
diterapkan sebagai model
produksi, menggantikan
MLP tunggal sepenuhnya.
Evaluasi diperbarui tiap
penambahan data kalibrasi
baru.

<!-- GAMBAR: perbandingan MLP dengan model
berbasis regresi linear dan alasan kenapa
memilih menggunakan MLP (tahap awal) -->

<!-- GAMBAR: hasil pelatihan model MLP awal
dengan data 6 relawan subjek yang sudah ada -->

29

<!-- GAMBAR: grafik peringkat 13 model dan
grafik prediksi-vs-aktual SVR/XGBoost dari
model/test_loso.ipynb -->

Hasil akhir model estimasi
tanda vital saat ini (SVR
untuk asam urat/sistolik/
diastolik, XGBoost untuk
gula darah/kolesterol)
setelah pengujian 11
subjek relawan -- lihat
Tabel L.4b untuk rincian
prediksi per subjek

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

Media Sosial
Screenshoot smua konten

1.7 Validasi Medis dan Kepatuhan Etik
Ethical Clearance

informed consent kosong/teranonimisasi

dokumentasi konsultasi dokter spesialis saraf

ringkasan hasil konsultasi/validasi

bukti validasi alur ABCD2 jika tersedia

30

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
Confusion matrix, ROC/Precision-Recall, threshold XGBoost, perbandingan 13 model
(MLP vs SVR vs XGBoost dkk., lihat model/test_loso.ipynb), serta dokumentasi
pelatihan model estimasi vital.
1.6 Integrasi Aplikasi dan Server
Tampilan  aplikasi,  dashboard,  API,  alur  pengiriman  data,  notifikasi  risiko,  dan
asesmen ABCD2.

confusion  matrix,  ROC/Precision-Recall,

threshold,

recall,

31

Lampiran 2. Tabel Penggunaan Dana Belmawa

Rincian  penggunaan  dana  Belmawa  yang  telah  direalisasikan  sepenuhnya
untuk  operasional  program  disajikan  pada  tabel  berikut,  dengan  sisa  saldo  akhir
sebesar Rp0.

BAHAN HABIS PAKAI (MAKS 60%)

No  Tanggal

Uraian

Jumlah
Pembeli-
an

Harga
Satuan
(Rp)

Satuan

Jumlah

1

12 Juni
2026

2

12 Juni
2026

3

13 Juni
2026

4

13 Juni
2026

5

13 Juni
2026

PPG Heart Rate
Monitor Sensor
for Arduino
Analog/Digital
Gravity
20mm 22mm
Silicone Strap for
Huawei GT 2 3 4
Samsung Galaxy
Watch 7 6 5 4
Amazfit Garmin
Sport Breathable
Strap
Seed Studio
XIAO ESP32-C3
Development
Board Mini WiFi
Bluetooth BLE
RISC-V Type-C
Module
KABEL EXTRA
SOFT SILICON
AWG HIGH
TEMPERATURE
KABEL AWG
LENTUR
14AWG -
30AWG AWG 14
16 18 20 22 24 2
putih
KABEL EXTRA
SOFT SILICON
AWG HIGH
TEMPERATURE
KABEL AWG

2

Rp323.000

pcs

Rp646.000

2

Rp20.300

pcs

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

LENTUR
14AWG -
30AWG AWG 14
16 18 20 22 24 2
merah
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(Pembelian 1)
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(pembelian 2)
Battery Li-
Polymer 3.7V
950mAH
JST SH 1mm
1.0mm Head
Connector
Konektor Pin
Leads Housing
Shell Variasi 4P
JST SH 1mm
1.0mm Head
Connector
Konektor Pin
Leads Housing
Shell Variasi 2P
JST SH 1mm
1.0mm Head
Connector
Konektor Pin
Leads Housing
Shell Variasi 3P
USB Type-C
Female Soket
Power Charger
Port Waterproof
Kabel 10cm
Socket PH2.0
MINI SWITCH
TOGLE

6

13 Juni
2026

7

13 Juni
2026

8

13 Juni
2026

9

28 Juni
2026

10

28 Juni
2026

11

28 Juni
2026

12

2 Juli
2026

13

2 Juli
2026

32

1

Rp575.000

pcs

Rp575.000

1

Rp575.000

pcs

Rp575.000

3

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

33

1

Rp20.000

pcs

Rp20.000

5

Rp3.405

pcs

Rp17.025

1

Rp27.200

pcs

Rp27.200

2

Rp250.000

kg

Rp500.000

5

Rp2.500

pcs

Rp12.500

10

Rp250

pcs

Rp2.500

SWITCH ON
OFF SAKLAR
SENTER HI
QUALITY
BAHAN
TEMBAGAA
MURNI UJUNG
KAKI OVAL
(BUKAN
KOTAK)
TP5000 3.6V /
4.2V 1A DC
4.5V-9V Lithium
Battery Charger
Module
RT9013-33GB
Fixed 3.3V
500mA Linear
Volta ge
Regulators LDO
SOT-23-5 WJ
Richtek
Technology
MAX30102 Pulse
Oximeter and
Heart Rate Sensor
Detak Jantung
Sensor
eSUN PETG
Basic 3D
Filament Cost
Effective High
Strength 3D
Printing Filament
- White
DIODES
DMP2130L-7
Mosfet P-
Channel SMD3A
20V LG
EBK61913701
mark MP1
SAMWHA
Ferrite Bead 1000
Ohm 1K SMD
0805

14

2 Juli
2026

15

2 Juli
2026

16

10 Juli
2026

17

10 Juli
2026

18

10 Juli
2026

19

10 Juli
2026

34

10

Rp250

pcs

Rp2.500

1

Rp259.000

pcs

Rp259.000

5

5

5

5

4

4

5

4

Rp100

pcs

Rp500

Rp100

pcs

Rp500

Rp100

pcs

Rp500

Rp100

pcs

Rp500

Rp1.500

pcs

Rp6.000

Rp1.000

pcs

Rp4.000

Rp200

pcs

Rp1.000

Rp180.000

bulan  Rp720.000

1

Rp427.635

paket  Rp427.635

1

Rp174.985

box

Rp174.985

CB2012GM102E
Beads
SAMSUNG
Ferrite Bead 60
Ohm SMD 1210
CIB32P600NE
Beads
XIAO ESP32S3
Original Board
IoT Development
Kit - Dual Core
WiFi Bluetooth
5.0 BLE
Microcontroller

Resistor 0805 1M

Resistor 0805
100K
Resistor 0805
10K
Resistor 0805
6KB
avx Type A 10uF
16V
10uF 35V SMD
Capacitor
LED 3mm
diffused (green)
Pembelian
Hosting VPS
Strip Alat Cek
3in1 Elvasense
(Gula
Darah/Kolesterol/
Asam Urat)
Bundling 3 Box +
Lancet
Strip Alat Cek
3in1 Elvasense
(Gula
Darah/Kolesterol/
Asam Urat)
CHOL 10'S

20

10 Juli
2026

21

17 Juli
2026

22

23

24

25

26

27

28

29

18 Juli
2026
18 Juli
2026
18 Juli
2026
18 Juli
2026
18 Juli
2026
18 Juli
2026
18 Juli
2026
29 Juli
2026

30

10
Agustus
2026

31

2
Septembe
r

SubTotal (Rp)

Rp4.799.7
45

35

SEWA DAN JASA (MAKS 15%)

No  Tanggal

Uraian

1

2

3

4

5

6

22 Juli
2026
22 Juli
2026
23 Juli
2026
23 Juli
2026

29 Juli
2026

29
Agustus
2026

3D Print Base
Casing
3D Print Cover
Casing
3D Print Base
Casing
3D Print Cover
Casing
Domain
Registration -
antaraga.web.id
Biaya Pembuatan
Akun untuk
Register Aplikasi
@25dollar

SubTotal (Rp)

Jumlah
Pembeli-
an

Harga
Satuan
(Rp)

Satuan

Jumlah

4

4

2

2

1

Rp30.000

pcs

120.000

Rp45.000

pcs

180.000

Rp30.000

pcs

60.000

Rp45.000

pcs

90.000

Rp13.078

paket

13.078

1

Rp452.166

paket

452.166

915.244

TRANSPORTASI LOKAL (MAKS 30%)

No

Tanggal
Pengelua
ran

1

12 Juni
2026

2

12 Juni
2026

3

12 Juni
2026

Uraian

Biaya Ongkos
Kirim - PPG
Heart Rate
Monitor Sensor
for Arduino
Analog/Digital
Gravity
Biaya Asuransi
Pengiriman - PPG
Heart Rate
Monitor Sensor
for Arduino
Analog/Digital
Gravity
Biaya Jasa
Aplikasi - PPG
Heart Rate
Monitor Sensor
for Arduino
Analog/Digital

Jumlah
Pembeli-
an

Harga
Satuan
(Rp)

Satuan

Jumlah

1

Rp21.000

transaksi  Rp21.000

1

Rp2.300

transaksi  Rp2.300

1

Rp1.000

transaksi  Rp1.000

36

1

Rp1.000

transaksi  Rp1.000

1

Rp6.500

transaksi  Rp6.500

1

Rp2.000

transaksi  Rp2.000

1

Rp2.786

transaksi  Rp2.786

4

12 Juni
2026

5

12 Juni
2026

6

12 Juni
2026

7

13 Juni
2026

Gravity

Biaya Layanan -
PPG Heart Rate
Monitor Sensor
for Arduino
Analog/Digital
Gravity
Biaya Ongkos
Kirim - 20mm
22mm Silicone
Strap for Huawei
GT 2 3 4
Samsung Galaxy
Watch 7 6 5 4
Amazfit Garmin
Sport Breathable
Strap
Biaya Layanan -
20mm 22mm
Silicone Strap for
Huawei GT 2 3 4
Samsung Galaxy
Watch 7 6 5 4
Amazfit Garmin
Sport Breathable
Strap
Biaya Layanan
pada pembelian
Seeed Studio
XIAO ESP32-C3
Development
Board Mini WiFi
Bluetooth BLE
RISC-V Type-C
Module, dan
KABEL EXTRA
SOFT SILICON
AWG HIGH
TEMPERATURE
KABEL AWG
LENTUR
14AWG - 30
AWG AWG 14
16 18 20 22 24 2
hitam dan merah

8

13 Juni

Biaya ongkir

1

Rp29.500

transaksi  Rp29.500

37

1

Rp3.700

transaksi  Rp3.700

1

Rp1.000

transaksi  Rp1.000

1

Rp29.500

transaksi  Rp29.500

1

Rp3.700

transaksi  Rp3.700

1

Rp1.000

transaksi  Rp1.000

2026

9

13 Juni
2026

10

13 Juni
2026

11

13 Juni
2026

12

13 Juni
2026

13

13 Juni
2026

(ongkos kirim)
pada pembelian
DFRobot
Fermion :
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(pembelian 1)
Biaya Asuransi
Pembelian -
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(Pembelian 1)
Biaya Layanan -
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(Pembelian 1)
Biaya ongkir
(ongkos kirim)
pada pembelian
DFRobot
Fermion :
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(pembelian 2)
Biaya Asuransi
pembelian -
MAX30102
Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(Pembelian 2)
Biaya Layanan
dalam pembelian
MAX30102

Heart Rate and
Oximeter Sensor
(Breakout) -
SEN0518
(pembelian 2)
Biaya Ongkos
Kirim - Battery
Li-Polimer 3.7V
950 mAH 063443
Asuransi
Pengiriman pada
pembelian
Battery Li-
Polymer 3.7V
950mAH
Biaya Layanan -
Battery Li-
Polimer 3.7V 950
mAH 063443
Biaya ongkir
(ongkos kirim)
pembelian JST
SH 1mm 1.0mm
Head Connector
Konektor Pin
Leads Housing
Shell
Biaya layanan
pada pembelian
JST SH 1mm
1.0mm Head
Connector
Konektor Pin
Leads Housing
Shell
Biaya Ongkir
(ongkos kirim)
dalam pembelian
USB Type-C
Female Soket
Power Charger
Port Waterproof
Kabel 10cm
Socket PH2.0
Biaya layanan
dalam pembelian

14

13 Juni
2026

15

13 Juni
2026

16

13 Juni
2026

17

28 Juni
2026

18

28 Juni
2026

19

2 Juli
2026

20

2 Juli
2026

38

1

Rp8.000

transaksi  Rp8.000

1

Rp600

transaksi

Rp600

1

Rp1.000

transaksi  Rp1.000

1

Rp8.000

transaksi  Rp8.000

1

Rp2.000

transaksi  Rp2.000

1

Rp8.000

transaksi  Rp8.000

1

Rp2.000

transaksi  Rp2.000

39

1

Rp8.000

transaksi  Rp8.000

1

Rp2.000

transaksi  Rp2.000

1

Rp8.000

transaksi  Rp8.000

1

Rp2.000

transaksi  Rp2.000

USB Type-C
Female Soket
Power Charger
Port Waterproof
Kabel 10cm
Socket PH2.0
Biaya Ongkos
Kirim - MINI
SWITCH
TOGLE
SWITCH ON
OFF SAKLAR
SENTER HI
QUALITY
BAHAN
TEMBAGAA
MURNI UJUNG
KAKI OVAL
(BUKAN
KOTAK)
Biaya Layanan
dalam pembelian
MINI SWITCH
TOGLE
SWITCH ON
OFF SAKLAR
SENTER HI
QUALITY
BAHAN
TEMBAGAA
MURNI UJUNG
KAKI OVAL
(BUKAN
KOTAK)
Biaya ongkir
(ongkos kirim)
dalam pembelian
TP5000 3.6V /
4.2V 1A DC
4.5V-9V Lithium
Battery Charger
Module
Biaya Layanan
dalam pembelian
TP5000 3.6V /
4.2V 1A DC
4.5V-9V Lithium

21

2 Juli
2026

22

2 Juli
2026

23

2 Juli
2026

24

2 Juli
2026

40

1

Rp2.000

transaksi  Rp2.000

1

Rp2.000

transaksi  Rp2.000

1

Rp31.000

transaksi  Rp31.000

1

Rp1.000

transaksi  Rp1.000

1

Rp1.500

transaksi  Rp1.500

25

2 Juli
2026

26

10 Juli
2026

27

10 Juli
2026

28

10 Juli
2026

29

10 Juli
2026

Battery Charger
Module
Biaya Layanan -
RT9013-33GB
Fixed 3.3V
500mA Linear
Volta ge
Regulators LDO
SOT-23-5 WJ
Richtek
Technology
Biaya Layanan -
MAX30102 Pulse
Oximeter and
Heart Rate Sensor
Detak Jantung
Sensor
Biaya Ongkos
Kirim - eSUN
PETG Basic 3D
Filament Cost
Effective High
Strength 3D
Printing Filament
Biaya Layanan -
eSUN PETG
Basic 3D
Filament Cost
Effective High
Strength 3D
Printing Filament
Biaya layanan
paket DIODES
DMP2130L-7
Mosfet P-
Channel SMD3A
20V LG
EBK61913701
mark MP1 +
SAMWHA
Ferrite Bead 1000
Ohm 1K SMD 08
05
CB2012GM102E
Beads +
SAMSUNG
Ferrite Bead 60

41

1

Rp100.000

paket  Rp100.000

1

Rp21.500

transaksi  Rp21.500

1

Rp1.700

transaksi  Rp1.700

1

Rp1.000

transaksi  Rp1.000

1

Rp42.000

transaksi  Rp42.000

1

Rp41.500

transaksi  Rp41.500

Ohm SMD 1210
CI B32P600NE
Beads
Biaya Observasi
Lapangan dan
Pengujian Alat -
Ethical Clearance
di FKM Rumah
Sakit Airlangga
Biaya Ongkos
Kirim - XIAO
ESP32S3
Original Board
IoT Development
Kit - Dual Core
Wifi Bluetooth
5.0 BLE
Microcontroller
Biaya Asuransi
Pengiriman -
XIAO ESP32S3
Original Board
IoT Development
Kit - Dual Core
Wifi Bluetooth
5.0 BLE
Microcontroller
Biaya Layanan -
XIAO ESP32S3
Original Board
IoT Development
Kit - Dual Core
Wifi Bluetooth
5.0 BLE
Microcontroller
Biaya
Transportasi
Pengiriman
Fillament ke Jasa
3D Print Auto
Forge
menggunakan
Gosend
Biaya
Transportasi
Pengiriman Hasil

30

13 Juli
2026

31

17 Juli
2026

32

17 Juli
2026

33

17 Juli
2026

34

18 Juli
2026

35

22 Juli
2026

42

1

Rp42.300

transaksi  Rp42.300

1

Rp2.000

transaksi  Rp2.000

1

Rp28.500

transaksi  Rp28.500

1

Rp31.000

transaksi  Rp31.000

1

Rp29.500

transaksi  Rp29.500

3D Print dari Jasa
3D Print Auto
Forge menuju
PENS
menggunakan
Gosend
Biaya
Transportasi
Pengiriman Hasil
3D Print terbaru
(yang telah
direvisi dimensi
desainnya) dari
Jasa 3D Print
Auto Forge
menuju PENS
menggunakan
Gosend
Biaya Layanan -
MAX30102 Pulse
Oximeter and
Heart Rate Sensor
Detak Jantung
Sensor
Biaya
Transportasi
Pengujian
ANTARAGA 2
dari PENS
menuju lokasi
relawan (relawan
2 & 3 berada di
satu tempat)
Biaya
Transportasi
Pengujian
ANTARAGA 2
dari lokasi
relawan (relawan
2 & 3 berada di
satu tempat)
menuju PENS
Biaya
Transportasi
Pengujian
ANTARAGA 3
dari PENS

36

23 Juli
2026

37

29 Juli
2026

38

6 Agustus
2026

39

6 Agustus
2026

40

10
Agustus
2026

43

1

Rp34.500

transaksi  Rp34.500

1

Rp28.500

transaksi  Rp28.500

1

Rp35.000

transaksi  Rp35.000

1

Rp4.000

transaksi  Rp4.000

1

Rp37.000

transaksi  Rp37.000

1

Rp35.000

transaksi  Rp35.000

menuju lokasi
relawan 4
Biaya
Transportasi
Pengujian
ANTARAGA 3
dari lokasi
relawan 4 menuju
lokasi relawan 5
Biaya
Transportasi
Pengujian
ANTARAGA 2
dari lokasi
relawan 5 menuju
PENS
Biaya Ongkos
Kirim - Strip Alat
Cek 3in1
Elvasense (Gula
Darah/Kolesterol/
Asam Urat)
Bundling 3 Box +
Lancet
Biaya Layanan
Strip Alat Cek
3in1 Elvasense
(Gula
Darah/Kolesterol/
Asam Urat)
Bundling 3 Box +
Lancet
Biaya
Transportasi
Pengujian
ANTARAGA 4
dari PENS
menuju lokasi
relawan 6
Biaya
Transportasi
Pengujian
ANTARAGA 4
dari lokasi
relawan 6 menuju
PENS

41

10
Agustus
2026

42

10
Agustus
2026

43

10
Agustus
2026

44

10
Agustus
2026

45

14
Agustus
2026

46

14
Agustus
2026

44

1

Rp23.000

transaksi  Rp23.000

1

Rp23.500

transaksi  Rp23.500

1

Rp1.000

transaksi  Rp1.000

1

Rp21.000

transaksi  Rp21.000

1

Rp353.000

transaksi  Rp353.000

1

Rp31.500

transaksi  Rp31.500

1

Rp32.000

transaksi  Rp32.000

Rp1.192.0
86

47

2
Septembe
r

48

2
Septembe
r

49

2
Septembe
r

50

2
Septembe
r

51

5
Septembe
r

52

5
Septembe
r

53

5
Septembe
r

Biaya Transportas
Pengujian
ANTARAGA 5
dari PENS
menuju lokasi
relawan 7
Biaya Transportas
Pengujian
ANTARAGA 5
dari lokasi
relawan 7 menuju
PENS
Biaya Layanan -
Strip Alat Cek
3in1 Elvasense
(Gula
Darah/Kolesterol/
Asam Urat)
CHOL 10'S
Biaya Ongkir -
Strip Alat Cek
3in1 Elvasense
(Gula
Darah/Kolesterol/
Asam Urat)
CHOL 10'S

Cek Lab Lansia
di Klinik Parahita

Biaya
Transportasi Cek
Lab Lansia
(lokasi relawan
11 to Klinik
Parahita)
Biaya
Transportasi Cek
Lab Lansia
(lokasi Klinik
Parahita to lokasi
relawan 11)

SubTotal (Rp)

LAIN-LAIN (MAKS 15%)

No  Tanggal

Uraian

Jumlah

Harga

Satuan

Jumlah

45

Pembeli-
an

Satuan
(Rp)

1

1

Rp166.500

paket

166.500

Rp165.482

paket

165.482

2

Rp27.200

pcs

54.400

1

Rp40.500

paket

40.500

1

Rp166.043

paket

166.043

592.925
7.500.000
7.500.000
0

1

2

3

6 Juni
2026
4 Juli
2026

29 Juli
2026

4

4 Agustus
2026

5

29
Agustus
2026

Periklanan
Konten 1
Periklanan
Konten 2
Kerusakan
Komponen -
MAX30102 Pulse
Oximeter and
Heart Rate Sensor
Detak Jantung
Sensor
Pencetakan
Protokol Ethical
Clearance dan
Informed Consent

Periklanan
Konten 3

SubTotal (Rp)

Total Keseluruhan (Rp)

Jumlah Pendanaan (Rp)

Saldo (Rp)

Lampiran 3. Tabel Penggunaan Dana In Kind dari PENS

Tabel berikut memuat rincian penggunaan dana tambahan (in kind) senilai
Rp2.000.000  yang  difasilitasi  oleh  Politeknik  Elektronika  Negeri  Surabaya
(PENS) untuk mendukung optimalisasi riset dan pengembangan.

SEWA DAN JASA

No  Uraian

Jumlah
Pembeli-
an

Harga
Satuan
(Rp)

Jumlah

Dokumentasi

1

Penggunaan
Lab IT
C306*

SubTotal (Rp)

LAIN-LAIN

No.  Uraian

4

Rp450.000  Rp1.800.000

1.800.000

Jumlah
Pembelian

Harga
Satuan
(Rp.)

Jumlah

Dokumentasi

46

1

Pengajuan
Hak Cipta*

1

Rp200.000  Rp200.000

SubTotal (Rp)

Rp200.000

Total Keseluruhan (Rp)

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

Rp575.000

1

Rp575.000

47

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

48

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

Weekly Meeting dengan
Dosen Pendamping

17 Juni 2026

300

49

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
Relawan,
Terhadap
Pengujian  Alur  Data
End-to-End,
dan
Pengumpulan
Data
Sinyal

240

240

180

50

Lampiran 6 Sertifikat Hak Kekayaan Intelektual
Sebagai  bentuk  pelindungan  kekayaan  intelektual  atas  inovasi  yang  telah
dikembangkan,  berikut  dilampirkan  Surat  Pencatatan  Ciptaan  yang  diterbitkan
oleh Kementerian Hukum dengan Nomor Permohonan EC002026157207 tanggal
28 Agustus 2026 dan Nomor Pencatatan 001449089 sebagai bukti perolehan Hak
Cipta (HKI) untuk program komputer ANTARAGA.

51

Lampiran 7. Ethical Clearance

Berikut adalah sertifikat Ethical Clearance yang diterbitkan oleh KEPK FKM
Universitas  Airlangga  pada  23  Juli  2026  sebagai  bukti  kelayakan  etik  atas
prosedur  pengujian  prototipe  ANTARAGA  yang  melibatkan  partisipasi  relawan
manusia.

Gambar L

52

Lampiran 8. Informed Consent

Sebagai  bukti  pemenuhan  etika  pengujian,  berikut  dilampirkan  salah  satu
dokumen Informed Consent yang telah disetujui dan ditandatangani oleh relawan.
Dokumen  Informed  Consent  selengkapnya  dari  seluruh  subjek  uji  dapat  diakses
melalui tautan berikut: Informed Consent Seluruh Relawan

53

54

55

56


