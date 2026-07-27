/**
 * ANTARAGA Smartband — KONFIGURASI
 * =====================================================================
 * SATU-SATUNYA file yang perlu kamu edit untuk operasional harian.
 * Isi bagian [WAJIB DIISI] sebelum flash.
 */
#pragma once

// =====================================================================
// [WAJIB DIISI]  WiFi
// =====================================================================
#define WIFI_SSID                 "GANTI_NAMA_WIFI"
#define WIFI_PASS                 "GANTI_PASSWORD_WIFI"
#define WIFI_CONNECT_TIMEOUT_MS   20000   // batas 1x percobaan connect
#define WIFI_RETRY_DELAY_MS       3000    // jeda antar percobaan

// =====================================================================
// [WAJIB DIISI]  Endpoint cloud (HTTPS)
// =====================================================================
#define DEVICE_ID                 "antaraga-001"
#define CLOUD_HOST                "api.ganti-cloudmu.com"
#define CLOUD_PORT                443
#define CLOUD_PATH                "/v1/ingest"

// Dikirim sebagai header  "Authorization: Bearer <key>".
// Kosongkan ("") kalau endpoint tidak butuh auth.
#define CLOUD_API_KEY             ""

// 1 = TLS tanpa verifikasi sertifikat (cepat, cocok untuk development).
// 0 = verifikasi pakai CLOUD_ROOT_CA di bawah (WAJIB untuk produksi).
#define CLOUD_INSECURE_TLS        1
#define CLOUD_ROOT_CA             nullptr   // tempel PEM root CA di sini bila INSECURE=0

#define HTTP_TIMEOUT_MS           8000

// =====================================================================
// Waktu (NTP) — supaya cloud punya timestamp absolut per batch
// =====================================================================
#define USE_NTP                   1
#define NTP_SERVER_1              "pool.ntp.org"
#define NTP_SERVER_2              "time.google.com"
#define NTP_WAIT_MS               6000

// =====================================================================
// Akuisisi — SEN0203 (PPG analog, A1/GPIO2)
// =====================================================================
#define PPG_FS_HZ                 200   // WAJIB pembagi bulat 1000 (200 -> 5 ms)

/* PPG_OVERSAMPLE: rata-rata N bacaan ADC per titik waktu (tekan noise acak
 * tanpa merusak morfologi gelombang).
 *
 * Recorder validasimu memakai 64x, TAPI di situ MCU tidak mengerjakan apa pun
 * selain ADC. Di firmware ini core yang sama juga menguras FIFO I2C MAX30102
 * dan menyusun batch, sementara core lain memutar TLS/WiFi. Anggaran waktu per
 * tick = 5000 us; satu adc_oneshot_read ~30-60 us, jadi 64x (~3 ms) terlalu
 * mepet. Default 16x = +2 bit resolusi efektif (12 -> 14 bit).
 *
 * Naikkan ke 32 atau 64 kalau mau, LALU cek baris "[STAT]" di serial:
 * selama ppg_overrun tetap 0, timing masih aman.                          */
#define PPG_OVERSAMPLE            16

// =====================================================================
// Akuisisi — MAX30102 (I2C, dibaca via FIFO)
// =====================================================================
// 1 = profil PWA  : 400 Hz (morfologi paling detail, throughput lebih berat)
// 0 = profil AMAN : 250 Hz (lebih ringan untuk WiFi lemah / kuota terbatas)
#define MAX_PROFILE_PWA           1

// Arus LED — nilai dari hasil optimasimu (target DC ~120-180k, batas 262143).
#define MAX_LED_RED               0x6F   // ~22 mA
#define MAX_LED_IR                0x5F   // ~19 mA

// =====================================================================
// Streaming
// =====================================================================
/* Jeda setelah sensor dinyalakan sebelum data mulai dikirim. Sampel selama
 * jendela ini DIBUANG, jadi noise transien power-on tidak ikut terkirim.
 *
 * CATATAN: recorder SEN0203-mu memakai warmup 8 detik karena baseline op-amp
 * SEN0203 (kopling DC) butuh waktu settle. 1000 ms sesuai permintaan, tapi
 * kalau batch-batch awal terlihat melayang/drift, naikkan nilai ini.        */
#define SENSOR_SETTLE_MS          1000

// Durasi data per 1x POST. Kecil = latensi rendah tapi overhead HTTP naik.
#define BATCH_MS                  500

// Jumlah buffer batch. (BATCH_POOL-1) x BATCH_MS = daya tahan saat WiFi ngadat
// sebelum data terpaksa dibuang. 6 x 500 ms = ~2,5 detik.
#define BATCH_POOL                6

// =====================================================================
// Baterai (Vsens di A0/GPIO1, pembagi R1=R2=100k -> Vbatt/2)
// =====================================================================
#define BATT_DIVIDER_GAIN         2.0f    // (R1+R2)/R2 = 200k/100k
#define BATT_CAL_TRIM             1.0f    // koreksi halus; ukur DMM lalu setel
#define BATT_OVERSAMPLE           16
#define BATT_PERIOD_MS            2000    // pembacaan tiap 2 s (di-EMA)
#define BATT_EMA_ALPHA            0.20f

// =====================================================================
// Debug
// =====================================================================
#define SERIAL_BAUD               115200
#define STAT_PERIOD_MS            5000    // baris "[STAT]" tiap 5 s
#define VERBOSE_HTTP              1       // cetak status code tiap POST
