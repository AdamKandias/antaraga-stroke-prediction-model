/**
 * ANTARAGA BPM - penguji algoritma di PC (bukan bagian firmware)
 * =====================================================================
 * Menjalankan src/bpm.cpp yang SAMA PERSIS dengan yang berjalan di ESP32,
 * tapi sampelnya datang dari file, bukan dari ADC. Gunanya satu: mengukur
 * ketepatan algoritma terhadap sinyal yang laju denyutnya SUDAH DIKETAHUI.
 * Serial monitor tidak bisa memberi tahu apakah "72 bpm" itu benar; uji ini
 * bisa.
 *
 * Dua mode:
 *
 *   1. SINTETIS - sinyal PPG buatan pada BPM yang diketahui, plus derau,
 *      baseline wander, dan (opsional) denyut yang sengaja dihilangkan.
 *      Ini regression test: jalankan setiap kali kamu menyentuh bpm.cpp.
 *
 *   2. CSV - rekaman nyata dari
 *      ../Firmware/.claude/programoptimasi/PPG_SEN0203_recorder_raw_pwa_60s.ino
 *      (kolom: t_ms,adc_raw,ppg_bandpass). Kolom yang dipakai adalah
 *      adc_raw - MENTAH, karena bpm.cpp memfilter sendiri.
 *
 * Bangun & jalankan (PlatformIO):
 *      pio run -e native -t exec                       # uji sintetis
 *      .pio/build/native/program rekaman.csv           # rekaman nyata
 *
 * Atau tanpa PlatformIO, dari folder FirmwareBPM:
 *      g++ -std=c++11 -O2 -Iinclude src/bpm.cpp tools/bpm_csv.cpp -o bpmtest
 */

#include "bpm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const float FS = (float)PPG_FS_HZ;

// =====================================================================
// Pembangkit PPG sintetis
// ---------------------------------------------------------------------
/* Bentuk gelombangnya SENGAJA tidak sinus. Sinus akan membuat detektor
 * terlihat sempurna secara palsu: yang sulit pada PPG nyata justru
 * ketidaksimetrisan (upstroke cepat, decay lambat) dan dicrotic notch -
 * notch itulah kandidat denyut-palsu utama, jadi ia harus ada di sini.
 *
 * Model: gelombang sistolik + notch diastolik pada ~35% siklus, ditumpuk
 * di atas baseline melayang (napas ~0,25 Hz) plus derau putih.  */
static float ppgWave(float phase)
{                                                                          // phase 0..1 dalam satu denyut
  const float sys = expf(-powf((phase - 0.16f) / 0.075f, 2.0f));           // puncak sistolik
  const float notch = 0.32f * expf(-powf((phase - 0.36f) / 0.060f, 2.0f)); // dicrotic notch
  const float dia = 0.18f * expf(-powf((phase - 0.52f) / 0.170f, 2.0f));   // gelombang diastolik
  return sys + notch + dia;
}

static unsigned long rngState = 12345u;
static float noise()
{ // seragam -1..1, deterministik
  rngState = rngState * 1103515245u + 12345u;
  return ((float)((rngState >> 16) & 0x7FFF) / 16383.5f) - 1.0f;
}

struct SynthCfg
{
  float bpm;
  float seconds;
  float dcLevel; // LSB
  float acAmp;   // LSB puncak-ke-palung
  float noiseLsb;
  float wanderLsb;
  int dropEveryN; // 0 = tidak ada; N = hilangkan denyut ke-N (uji denyut terlewat)
  const char *name;
};

static void runSynth(const SynthCfg &c)
{
  bpmInit(FS);
  bpmReset();

  const uint32_t n = (uint32_t)(c.seconds * FS);
  const float beatSec = 60.0f / c.bpm;
  uint32_t beatsGen = 0;
  float phase = 0.0f;

  BpmOut o;
  memset(&o, 0, sizeof(o));

  // Statistik hanya dikumpulkan setelah mesin mengunci, supaya jendela
  // settling tidak mencemari angka ketepatan.
  double sumBpm = 0.0, maxErr = 0.0;
  uint32_t nLocked = 0, nDetected = 0;

  for (uint32_t i = 0; i < n; i++)
  {
    const float t = i / FS;

    phase += 1.0f / (beatSec * FS);
    if (phase >= 1.0f)
    {
      phase -= 1.0f;
      beatsGen++;
    }

    // Denyut yang sengaja dihilangkan: amplitudonya ditekan, bukan dihapus,
    // supaya baseline tetap bersinambung seperti kontak yang melemah sekejap.
    float gain = 1.0f;
    if (c.dropEveryN > 0 && ((beatsGen + 1) % (uint32_t)c.dropEveryN) == 0)
      gain = 0.10f;

    const float wander = c.wanderLsb * sinf(2.0f * (float)M_PI * 0.25f * t);
    float v = c.dcLevel + wander + gain * c.acAmp * ppgWave(phase) + c.noiseLsb * noise();

    if (v < 0.0f)
      v = 0.0f;
    if (v > (float)PPG_ADC_MAX)
      v = (float)PPG_ADC_MAX;

    bpmPush((uint16_t)(v + 0.5f), &o);
    if (o.beat)
      nDetected++;

    if (o.status == BPM_LOCKED)
    {
      nLocked++;
      sumBpm += o.bpm;
      const double err = fabs((double)o.bpm - (double)c.bpm);
      if (err > maxErr)
        maxErr = err;
    }
  }

  const double avg = nLocked ? sumBpm / nLocked : 0.0;
  const double lockPc = 100.0 * nLocked / n;
  const bool ok = nLocked > 0 && fabs(avg - c.bpm) <= 1.5 && maxErr <= 5.0;

  printf("%-28s target=%6.1f  rerata=%6.2f  galat_maks=%5.2f  "
         "kunci=%5.1f%%  denyut=%u/%u  tolak=%u interp=%u resync=%u  %s\n",
         c.name, c.bpm, avg, maxErr, lockPc,
         (unsigned)nDetected, (unsigned)beatsGen,
         (unsigned)o.rejects, (unsigned)o.interp, (unsigned)o.resyncs,
         ok ? "OK" : "GAGAL");
}

/* Uji LONCATAN laju: 72 -> 130 bpm seketika di pertengahan rekaman.
 *
 * Ini yang menguji jalur re-sync. Gerbang median menolak apa pun yang
 * melenceng > BPM_IBI_DEV_PCT dari riwayat, jadi laju baru MULA-MULA memang
 * ditolak - itu benar. Yang diuji di sini: apakah detektor berhasil membuang
 * acuan basinya dan mengunci laju baru, bukan menolaknya selamanya.
 *
 * Loncatan seketika 58 bpm lebih kejam daripada apa pun yang bisa dilakukan
 * jantung sungguhan; kalau yang ini pulih, transisi nyata pasti pulih. */
static void runStep(float bpm1, float bpm2, float seconds)
{
  bpmInit(FS);
  bpmReset();

  const uint32_t n = (uint32_t)(seconds * FS);
  const uint32_t nStep = n / 2;
  float phase = 0.0f;

  BpmOut o;
  memset(&o, 0, sizeof(o));
  uint32_t relockIdx = 0;
  bool relocked = false;

  for (uint32_t i = 0; i < n; i++)
  {
    const float t = i / FS;
    const float bpm = (i < nStep) ? bpm1 : bpm2;
    phase += 1.0f / ((60.0f / bpm) * FS);
    if (phase >= 1.0f)
      phase -= 1.0f;

    const float v = 1800.0f + 60.0f * sinf(2.0f * (float)M_PI * 0.25f * t) + 200.0f * ppgWave(phase) + 4.0f * noise();
    bpmPush((uint16_t)(v + 0.5f), &o);

    // Kunci ulang = LOCKED lagi dan angkanya sudah dalam 3 bpm dari laju baru.
    if (i > nStep && !relocked && o.status == BPM_LOCKED &&
        fabsf(o.bpm - bpm2) <= 3.0f)
    {
      relocked = true;
      relockIdx = i;
    }
  }

  const float relockS = relocked ? (relockIdx - nStep) / FS : -1.0f;
  printf("\n%-28s %.0f->%.0f bpm: kunci ulang %.1f s  (akhir %.1f bpm, "
         "tolak=%u resync=%u)  %s\n",
         "loncatan laju", bpm1, bpm2, relockS, o.bpm,
         (unsigned)o.rejects, (unsigned)o.resyncs,
         (relocked && relockS <= 10.0f) ? "OK" : "GAGAL");
}

// =====================================================================
// Pembaca CSV - kolom kedua (adc_raw) dari recorder
// =====================================================================
static int runCsv(const char *path)
{
  FILE *f = fopen(path, "r");
  if (!f)
  {
    fprintf(stderr, "tidak bisa membuka %s\n", path);
    return 1;
  }

  bpmInit(FS);
  bpmReset();

  char line[512];
  BpmOut o;
  memset(&o, 0, sizeof(o));
  uint32_t nS = 0;
  double sumBpm = 0.0;
  uint32_t nLocked = 0;

  printf("t_s,raw,ac,bpm,bpm_inst,conf,status,beat\n");
  while (fgets(line, sizeof(line), f))
  {
    if (line[0] == '#' || line[0] == '\n' || line[0] == '\r')
      continue;
    if ((line[0] < '0' || line[0] > '9') && line[0] != '-')
      continue; // baris header

    // t_ms,adc_raw,...  -> ambil kolom kedua
    const char *c1 = strchr(line, ',');
    if (!c1)
      continue;
    const long raw = strtol(c1 + 1, nullptr, 10);
    if (raw < 0 || raw > PPG_ADC_MAX)
      continue;

    bpmPush((uint16_t)raw, &o);
    printf("%.3f,%ld,%.2f,%.2f,%.2f,%u,%s,%d\n",
           nS / FS, raw, o.ac_now, o.bpm, o.bpm_inst, (unsigned)o.conf,
           bpmStatusName(o.status), o.beat ? 1 : 0);
    nS++;
    if (o.status == BPM_LOCKED)
    {
      nLocked++;
      sumBpm += o.bpm;
    }
  }
  fclose(f);

  fprintf(stderr,
          "\n# %u sampel (%.1f s @ %.0f Hz)\n"
          "# BPM rerata saat LOCKED : %.2f  (%.1f%% durasi terkunci)\n"
          "# denyut=%u tolak=%u interp=%u resync=%u | ac=%.0f dc=%.0f pi=%u permil\n",
          (unsigned)nS, nS / FS, FS,
          nLocked ? sumBpm / nLocked : 0.0, nS ? 100.0 * nLocked / nS : 0.0,
          (unsigned)o.beats, (unsigned)o.rejects, (unsigned)o.interp,
          (unsigned)o.resyncs, o.ac, o.dc, (unsigned)o.pi_permil);
  return 0;
}

// =====================================================================
int main(int argc, char **argv)
{
  if (argc > 1)
    return runCsv(argv[1]);

  printf("ANTARAGA BPM - uji sintetis  (fs=%.0f Hz, band-pass %.1f-%.1f Hz)\n",
         FS, (double)BPM_HP_HZ, (double)BPM_LP_HZ);
  printf("Lulus = |rerata - target| <= 1,5 bpm DAN galat maksimum <= 5 bpm.\n\n");

  // Kolom acAmp/noiseLsb dalam LSB ADC 12-bit. AC 200 LSB pada DC 1800
  // setara perfusi ~111 per-mil - khas ujung jari pada SEN0203/SON1303.
  const SynthCfg tests[] = {
      // nama                       bpm  dtk    dc    ac  derau  wander  drop
      {45.0f, 30.0f, 1800.0f, 220.0f, 4.0f, 60.0f, 0, "bradikardia 45 bpm"},
      {60.0f, 30.0f, 1800.0f, 220.0f, 4.0f, 60.0f, 0, "istirahat 60 bpm"},
      {75.0f, 30.0f, 1800.0f, 200.0f, 4.0f, 60.0f, 0, "normal 75 bpm"},
      {100.0f, 30.0f, 1800.0f, 180.0f, 4.0f, 60.0f, 0, "jalan cepat 100 bpm"},
      {150.0f, 30.0f, 1800.0f, 150.0f, 4.0f, 60.0f, 0, "olahraga 150 bpm"},
      {190.0f, 30.0f, 1800.0f, 140.0f, 4.0f, 60.0f, 0, "maksimal 190 bpm"},
      {72.0f, 30.0f, 1800.0f, 40.0f, 4.0f, 60.0f, 0, "sinyal lemah (ac 40)"},
      {72.0f, 30.0f, 1800.0f, 200.0f, 25.0f, 60.0f, 0, "derau tinggi (25 LSB)"},
      {72.0f, 30.0f, 1800.0f, 200.0f, 4.0f, 400.0f, 0, "baseline melayang kuat"},
      {72.0f, 30.0f, 1800.0f, 200.0f, 4.0f, 60.0f, 5, "1 dari 5 denyut hilang"},
      {72.0f, 30.0f, 600.0f, 200.0f, 4.0f, 60.0f, 0, "DC rendah (600 LSB)"},
      {72.0f, 30.0f, 3400.0f, 200.0f, 4.0f, 60.0f, 0, "DC tinggi (3400 LSB)"},
  };

  for (unsigned i = 0; i < sizeof(tests) / sizeof(tests[0]); i++)
    runSynth(tests[i]);

  runStep(72.0f, 130.0f, 40.0f);

  // Kasus kontak: sinyal datar HARUS menghasilkan NO_CONTACT dan BPM = 0.
  // Ini pengujian yang paling sering dilewatkan - detektor yang mengarang
  // 70 bpm dari derau ADC saat sensor dilepas jauh lebih berbahaya daripada
  // detektor yang sesekali kehilangan kunci.
  {
    bpmInit(FS);
    bpmReset();
    BpmOut o;
    memset(&o, 0, sizeof(o));
    for (uint32_t i = 0; i < (uint32_t)(15 * FS); i++)
      bpmPush((uint16_t)(1800.0f + 3.0f * noise() + 0.5f), &o);
    printf("\n%-28s status=%-11s bpm=%.1f denyut=%u  %s\n",
           "sensor dilepas (datar)", bpmStatusName(o.status), o.bpm,
           (unsigned)o.beats,
           (o.status == BPM_NO_CONTACT && o.bpm == 0.0f) ? "OK" : "GAGAL");
  }
  return 0;
}
