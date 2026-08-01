/**
 * ANTARAGA — PRE-PROCESSING & SQI (Signal Quality Index)
 * =====================================================================
 * Dipanggil dari netTask (core 0) tepat sebelum serialisasi JSON. Sengaja
 * BUKAN di core 1: core sensor punya anggaran 5 ms per tick yang tidak boleh
 * diganggu, sedangkan core 0 justru banyak menganggur menunggu jaringan.
 *
 * PRINSIP RANCANGAN
 * -----------------
 * 1. Satu package = satu keputusan. Tidak ada state yang dibawa antar package,
 *    jadi package bagus tidak pernah ikut tercemar oleh tetangganya yang buruk.
 *
 * 2. Skor akhir = MINIMUM sub-skor, bukan rata-rata. Ini inti permintaannya:
 *    rata-rata menyamarkan outlier — satu lompatan gerakan parah akan larut di
 *    antara ratusan sampel lain dan package sampah tetap lolos. Minimum tidak
 *    bisa disamarkan; satu aspek rusak langsung menjatuhkan seluruh package.
 *
 * 3. Statistiknya bertipe EKSTREM (min, max, lompatan terbesar, panjang
 *    lintasan) — bukan rerata. Satu-satunya rerata di sini adalah DC, dan itu
 *    murni penyebut normalisasi + telemetri, tidak pernah jadi penilai mutu.
 *
 * 4. Data yang dikirim TIDAK disentuh. Tidak ada filter, smoothing, atau
 *    resampling. Modul ini hanya menjawab satu pertanyaan: kirim atau buang.
 *
 * TIGA KELAS CACAT YANG DITANGKAP
 * -------------------------------
 *   kontak/pencahayaan : level DC + sampel mentok rel + perfusi
 *   artefak terisolasi : lompatan antar sampel, dua tingkat (keras & lunak)
 *   noise tersebar     : tortuosity (panjang lintasan / p2p)
 *
 * Ketiganya perlu: max-jump buta terhadap noise beramplitudo sedang yang
 * merata, dan tortuosity buta terhadap satu lompatan besar yang terisolasi.
 */

#include "antaraga.h"
#include <string.h>

// =====================================================================
// Statistik ekstrem per kanal (satu lintasan)
// =====================================================================
struct ChanStat {
  uint32_t dc;      // rerata — hanya penyebut normalisasi
  uint32_t min;
  uint32_t max;
  uint32_t p2p;
  uint32_t jump;    // |x[i] - x[i-1]| TERBESAR dalam package
  uint32_t path;    // SIGMA |x[i] - x[i-1]| — panjang lintasan
  uint16_t clip;    // cacah sampel yang mentok rel
};

#define ABSDIFF(a, b)  (((a) > (b)) ? ((a) - (b)) : ((b) - (a)))

static void chanStat32(const uint32_t* x, uint16_t n, uint32_t sat, ChanStat* o) {
  memset(o, 0, sizeof(*o));
  if (!n) return;
  uint64_t sum = 0;
  o->min = 0xFFFFFFFFu;
  for (uint16_t i = 0; i < n; i++) {
    const uint32_t v = x[i];
    sum += v;
    if (v < o->min) o->min = v;
    if (v > o->max) o->max = v;
    if (v >= sat)   o->clip++;
    if (i) {
      const uint32_t d = ABSDIFF(v, x[i - 1]);
      if (d > o->jump) o->jump = d;
      o->path += d;
    }
  }
  o->dc  = (uint32_t)(sum / n);
  o->p2p = o->max - o->min;
}

static void chanStat16(const uint16_t* x, uint16_t n, uint16_t sat, ChanStat* o) {
  memset(o, 0, sizeof(*o));
  if (!n) return;
  uint32_t sum = 0;
  o->min = 0xFFFFFFFFu;
  for (uint16_t i = 0; i < n; i++) {
    const uint32_t v = x[i];
    sum += v;
    if (v < o->min) o->min = v;
    if (v > o->max) o->max = v;
    if (v >= sat)   o->clip++;
    if (i) {
      const uint32_t d = ABSDIFF(v, (uint32_t)x[i - 1]);
      if (d > o->jump) o->jump = d;
      o->path += d;
    }
  }
  o->dc  = sum / n;
  o->p2p = o->max - o->min;
}

/* Lintasan kedua: cacah lompatan yang melewati ambang. Ambangnya baru diketahui
 * setelah p2p dihitung, jadi tidak bisa digabung ke lintasan pertama. Biayanya
 * beberapa mikrodetik atas ratusan sampel — tidak berarti di core 0. */
static uint16_t countJumps32(const uint32_t* x, uint16_t n, uint32_t thr) {
  uint16_t c = 0;
  for (uint16_t i = 1; i < n; i++) if (ABSDIFF(x[i], x[i - 1]) >= thr) c++;
  return c;
}

static uint16_t countJumps16(const uint16_t* x, uint16_t n, uint32_t thr) {
  uint16_t c = 0;
  for (uint16_t i = 1; i < n; i++) {
    if (ABSDIFF((uint32_t)x[i], (uint32_t)x[i - 1]) >= thr) c++;
  }
  return c;
}

// Rasio panjang lintasan terhadap p2p, dikali 10. 0 = p2p nol (garis datar).
static uint16_t tort10(const ChanStat* s) {
  if (!s->p2p) return 0;
  const uint32_t t = (uint32_t)((uint64_t)s->path * 10u / s->p2p);
  return (t > 0xFFFFu) ? 0xFFFFu : (uint16_t)t;
}

// =====================================================================
// Pembentuk sub-skor
// =====================================================================
/* Skor jendela: 100 penuh di dalam [lo..hi], meluruh linear ke 0 saat menuju
 * floor / ceil, 0 di luar itu. Untuk besaran yang punya zona nyaman di tengah
 * — level DC dan perfusi: terlalu rendah dan terlalu tinggi sama-sama buruk. */
static uint8_t bandScore(uint32_t v, uint32_t floorV, uint32_t lo,
                         uint32_t hi, uint32_t ceilV) {
  if (v <= floorV || v >= ceilV) return 0;
  if (v >= lo && v <= hi)        return 100;
  if (v < lo)  return (uint8_t)(100u * (v - floorV) / (lo - floorV));
  return (uint8_t)(100u * (ceilV - v) / (ceilV - hi));
}

/* Skor "makin kecil makin baik": 100 sampai batas good, meluruh ke 0 di maxV.
 * Dipakai untuk tortuosity dan untuk fraksi lompatan. */
static uint8_t decayScore(uint32_t v, uint32_t good, uint32_t maxV) {
  if (v <= good)  return 100;
  if (v >= maxV)  return 0;
  return (uint8_t)(100u - 100u * (v - good) / (maxV - good));
}

static inline uint8_t minU8(uint8_t a, uint8_t b) { return a < b ? a : b; }

// =====================================================================
// Gerbang utama
// =====================================================================
/* PENTING: metrik SELALU dihitung, bahkan saat SQI_ENABLE 0. Yang dimatikan
 * oleh SQI_ENABLE hanyalah KEPUTUSAN buang/kirim di baris terakhir.
 *
 * Ini bukan detail sepele: SQI_ENABLE 0 justru dipakai untuk MENGKALIBRASI
 * ambang, dan kalibrasi butuh sebaran ir_dc / ir_pi / ir_jump_n / ir_tort10
 * yang nyata. Kalau perhitungannya ikut dilewati, seluruh metrik terkirim
 * sebagai 0 dan tidak ada yang bisa dikalibrasi. */
bool sqiEvaluate(const Batch* b, Sqi* q) {
  memset(q, 0, sizeof(*q));

  {
  ChanStat ir, red, pg;
  chanStat32(b->ir,  b->max_n, SQI_SAT_LEVEL,     &ir);
  chanStat32(b->red, b->max_n, SQI_SAT_LEVEL,     &red);
  chanStat16(b->ppg, b->ppg_n, SQI_PPG_SAT_LEVEL, &pg);

  // Ambang lompatan bersifat relatif terhadap p2p package ini sendiri, jadi
  // gerbangnya tidak bergeser saat amplitudo sinyal berubah.
  const uint32_t irHard  = (uint32_t)((uint64_t)ir.p2p * SQI_IR_JUMP_HARD_PCT / 100u);
  const uint32_t irSoft  = (uint32_t)((uint64_t)ir.p2p * SQI_IR_JUMP_MAX_PCT  / 100u);
  const uint32_t pgHard  = (uint32_t)((uint64_t)pg.p2p * SQI_PPG_JUMP_HARD_PCT / 100u);
  const uint32_t pgSoft  = (uint32_t)((uint64_t)pg.p2p * SQI_PPG_JUMP_MAX_PCT  / 100u);

  q->ir_dc      = ir.dc;
  q->ir_p2p     = ir.p2p;
  q->ir_jump    = ir.jump;
  q->ir_jump_n  = irSoft ? countJumps32(b->ir, b->max_n, irSoft) : 0;
  q->ir_tort10  = tort10(&ir);
  q->ir_pi      = ir.dc ? (uint16_t)((uint64_t)ir.p2p * 1000u / ir.dc) : 0;

  q->ppg_dc     = (uint16_t)pg.dc;
  q->ppg_p2p    = (uint16_t)pg.p2p;
  q->ppg_jump   = (uint16_t)pg.jump;
  q->ppg_jump_n = pgSoft ? countJumps16(b->ppg, b->ppg_n, pgSoft) : 0;
  q->ppg_tort10 = tort10(&pg);

  q->clip_n     = (uint16_t)(ir.clip + red.clip + pg.clip);

  // --- Gerbang keras: apa pun yang menyala di sini = buang ------------
  /* Sampel kurang. Toleransi 10% untuk PPG (dikunci tick FreeRTOS, jadi ketat)
   * dan 25% untuk MAX30102 (osilator internalnya sendiri, lebih longgar). */
  if (b->ppg_n < PPG_PER_BATCH - PPG_PER_BATCH / 10 ||
      b->max_n < MAX_PER_BATCH - MAX_PER_BATCH / 4) {
    q->flags |= SQI_F_SHORT;
  }

  if (ir.dc < SQI_IR_DC_MIN)                     q->flags |= SQI_F_NO_FINGER;
  if (ir.dc > SQI_IR_DC_MAX ||
      q->clip_n > SQI_CLIP_MAX_N)                q->flags |= SQI_F_SATURATED;

  // Perfusi — di BATCH_MS 1000 ini gerbang mutu sungguhan, bukan sekadar
  // lantai anti-flatline, karena jendelanya memuat denyut utuh.
  if (q->ir_pi < SQI_IR_PI_MIN_PERMIL)           q->flags |= SQI_F_FLAT;
  if (q->ir_pi > SQI_IR_PI_MAX_PERMIL)           q->flags |= SQI_F_MOTION;

  // Lompatan IR, dua tingkat.
  const uint32_t irSoftPermil = b->max_n ? (uint32_t)q->ir_jump_n * 1000u / b->max_n : 0;
  if (ir.p2p && ir.jump >= irHard)               q->flags |= SQI_F_MOTION;   // keras
  if (irSoftPermil > SQI_JUMP_SOFT_PERMIL)       q->flags |= SQI_F_MOTION;   // lunak

  // Noise tersebar pada IR.
  if (q->ir_tort10 >= SQI_IR_TORT_MAX_X10)       q->flags |= SQI_F_MOTION;

  // Kanal SON1303.
  const uint32_t pgSoftPermil = b->ppg_n ? (uint32_t)q->ppg_jump_n * 1000u / b->ppg_n : 0;
  if (pg.p2p < SQI_PPG_P2P_MIN || pg.p2p > SQI_PPG_P2P_MAX) q->flags |= SQI_F_PPG_BAD;
  if (pg.p2p && pg.jump >= pgHard)               q->flags |= SQI_F_PPG_BAD;
  if (pgSoftPermil > SQI_JUMP_SOFT_PERMIL)       q->flags |= SQI_F_PPG_BAD;
  if (q->ppg_tort10 >= SQI_PPG_TORT_MAX_X10)     q->flags |= SQI_F_PPG_BAD;

  // --- Skor: MINIMUM sub-skor ----------------------------------------
  const uint8_t sDc    = bandScore(ir.dc, SQI_IR_DC_MIN, SQI_IR_DC_GOOD_LO,
                                   SQI_IR_DC_GOOD_HI, SQI_IR_DC_MAX);
  const uint8_t sPerf  = bandScore(q->ir_pi, SQI_IR_PI_MIN_PERMIL, SQI_IR_PI_GOOD_LO,
                                   SQI_IR_PI_GOOD_HI, SQI_IR_PI_MAX_PERMIL);
  const uint8_t sJump  = decayScore(irSoftPermil, 0, SQI_JUMP_SOFT_PERMIL);
  const uint8_t sTort  = decayScore(q->ir_tort10, SQI_IR_TORT_GOOD_X10,
                                    SQI_IR_TORT_MAX_X10);
  const uint8_t sPpgJ  = decayScore(pgSoftPermil, 0, SQI_JUMP_SOFT_PERMIL);
  const uint8_t sPpgT  = decayScore(q->ppg_tort10, SQI_PPG_TORT_GOOD_X10,
                                    SQI_PPG_TORT_MAX_X10);
  const uint8_t sClip  = (q->clip_n == 0) ? 100
                       : (q->clip_n <= SQI_CLIP_MAX_N ? 50 : 0);

  q->score = minU8(minU8(minU8(sDc, sPerf), minU8(sJump, sTort)),
                   minU8(minU8(sPpgJ, sPpgT), sClip));
  if (q->flags) q->score = 0;
  }

#if SQI_ENABLE
  return q->flags == 0 && q->score >= SQI_MIN_SCORE;
#else
  /* Gerbang MATI: semua package dikirim apa adanya. Skor dan flag tetap ikut
   * di payload sebagai catatan — kamu bisa melihat package mana yang SEHARUSNYA
   * ditolak tanpa benar-benar kehilangan datanya. Itu justru cara paling cepat
   * mengetahui apakah ambangmu kelewat ketat. */
  return true;
#endif
}

// =====================================================================
// Alasan tolak dalam bentuk teks (untuk baris [STAT] dan log per-package)
// =====================================================================
void sqiFlagsText(uint8_t flags, char* buf, size_t cap) {
  if (!buf || cap == 0) return;
  buf[0] = '\0';
  if (!flags) { if (cap > 1) { buf[0] = '-'; buf[1] = '\0'; } return; }

  static const struct { uint8_t bit; const char* name; } kNames[] = {
    { SQI_F_NO_FINGER, "nofinger" }, { SQI_F_SATURATED, "sat"    },
    { SQI_F_FLAT,      "flat"     }, { SQI_F_MOTION,    "motion" },
    { SQI_F_PPG_BAD,   "ppg"      }, { SQI_F_SHORT,     "short"  },
  };

  size_t len = 0;
  for (uint8_t i = 0; i < sizeof(kNames) / sizeof(kNames[0]); i++) {
    if (!(flags & kNames[i].bit)) continue;
    const char* s = kNames[i].name;
    if (len && len + 1 < cap) buf[len++] = ' ';
    while (*s && len + 1 < cap) buf[len++] = *s++;
  }
  buf[len] = '\0';
}
