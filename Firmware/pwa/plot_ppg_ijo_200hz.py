#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisis PWA dari data mentah PPG SON1303 (XIAO ESP32-C3)
==========================================================
Mengubah adc_raw MENTAH menjadi 4 representasi untuk Pulse Wave Analysis:
  1. Band-pass : PPG bersih 0.5-15 Hz (pertahankan detail utk turunan)
  2. FFT       : spektrum frekuensi -> puncak PPG & cek interferensi
  3. VPG       : Velocity PPG = turunan PERTAMA (d PPG/dt)
                 titik w,y,z; menandai kaki & upstroke.
  4. APG       : Acceleration PPG = turunan KEDUA (SDPPG)
                 gelombang a,b,c,d,e -> aging index / arterial stiffness.

Butuh: numpy, scipy, matplotlib
Pakai : python plot_pwa.py rekam.txt
        python plot_pwa.py rekam.txt --session 1 --zoom 20 24 --save
"""

import sys
import argparse
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
import matplotlib.pyplot as plt

FS = 200.0   # Hz


# ---------------------------------------------------------------- parsing
def parse_file(path):
    """Pisahkan tiap sesi (blok START..END). Terima 3 atau 4 kolom."""
    sessions, cur, started = [], None, False
    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("t_ms"):
                cur = []; sessions.append(cur); started = True
                continue
            if line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            try:
                t = float(parts[0]); raw = float(parts[1])
            except ValueError:
                continue
            if cur is None and not started:
                cur = []; sessions.append(cur)
            if cur is not None:
                cur.append((t, raw))
    return [np.array(s) for s in sessions if len(s) > 100]


# ---------------------------------------------------------------- filters
def bandpass(sig, lo=0.5, hi=15.0, fs=FS, order=4):
    """Band-pass zero-phase (filtfilt tak menggeser fase -> aman utk PWA)."""
    b, a = butter(order, [lo, hi], btype="band", fs=fs)
    return filtfilt(b, a, sig)


def derivative(sig, fs=FS):
    """Turunan terhadap waktu (beda hingga terpusat)."""
    return np.gradient(sig, 1.0 / fs)


def compute_fft(sig, fs=FS):
    sig = sig - np.mean(sig)
    n = len(sig); win = np.hanning(n)
    mag = np.abs(np.fft.rfft(sig * win)) * 2.0 / np.sum(win)
    freq = np.fft.rfftfreq(n, 1.0 / fs)
    return freq, mag


# ---------------------------------------------------------------- cycle utils
def find_onsets(ppg, fs=FS):
    """Cari kaki (onset) tiap denyut: minimum sebelum puncak sistolik."""
    pk, _ = find_peaks(ppg, distance=int(0.4 * fs),
                       prominence=np.std(ppg) * 0.4)
    onsets = []
    for p in pk:
        w0 = max(0, p - int(0.35 * fs))
        onsets.append(w0 + int(np.argmin(ppg[w0:p + 1])))
    return np.array(sorted(set(onsets))), pk


def label_apg(apg_cycle):
    """Label a,b,c,d,e pada satu siklus APG (turunan kedua)."""
    n = len(apg_cycle)
    if n < 10:
        return None
    a = int(np.argmax(apg_cycle[:max(3, int(0.4 * n))]))
    after = apg_cycle[a:]
    b = a + int(np.argmin(after[:max(3, int(0.4 * n))]))
    half = int(0.45 * n)
    e = half + int(np.argmax(apg_cycle[half:]))
    seg = apg_cycle[b:e]
    c = d = None
    if len(seg) > 4:
        pks, _ = find_peaks(seg); trs, _ = find_peaks(-seg)
        if len(pks): c = b + int(pks[0])
        if len(trs): d = b + int(trs[0])
    return {"a": a, "b": b, "c": c, "d": d, "e": e}


def label_vpg(vpg_cycle):
    """Label w (puncak/max slope), y (min setelah w), z (puncak kecil)."""
    n = len(vpg_cycle)
    if n < 8:
        return None
    w = int(np.argmax(vpg_cycle[:max(3, int(0.5 * n))]))
    after = vpg_cycle[w:]
    y = w + int(np.argmin(after))
    seg = vpg_cycle[y:]
    z = None
    if len(seg) > 3:
        pks, _ = find_peaks(seg)
        if len(pks): z = y + int(pks[0])
    return {"w": w, "y": y, "z": z}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Analisis PWA PPG SON1303")
    ap.add_argument("file", nargs="?", default="rekam.txt")
    ap.add_argument("--session", type=int, default=None,
                    help="pilih sesi ke-N (default: terpanjang)")
    ap.add_argument("--zoom", type=float, nargs=2, metavar=("A", "B"),
                    default=None, help="zoom rentang waktu (detik) utk time-series")
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    try:
        sessions = parse_file(args.file)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {args.file}"); sys.exit(1)
    if not sessions:
        print("Tidak ada data valid."); sys.exit(1)

    arr = sessions[args.session - 1] if args.session else max(sessions, key=len)
    print(f"Sesi dipakai: {len(arr)} sampel ({len(arr)/FS:.1f}s)")

    t = (arr[:, 0] - arr[0, 0]) / 1000.0
    raw = arr[:, 1]

    # ----- filter & turunan -----
    ppg = bandpass(raw, 0.5, 15.0)    # PPG bersih untuk turunan
    vpg = derivative(ppg)             # turunan pertama
    apg = derivative(vpg)             # turunan kedua (SDPPG)
    freq, mag = compute_fft(raw)

    band = (freq > 0.7) & (freq < 3.0)
    f_ppg = freq[band][np.argmax(mag[band])]
    print(f"Frekuensi PPG dominan: {f_ppg:.2f} Hz (~{f_ppg*60:.0f} bpm)")

    # window zoom untuk time-series
    if args.zoom:
        m = (t >= args.zoom[0]) & (t <= args.zoom[1])
    else:
        c = len(t) // 2
        m = (t >= t[c]) & (t <= t[c] + 4)   # 4 detik di tengah

    # ================= PLOT =================
    fig = plt.figure(figsize=(15, 14))

    # (1) PPG band-pass
    ax1 = fig.add_subplot(5, 1, 1)
    ax1.plot(t[m], ppg[m], color="#e67300", lw=1.0)
    ax1.set_title("1. PPG band-pass 0.5-15 Hz"); ax1.grid(alpha=0.3)
    ax1.set_ylabel("amplitudo")

    # (2) FFT
    ax2 = fig.add_subplot(5, 1, 2)
    ax2.plot(freq, mag, color="#8e44ad", lw=0.8)
    ax2.set_xlim(0, 30)
    ax2.axvline(f_ppg, color="green", ls="--", lw=1, alpha=0.6,
                label=f"PPG {f_ppg:.2f} Hz")
    ax2.axvline(50, color="red", ls="--", lw=1, alpha=0.4, label="50 Hz")
    ax2.set_title("2. FFT - spektrum adc_raw")
    ax2.set_xlabel("frekuensi (Hz)"); ax2.set_ylabel("magnitudo")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

    # (3) VPG
    ax3 = fig.add_subplot(5, 1, 3)
    ax3.plot(t[m], vpg[m], color="#2980b9", lw=1.0)
    ax3.axhline(0, color="gray", lw=0.5)
    ax3.set_title("3. VPG - Velocity PPG (turunan pertama)")
    ax3.grid(alpha=0.3); ax3.set_ylabel("d PPG/dt")

    # (4) APG
    ax4 = fig.add_subplot(5, 1, 4)
    ax4.plot(t[m], apg[m], color="#16a085", lw=1.0)
    ax4.axhline(0, color="gray", lw=0.5)
    ax4.set_title("4. APG - Acceleration PPG (turunan kedua / SDPPG)")
    ax4.grid(alpha=0.3); ax4.set_ylabel("d2 PPG/dt2")

    # (5) Satu siklus VPG + APG dengan label
    ax5 = fig.add_subplot(5, 1, 5)
    onsets, pk = find_onsets(ppg)
    labeled = False
    if len(onsets) >= 3:
        mid = len(onsets) // 2
        i0, i1 = onsets[mid], onsets[mid + 1]
        if i1 - i0 > int(0.4 * FS):
            tc = np.arange(i1 - i0) / FS * 1000  # ms
            cyc_v = vpg[i0:i1]; cyc_a = apg[i0:i1]
            # normalisasi supaya dua kurva sebanding di satu sumbu
            cyc_vn = cyc_v / (np.max(np.abs(cyc_v)) + 1e-9)
            cyc_an = cyc_a / (np.max(np.abs(cyc_a)) + 1e-9)
            ax5.plot(tc, cyc_vn, color="#2980b9", lw=1.5, label="VPG (w,y,z)")
            ax5.plot(tc, cyc_an, color="#16a085", lw=1.5, label="APG (a-e)")
            ax5.axhline(0, color="gray", lw=0.5)
            # label APG a-b-c-d-e
            la = label_apg(cyc_a)
            if la:
                col = {"a": "red", "b": "blue", "c": "orange",
                       "d": "purple", "e": "brown"}
                for k, idx in la.items():
                    if idx is not None and 0 <= idx < len(cyc_an):
                        ax5.scatter(tc[idx], cyc_an[idx], color=col[k],
                                    s=55, zorder=5)
                        ax5.annotate(k, (tc[idx], cyc_an[idx]),
                                     textcoords="offset points", xytext=(0, 8),
                                     fontsize=11, fontweight="bold", color=col[k])
                a = cyc_a[la["a"]] if la["a"] is not None else np.nan
                def v(k): return cyc_a[la[k]] if la.get(k) is not None else np.nan
                if a and not np.isnan(a):
                    print("\nRasio APG (relatif ke a):")
                    for k in ["b", "c", "d", "e"]:
                        val = v(k)
                        if not np.isnan(val):
                            print(f"  {k}/a = {val/a:+.3f}")
                    bb, cc, dd, ee = v("b"), v("c"), v("d"), v("e")
                    if all(not np.isnan(x) for x in [bb, cc, dd, ee]):
                        print(f"  Aging Index (b-c-d-e)/a = {(bb-cc-dd-ee)/a:+.3f}")
                        print(f"  b/a (kekakuan arteri)    = {bb/a:+.3f}")
            # label VPG w,y,z
            lv = label_vpg(cyc_v)
            if lv:
                colv = {"w": "#c0392b", "y": "#16537e", "z": "#8e44ad"}
                for k, idx in lv.items():
                    if idx is not None and 0 <= idx < len(cyc_vn):
                        ax5.scatter(tc[idx], cyc_vn[idx], color=colv[k],
                                    s=45, marker="s", zorder=5)
                        ax5.annotate(k, (tc[idx], cyc_vn[idx]),
                                     textcoords="offset points", xytext=(0, -14),
                                     fontsize=10, fontweight="bold", color=colv[k])
            labeled = True
    if not labeled:
        ax5.text(0.5, 0.5, "Siklus tidak cukup jelas untuk pelabelan",
                 ha="center", transform=ax5.transAxes)
    ax5.set_title("5. Satu siklus - VPG (w,y,z) + APG (a,b,c,d,e), dinormalisasi")
    ax5.set_xlabel("waktu dalam siklus (ms)")
    ax5.set_ylabel("ternormalisasi"); ax5.grid(alpha=0.3)
    ax5.legend(fontsize=8, loc="upper right")

    plt.tight_layout()
    if args.save:
        out = "pwa_analysis.png"
        plt.savefig(out, dpi=120)
        print(f"\nTersimpan: {out}")
    plt.show()


if __name__ == "__main__":
    main()
