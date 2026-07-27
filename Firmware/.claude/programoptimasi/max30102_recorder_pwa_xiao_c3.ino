/*
 * MAX30102 Recorder PWA-OPTIMAL (RED+IR) — XIAO ESP32-C3
 * ====================================================================
 * Disetel untuk mendukung analisis PWA: laju sampel lebih tinggi, arus
 * LED lebih besar (SNR naik), averaging tetap rendah (jaga morfologi),
 * pulse width 18-bit. Output: t_ms, red_raw, ir_raw
 *
 * BATAS HARDWARE yang dihormati (XIAO ESP32-C3):
 *   - CPU RISC-V 160 MHz: sanggup; BUKAN bottleneck.
 *   - Bottleneck = throughput SERIAL vs kedalaman FIFO MAX30102 (32 sampel).
 *     Mencetak 2 kanal teks ~24 byte/sampel:
 *       200 Hz -> ~4.8 kB/s   (aman di 115200)
 *       250 Hz -> ~6.0 kB/s   (aman di 115200)
 *       400 Hz -> ~9.6 kB/s   (~83% dari 115200 -> RAWAN; butuh baud tinggi)
 *   - Karena itu: MODE 400 Hz OTOMATIS menaikkan baud ke 921600.
 *     >>> WAJIB set Serial Monitor ke baud yang sama dengan yang tercetak. <<<
 *
 * PILIH SATU profil lewat PROFILE di bawah:
 *   PROFILE_SAFE  : 250 Hz @ 115200 baud  (paling aman, tak perlu ubah apa2)
 *   PROFILE_PWA   : 400 Hz @ 921600 baud  (resolusi terbaik utk PWA;
 *                                          UBAH baud Serial Monitor ke 921600)
 *
 * Hanya untuk BARE MAX30102. Wiring: SDA=D4(GPIO6), SCL=D5(GPIO7),
 * VIN=3V3, GND=GND.
 */

#include <Wire.h>

// ================== PILIH PROFIL ==================
#define PROFILE_SAFE  0
#define PROFILE_PWA   1
#define PROFILE       PROFILE_PWA     // <-- ganti ke PROFILE_SAFE bila perlu

// ---------- Pin & I2C ----------
#define SDA_PIN        6
#define SCL_PIN        7
#define I2C_CLOCK      400000
#define MAX30102_ADDR  0x57

// ---------- Register ----------
#define REG_FIFO_WR_PTR  0x04
#define REG_OVF_COUNTER  0x05
#define REG_FIFO_RD_PTR  0x06
#define REG_FIFO_DATA    0x07
#define REG_FIFO_CONFIG  0x08
#define REG_MODE_CONFIG  0x09
#define REG_SPO2_CONFIG  0x0A
#define REG_LED1_PA      0x0C   // RED
#define REG_LED2_PA      0x0D   // IR
#define REG_PART_ID      0xFF

// ---------- Parameter rekaman ----------
#define RECORD_SECONDS  30      // 60 dtk -> ~70-80 detak utk ensemble average
#define WARMUP_SECONDS  3

// Arus LED terpisah (headroom ADC besar; naikkan DC -> SNR naik).
// Dari data punggung wrist-mu, target DC ~120-180k, aman dari batas 262143.
#define LED_RED  0x6F           // ~22 mA (RED lebih dipentingkan utk morfologi)
#define LED_IR   0x5F           // ~19 mA

// ---------- Profil akuisisi ----------
#if PROFILE == PROFILE_PWA
  #define SERIAL_BAUD 921600
  // SPO2: ADC_RGE=8192nA(0b10<<5) | SR=800Hz(0b100<<2) | PW=411us(0b11)
  //   -> ADC 800 Hz, SMP_AVE=2 -> keluaran 400 Hz
  #define CFG_SPO2   0x53
  #define CFG_FIFO   0x30        // SMP_AVE=2 (0b001) + ROLLOVER_EN
  #define FS_HZ      400         // integer (utk praprosesor)
#else  // PROFILE_SAFE
  #define SERIAL_BAUD 115200
  // SPO2: ADC_RGE=8192nA | SR=1000Hz(0b101<<2) | PW=411us -> ADC 1000 Hz
  //   SMP_AVE=4 -> keluaran 250 Hz
  #define CFG_SPO2   0x57
  #define CFG_FIFO   0x50        // SMP_AVE=4 + ROLLOVER_EN
  #define FS_HZ      250         // integer (utk praprosesor)
#endif
#define CFG_MODE   0x03          // SpO2 (RED+IR)
#define FS ((float)FS_HZ)        // versi float utk perhitungan runtime

// ============ Cek keamanan throughput (compile-time) ============
// ~24 byte/sampel * FS harus < ~90% kapasitas baud (baud/10 byte/s).
// Semua integer agar sah di praprosesor. Ekiv: FS*24*1000 > BAUD*90.
#if (FS_HZ * 24 * 1000) > (SERIAL_BAUD * 90)
  #error "Throughput serial terlalu tinggi utk baud ini. Pakai PROFILE_SAFE atau naikkan baud."
#endif

// ================= I2C helpers =================
void writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MAX30102_ADDR);
  Wire.write(reg); Wire.write(val);
  Wire.endTransmission();
}
uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(MAX30102_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((int)MAX30102_ADDR, 1);
  return Wire.available() ? Wire.read() : 0;
}
bool maxInit() {
  if (readReg(REG_PART_ID) != 0x15) return false;
  writeReg(REG_MODE_CONFIG, 0x40); delay(50);
  while (readReg(REG_MODE_CONFIG) & 0x40) delay(1);
  writeReg(REG_FIFO_WR_PTR, 0); writeReg(REG_OVF_COUNTER, 0);
  writeReg(REG_FIFO_RD_PTR, 0);
  writeReg(REG_FIFO_CONFIG, CFG_FIFO);
  writeReg(REG_SPO2_CONFIG, CFG_SPO2);
  writeReg(REG_LED1_PA, LED_RED);
  writeReg(REG_LED2_PA, LED_IR);
  writeReg(REG_MODE_CONFIG, CFG_MODE);
  return true;
}
uint8_t samplesAvailable() {
  uint8_t wr = readReg(REG_FIFO_WR_PTR);
  uint8_t rd = readReg(REG_FIFO_RD_PTR);
  return (uint8_t)((wr - rd) & 0x1F);
}
uint8_t ovfCount() { return readReg(REG_OVF_COUNTER); }
bool readSample(uint32_t &red, uint32_t &ir) {
  Wire.beginTransmission(MAX30102_ADDR);
  Wire.write(REG_FIFO_DATA);
  Wire.endTransmission(false);
  if (Wire.requestFrom((int)MAX30102_ADDR, 6) < 6) return false;
  uint8_t b[6];
  for (int i = 0; i < 6; i++) b[i] = Wire.read();
  red = (((uint32_t)b[0]<<16)|((uint32_t)b[1]<<8)|b[2]) & 0x03FFFF;
  ir  = (((uint32_t)b[3]<<16)|((uint32_t)b[4]<<8)|b[5]) & 0x03FFFF;
  return true;
}

// ================= State =================
uint32_t sampleIdx = 0;
bool recording = false, finished = false;
uint32_t warmupSamples, recordSamples, warmupCount = 0;
uint32_t satRed = 0, satIr = 0, ovfTotal = 0;

void setup() {
  Serial.begin(SERIAL_BAUD); delay(400);
  Wire.begin(SDA_PIN, SCL_PIN); Wire.setClock(I2C_CLOCK);
  if (!maxInit()) {
    Serial.println(F("# MAX30102 tak terdeteksi (butuh BARE chip)."));
    while (1) delay(1000);
  }
  warmupSamples = (uint32_t)(WARMUP_SECONDS * FS);
  recordSamples = (uint32_t)(RECORD_SECONDS * FS);
  Serial.println();
  Serial.print(F("# Recorder PWA RED+IR  |  FS="));
  Serial.print(FS, 0); Serial.print(F(" Hz  |  BAUD="));
  Serial.println(SERIAL_BAUD);
  Serial.println(F("# >> PASTIKAN Serial Monitor pada baud di atas! <<"));
  Serial.print(F("# Rekam ")); Serial.print(RECORD_SECONDS);
  Serial.println(F(" dtk. Tempel sensor, DIAM total."));
}

void loop() {
  if (finished) return;

  // Pantau overflow FIFO (indikator throughput tak cukup)
  ovfTotal += ovfCount();

  uint8_t n = samplesAvailable();
  for (uint8_t s = 0; s < n; s++) {
    uint32_t red, ir;
    if (!readSample(red, ir)) continue;

    if (!recording) {
      if (++warmupCount >= warmupSamples) {
        recording = true; sampleIdx = 0;
        Serial.println(F("# START"));
        Serial.println(F("t_ms,red_raw,ir_raw"));
      }
      continue;
    }

    if (red >= 262143) satRed++;
    if (ir  >= 262143) satIr++;

    float t_ms = sampleIdx * (1000.0f / FS);
    Serial.print(t_ms, 1);  Serial.print(',');
    Serial.print(red);      Serial.print(',');
    Serial.println(ir);

    if (++sampleIdx >= recordSamples) {
      Serial.println(F("# END"));
      Serial.print(F("# Total sampel: ")); Serial.print(recordSamples);
      Serial.print(F(" @ ")); Serial.print(FS, 0); Serial.println(F(" Hz"));
      Serial.print(F("# Saturasi RED: ")); Serial.print(satRed);
      Serial.print(F("  IR: ")); Serial.print(satIr);
      Serial.print(F("  | FIFO overflow (throughput): ")); Serial.println(ovfTotal);
      if (satRed || satIr)
        Serial.println(F("#  -> ada saturasi: turunkan LED_RED/LED_IR."));
      if (ovfTotal > 5)
        Serial.println(F("#  -> overflow: throughput kurang; pakai PROFILE_SAFE."));
      Serial.println(F("# Reset board untuk merekam lagi."));
      finished = true;
      return;
    }
  }
  delayMicroseconds(100);
}
