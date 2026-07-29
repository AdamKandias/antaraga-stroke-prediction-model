/**
 * ANTARAGA BPM — KONFIGURASI
 * =====================================================================
 * Program ini menghitung BPM DI PERANGKAT dari SON1303 saja. MAX30102,
 * WiFi, dan cloud tidak dipakai.
 *
 * Bagian [AKUISISI] SENGAJA identik dengan ../Firmware/include/config.h.
 * Itu inti programnya: BPM di sini dihitung dari deretan angka yang PERSIS
 * sama dengan yang dikirim firmware streaming ke cloud (pin, laju sampel,
 * kedalaman oversample, atenuasi & lebar ADC). Jadi kalau angka di sini
 * meleset dari hasil analisis cloud, penyebabnya algoritma — bukan beda
 * cara mencuplik.
 *
 * Kalau kamu mengubah PPG_FS_HZ / PPG_OVERSAMPLE di ../Firmware, ubah juga
 * di sini. Koefisien filter dihitung ulang otomatis dari PPG_FS_HZ, jadi
 * band-pass-nya tidak akan bergeser diam-diam (lihat src/bpm.cpp).
 */
#pragma once

// =====================================================================
// Pin — XIAO ESP32-S3 (nama silkscreen -> GPIO), sesuai skematik ANTARAGA
// =====================================================================
#define PIN_SIG_PPG        2    // D1 / A1  <- keluaran analog SON1303 (J2)
#define PIN_SEN_EN         3    // D2       -> gate Q2 (DMP2130L, P-MOS): LOW = sensor ON
#define PIN_LED            9    // D10      -> LED via R6 10k (HIGH = nyala)

#define SEN_POWER_ON       LOW  // Q2 P-channel: gate ditarik LOW -> tersambung
#define SEN_POWER_OFF      HIGH // R5 100k pull-up ke 3V3 -> default mati saat boot

// =====================================================================
// [AKUISISI] SON1303 — sama persis dengan varian streaming
// =====================================================================
#define PPG_FS_HZ          200  // WAJIB pembagi bulat 1000 (200 -> 5 ms)
#define PPG_PERIOD_MS      (1000 / PPG_FS_HZ)

/* Rata-rata N bacaan ADC per titik waktu. 16x = +2 bit resolusi efektif
 * (12 -> 14 bit) tanpa menumpulkan upstroke, karena ke-16 bacaan diambil
 * dalam hitungan mikrodetik — ini oversample, bukan filter waktu.
 *
 * 16 dipilih supaya identik dengan ../Firmware. Di sana angka itu ditekan
 * karena core yang sama juga menguras FIFO I2C MAX30102; program INI tidak
 * mengerjakan apa pun selain ADC + filter, jadi 32 atau 64 (seperti recorder
 * validasimu) sebenarnya masih muat di anggaran 5 ms. Naikkan kalau mau,
 * LALU pastikan "overrun" di baris [STAT] tetap 0. */
#define PPG_OVERSAMPLE     16

// Jeda setelah power-gate dibuka. Baseline op-amp SON1303 (kopling DC) butuh
// waktu settle; sampel selama jendela ini dibuang, tidak masuk detektor.
#define SENSOR_SETTLE_MS   1000

// Rel ADC 12-bit. Ambang "mentok" mengikuti SQI_PPG_SAT_LEVEL di ../Firmware.
#define PPG_ADC_MAX        4095
#define PPG_SAT_LEVEL      4090
#define PPG_FLOOR_LEVEL    5

// =====================================================================
// Band-pass — satu-satunya pemrosesan sinyal
// =====================================================================
/* Butterworth orde-2 bertingkat, HP lalu LP. Koefisien DIHITUNG SAAT RUNTIME
 * dari PPG_FS_HZ (src/bpm.cpp), bukan ditempel sebagai angka mati — kalau
 * laju sampel diubah tanpa mendesain ulang filter, pita lolosnya bergeser
 * dan detektor jadi salah tanpa satu pun pesan error.
 *
 * 0,5 Hz  : buang DC + baseline wander (napas, geseran kontak). SON1303
 *           terkopel DC, jadi tanpa ini ambang adaptif akan mengejar
 *           baseline yang melayang, bukan denyut.
 * 5 Hz    : buang dengung jala-jala 50 Hz, kedip lampu 100 Hz, dan derau
 *           ADC. Aman untuk BPM (denyut 0,5-3,7 Hz; upstroke ~2-4 Hz).
 *
 * CATATAN PENTING: pita ini dipilih untuk MENCARI PUNCAK, bukan untuk PWA.
 * LP 5 Hz menumpulkan dicrotic notch — itu justru diinginkan di sini supaya
 * notch tidak pernah ikut terhitung sebagai denyut. Karena itu firmware
 * streaming TIDAK memfilter apa pun: analisis morfologi di cloud butuh
 * mentahnya. Dua tujuan berbeda, dua perlakuan berbeda. */
#define BPM_HP_HZ          0.5f
#define BPM_LP_HZ          5.0f

// Baseline lambat (one-pole) untuk DC & indeks perfusi. 0,1 Hz: cukup lambat
// untuk tidak ikut mengejar denyut, cukup cepat untuk mengikuti geseran kulit.
#define BPM_DC_HZ          0.1f

/* Sampel yang dibuang sebelum keluaran dipercaya. HP 0,5 Hz punya transien
 * step beberapa detik; tanpa jendela ini denyut "hantu" dari transien filter
 * ikut terhitung dan BPM pertama melonjak. Ini DI ATAS SENSOR_SETTLE_MS. */
#define BPM_SETTLE_MS      3000

// =====================================================================
// Detektor denyut
// =====================================================================
/* Ambang adaptif dua tingkat (histeresis), sebagai fraksi amplitudo
 * puncak-ke-palung yang sedang terpantau:
 *   HI = mulai "eksursi" (kandidat denyut)
 *   LO = eksursi berakhir
 *
 * Histeresis-nya wajib: dengan SATU ambang, riak kecil di sekitar ambang
 * memicu belasan eksursi per denyut. Jarak HI-LO membuat sinyal harus
 * benar-benar turun dulu sebelum denyut berikutnya diakui.
 *
 * 0,60 relatif tinggi dan itu disengaja — dicrotic notch pada PPG sehat
 * jarang melampaui ~50% amplitudo sistolik, jadi ambang di 60% membuatnya
 * mustahil terhitung sebagai denyut kedua. */
#define BPM_THR_HI_FRAC    0.60f
#define BPM_THR_LO_FRAC    0.40f

/* Peluruhan pelacak amplitudo, dalam fraksi amplitudo per detik. Serangan
 * (attack) selalu seketika: puncak/palung baru langsung diikuti. Yang
 * diperlambat hanya pemulihannya, supaya ambang tidak merosot ke lantai
 * derau di sela antar denyut. 0,6/detik ~ konstanta waktu 0,8 detik. */
#define BPM_ENV_DECAY_PER_S 0.6f

// Rentang fisiologis yang diterima. Di luar ini interval dibuang mentah.
#define BPM_MIN            30.0f
#define BPM_MAX            220.0f

/* Blanking (refractory) setelah puncak terdeteksi. 260 ms = plafon 230 bpm,
 * sedikit di atas BPM_MAX supaya gerbang interval — bukan blanking — yang
 * memutuskan. Ini yang membunuh deteksi ganda pada satu upstroke. */
#define BPM_REFRACT_MS     260

/* Batas panjang satu eksursi. Sinyal yang bertahan di atas ambang lebih lama
 * dari ini bukan denyut: itu geseran baseline atau gerakan. Eksursi seperti
 * itu dibuang utuh (tidak ada puncak yang dilaporkan). 600 ms dipilih karena
 * fase sistolik denyut normal < 400 ms bahkan pada bradikardia. */
#define BPM_EXC_MAX_MS     600

// =====================================================================
// Gerbang interval (IBI) & penghalus
// =====================================================================
#define BPM_IBI_HIST       8     // panjang riwayat -> median & SDNN
#define BPM_MIN_BEATS      4     // interval valid minimum sebelum BPM diumumkan

/* Simpangan maksimum satu interval dari MEDIAN riwayat, dalam persen.
 * Median (bukan rerata) supaya satu interval sampah tidak menggeser acuan
 * dan menyeret gerbangnya sendiri.
 *
 * 30% cukup longgar untuk aritmia sinus pernapasan (variasi normal
 * 5-15%) tapi cukup ketat untuk menolak puncak yang terlewat/tergandakan. */
#define BPM_IBI_DEV_PCT    30

/* Perbaikan denyut TERLEWAT. Satu puncak yang gagal terdeteksi menghasilkan
 * interval ~2x median — kalau dibiarkan, ia ditolak gerbang di atas dan
 * BPM membeku sebentar. Kalau ibi/2 justru cocok dengan median (toleransi di
 * bawah), interval itu dipecah jadi DUA dan keduanya masuk riwayat.
 *
 * Ini interpolasi, bukan pengukuran: cacahnya dilaporkan terpisah sebagai
 * "interp" supaya bisa diaudit. Kalau angka itu tinggi, yang perlu dibetulkan
 * adalah kontak sensor, bukan algoritmanya. 0 = matikan. */
#define BPM_MISSED_FIX     1
#define BPM_MISSED_TOL_PCT 20

/* Berapa penolakan BERURUTAN sebelum riwayat dibuang dan detektor mencari
 * kunci baru. Tanpa ini, laju jantung yang berubah cepat (mulai olahraga,
 * berdiri tiba-tiba) akan ditolak terus-menerus oleh gerbang median yang
 * masih memegang laju lama — detektor mengunci diri sendiri. */
#define BPM_RESYNC_REJECTS 4

// Penghalus tampilan. bpm_inst = 60000/median (sudah tahan outlier);
// nilai yang dilaporkan di-EMA supaya angkanya tidak gemetar tiap denyut.
#define BPM_EMA_ALPHA      0.30f

/* Berapa lama BPM terakhir yang sahih tetap ditampilkan setelah sinyal
 * memburuk. Menahan angka lebih berguna daripada mengosongkannya saat
 * seseorang bergerak sebentar; lewat batas ini, nilainya dinolkan supaya
 * tidak ada angka basi yang terlihat seperti pengukuran hidup. */
#define BPM_HOLD_MS        5000

// =====================================================================
// Gerbang kontak & mutu (0..100, semangatnya sama dengan SQI di ../Firmware:
// skor akhir = MINIMUM sub-skor, bukan rata-rata)
// =====================================================================
/* Jendela DC yang dianggap "sensor menempel". SON1303 mengeluarkan tegangan
 * di sekitar tengah rel saat terpasang normal; menempel di rel atas/bawah
 * berarti tidak ada jari, LED sensor mati, atau op-amp saturasi.
 *
 * Ambang ini PALING PERLU dikalibrasi untuk unitmu: nyalakan
 * BPM_STREAM_CSV 1, lihat kolom dc saat jari menempel dan saat dilepas. */
#define BPM_DC_MIN         120
#define BPM_DC_MAX         3900

// Amplitudo AC minimum (LSB ADC 12-bit) untuk dianggap ada denyut.
// Di bawah ini sinyal praktis garis datar. Bandingkan SQI_PPG_P2P_MIN = 15.
#define BPM_AC_MIN_LSB     15

/* Indeks perfusi (AC/DC) dalam per-mil, dipakai sebagai sub-skor mutu.
 * MIN sengaja rendah — pergelangan jauh lebih lemah daripada ujung jari,
 * dan gerbang yang kelewat tinggi membuang data sehat. */
#define BPM_PI_MIN_PERMIL  3
#define BPM_PI_GOOD_LO     10
#define BPM_PI_GOOD_HI     400
#define BPM_PI_MAX_PERMIL  800

/* Sub-skor kestabilan: rerata |ibi - median| / median dalam per-mil.
 * <=5% dianggap sempurna (variasi pernapasan normal), >=25% dianggap nol. */
#define BPM_STAB_GOOD_PERMIL 50
#define BPM_STAB_MAX_PERMIL  250

// Toleransi sampel mentok rel per jendela 1 detik sebelum skor dijatuhkan.
#define BPM_CLIP_MAX_N     2

// Skor minimum supaya status jadi LOCKED (BPM dianggap sahih).
#define BPM_MIN_CONF       50

/* Berapa lama kondisi buruk harus BERTAHAN sebelum status jatuh ke
 * NO_CONTACT dan riwayat dihapus. Tanpa penahan ini, satu kedipan artefak
 * membuang kunci yang butuh 4 denyut untuk dibangun kembali. */
#define BPM_CONTACT_HOLD_MS 700

// =====================================================================
// Keluaran & debug
// =====================================================================
#define SERIAL_BAUD        115200
#define BPM_REPORT_MS      1000   // baris [BPM ] tiap 1 detik
#define STAT_PERIOD_MS     5000   // baris [STAT] tiap 5 detik

/* 1 = cetak SATU BARIS CSV PER SAMPEL (200 baris/detik) untuk Serial Plotter:
 *   t_ms,raw,ac,thr_hi,thr_lo,beat
 * Inilah cara mengkalibrasi BPM_DC_MIN/MAX dan BPM_THR_*: lihat sinyalnya,
 * jangan menduga. Baris [BPM ]/[STAT] otomatis dibungkam supaya CSV bersih.
 *
 * Ada ongkosnya: pencetakan terjadi di dalam task pencuplik, jadi timing 5 ms
 * ikut terganggu sedikit (terlihat sebagai overrun > 0). Matikan saat
 * mengukur sungguhan. */
#define BPM_STREAM_CSV     0

// 1 = LED D10 berkedip satu kali per denyut yang DITERIMA (kedip meluruh
// seperti detak). Cara tercepat melihat detektor bekerja tanpa serial monitor.
#define BPM_LED_BEAT       1
#define BPM_LED_FLASH_MS   140
#define LED_PWM_FREQ_HZ    4000
#define LED_PWM_BITS       12
#define LED_DUTY_MAX       ((1 << LED_PWM_BITS) - 1)
