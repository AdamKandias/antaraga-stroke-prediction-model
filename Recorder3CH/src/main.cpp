/**
 * ANTARAGA — PEREKAM 3 KANAL PPG MENTAH (RED + IR + HIJAU)
 * =====================================================================
 * Papan  : XIAO ESP32-S3, pin sesuai skematik ANTARAGA
 * Keluar : CSV per sampel ke serial, dibaca GUI di gui/plotter.py
 *
 * TIGA KANAL, DUA SENSOR, TIGA PANJANG GELOMBANG:
 *   MERAH      660 nm  <- MAX30102 LED1, I2C via FIFO
 *   INFRAMERAH 880 nm  <- MAX30102 LED2, I2C via FIFO
 *   HIJAU      525 nm  <- SON1303, keluaran analog di A1/GPIO2
 *
 * CATATAN DAYA (dari skematik, dan ini penting):
 *   MAX30102 (J3) mendapat 3V3 LANGSUNG lewat ferrite B2 + C5/C6.
 *   Ia TIDAK lewat Q2, jadi ia hidup terus dan tidak peduli keadaan D2.
 *   SON1303 (J2) yang dicatu lewat Q2 (DMP2130L, P-MOS): D2 LOW = nyala,
 *   dan R5 100k menariknya ke 3V3 supaya default-nya mati saat boot.
 *
 *   Konsekuensi praktis: kanal HIJAU butuh D2 LOW, kanal MERAH/INFRAMERAH
 *   tidak. Karena itu perintah 'g' hanya mematikan hijau — dua kanal
 *   MAX30102 tetap mengalir. Itu justru cara termurah membuktikan apakah
 *   LED hijau SON1303 ikut terbaca fotodioda MAX30102: matikan hijau
 *   sambil melihat DC merah/inframerah di GUI.
 *
 * BASIS WAKTU — dan kenapa dirancang begini:
 *   Loop ini DIKENDALIKAN FIFO MAX30102, bukan tick FreeRTOS. Setiap kali
 *   chip menghasilkan satu sampel, sampel itu diambil dan ADC hijau dibaca
 *   pada saat yang sama, lalu satu baris CSV dikirim. Akibatnya:
 *
 *     - tidak ada baris yang berisi merah/inframerah basi,
 *     - hijau selalu tercuplik dalam ~1 ms dari pasangannya,
 *     - laju baris = laju NYATA chip, apa pun yang tertulis di register.
 *
 *   Kolom t_ms adalah millis() SUNGGUHAN saat sampel dibaca, BUKAN hasil
 *   perkalian indeks dengan laju nominal. Ini disengaja: recorder lamamu
 *   (max30102_recorder_pwa_xiao_c3.ino) menghitung t_ms dari FS nominal,
 *   dan karena MAX30102 diam-diam meng-clamp SR ke 400 Hz, seluruh timing
 *   di file itu meleset 2x tanpa satu pun tanda. Dengan t_ms nyata, kelas
 *   kesalahan itu tidak bisa terjadi lagi.
 *
 * PERINTAH SERIAL (satu karakter):
 *   i  cetak ulang blok info      p  jeda / lanjut aliran
 *   g  hijau (SON1303) mati/nyala z  nolkan cacahan
 *   r/R  arus MERAH turun/naik    f/F  arus INFRAMERAH turun/naik
 *   h  bantuan
 */

#include <Arduino.h>
#include <Wire.h>

// =====================================================================
// SETELAN
// =====================================================================
#define PIN_SIG_PPG      2      // D1 / A1  <- keluaran analog SON1303 (J2)
#define PIN_SEN_EN       3      // D2       -> gate Q2, LOW = SON1303 nyala
#define PIN_SDA          5      // D4       <-> MAX30102 (J3)
#define PIN_SCL          6      // D5       <-> MAX30102 (J3)
#define SEN_POWER_ON     LOW
#define SEN_POWER_OFF    HIGH

#define I2C_HZ           400000
/* Di XIAO ESP32-S3 serial-nya USB-CDC asli, jadi angka baud ini praktis
 * tidak berpengaruh pada laju sebenarnya (~1 MB/s). Dipasang tinggi supaya
 * tetap benar kalau suatu saat dipakai lewat jembatan UART. */
#define SERIAL_BAUD      921600

/* 2026-07-31: sempat dinaikkan ke 64 dengan dugaan riak HIJAU adalah
 * alias/noise acak yang bisa dirata-ratakan. Terbukti SALAH — riaknya
 * ternyata interferensi ground yang mengambang (berubah drastis hanya
 * karena menyentuh/tidak menyentuh pin GND), jadi oversample lebih
 * banyak tidak menolong sama sekali. Dikembalikan ke 16. Perbaikan yang
 * benar ada di hardware: kapasitor filter di GPIO2/A1 + jalur GND
 * SON1303 yang lebih pendek/solid ke ESP32, bukan di firmware. */
#define GREEN_OVERSAMPLE 16

// Jeda setelah SON1303 dicatu, sebelum barisnya dianggap layak.
#define GREEN_SETTLE_MS  1000

/* MAX30102: SR=400 Hz, PW=411 us (18-bit), ADC_RGE=8192 nA, SMP_AVE=2
 * -> keluaran ~200 Hz (terukur ~196 Hz; osilator internal chip meleset
 * beberapa persen, dan itu sebabnya t_ms nyata dikirim per baris).
 *
 * JANGAN meminta SR di atas 400 Hz di mode SpO2 dengan PW 411 us: chip
 * meng-clamp diam-diam ke 400 Hz, jadi meminta 800 Hz dengan SMP_AVE=2
 * menghasilkan 200 Hz, bukan 400 Hz. Sudah terukur di ../DiagMAX30102.
 *
 * Mau ~400 Hz penuh? Ganti CFG_FIFO ke 0x10 (SMP_AVE=1). Tidak ada lagi
 * yang perlu disentuh — loop ini mengikuti laju chip, bukan tick tetap. */
#define SR_DEFAULT       3      // 0=50 1=100 2=200 3=400 4=800 5=1000 Hz
#define PW_DEFAULT       3      // 3 = 411 us (18-bit) — integrasi terpanjang
#define AVE_DEFAULT      1      // SMP_AVE: 0=1 1=2 2=4 3=8 4=16 5=32
/* 2026-07-31: sempat dicoba 0xA0 (~32 mA) supaya DC merah yang cuma 38%
 * skala penuh punya lebih banyak sinyal. Hasilnya JUSTRU lebih parah di
 * KETIGA kanal (DC hijau ambruk 1281->185, BPM merah/hijau ngaco ~200) —
 * lonjakan arus LED merah yang lebih besar tampaknya cukup untuk
 * mengganggu rel 3V3 yang juga dipakai SON1303 (penguat analog jauh lebih
 * peka terhadap itu daripada FIFO digital MAX30102). Dikembalikan ke
 * 0x6F. Kalau mau menaikkan sinyal merah lagi, naikkan SEDIKIT lewat
 * perintah live 'R' (langkah 0x10/~3,2 mA) sambil mengawasi DC ketiga
 * kanal di GUI, jangan lompat besar di firmware. */
#define LED_RED_DEFAULT  0x6F   // ~22 mA
#define LED_IR_DEFAULT   0x5F   // ~19 mA
#define LED_STEP         0x10   // langkah perintah r/R/f/F (~3,2 mA)

/* ADC_RGE — tuas tuning yang paling sering dilupakan.
 *
 * 0=2048 nA  1=4096 nA  2=8192 nA  3=16384 nA (skala penuh fotodioda)
 *
 * Rentang yang lebih KECIL berarti lebih peka: arus foto yang sama
 * menghasilkan lebih banyak cacahan. Derau elektronik ADC (dalam LSB)
 * hampir tidak berubah, jadi memperkecil rentang menaikkan SNR hampir
 * sebanding — SELAMA DC-nya belum mentok. Ini gratis: tidak menambah arus
 * LED sama sekali, malah memungkinkan arus DITURUNKAN untuk cacahan yang
 * sama, sehingga baterainya ikut hemat.
 *
 * Bahwa derau di sini memang didominasi elektronik, bukan foton, sudah
 * terukur: pada DC 81.552 LSB derau tembakan foton hanya ~1 LSB sementara
 * derau terukur ~5,1 LSB. */
#define RGE_DEFAULT      2      // 8192 nA, sama dengan ../Firmware

#define STAT_PERIOD_MS   5000

// =====================================================================
// Lapisan ADC — shim Arduino core 2.x / 3.x
// =====================================================================
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  #include "esp_adc/adc_oneshot.h"
  #define ADC_CH_GREEN   ADC_CHANNEL_1        // GPIO2 = A1
  typedef adc_channel_t AdcChan;
  static adc_oneshot_unit_handle_t s_adc = nullptr;

  static bool adcInit() {
    adc_oneshot_unit_init_cfg_t u = {};
    u.unit_id  = ADC_UNIT_1;
    u.ulp_mode = ADC_ULP_MODE_DISABLE;
    if (adc_oneshot_new_unit(&u, &s_adc) != ESP_OK) return false;
    adc_oneshot_chan_cfg_t c = {};
    c.atten    = ADC_ATTEN_DB_12;             // ~0..3,1 V
    c.bitwidth = ADC_BITWIDTH_12;             // 0..4095
    return adc_oneshot_config_channel(s_adc, ADC_CH_GREEN, &c) == ESP_OK;
  }
  static inline int adcRaw(AdcChan ch) {
    int v = 0;
    return (adc_oneshot_read(s_adc, ch, &v) == ESP_OK) ? v : -1;
  }
#else
  #include "driver/adc.h"
  #define ADC_CH_GREEN   ADC1_CHANNEL_1
  typedef adc1_channel_t AdcChan;
  static bool adcInit() {
    if (adc1_config_width(ADC_WIDTH_BIT_12) != ESP_OK) return false;
    return adc1_config_channel_atten(ADC_CH_GREEN, ADC_ATTEN_DB_11) == ESP_OK;
  }
  static inline int adcRaw(AdcChan ch) { return adc1_get_raw(ch); }
#endif

static uint32_t s_adcFail = 0;

/* Nilai MENTAH, tidak diubah ke mV. Kalibrasi eFuse bersifat monoton, jadi
 * mengubahnya ke mV tidak menambah informasi apa pun untuk analisis bentuk
 * gelombang — sementara tetap di domain raw membuat angkanya bisa langsung
 * dibandingkan dengan kolom adc_raw rekaman-rekaman lamamu. */
static uint16_t greenRead() {
  uint32_t acc = 0;
  uint8_t  ok  = 0;
  for (uint8_t i = 0; i < GREEN_OVERSAMPLE; i++) {
    const int v = adcRaw((AdcChan)ADC_CH_GREEN);
    if (v >= 0) { acc += (uint32_t)v; ok++; }
  }
  if (ok != GREEN_OVERSAMPLE) s_adcFail += (uint32_t)(GREEN_OVERSAMPLE - ok);
  return ok ? (uint16_t)(acc / ok) : 0;
}

// =====================================================================
// MAX30102
// =====================================================================
#define ADDR             0x57
#define R_FIFO_WR        0x04
#define R_OVF            0x05
#define R_FIFO_RD        0x06
#define R_FIFO_DATA      0x07
#define R_FIFO_CFG       0x08
#define R_MODE           0x09
#define R_SPO2           0x0A
#define R_LED1           0x0C   // RED
#define R_LED2           0x0D   // IR
#define R_REV_ID         0xFE
#define R_PART_ID        0xFF
#define MODE_SHDN        0x80
#define MODE_RESET       0x40
#define MODE_SPO2        0x03

static uint32_t s_i2cErr = 0;

static bool regWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(ADDR);
  Wire.write(reg);
  Wire.write(val);
  if (Wire.endTransmission() != 0) { s_i2cErr++; return false; }
  return true;
}

static bool regRead(uint8_t reg, uint8_t* out) {
  Wire.beginTransmission(ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) { s_i2cErr++; return false; }
  if (Wire.requestFrom((int)ADDR, 1) < 1)  { s_i2cErr++; return false; }
  *out = Wire.read();
  return true;
}

static uint8_t regReadOr(uint8_t reg, uint8_t fb) {
  uint8_t v;
  return regRead(reg, &v) ? v : fb;
}

static bool readPtrs(uint8_t& wr, uint8_t& ovf, uint8_t& rd) {
  Wire.beginTransmission(ADDR);
  Wire.write(R_FIFO_WR);
  if (Wire.endTransmission(false) != 0) { s_i2cErr++; return false; }
  if (Wire.requestFrom((int)ADDR, 3) < 3)  { s_i2cErr++; return false; }
  wr = Wire.read(); ovf = Wire.read(); rd = Wire.read();
  return true;
}

static void fifoClear() {
  regWrite(R_FIFO_WR, 0);
  regWrite(R_OVF, 0);
  regWrite(R_FIFO_RD, 0);
}

// Satu sampel = 6 byte: RED 3 byte lalu IR 3 byte (urutan slot mode SpO2).
static bool fifoReadOne(uint32_t& red, uint32_t& ir) {
  Wire.beginTransmission(ADDR);
  Wire.write(R_FIFO_DATA);
  if (Wire.endTransmission(false) != 0) { s_i2cErr++; return false; }
  if (Wire.requestFrom((int)ADDR, 6) < 6)  { s_i2cErr++; return false; }
  uint8_t b[6];
  for (uint8_t i = 0; i < 6; i++) b[i] = Wire.read();
  red = (((uint32_t)b[0] << 16) | ((uint32_t)b[1] << 8) | b[2]) & 0x03FFFF;
  ir  = (((uint32_t)b[3] << 16) | ((uint32_t)b[4] << 8) | b[5]) & 0x03FFFF;
  return true;
}

static uint8_t s_ledRed = LED_RED_DEFAULT;
static uint8_t s_ledIr  = LED_IR_DEFAULT;
static uint8_t s_rge    = RGE_DEFAULT;
static uint8_t s_sr     = SR_DEFAULT;
static uint8_t s_pw     = PW_DEFAULT;
static uint8_t s_ave    = AVE_DEFAULT;

static inline uint8_t cfgSpo2() {
  return (uint8_t)(((s_rge & 3) << 5) | ((s_sr & 7) << 2) | (s_pw & 3));
}
static inline uint8_t cfgFifo() {
  return (uint8_t)(((s_ave & 7) << 5) | 0x10);   // + FIFO_ROLLOVER_EN
}
static const uint16_t kRgeNa[4] = {2048, 4096, 8192, 16384};
static const uint16_t kSrHz[8]  = {50, 100, 200, 400, 800, 1000, 1600, 3200};
static const uint16_t kPwUs[4]  = {69, 118, 215, 411};

static void applyCfg() {
  regWrite(R_FIFO_CFG, cfgFifo());
  regWrite(R_SPO2, cfgSpo2());
  regWrite(R_LED1, s_ledRed);
  regWrite(R_LED2, s_ledIr);
  fifoClear();
}

/* Dicetak setiap kali setelan berubah. Penyetel otomatis (gui/tune.py)
 * MENUNGGU baris ini sebelum mulai mengukur, jadi tidak ada sapuan yang
 * mengukur setelan lama karena perintahnya belum sempat berlaku. */
static void printCfg() {
  Serial.printf("#cfg rge=%u(%unA) sr=%u(%uHz) pw=%u(%uus) ave=%u(%u)"
                " led_red=0x%02X(%.1fmA) led_ir=0x%02X(%.1fmA)\n",
                s_rge, kRgeNa[s_rge & 3], s_sr, kSrHz[s_sr & 7],
                s_pw, kPwUs[s_pw & 3], s_ave, (unsigned)(1u << (s_ave & 7)),
                s_ledRed, s_ledRed * 0.2f, s_ledIr, s_ledIr * 0.2f);
}

static bool maxBegin() {
  if (regReadOr(R_PART_ID, 0x00) != 0x15) return false;
  regWrite(R_MODE, MODE_RESET);
  delay(60);
  const uint32_t t0 = millis();
  while ((regReadOr(R_MODE, 0) & MODE_RESET) && millis() - t0 < 600) delay(2);

  fifoClear();
  applyCfg();
  regWrite(R_MODE, MODE_SPO2);      // langsung jalan, tanpa mampir SHUTDOWN
  fifoClear();
  return true;
}

// =====================================================================
// Keadaan
// =====================================================================
static bool     s_greenOn  = true;    // gate Q2 (hanya mempengaruhi HIJAU)
static bool     s_paused   = false;
static bool     s_ready    = false;   // GREEN_SETTLE_MS sudah lewat
static uint32_t s_rows     = 0;
static uint32_t s_late     = 0;       // baris saat FIFO sudah menumpuk (av > 1)
static uint32_t s_t0       = 0;
static uint32_t s_lastStat = 0;

static void greenApply() {
  digitalWrite(PIN_SEN_EN, s_greenOn ? SEN_POWER_ON : SEN_POWER_OFF);
}

static void printInfo() {
  Serial.println(F("#ANTARAGA3CH v1"));
  Serial.println(F("#ch=t_ms,green,red,ir,av"));
  Serial.printf("#wl green=525nm(SON1303,A1) red=660nm(MAX30102) ir=880nm(MAX30102)\n");
  Serial.printf("#range green=0..4095(12bit,oversample%u) red/ir=0..262143(18bit)\n",
                (unsigned)GREEN_OVERSAMPLE);
  Serial.printf("#max spo2=0x%02X fifo=0x%02X led_red=0x%02X led_ir=0x%02X"
                " rev=0x%02X part=0x%02X\n",
                (unsigned)regReadOr(R_SPO2, 0xEE), (unsigned)regReadOr(R_FIFO_CFG, 0xEE),
                (unsigned)regReadOr(R_LED1, 0xEE), (unsigned)regReadOr(R_LED2, 0xEE),
                (unsigned)regReadOr(R_REV_ID, 0xEE), (unsigned)regReadOr(R_PART_ID, 0xEE));
  printCfg();
  Serial.printf("#green_power=%s (gate Q2/D2; MAX30102 TIDAK lewat gate ini)\n",
                s_greenOn ? "on" : "off");
  Serial.println(F("#note t_ms = millis() nyata saat sampel dibaca, bukan indeks x laju nominal"));
  Serial.println(F("#cmd i=info p=jeda g=hijau z=nol r/R=red-/+ f/F=ir-/+ h=bantuan"));
}

static void printHelp() {
  Serial.println(F("# i info | p jeda-lanjut | g hijau mati-nyala | z nolkan cacahan"));
  Serial.println(F("# r/R arus MERAH turun/naik | f/F arus INFRAMERAH turun/naik"));
  Serial.println(F("# d/D rentang ADC peka/kasar | a/A averaging turun/naik"));
  Serial.println(F("# setel absolut (heksa/desimal, diakhiri newline):"));
  Serial.println(F("#   =r6F  arus merah      =f5F  arus inframerah"));
  Serial.println(F("#   =d1   rentang ADC 0..3 =a1   SMP_AVE 0..5   =s3  SR 0..7"));
}

/* Perintah setel-ABSOLUT, dipakai penyetel otomatis.
 *
 * Perintah relatif (r/R/f/F) tidak cukup untuk sapuan: skrip harus tahu
 * nilai sekarang dan menghitung berapa langkah, dan satu perintah yang
 * hilang membuat seluruh sisa sapuan mengukur setelan yang salah tanpa
 * ada yang tahu. Bentuk absolut membuat tiap titik sapuan berdiri sendiri.
 *
 * Format: '=' <huruf> <angka heksa> <newline>, mis. "=r6F\n".
 */
static char    s_setBuf[12];
static uint8_t s_setLen = 0;

static void handleSet(const char* s) {
  if (!s[0] || !s[1]) return;
  const char what = s[0];
  const long v = strtol(s + 1, nullptr, 16);
  switch (what) {
    case 'r': s_ledRed = (uint8_t)constrain(v, 0, 255); break;
    case 'f': s_ledIr  = (uint8_t)constrain(v, 0, 255); break;
    case 'd': s_rge    = (uint8_t)constrain(v, 0, 3);   break;
    case 'a': s_ave    = (uint8_t)constrain(v, 0, 5);   break;
    case 's': s_sr     = (uint8_t)constrain(v, 0, 7);   break;
    case 'w': s_pw     = (uint8_t)constrain(v, 0, 3);   break;
    default:  Serial.println(F("#err setel tidak dikenal")); return;
  }
  applyCfg();
  printCfg();
}

static void handleCmd(int c) {
  // Rakit perintah "=xNN\n" dulu; sisanya perintah satu karakter.
  if (s_setLen || c == '=') {
    if (c == '\n' || c == '\r') {
      s_setBuf[s_setLen] = '\0';
      handleSet(s_setBuf + 1);            // lewati '='
      s_setLen = 0;
    } else if (s_setLen < sizeof(s_setBuf) - 1) {
      s_setBuf[s_setLen++] = (char)c;
    } else {
      s_setLen = 0;                        // kepanjangan -> buang
      Serial.println(F("#err perintah kepanjangan"));
    }
    return;
  }

  switch (c) {
    case 'i': printInfo(); break;
    case 'h': printHelp(); break;
    case 'p':
      s_paused = !s_paused;
      Serial.printf("#paused=%d\n", s_paused ? 1 : 0);
      break;
    case 'g':
      s_greenOn = !s_greenOn;
      greenApply();
      /* Hanya HIJAU yang terpengaruh. MERAH/INFRAMERAH terus mengalir
       * karena MAX30102 dicatu langsung dari 3V3 lewat ferrite B2. */
      Serial.printf("#green_power=%s (merah/inframerah tidak terpengaruh)\n",
                    s_greenOn ? "on" : "off");
      break;
    case 'z':
      s_rows = 0; s_late = 0; s_i2cErr = 0; s_adcFail = 0;
      s_t0 = millis();
      Serial.println(F("#counters=0"));
      break;
    case 'r': case 'R': {
      const int v = (int)s_ledRed + ((c == 'R') ? LED_STEP : -LED_STEP);
      s_ledRed = (uint8_t)constrain(v, 0, 255);
      regWrite(R_LED1, s_ledRed);
      Serial.printf("#led_red=0x%02X (%.1f mA)\n", s_ledRed, s_ledRed * 0.2f);
      break;
    }
    case 'f': case 'F': {
      const int v = (int)s_ledIr + ((c == 'F') ? LED_STEP : -LED_STEP);
      s_ledIr = (uint8_t)constrain(v, 0, 255);
      regWrite(R_LED2, s_ledIr);
      Serial.printf("#led_ir=0x%02X (%.1f mA)\n", s_ledIr, s_ledIr * 0.2f);
      break;
    }
    case 'd': case 'D':
      // 'd' = lebih PEKA (rentang mengecil), 'D' = lebih kasar.
      s_rge = (uint8_t)constrain((int)s_rge + ((c == 'D') ? 1 : -1), 0, 3);
      applyCfg();
      printCfg();
      break;
    case 'a': case 'A':
      s_ave = (uint8_t)constrain((int)s_ave + ((c == 'A') ? 1 : -1), 0, 5);
      applyCfg();
      printCfg();
      break;
    default: break;
  }
}

// =====================================================================
void setup() {
  /* Amankan gate sebelum apa pun: digitalWrite DULU baru pinMode, karena
   * kalau dibalik pin sempat menggerakkan LOW (level default output) dan
   * LOW di D2 berarti SON1303 sempat berkedut hidup. */
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);
  pinMode(PIN_SEN_EN, OUTPUT);
  digitalWrite(PIN_SEN_EN, SEN_POWER_OFF);

  Serial.begin(SERIAL_BAUD);
  const uint32_t tb = millis();
  while (!Serial && millis() - tb < 2000) delay(10);
  delay(200);

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(I2C_HZ);
  Wire.setTimeOut(50);

  if (!adcInit()) {
    Serial.println(F("#FATAL adc1 gagal init"));
    while (1) delay(1000);
  }

  /* Nyalakan & tunggu SON1303 settle SEBELUM MAX30102 mulai berdenyut —
   * bukan sesudahnya. Urutan lama (maxBegin dulu, baru greenApply+settle)
   * berarti MAX30102 sudah memompa LED pada arus target SEPANJANG jendela
   * settle 1 detik SON1303, jadi op-amp SON1303 mencoba mencari titik
   * bias diam sambil rel 3V3-nya masih kena denyut LED MAX30102 di latar
   * belakang. Itu terbukti (2026-07-31) menghasilkan HIJAU redup kalau
   * arus default MAX30102 tinggi saat boot — padahal menaikkan arus yang
   * SAMA lewat perintah live 'R'/'F' setelah semuanya jalan lama tidak
   * bermasalah sama sekali, karena SON1303 saat itu sudah lama settle
   * dan tidak sedang mencari bias. Membalik urutan (settle dulu, MAX30102
   * menyusul) membuat baseline HIJAU terkunci sebelum LED MAX30102 aktif,
   * berapa pun arus targetnya. */
  s_greenOn = true;
  greenApply();
  Serial.printf("#settle %u ms (baseline op-amp SON1303, sebelum MAX30102 aktif)\n",
                (unsigned)GREEN_SETTLE_MS);
  const uint32_t ts = millis();
  while (millis() - ts < GREEN_SETTLE_MS) { (void)greenRead(); delay(2); }

  if (!maxBegin()) {
    Serial.println(F("#FATAL MAX30102 tidak terdeteksi di I2C 0x57"));
    Serial.println(F("#cek SDA=D4/GPIO5, SCL=D5/GPIO6, dan 3V3 lewat ferrite B2"));
    Serial.println(F("#(MAX30102 tidak lewat Q2, jadi keadaan D2 tidak relevan di sini)"));
    while (1) delay(1000);
  }

  printInfo();

  s_ready    = true;
  s_t0       = millis();
  s_lastStat = s_t0;
  Serial.println(F("#start"));
}

void loop() {
  while (Serial.available()) handleCmd(Serial.read());

  const uint32_t now = millis();
  if (now - s_lastStat >= STAT_PERIOD_MS) {
    s_lastStat = now;
    const uint32_t el = now - s_t0;
    Serial.printf("#stat t=%lu rows=%lu fs=%.1f late=%lu i2c_err=%lu adc_fail=%lu"
                  " green=%s\n",
                  (unsigned long)el, (unsigned long)s_rows,
                  el ? (float)s_rows * 1000.0f / (float)el : 0.0f,
                  (unsigned long)s_late, (unsigned long)s_i2cErr,
                  (unsigned long)s_adcFail, s_greenOn ? "on" : "off");
  }

  uint8_t wr, ovf, rd;
  if (!readPtrs(wr, ovf, rd)) { delay(1); return; }
  const uint8_t av = (uint8_t)((wr - rd) & 0x1F);
  if (!av) {
    /* delay(1) dan bukan busy-wait: periodenya ~5 ms jadi 1 ms tidak akan
     * melewatkan sampel, sementara menyerahkan CPU membuat task USB-CDC
     * kebagian jalan — kalau tidak, keluaran serial malah tersendat. */
    delay(1);
    return;
  }

  /* Satu sampel per iterasi, bukan seluruh FIFO. Dengan begitu setiap baris
   * memasangkan merah/inframerah dengan bacaan hijau yang diambil pada
   * saat yang sama; menguras 32 sampel sekaligus akan memasangkan 32 baris
   * ke SATU nilai hijau. */
  uint32_t red = 0, ir = 0;
  if (!fifoReadOne(red, ir)) return;
  const uint16_t green = greenRead();
  const uint32_t t     = millis();

  if (av > 1) s_late++;
  s_rows++;

  if (!s_paused && s_ready)
    Serial.printf("%lu,%u,%lu,%lu,%u\n", (unsigned long)t, (unsigned)green,
                  (unsigned long)red, (unsigned long)ir, (unsigned)av);
}
