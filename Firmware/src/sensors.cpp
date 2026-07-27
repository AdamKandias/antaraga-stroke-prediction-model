/**
 * ANTARAGA — CORE SENSOR (pinned ke core 1)
 * =====================================================================
 * Isi file ini:
 *   1. Driver bare-metal MAX30102 (I2C, dibaca lewat FIFO)
 *   2. Lapisan ADC (SEN0203 + sensor tegangan baterai) dengan shim supaya
 *      ikut ter-compile di Arduino core 2.x maupun 3.x
 *   3. sensorTask(): menunggu WiFi -> nyalakan sensor -> settle -> streaming
 *
 * Yang dikirim ke cloud MURNI angka mentah ADC. Tidak ada band-pass, tidak
 * ada deteksi puncak, tidak ada penghitungan BPM di firmware — semua analisis
 * (PWA, VPG, APG) dikerjakan di sisi cloud dari data mentah ini.
 */

#include "antaraga.h"
#include <Wire.h>

// =====================================================================
// 1. LAPISAN ADC — shim Arduino core 2.x / 3.x
// ---------------------------------------------------------------------
// Core 3.x (ESP-IDF 5.x) : esp_adc/adc_oneshot.h  <- dipakai kode optimasimu
// Core 2.x (ESP-IDF 4.4) : driver/adc.h (legacy)
// =====================================================================
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  #include "esp_adc/adc_oneshot.h"
  #include "esp_adc/adc_cali.h"
  #include "esp_adc/adc_cali_scheme.h"

  #define ADC_CH_PPG   ADC_CHANNEL_1     // GPIO2 = A1
  #define ADC_CH_BATT  ADC_CHANNEL_0     // GPIO1 = A0
  typedef adc_channel_t AdcChan;

  static adc_oneshot_unit_handle_t s_adc  = nullptr;
  static adc_cali_handle_t         s_cali = nullptr;

  static bool adcInit() {
    adc_oneshot_unit_init_cfg_t unitCfg = {};
    unitCfg.unit_id  = ADC_UNIT_1;
    unitCfg.ulp_mode = ADC_ULP_MODE_DISABLE;
    if (adc_oneshot_new_unit(&unitCfg, &s_adc) != ESP_OK) return false;

    adc_oneshot_chan_cfg_t chCfg = {};
    chCfg.atten    = ADC_ATTEN_DB_12;    // ~0..3,1 V
    chCfg.bitwidth = ADC_BITWIDTH_12;    // 0..4095
    if (adc_oneshot_config_channel(s_adc, ADC_CH_PPG,  &chCfg) != ESP_OK) return false;
    if (adc_oneshot_config_channel(s_adc, ADC_CH_BATT, &chCfg) != ESP_OK) return false;

    // Kalibrasi eFuse: raw -> mV yang akurat. Kalau chip tidak punya data
    // kalibrasi, s_cali = nullptr dan adcRawToMv() jatuh ke skala linear.
    adc_cali_curve_fitting_config_t caliCfg = {};
    caliCfg.unit_id  = ADC_UNIT_1;
    caliCfg.atten    = ADC_ATTEN_DB_12;
    caliCfg.bitwidth = ADC_BITWIDTH_12;
    if (adc_cali_create_scheme_curve_fitting(&caliCfg, &s_cali) != ESP_OK) s_cali = nullptr;
    return true;
  }

  static inline int adcRaw(AdcChan ch) {
    int v = 0;
    return (adc_oneshot_read(s_adc, ch, &v) == ESP_OK) ? v : -1;
  }

  static inline uint32_t adcRawToMv(int raw) {
    int mv = 0;
    if (s_cali && adc_cali_raw_to_voltage(s_cali, raw, &mv) == ESP_OK) return (uint32_t)mv;
    return (uint32_t)((raw * 3300L) / 4095L);   // fallback tanpa kalibrasi eFuse
  }

#else   // ---------------- Arduino core 2.x (legacy ADC driver) -------------
  #include "driver/adc.h"
  #include "esp_adc_cal.h"

  #define ADC_CH_PPG   ADC1_CHANNEL_1
  #define ADC_CH_BATT  ADC1_CHANNEL_0
  typedef adc1_channel_t AdcChan;

  static esp_adc_cal_characteristics_t s_cal;

  static bool adcInit() {
    if (adc1_config_width(ADC_WIDTH_BIT_12) != ESP_OK) return false;
    if (adc1_config_channel_atten(ADC_CH_PPG,  ADC_ATTEN_DB_11) != ESP_OK) return false;
    if (adc1_config_channel_atten(ADC_CH_BATT, ADC_ATTEN_DB_11) != ESP_OK) return false;
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &s_cal);
    return true;
  }
  static inline int      adcRaw(AdcChan ch)  { return adc1_get_raw(ch); }
  static inline uint32_t adcRawToMv(int raw) { return esp_adc_cal_raw_to_voltage(raw, &s_cal); }
#endif

/* Oversampling: N bacaan dalam ~mikrodetik dirata-ratakan jadi SATU titik
 * waktu. Menekan noise ADC acak tanpa menumpulkan upstroke / dicrotic notch,
 * jadi aman untuk analisis PWA. Ini beda dengan filter waktu (moving average
 * antar titik) yang justru merusak morfologi. */
static uint16_t adcOversample(AdcChan ch, uint8_t n) {
  uint32_t acc = 0;
  uint8_t  ok  = 0;
  for (uint8_t i = 0; i < n; i++) {
    int v = adcRaw(ch);
    if (v >= 0) { acc += (uint32_t)v; ok++; }
  }
  return ok ? (uint16_t)(acc / ok) : 0;
}

// =====================================================================
// 2. DRIVER MAX30102 (bare chip, bukan modul UART)
// =====================================================================
#define MAX_ADDR          0x57
#define REG_FIFO_WR_PTR   0x04
#define REG_OVF_COUNTER   0x05
#define REG_FIFO_RD_PTR   0x06
#define REG_FIFO_DATA     0x07
#define REG_FIFO_CONFIG   0x08
#define REG_MODE_CONFIG   0x09
#define REG_SPO2_CONFIG   0x0A
#define REG_LED1_PA       0x0C   // RED
#define REG_LED2_PA       0x0D   // IR
#define REG_PART_ID       0xFF

#define MODE_SHUTDOWN     0x80
#define MODE_RESET        0x40
#define MODE_SPO2         0x03   // RED + IR

#if MAX_PROFILE_PWA
  // ADC_RGE=8192nA | SR=800Hz | PW=411us, SMP_AVE=2 -> keluaran 400 Hz
  #define CFG_SPO2        0x53
  #define CFG_FIFO        0x30   // SMP_AVE=2 + ROLLOVER_EN
#else
  // ADC_RGE=8192nA | SR=1000Hz | PW=411us, SMP_AVE=4 -> keluaran 250 Hz
  #define CFG_SPO2        0x57
  #define CFG_FIFO        0x50   // SMP_AVE=4 + ROLLOVER_EN
#endif

static void maxWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MAX_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

static uint8_t maxRead(uint8_t reg) {
  Wire.beginTransmission(MAX_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return 0;
  if (Wire.requestFrom((int)MAX_ADDR, 1) < 1) return 0;
  return Wire.read();
}

/* Register 0x04/0x05/0x06 berurutan, jadi ketiganya diambil dalam SATU
 * transaksi I2C. Dipanggil 200x/detik, jadi penghematan ini nyata. */
static bool maxReadPtrs(uint8_t& wr, uint8_t& ovf, uint8_t& rd) {
  Wire.beginTransmission(MAX_ADDR);
  Wire.write(REG_FIFO_WR_PTR);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MAX_ADDR, 3) < 3) return false;
  wr  = Wire.read();
  ovf = Wire.read();
  rd  = Wire.read();
  return true;
}

static void maxClearFifo() {
  maxWrite(REG_FIFO_WR_PTR, 0);
  maxWrite(REG_OVF_COUNTER, 0);
  maxWrite(REG_FIFO_RD_PTR, 0);
}

static bool maxProbe() { return maxRead(REG_PART_ID) == 0x15; }

static bool maxBegin() {
  if (!maxProbe()) return false;
  maxWrite(REG_MODE_CONFIG, MODE_RESET);
  delay(50);
  uint32_t t0 = millis();
  while ((maxRead(REG_MODE_CONFIG) & MODE_RESET) && millis() - t0 < 500) delay(1);

  maxClearFifo();
  maxWrite(REG_FIFO_CONFIG, CFG_FIFO);
  maxWrite(REG_SPO2_CONFIG, CFG_SPO2);
  maxWrite(REG_LED1_PA,     MAX_LED_RED);
  maxWrite(REG_LED2_PA,     MAX_LED_IR);
  maxWrite(REG_MODE_CONFIG, MODE_SHUTDOWN);   // LED tetap padam sampai diminta
  return true;
}

static void maxStart() { maxWrite(REG_MODE_CONFIG, MODE_SPO2); maxClearFifo(); }

/* Baca n sampel sekaligus. Tiap sampel 6 byte (RED 3 + IR 3). Dipecah per 16
 * sampel (96 byte) supaya muat di buffer Wire ESP32 (128 byte). */
static uint8_t maxReadFifo(uint8_t n, uint32_t* red, uint32_t* ir) {
  uint8_t got = 0;
  while (n > 0) {
    uint8_t chunk = (n > 16) ? 16 : n;
    Wire.beginTransmission(MAX_ADDR);
    Wire.write(REG_FIFO_DATA);
    if (Wire.endTransmission(false) != 0) break;
    if (Wire.requestFrom((int)MAX_ADDR, (int)(chunk * 6)) < chunk * 6) break;

    for (uint8_t i = 0; i < chunk; i++) {
      uint8_t b[6];
      for (uint8_t j = 0; j < 6; j++) b[j] = Wire.read();
      red[got] = (((uint32_t)b[0] << 16) | ((uint32_t)b[1] << 8) | b[2]) & 0x03FFFF;
      ir [got] = (((uint32_t)b[3] << 16) | ((uint32_t)b[4] << 8) | b[5]) & 0x03FFFF;
      got++;
    }
    n -= chunk;
  }
  return got;
}

// =====================================================================
// 3. BATERAI — Vsens (A0) -> mV -> persen
// =====================================================================
/* Kurva pelepasan Li-Po 1S. Konversi linear 3,0-4,2 V salah besar karena
 * kurva Li-Po datar di tengah: 3,85 V itu ~50%, bukan ~71% seperti hasil
 * hitungan linear. Tabel ini diinterpolasi linear per segmen. */
static const struct { uint16_t mv; uint8_t pct; } kLipoCurve[] = {
  {4200,100},{4150, 95},{4110, 90},{4080, 85},{4020, 80},{3980, 75},{3950, 70},
  {3910, 65},{3870, 60},{3850, 55},{3840, 50},{3820, 45},{3800, 40},{3790, 35},
  {3770, 30},{3750, 25},{3730, 20},{3710, 15},{3690, 10},{3610,  5},{3270,  0}
};
static const uint8_t kLipoN = sizeof(kLipoCurve) / sizeof(kLipoCurve[0]);

static uint8_t lipoPercent(uint16_t mv) {
  if (mv >= kLipoCurve[0].mv)          return 100;
  if (mv <= kLipoCurve[kLipoN - 1].mv) return 0;
  for (uint8_t i = 1; i < kLipoN; i++) {
    if (mv >= kLipoCurve[i].mv) {
      const uint16_t hiMv = kLipoCurve[i - 1].mv, loMv = kLipoCurve[i].mv;
      const uint8_t  hiP  = kLipoCurve[i - 1].pct, loP = kLipoCurve[i].pct;
      return (uint8_t)(loP + (uint32_t)(mv - loMv) * (hiP - loP) / (hiMv - loMv));
    }
  }
  return 0;
}

volatile uint16_t g_battMv  = 0;
volatile uint8_t  g_battPct = 0;
static float      s_battEma = 0.0f;   // mV baterai, dihaluskan

static void readBattery(bool seed) {
  const uint16_t rawAvg = adcOversample((AdcChan)ADC_CH_BATT, BATT_OVERSAMPLE);
  // mV di pin -> mV baterai (dibalik pembagi R1/R2 100k), lalu trim kalibrasi
  const float mv = adcRawToMv(rawAvg) * BATT_DIVIDER_GAIN * BATT_CAL_TRIM;

  if (seed || s_battEma <= 0.0f) s_battEma = mv;
  else s_battEma += BATT_EMA_ALPHA * (mv - s_battEma);

  g_battMv  = (uint16_t)(s_battEma + 0.5f);
  g_battPct = lipoPercent(g_battMv);
}

// =====================================================================
// 4. PENGELOLAAN BATCH
// =====================================================================
static Batch* batchAcquire() {
  Batch* b = nullptr;
  if (xQueueReceive(g_qFree, &b, 0) != pdTRUE) {
    /* Pool habis = jaringan tidak mengejar. Buang batch TERTUA supaya data
     * terbaru tetap mengalir (streaming lebih berharga daripada arsip basi). */
    if (xQueueReceive(g_qFilled, &b, 0) == pdTRUE) g_stats.batches_dropped++;
    else return nullptr;
  }
  b->ppg_n = 0;
  b->max_n = 0;
  b->max_ovf = 0;
  return b;
}

// =====================================================================
// 5. TASK SENSOR
// =====================================================================
void sensorTask(void* arg) {
  (void)arg;

  // --- Langkah 1: tunggu core WiFi melapor tersambung -------------------
  xEventGroupWaitBits(g_events, EV_WIFI_OK, pdFALSE, pdTRUE, portMAX_DELAY);
  Serial.println(F("[SENSOR] WiFi siap -> menyalakan sensor"));

  // --- Langkah 2: nyalakan sensor --------------------------------------
  digitalWrite(PIN_SEN_EN, SEN_POWER_ON);      // D2 LOW -> P-MOS Q2 ON -> SEN0203 dapat 3V3

  if (!adcInit()) {
    Serial.println(F("[SENSOR] FATAL: ADC1 gagal init."));
    setState(ST_ERROR);
    digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
    vTaskDelete(nullptr);
  }

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);
  Wire.setTimeOut(50);

  if (!maxBegin()) {
    Serial.println(F("[SENSOR] FATAL: MAX30102 tidak terdeteksi di I2C 0x57."));
    Serial.println(F("[SENSOR] Cek SDA=D4/GPIO5, SCL=D5/GPIO6, dan 3V3 (ferrite B2)."));
    setState(ST_ERROR);
    digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
    vTaskDelete(nullptr);
  }
  maxStart();                                   // keluar dari shutdown, LED menyala
  setState(ST_SENSOR_WARMUP);

  Serial.printf("[SENSOR] MAX30102 %d Hz, SEN0203 %d Hz (oversample %dx). Settle %d ms...\n",
                MAX_FS_HZ, PPG_FS_HZ, PPG_OVERSAMPLE, SENSOR_SETTLE_MS);

  // --- Langkah 3: settle — sampel dibuang, bukan dikirim ----------------
  // FIFO tetap dikuras supaya tidak overflow dan tidak ada sisa data lama.
  const TickType_t kPeriod = pdMS_TO_TICKS(PPG_PERIOD_MS);
  TickType_t lastWake = xTaskGetTickCount();
  uint32_t scratchRed[34], scratchIr[34];

  for (uint32_t i = 0; i < (uint32_t)(SENSOR_SETTLE_MS / PPG_PERIOD_MS); i++) {
    vTaskDelayUntil(&lastWake, kPeriod);
    (void)adcOversample((AdcChan)ADC_CH_PPG, PPG_OVERSAMPLE);
    uint8_t wr, ovf, rd;
    if (maxReadPtrs(wr, ovf, rd)) {
      uint8_t avail = (uint8_t)((wr - rd) & 0x1F);
      if (avail) maxReadFifo(avail > 32 ? 32 : avail, scratchRed, scratchIr);
    }
  }
  maxClearFifo();
  readBattery(true);                            // bacaan pertama jadi seed EMA

  // --- Langkah 4: streaming --------------------------------------------
  setState(ST_STREAMING);
  Serial.println(F("[SENSOR] STREAMING"));

  Batch*   b        = batchAcquire();
  uint32_t seq      = 0;
  uint16_t battTick = 0;
  const uint16_t kBattTicks = BATT_PERIOD_MS / PPG_PERIOD_MS;

  lastWake = xTaskGetTickCount();
  for (;;) {
    vTaskDelayUntil(&lastWake, kPeriod);
    if ((TickType_t)(xTaskGetTickCount() - lastWake) >= kPeriod) g_stats.ppg_overrun++;

    if (!b) { b = batchAcquire(); if (!b) continue; }
    if (b->ppg_n == 0) {                        // titik pertama = penanda waktu batch
      b->seq        = seq;
      b->t0_ms      = millis();
      b->t0_unix_ms = unixMillis();
    }

    // 4a. SEN0203 — satu titik PPG mentah
    b->ppg[b->ppg_n++] = adcOversample((AdcChan)ADC_CH_PPG, PPG_OVERSAMPLE);
    g_stats.ppg_samples++;

    // 4b. MAX30102 — kuras seluruh FIFO (~2 sampel per tick di 400 Hz)
    uint8_t wr, ovf, rd;
    if (maxReadPtrs(wr, ovf, rd)) {
      if (ovf) {
        const uint32_t tot = (uint32_t)b->max_ovf + ovf;
        b->max_ovf = (tot > 255) ? 255 : (uint8_t)tot;
        g_stats.max_ovf_total += ovf;
      }
      uint8_t avail = (uint8_t)((wr - rd) & 0x1F);
      if (avail) {
        uint8_t got = maxReadFifo(avail > 32 ? 32 : avail, scratchRed, scratchIr);
        for (uint8_t i = 0; i < got; i++) {
          if (b->max_n < MAX_CAP) {
            b->red[b->max_n] = scratchRed[i];
            b->ir [b->max_n] = scratchIr [i];
            b->max_n++;
          } else {
            g_stats.max_trunc++;
          }
        }
        g_stats.max_samples += got;
      }
    }

    // 4c. Baterai — di core & task yang sama supaya handle ADC punya satu pemilik
    if (++battTick >= kBattTicks) { battTick = 0; readBattery(false); }

    // 4d. Batch penuh -> serahkan ke core WiFi
    if (b->ppg_n >= PPG_PER_BATCH) {
      b->batt_mv  = g_battMv;
      b->batt_pct = g_battPct;
      g_stats.batches_made++;
      seq++;
      if (xQueueSend(g_qFilled, &b, 0) != pdTRUE) {
        // Tidak seharusnya terjadi (kapasitas qFilled = BATCH_POOL). Kembalikan
        // ke pool alih-alih membiarkan pointer-nya bocor.
        g_stats.batches_dropped++;
        xQueueSend(g_qFree, &b, 0);
      }
      b = batchAcquire();
    }
  }
}
