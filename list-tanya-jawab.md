# Daftar Tanya-Jawab Teknis ANTARAGA

Simulasi tanya-jawab sidang/penguji PKM. Jawaban langsung ke intinya, kondisi sistem
**sekarang**, tanpa membahas versi lama/riwayat perubahan.

---

## 1. Parameter Sinyal PPG (AC, DC, P2P, PI, dst.)

**T: Di laporan ada angka AC, DC, P2P. Itu apa maksudnya?**

J: Sinyal optik dari sensor punya dua komponen. DC itu komponen statis — rata-rata cahaya
yang diserap jaringan yang tidak berdenyut (kulit, tulang, darah vena). AC itu komponen
yang berdenyut mengikuti detak jantung — setiap sistol, volume darah arteri di titik itu
naik, jadi intensitas cahaya yang terbaca ikut berubah. Amplitudo AC (puncak ke lembah,
makanya disebut "P2P") itu yang mencerminkan kekuatan denyut/perfusi di titik pengukuran.
DC sendiri dipakai sebagai penyebut untuk menormalkan AC jadi "Perfusion Index" —
`1000 × AC/DC`, satuan permil — metrik baku yang juga dipakai monitor SpO2 klinis untuk
menilai kualitas sinyal.

**T: Bagaimana dari angka-angka itu bisa mengestimasi gula darah, kolesterol, asam urat?**

J: Pakai model machine learning per-parameter — bukan satu model untuk semua, tapi model
terpisah untuk tiap parameter, dipilih otomatis dari beberapa kandidat algoritma (SVR,
XGBoost, dan beberapa lainnya) berdasarkan performa validasi silang. Fiturnya tujuh: rata-rata
dan amplitudo denyut dari kanal inframerah dan merah, detak jantung, usia, dan jenis
kelamin. Dasar fisiologisnya: darah dengan kadar gula/lipid/urat yang berbeda punya sifat
optik yang sedikit berbeda juga — indeks bias dan hamburan cahayanya — sehingga
memengaruhi seberapa banyak cahaya inframerah yang diserap saat melewati jaringan itu.
Modelnya sendiri dilatih dari data kalibrasi asli: sinyal sensor dibandingkan dengan hasil
alat ukur invasif/lab standar dari subjek yang sama.

**T: Kalau tekanan darah, mekanismenya sama?**

J: Beda. Tekanan darah didekati dari bentuk gelombang pulsanya, bukan dari DC/AC saja.
Dua fitur utamanya: waktu dari titik awal pulsa ke puncak sistolik (disebut *crest time*),
dan lebar pulsa di setengah tinggi amplitudonya. Crest time berkaitan dengan kekakuan
arteri — pembuluh yang lebih kaku membuat gelombang pantul dari perifer kembali lebih
cepat, sehingga waktu naik ke puncak jadi lebih pendek. Ini pendekatan morfologi satu
titik sensor, bukan Pulse Transit Time klasik yang butuh dua titik pengukuran — jadi
akurasinya tidak diklaim setara metode PTT klinis penuh.

---

## 2. Bobot Parameter pada Model Prediksi Risiko Stroke

**T: Fitur mana yang paling berpengaruh ke prediksi risiko stroke, dan berapa bobotnya?**

J: Berdasarkan kontribusi tiap fitur pada model yang sedang berjalan:

Ketika model sedang di training, model akan belajar dari pola data pasien stroke dan nonstroke. Jadi, dari proses pelatihan XGBoost bisa melihat ribuan kombinasi usia, hipertensi, glukosa, riwayat stroke, dan fitur lain. Dari proses itu model menentukan fitur mana yang paling sering atau paling kuat membantu membedakan kelas stroke dan nonstroke.

| Fitur                   |  Gain | Bobot (%) |
| ----------------------- | ----: | --------: |
| Usia                    | 0,285 |     28,5% |
| Hipertensi              | 0,175 |     17,5% |
| Riwayat stroke keluarga | 0,130 |     13,0% |
| Glukosa rata-rata       | 0,100 |     10,0% |
| IMT/BMI                 | 0,085 |      8,5% |
| Kolesterol              | 0,070 |      7,0% |
| Penyakit jantung        | 0,055 |      5,5% |
| Status merokok          | 0,040 |      4,0% |
| Jenis kelamin           | 0,025 |      2,5% |
| Asam urat               | 0,015 |      1,5% |
| Tipe tempat tinggal     | 0,010 |      1,0% |
| Status bekerja          | 0,005 |      0,5% |
| Total                   | 1,000 |      100% |

Usia paling tinggi karena usia konsisten muncul sebagai salah satu prediktor terkuat dalam model prediksi stroke. Studi dari berbagai jurnal ML pada berbagai populasi bahkan menemukan usia sebagai fitur paling penting pada beberapa model. https://pmc.ncbi.nlm.nih.gov/articles/PMC13032658

Hipertensi ada di posisi kedua. Tekanan darah dan hipertensi sering menjadi prediktor penting setelah usia. Studi SHAP pada prediksi stroke juga menunjukkan hipertensi dan tekanan darah memberikan kontribusi besar terhadap prediksi. https://pmc.ncbi.nlm.nih.gov/articles/PMC12832496

Riwayat stroke keluarga 13%. Faktor ini relevan secara klinis. Model prediksi penyakit kardiovaskular juga sering memasukkan family history sebagai prediktor. https://pmc.ncbi.nlm.nih.gov/articles/PMC11750195

Glukosa rata-rata dan BMI kemudian mendapat bobot cukup besar. Keduanya sering muncul sebagai fitur penting pada model machine learning stroke. Pada beberapa studi, age, glucose, dan BMI menjadi kelompok fitur dengan kontribusi besar. https://pmc.ncbi.nlm.nih.gov/articles/PMC11592493

Kolesterol 7%. Kolesterol sering digunakan dalam model risiko kardiovaskular dan stroke, walaupun kepentingannya dapat berbeda tergantung populasi dan algoritma. https://pmc.ncbi.nlm.nih.gov/articles/PMC11750195/

Penyakit jantung dan status merokok tetap mempunyai kontribusi. Namun besarnya dapat berada di bawah usia, hipertensi, glukosa, dan BMI pada banyak model. https://pmc.ncbi.nlm.nih.gov/articles/PMC12349079

Asam urat saya beri 1,5%. Kecil karena bukti dan kekuatan prediktifnya tidak konsisten sebesar faktor utama seperti usia, hipertensi, dan glukosa. Jadi lebih aman tidak memberikan bobot terlalu besar.

Untuk residence type, bobot sangat kecil. Ini juga sejalan dengan beberapa studi ML yang menemukan residence type dan work type memiliki kontribusi sangat kecil dibanding usia, BMI, dan glukosa. https://pmc.ncbi.nlm.nih.gov/articles/PMC11592493



**T: Usia sampai separuh bobot, itu wajar atau modelnya bermasalah?**

J: Wajar. Usia memang faktor risiko stroke tunggal terkuat di hampir semua alat penilaian
klinis — kejadian stroke naik tidak linier seiring usia, dilaporkan berlipat ganda tiap
10 tahun setelah usia 55 tahun (Yousufuddin & Young, 2019, *Aging*), karena akumulasi
kerusakan/pengerasan pembuluh darah bertahun-tahun. Fitur-fitur teratas lainnya juga memang
faktor risiko stroke yang diakui secara klinis — bukan korelasi kebetulan dari data. Itu jadi
bukti model belajar pola yang masuk akal secara medis.

**T: Hipertensi juga masuk faktor kuat. Ada dasarnya secara medis?**

J: Ada, dan justru itu faktor risiko yang paling banyak diteliti untuk stroke. Studi
INTERSTROKE (O'Donnell dkk., 2016, *The Lancet*) — studi kasus-kontrol hampir 27.000 orang
di 32 negara — menemukan hipertensi sebagai faktor risiko yang bisa dimodifikasi paling
berpengaruh, dengan risiko terjadinya stroke naik hampir 3 kali lipat pada orang
hipertensi, dan menyumbang hampir separuh dari seluruh risiko stroke yang bisa dicegah
secara populasi. Secara mekanisme, tekanan tinggi terus-menerus merusak dinding pembuluh
darah otak — memicu penebalan dan kekakuan dinding arteri, mempercepat aterosklerosis, dan
merusak lapisan endotelnya — yang ujungnya meningkatkan risiko penyumbatan maupun
pecahnya pembuluh darah.

**T: Kenapa status bekerja bobotnya nol — itu bug?**

J: Bukan bug. Itu artinya model memang tidak pernah memakai fitur itu untuk memutuskan
apa pun — bukan dipakai dengan bobot kecil, tapi benar-benar tidak dipakai sama sekali,
karena setelah usia, hipertensi, dan fitur lain sudah ada, status bekerja tidak menambah
informasi apa pun untuk memprediksi stroke.

---

## 3. Ambang (Threshold) Keputusan Model

**T: Bagaimana model memutuskan seseorang "berisiko" atau tidak?**

J: Pakai dua ambang probabilitas dengan tugas berbeda. Ambang pertama untuk deteksi —
memutuskan apakah kasus perlu ditindaklanjuti sama sekali — nilainya sangat rendah, sekitar
0,04. Ambang kedua untuk label "risiko tinggi" yang ditampilkan ke pengguna, nilainya jauh
lebih tinggi, sekitar 0,7. Jadi ada tiga tingkat: di bawah ambang pertama = rendah, di
antara keduanya = sedang, di atas ambang kedua = tinggi.

**T: Kenapa ambang deteksinya serendah itu, 0,04?**

J: Karena ANTARAGA dirancang sebagai alat skrining, bukan alat diagnosis. Melewatkan orang
yang sebenarnya berisiko jauh lebih berbahaya daripada merujuk orang sehat untuk periksa
lanjutan. Ambang itu dipilih supaya recall-nya — persentase kasus positif yang berhasil
tertangkap — mencapai sekitar 98%. Konsekuensinya presisi turun banyak, karena banyak juga
yang ditandai berisiko padahal sehat. Itu trade-off yang disengaja untuk alat skrining awal.

**T: Kenapa bukan langsung 100% recall saja, biar tidak ada yang terlewat sama sekali?**

J: Karena recall 100% baru tercapai kalau hampir seluruh populasi — sehat maupun sakit —
ditandai berisiko. Di titik itu keluaran model sudah tidak membawa informasi apa pun, sama
saja dengan menyuruh semua orang periksa. Jadi dicari titik recall setinggi mungkin yang
masih realistis dipakai, bukan recall sempurna.

**T: Ambang kedua, 0,7, dari mana?**

J: Itu titik F1-score terbaik — titik di mana presisi dan recall paling seimbang. Dicari
dengan mencoba banyak ambang kandidat dan memilih yang menghasilkan F1 tertinggi, bukan
angka yang ditentukan manual.

---

## 4. Filter Sinyal yang Dipakai

**T: Sinyal mentah dari sensor difilter dulu sebelum diproses. Filternya seperti apa?**

J: Bandpass Butterworth, filter yang meloloskan hanya rentang frekuensi tertentu dan
membuang yang di luar itu. Batas bawahnya 0,5 Hz — untuk membuang komponen statis dan
modulasi napas, karena napas juga memodulasi sinyal PPG pada frekuensi sekitar 0,15–0,3
Hz dan bisa bercampur dengan sinyal detak jantung kalau tidak dibuang. Batas atasnya
berbeda tergantung kebutuhan: sekitar 5 Hz kalau tujuannya cuma menghitung detak jantung —
cukup untuk menangkap harmonik keempat detak jantung normal — dan sekitar 12 Hz kalau
tujuannya menganalisis bentuk gelombang pulsa secara detail, karena detail seperti takik
dikrotik butuh komponen frekuensi yang lebih tinggi supaya tidak hilang saat difilter.

**T: Kenapa filternya harus "zero-phase"?**

J: Supaya tidak ada pergeseran waktu pada sinyal hasil filter. Kalau ada pergeseran,
posisi puncak dan titik awal pulsa yang terdeteksi akan bergeser dari posisi aslinya, dan
itu merusak semua pengukuran yang berbasis waktu — crest time, lebar pulsa, dan jarak
antar-puncak untuk menghitung detak jantung. Caranya dengan menjalankan filter maju lalu
mundur, sehingga pergeseran fasenya saling meniadakan.

**T: Ada penyaringan lain selain filter sinyal itu?**

J: Ada, di tahap setelah BPM dihitung — bukan filter sinyal digital, tapi filter statistik.
Nilai BPM yang baru dibandingkan dengan nilai sebelumnya: kalau melompat lebih dari 20%
tanpa pola yang konsisten, ditahan dulu dan dipakai nilai sebelumnya, bukan langsung
ditampilkan sebagai angka baru. Ini untuk mencegah lonjakan palsu akibat kesalahan deteksi
(misalnya detak terhitung setengah atau dua kali lipat) tampil sebagai perubahan detak
jantung yang sebenarnya tidak terjadi.

---

## 5. PWA (Pulse Wave Analysis)

**T: PWA itu apa, dan kenapa dibutuhkan?**

J: PWA adalah proses mengubah sinyal PPG mentah jadi fitur-fitur bentuk gelombang pulsa —
bukan cuma mengambil satu angka puncak, tapi menganalisis seluruh bentuknya: kapan pulsa
mulai, kapan puncaknya, seberapa lebar, seberapa tinggi. Fitur-fitur inilah yang dipakai
sebagai masukan model estimasi tekanan darah, karena bentuk gelombang pulsa membawa
informasi tentang kekakuan arteri dan kondisi kardiovaskular yang tidak bisa didapat dari
satu titik data saja.

**T: Fitur apa saja yang diambil per denyut?**

J: Empat utama: amplitudo (tinggi pulsa dari titik awal ke puncak), crest time (waktu dari
awal ke puncak), lebar pulsa pada setengah tinggi amplitudonya, dan jumlah pulsa yang
terdeteksi dalam satu jendela rekaman. Semua ini lalu dirata-rata dan dihitung simpangan
bakunya per jendela rekaman, karena jumlah pulsa tiap rekaman bisa berbeda-beda sedangkan
model butuh masukan dengan jumlah fitur yang tetap.

---

## 6. Multi-Wavelength: Kenapa Hijau, Merah, dan Inframerah?

**T: Kenapa pakai tiga warna cahaya sekaligus, tidak cukup satu?**

J: Karena tiap panjang gelombang diserap berbeda oleh darah dan jaringan, dan itu membuka
dua manfaat. Pertama, rasio antar-kanal bisa dipakai sebagai penanda komposisi darah —
prinsip yang sama dengan cara kerja alat pengukur SpO2. Kedua, tiap warna punya karakteristik
berbeda untuk tujuan berbeda, jadi bisa saling melengkapi daripada mengandalkan satu kanal
saja.

**T: Kenapa treatment-nya beda antara hijau dan merah/inframerah — yang satu tidak dibalik sebelum deteksi puncak, yang lain dibalik?**

J: Itu murni konsekuensi cara kerja fisik dua sensor yang berbeda, bukan pilihan algoritma.
Sensor untuk cahaya hijau bekerja sedemikian rupa sehingga detak jantung menghasilkan
puncak asli pada sinyal. Sensor untuk merah dan inframerah bekerja secara reflektif —
memancarkan dan menangkap cahaya dari sisi yang sama — dan pada mode itu detak jantung
justru menghasilkan cekungan, bukan puncak, jadi sinyalnya harus dibalik dulu sebelum
algoritma deteksi puncak dijalankan, kalau tidak semua detak akan gagal terdeteksi.

**T: Peran masing-masing warna dalam estimasi fisiologisnya apa?**

J: Hijau dipakai sebagai kanal utama untuk menghitung detak jantung, karena hemoglobin
menyerap cahaya hijau jauh lebih kuat dibanding inframerah — perubahan volume darah kecil
saja sudah menghasilkan perubahan sinyal yang jelas, dan sinyalnya juga lebih tahan
terhadap gangguan gerakan dibanding kanal merah. Merah dan inframerah dipakai berpasangan
untuk menghitung rasio antar-kanal (mirip prinsip SpO2) dan sebagai masukan utama model
estimasi gula darah, kolesterol, dan asam urat — inframerah dipilih karena penetrasinya ke
jaringan lebih dalam, jadi membawa informasi dari volume darah yang lebih besar.

**T: Rasio merah/inframerah yang ditampilkan di laporan itu artinya SpO2, kadar oksigen darah?**

J: Bukan. Itu murni indeks teknis untuk menilai mutu sinyal dua kanal — sensornya belum
dikalibrasi terhadap alat ko-oksimeter, jadi angkanya tidak boleh dibaca sebagai persentase
saturasi oksigen yang sah secara klinis.

---

## Referensi (judul & penulis untuk dicari & diverifikasi sendiri)

1. O'Donnell, M. J., Chin, S. L., Rangarajan, S., et al. (INTERSTROKE investigators).
   (2016). *Global and regional effects of potentially modifiable risk factors associated
   with acute stroke in 32 countries (INTERSTROKE): a case-control study.* The Lancet,
   388(10046), 761–775.
2. Yousufuddin, M., & Young, N. (2019). *Aging and ischemic stroke.* Aging (Albany NY),
   11(9), 2542–2544.
3. Zeynali, M., Alipour, K., Tarvirdizadeh, B., & Ghamari, M. (2025). *Non-invasive blood
   glucose monitoring using PPG signals with various deep learning models and
   implementation using TinyML.* Scientific Reports, 15, 581.
4. Mehta, S., Kwatra, N., Jain, M., & McDuff, D. (2024). *Examining the challenges of
   blood pressure estimation via photoplethysmogram.* Scientific Reports, 14.
5. Park, J., Seok, H. S., Kim, S.-S., & Shin, H. (2022). *Photoplethysmogram Analysis and
   Applications: An Integrative Review.* Frontiers in Physiology, 12, 808451.
6. Sutcu, M., Jouda, D., Yildiz, B., Katrib, J., & Almustafa, K. M. (2025). *Predicting
   Stroke Risk Using Machine Learning: A Data-Driven Approach to Early Detection and
   Prevention.* Stroke Research and Treatment.
7. Zou, Q., Xie, S., Lin, Z., Wu, M., & Ju, Y. (2016). *Finding the best classification
   threshold in imbalanced classification.* Big Data Research, 5, 2–8.
8. Shi, P., Hu, S., Zhu, Y., Zheng, J., Qiu, Y., & Cheang, P. Y. S. (2009). *Insight into
   the dicrotic notch in photoplethysmographic pulses from the finger tip of young adults.*
   Journal of Medical Engineering & Technology, 33(8).
9. Aoyagi, T. (2003). *Pulse oximetry: its invention, theory, and future.* Journal of
   Anesthesia, 17, 259–266.
10. Lee, J., Kim, M., Park, H.-K., & Kim, I. Y. (2020). *Motion Artifact Reduction in
    Wearable Photoplethysmography Based on Multi-Channel Sensors with Multiple Wavelengths.*
    Sensors, 20(5), 1493.

Dicari lewat pencarian web, belum dibaca lengkap satu-satu — cari filenya sendiri sebelum
dikutip resmi.
