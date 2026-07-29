/**
 * ANTARAGA BPM — FIRMWARE UTAMA (hitung denyut di perangkat)
 * =====================================================================
 * Board   : Seeed XIAO ESP32-S3
 * Sensor  : SON1303 saja (PPG analog di A1/GPIO2)
 * Keluaran: BPM ke serial monitor + LED D10 berkedip per detak
 *
 * BEDANYA DENGAN ../Firmware
 * ---------------------------------------------------------------------
 * ../Firmware  : mencuplik, TIDAK memfilter, TIDAK menghitung BPM. Data
 *                mentah dikirim ke cloud; seluruh analisis di sisi server.
 * program ini  : mencuplik dengan front-end yang SAMA PERSIS, lalu
 *                menghitung BPM di tempat. Tanpa WiFi, tanpa cloud,
 *                tanpa MAX30102.
 *
 * Keduanya sengaja dipisah karena tujuannya bertolak belakang: analisis
 * morfologi (PWA/VPG/APG) butuh sinyal mentah yang tak tersentuh, sedangkan
 * mencari puncak butuh sinyal yang sudah dibersihkan. Menaruh keduanya di
 * satu firmware berarti salah satu harus dikompromikan.
 *
 * Karena front-end-nya identik, program ini juga berguna sebagai ACUAN:
 * BPM di sini bisa dibandingkan langsung dengan hasil hitungan cloud atas
 * batch dari firmware streaming. Selisihnya murni beda algoritma.
 *
 * ALGORITMA
 * ---------
 *   1. D2 di-LOW-kan -> P-MOSFET Q2 nyambung -> SON1303 dapat 3V3.
 *   2. Settle 1 detik: sampel dibuang (transien power-on op-amp sensor).
 *   3. CORE 1 (ppgTask): cuplik A1 pada 200 Hz, oversample 16x, tiap
 *      sampel masuk mesin BPM (src/bpm.cpp).
 *   4. CORE 1 (loop)   : LED berkedip per detak + baris [BPM ] tiap detik.
 *
 * PETA PIN (skematik ANTARAGA -> XIAO ESP32-S3)
 * ---------------------------------------------------------------------
 *   D1 / A1  GPIO2  SIG_PPG   <- keluaran analog SON1303 (J2)
 *   D2       GPIO3  SEN_EN    -> gate Q2 DMP2130L (P-MOS). LOW = sensor ON
 *   D10      GPIO9  LED       -> R6 10k -> LED J7. HIGH = nyala
 *
 * ARTI LED D10
 * ---------------------------------------------------------------------
 *   kedip sedang (250 ms) : settle / sensor tidak menempel
 *   kilat per detak       : sedang mengukur  <- kondisi normal
 */

#include "ppg.h"

// =====================================================================
// LED D10 — satu kilat per detak
// ---------------------------------------------------------------------
// Semua pola lewat LEDC (PWM), termasuk yang sekadar kedip. Alasannya sama
// dengan di ../Firmware/src/main.cpp: begitu sebuah pin ter-attach ke LEDC,
// digitalWrite() pada pin itu tidak lagi berpengaruh. Mencampur keduanya
// membuat salah satu pola mati diam-diam setelah pola lainnya sekali jalan.
// =====================================================================
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  #define LED_PWM_ATTACH()  ledcAttach(PIN_LED, LED_PWM_FREQ_HZ, LED_PWM_BITS)
  #define LED_PWM_WRITE(d)  ledcWrite(PIN_LED, (d))
#else                                     // core 2.x: API berbasis kanal
  #define LED_PWM_CH        0
  #define LED_PWM_ATTACH()  do { ledcSetup(LED_PWM_CH, LED_PWM_FREQ_HZ, LED_PWM_BITS); \
                                 ledcAttachPin(PIN_LED, LED_PWM_CH); } while (0)
  #define LED_PWM_WRITE(d)  ledcWrite(LED_PWM_CH, (d))
#endif

/* Kilat yang MELURUH, bukan nyala-padam. Kuadratik (bukan linear) supaya
 * terlihat seperti detak: mata menangkap kecerahan secara logaritmik, jadi
 * peluruhan linear justru tampak menggantung terang lalu mati mendadak. */
static void ledService(const BpmOut& o) {
  static uint32_t seenBeat  = 0;
  static uint32_t flashT0   = 0;
  static uint32_t blinkT0   = 0;
  static bool     blinkOn   = false;

  const uint32_t now = millis();

  const uint32_t seq = g_ppg.beat_seq;
  if (seq != seenBeat) { seenBeat = seq; flashT0 = now; }

#if BPM_LED_BEAT
  const bool measuring = (o.status == BPM_SEARCHING || o.status == BPM_NOISY ||
                          o.status == BPM_LOCKED);
  if (measuring) {
    const uint32_t dt = now - flashT0;
    if (dt < BPM_LED_FLASH_MS && flashT0) {
      const float k = 1.0f - (float)dt / (float)BPM_LED_FLASH_MS;
      LED_PWM_WRITE((uint32_t)(k * k * LED_DUTY_MAX));
    } else {
      LED_PWM_WRITE(0);
    }
    return;
  }
#else
  (void)flashT0; (void)o;
#endif

  // Belum menempel / belum settle: kedip sedang, sama seperti pola WARMUP
  // di firmware streaming supaya artinya tidak perlu dihafal dua kali.
  if (now - blinkT0 >= 250) {
    blinkT0 = now;
    blinkOn = !blinkOn;
  }
  LED_PWM_WRITE(blinkOn ? LED_DUTY_MAX : 0);
}

// =====================================================================
// Laporan
// =====================================================================
static void printBpm(const BpmOut& o) {
  char bpmTxt[12];
  if (o.status == BPM_LOCKED && o.bpm > 0.0f) snprintf(bpmTxt, sizeof(bpmTxt), "%5.1f", o.bpm);
  else if (o.bpm > 0.0f)                      snprintf(bpmTxt, sizeof(bpmTxt), "(%4.1f)", o.bpm);
  else                                        snprintf(bpmTxt, sizeof(bpmTxt), "   --");

  /* Angka dalam tanda kurung = nilai TERTAHAN: detektor masih memegang hasil
   * terakhir tapi status sudah bukan LOCKED. Dibedakan supaya tidak ada
   * pembaca yang salah menganggapnya pengukuran hidup — itu satu-satunya
   * cara salah baca yang benar-benar berbahaya di sini. */
  Serial.printf("[BPM ] %s bpm  conf %3u  %-10s | inst %5.1f | ibi %4.0f ms sdnn %3.0f\n",
                bpmTxt, (unsigned)o.conf, bpmStatusName(o.status),
                o.bpm_inst, o.ibi_med_ms, o.sdnn_ms);
  Serial.printf("       ac=%-6.0f dc=%-6.0f pi=%u permil clip=%u"
                " | denyut=%lu tolak=%lu interp=%lu resync=%lu\n",
                o.ac, o.dc, (unsigned)o.pi_permil, (unsigned)o.clip_n,
                (unsigned long)o.beats, (unsigned long)o.rejects,
                (unsigned long)o.interp, (unsigned long)o.resyncs);
}

static void printStats() {
  /* fs_ukur = laju cuplik yang BENAR-BENAR tercapai. Ini bukan hiasan:
   * seluruh basis waktu mesin BPM menganggap tiap sampel berjarak tepat
   * 1000/PPG_FS_HZ ms. Kalau angka ini meleset dari PPG_FS_HZ, BPM-nya
   * meleset dengan faktor yang sama persis. */
  const uint32_t upMs  = millis();
  const uint32_t t0    = g_ppg.t0_ms;
  const uint32_t runMs = (t0 && upMs > t0) ? (upMs - t0) : 0;
  const float fsMeas   = runMs ? (float)g_ppg.samples * 1000.0f / (float)runMs : 0.0f;

  Serial.printf("[STAT] up=%lus | sampel=%lu (fs_ukur~%.1f Hz) | overrun=%lu"
                " adc_gagal=%lu | heap=%lu\n",
                (unsigned long)(upMs / 1000), (unsigned long)g_ppg.samples,
                fsMeas, (unsigned long)g_ppg.overrun,
                (unsigned long)g_ppg.adc_fail, (unsigned long)ESP.getFreeHeap());
}

// =====================================================================
// setup()
// =====================================================================
void setup() {
  /* Power-gate diamankan sebelum apa pun. digitalWrite DULU baru pinMode:
   * kalau dibalik, pin sempat menggerakkan LOW (level default output)
   * beberapa mikrodetik, dan LOW di D2 = MOSFET nyambung, alias SON1303
   * sempat berkedut hidup sebelum ADC siap. */
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
  pinMode(PIN_SEN_EN, OUTPUT);
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);

  LED_PWM_ATTACH();
  LED_PWM_WRITE(0);

  Serial.begin(SERIAL_BAUD);
  const uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) delay(10);   // USB-CDC, jangan blok selamanya

#if !BPM_STREAM_CSV
  Serial.println(F("\n\n======================================"));
  Serial.println(F("  ANTARAGA — BPM dari SON1303"));
  Serial.println(F("======================================"));
  Serial.printf("Sensor    : SON1303 di A1/GPIO2, %d Hz, oversample %dx\n",
                PPG_FS_HZ, PPG_OVERSAMPLE);
  Serial.printf("Band-pass : %.2f - %.2f Hz (Butterworth orde-2 bertingkat)\n",
                (double)BPM_HP_HZ, (double)BPM_LP_HZ);
  Serial.printf("Rentang   : %.0f - %.0f bpm | blanking %d ms | ambang %.0f%%/%.0f%%\n",
                (double)BPM_MIN, (double)BPM_MAX, BPM_REFRACT_MS,
                (double)(BPM_THR_HI_FRAC * 100.0f), (double)(BPM_THR_LO_FRAC * 100.0f));
  Serial.printf("Riwayat   : median %d interval, %d denyut minimum, simpangan %d%%\n",
                BPM_IBI_HIST, BPM_MIN_BEATS, BPM_IBI_DEV_PCT);
  Serial.printf("Settle    : %d ms sensor + %d ms filter\n",
                SENSOR_SETTLE_MS, BPM_SETTLE_MS);
  Serial.println(F("--------------------------------------"));
  Serial.println(F("Tempelkan sensor, DIAM, tunggu status LOCKED."));
  Serial.println(F("--------------------------------------"));
#endif

  // Core 1, prioritas di atas loopTask (=1) supaya jadwal 5 ms terjaga.
  // Stack 4096 cukup: tidak ada TLS/JSON di sini, hanya ADC + float.
  xTaskCreatePinnedToCore(ppgTask, "ppg", 4096, nullptr, 6, nullptr, 1);
}

// =====================================================================
// loop() — core 1, prioritas terendah: LED + laporan
// =====================================================================
void loop() {
  static uint32_t lastBpm  = 0;
  static uint32_t lastStat = 0;

  BpmOut o;
  ppgGet(&o);

  ledService(o);

  const uint32_t now = millis();

#if !BPM_STREAM_CSV
  if (now - lastBpm >= BPM_REPORT_MS) {
    lastBpm = now;
    if (g_ppg.ready) printBpm(o);
  }
  if (now - lastStat >= STAT_PERIOD_MS) {
    lastStat = now;
    printStats();
  }
#else
  (void)lastBpm; (void)lastStat;   // baris CSV dicetak dari ppgTask
#endif

  delay(10);
}
