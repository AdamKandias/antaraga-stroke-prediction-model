/**
 * ANTARAGA Smartband — FIRMWARE UTAMA (streaming ke cloud)
 * =====================================================================
 * Board   : Seeed XIAO ESP32-S3
 * Sensor  : MAX30102 (I2C, FIFO)  +  SON1303 (PPG analog)
 * Metode  : streaming — data MENTAH dikirim terus-menerus via HTTPS
 *
 * ALGORITMA
 * ---------
 *   1. CORE 0 (netTask)   : nyalakan WiFi, cari & sambung AP, sinkron NTP.
 *   2. CORE 1 (sensorTask): menunggu sinyal "WiFi OK", lalu menyalakan
 *                           MAX30102 (keluar shutdown, baca via FIFO) dan
 *                           SON1303 (D2 di-LOW-kan -> P-MOSFET Q2 nyambung).
 *   3. Tunggu SENSOR_SETTLE_MS (1 dtk): sampel dibuang, jadi noise transien
 *      power-on tidak ikut terkirim.
 *   4. Streaming: sensorTask mengisi Batch -> netTask POST HTTPS ke cloud.
 *      Isinya MURNI nilai ADC mentah kedua sensor.
 *   5. Bersamaan: A0 membaca tegangan baterai -> persen -> ikut tiap batch.
 *   6. Selama streaming, LED di D10 berkedip.
 *
 * PETA PIN (skematik ANTARAGA -> XIAO ESP32-S3)
 * ---------------------------------------------------------------------
 *   D0 / A0  GPIO1  Vsens     <- R1/R2 100k dari Vbatt (Vsens = Vbatt/2)
 *   D1 / A1  GPIO2  SIG_PPG   <- keluaran analog SON1303 (J2)
 *   D2       GPIO3  SEN_EN    -> gate Q2 DMP2130L (P-MOS). LOW = sensor ON
 *   D4       GPIO5  SDA       <-> MAX30102 (J3)
 *   D5       GPIO6  SCL       <-> MAX30102 (J3)
 *   D10      GPIO9  LED       -> R6 10k -> LED J7. HIGH = nyala
 *
 * ARTI KEDIP LED D10
 * ---------------------------------------------------------------------
 *   cepat  (100 ms)          : mencari / menyambung WiFi
 *   sedang (250 ms)          : sensor menyala, sedang settle 1 detik
 *   BERNAPAS (redup-terang)  : STREAMING — sedang mengambil data  <- normal
 *   kedip ganda              : sensor jalan tapi jaringan putus (data dibuffer)
 *   nyala panjang 800 ms     : sensor gagal init — cek serial monitor
 */

#include "antaraga.h"
#include <WiFi.h>     // hanya untuk WiFi.RSSI() di baris [STAT]
#include <esp_ota_ops.h>   // hanya untuk menampilkan partisi aktif di banner

// =====================================================================
// Objek global
// =====================================================================
EventGroupHandle_t   g_events  = nullptr;
QueueHandle_t        g_qFree   = nullptr;
QueueHandle_t        g_qFilled = nullptr;
volatile DeviceState g_state   = ST_BOOT;
Stats                g_stats   = {};

// Pool buffer batch — dialokasikan statis supaya tidak ada malloc saat runtime
// (fragmentasi heap adalah pembunuh utama firmware yang jalan berjam-jam).
static Batch  s_pool[BATCH_POOL];

void setState(DeviceState s) {
  if (g_state == ST_ERROR && s != ST_ERROR) return;   // ST_ERROR bersifat sticky
  g_state = s;
}

static const char* stateName(DeviceState s) {
  switch (s) {
    case ST_BOOT:             return "BOOT";
    case ST_WIFI_CONNECTING:  return "WIFI";
    case ST_SENSOR_WARMUP:    return "WARMUP";
    case ST_STREAMING:        return "STREAM";
    case ST_NET_LOST:         return "NET_LOST";
    case ST_ERROR:            return "ERROR";
  }
  return "?";
}

// =====================================================================
// LED indikator (D10)
// ---------------------------------------------------------------------
// SELURUH pola digerakkan lewat PWM (LEDC), termasuk yang sekadar kedip.
// Ini disengaja: begitu sebuah pin ter-attach ke LEDC, digitalWrite() di pin
// itu tidak lagi berpengaruh sampai LEDC dilepas. Kalau napas memakai PWM
// sementara kedip memakai digitalWrite, pola kedip akan mati diam-diam setelah
// perangkat sekali saja masuk STREAMING. Satu jalur keluaran = tidak ada
// kelas bug itu sama sekali.
//
// Tabel pola: indeks GENAP = durasi nyala, indeks GANJIL = durasi padam.
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

static const uint16_t PAT_BOOT  [] = { 50,  50};
static const uint16_t PAT_WIFI  [] = {100, 100};
static const uint16_t PAT_WARMUP[] = {250, 250};
static const uint16_t PAT_LOST  [] = { 60, 120, 60, 760};
static const uint16_t PAT_ERROR [] = {800, 200};

/* Kurva napas. Level persepsi mengikuti (1 - cos)/2 — mulus dan melambat
 * sendiri di kedua ujung, itulah yang membuatnya terasa seperti napas dan bukan
 * segitiga naik-turun. Level itu LALU dipangkatkan gamma untuk jadi duty,
 * karena mata menangkap kecerahan secara logaritmik. Tanpa gamma, LED terlihat
 * melonjak terang di awal lalu menggantung penuh separuh siklus. */
static uint32_t breathDuty(uint32_t elapsedMs) {
  const float phase = (float)(elapsedMs % LED_BREATH_PERIOD_MS) / (float)LED_BREATH_PERIOD_MS;
  float lvl = 0.5f * (1.0f - cosf(2.0f * (float)PI * phase));   // 0..1
  float g = lvl;
  for (uint8_t i = 1; i < LED_BREATH_GAMMA; i++) g *= lvl;
  return (uint32_t)(g * (float)LED_DUTY_MAX + 0.5f);
}

static void ledService() {
  static DeviceState prev      = ST_BOOT;
  static uint8_t     step      = 0;
  static uint32_t    stepStart = 0;
  static uint32_t    phaseT0   = 0;

  const uint32_t now = millis();
  if (g_state != prev) {                     // ganti status -> mulai pola dari awal
    prev      = g_state;
    step      = 0;
    stepStart = now;
    phaseT0   = now;
  }

  /* STREAMING = sedang mengambil data. Ini satu-satunya status yang bernapas,
   * supaya "sedang mengukur" langsung terbaca tanpa menghitung kedipan.
   *
   * ST_NET_LOST sengaja TIDAK ikut bernapas meski sensor tetap mencuplik:
   * status itu perlu tampil beda karena data sedang menumpuk di buffer dan
   * bisa mulai terbuang. Kedip ganda menyampaikan peringatan itu; napas tidak. */
  if (g_state == ST_STREAMING) {
    LED_PWM_WRITE(breathDuty(now - phaseT0));
    return;
  }

  const uint16_t* pat;
  uint8_t         nSteps;
  switch (g_state) {
    case ST_WIFI_CONNECTING: pat = PAT_WIFI;   nSteps = 2; break;
    case ST_SENSOR_WARMUP:   pat = PAT_WARMUP; nSteps = 2; break;
    case ST_NET_LOST:        pat = PAT_LOST;   nSteps = 4; break;
    case ST_ERROR:           pat = PAT_ERROR;  nSteps = 2; break;
    default:                 pat = PAT_BOOT;   nSteps = 2; break;
  }

  if (now - stepStart >= pat[step]) {
    stepStart = now;
    step      = (uint8_t)((step + 1) % nSteps);
  }
  LED_PWM_WRITE((step % 2 == 0) ? LED_DUTY_MAX : 0);
}

// =====================================================================
// Statistik ke serial
// =====================================================================
static void printStats() {
  Serial.printf(
    "[STAT] %-8s up=%lus | batch made=%lu sent=%lu drop=%lu httpfail=%lu"
    " code=%ld post=%lums\n",
    stateName(g_state), (unsigned long)(millis() / 1000),
    (unsigned long)g_stats.batches_made, (unsigned long)g_stats.batches_sent,
    (unsigned long)g_stats.batches_dropped, (unsigned long)g_stats.http_fail,
    (long)g_stats.last_http_code, (unsigned long)g_stats.last_post_ms);

  /* fs_max_ukur = laju MAX30102 yang BENAR-BENAR tercapai. Basis waktunya
   * cacahan PPG (dikunci tick FreeRTOS/kristal ESP32), jadi angka ini jauh
   * lebih dipercaya daripada MAX_FS_HZ nominal. Kalau meleset jauh dari
   * MAX_FS_HZ, kombinasi SR/pulse-width di CFG_SPO2 tidak dilayani chip. */
  const uint32_t ppgN = g_stats.ppg_samples;
  const float fsMaxMeas = ppgN ? ((float)g_stats.max_samples * PPG_FS_HZ / (float)ppgN) : 0.0f;

  Serial.printf(
    "       ppg=%lu max=%lu (fs_max_ukur=%.1f Hz) | ovf=%lu overrun=%lu trunc=%lu\n",
    (unsigned long)ppgN, (unsigned long)g_stats.max_samples, fsMaxMeas,
    (unsigned long)g_stats.max_ovf_total, (unsigned long)g_stats.ppg_overrun,
    (unsigned long)g_stats.max_trunc);

  /* Gerbang SQI. lolos+tolak = package yang sempat dinilai; sisanya terhadap
   * batch made adalah yang keburu dibuang di pool karena jaringan tertinggal. */
  const uint32_t sqiTot = g_stats.sqi_pass + g_stats.sqi_reject;
  char sqiWhy[SQI_FLAGS_TEXT_CAP];
  sqiFlagsText(g_stats.sqi_last_flags, sqiWhy, sizeof(sqiWhy));
  Serial.printf(
    "       sqi lolos=%lu tolak=%lu (%lu%%) | skor terakhir=%u alasan=%s\n",
    (unsigned long)g_stats.sqi_pass, (unsigned long)g_stats.sqi_reject,
    (unsigned long)(sqiTot ? g_stats.sqi_pass * 100UL / sqiTot : 0),
    (unsigned)g_stats.sqi_last_score, sqiWhy);

  Serial.printf(
    "       batt=%u mV (%u%%) | rssi=%d dBm | heap=%lu\n",
    (unsigned)g_battMv, (unsigned)g_battPct,
    (int)WiFi.RSSI(), (unsigned long)ESP.getFreeHeap());
}

// =====================================================================
// setup()
// =====================================================================
void setup() {
  /* LED & power-gate sensor: amankan dulu sebelum apa pun.
   * digitalWrite DULU baru pinMode — kalau dibalik, pin sempat menggerakkan
   * LOW (level default output) beberapa mikrodetik, dan LOW di D2 = MOSFET
   * nyambung, alias SON1303 sempat berkedut hidup. */
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);   // SON1303 tetap mati sampai WiFi siap
  pinMode(PIN_SEN_EN, OUTPUT);
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
  /* LED lewat LEDC sejak awal. Attach dulu, baru tulis 0 — supaya pin tidak
   * sempat menyala sekejap saat boot. */
  LED_PWM_ATTACH();
  LED_PWM_WRITE(0);

  Serial.begin(SERIAL_BAUD);
  const uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) delay(10);   // USB-CDC, jangan blok selamanya

  Serial.println(F("\n\n======================================"));
  Serial.println(F("  ANTARAGA Smartband — mode STREAMING"));
  Serial.println(F("======================================"));
  Serial.printf("Firmware : %s  (partisi %s)\n", FW_VERSION,
                esp_ota_get_running_partition() ? esp_ota_get_running_partition()->label : "?");
  Serial.printf("Device   : %s\n", DEVICE_ID);
  Serial.printf("Endpoint : https://%s:%d%s\n", CLOUD_HOST, CLOUD_PORT, CLOUD_PATH);
  Serial.printf("MAX30102 : %d Hz (RED+IR, FIFO)\n", MAX_FS_HZ);
  Serial.printf("SON1303  : %d Hz (oversample %dx, pin A1/GPIO2)\n",
                PPG_FS_HZ, PPG_OVERSAMPLE);
  Serial.printf("Batch    : %d ms -> %d ppg + ~%d max/kanal, pool %d (~%d ms buffer)\n",
                BATCH_MS, PPG_PER_BATCH, MAX_PER_BATCH, BATCH_POOL,
                (BATCH_POOL - 1) * BATCH_MS);
  Serial.printf("RAM pool : %u byte\n", (unsigned)sizeof(s_pool));
  Serial.println(F("--------------------------------------"));

  // --- Primitif sinkronisasi ------------------------------------------
  g_events  = xEventGroupCreate();
  g_qFree   = xQueueCreate(BATCH_POOL, sizeof(Batch*));
  g_qFilled = xQueueCreate(BATCH_POOL, sizeof(Batch*));
  if (!g_events || !g_qFree || !g_qFilled) {
    Serial.println(F("FATAL: gagal membuat queue/event group."));
    setState(ST_ERROR);
    return;
  }
  for (int i = 0; i < BATCH_POOL; i++) {
    Batch* p = &s_pool[i];
    xQueueSend(g_qFree, &p, 0);
  }

  // --- Dua core, dua tugas --------------------------------------------
  // Core 0: WiFi/TLS. Stack besar karena handshake TLS rakus stack.
  xTaskCreatePinnedToCore(netTask, "net", 12288, nullptr, 4, nullptr, 0);
  // Core 1: akuisisi. Prioritas di atas loopTask (=1) supaya timing 5 ms terjaga.
  xTaskCreatePinnedToCore(sensorTask, "sensor", 6144, nullptr, 6, nullptr, 1);
}

// =====================================================================
// loop() — berjalan di core 1, prioritas terendah: LED + statistik
// =====================================================================
void loop() {
  static uint32_t lastStat = 0;

  ledService();

  const uint32_t now = millis();
  if (now - lastStat >= STAT_PERIOD_MS) {
    lastStat = now;
    printStats();
  }
  delay(10);
}
