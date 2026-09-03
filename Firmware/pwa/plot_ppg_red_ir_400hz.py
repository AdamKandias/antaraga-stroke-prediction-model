#!/usr/bin/env python3
"""
Analisis & plot rekaman PPG mentah DUA KANAL (RED + IR) - KHUSUS 400 Hz.
Untuk tiap kanal: band-pass, FFT, turunan-1 (VPG), turunan-2 (SDPPG/APG).

Disetel untuk sampling 400 Hz (profil PWA recorder):
  - Jendela turunan Savitzky-Golay diskalakan ke ~50 ms (bukan jumlah sampel
    tetap), supaya turunan-2 tidak berisik pada laju tinggi.
  - Band-pass default 0.5-12 Hz (pertahankan komponen tinggi tempat notch).
  - Tampilan spektrum sampai 15 Hz.

Format input (recorder RED+IR):  t_ms, red_raw, ir_raw
(Kompatibel juga dengan format lama t_ms, ir_raw, ppg_bandpass -> hanya IR.)

Pemakaian:
    python plot_ppg_red_ir_400hz.py rekaman.csv
    python plot_ppg_red_ir_400hz.py rekaman.csv --band 0.5 15 --save
    python plot_ppg_red_ir_400hz.py rekaman.csv --channel ir
    python plot_ppg_red_ir_400hz.py rekaman.csv --fs 250      # override bila perlu
"""
import argparse
import sys
import numpy as np

try:
    import pandas as pd
except ImportError:
    sys.exit("Butuh pandas: pip install pandas")
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("Butuh matplotlib: pip install matplotlib")
try:
    from scipy.signal import butter, filtfilt, savgol_filter, welch
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

DERIV_WIN_MS = 50.0   # target lebar jendela turunan (ms) - diskalakan ke fs


def load_recording(path):
    """Baca robust; abaikan '#'/log boot; deteksi kolom dari header."""
    header_cols = None
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            s = ln.strip()
            if s.startswith("t_ms"):
                header_cols = [c.strip() for c in s.split(",")]
                continue
            parts = s.split(",")
            if len(parts) == 3:
                try:
                    rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
                except ValueError:
                    pass
    if not rows:
        sys.exit("Tidak ada baris data 3-kolom yang valid.")
    arr = np.array(rows)
    cols = header_cols if (header_cols and len(header_cols) == 3) \
        else ["t_ms", "red_raw", "ir_raw"]
    return pd.DataFrame(arr, columns=cols), cols


def sg_window(fs):
    """Jendela Savitzky-Golay ganjil yang mendekati DERIV_WIN_MS pada fs ini."""
    w = int(round(DERIV_WIN_MS / 1000.0 * fs))
    if w % 2 == 0:
        w += 1
    return max(5, w)   # minimal 5 untuk orde-3


def bandpass(x, fs, lo, hi):
    if HAVE_SCIPY:
        b, a = butter(4, [lo / (fs / 2), hi / (fs / 2)], btype="band")
        return filtfilt(b, a, x)
    x = x - np.mean(x)
    win = max(1, int(fs / (hi * 2)))
    return x - np.convolve(x, np.ones(win) / win, mode="same")


def deriv(x, fs, order):
    if HAVE_SCIPY:
        w = min(sg_window(fs), (len(x) // 2) * 2 - 1)
        return savgol_filter(x, w, 3, deriv=order, delta=1.0 / fs)
    d = np.gradient(x, 1.0 / fs)
    return d if order == 1 else np.gradient(d, 1.0 / fs)


def spectrum(x, fs):
    if HAVE_SCIPY:
        return welch(x, fs=fs, nperseg=min(len(x), int(fs * 8)))
    spec = np.abs(np.fft.rfft(x - x.mean())) ** 2
    return np.fft.rfftfreq(len(x), 1.0 / fs), spec


def analyze_channel(raw, fs, lo, hi, invert=True):
    bp = bandpass(raw, fs, lo, hi)
    if invert:
        bp = -bp   # PPG reflektif: sistol turun -> dibalik agar naik
    return {"bp": bp, "vpg": deriv(bp, fs, 1),
            "apg": deriv(bp, fs, 2), "spec": spectrum(bp, fs)}


def main():
    ap = argparse.ArgumentParser(description="Plot PPG RED & IR - khusus 400 Hz.")
    ap.add_argument("file")
    ap.add_argument("--fs", type=float, default=400.0,
                    help="laju sampel Hz (default 400)")
    ap.add_argument("--band", type=float, nargs=2, default=[0.5, 12.0],
                    metavar=("LO", "HI"))
    ap.add_argument("--channel", choices=["both", "red", "ir"], default="both")
    ap.add_argument("--no-invert", dest="invert", action="store_false", default=True)
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    fs, (lo, hi) = args.fs, args.band

    df, cols = load_recording(args.file)

    # Peringatan bila laju sampel mungkin tak cocok dengan data
    if len(df) > 1:
        dt = np.median(np.diff(df["t_ms"].values))
        fs_data = 1000.0 / dt if dt > 0 else fs
        if abs(fs_data - fs) / fs > 0.1:
            print(f"[peringatan] dt data ~{dt:.2f} ms (≈{fs_data:.0f} Hz) "
                  f"tak cocok dengan --fs {fs:.0f}. Sesuaikan --fs bila perlu.")

    n_skip = int(1.0 * fs)
    have_red, have_ir = "red_raw" in cols, "ir_raw" in cols
    if not have_ir and not have_red:
        have_ir = True
        df = df.rename(columns={cols[1]: "ir_raw"})

    channels = []
    if args.channel in ("both", "red") and have_red:
        channels.append(("RED", df["red_raw"].values.astype(float)[n_skip:], "tab:red"))
    if args.channel in ("both", "ir") and have_ir:
        channels.append(("IR", df["ir_raw"].values.astype(float)[n_skip:], "tab:brown"))
    if not channels:
        sys.exit(f"Kanal diminta tak ada. Kolom tersedia: {cols}")
    if args.channel == "both" and not have_red:
        print("[catatan] File hanya punya IR (tak ada red_raw).")

    t = np.arange(len(channels[0][1])) / fs
    show = t <= 8   # tampilkan 8 detik pertama utk keterbacaan

    nrow = len(channels)
    fig, ax = plt.subplots(nrow, 4, figsize=(20, 4.2 * nrow), squeeze=False)
    fig.suptitle(f"Analisis PPG RED & IR @ {fs:.0f} Hz - {args.file}  "
                 f"(band {lo}-{hi} Hz, SG~{sg_window(fs)} smp)", fontsize=13)

    for r, (name, raw, color) in enumerate(channels):
        res = analyze_channel(raw, fs, lo, hi, invert=args.invert)
        fxx, pxx = res["spec"]
        band_hr = (fxx >= 0.7) & (fxx <= 3.5)
        hr = fxx[band_hr][np.argmax(pxx[band_hr])] * 60 if band_hr.any() else float("nan")

        ax[r, 0].plot(t[show], res["bp"][show], color=color, lw=1.1)
        ax[r, 0].set_title(f"{name}: Band-pass"); ax[r, 0].set_ylabel(name)
        ax[r, 0].set_xlabel("s"); ax[r, 0].grid(alpha=0.3)

        ax[r, 1].semilogy(fxx, pxx, color=color, lw=1.0)
        ax[r, 1].axvline(hr / 60, color="green", ls="--", alpha=0.7, label=f"HR~{hr:.0f}")
        ax[r, 1].set_xlim(0, 15); ax[r, 1].set_title(f"{name}: FFT/spektrum")
        ax[r, 1].set_xlabel("Hz"); ax[r, 1].legend(); ax[r, 1].grid(alpha=0.3, which="both")

        ax[r, 2].plot(t[show], res["vpg"][show], color=color, lw=1.0)
        ax[r, 2].axhline(0, color="k", ls=":", alpha=0.4)
        ax[r, 2].set_title(f"{name}: Turunan-1 (VPG)"); ax[r, 2].set_xlabel("s")
        ax[r, 2].grid(alpha=0.3)

        ax[r, 3].plot(t[show], res["apg"][show], color=color, lw=1.0)
        ax[r, 3].axhline(0, color="k", ls=":", alpha=0.4)
        ax[r, 3].set_title(f"{name}: Turunan-2 (APG/SDPPG)"); ax[r, 3].set_xlabel("s")
        ax[r, 3].grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if not HAVE_SCIPY:
        print("[catatan] scipy tak terpasang -> filter/turunan sederhana. "
              "pip install scipy untuk hasil terbaik.")

    if args.save:
        out = args.file.rsplit(".", 1)[0] + "_red_ir_400hz.png"
        plt.savefig(out, dpi=110)
        print(f"Tersimpan: {out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
