# Data referensi eksternal — bukan dataset training utama

`gusti_2025_max30105_glucose.csv` adalah salinan Tabel 2 dari:

> Gusti, A. W. R., Kemalasari, & Parasian C., J. S. P. (2025). *Deteksi Dini
> Kesehatan Berdasarkan Nilai Kadar Gula Darah, Kolesterol, dan Asam Urat
> Non-Invasif dengan Multi-Layer Perceptron.* Jurnal Riset Rekayasa Elektro,
> 7(2), 127–136.

30 baris ini adalah data uji asli mereka: `ir1_raw` (nilai mentah sensor
inframerah MAX30105), `age_years`, `heart_rate_bpm` sebagai input, dan kolom
`*_ground_truth` (alat invasif Elvasense 3in1) sebagai target. Kolom
`*_paper_mlp` adalah keluaran model MLP mereka sendiri — disertakan untuk
sanity-check, bukan untuk dilatih ulang sebagai target.

## Mengapa ini TIDAK dipakai langsung sebagai dataset training ANTARAGA

1. **Beda hardware.** `ir1_raw` adalah nilai mentah MAX30105 mereka pada
   posisi/kalibrasi sensor spesifik alat mereka. Hardware ANTARAGA (PPG
   multi-wavelength SON1303 + MAX30102, lihat `model/ppg_features.py`)
   punya rentang dan karakteristik sinyal yang berbeda — nilai mentah tidak
   bisa dibandingkan apple-to-apple tanpa kalibrasi ulang di alat ANTARAGA
   sendiri.
2. **n sangat kecil.** Hanya 30 baris, dari populasi Puskesmas Keputih
   Surabaya. Tidak cukup untuk melatih model yang general ke populasi
   pengguna ANTARAGA.
3. **Tidak ada data tekanan darah.** Jurnal ini hanya mengestimasi gula
   darah, kolesterol, asam urat — bukan tekanan darah. ANTARAGA butuh
   tekanan darah juga (lihat proposal), yang harus didekati lewat jalur lain
   (morfologi pulsa / pulse transit time, bukan dari jurnal ini).
4. **Tidak ada fitur morfologi pulsa.** Input mereka cuma satu nilai IR
   mentah + usia + HR, bukan fitur PWA (amplitude, crest time, dst.) yang
   diekstrak `model/ppg_features.py`. Kalaupun dipakai, perlu mapping
   ulang fitur, bukan langsung pakai kolom `ir1_raw`.

## Cara pakai yang aman

- Sebagai **referensi/sanity-check**: bandingkan urutan besaran (relative
  trend) hasil model ANTARAGA dengan data ini, bukan untuk mencocokkan nilai
  absolut.
- Sebagai **kandidat data tambahan untuk transfer learning** *nanti*, setelah
  ada data kalibrasi asli dari prototipe ANTARAGA sendiri (lihat
  `data/calibration/README.md`) — dan itu pun harus diuji apakah benar
  membantu atau malah menyesatkan, tidak diasumsikan otomatis berguna.
- **Jangan** digabung mentah-mentah dengan data sintetis buatan sendiri untuk
  "menambah" dataset — itu membuat model belajar menebak balik fungsi yang
  kita buat sendiri, bukan fisiologi pengguna asli. Error kecil yang
  dihasilkan dengan cara ini tidak berarti model akurat di pemakaian nyata.
