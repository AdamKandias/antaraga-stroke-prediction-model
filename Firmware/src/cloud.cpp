/**
 * ANTARAGA — CORE WiFi / CLOUD (pinned ke core 0)
 * =====================================================================
 * Tugas:
 *   1. Connect WiFi (langkah PERTAMA saat boot; sensor menunggu sinyal ini)
 *   2. Sinkron NTP supaya tiap batch punya timestamp absolut
 *   3. Ambil batch dari qFilled -> serialisasi JSON -> POST HTTPS -> qFree
 *
 * Kenapa batch, bukan per-sampel?
 *   Aliran datanya 400 Hz x 2 kanal (MAX30102) + 200 Hz (SEN0203) = 1000
 *   nilai/detik. Satu POST HTTPS per sampel mustahil: handshake + header
 *   saja sudah ratusan byte dan puluhan milidetik. Jadi data dikemas per
 *   BATCH_MS (default 500 ms) dan dikirim lewat SATU koneksi TLS yang
 *   dipertahankan (keep-alive), sehingga handshake cuma sekali di awal.
 *   Isi payload tetap 100% nilai mentah — tidak ada yang dibuang/diolah.
 */

#include "antaraga.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <sys/time.h>
#include <time.h>

// =====================================================================
// Buffer JSON — dihitung compile-time dari ukuran batch
//   PPG  : maks 4 digit + koma      -> 6 byte/nilai (aman)
//   RED/IR: maks 6 digit + koma     -> 8 byte/nilai (aman)
// =====================================================================
#define JSON_BUF_SIZE  (384 + PPG_PER_BATCH * 6 + MAX_CAP * 2 * 8)
static char s_json[JSON_BUF_SIZE];

// Penulis JSON tanpa heap: String/ArduinoJson akan memfragmentasi heap kalau
// dipanggil 2x/detik selama berjam-jam. Ini menulis langsung ke buffer statis.
struct JsonWriter {
  char*  buf;
  size_t cap;
  size_t len;
  bool   overflow;

  void reset()            { len = 0; overflow = false; }
  void chr(char c)        { if (len + 1 < cap) buf[len++] = c; else overflow = true; }
  void str(const char* s) { while (*s) chr(*s++); }
  void key(const char* k) { chr('"'); str(k); chr('"'); chr(':'); }
  void u32(uint32_t v) {
    char t[11]; uint8_t n = 0;
    do { t[n++] = (char)('0' + (v % 10)); v /= 10; } while (v);
    while (n) chr(t[--n]);
  }
  void u64(uint64_t v) {
    char t[21]; uint8_t n = 0;
    do { t[n++] = (char)('0' + (uint8_t)(v % 10)); v /= 10; } while (v);
    while (n) chr(t[--n]);
  }
};
static JsonWriter s_jw = { s_json, JSON_BUF_SIZE, 0, false };

static size_t buildJson(const Batch* b) {
  JsonWriter& w = s_jw;
  w.reset();
  w.chr('{');
  w.key("id");        w.chr('"'); w.str(DEVICE_ID); w.chr('"'); w.chr(',');
  w.key("seq");       w.u32(b->seq);                             w.chr(',');
  w.key("t_ms");      w.u32(b->t0_ms);                           w.chr(',');
  w.key("t_unix_ms"); w.u64(b->t0_unix_ms);                      w.chr(',');
  w.key("fs_ppg");    w.u32(PPG_FS_HZ);                          w.chr(',');
  w.key("fs_max");    w.u32(MAX_FS_HZ);                          w.chr(',');
  w.key("batt_mv");   w.u32(b->batt_mv);                         w.chr(',');
  w.key("batt_pct");  w.u32(b->batt_pct);                        w.chr(',');
  w.key("ovf");       w.u32(b->max_ovf);                         w.chr(',');

  // SEN0203 — ADC mentah 0..4095
  w.key("ppg"); w.chr('[');
  for (uint16_t i = 0; i < b->ppg_n; i++) { if (i) w.chr(','); w.u32(b->ppg[i]); }
  w.chr(']'); w.chr(',');

  // MAX30102 — ADC mentah 18-bit
  w.key("red"); w.chr('[');
  for (uint16_t i = 0; i < b->max_n; i++) { if (i) w.chr(','); w.u32(b->red[i]); }
  w.chr(']'); w.chr(',');

  w.key("ir"); w.chr('[');
  for (uint16_t i = 0; i < b->max_n; i++) { if (i) w.chr(','); w.u32(b->ir[i]); }
  w.chr(']');

  w.chr('}');
  if (w.overflow) return 0;
  w.buf[w.len] = '\0';
  return w.len;
}

// =====================================================================
// WiFi
// =====================================================================
static bool wifiConnectOnce() {
  WiFi.disconnect(false, false);      // eraseap=false: jangan tulis NVS tiap retry
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  const uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < WIFI_CONNECT_TIMEOUT_MS) {
    vTaskDelay(pdMS_TO_TICKS(200));
  }
  return WiFi.status() == WL_CONNECTED;
}

static void wifiWaitConnected() {
  uint32_t attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[WIFI] menyambung ke \"%s\" (percobaan %lu)...\n",
                  WIFI_SSID, (unsigned long)++attempt);
    if (wifiConnectOnce()) break;
    vTaskDelay(pdMS_TO_TICKS(WIFI_RETRY_DELAY_MS));
  }
  Serial.print(F("[WIFI] tersambung, IP "));
  Serial.print(WiFi.localIP());
  Serial.printf("  RSSI %d dBm\n", WiFi.RSSI());
}

// =====================================================================
// NTP
// =====================================================================
uint64_t unixMillis() {
  if (!(xEventGroupGetBits(g_events) & EV_NTP_OK)) return 0;
  struct timeval tv;
  gettimeofday(&tv, nullptr);
  return (uint64_t)tv.tv_sec * 1000ULL + (uint64_t)(tv.tv_usec / 1000);
}

static void ntpSync() {
#if USE_NTP
  configTime(0, 0, NTP_SERVER_1, NTP_SERVER_2);       // simpan UTC; offset di cloud
  const uint32_t t0 = millis();
  while (time(nullptr) < 1700000000L && millis() - t0 < NTP_WAIT_MS) {
    vTaskDelay(pdMS_TO_TICKS(200));
  }
  if (time(nullptr) >= 1700000000L) {
    xEventGroupSetBits(g_events, EV_NTP_OK);
    Serial.printf("[NTP] sinkron, epoch %lu\n", (unsigned long)time(nullptr));
  } else {
    Serial.println(F("[NTP] gagal — t_unix_ms akan dikirim 0, pakai t_ms saja."));
  }
#endif
}

// =====================================================================
// HTTPS
// =====================================================================
static WiFiClientSecure s_tls;
static HTTPClient       s_http;

static void tlsInit() {
#if CLOUD_INSECURE_TLS
  s_tls.setInsecure();     // dev: sertifikat tidak diverifikasi
  Serial.println(F("[TLS] MODE INSECURE — sertifikat server TIDAK diverifikasi."));
#else
  s_tls.setCACert(CLOUD_ROOT_CA);
#endif
}

// true = HTTP 2xx
static bool cloudPost(const char* body, size_t len) {
  if (!s_http.begin(s_tls, CLOUD_HOST, CLOUD_PORT, CLOUD_PATH, true)) {
    Serial.println(F("[HTTP] begin() gagal"));
    return false;
  }
  s_http.setReuse(true);                    // pertahankan sesi TLS antar batch
  s_http.setTimeout(HTTP_TIMEOUT_MS);
  s_http.setConnectTimeout(HTTP_TIMEOUT_MS);
  s_http.addHeader("Content-Type", "application/json");
  if (strlen(CLOUD_API_KEY) > 0) s_http.addHeader("Authorization", "Bearer " CLOUD_API_KEY);

  const uint32_t tPost = millis();
  const int code = s_http.POST((uint8_t*)body, len);
  g_stats.last_http_code = code;
  g_stats.last_post_ms   = millis() - tPost;

  // Body respons WAJIB dikuras supaya koneksi keep-alive tidak desinkron.
  // Endpoint ingest normalnya balas JSON pendek, jadi getString() aman di sini.
  String resp = s_http.getString();
  s_http.end();

  const bool ok = (code >= 200 && code < 300);
  if (!ok) {
    Serial.printf("[HTTP] gagal code=%d  %s\n", code,
                  code > 0 ? resp.c_str() : s_http.errorToString(code).c_str());
  }
#if VERBOSE_HTTP
  else Serial.printf("[HTTP] %d  %u byte  %lu ms\n", code, (unsigned)len,
                     (unsigned long)g_stats.last_post_ms);
#endif
  return ok;
}

// =====================================================================
// TASK JARINGAN
// =====================================================================
void netTask(void* arg) {
  (void)arg;

  // --- Langkah 1: WiFi harus hidup DULU, baru sensor boleh menyala -----
  setState(ST_WIFI_CONNECTING);
  WiFi.persistent(false);      // jangan aus-kan flash: kredensial sudah di config.h
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);        // modem-sleep bikin latensi POST melonjak ratusan ms
  WiFi.setAutoReconnect(true);
  WiFi.setHostname(DEVICE_ID);
  wifiWaitConnected();

  ntpSync();
  tlsInit();

  // Ini yang membangunkan sensorTask di core 1.
  xEventGroupSetBits(g_events, EV_WIFI_OK);

  // --- Langkah 2: pompa batch ke cloud --------------------------------
  for (;;) {
    if (WiFi.status() != WL_CONNECTED) {
      /* Batch TIDAK diambil selama jaringan mati — biar menumpuk di qFilled
       * sebagai buffer. Kalau pool habis, sensorTask yang membuang yang
       * tertua. Sensor sendiri tidak pernah berhenti mencuplik. */
      if (g_state == ST_STREAMING) setState(ST_NET_LOST);
      Serial.println(F("[WIFI] terputus, menyambung ulang..."));
      s_http.end();
      s_tls.stop();
      wifiWaitConnected();
      if (!(xEventGroupGetBits(g_events) & EV_NTP_OK)) ntpSync();
      if (g_state == ST_NET_LOST) setState(ST_STREAMING);
      continue;
    }

    Batch* b = nullptr;
    if (xQueueReceive(g_qFilled, &b, pdMS_TO_TICKS(1000)) != pdTRUE) continue;

    const size_t n = buildJson(b);
    bool ok = false;
    if (n == 0) {
      Serial.println(F("[HTTP] JSON overflow — naikkan JSON_BUF_SIZE / turunkan BATCH_MS"));
    } else {
      ok = cloudPost(s_json, n);
      /* Satu kali retry: POST pertama setelah jeda sering gagal karena server
       * sudah menutup koneksi keep-alive di sisinya. Retry pakai koneksi baru. */
      if (!ok && WiFi.status() == WL_CONNECTED) {
        s_http.end();
        s_tls.stop();
        ok = cloudPost(s_json, n);
      }
    }

    xQueueSend(g_qFree, &b, 0);          // buffer kembali ke pool apa pun hasilnya
    if (ok) {
      g_stats.batches_sent++;
      if (g_state == ST_NET_LOST) setState(ST_STREAMING);
    } else {
      g_stats.http_fail++;
    }
  }
}
