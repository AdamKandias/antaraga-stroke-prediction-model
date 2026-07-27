# ANTARAGA Smartband — Firmware Streaming

XIAO ESP32-S3. Mengalirkan **data mentah** MAX30102 (RED+IR) dan SEN0203 (PPG analog)
ke cloud lewat HTTPS, plus persen baterai. Tidak ada pemrosesan sinyal di firmware —
semua analisis (PWA, VPG, APG, BPM, SpO2) dikerjakan di sisi cloud.

---

## ⚡ Koneksi ke Backend ANTARAGA (Baca ini dulu)

### Langkah 1 — Jalankan backend

```bash
cd stroke-prediction-model
./scripts/dev.sh
```

Output akan menampilkan URL ngrok, contoh:
```
URL ngrok : https://eafc-103-24-56-36.ngrok-free.app
```

### Langkah 2 — Isi `include/config.h`

```cpp
#define WIFI_SSID          "nama_wifi_kamu"
#define WIFI_PASS          "password_wifi"

#define DEVICE_ID          "antaraga-001"
// Host TANPA https:// dan TANPA trailing slash
#define CLOUD_HOST         "eafc-103-24-56-36.ngrok-free.app"
#define CLOUD_PORT         443
#define CLOUD_PATH         "/v1/ingest"

// Kosongkan kalau backend DEV_MODE=true (default dev)
#define CLOUD_API_KEY      ""
#define CLOUD_INSECURE_TLS 1   // wajib 1 untuk ngrok
```

> URL ngrok berubah setiap restart `dev.sh`. Perbarui `CLOUD_HOST`
> dan flash ulang setiap kali URL berubah.

### Langkah 3 — Flash & monitor

```bash
cd Firmware
pio run --target upload && pio device monitor
```

LED denyut 1x/detik = streaming aktif. Data langsung masuk ke
dashboard Flutter dan bisa dipantau di:
```
http://localhost:8000/docs        → dokumentasi API
http://localhost:8000/serial/ports → port serial yang tersambung
```

Monitor serial tanpa Arduino IDE — buka browser dan gunakan
endpoint WebSocket `/serial/ws` (lihat bagian **Serial Monitor**).

### Alur data lengkap

```
Smartband  →  HTTPS POST /v1/ingest (tiap 500ms)
           →  Backend ekstrak fitur PWA
           →  Prediksi vital (MLP) + risiko stroke (XGBoost)
           →  Simpan ke database
           →  Flutter polling /vitals/latest tiap 5 detik
           →  Push notification FCM kalau risiko HIGH
```

---

## Alur kerja

```
boot
 │
 ├─ CORE 0 (netTask) ── nyalakan WiFi → cari & sambung AP → sinkron NTP → set EV_WIFI_OK
 │                                                                             │
 ├─ CORE 1 (sensorTask) ── tunggu EV_WIFI_OK ────────────────────────────────┘
 │        └─ D2 = LOW  → P-MOSFET Q2 nyambung → SEN0203 dapat 3V3
 │        └─ MAX30102 keluar dari shutdown, dibaca lewat FIFO
 │        └─ settle 1 detik (sampel DIBUANG, bukan dikirim)
 │        └─ isi Batch tiap 500 ms → qFilled
 │
 ├─ CORE 0 (netTask) ── ambil dari qFilled → JSON → POST HTTPS → kembalikan ke qFree
 │
 └─ CORE 1 (loop)   ── kedipkan LED D10 + cetak [STAT] tiap 5 detik
```

Baterai dibaca di task yang sama dengan PPG (tiap 2 detik, A0) supaya handle ADC1
hanya punya satu pemilik. Hasilnya ikut di setiap batch.

## Yang harus diisi sebelum flash

Semua di [include/config.h](include/config.h):

| Konstanta | Isi dengan |
|---|---|
| `WIFI_SSID`, `WIFI_PASS` | kredensial AP |
| `CLOUD_HOST`, `CLOUD_PORT`, `CLOUD_PATH` | endpoint HTTPS penerima |
| `CLOUD_API_KEY` | token (dikirim `Authorization: Bearer <key>`), kosongkan bila tak perlu |
| `DEVICE_ID` | id unik perangkat |
| `CLOUD_INSECURE_TLS` | `1` saat development; **`0` + isi `CLOUD_ROOT_CA` untuk produksi** |

## Kontrak payload

`POST {CLOUD_PATH}` · `Content-Type: application/json` · satu request per `BATCH_MS` (default 500 ms).

```json
{
  "id": "antaraga-001",
  "seq": 42,
  "t_ms": 128450,
  "t_unix_ms": 1753600000123,
  "fs_ppg": 200,
  "fs_max": 400,
  "batt_mv": 3912,
  "batt_pct": 72,
  "ovf": 0,
  "ppg": [2041, 2043, 2044, "... 100 nilai"],
  "red": [131072, 131155, "... ~200 nilai"],
  "ir":  [148390, 148402, "... ~200 nilai"]
}
```

| Field | Arti |
|---|---|
| `seq` | nomor batch berurutan sejak streaming mulai. Lompatan = batch hilang (WiFi ngadat) |
| `t_ms` | `millis()` saat sampel PPG **pertama** batch ini |
| `t_unix_ms` | epoch UTC ms saat sampel pertama; `0` bila NTP gagal |
| `ppg[]` | ADC mentah SEN0203, 0–4095, hasil rata-rata `PPG_OVERSAMPLE` bacaan per titik |
| `red[]`, `ir[]` | ADC mentah MAX30102, 18-bit (0–262143). Nilai 262143 = saturasi |
| `ovf` | overflow FIFO MAX30102 pada batch ini. Bukan 0 = ada sampel hilang |
| `batt_pct` | 0–100, hasil interpolasi kurva Li-Po (bukan skala linear) |

### Merekonstruksi sumbu waktu

`ppg[i]` jatuh di `t_ms + i * 1000 / fs_ppg` — akurat, karena dicuplik oleh tick
FreeRTOS ESP32.

Untuk `red[]`/`ir[]`, **jangan langsung pakai `fs_max`**. MAX30102 punya osilator
internal sendiri yang tidak sinkron dengan ESP32, jadi jumlah sampel per batch
sedikit bervariasi. Turunkan laju sebenarnya dari cacahan:

```
fs_max_nyata = len(red) / (len(ppg) / fs_ppg)
```

Firmware juga mencetak angka ini tiap 5 detik sebagai `fs_max_ukur` di baris `[STAT]`.
Kalau jauh dari `fs_max`, artinya chip tidak melayani kombinasi sample-rate ×
pulse-width yang dipilih — turunkan `MAX_PROFILE_PWA` ke `0`.

Respons server: status **2xx** = sukses. Body dibaca lalu dibuang, jadi apa pun boleh,
tapi buat sependek mungkin (mis. `{"ok":true}`) supaya koneksi keep-alive cepat bebas.

## Arti kedip LED (D10)

| Pola | Arti |
|---|---|
| kedip cepat, 100 ms | mencari / menyambung WiFi |
| kedip sedang, 250 ms | sensor menyala, sedang settle 1 detik |
| **denyut pendek 1×/detik** | **STREAMING normal** |
| kedip ganda lalu jeda | sensor jalan, jaringan putus — data dibuffer |
| nyala panjang 800 ms | sensor gagal init, cek serial monitor |

## Membaca baris [STAT]

```
[STAT] STREAM   up=125s | batch made=248 sent=248 drop=0 httpfail=0 code=200 post=143ms
       ppg=24800 max=49612 (fs_max_ukur=400.1 Hz) | ovf=0 overrun=0 trunc=0
       batt=3912 mV (72%) | rssi=-58 dBm | heap=182340
```

| Kolom | Sehat bila | Kalau tidak |
|---|---|---|
| `drop` | 0 | cloud/WiFi tidak mengejar → naikkan `BATCH_POOL` atau `BATCH_MS` |
| `httpfail` | 0 | cek endpoint, sertifikat, token |
| `post` | < `BATCH_MS` | lihat catatan keep-alive di bawah |
| `ovf` | 0 | FIFO MAX30102 kebablasan → `PPG_OVERSAMPLE` terlalu besar |
| `overrun` | 0 | task sensor telat dari jadwal 5 ms → turunkan `PPG_OVERSAMPLE` |
| `trunc` | 0 | `MAX_CAP` kurang (nyaris mustahil, headroom sudah 25%) |
| `fs_max_ukur` | ≈ `fs_max` | lihat bagian rekonstruksi sumbu waktu di atas |

### Endpoint WAJIB mendukung HTTP keep-alive

Firmware mempertahankan satu sesi TLS untuk semua batch. Kalau server membalas
`Connection: close`, setiap POST harus handshake TLS ulang (±300–800 ms), dan di
`BATCH_MS = 500` itu tidak akan terkejar — `post` akan mendekati/melebihi 500 ms
lalu `drop` mulai naik.

Ciri-cirinya di `[STAT]`: `post` besar dan `drop` bertambah terus. Solusinya urut:
nyalakan keep-alive di server → naikkan `BATCH_MS` ke 1000 → naikkan `BATCH_POOL`.

## Kalibrasi baterai

`Vsens = Vbatt / 2` lewat pembagi R1/R2 100 kΩ. Ukur `Vbatt` dengan multimeter,
bandingkan dengan `batt=... mV` di `[STAT]`, lalu setel `BATT_CAL_TRIM` di
`config.h`:

```
BATT_CAL_TRIM = Vbatt_multimeter / Vbatt_terbaca
```

Impedansi pembagi 50 kΩ tergolong tinggi untuk ADC ESP32; C8 100 nF yang menahan
muatan saat sampling. Kalau bacaan konsisten rendah, trim di atas yang mengoreksi.

## Peta pin

| XIAO | GPIO | Fungsi |
|---|---|---|
| D0 / A0 | 1 | `Vsens` — pembagi tegangan baterai |
| D1 / A1 | 2 | `SIG_PPG` — keluaran analog SEN0203 |
| D2 | 3 | enable P-MOSFET Q2 (DMP2130L) — **LOW = sensor ON** |
| D4 | 5 | I2C SDA → MAX30102 |
| D5 | 6 | I2C SCL → MAX30102 |
| D10 | 9 | LED via R6 10 kΩ — HIGH = nyala |

## Build

`platformio.ini` memakai fork **pioarduino** karena firmware ini butuh Arduino
core 3.x (ESP-IDF 5.x) untuk `esp_adc/adc_oneshot.h`. Platform resmi PlatformIO
masih terkunci di core 2.0.17.

`src/sensors.cpp` tetap punya jalur cadangan untuk core 2.x, jadi bila fork tidak
bisa diunduh, ganti saja `platform = espressif32` — hanya kalibrasi ADC-nya yang
memakai skema lama.

## Struktur

| File | Isi |
|---|---|
| [include/config.h](include/config.h) | **satu-satunya file yang perlu diedit** |
| [include/antaraga.h](include/antaraga.h) | peta pin, struct `Batch`, kontrak antar-modul |
| [src/main.cpp](src/main.cpp) | setup, pembuatan task, LED, `[STAT]` |
| [src/sensors.cpp](src/sensors.cpp) | driver MAX30102, lapisan ADC, `sensorTask` (core 1) |
| [src/cloud.cpp](src/cloud.cpp) | WiFi, NTP, penulis JSON, POST HTTPS, `netTask` (core 0) |
