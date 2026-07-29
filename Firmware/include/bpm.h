/**
 * ANTARAGA BPM — kontrak mesin penghitung denyut
 * =====================================================================
 * SENGAJA tanpa Arduino.h, tanpa driver, tanpa Serial. Mesin ini hanya
 * menerima deretan angka ADC mentah SON1303 dan mengembalikan BPM.
 *
 * Konsekuensi yang dikejar: file src/bpm.cpp yang sama bisa dijalankan
 * di ESP32 (src/ppg.cpp memberinya sampel dari ADC) DAN di PC (tools/
 * bpm_csv.cpp memberinya sampel dari CSV hasil rekaman recorder-mu).
 * Algoritmanya diuji di PC terhadap rekaman nyata yang sudah kamu punya,
 * bukan ditebak lewat serial monitor.
 *
 * Pemakaian:
 *      bpmInit(PPG_FS_HZ);
 *      for (;;) { ... bpmPush(adcRaw, &out); }        // 1x per periode sampel
 *
 * bpmPush() WAJIB dipanggil pada laju tetap PPG_FS_HZ: seluruh basis waktu
 * (interval, refractory, peluruhan ambang) dihitung dari CACAHAN SAMPEL,
 * bukan dari jam dinding. Itu justru yang membuat hasilnya presisi —
 * cacahan sampel dikunci tick FreeRTOS, sementara millis() di dalam task
 * yang juga meladeni USB bisa tergeser beberapa milidetik.
 */
#pragma once

#include <stdint.h>
#include "config.h"

// ---------------------------------------------------------------------
// Status mesin — inilah yang menentukan apakah angka BPM boleh dipercaya
// ---------------------------------------------------------------------
enum BpmStatus : uint8_t {
  BPM_SETTLING = 0,   // transien filter belum lewat (BPM_SETTLE_MS)
  BPM_NO_CONTACT,     // DC di luar jendela / AC nyaris nol -> sensor tidak menempel
  BPM_SEARCHING,      // sinyal ada, denyut valid belum cukup (< BPM_MIN_BEATS)
  BPM_NOISY,          // denyut terdeteksi tapi skor mutu di bawah BPM_MIN_CONF
  BPM_LOCKED          // BPM sahih  <- satu-satunya status yang layak dipakai
};

// ---------------------------------------------------------------------
// Keluaran — POD, aman dicopy antar task
// ---------------------------------------------------------------------
struct BpmOut {
  BpmStatus status;
  uint8_t   conf;         // 0..100, MINIMUM sub-skor (bukan rata-rata)
  bool      beat;         // true HANYA pada sampel saat denyut diterima
  uint8_t   _pad;

  float     bpm;          // dilaporkan (EMA). 0 = belum ada nilai sahih
  float     bpm_inst;     // 60000 / median(riwayat IBI), tanpa penghalusan
  float     ibi_med_ms;   // median interval
  float     sdnn_ms;      // simpangan baku riwayat IBI — telemetri HRV kasar
  uint32_t  bpm_age_ms;   // umur nilai `bpm`; > BPM_HOLD_MS -> bpm dinolkan

  // --- keadaan sinyal (untuk kalibrasi ambang & audit) ---
  float     ac;           // amplitudo puncak-ke-palung terpantau (LSB)
  float     dc;           // baseline lambat (LSB)
  uint16_t  pi_permil;    // 1000 * ac / dc — indeks perfusi
  uint16_t  clip_n;       // sampel mentok rel pada jendela 1 detik terakhir

  // --- nilai sesaat, berguna saat BPM_STREAM_CSV = 1 ---
  float     ac_now;       // keluaran band-pass sampel ini
  float     thr_hi;
  float     thr_lo;

  // --- cacahan sejak boot ---
  uint32_t  beats;        // denyut diterima
  uint32_t  rejects;      // interval ditolak gerbang IBI
  uint32_t  interp;       // interval hasil perbaikan denyut terlewat
  uint32_t  resyncs;      // riwayat dibuang karena penolakan berurutan
};

// ---------------------------------------------------------------------
// API
// ---------------------------------------------------------------------
/* Siapkan mesin untuk laju sampel fs (Hz). Mendesain ulang band-pass, jadi
 * WAJIB dipanggil sebelum bpmPush(). Aman dipanggil ulang. */
void bpmInit(float fs);

/* Hapus seluruh keadaan (filter, ambang, riwayat interval) tanpa mengubah
 * desain filter. Dipakai saat kontak hilang atau setelah power-cycle sensor.
 * Cacahan seumur-hidup (beats/rejects/...) TIDAK dinolkan. */
void bpmReset();

/* Masukkan satu sampel ADC mentah (0..PPG_ADC_MAX) dan ambil keadaan mesin.
 * `out` boleh nullptr. out->beat true hanya pada pemanggilan saat sebuah
 * denyut diterima — dipakai untuk mengedipkan LED per detak. */
void bpmPush(uint16_t raw, BpmOut* out);

// Salinan keadaan terakhir tanpa memasukkan sampel baru.
void bpmSnapshot(BpmOut* out);

// Nama status untuk dicetak.
const char* bpmStatusName(BpmStatus s);
