# Data kalibrasi ANTARAGA (untuk dilatih nanti, bukan sekarang)

Folder ini kosong sampai prototipe fisik ANTARAGA selesai dan tahap
"Pengujian Alat" di proposal dijalankan. `model/train_ppg_vitals.py` akan
gagal dengan pesan jelas kalau file `calibration_data.csv` di sini belum ada
- itu sengaja, supaya tidak ada yang tergoda melatih model dengan data yang
belum valid.

## Format yang diharapkan: `calibration_data.csv`

Satu baris = satu sesi pengukuran (satu responden, satu waktu), terdiri dari
sinyal PPG mentah pada window tertentu (disarankan >= 8 detik, sampling rate
konstan) + nilai ground truth dari alat medis pembanding pada saat yang sama.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `subject_id` | string | ID responden (anonim, bukan nama asli) |
| `session_ts` | ISO 8601 | Waktu pengukuran |
| `fs_hz` | float | Sampling rate sinyal PPG mentah (Hz) |
| `green_raw` | string | Sinyal channel hijau (SON1303), berupa list nilai dipisah `;` |
| `red_raw` | string | Sinyal channel merah (MAX30102), list nilai dipisah `;` |
| `infrared_raw` | string | Sinyal channel infrared (MAX30102), list nilai dipisah `;` |
| `age_years` | float | Usia responden saat pengukuran |
| `systolic_bp_mmhg` | float | Ground truth tekanan darah sistolik (tensimeter standar) |
| `diastolic_bp_mmhg` | float | Ground truth tekanan darah diastolik (tensimeter standar) |
| `blood_glucose_mg_dl` | float | Ground truth gula darah (alat invasif/strip, bukan estimasi) |

Catatan:
- Ground truth **wajib** dari alat medis pembanding yang diukur pada waktu
  yang (hampir) bersamaan dengan sinyal PPG - sama seperti metode jurnal
  Gusti et al. (2025) yang membandingkan ke Elvasense/tensimeter.
- Targetkan minimal puluhan responden lintas rentang usia & kondisi (bukan
  cuma mahasiswa sehat) supaya model tidak bias ke satu kelompok demografis.
- `model/train_ppg_vitals.py` akan memanggil
  `model.ppg_features.extract_pwa_features()` pada `green_raw`/`red_raw`/
  `infrared_raw` untuk menghasilkan fitur, lalu melatih `MLPRegressor`
  multi-output (`systolic_bp_mmhg`, `diastolic_bp_mmhg`,
  `blood_glucose_mg_dl`).
- Kalau jumlah baris masih sangat kecil (puluhan), evaluasi pakai
  leave-one-out CV, bukan train/test split biasa - dan tetap laporkan
  interval ketidakpastian, jangan klaim angka akurasi tunggal seperti
  90% tanpa konteks ukuran sampel (lihat keterbatasan yang diakui sendiri
  oleh Gusti et al. 2025 di bagian kesimpulan mereka).
