/**
 * ANTARAGA BPM — ALGORITMA PENGHITUNG DENYUT dari SON1303
 * =====================================================================
 * Masukan  : deret ADC 12-bit SON1303 pada laju TETAP PPG_FS_HZ (200 Hz),
 *            hasil oversample 16x — persis seperti yang dicuplik
 *            ../Firmware/src/sensors.cpp.
 * Keluaran : BPM + skor keyakinan + status kontak.
 *
 * ENAM LAPIS, dan tiap lapis menangkap kelas kesalahan yang lapis lain
 * TIDAK bisa lihat. Urutannya penting:
 *
 *   1. BAND-PASS 0,5-5 Hz (Butterworth orde-2 bertingkat)
 *      Buang DC & baseline wander di bawah, dengung jala-jala di atas.
 *      SON1303 terkopel DC: tanpa lapis ini ambang adaptif akan mengejar
 *      baseline yang melayang, bukan denyut.
 *
 *   2. PELACAK AMPLITUDO (serangan seketika, peluruhan lambat)
 *      Amplitudo PPG pergelangan berubah beberapa kali lipat hanya karena
 *      tekanan kontak. Ambang tetap SELALU salah: kalau pas untuk sinyal
 *      kuat, ia melewatkan seluruh denyut lemah, dan sebaliknya.
 *
 *   3. EKSURSI BERHISTERESIS + BLANKING
 *      Ambang naik (60%) dan ambang turun (40%) memisahkan "denyut mulai"
 *      dari "denyut selesai". Satu ambang saja menghasilkan belasan
 *      pemicu per denyut dari riak di sekitar ambang.
 *
 *   4. MAKSIMUM LOKAL + INTERPOLASI PARABOLA
 *      Puncak diambil sebagai maksimum lokal TERBESAR di dalam eksursi,
 *      lalu diperhalus ke resolusi sub-sampel. Di 200 Hz, kuantisasi
 *      5 ms saja sudah bernilai ~0,4 bpm di 60 bpm — interpolasi tiga
 *      titik menghapus hampir seluruh jitter itu tanpa biaya berarti.
 *
 *   5. GERBANG INTERVAL BERBASIS MEDIAN (+ perbaikan denyut terlewat)
 *      Interval di luar rentang fisiologis atau melenceng jauh dari median
 *      riwayat dibuang. Median, bukan rerata: satu interval sampah tidak
 *      boleh menggeser acuan yang menilainya sendiri.
 *
 *   6. SKOR KEYAKINAN = MINIMUM SUB-SKOR
 *      Sama seperti gerbang SQI di ../Firmware/src/sqi.cpp, dan alasannya
 *      sama: rata-rata menyamarkan outlier. Satu aspek rusak harus bisa
 *      menjatuhkan seluruh keputusan.
 *
 * BASIS WAKTU: seluruh perhitungan memakai CACAHAN SAMPEL, bukan millis().
 * Cacahan sampel dikunci tick FreeRTOS; millis() di dalam task yang juga
 * meladeni USB-CDC bisa tergeser beberapa milidetik, dan pergeseran itu
 * masuk langsung ke interval sebagai jitter BPM.
 *
 * File ini TIDAK menyentuh Arduino atau ADC — supaya bisa dikompilasi juga
 * di PC dan diuji terhadap rekaman CSV (lihat tools/bpm_csv.cpp).
 */

#include "bpm.h"
#include <math.h>
#include <string.h>

#ifndef M_PI
  #define M_PI 3.14159265358979323846
#endif
#define SQRT2_F 1.41421356237f

// =====================================================================
// 1. BIQUAD — bentuk langsung II tertranspos
// =====================================================================
/* Dipilih karena keadaannya hanya dua register per tingkat dan koefisiennya
 * dipakai apa adanya (tanpa penskalaan ulang), jadi mudah dibandingkan
 * dengan koefisien yang dipakai recorder validasimu. */
struct Biquad {
  float b0, b1, b2, a1, a2;
  float z1, z2;

  inline float process(float x) {
    const float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
  inline void clear() { z1 = 0.0f; z2 = 0.0f; }
};

/* Butterworth orde-2 lewat prewarp tan (transformasi bilinear).
 *
 * Koefisien DIHITUNG, tidak ditempel: laju sampel adalah parameter, dan
 * koefisien mati yang didesain untuk 200 Hz akan menggeser pita lolosnya
 * secara diam-diam kalau PPG_FS_HZ diubah — filter tetap jalan, hasilnya
 * saja yang salah. Itu kelas bug yang tidak menghasilkan pesan error.
 *
 * Diverifikasi: pada fs = 200 Hz kedua fungsi ini menghasilkan koefisien
 * yang sama dengan yang dipakai .claude/programoptimasi/
 * PPG_SEN0203_recorder_raw_pwa_60s.ino (HP 0,48 Hz & LP 5 Hz), jadi
 * jalur sinyalnya identik dengan rekaman yang sudah kamu validasi. */
static void designHighpass(Biquad& f, float fc, float fs) {
  const float k = tanf((float)M_PI * fc / fs);
  const float n = 1.0f / (1.0f + SQRT2_F * k + k * k);
  f.b0 =  n;
  f.b1 = -2.0f * n;
  f.b2 =  n;
  f.a1 =  2.0f * (k * k - 1.0f) * n;
  f.a2 = (1.0f - SQRT2_F * k + k * k) * n;
  f.clear();
}

static void designLowpass(Biquad& f, float fc, float fs) {
  const float k = tanf((float)M_PI * fc / fs);
  const float n = 1.0f / (1.0f + SQRT2_F * k + k * k);
  f.b0 = k * k * n;
  f.b1 = 2.0f * f.b0;
  f.b2 = f.b0;
  f.a1 =  2.0f * (k * k - 1.0f) * n;
  f.a2 = (1.0f - SQRT2_F * k + k * k) * n;
  f.clear();
}

// =====================================================================
// 2. SUB-SKOR (bentuknya disamakan dengan ../Firmware/src/sqi.cpp)
// =====================================================================
// 100 penuh di dalam [lo..hi], meluruh linear ke 0 menuju floor/ceil.
// Untuk besaran yang punya zona nyaman di tengah — perfusi: terlalu rendah
// berarti tidak ada denyut, terlalu tinggi hampir pasti gerakan.
static uint8_t bandScore(float v, float floorV, float lo, float hi, float ceilV) {
  if (v <= floorV || v >= ceilV) return 0;
  if (v >= lo && v <= hi)        return 100;
  if (v < lo)  return (uint8_t)(100.0f * (v - floorV) / (lo - floorV));
  return (uint8_t)(100.0f * (ceilV - v) / (ceilV - hi));
}

// "Makin kecil makin baik": 100 sampai good, meluruh ke 0 di maxV.
static uint8_t decayScore(float v, float good, float maxV) {
  if (v <= good) return 100;
  if (v >= maxV) return 0;
  return (uint8_t)(100.0f - 100.0f * (v - good) / (maxV - good));
}

static inline uint8_t minU8(uint8_t a, uint8_t b) { return a < b ? a : b; }

// =====================================================================
// 3. KEADAAN MESIN
// =====================================================================
struct Engine {
  // --- tetap sejak bpmInit ---
  float    fs;
  float    msPerSample;
  Biquad   hp, lp;
  uint32_t settleN;        // sampel yang dibuang di awal (transien filter)
  uint32_t refractN;       // blanking antar puncak, dalam sampel
  uint32_t excMaxN;        // panjang eksursi maksimum, dalam sampel
  uint32_t contactHoldN;   // lama kondisi buruk sebelum status jatuh
  uint32_t clipWinN;       // panjang jendela cacah clipping (= 1 detik)
  float    dcAlpha;        // one-pole baseline
  float    envDecay;       // peluruhan pelacak amplitudo per sampel
  float    ibiMinMs, ibiMaxMs;

  // --- berjalan ---
  uint32_t n;              // indeks sampel, naik terus
  bool     seeded;
  float    dc;
  float    envHi, envLo;
  float    s1, s2;         // x[n-2], x[n-1] — jendela uji maksimum lokal

  // eksursi yang sedang berjalan
  bool     inExc;
  uint32_t excStart;
  bool     haveMax;
  float    maxVal, maxPrev, maxNext;
  uint32_t maxIdx;

  // acuan denyut sebelumnya
  bool     havePrev;
  uint32_t prevIdx;
  float    prevFrac;
  uint32_t lastPeakIdx;

  // riwayat interval (ring)
  float    ibi[BPM_IBI_HIST];
  uint8_t  ibiN, ibiW;
  uint8_t  rejectRun;

  // statistik riwayat — dihitung ulang HANYA saat riwayat berubah
  float    med, sdnn, stabPermil;

  // clipping per jendela 1 detik
  uint32_t clipTick;
  uint16_t clipCur, clipPrev;

  // gerbang kontak
  uint32_t badRun;
  bool     contactLost;

  // nilai yang dilaporkan
  float    bpmDisp, bpmInst;
  uint32_t lastGoodIdx;
  bool     haveGood;
  bool     emaStale;       // riwayat baru dibuang -> jangan di-EMA dari nilai lama

  uint32_t beats, rejects, interp, resyncs;
};

static Engine e;
static BpmOut s_last;   // keadaan terakhir, untuk bpmSnapshot() dari task lain

// ---------------------------------------------------------------------
// Riwayat interval
// ---------------------------------------------------------------------
/* Setiap jalur yang membuang riwayat juga MELUCUTI acuan EMA. Alasannya:
 * riwayat dibuang justru karena nilai lama sudah terbukti tidak berlaku
 * (kontak hilang, atau laju berubah terlalu jauh untuk gerbang median). Kalau
 * EMA tetap merayap dari angka lama, kunci baru butuh ~8 denyut tambahan
 * hanya untuk melupakan nilai yang sudah kita nyatakan salah. */
static void histClear() {
  e.ibiN = 0;
  e.ibiW = 0;
  e.rejectRun = 0;
  e.med = e.sdnn = e.stabPermil = 0.0f;
  e.emaStale = true;
}

/* Median lewat penyisipan langsung. n <= 8, jadi O(n^2) di sini lebih murah
 * daripada quickselect — dan hasilnya bisa dibaca sekali lihat. */
static void histStats() {
  const uint8_t n = e.ibiN;
  if (!n) { e.med = e.sdnn = e.stabPermil = 0.0f; return; }

  float t[BPM_IBI_HIST];
  for (uint8_t i = 0; i < n; i++) {
    float v = e.ibi[i];
    uint8_t j = i;
    while (j && t[j - 1] > v) { t[j] = t[j - 1]; j--; }
    t[j] = v;
  }
  e.med = (n & 1) ? t[n / 2] : 0.5f * (t[n / 2 - 1] + t[n / 2]);

  // SDNN: simpangan baku interval — telemetri HRV kasar, bukan penilai mutu.
  float sum = 0.0f, dev = 0.0f;
  for (uint8_t i = 0; i < n; i++) sum += e.ibi[i];
  const float mean = sum / n;
  for (uint8_t i = 0; i < n; i++) {
    const float d = e.ibi[i] - mean;
    dev += d * d;
  }
  e.sdnn = sqrtf(dev / n);

  /* Kestabilan: rerata |ibi - MEDIAN| / median. Sengaja terhadap median,
   * bukan mean — pada riwayat yang tercemar satu outlier, mean sudah
   * tergeser sehingga simpangan terhadapnya justru terlihat kecil. */
  float ad = 0.0f;
  for (uint8_t i = 0; i < n; i++) ad += fabsf(e.ibi[i] - e.med);
  e.stabPermil = e.med > 0.0f ? (ad / n) * 1000.0f / e.med : 1000.0f;
}

static void histPush(float ibi) {
  e.ibi[e.ibiW] = ibi;
  e.ibiW = (uint8_t)((e.ibiW + 1) % BPM_IBI_HIST);
  if (e.ibiN < BPM_IBI_HIST) e.ibiN++;
  histStats();
}

// =====================================================================
// 4. API
// =====================================================================
void bpmInit(float fs) {
  memset(&e, 0, sizeof(e));
  memset(&s_last, 0, sizeof(s_last));
  e.fs          = fs;
  e.msPerSample = 1000.0f / fs;

  designHighpass(e.hp, BPM_HP_HZ, fs);
  designLowpass (e.lp, BPM_LP_HZ, fs);

  e.settleN      = (uint32_t)(BPM_SETTLE_MS      * fs / 1000.0f);
  e.refractN     = (uint32_t)(BPM_REFRACT_MS     * fs / 1000.0f);
  e.excMaxN      = (uint32_t)(BPM_EXC_MAX_MS     * fs / 1000.0f);
  e.contactHoldN = (uint32_t)(BPM_CONTACT_HOLD_MS * fs / 1000.0f);
  e.clipWinN     = (uint32_t)fs;

  // One-pole: alpha = 1 - exp(-2*pi*fc/fs). Bentuk eksak, bukan hampiran
  // 2*pi*fc/fs — di fc rendah keduanya nyaris sama, tapi yang eksak tidak
  // pernah melewati 1 kalau suatu saat fc dinaikkan.
  e.dcAlpha  = 1.0f - expf(-2.0f * (float)M_PI * BPM_DC_HZ / fs);
  e.envDecay = BPM_ENV_DECAY_PER_S / fs;

  e.ibiMinMs = 60000.0f / BPM_MAX;
  e.ibiMaxMs = 60000.0f / BPM_MIN;

  histClear();
}

void bpmReset() {
  e.hp.clear();
  e.lp.clear();
  e.n = 0;
  e.seeded = false;
  e.dc = e.envHi = e.envLo = 0.0f;
  e.s1 = e.s2 = 0.0f;
  e.inExc = false;
  e.haveMax = false;
  e.havePrev = false;
  e.lastPeakIdx = 0;
  e.clipTick = 0;
  e.clipCur = e.clipPrev = 0;
  e.badRun = 0;
  e.contactLost = false;
  e.bpmDisp = e.bpmInst = 0.0f;
  e.haveGood = false;
  histClear();

  memset(&s_last, 0, sizeof(s_last));
  s_last.status = BPM_SETTLING;
}

// ---------------------------------------------------------------------
// Satu sampel
// ---------------------------------------------------------------------
void bpmPush(uint16_t raw, BpmOut* out) {
  const uint32_t idx = e.n++;
  bool beatNow = false;

  // --- 0. clipping: cacah per jendela 1 detik ---------------------------
  if (raw >= PPG_SAT_LEVEL || raw <= PPG_FLOOR_LEVEL) e.clipCur++;
  if (++e.clipTick >= e.clipWinN) {
    e.clipTick = 0;
    e.clipPrev = e.clipCur;
    e.clipCur  = 0;
  }

  const float x = (float)raw;

  // --- 1. baseline lambat (DC) ------------------------------------------
  // Disemai dengan sampel pertama: kalau dimulai dari 0, one-pole 0,1 Hz
  // butuh belasan detik untuk memanjat ke level nyata, dan selama itu
  // indeks perfusi (AC/DC) mengarang angka besar.
  if (!e.seeded) { e.dc = x; e.seeded = true; }
  else           e.dc += e.dcAlpha * (x - e.dc);

  // --- 1b. band-pass 0,5-5 Hz -------------------------------------------
  const float s = e.lp.process(e.hp.process(x));

  // --- 2. pelacak amplitudo: serangan seketika, peluruhan lambat --------
  const float ampPrev = e.envHi - e.envLo;
  if (s > e.envHi) e.envHi = s; else e.envHi -= ampPrev * e.envDecay;
  if (s < e.envLo) e.envLo = s; else e.envLo += ampPrev * e.envDecay;
  if (e.envHi < e.envLo) {                       // sinyal hilang total
    const float mid = 0.5f * (e.envHi + e.envLo);
    e.envHi = e.envLo = mid;
  }
  const float amp   = e.envHi - e.envLo;
  const float thrHi = e.envLo + BPM_THR_HI_FRAC * amp;
  const float thrLo = e.envLo + BPM_THR_LO_FRAC * amp;

  // --- gerbang kontak ---------------------------------------------------
  const float piPermil = (e.dc > 1.0f) ? (amp * 1000.0f / e.dc) : 0.0f;
  const bool  settled  = (idx >= e.settleN);
  const bool  bad      = (e.dc < BPM_DC_MIN) || (e.dc > BPM_DC_MAX) ||
                         (amp < BPM_AC_MIN_LSB) ||
                         (piPermil < BPM_PI_MIN_PERMIL);

  if (bad) {
    /* Riwayat dibuang TEPAT pada transisi, bukan tiap sampel: sekali dibuang,
     * yang tersisa hanya menunggu sinyal kembali. Membuangnya berulang kali
     * juga akan menahan status di NO_CONTACT satu sampel lebih lama setiap
     * kali sinyal baru mulai pulih. */
    if (++e.badRun == e.contactHoldN) {
      e.contactLost = true;
      e.inExc  = false;
      e.havePrev = false;
      histClear();
    }
  } else {
    e.badRun = 0;
    e.contactLost = false;
  }

  // --- 3+4. eksursi berhisteresis -> maksimum lokal -> puncak sub-sampel -
  if (!e.inExc) {
    /* Mulai eksursi hanya kalau: sudah lewat transien, amplitudo memang ada
     * (kalau tidak, ambang yang meluruh akan menempel ke lantai derau dan
     * "denyut" hantu muncul dari riak ADC), dan blanking sudah lewat. */
    if (settled && !e.contactLost && amp >= BPM_AC_MIN_LSB && s >= thrHi &&
        (!e.havePrev || (idx - e.lastPeakIdx) >= e.refractN)) {
      e.inExc    = true;
      e.excStart = idx;
      e.haveMax  = false;
      e.maxVal   = 0.0f;
    }
  } else {
    /* Uji maksimum lokal pada x[n-1] — butuh tetangga KANANNYA, jadi
     * keputusan memang harus tertunda satu sampel. Yang diambil adalah
     * maksimum lokal TERBESAR sepanjang eksursi, bukan yang pertama:
     * pada denyut beramplitudo tinggi, riak kecil di kaki upstroke bisa
     * membentuk maksimum lokal lebih dulu. */
    if (e.s2 > e.s1 && e.s2 >= s && (!e.haveMax || e.s2 > e.maxVal)) {
      e.maxVal  = e.s2;
      e.maxIdx  = idx - 1;
      e.maxPrev = e.s1;
      e.maxNext = s;
      e.haveMax = true;
    }

    const bool tooLong = (idx - e.excStart) > e.excMaxN;
    if (s < thrLo || tooLong) {
      /* Eksursi kelewat panjang = geseran baseline atau gerakan, BUKAN
       * denyut (fase sistolik < 400 ms bahkan pada bradikardia). Dibuang
       * utuh: tidak ada puncak, dan acuan interval tidak digeser. */
      if (e.haveMax && !tooLong) {
        // Interpolasi parabola tiga titik -> posisi puncak sub-sampel.
        // Penyebut negatif untuk maksimum sejati; kalau tidak, jangan
        // digeser sama sekali.
        float frac = 0.0f;
        const float den = e.maxPrev - 2.0f * e.maxVal + e.maxNext;
        if (den < -1e-6f) {
          frac = 0.5f * (e.maxPrev - e.maxNext) / den;
          if (frac >  0.5f) frac =  0.5f;
          if (frac < -0.5f) frac = -0.5f;
        }

        if (!e.havePrev) {
          beatNow = true;                       // puncak pertama: acuan saja
        } else {
          const float ibi = ((float)(e.maxIdx - e.prevIdx) + (frac - e.prevFrac))
                            * e.msPerSample;

          // --- 5. gerbang interval berbasis median ---------------------
          bool accepted = false;
          if (ibi >= e.ibiMinMs && ibi <= e.ibiMaxMs) {
            if (e.ibiN < 3) {                   // belum ada acuan tepercaya
              histPush(ibi);
              accepted = true;
            } else {
              const float tol = e.med * (BPM_IBI_DEV_PCT / 100.0f);
              if (fabsf(ibi - e.med) <= tol) {
                histPush(ibi);
                accepted = true;
              }
#if BPM_MISSED_FIX
              /* Denyut TERLEWAT: intervalnya ~2x median. Kalau separuhnya
               * cocok dengan median, pecah jadi dua dan masukkan keduanya.
               * Ini interpolasi, bukan pengukuran — karena itu dicacah
               * terpisah sebagai "interp" supaya bisa diaudit.
               *
               * Hanya SATU denyut terlewat yang dipulihkan. Dua kali lewat
               * berurutan berarti kontaknya memang buruk, dan menebak dua
               * denyut dari satu interval sudah lebih banyak mengarang
               * daripada mengukur. */
              else if (fabsf(ibi * 0.5f - e.med) <= e.med * (BPM_MISSED_TOL_PCT / 100.0f)) {
                histPush(ibi * 0.5f);
                histPush(ibi * 0.5f);
                e.interp++;
                accepted = true;
              }
#endif
            }
          }

          if (accepted) {
            e.beats++;
            e.rejectRun = 0;
            beatNow = true;
          } else {
            e.rejects++;
            /* Penolakan BERURUTAN artinya acuannya sendiri yang sudah
             * basi — laju jantung berubah cepat (mulai bergerak, berdiri)
             * atau sensor bergeser. Tanpa jalur re-sync ini, gerbang median
             * akan menolak laju baru selamanya: detektor mengunci dirinya. */
            if (++e.rejectRun >= BPM_RESYNC_REJECTS) {
              histClear();
              e.resyncs++;
            }
          }
        }

        /* Acuan SELALU maju ke puncak terakhir yang terdeteksi, diterima
         * atau tidak. Kalau acuannya dibiarkan basi, satu interval yang
         * ditolak membuat SEMUA interval sesudahnya diukur dari titik yang
         * salah — dan semuanya ikut tertolak. */
        e.prevIdx     = e.maxIdx;
        e.prevFrac    = frac;
        e.lastPeakIdx = e.maxIdx;
        e.havePrev    = true;
      }
      e.inExc = false;
    }
  }

  e.s1 = e.s2;
  e.s2 = s;

  // --- 6. skor keyakinan = MINIMUM sub-skor -----------------------------
  const uint8_t sFill = (uint8_t)((uint32_t)e.ibiN * 100u / BPM_IBI_HIST);
  const uint8_t sStab = e.ibiN ? decayScore(e.stabPermil, BPM_STAB_GOOD_PERMIL,
                                            BPM_STAB_MAX_PERMIL) : 0;
  const uint8_t sPerf = bandScore(piPermil, BPM_PI_MIN_PERMIL, BPM_PI_GOOD_LO,
                                  BPM_PI_GOOD_HI, BPM_PI_MAX_PERMIL);
  const uint8_t sClip = (e.clipPrev == 0) ? 100
                      : (e.clipPrev <= BPM_CLIP_MAX_N ? 50 : 0);

  const uint8_t conf = minU8(minU8(sFill, sStab), minU8(sPerf, sClip));

  // --- nilai yang dilaporkan --------------------------------------------
  if (e.ibiN >= BPM_MIN_BEATS && e.med > 0.0f) {
    e.bpmInst = 60000.0f / e.med;
    if (beatNow) {                    // diperbarui per denyut, bukan per sampel
      /* Menyentak (bukan meng-EMA) hanya sah karena bpmInst sudah median dari
       * BPM_MIN_BEATS interval yang lolos gerbang — jadi yang disentak ke
       * layar tetap nilai yang tahan outlier, bukan satu interval mentah. */
      if (!e.haveGood || e.emaStale) e.bpmDisp = e.bpmInst;
      else e.bpmDisp += BPM_EMA_ALPHA * (e.bpmInst - e.bpmDisp);
      e.emaStale     = false;
      e.haveGood     = true;
      e.lastGoodIdx  = idx;
    }
  }

  const uint32_t ageMs = e.haveGood
      ? (uint32_t)((idx - e.lastGoodIdx) * e.msPerSample) : 0;
  if (e.haveGood && ageMs > BPM_HOLD_MS) {
    /* Angka basi lebih berbahaya daripada tidak ada angka: di layar,
     * "72" yang membeku terlihat persis seperti pengukuran hidup. */
    e.haveGood = false;
    e.bpmDisp  = 0.0f;
    e.bpmInst  = 0.0f;
  }

  /* Keadaan disalin ke s_last SETIAP sampel, bukan hanya saat `out` diminta:
   * bpmSnapshot() dipanggil dari task lain (loop() yang mencetak laporan) dan
   * harus punya sesuatu yang utuh untuk dibaca tanpa perlu ikut memasukkan
   * sampel. */
  s_last.beat       = beatNow;
  s_last.conf       = conf;
  s_last.bpm        = e.haveGood ? e.bpmDisp : 0.0f;
  s_last.bpm_inst   = e.haveGood ? e.bpmInst : 0.0f;
  s_last.ibi_med_ms = e.med;
  s_last.sdnn_ms    = e.sdnn;
  s_last.bpm_age_ms = ageMs;
  s_last.ac         = amp;
  s_last.dc         = e.dc;
  s_last.pi_permil  = (uint16_t)(piPermil > 65535.0f ? 65535.0f : piPermil);
  s_last.clip_n     = e.clipPrev;
  s_last.ac_now     = s;
  s_last.thr_hi     = thrHi;
  s_last.thr_lo     = thrLo;
  s_last.beats      = e.beats;
  s_last.rejects    = e.rejects;
  s_last.interp     = e.interp;
  s_last.resyncs    = e.resyncs;

  if      (!settled)               s_last.status = BPM_SETTLING;
  else if (e.contactLost)          s_last.status = BPM_NO_CONTACT;
  else if (e.ibiN < BPM_MIN_BEATS) s_last.status = BPM_SEARCHING;
  else if (conf < BPM_MIN_CONF)    s_last.status = BPM_NOISY;
  else                             s_last.status = BPM_LOCKED;

  if (out) *out = s_last;
}

void bpmSnapshot(BpmOut* out) {
  if (!out) return;
  *out = s_last;
  /* beat adalah PERISTIWA satu sampel, bukan keadaan. Kalau ikut disalin,
   * pembaca laporan akan melihat denyut yang sama berkali-kali dan LED bisa
   * dikedipkan dua kali untuk satu detak. */
  out->beat = false;
}

const char* bpmStatusName(BpmStatus s) {
  switch (s) {
    case BPM_SETTLING:   return "SETTLING";
    case BPM_NO_CONTACT: return "NO_CONTACT";
    case BPM_SEARCHING:  return "SEARCHING";
    case BPM_NOISY:      return "NOISY";
    case BPM_LOCKED:     return "LOCKED";
  }
  return "?";
}
