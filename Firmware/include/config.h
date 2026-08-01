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
#define WIFI_SSID                 "miaw"
#define WIFI_PASS                 "keputihtegaltimur1"
#define WIFI_CONNECT_TIMEOUT_MS   20000   // batas 1x percobaan connect
#define WIFI_RETRY_DELAY_MS       3000    // jeda antar percobaan

// =====================================================================
// [WAJIB DIISI]  Endpoint cloud (HTTPS)
// =====================================================================
#define DEVICE_ID                 "antaraga-001"
#define CLOUD_HOST                "api.antaraga.web.id"
#define CLOUD_PORT                443
#define CLOUD_PATH                "/v1/ingest"

// Dikirim sebagai header  "Authorization: Bearer <key>".
// Kosongkan ("") kalau endpoint tidak butuh auth.
#define CLOUD_API_KEY             "antaraga-hw-2026-01"

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
// Akuisisi — SON1303 (PPG analog, A1/GPIO2)
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
// 1 = profil PWA  : 400 Hz (morfologi paling detail, throughput 2x lebih berat)
// 0 = profil AMAN : 200 Hz (lebih ringan untuk WiFi lemah / kuota terbatas)
//
// Keduanya menjalankan chip di SR=400 Hz — batas mode SpO2 pada pulse width
// 411 us. Bedanya cuma averaging hardware (SMP_AVE 1 vs 2). Jangan menaikkan
// SR di CFG_SPO2 melewati 400: chip meng-clamp diam-diam dan laju keluaran
// nyata malah turun.
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
 * CATATAN: recorder SON1303-mu memakai warmup 8 detik karena baseline op-amp
 * SON1303 (kopling DC) butuh waktu settle. 1000 ms sesuai permintaan, tapi
 * kalau batch-batch awal terlihat melayang/drift, naikkan nilai ini.        */
#define SENSOR_SETTLE_MS          1000

/* Durasi data per package (= per 1x POST).
 *
 * 1000 ms dipilih supaya jendela memuat SATU siklus jantung utuh pada >=60 bpm.
 * Itu yang membuat perfusi (p2p/DC) jadi metrik mutu yang sahih — di 500 ms,
 * package yang jatuh di fase diastol bisa tidak memuat upstroke sama sekali,
 * sehingga perfusi hanya bisa dipakai sebagai lantai anti-flatline.
 *
 * Bonusnya: overhead TLS/HTTP per byte turun dan anggaran waktu per POST
 * berlipat dua. Ongkosnya: latensi 1 detik, dan satu artefak membuang 1 detik.
 *
 * Kalau turun lagi ke 500, WAJIB turunkan SQI_IR_PI_MIN_PERMIL kembali ke ~1,
 * kalau tidak gerbang perfusi akan membuang data sehat secara sistematis. */
#define BATCH_MS                  1000

// Jumlah buffer package. (BATCH_POOL-1) x BATCH_MS = daya tahan saat WiFi
// ngadat sebelum data terpaksa dibuang. 6 x 1000 ms = ~5 detik.
#define BATCH_POOL                6

// =====================================================================
// SQI — gerbang kelayakan per package (dihitung di core 0, src/sqi.cpp)
// =====================================================================
/* Satu package = satu keputusan: layak -> POST, tidak layak -> DIBUANG.
 * Tidak ada nilai yang dirata-rata antar package, dan skor akhir diambil dari
 * MINIMUM sub-skor. Rata-rata justru menyamarkan outlier — satu lompatan
 * gerakan akan tenggelam dan package sampah tetap lolos.
 *
 * 0 = semua package dikirim apa adanya (berguna saat kalibrasi ambang). */
#define SQI_ENABLE                0

// --- MAX30102 kanal IR (ADC 18-bit, 0..262143) -----------------------
#define SQI_SAT_LEVEL             262100  // ambang "mentok rel"
#define SQI_CLIP_MAX_N            2       // toleransi sampel mentok per package

// Jendela DC. [DC_MIN..DC_MAX] = batas tolak. [DC_GOOD_LO..DC_GOOD_HI] = skor
// penuh; di antaranya skor meluruh linear. Nilai GOOD mengacu target DC
// 120-180k dari hasil optimasi arus LED-mu.
#define SQI_IR_DC_MIN             30000
#define SQI_IR_DC_GOOD_LO         80000
#define SQI_IR_DC_GOOD_HI         220000
#define SQI_IR_DC_MAX             255000

/* Perfusi (p2p / DC) dalam per-mil. Di BATCH_MS 1000 ini gerbang mutu SUNGGUHAN,
 * bukan lagi sekadar lantai anti-flatline, karena jendelanya memuat denyut utuh.
 *
 * Nilai khas: jari ~5-30 per-mil (0,5-3%), pergelangan jauh lebih rendah.
 * MIN sengaja dipatok konservatif — kalau kelewat tinggi, gerbang membuang data
 * sehat dan kamu tidak punya apa pun untuk dikalibrasi. Naikkan SETELAH melihat
 * sebaran ir_p2p/ir_dc yang nyata dari sensormu (pakai SQI_ENABLE 0). */
#define SQI_IR_PI_MIN_PERMIL      2       // 0,2%
#define SQI_IR_PI_GOOD_LO         5       // 0,5%
#define SQI_IR_PI_GOOD_HI         60      // 6%
#define SQI_IR_PI_MAX_PERMIL      200     // 20% — di atas ini hampir pasti gerakan

/* Outlier DUA TINGKAT, sebagai % dari p2p package.
 *   HARD  : ada SATU sampel melompat sejauh ini -> tolak, tanpa ampun.
 *   SOFT  : dihitung berapa BANYAK sampel yang melompat sejauh ini; ditolak
 *           kalau cacahnya melebihi SQI_JUMP_SOFT_PERMIL dari total sampel.
 *
 * Alasan dua tingkat: satu glitch I2C / bacaan ADC nyasar BUKAN artefak
 * fisiologis, dan membuang 1 detik data bersih karenanya itu mubazir. Gerakan
 * sungguhan menghasilkan banyak lompatan, bukan satu. */
#define SQI_IR_JUMP_HARD_PCT      60
#define SQI_IR_JUMP_MAX_PCT       35
#define SQI_JUMP_SOFT_PERMIL      10      // 1% dari sampel

/* Tortuosity = panjang lintasan / p2p, disimpan x10 (jadi 35 = 3,5).
 *
 * Menangkap kelas noise yang TIDAK terlihat oleh max-jump: noise tersebar
 * beramplitudo sedang — tremor kontak, dan noise per-sampel MAX30102 yang naik
 * ~sqrt(2) sejak SMP_AVE=1. Juga kedip optik 100 Hz dari lampu ruangan, yang
 * tetap masuk lewat fotodioda meski perangkat bertenaga baterai.
 *
 * PPG bersih menempuh ~2x p2p per denyut, jadi di jendela 1 detik (1-1,7 denyut)
 * nilainya ~20-40. Noise membuatnya meledak. Ini BUKAN averaging: penjumlahan
 * selisih absolut justru makin peka terhadap noise, bukan menghaluskannya. */
#define SQI_IR_TORT_GOOD_X10      60      // 6,0 — di bawah ini skor penuh
#define SQI_IR_TORT_MAX_X10       150     // 15,0 — di atas ini tolak

// --- SON1303 (ADC 12-bit, 0..4095) -----------------------------------
#define SQI_PPG_SAT_LEVEL         4090
#define SQI_PPG_P2P_MIN           15      // di bawah ini praktis garis datar
#define SQI_PPG_P2P_MAX           3500    // hampir selebar rel = terpotong/gerakan
#define SQI_PPG_JUMP_HARD_PCT     70
#define SQI_PPG_JUMP_MAX_PCT      45
#define SQI_PPG_TORT_GOOD_X10     80
#define SQI_PPG_TORT_MAX_X10      200

// Skor minimum supaya package dikirim (0..100).
#define SQI_MIN_SCORE             60

// =====================================================================
// Baterai (Vsens di A0/GPIO1, pembagi R1=R2=100k -> Vbatt/2)
// =====================================================================
#define BATT_DIVIDER_GAIN         2.0f    // (R1+R2)/R2 = 200k/100k
#define BATT_CAL_TRIM             1.0f    // koreksi halus; ukur DMM lalu setel
#define BATT_OVERSAMPLE           16
#define BATT_PERIOD_MS            2000    // pembacaan tiap 2 s (di-EMA)
#define BATT_EMA_ALPHA            0.20f

// =====================================================================
// OTA — ganti firmware lewat WiFi, .bin didorong dari dashboard
// =====================================================================
/* Model PULL: perangkat yang bertanya ke server, bukan server yang mendorong.
 * Konsekuensinya perangkat bisa berada di jaringan mana pun — tidak perlu satu
 * LAN, tidak perlu port terbuka, tidak perlu tahu IP-nya.
 *
 * Partisi sudah siap: default_8MB.csv punya app0 dan app1 masing-masing 3,34 MB
 * plus otadata. Firmware ini ~1,05 MB, jadi muat di sepertiga slot. Update
 * ditulis ke slot yang TIDAK sedang berjalan, lalu boot dialihkan ke sana —
 * firmware lama tetap utuh sebagai cadangan.
 *
 * KONTRAK SERVER (tiga endpoint):
 *
 *   GET  {OTA_PATH_CHECK}?device_id=<id>&fw=<versi>
 *        -> {"pending":true,"fw":"1.1.0"}      ada firmware baru
 *        -> {"pending":false}                  tidak ada
 *
 *   GET  {OTA_PATH_FIRMWARE}?device_id=<id>
 *        -> body = isi .bin mentah, Content-Length WAJIB benar
 *
 *   POST {OTA_PATH_ACK}?device_id=<id>&fw=<versi>
 *        -> dipanggil setelah flash berhasil, supaya dashboard menandai selesai
 */
#define OTA_ENABLE                1
#define OTA_CHECK_INTERVAL_MS     60000   // jeda antar pengecekan (0 = mati)
#define OTA_PATH_CHECK            "/v1/ota/check"
#define OTA_PATH_FIRMWARE         "/v1/ota/firmware"
#define OTA_PATH_ACK              "/v1/ota/ack"
#define OTA_DOWNLOAD_TIMEOUT_MS   60000   // unduh ~1 MB lewat WiFi

/* Versi yang tertanam di biner. WAJIB dinaikkan tiap kali kamu membuat .bin
 * baru untuk diunggah ke dashboard.
 *
 * Ini yang mencegah loop reflash: kalau ACK ke server gagal (jaringan putus
 * sedetik), server masih menganggap ada update pending. Tanpa perbandingan
 * versi, perangkat akan mengunduh dan mem-flash biner yang SAMA berulang kali
 * setiap OTA_CHECK_INTERVAL_MS dan tidak pernah sempat bekerja. Dengan versi,
 * perangkat mengenali "ini sudah saya pakai", melewatkannya, dan mengirim ulang
 * ACK-nya — jadi kegagalan ACK sembuh sendiri. */
#define FW_VERSION                "1.0.0"

/* Pengaman anti-brick. Firmware yang baru dipasang berstatus PERCOBAAN sampai
 * berhasil POST sebanyak ini. Kalau sampai OTA_TRIAL_TIMEOUT_MS belum tercapai,
 * perangkat mengalihkan boot kembali ke partisi lama lalu restart.
 *
 * CATATAN JUJUR: rollback otomatis di level bootloader ESP-IDF TIDAK aktif di
 * build Arduino/pioarduino standar. Pemulihan ini berjalan di level aplikasi,
 * jadi ia TIDAK menolong kalau firmware baru crash/boot-loop sebelum sempat
 * menilai dirinya sendiri. Tetap uji .bin lewat kabel sekali sebelum diunggah. */
#define OTA_TRIAL_POSTS           3
#define OTA_TRIAL_TIMEOUT_MS      120000

// =====================================================================
// LED indikator (D10)
// =====================================================================
/* Saat STREAMING, LED "bernapas" — meredup dan menyala perlahan, bukan kedip.
 * Ini butuh PWM (LEDC), bukan digitalWrite.
 *
 * Resolusi 12 bit dipilih bukan tanpa alasan: kurva napas memakai koreksi gamma,
 * dan di 8 bit ujung gelapnya terkuantisasi kasar — duty 1, 2, 3 sudah terasa
 * seperti lompatan besar, sehingga napasnya tersendat saat mendekati padam.
 * 12 bit membuat naik-turun dari gelap terasa mulus.
 *
 * 4 kHz jauh di atas ambang kedip yang terlihat mata, dan aman untuk resolusi
 * 12 bit (batas LEDC di clock 80 MHz adalah 80e6/4096 ~ 19,5 kHz). */
#define LED_PWM_FREQ_HZ           4000
#define LED_PWM_BITS              12
#define LED_DUTY_MAX              ((1 << LED_PWM_BITS) - 1)

// Durasi satu tarikan napas penuh (terang -> redup -> terang).
// 3000 ms ~ 20 napas/menit, kira-kira laju napas orang beristirahat.
#define LED_BREATH_PERIOD_MS      3000

/* Gamma untuk koreksi persepsi. Mata menangkap kecerahan secara logaritmik,
 * jadi duty yang naik linear justru terlihat melonjak cepat di awal lalu
 * mendatar — sama sekali tidak seperti napas. Nilai 2 (duty = level^2) cukup
 * dekat dengan persepsi dan hanya butuh satu perkalian. Naikkan ke 3 kalau mau
 * jeda gelapnya lebih lama. */
#define LED_BREATH_GAMMA          2

// =====================================================================
// Debug
// =====================================================================
#define SERIAL_BAUD               115200
#define STAT_PERIOD_MS            5000    // baris "[STAT]" tiap 5 s
#define VERBOSE_HTTP              1       // cetak status code tiap POST
#define VERBOSE_SQI               1       // cetak alasan tiap package yang dibuang
