# Narasi Fix - Logbook ANTARAGA

---

Narasi fix final (mencakup kontribusi seluruh tim) untuk tanggal-tanggal yang sebelumnya ditolak/unsubmit, sudah disesuaikan dengan laporan kemajuan terbaru yang menggunakan SVR dan XGBoost untuk estimasi nilai vital (pengganti MLP). Diambil dari kolom `NARASI FIX` pada `DRAFT LOGBOOK ANTARAGA 2026 - FIX LOGBOOK.csv`, siap ditempel kembali ke kolom yang sama saat submit ulang.

---

## 16 Agustus 2026

*Pengolahan Hasil Pengujian, Koordinasi Persiapan Monev, dan Penyusunan Laporan Kemajuan*

Pada sisi machine learning, Adam merancang model Multilayer Perceptron (MLP) untuk kalibrasi sensor PPG. Model XGBoost yang sebelumnya telah selesai dikembangkan berfungsi memprediksi risiko stroke dari nilai vital, namun nilai-nilai vital tersebut masih harus diukur menggunakan alat invasif. Tugas model MLP adalah menerjemahkan sinyal optik dari sensor menjadi nilai vital, sehingga pengguna tidak perlu ditusuk jarum atau dipasangi manset untuk memperoleh data tersebut. Selain merancang model, Adam juga menerapkan rancangan MLP ke dalam kode pelatihan dan menyambungkannya ke dashboard agar model dapat dilatih langsung dari dashboard web, lalu melatihnya menggunakan data kalibrasi yang sudah terkumpul, sekaligus memeriksa akurasi model yang dihasilkan. Model MLP berhasil dibuat, dengan mekanisme yang memungkinkan model dilatih ulang secara mudah ketika ada data subjek baru, cukup dengan mengeklik tombol latih MLP pada dashboard. Namun, akurasi model masih tergolong rendah karena jumlah data subjek yang tersedia masih sedikit (terbatas). Karena keterbatasan ini, Adam mulai mencoba studi literatur terkait model lain yang mampu menangani data terbatas dengan lebih baik, seperti XGBoost dan SVR, sebagai kandidat pengganti MLP untuk tugas estimasi nilai vital. 

Pada sisi hardware, Ally mengolah data hasil empat sesi pengujian yang sudah terkumpul dari sisi perangkat keras, lalu menyusun bagian perangkat keras pada laporan kemajuan. Kadek meninjau kelengkapan data dari empat sesi pengujian (6 relawan), lalu mengoordinasikan penyusunan laporan kemajuan agar setiap bagian dapat diselesaikan tepat waktu. Tiwi merapikan arsip administrasi dari empat sesi pengujian yang sudah berjalan, lalu menulis bagian laporan kemajuan yang menjadi tanggung jawabnya. Zeven mengolah dokumentasi yang terkumpul dari empat sesi pengujian, lalu menyiapkan bahan visual untuk laporan kemajuan dan konten media sosial.

---

## 27 Agustus 2026

*Asistensi dan Bimbingan Rutin kepada Dosen Pendamping*

Seluruh anggota tim ANTARAGA (Adam, Ally, Kadek, Tiwi, dan Zeven) melaksanakan asistensi dan bimbingan rutin bersama dosen pendamping untuk mengevaluasi perkembangan model MLP yang digunakan pada tahap awal. Sebagai kelanjutan dari studi literatur yang dimulai sebelumnya, Adam menemukan bahwa terdapat kandidat model lain yang jauh lebih baik daripada MLP untuk menangani data yang sedikit. Berdasarkan hasil pencarian dan perbandingan beberapa algoritma regresi, ditemukan kandidat model SVR dan XGBoost yang menunjukkan performa lebih baik pada beberapa parameter dibandingkan model MLP. Hasil temuan tersebut kemudian dibahas bersama dosen pendamping sebagai dasar untuk menentukan arah pengembangan model AI estimasi selanjutnya. Pembahasan bimbingan turut mencakup progres logbook, laporan kemajuan, hasil pengujian yang telah dilakukan, keterbatasan jumlah data kalibrasi, rencana evaluasi beberapa algoritma regresi alternatif sebagai pembanding MLP, rencana pengujian berikutnya, serta pembagian tugas untuk persiapan presentasi PKP2. Dari hasil diskusi, ditetapkan bahwa pengembangan model berikutnya akan dilakukan melalui evaluasi model berdasarkan masing-masing parameter fisiologis, sehingga dapat diperoleh konfigurasi model yang paling sesuai. Dosen pendamping juga memberikan saran dan masukan terkait hasil monev 3 yang telah dilaksanakan sebelumnya.

---

## 29 Agustus 2026

*Finalisasi dan penguploadan Pengiklanan Konten Medsos 3*

Melakukan finalisasi dan publikasi konten media sosial ketiga yang menampilkan peragaan sistem ANTARAGA yang sedang berjalan. Adam melanjutkan evaluasi model SVR dan XGBoost berdasarkan hasil perbandingan sebelumnya. Analisis dilakukan untuk menentukan model yang paling sesuai pada masing-masing parameter fisiologis dengan mempertimbangkan performa hasil training dan validasi. Dari evaluasi tersebut disusun konfigurasi model akhir yang akan digunakan sebagai pengganti model MLP pada sistem kalibrasi ANTARAGA. Adam juga menyiapkan bahan teknis peragaan sistem ANTARAGA untuk mendukung konten, sekaligus membuat akun Google Play Console dan menyelesaikan pembayaran biaya pendaftaran sebagai persiapan publikasi aplikasi mobile ANTARAGA melalui Google Play Store. Ally menyiapkan bahan visual dari sisi perangkat keras ANTARAGA yang digunakan dalam peragaan sistem untuk mendukung pembuatan konten media sosial ketiga. Kadek mengoordinasikan proses finalisasi, pengunggahan, dan pengiklanan konten agar publikasi ANTARAGA dapat menjangkau lebih banyak pengguna. Tiwi menyusun naskah akhir konten media sosial ketiga serta membantu proses pengunggahan dan pengiklanan konten pada media sosial ANTARAGA. Zeven menyelesaikan desain visual konten media sosial ketiga serta menyiapkan dan mengunggah bahan visual bersama tim untuk mendukung publikasi konten ANTARAGA. Hasilnya, konten media sosial ketiga berhasil difinalisasi, diunggah, dan diiklankan, serta persiapan awal distribusi aplikasi ANTARAGA melalui Google Play Store telah dilakukan.

---

## 2 September 2026

*Menjalankan Pengujian Kelima Smartband ANTARAGA bersama Relawan, Menambah 3 Data Kalibrasi Baru, Sekaligus Melatih Ulang Model MLP dengan Data yang Sudah Bertambah*

Melaksanakan pengujian kelima smartband ANTARAGA bersama relawan dan memperoleh 3 data kalibrasi baru. Selain penambahan data, mulai diterapkan konfigurasi model baru berdasarkan hasil evaluasi sebelumnya, yaitu penggunaan SVR dan XGBoost per parameter fisiologis yang sesuai untuk estimasi data vital. Keputusan akhirnya adalah mengganti model MLP dengan konfigurasi model baru ini, sebagai tindak lanjut dari hasil pembahasan bersama dosen pendamping pada 27 Agustus dan evaluasi lanjutan pada 29 Agustus sebelumnya. Data baru yang diperoleh dari pengujian kelima ini kemudian ditambahkan ke dataset kalibrasi dan data latih model, untuk mendukung peningkatan performa model dalam melakukan estimasi data vital. Selain itu, Adam mulai menyusun draf Laporan Kemajuan pada bagian perkembangan software ANTARAGA, meliputi perkembangan aplikasi mobile, backend server, integrasi sistem, serta model AI deteksi risiko stroke yang telah dikembangkan. Ally mendampingi pengujian dari sisi perangkat keras. Kadek mengoordinasikan pelaksanaan pengujian kelima, sekaligus melakukan pembelian strip kolesterol tambahan sebagai kelengkapan alat ukur pendukung pengujian. Tiwi membantu administrasi dan pencatatan data, sedangkan Zeven mendokumentasikan kegiatan dan mengumpulkan bahan visual untuk kebutuhan presentasi dan media sosial.

---

## 3 September 2026

*Finalisasi Laporan Kemajuan PKM 2026*

Adam melakukan penyusunan bagian perangkat lunak dan kecerdasan buatan, serta melakukan finalisasi narasi untuk keseluruhan bagian software. Ally melakukan finalisasi bagian perkembangan perangkat keras ANTARAGA, termasuk kondisi smartband, komponen sensor, serta perkembangan integrasi perangkat untuk mendukung demonstrasi produk. Kadek melakukan finalisasi penyusunan Laporan Kemajuan dengan mereview narasi dan isi yang dimasukkan tim, serta mengerjakan lampiran-lampiran sesuai kebutuhan laporan kemajuan. Tiwi melakukan finalisasi bagian pendahuluan, metode pelaksanaan, luaran, serta bagian administrasi yang diperlukan dalam Laporan Kemajuan, dan melakukan perapian tata tulis dokumen. Zeven melakukan finalisasi input dokumentasi visual untuk Laporan Kemajuan, screenshot antarmuka website dan aplikasi mobile, dokumentasi produk ANTARAGA, surat HKI, serta seluruh dokumentasi yang dibutuhkan pada laporan kemajuan.

---

## 5 September 2026

*Melanjutkan Pembuatan Laporan Kemajuan dan Pengujian 6*

Kegiatan hari ini diawali dengan revisi minor Laporan Kemajuan, dilanjutkan dengan mobilisasi tim dari PENS menuju lokasi relawan pertama, lalu ke Klinik Parahita untuk memperoleh data pembanding, kemudian menuju lokasi relawan berikutnya untuk pelaksanaan pengujian keenam smartband ANTARAGA. Adam menambah 2 data kalibrasi dari pengujian laboratorium dan alat pembanding terstandar (pengujian keenam). Di sela sesi ini, dilakukan pemeriksaan terhadap metode validasi pada skrip pelatihan MLP. Adam menemukan bahwa sebelumnya pembagian data dilakukan berdasarkan baris rekaman, bukan berdasarkan subjek, sehingga terdapat risiko data dari subjek yang sama masuk ke data latih dan data uji. Untuk mengurangi risiko kebocoran informasi tersebut, metode validasi diperbaiki menggunakan Leave-One-Subject-Out (LOSO). Model kemudian dilatih ulang dan divalidasi menggunakan 11 subjek kalibrasi yang telah terkumpul hingga saat ini, sehingga evaluasi performa model dapat dilakukan dengan pemisahan berdasarkan subjek yang lebih sesuai. Selain itu, dilakukan finalisasi implementasi model SVR dan XGBoost, sebagai model pengganti MLP yang telah ditetapkan sebelumnya, beserta evaluasi hasil training pada 11 data relawan (subjek) yang telah terkumpul. Ally mendampingi proses pengambilan data dari sisi perangkat keras sekaligus menyempurnakan bagian perangkat keras pada laporan kemajuan. Kadek mengoordinasikan pengujian, penambahan data kalibrasi lanjutan, serta memimpin penyusunan laporan kemajuan secara menyeluruh. Kegiatan ini terjadwal untuk melakukan pengujian terlebih dulu, dilanjutkan dengan melanjutkan laporan kemajuan dan pelatihan model, dimulai dari keberangkatan bersama dari PENS pada pukul 1 ke lokasi relawan, lalu ke Klinik Parahita bersama relawan, lalu kembali ke kediaman relawan untuk dilakukan pengujian kepada tetangga relawan, kembali ke PENS dan melanjutkan laporan kemajuan serta pelatihan model di Kopi Kenangan hingga pukul 23.00 (tutup). Tiwi mencatat dan mengarsipkan data hasil pengujian serta menyusun bagian administratif laporan. Zeven mendokumentasikan kegiatan dan menyiapkan bahan visual pendukung laporan kemajuan.
