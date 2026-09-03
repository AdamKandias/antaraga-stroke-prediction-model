/*
 * PPG Recorder SEN0203 - DATA MENTAH untuk PWA - XIAO ESP32-C3
 * ====================================================================
 * Versi FINAL pengambilan data thesis. Dioptimasi untuk analisis Pulse
 * Wave Analysis (PWA): menyimpan sinyal MENTAH seutuh mungkin supaya
 * morfologi (upstroke, dicrotic notch, gelombang a-b-c-d-e) terjaga.
 *
 * PRINSIP DESAIN:
 *   - Oversample 64x  : tekan noise ADC ACAK tanpa merusak bentuk
 *                       gelombang (64 bacaan dalam ~mikrodetik = 1 titik
 *                       waktu). Menaikkan resolusi efektif ADC. AMAN utk PWA.
 *   - TIDAK ada sinkron-50Hz : jendela 20ms akan menumpulkan upstroke &
 *                       notch. Noise 50Hz ditangani di HARDWARE (elektroda
 *                       ground + low-pass RC), jadi tak perlu di software.
 *   - adc_raw TIDAK di-band-pass : disimpan apa adanya. Kamu filter ulang
 *                       sesukamu saat analisis (band-pass, VPG, APG).
 *   - Kolom ppg_bandpass hanya BANTU visual, bukan untuk analisis final.
 *
 * SETUP HARDWARE (wajib untuk data bersih):
 *   - Elektroda ground: logam ke kulit pergelangan, ke pin GND.
 *   - Low-pass RC di jalur sinyal (cutoff ~15-20 Hz, JANGAN <15Hz agar
 *     upstroke/notch tak tumpul). Contoh R=10k, C=1uF -> ~16Hz.
 *   - Jauhkan dari sumber listrik. Charger laptop dicabut.
 *
 * Output CSV: t_ms, adc_raw, ppg_bandpass
 * Wiring: S->A0(GPIO2), +->3V3, -->GND.  Baud 115200.
 * Butuh ESP32 Arduino core v3.x (esp_adc/adc_oneshot.h).
 */

#include <Arduino.h>
#include "esp_adc/adc_oneshot.h"

// ---------- ADC ----------
#define ADC_UNIT ADC_UNIT_1
#define ADC_CHAN ADC_CHANNEL_2       // GPIO2 = A0 pada XIAO ESP32-C3
#define ADC_ATTEN ADC_ATTEN_DB_12    // ~0..3.3V
#define ADC_BITWIDTH ADC_BITWIDTH_12 // 0..4095
#define OVERSAMPLE 64                // rata-rata bacaan/titik (anti noise acak)

#define ADC_VREF_MV 3300.0f
#define ADC_MAX_CNT 4095.0f

// ---------- Rekaman ----------
#define RECORD_SECONDS 60
#define WARMUP_SECONDS 8
#define FS 200.0f
#define SAMPLE_US (uint32_t)(1000000UL / (uint32_t)FS) // 5000 us

// ---------- Band-pass Butterworth 0.5-5 Hz (kolom BANTU saja) ----------
#define INVERT_PPG 0
struct Biquad
{
  float b0, b1, b2, a1, a2;
  float z1, z2;
  inline float process(float x)
  {
    float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
};
Biquad hp = {0.98939225f, -1.97878451f, 0.98939225f, -1.97867496f, 0.97889406f, 0, 0};
Biquad lp = {0.00554272f, 0.01108544f, 0.00554272f, -1.77863178f, 0.80080265f, 0, 0};

// ---------- Handle ADC oneshot ----------
adc_oneshot_unit_handle_t adcHandle = nullptr;

// ---------- Hardware timer + ring buffer ----------
hw_timer_t *sampleTimer = nullptr;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
volatile uint16_t ringBuf[256];
volatile uint8_t ringHead = 0, ringTail = 0;

static inline uint16_t adcOversample()
{
  uint32_t acc = 0;
  int v;
  for (int i = 0; i < OVERSAMPLE; i++)
    if (adc_oneshot_read(adcHandle, ADC_CHAN, &v) == ESP_OK)
      acc += (uint32_t)v;
  return (uint16_t)(acc / OVERSAMPLE);
}

void IRAM_ATTR onSampleTimer()
{
  portENTER_CRITICAL_ISR(&timerMux);
  uint16_t raw = adcOversample();
  uint8_t next = (ringHead + 1) & 0xFF;
  if (next != ringTail)
  {
    ringBuf[ringHead] = raw;
    ringHead = next;
  }
  portEXIT_CRITICAL_ISR(&timerMux);
}

// ---------- State ----------
uint32_t sampleIdx = 0;
bool recording = false, finished = false;
uint32_t warmupSamples, recordSamples, warmupCount = 0;

void setup()
{
  Serial.begin(115200);
  delay(300);

  adc_oneshot_unit_init_cfg_t initCfg = {.unit_id = ADC_UNIT, .ulp_mode = ADC_ULP_MODE_DISABLE};
  adc_oneshot_new_unit(&initCfg, &adcHandle);
  adc_oneshot_chan_cfg_t chanCfg = {.atten = ADC_ATTEN, .bitwidth = ADC_BITWIDTH};
  adc_oneshot_config_channel(adcHandle, ADC_CHAN, &chanCfg);

  warmupSamples = (uint32_t)(WARMUP_SECONDS * FS);
  recordSamples = (uint32_t)(RECORD_SECONDS * FS);

  Serial.print(F("# PPG Recorder SEN0203 DATA MENTAH (PWA). Oversample="));
  Serial.print(OVERSAMPLE);
  Serial.println(F("x, tanpa sinkron-50Hz."));
  Serial.println(F("# Pastikan elektroda ground + low-pass RC terpasang, DIAM total."));
  Serial.print(F("# Warmup "));
  Serial.print(WARMUP_SECONDS);
  Serial.print(F(" dtk, rekam "));
  Serial.print(RECORD_SECONDS);
  Serial.println(F(" dtk."));

  sampleTimer = timerBegin(1000000);
  timerAttachInterrupt(sampleTimer, &onSampleTimer);
  timerAlarm(sampleTimer, SAMPLE_US, true, 0);
}

void loop()
{
  if (finished)
    return;
  while (ringTail != ringHead)
  {
    portENTER_CRITICAL(&timerMux);
    uint16_t raw = ringBuf[ringTail];
    ringTail = (ringTail + 1) & 0xFF;
    portEXIT_CRITICAL(&timerMux);

    float voltage_mV = ((float)raw / ADC_MAX_CNT) * ADC_VREF_MV;
    float f = hp.process(voltage_mV);
    f = lp.process(f);
    float sigv = INVERT_PPG ? -f : f;

    if (!recording)
    {
      if (++warmupCount >= warmupSamples)
      {
        recording = true;
        sampleIdx = 0;
        Serial.println(F("# START"));
        Serial.println(F("t_ms,adc_raw,ppg_bandpass"));
      }
      continue;
    }

    float t_ms = sampleIdx * (1000.0f / FS);
    Serial.print(t_ms, 1);
    Serial.print(',');
    Serial.print(raw);
    Serial.print(','); // raw MENTAH (belum band-pass)
    Serial.println(sigv, 4);

    if (++sampleIdx >= recordSamples)
    {
      Serial.println(F("# END"));
      Serial.print(F("# Total sampel: "));
      Serial.print(recordSamples);
      Serial.print(F("  @ "));
      Serial.print(FS, 0);
      Serial.print(F(" Hz, oversample="));
      Serial.print(OVERSAMPLE);
      Serial.println(F("x"));
      Serial.println(F("# Reset board untuk merekam lagi."));
      finished = true;
      return;
    }
  }
  delayMicroseconds(200);
}
