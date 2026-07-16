#!/usr/bin/env python3
"""
ANTARAGA Sensor Monitor
=======================
Visualisasi data serial sensor (MAX30102, SEN0203, dll.) secara real-time.

Fitur:
  - Auto-detect COM port + nama device
  - Pilih baud rate
  - Graf real-time multi-channel (scrolling)
  - Simpan SEMUA history (tidak terpotong seperti Arduino Serial Plotter)
  - Export CSV + Export gambar (PNG / JPG / PDF)
  - Pause tampilan tanpa menghentikan pengumpulan data
  - Log data mentah serial

Format data yang didukung (auto-detect):
  1. Angka saja        : "72,98,12345"
  2. Key=value         : "BPM=72.5,SPO2=98.2"
  3. Key:value         : "BPM:72 SPO2:98 GREEN:12345"
  4. Header + CSV      : baris pertama "BPM,SPO2,GREEN" lalu "72,98,12345"

Install dependensi:
  pip install pyserial matplotlib
"""

import csv
import queue
import re
import threading
import time
from collections import deque
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import serial
    import serial.tools.list_ports
    SERIAL_OK = True
except ImportError:
    SERIAL_OK = False

# ── Warna channel ────────────────────────────────────────────────────────────
COLORS = ['#89B4FA', '#F38BA8', '#A6E3A1', '#FAB387', '#CBA6F7',
          '#89DCEB', '#F9E2AF', '#94E2D5']

# ── Tema gelap (Catppuccin Mocha) ────────────────────────────────────────────
BG      = '#1E1E2E'
SURFACE = '#313244'
OVERLAY = '#45475A'
TEXT    = '#CDD6F4'
SUBTEXT = '#BAC2DE'


class SensorMonitor:
    MAX_HISTORY = 500_000  # maksimum baris data yang disimpan di memori

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ANTARAGA Sensor Monitor")
        self.root.geometry("1200x720")
        self.root.minsize(900, 550)
        self.root.configure(bg=BG)

        # ── State data ───────────────────────────────────────────────
        self.data_q: queue.Queue = queue.Queue()
        self.channel_names: list[str] = []
        # channel -> deque of (elapsed_s, value)  — SEMUA data sejak connect
        self.channel_history: dict[str, deque] = {}
        self.csv_rows: list[dict] = []

        self.t0: float | None = None
        self.sample_count = 0
        self._rate_t0 = time.time()
        self._rate_n0 = 0
        self.sample_rate = 0.0

        # ── State koneksi ────────────────────────────────────────────
        self.ser: 'serial.Serial | None' = None
        self.reader: threading.Thread | None = None
        self.running = False
        self.paused = False

        self._build_ui()
        self._refresh_ports()
        self._start_anim()

    # ════════════════════════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════════════════════════

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame',       background=BG)
        style.configure('TLabel',       background=BG,      foreground=TEXT)
        style.configure('TButton',      background=SURFACE, foreground=TEXT, padding=4)
        style.configure('TCombobox',    fieldbackground=SURFACE, background=SURFACE,
                        foreground=TEXT, selectbackground=OVERLAY)
        style.map('TButton', background=[('active', OVERLAY)])
        style.configure('Accent.TButton', background='#89B4FA', foreground=BG)

        # ── Toolbar ──────────────────────────────────────────────────
        bar = ttk.Frame(self.root, padding=(8, 6))
        bar.pack(fill='x')

        ttk.Label(bar, text="Port:").pack(side='left')
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(bar, textvariable=self.port_var,
                                     width=32, state='readonly')
        self.port_cb.pack(side='left', padx=(4, 2))
        ttk.Button(bar, text="⟳", width=3,
                   command=self._refresh_ports).pack(side='left', padx=(0, 12))

        ttk.Label(bar, text="Baud:").pack(side='left')
        self.baud_var = tk.StringVar(value='115200')
        ttk.Combobox(bar, textvariable=self.baud_var, width=10, state='readonly',
                     values=['9600','19200','38400','57600','115200',
                             '250000','500000','1000000']).pack(side='left', padx=(4, 12))

        self.conn_btn = ttk.Button(bar, text="▶  Connect",
                                   command=self._toggle_connect, style='Accent.TButton', width=14)
        self.conn_btn.pack(side='left', padx=(0, 16))

        ttk.Separator(bar, orient='vertical').pack(side='left', fill='y', padx=6)

        ttk.Label(bar, text="Window:").pack(side='left')
        self.win_var = tk.IntVar(value=10)
        ttk.Combobox(bar, textvariable=self.win_var, width=6, state='readonly',
                     values=[5, 10, 20, 30, 60, 120, 300]).pack(side='left', padx=(4, 2))
        ttk.Label(bar, text="dtk").pack(side='left', padx=(0, 12))

        self.pause_btn = ttk.Button(bar, text="⏸  Pause",
                                    command=self._toggle_pause, width=12)
        self.pause_btn.pack(side='left', padx=(0, 6))
        ttk.Button(bar, text="🗑  Clear",
                   command=self._clear, width=10).pack(side='left')

        # export kanan
        ttk.Button(bar, text="🖼  Export Gambar",
                   command=self._export_img).pack(side='right', padx=4)
        ttk.Button(bar, text="📄  Export CSV",
                   command=self._export_csv).pack(side='right', padx=4)

        # ── Panel tengah (graf + log) ─────────────────────────────────
        paned = tk.PanedWindow(self.root, orient='vertical',
                               bg=OVERLAY, sashwidth=4, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=8, pady=(4, 0))

        # Graf
        graph_frame = ttk.Frame(paned)
        paned.add(graph_frame, minsize=300)

        self.fig, self.ax = plt.subplots(figsize=(12, 5))
        self.fig.patch.set_facecolor(BG)
        self.ax.set_facecolor(BG)
        self._style_ax()

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        nav_frame = ttk.Frame(graph_frame)
        nav_frame.pack(fill='x')
        NavigationToolbar2Tk(self.canvas, nav_frame).update()

        # Log data mentah
        log_frame = ttk.Frame(paned)
        paned.add(log_frame, minsize=80)
        paned.sash_place(0, 0, 560)  # default split

        log_header = ttk.Frame(log_frame)
        log_header.pack(fill='x')
        ttk.Label(log_header, text="  Log Data Mentah Serial",
                  foreground=SUBTEXT).pack(side='left')
        ttk.Button(log_header, text="Bersihkan Log",
                   command=self._clear_log, width=14).pack(side='right', padx=4)

        self.log_text = tk.Text(log_frame, height=6, bg=SURFACE, fg=TEXT,
                                font=('Courier New', 9), state='disabled',
                                insertbackground=TEXT, relief='flat')
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        self.log_text.pack(fill='both', expand=True)

        self._log_q: queue.Queue = queue.Queue()

        # ── Status bar ────────────────────────────────────────────────
        status_bar = ttk.Frame(self.root, padding=(8, 3))
        status_bar.pack(fill='x', side='bottom')

        self.status_var = tk.StringVar(value="● Tidak terhubung")
        ttk.Label(status_bar, textvariable=self.status_var,
                  foreground='#6C7086').pack(side='left')

        self.stats_var = tk.StringVar(value="")
        ttk.Label(status_bar, textvariable=self.stats_var,
                  foreground=SUBTEXT).pack(side='right')

    def _style_ax(self):
        self.ax.tick_params(colors=SUBTEXT, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(OVERLAY)
        self.ax.set_xlabel('Waktu (detik)', color=SUBTEXT, fontsize=9)
        self.ax.set_ylabel('Nilai', color=SUBTEXT, fontsize=9)
        self.ax.grid(True, color=OVERLAY, linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.set_title('Menunggu data dari sensor...', color=TEXT, pad=8, fontsize=10)

    # ════════════════════════════════════════════════════════════════
    # Port management
    # ════════════════════════════════════════════════════════════════

    def _refresh_ports(self):
        if not SERIAL_OK:
            self.port_cb['values'] = ['⚠ pyserial tidak terinstall']
            return
        ports = serial.tools.list_ports.comports()
        items = [f"{p.device}  —  {p.description}" for p in sorted(ports)]
        self.port_cb['values'] = items or ['(tidak ada port terdeteksi)']
        if items:
            self.port_cb.current(0)

    def _selected_port(self) -> str:
        v = self.port_var.get()
        return v.split('  —  ')[0].strip() if '  —  ' in v else v.strip()

    # ════════════════════════════════════════════════════════════════
    # Connect / disconnect
    # ════════════════════════════════════════════════════════════════

    def _toggle_connect(self):
        if self.running:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        if not SERIAL_OK:
            messagebox.showerror("Error", "Install pyserial dulu:\n  pip install pyserial")
            return
        port = self._selected_port()
        if not port or 'tidak ada' in port or 'tidak terinstall' in port:
            messagebox.showwarning("Pilih port", "Pilih port serial yang valid terlebih dahulu.")
            return
        baud = int(self.baud_var.get())
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            self.running = True
            self.t0 = time.time()
            self._rate_t0 = self.t0
            self._rate_n0 = 0
            self.conn_btn.config(text="■  Disconnect")
            self.status_var.set(f"● Terhubung  {port}  @  {baud} baud")
            self.reader = threading.Thread(target=self._read_loop, daemon=True)
            self.reader.start()
        except Exception as exc:
            messagebox.showerror("Gagal connect", str(exc))

    def _disconnect(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.conn_btn.config(text="▶  Connect")
        self.status_var.set("● Tidak terhubung")

    # ════════════════════════════════════════════════════════════════
    # Serial reader (background thread)
    # ════════════════════════════════════════════════════════════════

    def _read_loop(self):
        header_seen = False
        while self.running and self.ser and self.ser.is_open:
            try:
                raw = self.ser.readline()
                if not raw:
                    continue
                line = raw.decode('utf-8', errors='replace').strip()
                if not line:
                    continue

                elapsed = time.time() - self.t0
                self._log_q.put(line)

                parsed = self._parse(line, elapsed, header_seen)
                if parsed is None:
                    # might be a header line — mark seen so next call treats as data
                    header_seen = True
                    continue
                header_seen = True
                self.data_q.put(parsed)

            except Exception:
                if self.running:
                    time.sleep(0.01)

    # ════════════════════════════════════════════════════════════════
    # Parser — mendukung berbagai format
    # ════════════════════════════════════════════════════════════════

    _KV_RE = re.compile(r'([A-Za-z_]\w*)\s*[=:]\s*(-?[\d.]+(?:e[+-]?\d+)?)')

    def _parse(self, line: str, t: float, header_seen: bool) -> dict | None:
        # 1. key=val or key:val
        kvs = self._KV_RE.findall(line)
        if kvs:
            row = {k: float(v) for k, v in kvs}
            row['_t'] = t
            return row

        # Normalise separators
        line2 = line.replace('\t', ',').replace(';', ',')
        parts = [p.strip() for p in re.split(r'[,\s]+', line2) if p.strip()]

        # 2. All non-numeric → header row
        if not header_seen and parts and all(not self._is_num(p) for p in parts):
            self.channel_names = parts
            return None

        nums = []
        for p in parts:
            try:
                nums.append(float(p))
            except ValueError:
                pass

        if not nums:
            return None

        # 3. Assign channel names
        names = (self.channel_names if self.channel_names and len(self.channel_names) == len(nums)
                 else [f'CH{i+1}' for i in range(len(nums))])
        row = dict(zip(names, nums))
        row['_t'] = t
        return row

    @staticmethod
    def _is_num(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    # ════════════════════════════════════════════════════════════════
    # Animation / graph update (main thread, setiap 100 ms)
    # ════════════════════════════════════════════════════════════════

    def _start_anim(self):
        self._anim = FuncAnimation(self.fig, self._update,
                                   interval=100, cache_frame_data=False)

    def _update(self, _frame):
        # Drain log queue → text widget
        log_lines = []
        while not self._log_q.empty():
            log_lines.append(self._log_q.get_nowait())
        if log_lines:
            self.log_text.config(state='normal')
            for ln in log_lines[-50:]:
                ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                self.log_text.insert('end', f"[{ts}]  {ln}\n")
            self.log_text.see('end')
            # Jaga agar tidak overflow
            lines_in_widget = int(self.log_text.index('end-1c').split('.')[0])
            if lines_in_widget > 1000:
                self.log_text.delete('1.0', f'{lines_in_widget - 500}.0')
            self.log_text.config(state='disabled')

        # Drain data queue
        new_data = False
        while not self.data_q.empty():
            row = self.data_q.get_nowait()
            t = row.pop('_t')

            for ch, val in row.items():
                if ch not in self.channel_history:
                    self.channel_history[ch] = deque()
                self.channel_history[ch].append((t, val))

            csv_row = {'timestamp': datetime.now().isoformat(timespec='milliseconds'),
                       'elapsed_s': round(t, 4)}
            csv_row.update(row)
            if len(self.csv_rows) < self.MAX_HISTORY:
                self.csv_rows.append(csv_row)

            self.sample_count += 1
            new_data = True

        # Update sample rate
        now = time.time()
        if (now - self._rate_t0) >= 1.0:
            self.sample_rate = (self.sample_count - self._rate_n0) / (now - self._rate_t0)
            self._rate_n0 = self.sample_count
            self._rate_t0 = now
            self.stats_var.set(
                f"{self.sample_rate:.1f} sampel/dtk  │  Total: {self.sample_count:,} sampel"
            )

        if self.paused or not self.channel_history:
            return

        # ── Gambar ulang ──────────────────────────────────────────
        win = self.win_var.get()
        all_t = [t for dq in self.channel_history.values() for t, _ in dq]
        if not all_t:
            return
        t_max = max(all_t)
        t_min = max(0.0, t_max - win)

        self.ax.clear()
        self.ax.set_facecolor(BG)
        self._style_ax()
        self.ax.set_xlim(t_min, t_max + 0.05)

        for i, (ch, dq) in enumerate(self.channel_history.items()):
            color = COLORS[i % len(COLORS)]
            xs = [t for t, _ in dq if t >= t_min]
            ys = [v for t, v in dq if t >= t_min]
            if xs:
                self.ax.plot(xs, ys, color=color, linewidth=1.2, label=ch)

        if self.channel_history:
            self.ax.legend(loc='upper left', facecolor=SURFACE, labelcolor=TEXT,
                           edgecolor=OVERLAY, framealpha=0.85, fontsize=8)

        port_label = self.port_var.get().split('  —  ')[0] if self.port_var.get() else ''
        self.ax.set_title(
            f"Sensor Data  —  {port_label}" if port_label else "Sensor Data",
            color=TEXT, pad=8, fontsize=10
        )

    # ════════════════════════════════════════════════════════════════
    # Controls
    # ════════════════════════════════════════════════════════════════

    def _toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="▶  Resume" if self.paused else "⏸  Pause")

    def _clear(self):
        self.channel_history.clear()
        self.csv_rows.clear()
        self.channel_names.clear()
        self.sample_count = 0
        self.t0 = time.time() if self.running else None
        self._clear_log()

    def _clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')

    # ════════════════════════════════════════════════════════════════
    # Export
    # ════════════════════════════════════════════════════════════════

    def _export_csv(self):
        if not self.csv_rows:
            messagebox.showinfo("Export CSV", "Belum ada data yang dikumpulkan.")
            return
        fname = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV', '*.csv'), ('Semua file', '*.*')],
            initialfile=fname,
        )
        if not path:
            return
        try:
            fields = list(self.csv_rows[0].keys())
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(self.csv_rows)
            messagebox.showinfo("Export CSV", f"✅ Berhasil disimpan ({len(self.csv_rows):,} baris):\n{path}")
        except Exception as exc:
            messagebox.showerror("Gagal", str(exc))

    def _export_img(self):
        fname = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg'), ('PDF', '*.pdf'), ('Semua file', '*.*')],
            initialfile=fname,
        )
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=150, bbox_inches='tight',
                             facecolor=self.fig.get_facecolor())
            messagebox.showinfo("Export Gambar", f"✅ Disimpan:\n{path}")
        except Exception as exc:
            messagebox.showerror("Gagal", str(exc))

    # ════════════════════════════════════════════════════════════════
    # Cleanup
    # ════════════════════════════════════════════════════════════════

    def close(self):
        self._disconnect()
        plt.close(self.fig)
        self.root.destroy()


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    if not SERIAL_OK:
        print("⚠️  pyserial tidak terinstall.\n   Jalankan:  pip install pyserial matplotlib")

    root = tk.Tk()
    app = SensorMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == '__main__':
    main()
