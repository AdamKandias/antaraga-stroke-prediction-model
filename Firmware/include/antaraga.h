/**
 * ANTARAGA Smartband — tipe & kontrak antar-modul
 * =====================================================================
 * Pembagian kerja (sesuai algoritma):
 *
 *   CORE 0  "core WiFi"    : netTask()    — connect WiFi, NTP, SQI, POST HTTPS.
 *   CORE 1  "core sensor"  : sensorTask() — MAX30102 (FIFO) + SON1303 + baterai.
 *   CORE 1  loop()         : LED indikator D10 + cetak statistik.
 *
 * Aliran data: sensorTask mengisi Batch -> qFilled -> netTask kirim -> qFree.
 * Producer tidak pernah menunggu jaringan; kalau qFree habis, batch TERTUA
 * dibuang dan dihitung di Stats.dropped.
 */
#pragma once

#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <freertos/event_groups.h>
#include "config.h"

// ---------------------------------------------------------------------
// Pin — XIAO ESP32-S3 (nama silkscreen -> GPIO), sesuai skematik ANTARAGA
// ---------------------------------------------------------------------
#define PIN_VSENS        1    // D0 / A0  <- pembagi tegangan baterai (R1/R2 100k)
#define PIN_SIG_PPG      2    // D1 / A1  <- keluaran analog SON1303
#define PIN_SEN_EN       3    // D2       -> gate Q2 (DMP2130L, P-MOS): LOW = sensor ON
#define PIN_SDA          5    // D4       <-> MAX30102 SDA
#define PIN_SCL          6    // D5       <-> MAX30102 SCL
#define PIN_LED          9    // D10      -> LED via R6 10k (HIGH = nyala)

#define SEN_POWER_ON     LOW  // Q2 P-channel: gate ditarik LOW -> tersambung
#define SEN_POWER_OFF    HIGH // R5 100k pull-up ke 3V3 -> default mati saat boot

// ---------------------------------------------------------------------
// Turunan laju sampel
// ---------------------------------------------------------------------
/* Kedua profil memakai SR=400 Hz di chip (batas mode SpO2 pada PW 411 us);
 * yang membedakan hanya SMP_AVE. Lihat CFG_SPO2/CFG_FIFO di src/sensors.cpp —
 * angka di bawah HARUS ikut kalau CFG_FIFO diubah, karena nilai ini yang
 * dikirim ke cloud sebagai "fs_max". */
#if MAX_PROFILE_PWA
  #define MAX_FS_HZ      400    // SMP_AVE=1
#else
  #define MAX_FS_HZ      200    // SMP_AVE=2
#endif

#define PPG_PERIOD_MS    (1000 / PPG_FS_HZ)
static_assert(1000 % PPG_FS_HZ == 0, "PPG_FS_HZ harus pembagi bulat dari 1000");
static_assert(BATCH_MS % PPG_PERIOD_MS == 0, "BATCH_MS harus kelipatan periode PPG");

#define PPG_PER_BATCH    (PPG_FS_HZ * BATCH_MS / 1000)
#define MAX_PER_BATCH    (MAX_FS_HZ * BATCH_MS / 1000)
// Headroom 25% untuk jitter clock internal MAX30102 (toleransi osilatornya
// beberapa persen, jadi jumlah sampel per batch tidak selalu persis).
#define MAX_CAP          (MAX_PER_BATCH + MAX_PER_BATCH / 4 + 8)

// ---------------------------------------------------------------------
// Batch: satu paket data mentah siap kirim
// ---------------------------------------------------------------------
struct Batch {
  uint32_t seq;              // nomor urut, naik terus sejak streaming mulai
  uint32_t t0_ms;            // millis() saat sampel PPG pertama batch ini
  uint64_t t0_unix_ms;       // epoch ms (0 kalau NTP belum sinkron)

  uint16_t ppg_n;
  uint16_t max_n;
  uint16_t ppg[PPG_PER_BATCH];   // ADC mentah SON1303 (0..4095, hasil oversample)
  uint32_t red[MAX_CAP];         // ADC mentah MAX30102 kanal RED (18-bit)
  uint32_t ir [MAX_CAP];         // ADC mentah MAX30102 kanal IR  (18-bit)

  uint16_t batt_mv;          // tegangan baterai (mV, sudah dikali pembagi)
  uint8_t  batt_pct;         // 0..100
  uint8_t  max_ovf;          // overflow FIFO MAX30102 selama batch ini
};

// ---------------------------------------------------------------------
// SQI — metrik kualitas SATU package (dihitung di core 0, sqi.cpp).
// Metadata saja — gerbang kirim/buang dilakukan di CLOUD, bukan di sini.
// ---------------------------------------------------------------------
// Indikator masalah. Flag apa pun yang menyala memaksa skor jadi 0 (lihat
// sqi.cpp), sebagai sinyal kuat "kemungkinan besar bermutu rendah". Dikirim
// ke cloud sebagai "sqi_flags" supaya cloud yang memutuskan kirim/buang.
#define SQI_F_NO_FINGER  (1 << 0)   // DC IR terlalu rendah — sensor tidak menempel
#define SQI_F_SATURATED  (1 << 1)   // DC kelewat tinggi / sampel mentok rel ADC
#define SQI_F_FLAT       (1 << 2)   // nyaris tanpa riak — sensor macet / tidak ada denyut
#define SQI_F_MOTION     (1 << 3)   // lompatan antar sampel berurutan tidak wajar
#define SQI_F_PPG_BAD    (1 << 4)   // kanal SON1303 di luar batas wajar
#define SQI_F_SHORT      (1 << 5)   // jumlah sampel kurang dari yang seharusnya

struct Sqi {
  uint8_t  score;       // 0..100 — MINIMUM sub-skor, bukan rata-ratanya
  uint8_t  flags;       // 0 = bersih

  uint32_t ir_dc;       // rerata IR (hanya penyebut normalisasi & telemetri)
  uint32_t ir_p2p;      // puncak-ke-puncak IR
  uint32_t ir_jump;     // lompatan TERBESAR antar dua sampel berurutan
  uint16_t ir_jump_n;   // cacah sampel yang melompat >= ambang LUNAK
  uint16_t ir_tort10;   // panjang lintasan / p2p, x10
  uint16_t ir_pi;       // perfusi p2p/DC dalam per-mil

  uint16_t ppg_dc;
  uint16_t ppg_p2p;
  uint16_t ppg_jump;
  uint16_t ppg_jump_n;
  uint16_t ppg_tort10;

  uint16_t clip_n;      // cacah sampel yang mentok rel (IR + RED + PPG)
};

// Menghitung SELURUH metrik/skor SQI ke *out sebagai metadata untuk cloud.
// TIDAK memutuskan kirim/buang — gerbang kelayakan sepenuhnya di cloud.
// Tidak mengubah isi Batch sama sekali — data yang dikirim tetap 100% mentah.
void sqiEvaluate(const Batch* b, Sqi* out);

/* Alasan tolak jadi teks. Buffer WAJIB disediakan pemanggil (bukan statis di
 * dalam fungsi): ini dipanggil dari loop() di core 1 DAN dari netTask di core 0,
 * jadi buffer bersama akan saling menimpa. Kapasitas aman: 48 byte. */
#define SQI_FLAGS_TEXT_CAP 48
void sqiFlagsText(uint8_t flags, char* buf, size_t cap);

// ---------------------------------------------------------------------
// Status perangkat (menentukan pola kedip LED D10)
// ---------------------------------------------------------------------
enum DeviceState : uint8_t {
  ST_BOOT = 0,
  ST_WIFI_CONNECTING,   // kedip cepat
  ST_SENSOR_WARMUP,     // kedip sedang
  ST_STREAMING,         // denyut pendek 1x/detik  <- kondisi normal
  ST_NET_LOST,          // kedip ganda: sensor jalan, jaringan putus
  ST_ERROR              // nyala panjang: sensor gagal init
};

// ---------------------------------------------------------------------
// Statistik runtime (ditulis task, dibaca loop() untuk baris [STAT])
// ---------------------------------------------------------------------
struct Stats {
  volatile uint32_t batches_made;
  volatile uint32_t batches_sent;
  volatile uint32_t batches_dropped;  // qFree habis -> batch tertua dibuang
  volatile uint32_t http_fail;
  volatile uint32_t max_ovf_total;    // FIFO MAX30102 kebablasan
  volatile uint32_t ppg_overrun;      // sensorTask telat dari jadwal 5 ms
  volatile uint32_t max_trunc;        // sampel MAX30102 dibuang, MAX_CAP penuh
  volatile int32_t  last_http_code;
  volatile uint32_t last_post_ms;     // durasi 1x POST; kalau > BATCH_MS, jaringan kalah cepat
  volatile uint32_t ppg_samples;
  volatile uint32_t max_samples;

  // Metrik SQI — semua package tetap dikirim; ini murni visibilitas lokal.
  // Gerbang kirim/buang dilakukan di cloud dari metadata sqi/sqi_flags.
  volatile uint32_t sqi_flagged;     // cacah package dengan sqi_flags != 0
  volatile uint8_t  sqi_last_score;
  volatile uint8_t  sqi_last_flags;
};

// ---------------------------------------------------------------------
// Objek global (didefinisikan di main.cpp)
// ---------------------------------------------------------------------
#define EV_WIFI_OK   (1 << 0)   // WiFi pernah/sedang tersambung
#define EV_NTP_OK    (1 << 1)

extern EventGroupHandle_t g_events;
extern QueueHandle_t      g_qFree;    // Batch* kosong siap diisi
extern QueueHandle_t      g_qFilled;  // Batch* penuh siap dikirim
extern volatile DeviceState g_state;
extern Stats                g_stats;

// Bacaan baterai terakhir (ditulis sensors.cpp, dibaca loop() untuk [STAT])
extern volatile uint16_t g_battMv;
extern volatile uint8_t  g_battPct;

void setState(DeviceState s);

// ---------------------------------------------------------------------
// Entry point tiap modul
// ---------------------------------------------------------------------
void sensorTask(void* arg);   // sensors.cpp — pinned ke core 1
void netTask(void* arg);      // cloud.cpp   — pinned ke core 0

uint64_t unixMillis();        // cloud.cpp — 0 kalau NTP belum sinkron
