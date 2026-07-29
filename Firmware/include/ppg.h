/**
 * ANTARAGA BPM — kontrak lapisan perangkat keras (ESP32 saja)
 * =====================================================================
 * Pemisahan yang dijaga: include/bpm.h tidak boleh tahu apa pun tentang
 * Arduino (supaya algoritmanya bisa diuji di PC), jadi semua yang berbau
 * ADC/task/pin dikumpulkan di sini.
 */
#pragma once

#include <Arduino.h>
#include "bpm.h"

struct PpgStats {
  volatile uint32_t samples;   // sampel yang masuk detektor
  volatile uint32_t overrun;   // task telat dari jadwal PPG_PERIOD_MS
  volatile uint32_t adc_fail;  // bacaan ADC yang gagal (dari total oversample)
  volatile uint32_t beat_seq;  // naik 1 tiap denyut diterima -> pemicu LED
  /* millis() saat sampel PERTAMA masuk detektor. Penyebut laju cuplik ukur
   * harus ini, bukan uptime: boot + settle sensor menyumbang ~2 detik yang
   * tidak menghasilkan satu pun sampel, dan kalau ikut dibagi, fs_ukur
   * terlihat rendah selama menit pertama — persis angka yang dipakai untuk
   * memutuskan apakah basis waktunya sehat. */
  volatile uint32_t t0_ms;
  volatile bool     ready;     // sudah lewat SENSOR_SETTLE_MS
};

extern PpgStats g_ppg;

// Task pencuplik 200 Hz. Dipin ke core 1 di main.cpp.
void ppgTask(void* arg);

/* Salinan keadaan detektor yang AMAN dibaca dari task lain (loop()).
 * Bukan sekadar kenyamanan: BpmOut berisi belasan field, dan pembacaan tanpa
 * kunci bisa mengambil separuh nilai lama + separuh nilai baru — mis. bpm
 * dari denyut ini dengan status dari denyut sebelumnya. */
void ppgGet(BpmOut* out);
