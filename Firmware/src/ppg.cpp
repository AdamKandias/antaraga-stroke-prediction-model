/**
 * ANTARAGA BPM — PENCUPLIK SON1303 (pinned ke core 1)
 * =====================================================================
 * Isi file ini:
 *   1. Lapisan ADC dengan shim Arduino core 2.x / 3.x
 *   2. ppgTask(): nyalakan sensor -> settle -> cuplik 200 Hz -> bpmPush()
 *
 * Lapisan ADC-nya SALINAN dari ../Firmware/src/sensors.cpp: unit, kanal,
 * atenuasi, lebar bit, dan cara oversample-nya sama sampai ke detailnya.
 * Itu bukan kebetulan — kalau front-end-nya berbeda sedikit saja (mis.
 * atenuasi lain), sinyal yang masuk algoritma di sini bukan lagi sinyal yang
 * dikirim firmware streaming ke cloud, dan membandingkan hasil keduanya jadi
 * tidak ada artinya.
 */

#include "ppg.h"

// =====================================================================
// 1. LAPISAN ADC — shim Arduino core 2.x / 3.x
// ---------------------------------------------------------------------
// Core 3.x (ESP-IDF 5.x) : esp_adc/adc_oneshot.h  <- jalur utama
// Core 2.x (ESP-IDF 4.4) : driver/adc.h (legacy)
// =====================================================================
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  #include "esp_adc/adc_oneshot.h"

  #define ADC_CH_PPG   ADC_CHANNEL_1     // GPIO2 = A1 pada XIAO ESP32-S3
  typedef adc_channel_t AdcChan;

  static adc_oneshot_unit_handle_t s_adc = nullptr;

  static bool adcInit() {
    adc_oneshot_unit_init_cfg_t unitCfg = {};
    unitCfg.unit_id  = ADC_UNIT_1;
    unitCfg.ulp_mode = ADC_ULP_MODE_DISABLE;
    if (adc_oneshot_new_unit(&unitCfg, &s_adc) != ESP_OK) return false;

    adc_oneshot_chan_cfg_t chCfg = {};
    chCfg.atten    = ADC_ATTEN_DB_12;    // ~0..3,1 V
    chCfg.bitwidth = ADC_BITWIDTH_12;    // 0..4095
    return adc_oneshot_config_channel(s_adc, ADC_CH_PPG, &chCfg) == ESP_OK;
  }

  static inline int adcRaw(AdcChan ch) {
    int v = 0;
    return (adc_oneshot_read(s_adc, ch, &v) == ESP_OK) ? v : -1;
  }

#else   // ---------------- Arduino core 2.x (legacy ADC driver) -------------
  #include "driver/adc.h"

  #define ADC_CH_PPG   ADC1_CHANNEL_1
  typedef adc1_channel_t AdcChan;

  static bool adcInit() {
    if (adc1_config_width(ADC_WIDTH_BIT_12) != ESP_OK) return false;
    return adc1_config_channel_atten(ADC_CH_PPG, ADC_ATTEN_DB_11) == ESP_OK;
  }
  static inline int adcRaw(AdcChan ch) { return adc1_get_raw(ch); }
#endif

/* Kalibrasi eFuse (raw -> mV) SENGAJA tidak dipakai di sini, berbeda dari
 * ../Firmware yang butuh mV untuk baterai. Algoritma BPM bekerja pada
 * SELISIH terhadap baseline-nya sendiri, dan kurva kalibrasi bersifat
 * monoton — mengubah raw ke mV hanya menskalakan ulang sinyal yang sudah
 * dinormalisasi ambang adaptif. Menyimpannya di domain raw membuat angka di
 * baris debug bisa langsung dibandingkan dengan kolom adc_raw rekaman
 * recorder-mu, tanpa konversi di kepala. */
static uint16_t adcOversample(AdcChan ch, uint8_t n) {
  uint32_t acc = 0;
  uint8_t  ok  = 0;
  for (uint8_t i = 0; i < n; i++) {
    const int v = adcRaw(ch);
    if (v >= 0) { acc += (uint32_t)v; ok++; }
  }
  if (ok != n) g_ppg.adc_fail += (uint32_t)(n - ok);
  return ok ? (uint16_t)(acc / ok) : 0;
}

// =====================================================================
// 2. Keadaan bersama
// =====================================================================
PpgStats g_ppg = {};

static BpmOut       s_pub;      // salinan terbit untuk loop()
static portMUX_TYPE s_pubMux = portMUX_INITIALIZER_UNLOCKED;

void ppgGet(BpmOut* out) {
  if (!out) return;
  portENTER_CRITICAL(&s_pubMux);
  *out = s_pub;
  portEXIT_CRITICAL(&s_pubMux);
}

static inline void publish(const BpmOut& o) {
  portENTER_CRITICAL(&s_pubMux);
  s_pub = o;
  portEXIT_CRITICAL(&s_pubMux);
}

// =====================================================================
// 3. TASK PENCUPLIK
// =====================================================================
void ppgTask(void* arg) {
  (void)arg;

  // --- Langkah 1: nyalakan sensor --------------------------------------
  digitalWrite(PIN_SEN_EN, SEN_POWER_ON);   // D2 LOW -> P-MOS Q2 ON -> SON1303 dapat 3V3

  if (!adcInit()) {
    Serial.println(F("[PPG] FATAL: ADC1 gagal init."));
    digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
    vTaskDelete(nullptr);
  }

  bpmInit((float)PPG_FS_HZ);
  bpmReset();

  Serial.printf("[PPG] SON1303 %d Hz, oversample %dx, A1/GPIO2. Settle %d ms...\n",
                PPG_FS_HZ, PPG_OVERSAMPLE, SENSOR_SETTLE_MS);

  const TickType_t kPeriod = pdMS_TO_TICKS(PPG_PERIOD_MS);
  TickType_t       lastWake = xTaskGetTickCount();

  /* --- Langkah 2: settle — sampel DIBUANG, tidak masuk detektor --------
   * Baseline op-amp SON1303 (kopling DC) butuh waktu setelah power-gate
   * dibuka. Sampel transien itu tidak boleh masuk band-pass: HP 0,5 Hz akan
   * meresponsnya sebagai step raksasa yang berdering beberapa detik, dan
   * dering itu terlihat seperti denyut.
   *
   * ADC tetap dibaca (bukan sekadar delay) supaya sample-and-hold ADC ikut
   * hangat dan bacaan pertama yang dipakai tidak berbeda karakter. */
  for (uint32_t i = 0; i < (uint32_t)(SENSOR_SETTLE_MS / PPG_PERIOD_MS); i++) {
    vTaskDelayUntil(&lastWake, kPeriod);
    (void)adcOversample((AdcChan)ADC_CH_PPG, PPG_OVERSAMPLE);
  }
  bpmReset();                                // mulai dari keadaan bersih
  g_ppg.ready = true;

#if BPM_STREAM_CSV
  Serial.println(F("# t_ms,raw,ac,thr_hi,thr_lo,beat,bpm,status"));
#else
  Serial.println(F("[PPG] MENGUKUR (detektor settle 3 detik lagi)"));
#endif

  // --- Langkah 3: cuplik pada laju tetap -------------------------------
  BpmOut o;
  g_ppg.t0_ms = millis();
  lastWake    = xTaskGetTickCount();
  for (;;) {
    vTaskDelayUntil(&lastWake, kPeriod);
    /* Telat = jadwal 5 ms tidak terpenuhi, dan itu langsung merusak BASIS
     * WAKTU interval (mesin menganggap tiap sampel berjarak tepat 5 ms).
     * Karena itu overrun dicacah dan dicetak, bukan diabaikan. */
    if ((TickType_t)(xTaskGetTickCount() - lastWake) >= kPeriod) g_ppg.overrun++;

    const uint16_t raw = adcOversample((AdcChan)ADC_CH_PPG, PPG_OVERSAMPLE);
    bpmPush(raw, &o);
    g_ppg.samples++;

    if (o.beat) g_ppg.beat_seq++;
    publish(o);

#if BPM_STREAM_CSV
    /* Mode kalibrasi. Cetakan terjadi DI DALAM task pencuplik, jadi timing
     * 5 ms ikut terganggu (terlihat sebagai overrun > 0) — itu harga yang
     * sengaja dibayar untuk bisa melihat sinyal, ambang, dan penanda denyut
     * pada satu sumbu waktu yang sama. Matikan saat mengukur sungguhan. */
    Serial.printf("%lu,%u,%.1f,%.1f,%.1f,%d,%.1f,%s\n",
                  (unsigned long)(g_ppg.samples * PPG_PERIOD_MS), (unsigned)raw,
                  o.ac_now, o.thr_hi, o.thr_lo, o.beat ? 1 : 0, o.bpm,
                  bpmStatusName(o.status));
#endif
  }
}
