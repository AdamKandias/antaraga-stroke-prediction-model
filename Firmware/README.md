# ANTARAGA Smartband — Firmware Streaming

XIAO ESP32-S3. Mengalirkan **data mentah** MAX30102 (RED+IR, 400 Hz) dan SON1303
(PPG analog, 200 Hz) ke cloud lewat HTTPS, plus persen baterai. Data dikemas per
**package 1000 ms** dan disaring gerbang SQI sebelum dikirim — package yang tidak
layak dibuang di perangkat, tidak pernah menyentuh jaringan.

Jendela 1 detik dipilih supaya memuat **satu siklus jantung utuh** pada ≥60 bpm.
Itu yang membuat perfusi jadi metrik mutu yang sahih; di 500 ms, package yang
jatuh di fase diastol bisa tidak memuat upstroke sama sekali.

Yang **dikirim** tetap 100% mentah: SQI hanya memutuskan kirim/buang, tidak
memfilter, menghaluskan, atau me-resample satu sampel pun. Semua analisis (PWA,
VPG, APG, BPM, SpO2) tetap dikerjakan di sisi cloud.

## Alur kerja

```
boot
 │
 ├─ CORE 0 (netTask) ── nyalakan WiFi → cari & sambung AP → sinkron NTP → set EV_WIFI_OK
 │                                                                             │
 ├─ CORE 1 (sensorTask) ── tunggu EV_WIFI_OK ────────────────────────────────┘
 │        └─ D2 = LOW  → P-MOSFET Q2 nyambung → SON1303 dapat 3V3
 │        └─ MAX30102 keluar dari shutdown, dibaca lewat FIFO
 │        └─ settle 1 detik (sampel DIBUANG, bukan dikirim)
 │        └─ isi package tiap 500 ms → qFilled
 │
 ├─ CORE 0 (netTask) ── ambil dari qFilled → SQI → layak? → JSON → POST HTTPS
 │                                             └─ tidak layak → BUANG        │
 │                                                    └── kembalikan ke qFree ┘
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
| `FW_VERSION` | **naikkan tiap kali membuat `.bin` untuk diunggah** — lihat bagian OTA |

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
  "sqi": 87,
  "sqi_flags": 0,
  "ir_dc": 138204,
  "ir_p2p": 4120,
  "ir_pi": 29,
  "ir_jump": 610,
  "ir_jump_n": 0,
  "ir_tort10": 34,
  "ppg_dc": 2042,
  "ppg_p2p": 180,
  "ppg_jump_n": 0,
  "ppg_tort10": 51,
  "clip_n": 0,
  "ppg": [2041, 2043, 2044, "... 200 nilai"],
  "red": [131072, 131155, "... ~400 nilai"],
  "ir":  [148390, 148402, "... ~400 nilai"]
}
```

| Field | Arti |
|---|---|
| `seq` | nomor package berurutan sejak streaming mulai. **Lompatan = package hilang ATAU ditolak SQI** |
| `t_ms` | `millis()` saat sampel PPG **pertama** package ini |
| `t_unix_ms` | epoch UTC ms saat sampel pertama; `0` bila NTP gagal |
| `ppg[]` | ADC mentah SON1303, 0–4095, hasil rata-rata `PPG_OVERSAMPLE` bacaan per titik |
| `red[]`, `ir[]` | ADC mentah MAX30102, 18-bit (0–262143). Nilai 262143 = saturasi |
| `ovf` | overflow FIFO MAX30102. **Lihat peringatan di bawah — tidak dapat dipercaya pada unit ini** |
| `batt_pct` | 0–100, interpolasi kurva Li-Po 3,3–4,2 V (bukan skala linear) |
| `sqi` | skor kelayakan 0–100. Package yang sampai ke cloud selalu ≥ `SQI_MIN_SCORE` |
| `sqi_flags` | bitmask alasan tolak. Pada package yang terkirim **selalu 0** — ada untuk audit |
| `ir_dc`, `ir_p2p` | rerata IR dan puncak-ke-puncak. `ir_dc` cuma penyebut normalisasi, bukan penilai mutu |
| `ir_pi` | perfusi `p2p/DC` dalam **per-mil**. 29 = 2,9% |
| `ir_jump` | lompatan TERBESAR antar dua sampel berurutan |
| `ir_jump_n` | cacah sampel yang melompat ≥ ambang lunak (35% p2p) |
| `ir_tort10` | tortuosity `Σ\|Δ\|/p2p` **×10**. 34 = 3,4 — makin kecil makin mulus |
| `ppg_*` | idem untuk kanal SON1303 |
| `clip_n` | cacah sampel yang mentok rel ADC (IR + RED + PPG) |

> **`ovf` tidak dapat dipercaya.** Pada unit yang diuji, register `OVF_COUNTER`
> (0x05) MAX30102 macet di `1`: terbaca 1 lewat burst maupun transaksi terpisah,
> dan menolak di-clear, padahal FIFO hanya terisi 1 dari 32 slot dan cacah sampel
> membuktikan tidak ada data hilang. Firmware menjumlahkan register itu tiap
> polling (200×/detik), jadi angkanya membengkak tanpa arti. Abaikan field ini di
> cloud; pakai `seq` untuk mendeteksi package hilang.

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
Selisih beberapa Hz itu normal (osilator MAX30102 punya toleransi beberapa persen).

Selisih **kelipatan bulat** — misalnya `fs_max_ukur` ≈ setengah atau seperempat
`fs_max` — artinya lain: kombinasi sample-rate × pulse-width di `CFG_SPO2` tidak
dilayani chip. Di mode SpO2 (2 LED) dengan PW 411 µs, `SPO2_SR` mentok di 400 Hz;
minta 800 atau 1000 Hz dan chip meng-clamp tanpa memberi error, lalu `SMP_AVE`
membagi hasilnya. Perbaikannya di `CFG_SPO2`/`CFG_FIFO` ([src/sensors.cpp](src/sensors.cpp)),
bukan di `MAX_PROFILE_PWA` — dan `MAX_FS_HZ` di
[include/antaraga.h](include/antaraga.h) wajib ikut disesuaikan, karena nilai
itulah yang dikirim sebagai `fs_max`.

Respons server: status **2xx** = sukses. Body dibaca lalu dibuang, jadi apa pun boleh,
tapi buat sependek mungkin (mis. `{"ok":true}`) supaya koneksi keep-alive cepat bebas.

## Gerbang SQI

Dijalankan di **core 0** ([src/sqi.cpp](src/sqi.cpp)) tepat sebelum serialisasi —
bukan di core sensor, yang anggaran 5 ms per tick-nya tidak boleh diganggu.
Hitungannya jalan-lurus atas ~500 sampel, puluhan mikrodetik.

Tiga aturan rancangannya:

1. **Satu package = satu keputusan.** Tidak ada state yang dibawa antar package,
   jadi package bagus tidak pernah tercemar tetangganya yang buruk.
2. **Skor = MINIMUM sub-skor, bukan rata-rata.** Rata-rata menyamarkan outlier:
   satu lompatan gerakan parah akan larut di antara 200 sampel lain dan package
   sampah tetap lolos. Minimum tidak bisa disamarkan.
3. **Statistiknya bertipe ekstrem** (min, max, lompatan terbesar). Satu-satunya
   rerata adalah `ir_dc`/`ppg_dc`, dan itu murni penyebut normalisasi — tidak
   pernah jadi penilai mutu.

### Tiga kelas cacat yang ditangkap

Ketiganya perlu, karena masing-masing buta terhadap yang lain:

| Kelas | Metrik | Menangkap |
|---|---|---|
| kontak & pencahayaan | `ir_dc`, `clip_n`, `ir_pi` | sensor lepas, bocor cahaya, saturasi, oklusi |
| artefak **terisolasi** | `ir_jump` + `ir_jump_n` (dua tingkat) | sentakan gerakan, glitch I2C |
| noise **tersebar** | `ir_tort10` (tortuosity) | tremor kontak, noise per-sampel, kedip lampu 100 Hz |

**Lompatan dua tingkat.** Tingkat **keras** (`SQI_IR_JUMP_HARD_PCT`, 60% p2p):
satu sampel saja melompat sejauh itu → tolak. Tingkat **lunak**
(`SQI_IR_JUMP_MAX_PCT`, 35% p2p): dicacah berapa banyak, ditolak kalau
melebihi `SQI_JUMP_SOFT_PERMIL` (1%) dari total sampel. Alasannya, satu glitch
I2C **bukan** artefak fisiologis — membuang 1 detik data bersih karenanya itu
mubazir. Gerakan sungguhan menghasilkan banyak lompatan, bukan satu.

**Tortuosity** = `Σ|x[i]−x[i−1]| / p2p`. PPG bersih menempuh ~2× p2p per denyut,
jadi di jendela 1 detik nilainya ~2–4. Noise membuat lintasannya meledak untuk
rentang yang sama. Ini **bukan** averaging: penjumlahan selisih absolut justru
makin peka terhadap noise, bukan menghaluskannya.

| Flag | Bit | Arti | Ambang di `config.h` |
|---|---|---|---|
| `nofinger` | 0 | DC IR terlalu rendah, sensor tidak menempel | `SQI_IR_DC_MIN` |
| `sat` | 1 | DC kelewat tinggi / sampel mentok rel | `SQI_IR_DC_MAX`, `SQI_CLIP_MAX_N` |
| `flat` | 2 | perfusi di bawah lantai — sensor macet / oklusi | `SQI_IR_PI_MIN_PERMIL` |
| `motion` | 3 | lompatan (keras/lunak), perfusi berlebih, atau tortuosity tinggi | `SQI_IR_JUMP_*`, `SQI_IR_PI_MAX_PERMIL`, `SQI_IR_TORT_MAX_X10` |
| `ppg` | 4 | kanal SON1303 di luar batas wajar | `SQI_PPG_*` |
| `short` | 5 | jumlah sampel kurang | — |

> **Kalau `BATCH_MS` diturunkan lagi ke 500**, `SQI_IR_PI_MIN_PERMIL` WAJIB
> dikembalikan ke ~1. Jendela 500 ms lebih pendek dari satu siklus jantung, jadi
> package yang jatuh di fase diastol bisa tidak memuat upstroke sama sekali —
> perfusinya kecil **padahal sinyalnya sehat**, dan gerbang akan membuang data
> bagus secara sistematis.

### Mengkalibrasi ambangnya

Semua angka di `config.h` adalah **titik awal hasil penalaran, bukan hasil ukur
dari sensormu**. Urutan yang benar:

1. Set `SQI_ENABLE 0` — semua package terkirim apa adanya, gerbang mati.
2. Rekam beberapa menit: sensor menempel diam, menempel sambil bergerak, dan
   lepas sama sekali.
3. Di cloud, plot sebaran `ir_dc`, `ir_pi`, `ir_jump_n`, dan `ir_tort10` untuk
   ketiga kondisi itu. Batas antar-kelompoknya akan terlihat sendiri.
4. Patok ambangnya di sana, lalu `SQI_ENABLE 1`.

`VERBOSE_SQI 1` mencetak alasan tiap package yang dibuang ke serial — berguna
untuk melihat flag mana yang paling sering memicu tolak.

**Konsekuensi operasional:** selama sensor tidak menempel, perangkat tidak
mengirim apa pun. Bagi cloud itu tidak bisa dibedakan dari perangkat mati.
Kalau perlu membedakannya, sediakan heartbeat terpisah — gerbang ini sengaja
tidak mengirim apa-apa saat menolak.

## OTA — ganti firmware dari dashboard, tanpa buka casing

Model **pull**: perangkat yang bertanya ke server, bukan server yang mendorong.
Konsekuensinya perangkat bisa berada di jaringan mana pun — tidak perlu satu LAN,
tidak perlu port terbuka, tidak perlu tahu IP-nya.

Partisi sudah siap sejak awal: `default_8MB.csv` punya `app0` dan `app1`
masing-masing 3,34 MB plus `otadata`. Firmware ini ~1,07 MB, jadi muat di
sepertiga slot. Update ditulis ke slot yang **tidak** sedang berjalan, lalu boot
dialihkan ke sana — firmware lama tetap utuh sebagai cadangan.

### Kontrak server

```
GET  /v1/ota/check?device_id=<id>&fw=<versi_sekarang>
     → {"pending":true,"fw":"1.1.0"}     ada firmware baru
     → {"pending":false}                 tidak ada

GET  /v1/ota/firmware?device_id=<id>
     → body = isi .bin mentah
     → Content-Length WAJIB benar

POST /v1/ota/ack?device_id=<id>&fw=<versi_terpasang>
     → dipanggil setelah flash berhasil, supaya dashboard menandai selesai
```

Semua endpoint menerima `Authorization: Bearer <CLOUD_API_KEY>` yang sama dengan
ingest. Path-nya bisa diubah di `config.h` (`OTA_PATH_*`).

### Alur di dashboard

1. Build `.bin` baru — **naikkan `FW_VERSION` di [config.h](include/config.h)**.
2. Unggah `.pio/build/seeed_xiao_esp32s3/firmware.bin` ke dashboard.
3. Tandai perangkat sasaran sebagai *pending* dengan versi barunya.
4. Perangkat menemukannya dalam ≤ `OTA_CHECK_INTERVAL_MS` (default 60 detik),
   mengunduh, mem-flash, lalu restart sendiri.

### Dua pengaman yang wajib kamu pahami

**Perbandingan versi memutus loop reflash.** Kalau ACK tidak sampai ke server
(jaringan putus sedetik), server masih menganggap ada update pending. Tanpa
perbandingan versi, perangkat akan mengunduh dan mem-flash biner yang **sama**
berulang kali tiap 60 detik dan tidak pernah sempat bekerja. Karena itu
`FW_VERSION` **harus** dinaikkan tiap build — kalau lupa, perangkat akan
melewatkan update dan hanya mengirim ulang ACK.

**Status percobaan.** Firmware hasil OTA belum dianggap sah sampai berhasil
`OTA_TRIAL_POSTS` kali POST. Kalau sampai `OTA_TRIAL_TIMEOUT_MS` belum tercapai,
perangkat mengalihkan boot kembali ke partisi yang **terbukti** pernah jalan lalu
restart. Slot yang belum pernah terbukti tidak akan pernah dijadikan sasaran
revert — kalau tidak, revert pada OTA pertama justru melompat ke slot kosong.

> **Batas pengaman ini.** Rollback otomatis di level bootloader ESP-IDF **tidak
> aktif** di build Arduino/pioarduino standar. Pemulihan di atas berjalan di
> level aplikasi, jadi ia tidak menolong kalau firmware baru crash atau boot-loop
> **sebelum** sempat menilai dirinya. Selalu uji `.bin` lewat kabel sekali
> sebelum diunggah ke dashboard.

### Selama unduhan, data hilang

`netTask` tidak menguras `qFilled` selama mengunduh (belasan detik). `sensorTask`
tetap mencuplik, pool penuh, dan batch selama jendela itu dibuang — terlihat
sebagai lonjakan `drop` di `[STAT]`. Ini disengaja: kehilangan beberapa detik
sekali jauh lebih murah daripada menghentikan akuisisi atau menunda update.

### Keamanan — baca sebelum dipakai di lapangan

`CLOUD_INSECURE_TLS 1` berarti sertifikat server **tidak diverifikasi**.
Menambahkan OTA di atas kanal itu berarti siapa pun yang bisa menyisip di
koneksi dapat memasang firmware apa pun ke alat yang menempel di tubuh orang.

Sebelum dipakai di luar meja kerja, minimal salah satu: set
`CLOUD_INSECURE_TLS 0` dan isi `CLOUD_ROOT_CA`, atau verifikasi tanda tangan
biner sebelum dipasang. Firmware mencetak peringatan ini di serial saat boot
selama OTA aktif dengan TLS tanpa verifikasi.

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
[STAT] STREAM   up=125s | batch made=124 sent=115 drop=0 httpfail=0 code=200 post=286ms
       ppg=24800 max=49612 (fs_max_ukur=400.1 Hz) | ovf=0 overrun=0 trunc=0
       sqi lolos=115 tolak=9 (92%) | skor terakhir=87 alasan=-
       batt=3912 mV (72%) | rssi=-58 dBm | heap=182340
```

| Kolom | Sehat bila | Kalau tidak |
|---|---|---|
| `drop` | 0 | cloud/WiFi tidak mengejar → naikkan `BATCH_POOL` atau `BATCH_MS` |
| `httpfail` | 0 | cek endpoint, sertifikat, token |
| `post` | < `BATCH_MS` | lihat catatan keep-alive di bawah |
| `ovf` | — | **abaikan**, register chip tidak dapat dipercaya (lihat kontrak payload) |
| `overrun` | 0 | task sensor telat dari jadwal 5 ms → turunkan `PPG_OVERSAMPLE` |
| `trunc` | 0 | `MAX_CAP` kurang (nyaris mustahil, headroom sudah 25%) |
| `fs_max_ukur` | ≈ `fs_max` | lihat bagian rekonstruksi sumbu waktu di atas |
| `sqi lolos` | tinggi saat sensor menempel | `alasan=` menunjukkan flag yang paling sering memicu tolak |

Catatan: `sent` sekarang menghitung package yang **lolos SQI dan berhasil di-POST**,
jadi `made > sent` itu wajar — selisihnya package yang sengaja dibuang.

### Endpoint WAJIB mendukung HTTP keep-alive

Firmware mempertahankan satu sesi TLS untuk semua package. Kalau server membalas
`Connection: close`, setiap POST harus handshake TLS ulang (±300–800 ms). Di
`BATCH_MS = 1000` itu masih terkejar, tapi menyisakan sedikit sekali margin —
payload 400 Hz berukuran ~8–9 KB per package.

Ciri-cirinya di `[STAT]`: `post` besar dan `drop` bertambah terus. Solusinya urut:
nyalakan keep-alive di server → naikkan `BATCH_POOL` → naikkan `BATCH_MS`.

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
| D1 / A1 | 2 | `SIG_PPG` — keluaran analog SON1303 |
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
| [src/sqi.cpp](src/sqi.cpp) | pre-processing & gerbang kelayakan per package (core 0) |
| [src/cloud.cpp](src/cloud.cpp) | WiFi, NTP, penulis JSON, POST HTTPS, `netTask` (core 0) |
