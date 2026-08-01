#!/usr/bin/env python3
"""
ANTARAGA — Plotter 3 kanal PPG mentah (MERAH / INFRAMERAH / HIJAU)
=====================================================================
Pasangan PC untuk src/main.cpp. Membaca CSV dari serial, menggambar tiga
kurva yang masing-masing bisa dimatikan/dinyalakan, menghitung statistik
penempatan sensor secara langsung, dan merekam aliran mentahnya ke file.

  python gui/plotter.py                 # pilih port di jendela
  python gui/plotter.py COM7            # langsung ke port itu

Butuh: pyserial (pip install pyserial). numpy/matplotlib/tkinter sudah
standar di instalasi Python-mu.

CATATAN: satu port serial hanya bisa dipegang satu proses. Tutup serial
monitor PlatformIO sebelum menekan Sambung.
"""

import sys
import time
import queue
import threading
from collections import deque

import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("pyserial belum terpasang.  Jalankan:  pip install pyserial")
    sys.exit(1)

# ---------------------------------------------------------------------
# Kanal: (kunci, kolom di CSV, label, warna, skala penuh ADC)
# ---------------------------------------------------------------------
CHANNELS = [
    ("red",   2, "MERAH  660 nm  (MAX30102)",      "#e0564f", 262143),
    ("ir",    3, "INFRAMERAH  880 nm  (MAX30102)", "#7d74ea", 262143),
    ("green", 1, "HIJAU  525 nm  (SON1303)",       "#3cb371", 4095),
]
COL_T, COL_GREEN, COL_RED, COL_IR, COL_AV = 0, 1, 2, 3, 4
NCOL = 5

RING_CAP = 60000          # ~5 menit di 200 Hz
PLOT_MAX_PTS = 1500       # titik per kurva yang digambar (sisanya di-decimate)
# Satu penggambaran 3 kanal terukur 27-43 ms di mesin ini, jadi 70 ms
# (~14 FPS) menyisakan ruang napas. PPG isinya < 5 Hz — 14 FPS sudah jauh
# lebih dari cukup, dan 50 ms akan memakan hampir satu inti penuh terus-
# menerus tanpa terlihat lebih mulus.
PLOT_INTERVAL_MS = 70
STAT_INTERVAL_MS = 250

# Acuan dari rekaman optimasi (rekam_ppg_merah_v2_irred1.txt) —
# supaya angka perfusi di panel statistik ada pembandingnya.
REF_PI = {"red": 1.44, "ir": 3.03, "green": None}


# =====================================================================
# Penyangga cincin — dipakai daripada deque supaya tiap penggambaran
# tidak perlu menyalin ulang puluhan ribu nilai ke array baru.
# =====================================================================
class Ring:
    def __init__(self, cap, ncol):
        self.buf = np.zeros((cap, ncol), dtype=np.float64)
        self.cap = cap
        self.n = 0
        self.head = 0

    def clear(self):
        self.n = 0
        self.head = 0

    def append(self, rows):
        rows = np.asarray(rows, dtype=np.float64)
        k = len(rows)
        if k == 0:
            return
        if k >= self.cap:
            rows = rows[-self.cap:]
            k = len(rows)
        end = self.head + k
        if end <= self.cap:
            self.buf[self.head:end] = rows
        else:
            cut = self.cap - self.head
            self.buf[self.head:] = rows[:cut]
            self.buf[:end - self.cap] = rows[cut:]
        self.head = end % self.cap
        self.n = min(self.n + k, self.cap)

    def last(self, k):
        k = min(k, self.n)
        if k == 0:
            return np.zeros((0, self.buf.shape[1]))
        start = (self.head - k) % self.cap
        if start + k <= self.cap:
            return self.buf[start:start + k]
        return np.concatenate((self.buf[start:], self.buf[:start + k - self.cap]))


# =====================================================================
# Pembaca serial — thread terpisah
# =====================================================================
class Reader(threading.Thread):
    def __init__(self, port, baud, row_q, log_q):
        super().__init__(daemon=True)
        self.port, self.baud = port, baud
        self.row_q, self.log_q = row_q, log_q
        self.stop_evt = threading.Event()
        self.ser = None
        self._wlock = threading.Lock()
        self._rec = None
        self._rec_lock = threading.Lock()
        self.err = None

    # --- perekaman ---
    def rec_start(self, path, header_lines):
        with self._rec_lock:
            self.rec_stop()
            self._rec = open(path, "w", encoding="utf-8", newline="\n")
            self._rec.write("# ANTARAGA 3 kanal PPG mentah — %s\n"
                            % time.strftime("%Y-%m-%d %H:%M:%S"))
            for ln in header_lines:
                self._rec.write(ln if ln.endswith("\n") else ln + "\n")
            self._rec.write("t_ms,green,red,ir,av\n")
            self._rec.flush()

    def rec_stop(self):
        if self._rec:
            try:
                self._rec.write("# END\n")
                self._rec.close()
            except OSError:
                pass
            self._rec = None

    @property
    def recording(self):
        return self._rec is not None

    def send(self, ch):
        with self._wlock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(ch.encode())
                except serial.SerialException as e:
                    self.log_q.put("#GUI galat kirim: %s" % e)

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.2)
        except serial.SerialException as e:
            self.err = str(e)
            self.log_q.put("#GUI GAGAL buka %s: %s" % (self.port, e))
            return
        time.sleep(0.3)
        self.ser.reset_input_buffer()
        self.send("i")

        buf = b""
        pending = []
        last_flush = time.time()
        while not self.stop_evt.is_set():
            try:
                chunk = self.ser.read(8192)
            except serial.SerialException as e:
                self.log_q.put("#GUI koneksi putus: %s" % e)
                break
            if chunk:
                buf += chunk
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line:
                        continue
                    with self._rec_lock:
                        if self._rec:
                            self._rec.write(line + "\n")
                    if line[0] == "#":
                        self.log_q.put(line)
                        continue
                    parts = line.split(",")
                    if len(parts) != NCOL:
                        continue
                    try:
                        pending.append([float(p) for p in parts])
                    except ValueError:
                        continue
            now = time.time()
            if pending and (len(pending) >= 64 or now - last_flush > 0.05):
                self.row_q.put(pending)
                pending = []
                last_flush = now
            if not chunk:
                time.sleep(0.005)

        if pending:
            self.row_q.put(pending)
        with self._rec_lock:
            self.rec_stop()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except serial.SerialException:
            pass


# =====================================================================
# Analisis ringkas — dipakai panel statistik
# =====================================================================
def movavg(x, win):
    """Rerata bergerak dengan jendela TERPANGKAS di tepi (lewat cumsum).

    Tepinya wajib begini, bukan np.convolve(mode='same'): konvolusi itu
    menganggap di luar array nilainya nol, jadi baseline di tepi meluruh
    ke nol dan sinyal tepinya ikut rusak. Menambalnya dengan meratakan
    tepi ke satu konstanta lebih buruk lagi — plateau konstan berkorelasi
    sempurna dengan dirinya di SEMUA lag, sehingga autokorelasi derau
    murni pun terlihat sangat periodik (conf 0,45 padahal seharusnya
    0,05). Jendela yang menyusut di tepi tidak punya kedua cacat itu."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n < 4:
        return np.full(n, x.mean() if n else 0.0)
    win = max(3, int(win) | 1)
    h = win // 2
    cs = np.concatenate(([0.0], np.cumsum(x)))
    idx = np.arange(n)
    lo = np.clip(idx - h, 0, n)
    hi = np.clip(idx + h + 1, 0, n)
    return (cs[hi] - cs[lo]) / (hi - lo)


def detrend(x, win):
    return np.asarray(x, dtype=np.float64) - movavg(x, win)


def ac_signal(x, fs):
    """Ambil komponen denyut: high-pass DUA TINGKAT + low-pass ringan.

    Kenapa dua tingkat, bukan satu: gelombang napas ~0,25 Hz selalu ada di
    PPG nyata, dan satu tingkat rerata-bergerak hanya menekannya ke ~53%.
    Sisa sebesar itu membuat autokorelasi meluruh MONOTON sepanjang rentang
    lag, sehingga puncaknya selalu jatuh di lag terpendek — BPM apa pun
    dilaporkan sebagai ~220. Dua tingkat menekannya ke ~28% sementara
    denyut 43 bpm justru lolos dengan gain 1,23, jadi denyutnya kembali
    menang. (Terbukti: 43 & 60 bpm gagal dengan satu tingkat, lulus dengan
    dua.)

    Low-pass ~5 Hz membuang derau per sampel dan kedip lampu; jendela 17
    sampel pada 200 Hz kira-kira -3 dB di 5 Hz, dan pada 190 bpm masih
    meneruskan 88%."""
    fs = max(float(fs), 20.0)
    w_hp = fs * 2.5                     # sisakan 30..220 bpm
    y = detrend(detrend(x, w_hp), w_hp)
    return movavg(y, max(3, int(round(0.44 * fs / 5.0))))


def bpm_autocorr(x, fs, bpm_min=40.0, bpm_max=180.0):
    """Periode dominan lewat autokorelasi (FFT). Mengembalikan (bpm, conf).

    Autokorelasi dipilih, bukan pencari puncak, karena ia sekaligus
    melaporkan SEBERAPA periodik sinyalnya. Pencari puncak selalu
    menemukan sesuatu di derau dan melaporkan BPM yang terdengar
    meyakinkan; conf < 0,30 di sini berarti angkanya tidak berarti.

    Rentang 30..220 (dulu) kelewat lebar untuk tes duduk diam begini:
    MERAH/INFRAMERAH punya takik dikrotik & riak sisa yang autokorelasinya
    kadang lebih tinggi dari detak sebenarnya, jadi puncak tertinggi di
    rentang lebar itu bisa jatuh di 2x detak (takik dikrotik, ~200 bpm)
    atau setengah detak (modulasi napas/amplitudo, ~35 bpm) alih-alih
    detak asli. 40..180 masih longgar untuk istirahat sampai olahraga
    ringan, tapi cukup sempit untuk membuang dua jenis kesalahan oktaf
    itu. Naikkan lagi kalau subjeknya bayi (>180) atau atlet sangat
    bugar saat istirahat (<40)."""
    n = len(x)
    if n < int(fs * 4) or fs < 20:
        return None, 0.0
    y = ac_signal(x, fs)
    y -= y.mean()
    r0 = float(np.dot(y, y)) / n
    if r0 <= 0:
        return None, 0.0
    nf = 1 << (2 * n - 1).bit_length()
    f = np.fft.rfft(y, nf)
    ac = np.fft.irfft(f * np.conj(f), nf)[:n] / n
    lo = int(fs * 60.0 / bpm_max)
    hi = min(int(fs * 60.0 / bpm_min), n // 2)
    if hi - lo < 3:
        return None, 0.0
    seg = ac[lo:hi]

    # WAJIB maksimum LOKAL, bukan sekadar argmax rentang. np.argmax selalu
    # mengembalikan sesuatu — termasuk saat kurvanya cuma meluruh monoton
    # tanpa puncak sama sekali, dan maksimum kurva meluruh selalu jatuh di
    # ujung rentang, yaitu lag terpendek = 220 bpm. Itulah asal angka
    # "kadang 220 bpm" pada sinyal yang sebenarnya tidak punya denyut.
    inner = seg[1:-1]
    peak = (inner > seg[:-2]) & (inner >= seg[2:])
    if not peak.any():
        return None, 0.0
    cand = np.flatnonzero(peak) + 1
    b = int(cand[np.argmax(seg[cand])])

    # Interpolasi parabola: pada 220 bpm satu lag bernilai ~4 bpm, jadi tanpa
    # ini resolusinya kasar sekali di ujung atas rentang.
    y0, y1, y2 = float(seg[b - 1]), float(seg[b]), float(seg[b + 1])
    den = y0 - 2.0 * y1 + y2
    frac = 0.5 * (y0 - y2) / den if den < -1e-12 else 0.0
    frac = max(-0.5, min(0.5, frac))
    # conf negatif berarti "puncak" terbaik pun antikorelasi = tidak ada
    # periodisitas sama sekali; 0,00 lebih jelas dibaca daripada -0,16.
    return 60.0 * fs / (lo + b + frac), max(0.0, float(y1 / r0))


# =====================================================================
# Aplikasi
# =====================================================================
class App:
    def __init__(self, root, port_hint=None):
        self.root = root
        root.title("ANTARAGA — Plotter 3 Kanal PPG Mentah")
        root.geometry("1180x820")

        self.ring = Ring(RING_CAP, NCOL)
        self.row_q = queue.Queue()
        self.log_q = queue.Queue()
        self.reader = None
        self.meta = deque(maxlen=40)
        self.fs = 200.0
        self.frozen = False

        self._build_ui(port_hint)
        self._rebuild_axes()
        # id disimpan supaya bisa dibatalkan saat tutup (dan bisa dimatikan
        # oleh uji otomatis yang ingin memanggil tick-nya sendiri).
        self._id_plot = self.root.after(PLOT_INTERVAL_MS, self._tick_plot)
        self._id_stats = self.root.after(STAT_INTERVAL_MS, self._tick_stats)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- UI ----------------
    def _build_ui(self, port_hint):
        bar = ttk.Frame(self.root, padding=(8, 6))
        bar.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(bar, text="Port").pack(side=tk.LEFT)
        self.cmb_port = ttk.Combobox(bar, width=22, state="readonly")
        self.cmb_port.pack(side=tk.LEFT, padx=(4, 2))
        ttk.Button(bar, text="↻", width=3, command=self._refresh_ports).pack(side=tk.LEFT)
        self._refresh_ports()
        if port_hint:
            self.cmb_port.set(port_hint)

        ttk.Label(bar, text="Baud").pack(side=tk.LEFT, padx=(10, 2))
        self.cmb_baud = ttk.Combobox(bar, width=9, state="readonly",
                                     values=["921600", "115200", "460800", "2000000"])
        self.cmb_baud.set("921600")
        self.cmb_baud.pack(side=tk.LEFT)

        self.btn_conn = ttk.Button(bar, text="Sambung", command=self._toggle_conn)
        self.btn_conn.pack(side=tk.LEFT, padx=10)

        self.btn_rec = ttk.Button(bar, text="● Rekam CSV", command=self._toggle_rec,
                                  state=tk.DISABLED)
        self.btn_rec.pack(side=tk.LEFT)
        ttk.Button(bar, text="Bersihkan", command=self._clear).pack(side=tk.LEFT, padx=6)
        self.btn_freeze = ttk.Button(bar, text="Beku", command=self._toggle_freeze)
        self.btn_freeze.pack(side=tk.LEFT)

        # --- panel kiri ---
        body = ttk.Frame(self.root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        side = ttk.Frame(body, padding=(8, 4))
        side.pack(side=tk.LEFT, fill=tk.Y)

        box = ttk.LabelFrame(side, text="Kurva", padding=6)
        box.pack(fill=tk.X)
        self.var_en = {}
        for key, _col, label, color, _fs in CHANNELS:
            v = tk.BooleanVar(value=True)
            self.var_en[key] = v
            cb = tk.Checkbutton(box, text=label.split("(")[0].strip(), variable=v,
                                command=self._rebuild_axes, fg=color,
                                selectcolor="#ffffff", anchor="w", justify="left")
            cb.pack(fill=tk.X, anchor="w")

        self.var_overlay = tk.BooleanVar(value=False)
        tk.Checkbutton(box, text="Tumpuk 1 sumbu\n(ternormalisasi)",
                       variable=self.var_overlay, command=self._rebuild_axes,
                       anchor="w", justify="left").pack(fill=tk.X, pady=(6, 0))
        self.var_ac = tk.BooleanVar(value=False)
        tk.Checkbutton(box, text="Tampilkan AC saja\n(buang baseline)",
                       variable=self.var_ac, anchor="w",
                       justify="left").pack(fill=tk.X)

        wbox = ttk.LabelFrame(side, text="Jendela tampil", padding=6)
        wbox.pack(fill=tk.X, pady=8)
        self.var_win = tk.DoubleVar(value=10.0)
        for sec in (5, 10, 20, 30, 60):
            ttk.Radiobutton(wbox, text="%d detik" % sec, value=float(sec),
                            variable=self.var_win).pack(anchor="w")

        cbox = ttk.LabelFrame(side, text="Kendali perangkat", padding=6)
        cbox.pack(fill=tk.X)
        row = ttk.Frame(cbox); row.pack(fill=tk.X)
        ttk.Label(row, text="Arus MERAH").pack(side=tk.LEFT)
        ttk.Button(row, text="−", width=3, command=lambda: self._send("r")).pack(side=tk.RIGHT)
        ttk.Button(row, text="+", width=3, command=lambda: self._send("R")).pack(side=tk.RIGHT)
        row = ttk.Frame(cbox); row.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row, text="Arus INFRAMERAH").pack(side=tk.LEFT)
        ttk.Button(row, text="−", width=3, command=lambda: self._send("f")).pack(side=tk.RIGHT)
        ttk.Button(row, text="+", width=3, command=lambda: self._send("F")).pack(side=tk.RIGHT)
        ttk.Button(cbox, text="Hijau (SON1303) mati/nyala",
                   command=lambda: self._send("g")).pack(fill=tk.X, pady=(6, 0))
        ttk.Button(cbox, text="Nolkan cacahan",
                   command=lambda: self._send("z")).pack(fill=tk.X, pady=(2, 0))
        ttk.Label(cbox, text="Mematikan hijau TIDAK\nmematikan merah/inframerah\n"
                            "(MAX30102 tidak lewat Q2)",
                  foreground="#666").pack(anchor="w", pady=(6, 0))

        # --- kanvas ---
        right = ttk.Frame(body)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # constrained_layout SENGAJA tidak dipakai: ia menyelesaikan ulang tata
        # letak pada SETIAP penggambaran, dan dengan 3 subplot itu menembus
        # 50 ms — lebih lama dari interval timer, sehingga callback menumpuk
        # lebih cepat daripada yang bisa dilayani dan CPU langsung penuh.
        # Tata letak diatur sekali saja di _rebuild_axes().
        self.fig = Figure(figsize=(9, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- statistik ---
        sbox = ttk.LabelFrame(self.root, text="Statistik jendela (DC & AC mentah, "
                                             "perfusi = AC/DC, BPM = autokorelasi)",
                              padding=(8, 4))
        sbox.pack(side=tk.TOP, fill=tk.X)
        cols = ("kanal", "DC", "AC p2p (1 dtk)", "perfusi permil", "acuan permil",
                "BPM", "periodisitas")
        self.tree = ttk.Treeview(sbox, columns=cols, show="headings", height=3)
        for c, w in zip(cols, (200, 90, 110, 120, 110, 80, 100)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill=tk.X)
        for key, _c, label, _col, _fs in CHANNELS:
            self.tree.insert("", "end", iid=key, values=(label, "-", "-", "-", "-", "-", "-"))

        self.lbl_status = ttk.Label(self.root, text="Belum tersambung.",
                                    anchor="w", padding=(8, 3))
        self.lbl_status.pack(side=tk.TOP, fill=tk.X)
        self.txt_log = tk.Text(self.root, height=5, wrap="none", state=tk.DISABLED,
                               font=("Consolas", 8))
        self.txt_log.pack(side=tk.TOP, fill=tk.X)

    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.cmb_port["values"] = ports
        if ports and not self.cmb_port.get():
            self.cmb_port.set(ports[0])

    # ---------------- koneksi ----------------
    def _toggle_conn(self):
        if self.reader and self.reader.is_alive():
            self.reader.stop_evt.set()
            self.reader.join(timeout=1.5)
            self.reader = None
            self.btn_conn.config(text="Sambung")
            self.btn_rec.config(state=tk.DISABLED, text="● Rekam CSV")
            self._log("#GUI terputus")
            return
        port = self.cmb_port.get().strip()
        if not port:
            messagebox.showwarning("Port", "Pilih port serial dulu.")
            return
        self.reader = Reader(port, int(self.cmb_baud.get()), self.row_q, self.log_q)
        self.reader.start()
        self.btn_conn.config(text="Putus")
        self.btn_rec.config(state=tk.NORMAL)
        self._log("#GUI menyambung ke %s" % port)

    def _send(self, ch):
        if self.reader:
            self.reader.send(ch)

    def _toggle_rec(self):
        if not self.reader:
            return
        if self.reader.recording:
            self.reader.rec_stop()
            self.btn_rec.config(text="● Rekam CSV")
            self._log("#GUI rekaman ditutup")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="rekam_3ch.txt",
            filetypes=[("Teks/CSV", "*.txt *.csv"), ("Semua", "*.*")])
        if not path:
            return
        self.reader.rec_start(path, list(self.meta))
        self.btn_rec.config(text="■ Stop rekam")
        self._log("#GUI merekam ke %s" % path)

    def _clear(self):
        self.ring.clear()

    def _toggle_freeze(self):
        self.frozen = not self.frozen
        self.btn_freeze.config(text="Lanjut" if self.frozen else "Beku")

    def _log(self, line):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert("end", line + "\n")
        self.txt_log.see("end")
        if float(self.txt_log.index("end-1c").split(".")[0]) > 300:
            self.txt_log.delete("1.0", "100.0")
        self.txt_log.config(state=tk.DISABLED)

    # ---------------- sumbu ----------------
    def _rebuild_axes(self):
        """Tata ulang subplot. Kanal yang dimatikan tidak menyisakan ruang
        kosong — sumbunya benar-benar dibuang, bukan cuma disembunyikan."""
        self.fig.clear()
        self.lines = {}
        active = [c for c in CHANNELS if self.var_en[c[0]].get()]
        if not active:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "Semua kurva dimatikan", ha="center", va="center",
                    transform=ax.transAxes, color="#888")
            ax.set_xticks([]); ax.set_yticks([])
            self.canvas.draw_idle()
            return

        if self.var_overlay.get():
            ax = self.fig.add_subplot(111)
            ax.set_ylabel("ternormalisasi (z-score)")
            ax.set_xlabel("detik (0 = sekarang)")
            ax.grid(alpha=0.25)
            for key, _col, label, color, _full in active:
                (ln,) = ax.plot([], [], lw=1.0, color=color, label=label)
                self.lines[key] = (ax, ln)
            ax.legend(loc="upper left", fontsize=8)
        else:
            first = None
            for i, (key, _col, label, color, _full) in enumerate(active):
                ax = self.fig.add_subplot(len(active), 1, i + 1, sharex=first)
                first = first or ax
                (ln,) = ax.plot([], [], lw=1.0, color=color)
                ax.set_ylabel("LSB", fontsize=8)
                ax.set_title(label, fontsize=9, loc="left", color=color)
                ax.grid(alpha=0.25)
                ax.tick_params(labelsize=8)
                if i < len(active) - 1:
                    ax.tick_params(labelbottom=False)
                else:
                    ax.set_xlabel("detik (0 = sekarang)")
                self.lines[key] = (ax, ln)
        self.fig.subplots_adjust(left=0.10, right=0.99, top=0.94, bottom=0.10,
                                 hspace=0.42)
        self.canvas.draw_idle()

    # ---------------- loop gambar ----------------
    def _drain(self):
        got = 0
        while True:
            try:
                rows = self.row_q.get_nowait()
            except queue.Empty:
                break
            self.ring.append(rows)
            got += len(rows)
        while True:
            try:
                line = self.log_q.get_nowait()
            except queue.Empty:
                break
            self.meta.append(line)
            self._log(line)
            if line.startswith("#stat"):
                for tok in line.split():
                    if tok.startswith("fs="):
                        try:
                            v = float(tok[3:])
                            if v > 20:
                                self.fs = v
                        except ValueError:
                            pass
        return got

    def _window_data(self):
        need = int(self.var_win.get() * max(self.fs, 20) * 1.2) + 10
        return self.ring.last(min(need, RING_CAP))

    @staticmethod
    def _pace(t_start, floor_ms):
        """Jadwalkan tick berikutnya paling cepat selama tick ini berjalan.

        Tanpa ini, kalau satu penggambaran lebih lama dari intervalnya, timer
        Tk menumpuk lebih cepat daripada yang bisa dilayani: CPU langsung
        100% dan jendela berhenti merespons. Penjadwalan yang mengikuti
        biaya nyata membuat GUI melambat dengan mulus alih-alih macet."""
        el = int((time.perf_counter() - t_start) * 1000)
        return max(floor_ms, min(el * 2, 1000))

    def _tick_plot(self):
        t_start = time.perf_counter()
        self._drain()
        if not self.frozen and self.lines:
            d = self._window_data()
            if len(d) > 4:
                t = (d[:, COL_T] - d[-1, COL_T]) / 1000.0
                keep = t >= -self.var_win.get()
                d, t = d[keep], t[keep]
                step = max(1, len(t) // PLOT_MAX_PTS)
                ts = t[::step]
                for key, col, _label, _color, _full in CHANNELS:
                    if key not in self.lines:
                        continue
                    ax, ln = self.lines[key]
                    y = d[:, col]
                    if self.var_overlay.get():
                        y = ac_signal(y, self.fs)
                        sd = y.std()
                        y = y / sd if sd > 1e-9 else y
                    elif self.var_ac.get():
                        y = ac_signal(y, self.fs)
                    ys = y[::step]
                    ln.set_data(ts, ys)
                    ax.set_xlim(-self.var_win.get(), 0)
                    if len(ys):
                        lo, hi = float(ys.min()), float(ys.max())
                        pad = max((hi - lo) * 0.08, 1e-6)
                        ax.set_ylim(lo - pad, hi + pad)
                self.canvas.draw_idle()
        self._id_plot = self.root.after(self._pace(t_start, PLOT_INTERVAL_MS),
                                        self._tick_plot)

    def _tick_stats(self):
        t_start = time.perf_counter()
        # Ikut menguras antrean supaya panel ini tidak bergantung pada loop
        # gambar. _drain() idempoten, jadi dua pemanggil tidak masalah.
        self._drain()
        d = self._window_data()
        if len(d) > 8:
            t = d[:, COL_T]
            span = (t[-1] - t[0]) / 1000.0
            fs_meas = (len(d) - 1) / span if span > 0.2 else float("nan")
            if fs_meas == fs_meas and fs_meas > 20:
                self.fs = 0.7 * self.fs + 0.3 * fs_meas

            n1s = min(len(d), max(8, int(self.fs)))
            for key, col, label, _color, _full in CHANNELS:
                y = d[:, col]
                dc = float(y.mean())
                seg = y[-n1s:]
                ac = float(seg.max() - seg.min())
                pi = 1000.0 * ac / dc if dc > 1 else 0.0
                bpm, conf = bpm_autocorr(y, self.fs)
                ref = REF_PI.get(key)
                self.tree.item(key, values=(
                    label,
                    "%.0f" % dc,
                    "%.0f" % ac,
                    "%.2f" % pi,
                    ("%.2f" % ref) if ref else "—",
                    ("%.1f" % bpm) if bpm else "—",
                    ("%.2f" % conf) + ("" if conf >= 0.30 else "  (derau)"),
                ))
            late = int(d[:, COL_AV].max())
            self.lbl_status.config(
                text="fs terukur %.1f Hz   |   %d baris di penyangga   |   "
                     "av maks %d %s   |   %s"
                     % (self.fs, self.ring.n, late,
                        "(FIFO menumpuk)" if late > 1 else "(sehat)",
                        "MEREKAM" if (self.reader and self.reader.recording) else "siap"))
        self._id_stats = self.root.after(self._pace(t_start, STAT_INTERVAL_MS),
                                         self._tick_stats)

    def _on_close(self):
        for i in (getattr(self, "_id_plot", None), getattr(self, "_id_stats", None)):
            if i:
                try:
                    self.root.after_cancel(i)
                except tk.TclError:
                    pass
        if self.reader:
            self.reader.stop_evt.set()
            self.reader.join(timeout=1.5)
        self.root.destroy()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    try:
        root.call("tk", "scaling", 1.15)
    except tk.TclError:
        pass
    App(root, port)
    root.mainloop()


if __name__ == "__main__":
    main()
