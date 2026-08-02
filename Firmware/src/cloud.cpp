/**
 * ANTARAGA — CORE WiFi / CLOUD (pinned ke core 0)
 * =====================================================================
 * Tugas:
 *   1. Connect WiFi (langkah PERTAMA saat boot; sensor menunggu sinyal ini)
 *   2. Sinkron NTP supaya tiap batch punya timestamp absolut
 *   3. Ambil batch dari qFilled -> serialisasi JSON -> POST HTTPS -> qFree
 *
 * Kenapa batch, bukan per-sampel?
 *   Aliran datanya 400 Hz x 2 kanal (MAX30102) + 200 Hz (SON1303) = 1000
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
#include <Update.h>
#include <Preferences.h>
#include <esp_ota_ops.h>
#include <sys/time.h>
#include <time.h>

// =====================================================================
// Buffer JSON — dihitung compile-time dari ukuran batch
//   PPG  : maks 4 digit + koma      -> 6 byte/nilai (aman)
//   RED/IR: maks 6 digit + koma     -> 8 byte/nilai (aman)
// =====================================================================
#define JSON_BUF_SIZE  (512 + PPG_PER_BATCH * 6 + MAX_CAP * 2 * 8)
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

static size_t buildJson(const Batch* b, const Sqi* q) {
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

  /* Metrik SQI ikut dikirim SELALU, apa pun nilainya — inilah yang dipakai
   * cloud sebagai gerbang kirim/buang sungguhan. Firmware tidak lagi
   * membuang package apa pun sendiri. */
  w.key("sqi");        w.u32(q->score);                          w.chr(',');
  w.key("sqi_flags");  w.u32(q->flags);                          w.chr(',');
  w.key("ir_dc");      w.u32(q->ir_dc);                          w.chr(',');
  w.key("ir_p2p");     w.u32(q->ir_p2p);                         w.chr(',');
  w.key("ir_pi");      w.u32(q->ir_pi);                          w.chr(',');
  w.key("ir_jump");    w.u32(q->ir_jump);                        w.chr(',');
  w.key("ir_jump_n");  w.u32(q->ir_jump_n);                      w.chr(',');
  w.key("ir_tort10");  w.u32(q->ir_tort10);                      w.chr(',');
  w.key("ppg_dc");     w.u32(q->ppg_dc);                         w.chr(',');
  w.key("ppg_p2p");    w.u32(q->ppg_p2p);                        w.chr(',');
  w.key("ppg_jump_n"); w.u32(q->ppg_jump_n);                     w.chr(',');
  w.key("ppg_tort10"); w.u32(q->ppg_tort10);                     w.chr(',');
  w.key("clip_n");     w.u32(q->clip_n);                         w.chr(',');

  // SON1303 — ADC mentah 0..4095
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

/* Klien TERPISAH untuk OTA. Memakai s_http yang sama akan mengacaukan sesi
 * keep-alive streaming: unduhan firmware itu transaksi panjang dengan header
 * dan timeout yang berbeda, dan kalau gagal di tengah, state HTTPClient-nya
 * ikut kotor untuk POST batch berikutnya. */
static WiFiClientSecure s_otaTls;
static HTTPClient       s_otaHttp;

static void tlsInit() {
#if CLOUD_INSECURE_TLS
  s_tls.setInsecure();     // dev: sertifikat tidak diverifikasi
  s_otaTls.setInsecure();
  /* PERINGATAN KEAMANAN: dengan sertifikat tidak diverifikasi, siapa pun yang
   * bisa menyisip di koneksi ini dapat memasang firmware apa pun ke alat yang
   * menempel di tubuh orang. Sebelum OTA dipakai di lapangan, set
   * CLOUD_INSECURE_TLS 0 dan isi CLOUD_ROOT_CA. */
  Serial.println(F("[TLS] MODE INSECURE — sertifikat server TIDAK diverifikasi."));
#if OTA_ENABLE
  Serial.println(F("[TLS] OTA aktif di atas kanal tanpa verifikasi — JANGAN dipakai produksi."));
#endif
#else
  s_tls.setCACert(CLOUD_ROOT_CA);
  s_otaTls.setCACert(CLOUD_ROOT_CA);
#endif
}

// =====================================================================
// OTA — pengurai JSON minimal
// ---------------------------------------------------------------------
// Respons OTA cuma beberapa puluh byte, jadi ArduinoJson tidak sepadan —
// library itu justru memfragmentasi heap yang sedang kita jaga untuk TLS.
// =====================================================================
#if OTA_ENABLE
static bool jsonFindBool(const String& s, const char* key, bool* out) {
  String pat = String('"') + key + '"';
  int i = s.indexOf(pat);
  if (i < 0) return false;
  i = s.indexOf(':', i + pat.length());
  if (i < 0) return false;
  while (++i < (int)s.length() && (s[i] == ' ' || s[i] == '\t')) {}
  *out = s.startsWith("true", i);
  return true;
}

static bool jsonFindStr(const String& s, const char* key, char* out, size_t cap) {
  String pat = String('"') + key + '"';
  int i = s.indexOf(pat);
  if (i < 0) return false;
  i = s.indexOf(':', i + pat.length());
  if (i < 0) return false;
  i = s.indexOf('"', i);
  if (i < 0) return false;
  const int j = s.indexOf('"', i + 1);
  if (j < 0) return false;
  size_t n = (size_t)(j - i - 1);
  if (n >= cap) n = cap - 1;
  memcpy(out, s.c_str() + i + 1, n);
  out[n] = '\0';
  return true;
}

// =====================================================================
// OTA — pengaman percobaan (anti-brick)
// ---------------------------------------------------------------------
// Firmware yang baru dipasang berstatus PERCOBAAN sampai membuktikan diri
// lewat OTA_TRIAL_POSTS kali POST berhasil. Gagal sampai batas waktu ->
// boot dialihkan kembali ke partisi yang terakhir terbukti jalan.
//
// Kita TIDAK pernah mengalihkan ke slot yang belum pernah terbukti berjalan:
// "good_part" hanya ditulis setelah firmware di slot itu sukses POST. Tanpa
// syarat ini, revert pada OTA pertama justru melompat ke slot kosong.
// =====================================================================
static Preferences s_nvs;
static bool     s_inTrial    = false;
static uint32_t s_trialStart = 0;
static uint32_t s_trialOk    = 0;

static const char* runningLabel() {
  const esp_partition_t* p = esp_ota_get_running_partition();
  return p ? p->label : "?";
}

static void otaTrialInit() {
  s_nvs.begin("antaraga", false);
  s_inTrial    = s_nvs.getBool("ota_trial", false);
  s_trialStart = millis();
  s_trialOk    = 0;
  if (s_inTrial) {
    Serial.printf("[OTA] firmware %s di %s berstatus PERCOBAAN — butuh %d POST sukses\n",
                  FW_VERSION, runningLabel(), OTA_TRIAL_POSTS);
  }
}

static void otaTrialRevert() {
  char good[16] = {0};
  s_nvs.getString("good_part", good, sizeof(good));

  if (good[0] == '\0' || strcmp(good, runningLabel()) == 0) {
    // Tidak ada cadangan yang terbukti. Membalik boot ke slot yang belum pernah
    // jalan justru menjamin brick, jadi lebih baik tetap di sini dan mencoba.
    Serial.println(F("[OTA] percobaan gagal, tapi tidak ada partisi cadangan "
                     "terbukti — tetap berjalan."));
    s_nvs.putBool("ota_trial", false);
    s_inTrial = false;
    return;
  }

  const esp_partition_t* prev = esp_partition_find_first(
      ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_ANY, good);
  if (!prev) {
    Serial.printf("[OTA] partisi cadangan \"%s\" tidak ditemukan — tetap berjalan.\n", good);
    s_nvs.putBool("ota_trial", false);
    s_inTrial = false;
    return;
  }

  Serial.printf("[OTA] PERCOBAAN GAGAL — kembali ke %s lalu restart.\n", good);
  s_nvs.putBool("ota_trial", false);
  s_nvs.end();
  esp_ota_set_boot_partition(prev);
  vTaskDelay(pdMS_TO_TICKS(200));
  esp_restart();
}

// Dipanggil setiap selesai POST batch.
static void otaTrialOnPost(bool ok) {
  if (!s_inTrial) {
    // Bukan percobaan: catat slot ini sebagai "terbukti" sekali saja, supaya
    // OTA berikutnya punya sasaran revert yang sah.
    static bool recorded = false;
    if (ok && !recorded) {
      recorded = true;
      char good[16] = {0};
      s_nvs.getString("good_part", good, sizeof(good));
      if (strcmp(good, runningLabel()) != 0) s_nvs.putString("good_part", runningLabel());
    }
    return;
  }

  if (ok && ++s_trialOk >= OTA_TRIAL_POSTS) {
    s_nvs.putBool("ota_trial", false);
    s_nvs.putString("good_part", runningLabel());
    s_inTrial = false;
    Serial.printf("[OTA] firmware %s TERBUKTI jalan — dikunci di %s.\n",
                  FW_VERSION, runningLabel());
    return;
  }
  if (millis() - s_trialStart > OTA_TRIAL_TIMEOUT_MS) otaTrialRevert();
}

// =====================================================================
// OTA — cek, unduh, pasang
// =====================================================================
static void otaSendAck() {
  char url[256];
  snprintf(url, sizeof(url), "https://%s:%d%s?device_id=%s&fw=%s",
           CLOUD_HOST, CLOUD_PORT, OTA_PATH_ACK, DEVICE_ID, FW_VERSION);
  if (!s_otaHttp.begin(s_otaTls, url)) return;
  if (strlen(CLOUD_API_KEY) > 0) s_otaHttp.addHeader("Authorization", "Bearer " CLOUD_API_KEY);
  s_otaHttp.setTimeout(HTTP_TIMEOUT_MS);
  s_otaHttp.POST((uint8_t*)nullptr, 0);
  s_otaHttp.end();
}

/* true = ada firmware baru yang BERBEDA versinya dan perlu diunduh.
 * Kalau server bilang pending tapi versinya sama dengan yang sedang berjalan,
 * berarti ACK sebelumnya tidak sampai — kita kirim ulang ACK dan TIDAK
 * mengunduh apa pun. Ini yang memutus loop reflash. */
static bool otaCheckPending() {
  char url[256];
  snprintf(url, sizeof(url), "https://%s:%d%s?device_id=%s&fw=%s",
           CLOUD_HOST, CLOUD_PORT, OTA_PATH_CHECK, DEVICE_ID, FW_VERSION);

  if (!s_otaHttp.begin(s_otaTls, url)) return false;
  if (strlen(CLOUD_API_KEY) > 0) s_otaHttp.addHeader("Authorization", "Bearer " CLOUD_API_KEY);
  s_otaHttp.setTimeout(HTTP_TIMEOUT_MS);

  const int code = s_otaHttp.GET();
  String body;
  if (code == 200) body = s_otaHttp.getString();
  s_otaHttp.end();

  if (code != 200) {
    Serial.printf("[OTA] cek gagal code=%d\n", code);
    return false;
  }

  bool pending = false;
  if (!jsonFindBool(body, "pending", &pending) || !pending) return false;

  char newFw[32] = {0};
  if (jsonFindStr(body, "fw", newFw, sizeof(newFw)) && strcmp(newFw, FW_VERSION) == 0) {
    Serial.printf("[OTA] server menawarkan %s — sama dengan yang berjalan. "
                  "Kirim ulang ACK, tidak mengunduh.\n", newFw);
    otaSendAck();
    return false;
  }

  Serial.printf("[OTA] firmware baru tersedia: %s (sekarang %s)\n",
                newFw[0] ? newFw : "(versi tidak disebut)", FW_VERSION);
  return true;
}

// Unduh .bin lalu tulis ke partisi OTA yang tidak sedang berjalan.
// Kalau berhasil: tandai percobaan, ACK, restart. Tidak pernah kembali.
static void otaPerform() {
  char url[256];
  snprintf(url, sizeof(url), "https://%s:%d%s?device_id=%s",
           CLOUD_HOST, CLOUD_PORT, OTA_PATH_FIRMWARE, DEVICE_ID);

  Serial.println(F("[OTA] mengunduh firmware..."));
  if (!s_otaHttp.begin(s_otaTls, url)) {
    Serial.println(F("[OTA] begin() gagal"));
    return;
  }
  if (strlen(CLOUD_API_KEY) > 0) s_otaHttp.addHeader("Authorization", "Bearer " CLOUD_API_KEY);
  s_otaHttp.setTimeout(OTA_DOWNLOAD_TIMEOUT_MS);

  const int code = s_otaHttp.GET();
  if (code != 200) {
    Serial.printf("[OTA] unduh gagal code=%d\n", code);
    s_otaHttp.end();
    return;
  }

  const int binSize = s_otaHttp.getSize();
  /* Content-Length WAJIB. Dengan UPDATE_SIZE_UNKNOWN, Update tidak bisa
   * memeriksa kelengkapan, sehingga unduhan yang terpotong di tengah bisa
   * lolos sebagai "berhasil" dan mem-boot image cacat. */
  if (binSize <= 0) {
    Serial.println(F("[OTA] server tidak mengirim Content-Length — dibatalkan."));
    s_otaHttp.end();
    return;
  }
  Serial.printf("[OTA] ukuran %d byte -> menulis ke partisi cadangan...\n", binSize);

  if (!Update.begin((size_t)binSize)) {
    Serial.printf("[OTA] Update.begin gagal: %s\n", Update.errorString());
    s_otaHttp.end();
    return;
  }

  WiFiClient* stream = s_otaHttp.getStreamPtr();
  const size_t written = Update.writeStream(*stream);
  s_otaHttp.end();

  if (written != (size_t)binSize || !Update.end() || !Update.isFinished()) {
    Serial.printf("[OTA] flash GAGAL (%u/%d byte): %s\n",
                  (unsigned)written, binSize, Update.errorString());
    Update.abort();
    /* Firmware lama tetap utuh dan tetap jadi partisi boot — tidak ada yang
     * rusak, siklus berikutnya boleh mencoba lagi. */
    return;
  }

  Serial.println(F("[OTA] flash BERHASIL. Menandai status percobaan lalu restart."));
  s_nvs.putBool("ota_trial", true);
  otaSendAck();
  s_nvs.end();
  vTaskDelay(pdMS_TO_TICKS(500));
  esp_restart();
}
#endif  // OTA_ENABLE

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
#if OTA_ENABLE
  otaTrialInit();
  Serial.printf("[OTA] versi %s, berjalan di partisi %s\n", FW_VERSION, runningLabel());
#endif

  // Ini yang membangunkan sensorTask di core 1.
  xEventGroupSetBits(g_events, EV_WIFI_OK);

  // --- Langkah 2: pompa batch ke cloud --------------------------------
#if OTA_ENABLE && OTA_CHECK_INTERVAL_MS > 0
  uint32_t lastOtaMs = millis();
#endif

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
#if OTA_ENABLE && OTA_CHECK_INTERVAL_MS > 0
      lastOtaMs = millis();   // jangan langsung cek OTA sesaat setelah reconnect
#endif
      continue;
    }

#if OTA_ENABLE && OTA_CHECK_INTERVAL_MS > 0
    /* Cek OTA dilakukan DI ANTARA batch, bukan di tengah pengiriman, supaya
     * tidak ada dua transaksi TLS yang tumpang tindih.
     *
     * Selama unduhan (belasan detik), netTask tidak menguras qFilled. sensorTask
     * tetap mencuplik dan pool akan penuh, jadi batch selama jendela itu memang
     * hilang — terlihat sebagai lonjakan "drop" di [STAT]. Itu disengaja: satu
     * kali kehilangan beberapa detik data jauh lebih murah daripada menghentikan
     * akuisisi atau menunda update. */
    if (millis() - lastOtaMs >= OTA_CHECK_INTERVAL_MS) {
      lastOtaMs = millis();
      if (otaCheckPending()) {
        s_http.end();          // lepaskan sesi streaming dulu: unduhan butuh
        s_tls.stop();          // heap untuk buffer TLS-nya sendiri
        otaPerform();          // berhasil -> esp_restart(), tidak kembali ke sini
        lastOtaMs = millis();  // gagal -> jangan langsung ulang, beri jeda penuh
      }
    }
#endif

    Batch* b = nullptr;
    if (xQueueReceive(g_qFilled, &b, pdMS_TO_TICKS(1000)) != pdTRUE) continue;

    /* METRIK SQI — dihitung untuk SETIAP package sebagai metadata; tidak lagi
     * memutuskan kirim/buang di sini. Gerbang kelayakan sepenuhnya dipindah ke
     * cloud: cloud punya akses ke seluruh sub-metrik (ir_dc, ir_pi, ir_jump,
     * tortuosity, dst), bisa mengubah ambang kapan pun tanpa flash ulang
     * firmware, dan bisa memutuskan lebih optimal karena melihat lebih dari
     * satu package sekaligus. Hitungannya hanya jalan-lurus atas ~500 sampel
     * (puluhan mikrodetik), dan ini core 0 yang memang sedang menunggu, bukan
     * core sensor. */
    Sqi q;
    sqiEvaluate(b, &q);
    g_stats.sqi_last_score = q.score;
    g_stats.sqi_last_flags = q.flags;
    if (q.flags) {
      g_stats.sqi_flagged++;
#if VERBOSE_SQI
      char why[SQI_FLAGS_TEXT_CAP];
      sqiFlagsText(q.flags, why, sizeof(why));
      Serial.printf("[SQI ] flag seq=%lu skor=%u (%s) ir_dc=%lu pi=%u permil"
                    " jump=%lu n=%u tort=%u.%u\n",
                    (unsigned long)b->seq, (unsigned)q.score, why,
                    (unsigned long)q.ir_dc, (unsigned)q.ir_pi,
                    (unsigned long)q.ir_jump, (unsigned)q.ir_jump_n,
                    (unsigned)(q.ir_tort10 / 10), (unsigned)(q.ir_tort10 % 10));
#endif
    }

    const size_t n = buildJson(b, &q);
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

#if OTA_ENABLE
    /* POST yang berhasil = bukti hidup paling kuat yang kita punya: WiFi jalan,
     * TLS jalan, sensor menghasilkan data, dan cloud menerimanya. Itulah yang
     * dipakai untuk mengesahkan firmware hasil OTA. */
    otaTrialOnPost(ok);
#endif
  }
}
