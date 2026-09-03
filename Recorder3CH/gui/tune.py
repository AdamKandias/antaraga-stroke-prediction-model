#!/usr/bin/env python3
"""
ANTARAGA - Penyetel otomatis MAX30102 (cari pembacaan mentah paling optimal)
=====================================================================
Menyapu RENTANG ADC dan ARUS LED, mengukur SNR nyata di tiap titik, lalu
merekomendasikan setelan terbaik beserta baris yang tinggal ditempel ke
konfigurasi.

    python gui/tune.py COM3

Butuh firmware Recorder3CH versi terbaru (yang punya perintah "=dN"). Skrip
akan menolak jalan kalau firmware-nya belum mendukung, supaya tidak
melaporkan hasil sapuan yang sebenarnya tidak pernah berlaku.

KENAPA RENTANG ADC IKUT DISAPU, BUKAN CUMA ARUS LED
---------------------------------------------------
ADC_RGE menentukan arus foto skala penuh (2048/4096/8192/16384 nA). Rentang
yang lebih kecil = lebih peka: arus foto yang sama menghasilkan lebih banyak
cacahan, TANPA menambah arus LED sedikit pun. Karena derau di sini didominasi
elektronik ADC (pada DC 81.552 LSB, derau tembakan foton hanya ~1 LSB
sementara derau terukur ~5,1 LSB), memperkecil rentang menaikkan SNR hampir
sebanding - dan malah memungkinkan arus LED DITURUNKAN untuk cacahan yang
sama, sehingga baterai ikut hemat.

Menaikkan arus LED saja akan sampai ke DC yang sama dengan ongkos daya jauh
lebih besar. Itu sebabnya sapuan ini menyusun keduanya, bukan salah satu.

CARA KERJA
----------
Untuk tiap rentang ADC:
  1. LED dimatikan -> ukur lantai gelap
  2. Arus uji -> ukur DC, hitung kemiringan (DC per LSB arus)
  3. Ekstrapolasi arus yang mendaratkan DC di target, pasang, ukur penuh
Kemiringannya linear (terbukti di sapuan ../DiagMAX30102), jadi dua titik
sudah cukup dan sapuannya selesai dalam ~45 detik, bukan belasan menit.
"""

import os
import sys
import time
import numpy as np

# supaya `python gui/tune.py` dari mana pun tetap menemukan plotter.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import serial
except ImportError:
    print("pyserial belum terpasang:  pip install pyserial")
    sys.exit(1)

from plotter import ac_signal, bpm_autocorr, COL_T, COL_GREEN, COL_RED, COL_IR

# ---------------------------------------------------------------------
TARGET_DC = 160000.0      # sasaran DC: SNR tinggi, sisa ruang 39% untuk gerakan
DC_MIN, DC_MAX = 90000.0, 205000.0
SAT = 262100
RGE_NA = {0: 2048, 1: 4096, 2: 8192, 3: 16384}
PROBE_CUR = 0x40          # ~12,8 mA untuk mengukur kemiringan
T_DARK, T_PROBE, T_FULL = 1.5, 2.5, 8.0   # 8 s: cukup untuk BPM ikut sahih


class Dev:
    def __init__(self, port, baud=921600):
        self.ser = serial.Serial(port, baud, timeout=0.2)
        time.sleep(0.4)
        self.ser.reset_input_buffer()
        self.buf = b""
        self.cfg = None

    def close(self):
        try:
            self.ser.close()
        except serial.SerialException:
            pass

    def _lines(self):
        chunk = self.ser.read(8192)
        if chunk:
            self.buf += chunk
            *lines, self.buf = self.buf.split(b"\n")
            for ln in lines:
                yield ln.decode("utf-8", "replace").strip()

    def wait_cfg(self, timeout=3.0):
        """Tunggu gema #cfg supaya tidak ada titik sapuan yang mengukur
        setelan lama karena perintahnya belum sempat berlaku."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            for ln in self._lines():
                if ln.startswith("#cfg"):
                    self.cfg = ln
                    return ln
        return None

    def set(self, **kw):
        for key, letter in (("rge", "d"), ("red", "r"), ("ir", "f"),
                            ("ave", "a"), ("sr", "s")):
            if key in kw:
                self.ser.write(("=%s%X\n" % (letter, kw[key])).encode())
                if self.wait_cfg() is None:
                    raise RuntimeError(
                        "firmware tidak menjawab '#cfg' - flash ulang "
                        "Recorder3CH (versi lama belum punya perintah ini)")

    def capture(self, seconds):
        # Beri LED & rantai ADC waktu menetap, lalu BUANG apa pun yang
        # sempat mengalir - kalau tidak, sampel pertama tiap titik sapuan
        # masih membawa setelan sebelumnya dan menyeret rerata DC-nya.
        time.sleep(0.25)
        self.ser.reset_input_buffer()
        self.buf = b""
        rows = []
        t0 = time.time()
        while time.time() - t0 < seconds:
            for ln in self._lines():
                if not ln or ln[0] == "#":
                    continue
                p = ln.split(",")
                if len(p) == 5:
                    try:
                        rows.append([float(v) for v in p])
                    except ValueError:
                        pass
        return np.asarray(rows) if rows else np.zeros((0, 5))


def metrics(d, fs_hint=200.0):
    """DC, derau, AC, SNR, perfusi, BPM untuk merah & inframerah."""
    out = {}
    if len(d) < 50:
        return None
    span = (d[-1, COL_T] - d[0, COL_T]) / 1000.0
    fs = (len(d) - 1) / span if span > 0.5 else fs_hint
    out["fs"] = fs
    for name, col in (("red", COL_RED), ("ir", COL_IR), ("green", COL_GREEN)):
        x = d[:, col]
        dc = float(x.mean())
        # Derau per sampel dari |beda| berurutan: pada 200 Hz denyut hampir
        # tidak menyumbang ke beda antar sampel, jadi ini lantai derau.
        sigma = float(np.abs(np.diff(x)).mean()) / 1.128
        ac_win = ac_signal(x, fs)
        n1 = max(8, int(fs))
        p2p = [float(ac_win[i:i + n1].max() - ac_win[i:i + n1].min())
               for i in range(0, len(ac_win) - n1 + 1, n1)]
        ac = float(np.median(p2p)) if p2p else 0.0
        bpm, conf = bpm_autocorr(x, fs)
        out[name] = dict(dc=dc, sigma=sigma, ac=ac,
                         snr=(ac / sigma if sigma > 1e-6 else 0.0),
                         pi=(1000.0 * ac / dc if dc > 1 else 0.0),
                         bpm=bpm, conf=conf,
                         clip=int((x >= SAT).sum()))
    return out


def sweep_range(dev, rge, log):
    log("\n--- rentang ADC %d (%d nA) ---" % (rge, RGE_NA[rge]))
    dev.set(rge=rge, red=0, ir=0)
    m = metrics(dev.capture(T_DARK))
    if not m:
        log("    tidak ada data"); return None
    dark_r, dark_i = m["red"]["dc"], m["ir"]["dc"]
    log("    lantai gelap: merah %.0f  inframerah %.0f LSB" % (dark_r, dark_i))

    dev.set(red=PROBE_CUR, ir=PROBE_CUR)
    m = metrics(dev.capture(T_PROBE))
    if not m:
        log("    tidak ada data"); return None
    k_r = (m["red"]["dc"] - dark_r) / PROBE_CUR
    k_i = (m["ir"]["dc"] - dark_i) / PROBE_CUR
    log("    uji 0x%02X: merah %.0f (%.0f LSB/step) | inframerah %.0f (%.0f LSB/step)"
        % (PROBE_CUR, m["red"]["dc"], k_r, m["ir"]["dc"], k_i))
    if k_r <= 0 or k_i <= 0:
        log("    LED tidak merespons - dilewati"); return None

    cur_r = int(round((TARGET_DC - dark_r) / k_r))
    cur_i = int(round((TARGET_DC - dark_i) / k_i))
    over = (cur_r > 255 or cur_i > 255)
    cur_r, cur_i = max(1, min(255, cur_r)), max(1, min(255, cur_i))
    log("    arus untuk DC %.0fk: merah 0x%02X (%.1f mA) | inframerah 0x%02X (%.1f mA)%s"
        % (TARGET_DC / 1000, cur_r, cur_r * 0.2, cur_i, cur_i * 0.2,
           "  <- MENTOK 0xFF" if over else ""))

    dev.set(red=cur_r, ir=cur_i)
    m = metrics(dev.capture(T_FULL))
    if not m:
        log("    tidak ada data"); return None
    m["rge"] = rge
    m["cur_red"], m["cur_ir"] = cur_r, cur_i
    m["reachable"] = not over
    for ch in ("red", "ir"):
        c = m[ch]
        log("    %-10s DC %7.0f  derau %5.2f  AC %6.1f  SNR %6.1f  perfusi %5.2f permil"
            "  BPM %s (%.2f)%s"
            % (ch, c["dc"], c["sigma"], c["ac"], c["snr"], c["pi"],
               ("%.1f" % c["bpm"]) if c["bpm"] else "-", c["conf"],
               "  MENTOK REL" if c["clip"] else ""))
    return m


def main():
    if len(sys.argv) < 2:
        print("Pakai: python gui/tune.py COM3")
        sys.exit(1)
    port = sys.argv[1]

    lines = []
    def log(s):
        print(s, flush=True)
        lines.append(s)

    log("=" * 66)
    log("ANTARAGA - penyetel otomatis MAX30102")
    log("=" * 66)
    log("Tempelkan sensor SEKARANG, tekanan sekadar menyentuh, lalu DIAM")
    log("total sampai selesai (~45 detik). Bergerak di tengah sapuan membuat")
    log("titik-titiknya tidak sebanding satu sama lain.")
    for i in range(5, 0, -1):
        print("  mulai dalam %d detik...   \r" % i, end="", flush=True)
        time.sleep(1)
    print(" " * 40)

    dev = Dev(port)
    try:
        dev.ser.write(b"i")
        if dev.wait_cfg(4.0) is None:
            log("\nFirmware belum mendukung perintah setel-absolut.")
            log("Flash ulang: cd d:\\ANTARAGA\\Recorder3CH && pio run -t upload")
            return
        log("firmware: %s" % dev.cfg)

        results = []
        for rge in (0, 1, 2, 3):
            r = sweep_range(dev, rge, log)
            if r:
                results.append(r)

        # ---- pilih pemenang ----
        log("\n" + "=" * 66)
        log("RINGKASAN (target DC %.0fk)" % (TARGET_DC / 1000))
        log("=" * 66)
        # KRITERIA - sengaja TIDAK memakai SNR.
        #
        # Pada DC target yang sama, AC dalam LSB juga sama: perfusi itu sifat
        # jaringan, bukan sifat setelan. Jadi yang benar-benar membedakan antar
        # kandidat hanya DERAU. Memakai SNR berarti menggantungkan keputusan
        # pada ada-tidaknya denyut yang bagus saat sapuan berjalan - padahal
        # sapuan justru sering dilakukan ketika penempatannya belum baik.
        #
        # Derau dinyatakan relatif terhadap DC (per-mil) supaya sebanding
        # langsung dengan kolom perfusi: perfusi 1,45 permil dengan derau
        # 0,03 permil berarti denyutnya 48x di atas lantai derau.
        log(" rge     nA  arus M/IR    DC merah  derau permil |  DC infra  derau permil | daya LED")
        ok = []
        for m in results:
            mA = (m["cur_red"] + m["cur_ir"]) * 0.2
            for ch in ("red", "ir"):
                c = m[ch]
                c["nrel"] = 1000.0 * c["sigma"] / c["dc"] if c["dc"] > 1 else 9e9
            m["nrel"] = max(m["red"]["nrel"], m["ir"]["nrel"])
            flag = ""
            if not m["reachable"]:
                flag = "  (arus mentok)"
            elif not (DC_MIN <= m["red"]["dc"] <= DC_MAX and
                      DC_MIN <= m["ir"]["dc"] <= DC_MAX):
                flag = "  (DC di luar jendela)"
            elif m["red"]["clip"] or m["ir"]["clip"]:
                flag = "  (mentok rel)"
            else:
                ok.append(m)
            log("  %d  %6d  0x%02X/0x%02X %9.0f %13.4f | %9.0f %13.4f | %5.1f mA%s"
                % (m["rge"], RGE_NA[m["rge"]], m["cur_red"], m["cur_ir"],
                   m["red"]["dc"], m["red"]["nrel"], m["ir"]["dc"],
                   m["ir"]["nrel"], mA, flag))

        if not ok:
            log("\nTidak ada setelan yang memenuhi syarat. Kemungkinan sensor")
            log("tidak menempel selama sapuan, atau kopling optiknya terlalu lemah.")
            return

        conf_max = max(max(m["red"]["conf"], m["ir"]["conf"]) for m in results)
        if conf_max < 0.30:
            log("\n  CATATAN: tidak ada denyut sahih selama sapuan (periodisitas")
            log("  tertinggi %.2f). Kolom DC dan derau TETAP SAH - keduanya tidak" % conf_max)
            log("  butuh denyut - jadi pilihan di bawah tetap berlaku. Yang belum")
            log("  terbukti hanyalah perfusi/BPM di setelan itu; ulangi sambil")
            log("  memakai sensor dengan benar untuk memastikannya.")

        # Derau relatif terkecil menang; daya LED terkecil sebagai pemutus seri.
        best = min(ok, key=lambda m: (round(m["nrel"], 4),
                                      m["cur_red"] + m["cur_ir"]))
        log("\nPILIHAN: rentang ADC %d (%d nA), merah 0x%02X, inframerah 0x%02X"
            % (best["rge"], RGE_NA[best["rge"]], best["cur_red"], best["cur_ir"]))
        log("  DC merah %.0f (SNR %.1f) | DC inframerah %.0f (SNR %.1f) | %.1f mA total"
            % (best["red"]["dc"], best["red"]["snr"], best["ir"]["dc"],
               best["ir"]["snr"], (best["cur_red"] + best["cur_ir"]) * 0.2))

        base = next((m for m in results if m["rge"] == 2), None)
        if base and base is not best:
            g_r = best["red"]["snr"] / base["red"]["snr"] if base["red"]["snr"] else 0
            g_i = best["ir"]["snr"] / base["ir"]["snr"] if base["ir"]["snr"] else 0
            d_mA = ((best["cur_red"] + best["cur_ir"]) -
                    (base["cur_red"] + base["cur_ir"])) * 0.2
            log("  vs setelan lama (rge 2): SNR merah x%.2f, inframerah x%.2f,"
                " daya LED %+.1f mA" % (g_r, g_i, d_mA))

        spo2 = (best["rge"] << 5) | (3 << 2) | 3      # SR 400 Hz, PW 411 us
        log("\nTempelkan ke ../Firmware/include/config.h:")
        log("  #define MAX_LED_RED  0x%02X" % best["cur_red"])
        log("  #define MAX_LED_IR   0x%02X" % best["cur_ir"])
        log("dan ke ../Firmware/src/sensors.cpp:")
        log("  #define CFG_SPO2     0x%02X   // ADC_RGE=%d nA | SR=400Hz | PW=411us"
            % (spo2, RGE_NA[best["rge"]]))
        log("\nUntuk Recorder3CH/src/main.cpp:")
        log("  #define RGE_DEFAULT      %d" % best["rge"])
        log("  #define LED_RED_DEFAULT  0x%02X" % best["cur_red"])
        log("  #define LED_IR_DEFAULT   0x%02X" % best["cur_ir"])

        g = best["green"]
        log("\nKanal HIJAU (SON1303) tidak bisa disetel dari firmware - hanya")
        log("penempatan yang mengubahnya. Saat ini: DC %.0f, AC %.1f, perfusi"
            " %.1f permil, BPM %s (%.2f)."
            % (g["dc"], g["ac"], g["pi"],
               ("%.1f" % g["bpm"]) if g["bpm"] else "-", g["conf"]))

        # kembalikan perangkat ke pilihan terbaik
        dev.set(rge=best["rge"], red=best["cur_red"], ir=best["cur_ir"])
        log("\nPerangkat sudah dipasangi setelan pilihan. Buka GUI untuk melihat"
            " hasilnya.")
    finally:
        dev.close()
        try:
            with open("tune_hasil.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print("\n(laporan disimpan ke tune_hasil.txt)")
        except OSError:
            pass


if __name__ == "__main__":
    main()
