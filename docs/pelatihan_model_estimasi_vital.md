# Cara Melatih Model Estimasi Vital ANTARAGA

Model estimasi vital (gula darah, kolesterol, asam urat, sistolik, diastolik dari sinyal PPG)
dipilih otomatis dari beberapa algoritma (MLP, SVR, KNN, Random Forest, ExtraTrees,
GradientBoosting, XGBoost) dan beberapa set fitur, per parameter — algoritma dengan R² tertinggi
disimpan sebagai model produksi. Metodologinya sama persis antara notebook eksplorasi
(`model/test_loso.ipynb`), endpoint dashboard (`/v1/calibrate/train`), dan skrip CLI di dokumen ini —
satu sumber logika di `api/vital_model_training.py`.

Ada 3 cara melatih ulang model. Pilih salah satu sesuai situasi.

---

## Opsi A — Dari laptop sendiri, otomatis sampai terunggah (disarankan)

Dipakai kalau tombol "Latih dari Data Asli" di dashboard timeout (504), atau memang lebih suka
melatih di laptop sendiri lalu mengunggah hasilnya ke server.

```bash
cd stroke-prediction-model
./scripts/deploy_model_from_local.sh
```

Skrip ini otomatis:
1. **Mengunduh data kalibrasi terbaru** dari server (`/v1/calibrate/export.csv`) — jadi selalu
   melatih dari data paling baru, bukan CSV lama yang mungkin masih tersimpan di laptop.
2. Melatih model secara lokal (13 model × 4 set fitur per parameter, ~10-30 detik untuk data
   sekarang).
3. Mengunggah artifact hasil latihan ke server lewat `scp` + `docker cp` langsung ke dalam
   container yang sedang berjalan (tidak perlu restart apa pun).

Kamu akan diminta memasukkan `root@host` VPS dan nama container (default `antaraga-api-1`), lalu
password SSH lewat prompt biasa (tidak disimpan di mana pun).

---

## Opsi B — Manual, langkah demi langkah (kalau Opsi A tidak bisa dipakai)

**1. Unduh data kalibrasi terbaru dari server** (WAJIB dilakukan dulu — jangan pakai CSV lama).

`/v1/calibrate/export.csv` dilindungi sesi dashboard (sama seperti `/dashboard`), jadi login dulu
untuk dapat cookie sesi, baru unduh CSV-nya:

```bash
curl -c /tmp/antaraga_cookie.txt \
  --data-urlencode "email=EMAIL_DASHBOARD" \
  --data-urlencode "password=PASSWORD_DASHBOARD" \
  --data-urlencode "next_path=/dashboard" \
  https://www.antaraga.web.id/login

curl -b /tmp/antaraga_cookie.txt \
  https://www.antaraga.web.id/v1/calibrate/export.csv -o /tmp/kalibrasi_terbaru.csv
```

**2. Latih model secara lokal dari CSV itu:**

```bash
cd stroke-prediction-model
python3 model/train_mlp_calibration.py --csv /tmp/kalibrasi_terbaru.csv
```

Ini akan menulis `model/artifacts/mlp_calibration.joblib` dan
`model/artifacts/mlp_calibration_metrics.json` di laptop, sekaligus mencetak tabel model
pemenang per parameter ke terminal.

**3. Unggah kedua berkas itu ke server:**

```bash
scp model/artifacts/mlp_calibration.joblib root@HOST_VPS:/tmp/
scp model/artifacts/mlp_calibration_metrics.json root@HOST_VPS:/tmp/
ssh root@HOST_VPS "docker cp /tmp/mlp_calibration.joblib antaraga-api-1:/app/model/artifacts/mlp_calibration.joblib && \
  docker cp /tmp/mlp_calibration_metrics.json antaraga-api-1:/app/model/artifacts/mlp_calibration_metrics.json && \
  rm -f /tmp/mlp_calibration.joblib /tmp/mlp_calibration_metrics.json"
```

Ganti `HOST_VPS` dengan alamat VPS, dan `antaraga-api-1` dengan nama container kalau berbeda
(cek dengan `docker ps` di server).

---

## Opsi C — Langsung di server lewat SSH (tanpa lewat laptop)

Kalau sedang login ke VPS dan datanya sudah ada di database server (tidak perlu CSV):

```bash
docker exec -it antaraga-api-1 python model/train_mlp_calibration.py --mode real
```

`--mode real` = hanya data sensor asli (bukan data demo). Ganti ke `--mode all` untuk memakai
semua data termasuk demo, atau `--mode demo` untuk hanya data demo.

**Catatan:** command ini dijalankan dengan `docker exec` langsung ke container yang sedang
berjalan (bukan `docker compose exec`, dan bukan dari dalam shell container) — cukup satu baris
dari host VPS, tidak perlu tahu lokasi `docker-compose.prod.yml`.

---

## Setelah selesai (berlaku untuk ketiga opsi)

Server mendeteksi artifact baru secara otomatis lewat perubahan waktu modifikasi berkas
(lihat `api/ml_calibration.py`) — **tidak perlu restart container atau server**. Model baru langsung
dipakai pada permintaan estimasi vital berikutnya, baik dari dashboard maupun aplikasi mobile.

Untuk memastikan, buka dashboard → tab Kalibrasi → "↺ Muat Laporan", cek kolom "Model" per
parameter sudah menunjukkan hasil terbaru.
