/**
 * ANTARAGA Smartband — tipe & kontrak antar-modul
 * =====================================================================
 * Pembagian kerja (sesuai algoritma):
 *
 *   CORE 0  "core WiFi"    : netTask()    — connect WiFi, NTP, POST HTTPS.
 *   CORE 1  "core sensor"  : sensorTask() — MAX30102 (FIFO) + SEN0203 + baterai.
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
#define PIN_SIG_PPG      2    // D1 / A1  <- keluaran analog SEN0203
#define PIN_SEN_EN       3    // D2       -> gate Q2 (DMP2130L, P-MOS): LOW = sensor ON
#define PIN_SDA          5    // D4       <-> MAX30102 SDA
#define PIN_SCL          6    // D5       <-> MAX30102 SCL
#define PIN_LED          9    // D10      -> LED via R6 10k (HIGH = nyala)

#define SEN_POWER_ON     LOW  // Q2 P-channel: gate ditarik LOW -> tersambung
#define SEN_POWER_OFF    HIGH // R5 100k pull-up ke 3V3 -> default mati saat boot

// ---------------------------------------------------------------------
// Turunan laju sampel
// ---------------------------------------------------------------------
#if MAX_PROFILE_PWA
  #define MAX_FS_HZ      400
#else
  #define MAX_FS_HZ      250
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
  uint16_t ppg[PPG_PER_BATCH];   // ADC mentah SEN0203 (0..4095, hasil oversample)
  uint32_t red[MAX_CAP];         // ADC mentah MAX30102 kanal RED (18-bit)
  uint32_t ir [MAX_CAP];         // ADC mentah MAX30102 kanal IR  (18-bit)

  uint16_t batt_mv;          // tegangan baterai (mV, sudah dikali pembagi)
  uint8_t  batt_pct;         // 0..100
  uint8_t  max_ovf;          // overflow FIFO MAX30102 selama batch ini
};

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
