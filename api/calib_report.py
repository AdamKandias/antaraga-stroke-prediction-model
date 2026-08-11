"""
Laporan hasil pemeriksaan per-rekaman kalibrasi — siap cetak / simpan PDF.

Menghasilkan satu halaman HTML berukuran A4 yang di-render browser lalu
dicetak lewat dialog "Save as PDF".  Tidak memakai library PDF sama sekali:
kontrol tipografi penuh, logo di-embed sebagai data URI, dan hasilnya identik
di semua mesin karena semuanya self-contained.

Dipakai oleh endpoint GET /v1/calibrate/{record_id}/laporan.html (api/main.py).
"""
from __future__ import annotations

import base64
import hashlib
import pathlib
from datetime import datetime, timedelta, timezone

import numpy as np

BRAND = "#007e73"          # teal wordmark antaraga
BRAND_DARK = "#005b53"
_ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

# WIB — semua timestamp DB disimpan UTC (datetime.utcnow), laporan tampil lokal.
_WIB = timezone(timedelta(hours=7))

_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


# ── Aset ───────────────────────────────────────────────────────────────────

_logo_cache: str | None = None


def _logo_data_uri() -> str:
    """Logo antaraga sebagai data URI.  Dibaca sekali lalu di-cache.

    Versi wordmark (sudah dipangkas margin putihnya) dipakai lebih dulu: ikon
    aslinya kanvas 512×512 dengan tulisan hanya di pita tengah, jadi kalau
    dipasang di kop surat tulisannya jadi kecil sekali.
    """
    global _logo_cache
    if _logo_cache is None:
        _logo_cache = ""
        for nama in ("logo-antaraga-wordmark.png", "icon-antaraga.png"):
            p = _ASSETS / nama
            if p.exists():
                _logo_cache = "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
                break
    return _logo_cache


# ── Ikon garis-tunggal (inline SVG, ikut warna currentColor) ───────────────
# Emoji tidak dipakai: render-nya beda-beda antar OS dan terlihat murah di
# dokumen cetak.  SVG stroke tetap tajam di berbagai DPI printer.

_ICON_BODY = {
    "heart": '<path d="M12 20.5S3.5 15 3.5 9.2A4.7 4.7 0 0 1 12 6.4a4.7 4.7 0 0 1 8.5 2.8c0 5.8-8.5 11.3-8.5 11.3Z"/>',
    "gauge": '<path d="M4 18a8.5 8.5 0 1 1 16 0"/><path d="M12 18V9"/><path d="m12 9 4-2.5"/><circle cx="12" cy="18" r="1.3"/>',
    "droplet": '<path d="M12 3s5.5 6 5.5 9.7A5.5 5.5 0 0 1 6.5 12.7C6.5 9 12 3 12 3Z"/>',
    "flask": '<path d="M9.5 3h5"/><path d="M10.5 3v6.2L5.8 17.4A2 2 0 0 0 7.5 20.5h9a2 2 0 0 0 1.7-3.1L13.5 9.2V3"/><path d="M8 14.5h8"/>',
    "molecule": '<circle cx="12" cy="5.5" r="2.2"/><circle cx="5.5" cy="17" r="2.2"/><circle cx="18.5" cy="17" r="2.2"/><path d="M10.6 7.4 7 14.2M13.4 7.4 17 14.2M7.7 17h8.6"/>',
    "wave": '<path d="M2 12h3l2.5-6 4 13L15 9l2 3h5"/>',
    "user": '<circle cx="12" cy="8" r="3.6"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>',
    "shield": '<path d="M12 3 5 6v6c0 4.4 3 7.7 7 9 4-1.3 7-4.6 7-9V6Z"/><path d="M12 9v4"/><path d="M12 16h.01"/>',
    "chip": '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    "check": '<path d="m4.5 12.5 5 5 10-11"/>',
    "alert": '<path d="M12 4.5 2.8 20h18.4Z"/><path d="M12 10v4.2M12 17h.01"/>',
}


def _icon(name: str, size: int = 14, stroke: float = 1.7) -> str:
    body = _ICON_BODY.get(name, "")
    return (
        f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


# ── Klasifikasi klinis ─────────────────────────────────────────────────────
# tone: ok | low | watch | high | crit | na  → dipetakan ke warna badge di CSS.

def _classify_bp(sis: float | None, dia: float | None) -> tuple[str, str]:
    """Klasifikasi tekanan darah — ESC/ESH & Konsensus PERHI.

    Bila sistolik dan diastolik jatuh di kategori berbeda, yang dipakai adalah
    kategori tertinggi (aturan baku pada guideline hipertensi).
    """
    if sis is None and dia is None:
        return ("Tidak diukur", "na")
    s = sis if sis is not None else 0
    d = dia if dia is not None else 0
    if s >= 180 or d >= 110:
        return ("Hipertensi Derajat 3", "crit")
    if s >= 160 or d >= 100:
        return ("Hipertensi Derajat 2", "crit")
    if s >= 140 or d >= 90:
        return ("Hipertensi Derajat 1", "high")
    if s >= 130 or d >= 85:
        return ("Normal Tinggi (Pra-hipertensi)", "watch")
    if s < 90 or (d and d < 60):
        return ("Hipotensi", "low")
    if s >= 120 or d >= 80:
        return ("Normal", "ok")
    return ("Optimal", "ok")


def _classify_bpm(bpm: float | None) -> tuple[str, str]:
    if bpm is None:
        return ("Tidak terukur", "na")
    if bpm < 50:
        return ("Bradikardia", "high")
    if bpm < 60:
        return ("Bradikardia Ringan", "watch")
    if bpm <= 100:
        return ("Normal (Sinus)", "ok")
    if bpm <= 120:
        return ("Takikardia Ringan", "watch")
    return ("Takikardia", "high")


_KONDISI_LABEL = {
    "puasa": "Puasa (≥8 jam)",
    "2j_setelah_makan": "2 Jam Setelah Makan",
    "2j_makan": "2 Jam Setelah Makan",
    "sewaktu": "Sewaktu (Acak)",
}


def _glucose_ref(kondisi: str | None) -> str:
    k = (kondisi or "sewaktu").lower()
    if k == "puasa":
        return "70 – 99 (puasa)"
    if k.startswith("2j"):
        return "< 140 (2 jam PP)"
    return "< 140 (sewaktu)"


def _classify_glucose(val: float | None, kondisi: str | None) -> tuple[str, str]:
    """Ambang ADA / PERKENI — batasnya berbeda per kondisi pengambilan."""
    if val is None:
        return ("Tidak diukur", "na")
    k = (kondisi or "sewaktu").lower()
    if k == "puasa":
        if val < 70:
            return ("Hipoglikemia", "high")
        if val < 100:
            return ("Normal", "ok")
        if val < 126:
            return ("Prediabetes (GDPT)", "watch")
        return ("Rentang Diabetes", "crit")
    # 2 jam post-prandial dan sewaktu memakai ambang yang sama
    if val < 70:
        return ("Hipoglikemia", "high")
    if val < 140:
        return ("Normal", "ok")
    if val < 200:
        return ("Prediabetes (TGT)", "watch")
    return ("Rentang Diabetes", "crit")


def _classify_chol(val: float | None) -> tuple[str, str]:
    if val is None:
        return ("Tidak diukur", "na")
    if val < 200:
        return ("Optimal", "ok")
    if val < 240:
        return ("Batas Tinggi", "watch")
    return ("Tinggi (Hiperkolesterolemia)", "high")


def _classify_uric(val: float | None, gender: str) -> tuple[str, str]:
    if val is None:
        return ("Tidak diukur", "na")
    lo, hi = (3.4, 7.0) if gender == "L" else (2.4, 6.0)
    if val < lo:
        return ("Di Bawah Rujukan", "low")
    if val <= hi:
        return ("Normal", "ok")
    return ("Hiperurisemia", "high")


def _uric_ref(gender: str) -> str:
    return "3,4 – 7,0 (pria)" if gender == "L" else "2,4 – 6,0 (wanita)"


# ── Utilitas format (locale Indonesia: koma desimal, titik ribuan) ─────────

def _num(v: float | None, dec: int = 1) -> str:
    if v is None:
        return "—"
    s = f"{float(v):,.{dec}f}"
    return s.replace(",", " ").replace(".", ",")


def _int(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{int(round(float(v))):,}".replace(",", ".")


def _tgl_panjang(dt: datetime) -> str:
    return f"{dt.day} {_BULAN[dt.month - 1]} {dt.year}"


def _parse_raw(raw: str | None) -> np.ndarray:
    if not raw:
        return np.array([], dtype=float)
    try:
        return np.fromstring(raw.replace(";", " "), sep=" ", dtype=float)
    except Exception:
        return np.array([], dtype=float)


# ── Strip gelombang PPG ────────────────────────────────────────────────────

def _ppg_strip_svg(ir: np.ndarray, fs: float, seconds: float = 8.0) -> str:
    """Gelombang denyut inframerah pada kertas berpetak, gaya strip rekam medis.

    Mengembalikan string kosong bila sinyal terlalu pendek untuk difilter —
    lebih baik menghilangkan panelnya daripada mencetak garis datar palsu.
    """
    if ir.size < 60:
        return ""

    fs = max(float(fs or 100.0), 20.0)
    seg = ir[-int(seconds * fs):] if ir.size > seconds * fs else ir

    try:
        from api.ppg_analysis import ac_signal
        y = ac_signal(seg, fs)
    except Exception:
        return ""

    span = float(np.percentile(y, 99) - np.percentile(y, 1))
    if not np.isfinite(span) or span <= 0:
        return ""

    W, H = 1000.0, 190.0
    pad = 12.0

    # Turunkan resolusi ke ±900 titik: cukup untuk mata pada lebar 180 mm,
    # dan menjaga ukuran HTML tetap kecil.
    if y.size > 900:
        y = y[np.linspace(0, y.size - 1, 900).astype(int)]

    xs = np.linspace(pad, W - pad, y.size)
    mid = H / 2.0
    amp = (H / 2.0 - pad) / (span / 2.0)
    ys = np.clip(mid - y * amp, 2.0, H - 2.0)

    pts = " ".join(f"{x:.1f},{v:.1f}" for x, v in zip(xs, ys))
    dur = seg.size / fs

    return f"""
    <div class="strip">
      <svg viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" class="strip-svg">
        <defs>
          <pattern id="gminor" width="20" height="19" patternUnits="userSpaceOnUse">
            <path d="M20 0H0V19" fill="none" stroke="#d9ebe8" stroke-width="0.7"/>
          </pattern>
          <pattern id="gmajor" width="100" height="95" patternUnits="userSpaceOnUse">
            <rect width="100" height="95" fill="url(#gminor)"/>
            <path d="M100 0H0V95" fill="none" stroke="#a8d5ce" stroke-width="1.1"/>
          </pattern>
        </defs>
        <rect width="{W:.0f}" height="{H:.0f}" fill="url(#gmajor)"/>
        <polyline points="{pts}" fill="none" stroke="{BRAND}" stroke-width="1.9"
                  stroke-linejoin="round" stroke-linecap="round"/>
      </svg>
      <div class="strip-cap">
        <span>Kanal inframerah · komponen denyut (bandpass 0,5–5 Hz)</span>
        <span>Durasi {_num(dur, 1)} dtk · laju cuplik {_num(fs, 0)} Hz · {_int(seg.size)} sampel</span>
      </div>
    </div>"""


# ── Komponen HTML ──────────────────────────────────────────────────────────

def _badge(label: str, tone: str) -> str:
    return f'<span class="bdg t-{tone}">{label}</span>'


def _row(icon: str, name: str, sub: str, value: str, unit: str,
         ref: str, status: tuple[str, str]) -> str:
    label, tone = status
    dim = ' class="dim"' if tone == "na" else ""
    return f"""<tr>
      <td class="p-name"><span class="p-ic">{_icon(icon)}</span>
        <span><b>{name}</b><em>{sub}</em></span></td>
      <td class="p-val"{dim}>{value}</td>
      <td class="p-unit">{unit}</td>
      <td class="p-ref">{ref}</td>
      <td class="p-st">{_badge(label, tone)}</td>
    </tr>"""


def _kv(label: str, value: str) -> str:
    return f'<div class="kv"><dt>{label}</dt><dd>{value}</dd></div>'


def _tile(icon: str, label: str, value: str, unit: str, foot: str, tone: str) -> str:
    return f"""<div class="tile t-{tone}">
      <div class="tile-h">{_icon(icon, 13)}<span>{label}</span></div>
      <div class="tile-v">{value}<small>{unit}</small></div>
      <div class="tile-f">{foot}</div>
    </div>"""


_CSS = """
:root{--brand:%(brand)s;--brand-d:%(brand_d)s;--ink:#16211f;--ink2:#4a5b58;
  --mut:#7b8b88;--line:#dbe5e3;--line2:#eef4f3;--bg:#fff;
  --ok:#0f7b5f;--ok-bg:#e6f5ef;--watch:#a45c07;--watch-bg:#fdf3e3;
  --high:#b02020;--high-bg:#fceceb;--crit:#8a1414;--crit-bg:#f8dedd;
  --low:#1d4ed8;--low-bg:#e8eeff;--na:#7b8b88;--na-bg:#f1f4f4;}

*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:#eef1f0;color:var(--ink);
  font-family:"Inter","Segoe UI",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
  font-size:10.2pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:210mm;min-height:297mm;margin:16px auto;padding:13mm 14mm 15mm;
  background:var(--bg);box-shadow:0 6px 28px rgba(0,0,0,.16)}
.ic{vertical-align:-2px;flex:none}

/* Kop surat */
.kop{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;
  padding-bottom:8px}
.kop-l img{height:9.5mm;width:auto;display:block}
.kop-l .sub{margin-top:6px;font-size:7.6pt;letter-spacing:.055em;text-transform:uppercase;
  color:var(--mut);font-weight:700;line-height:1.5}
.kop-r{text-align:right;padding-bottom:1px}
.kop-r h1{margin:0;font-size:15pt;font-weight:800;letter-spacing:-.02em;color:var(--brand-d);
  line-height:1.1}
.kop-r .h1s{font-size:8.2pt;color:var(--mut);letter-spacing:.05em;text-transform:uppercase;
  font-weight:650;margin-top:3px}
.kop-rule{height:3px;background:linear-gradient(90deg,var(--brand) 0 74%%,#c9a227 74%% 100%%);
  border-radius:2px}

/* Baris metadata dokumen */
.meta{display:flex;flex-wrap:wrap;gap:0;margin:9px 0 13px;border:1px solid var(--line);
  border-radius:5px;overflow:hidden;background:#fafcfb}
.meta div{flex:1 1 0;min-width:33mm;padding:6px 9px;border-right:1px solid var(--line)}
.meta div:last-child{border-right:0}
.meta dt{font-size:7.2pt;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);
  font-weight:700;margin:0}
.meta dd{margin:1px 0 0;font-size:9.2pt;font-weight:650;font-variant-numeric:tabular-nums}

/* Judul bagian */
h2{display:flex;align-items:center;gap:7px;margin:15px 0 7px;font-size:9.4pt;font-weight:800;
  text-transform:uppercase;letter-spacing:.08em;color:var(--brand-d)}
h2::after{content:"";flex:1;height:1px;background:var(--line)}
h2 .ic{color:var(--brand)}

/* Identitas subjek */
.ident{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--line);
  border-radius:5px;overflow:hidden}
.kv{padding:6.5px 10px;border-right:1px solid var(--line2);border-bottom:1px solid var(--line2)}
.ident .kv:nth-child(3n){border-right:0}
.ident .kv:nth-last-child(-n+3){border-bottom:0}
.kv dt{margin:0;font-size:7.3pt;text-transform:uppercase;letter-spacing:.055em;
  color:var(--mut);font-weight:700}
.kv dd{margin:1px 0 0;font-size:9.6pt;font-weight:620}

/* Kartu ringkas */
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:8px}
.tile{border:1px solid var(--line);border-left-width:3px;border-radius:5px;padding:7px 9px 8px;
  background:#fcfefd}
.tile-h{display:flex;align-items:center;gap:5px;font-size:7.4pt;font-weight:700;
  text-transform:uppercase;letter-spacing:.05em;color:var(--mut)}
.tile-v{font-size:17pt;font-weight:800;letter-spacing:-.025em;line-height:1.15;margin-top:2px;
  font-variant-numeric:tabular-nums}
.tile-v small{font-size:7.8pt;font-weight:650;color:var(--mut);margin-left:3px;letter-spacing:0}
.tile-f{font-size:7.5pt;font-weight:650;margin-top:1px}
.tile.t-ok{border-left-color:var(--ok)}   .tile.t-ok .tile-f{color:var(--ok)}
.tile.t-watch{border-left-color:var(--watch)} .tile.t-watch .tile-f{color:var(--watch)}
.tile.t-high{border-left-color:var(--high)}  .tile.t-high .tile-f{color:var(--high)}
.tile.t-crit{border-left-color:var(--crit)}  .tile.t-crit .tile-f{color:var(--crit)}
.tile.t-low{border-left-color:var(--low)}    .tile.t-low .tile-f{color:var(--low)}
.tile.t-na{border-left-color:var(--na)}      .tile.t-na .tile-f{color:var(--na)}
.tile.t-na .tile-v{color:var(--mut)}

/* Tabel hasil */
table{width:100%%;border-collapse:collapse}
thead th{background:#f2f7f6;color:var(--ink2);font-size:7.3pt;text-transform:uppercase;
  letter-spacing:.06em;font-weight:700;text-align:left;padding:6px 9px;
  border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
tbody td{padding:6.5px 9px;border-bottom:1px solid var(--line2);vertical-align:middle}
tbody tr:last-child td{border-bottom:1px solid var(--line)}
.p-name{width:38%%}
.p-name > span:last-child{display:inline-block;vertical-align:middle}
.p-name b{font-weight:670;font-size:9.7pt;display:block;line-height:1.25}
.p-name em{font-style:normal;font-size:7.6pt;color:var(--mut);display:block}
.p-ic{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;
  border-radius:5px;background:#e9f4f2;color:var(--brand);margin-right:8px;vertical-align:middle}
.p-val{font-size:11.6pt;font-weight:750;text-align:right;white-space:nowrap;
  font-variant-numeric:tabular-nums;width:15%%}
.p-val.dim{color:var(--mut);font-weight:600}
.p-unit{font-size:8pt;color:var(--mut);width:11%%;font-weight:600}
.p-ref{font-size:8.4pt;color:var(--ink2);width:17%%;font-variant-numeric:tabular-nums}
.p-st{width:19%%;text-align:right}

.bdg{display:inline-block;padding:2px 8px;border-radius:20px;font-size:7.7pt;font-weight:750;
  letter-spacing:.015em;white-space:nowrap}
.t-ok{background:var(--ok-bg);color:var(--ok)}
.t-watch{background:var(--watch-bg);color:var(--watch)}
.t-high{background:var(--high-bg);color:var(--high)}
.t-crit{background:var(--crit-bg);color:var(--crit)}
.t-low{background:var(--low-bg);color:var(--low)}
.t-na{background:var(--na-bg);color:var(--na)}

/* Grid teknis 2 kolom */
.tech{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);
  border-radius:5px;overflow:hidden}
.tech .kv:nth-child(4n){border-right:0}
.tech .kv:nth-last-child(-n+4){border-bottom:0}
.tech .kv dt{white-space:nowrap}
.tech .kv dd{font-size:9.1pt;font-variant-numeric:tabular-nums}

/* Strip gelombang */
.strip{margin-top:7px;border:1px solid var(--line);border-radius:5px;overflow:hidden}
.strip-svg{display:block;width:100%%;height:26mm}
.strip-cap{display:flex;justify-content:space-between;gap:10px;padding:4.5px 9px;
  background:#fafcfb;border-top:1px solid var(--line);font-size:7.5pt;color:var(--mut);
  font-weight:600}

/* Interpretasi */
.interp{border:1px solid var(--line);border-left:3px solid var(--brand);border-radius:5px;
  padding:9px 12px;background:#fbfdfc}
.interp ul{margin:0;padding-left:15px}
.interp li{margin:0 0 4px;font-size:9.2pt;line-height:1.55}
.interp li:last-child{margin-bottom:0}
.interp b{font-weight:700}

/* Faktor risiko */
.risk{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 9px}
.rk{display:flex;align-items:flex-start;gap:7px;padding:6px 9px;border:1px solid var(--line);
  border-radius:5px;font-size:8.7pt;line-height:1.4;background:#fcfefd}
.rk .ic{margin-top:1.5px}
.rk.on{border-color:#f0cfcc;background:#fdf6f5}
.rk.on .ic{color:var(--high)}
.rk.off .ic{color:var(--ok)}
.rk b{display:block;font-weight:700}
.rk span{color:var(--mut);font-size:7.9pt}

/* Tanda tangan + catatan kaki */
.sign{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-top:16px}
.note{flex:1;font-size:7.7pt;color:var(--mut);line-height:1.55;border-top:1px solid var(--line);
  padding-top:7px}
.note b{color:var(--ink2)}
.ttd{width:58mm;text-align:center;font-size:8.2pt;border-top:1px solid var(--line);padding-top:7px}
.ttd .sp{height:15mm}
.ttd .nm{font-weight:700;border-top:1px solid var(--ink2);padding-top:3px;display:block}
.ttd .rl{color:var(--mut);font-size:7.6pt}

.foot{margin-top:11px;padding-top:6px;border-top:1px solid var(--line);display:flex;
  justify-content:space-between;gap:12px;font-size:7.3pt;color:var(--mut);font-weight:600;
  letter-spacing:.02em}

/* Bilah aksi — tidak ikut tercetak */
.bar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  justify-content:center;padding:10px;background:#16211f;color:#e7efee;font-size:9pt}
.bar button{font:inherit;font-weight:700;padding:7px 16px;border:0;border-radius:6px;
  background:var(--brand);color:#fff;cursor:pointer}
.bar button:hover{background:var(--brand-d)}
.bar span{color:#9db3af}

@media print{
  body{background:#fff}
  .bar{display:none}
  .sheet{width:auto;min-height:0;margin:0;padding:0;box-shadow:none}
  h2,table,.tiles,.ident,.tech,.strip,.interp,.risk,.sign{break-inside:avoid;
    page-break-inside:avoid}
  tr{break-inside:avoid;page-break-inside:avoid}
  h2{break-after:avoid;page-break-after:avoid}
}
/* Kaki halaman berulang sengaja tidak dipakai: position:fixed di Chrome
   terlempar ke atas halaman berikutnya dan menimpa isi laporan. */
@page{size:A4 portrait;margin:12mm 13mm 13mm}
""" % {"brand": BRAND, "brand_d": BRAND_DARK}


# ── Penyusun laporan ───────────────────────────────────────────────────────

def build_record_report_html(rec, autoprint: bool = True) -> str:
    """Rakit laporan pemeriksaan A4 untuk satu rekaman kalibrasi."""
    gender = (rec.gender or "L").strip().upper()
    gender_txt = "Laki-laki" if gender == "L" else "Perempuan"
    kondisi_txt = _KONDISI_LABEL.get((rec.kondisi or "sewaktu").lower(), "Sewaktu (Acak)")

    sesi = (rec.created_at or datetime.utcnow()).replace(tzinfo=timezone.utc).astimezone(_WIB)
    terbit = datetime.now(_WIB)

    no_doc = f"ANT/CAL/{sesi.year}/{rec.id:05d}"
    # Kode verifikasi: sidik jari isi laporan, supaya salinan cetak bisa
    # dicocokkan dengan baris database aslinya.
    kode = hashlib.sha1(
        f"{rec.id}|{rec.device_id}|{rec.subject_id}|{rec.created_at}|"
        f"{rec.sistolik_mmhg}|{rec.diastolik_mmhg}|{rec.gula_darah_mg_dl}|"
        f"{rec.kolesterol_mg_dl}|{rec.asam_urat_mg_dl}|{rec.bpm}".encode()
    ).hexdigest()[:10].upper()

    sis, dia, bpm = rec.sistolik_mmhg, rec.diastolik_mmhg, rec.bpm
    gula, kol, au = rec.gula_darah_mg_dl, rec.kolesterol_mg_dl, rec.asam_urat_mg_dl

    st_bp = _classify_bp(sis, dia)
    st_bpm = _classify_bpm(bpm)
    st_gula = _classify_glucose(gula, rec.kondisi)
    st_kol = _classify_chol(kol)
    st_au = _classify_uric(au, gender)

    # Rasio-of-ratios merah/inframerah — indeks teknis mutu sinyal dua kanal,
    # bukan nilai SpO2 (sensor belum dikalibrasi terhadap ko-oksimeter).
    ratio_r = None
    if all(v for v in (rec.red_ac_p2p, rec.red_dc_mean, rec.ir_ac_p2p, rec.ir_dc_mean)):
        den = rec.ir_ac_p2p / rec.ir_dc_mean
        if den > 0:
            ratio_r = (rec.red_ac_p2p / rec.red_dc_mean) / den

    ir = _parse_raw(rec.infrared_raw)
    fs = float(rec.fs_hz or 100.0)
    durasi = ir.size / fs if ir.size else None

    # ── Kartu ringkas ────────────────────────────────────────────────────
    bp_val = f"{_int(sis)}/{_int(dia)}" if sis is not None and dia is not None else "—"
    tiles = "".join([
        _tile("gauge", "Tekanan Darah", bp_val, "mmHg", st_bp[0], st_bp[1]),
        _tile("heart", "Denyut Jantung", _num(bpm, 0), "bpm", st_bpm[0], st_bpm[1]),
        _tile("droplet", "Gula Darah", _num(gula, 0), "mg/dL", st_gula[0], st_gula[1]),
        _tile("molecule", "Asam Urat", _num(au, 1), "mg/dL", st_au[0], st_au[1]),
    ])

    # ── Tabel hasil ──────────────────────────────────────────────────────
    rows = "".join([
        _row("gauge", "Tekanan Darah Sistolik", "Sfigmomanometer digital",
             _num(sis, 0), "mmHg", "< 120", st_bp),
        _row("gauge", "Tekanan Darah Diastolik", "Sfigmomanometer digital",
             _num(dia, 0), "mmHg", "< 80", st_bp),
        _row("heart", "Denyut Jantung (HR)", "Fotopletismografi inframerah",
             _num(bpm, 0), "bpm", "60 – 100", st_bpm),
        _row("droplet", "Gula Darah", f"Glukometer · {kondisi_txt}",
             _num(gula, 0), "mg/dL", _glucose_ref(rec.kondisi), st_gula),
        _row("flask", "Kolesterol Total", "Strip enzimatik POCT",
             _num(kol, 0), "mg/dL", "< 200", st_kol),
        _row("molecule", "Asam Urat", "Strip enzimatik POCT",
             _num(au, 1), "mg/dL", _uric_ref(gender), st_au),
    ])

    # ── Faktor risiko stroke yang dapat dimodifikasi ─────────────────────
    usia = float(rec.age_years or 0)
    faktor = [
        ("Hipertensi", "Sistolik ≥ 140 atau diastolik ≥ 90 mmHg",
         (sis is not None and sis >= 140) or (dia is not None and dia >= 90)),
        ("Hiperglikemia", "Melampaui ambang normal sesuai kondisi pengambilan",
         st_gula[1] in ("watch", "crit")),
        ("Dislipidemia", "Kolesterol total ≥ 200 mg/dL",
         kol is not None and kol >= 200),
        ("Hiperurisemia", f"Di atas rujukan {'pria' if gender == 'L' else 'wanita'}",
         st_au[1] == "high"),
        ("Aritmia / laju tidak normal", "Denyut di luar rentang 60–100 bpm",
         st_bpm[1] in ("watch", "high")),
    ]
    risk_html = "".join(
        f'<div class="rk {"on" if on else "off"}">{_icon("alert" if on else "check", 13)}'
        f'<div><b>{nm}</b><span>{desc}</span></div></div>'
        for nm, desc, on in faktor
    )

    # ── Interpretasi naratif ─────────────────────────────────────────────
    poin: list[str] = []
    if sis is not None and dia is not None:
        poin.append(
            f"Tekanan darah tercatat <b>{_int(sis)}/{_int(dia)} mmHg</b> — "
            f"masuk kategori <b>{st_bp[0]}</b>."
        )
    if bpm is not None:
        poin.append(
            f"Laju denyut dari sinyal PPG <b>{_num(bpm, 0)} bpm</b> "
            f"(<b>{st_bpm[0]}</b>), diambil dengan autokorelasi pada kanal inframerah."
        )
    if gula is not None:
        poin.append(
            f"Gula darah <b>{_num(gula, 0)} mg/dL</b> pada kondisi "
            f"<b>{kondisi_txt.lower()}</b> — interpretasi <b>{st_gula[0]}</b> "
            f"(rujukan {_glucose_ref(rec.kondisi)} mg/dL)."
        )
    if kol is not None:
        poin.append(f"Kolesterol total <b>{_num(kol, 0)} mg/dL</b> — <b>{st_kol[0]}</b>.")
    if au is not None:
        poin.append(f"Asam urat <b>{_num(au, 1)} mg/dL</b> — <b>{st_au[0]}</b>.")
    if durasi:
        poin.append(
            f"Sinyal PPG pendamping direkam <b>{_num(durasi, 1)} detik</b> "
            f"pada laju cuplik {_num(fs, 0)} Hz."
        )
    if not poin:
        # Semua nilai rujukan kosong — jangan cetak kotak interpretasi melompong.
        poin.append(
            "Tidak ada nilai alat rujukan yang terisi pada sesi ini. Laporan hanya "
            "memuat identitas subjek dan parameter teknis sensor."
        )
    interp = "".join(f"<li>{p}</li>" for p in poin)

    # ── Panel teknis sensor ──────────────────────────────────────────────
    tech = "".join([
        _kv("IR — DC", _int(rec.ir_dc_mean)),
        _kv("IR — AC p-p", _int(rec.ir_ac_p2p)),
        _kv("Merah — DC", _int(rec.red_dc_mean)),
        _kv("Merah — AC p-p", _int(rec.red_ac_p2p)),
        _kv("Rasio R (merah/IR)", _num(ratio_r, 3)),
        _kv("Laju Cuplik", f"{_num(fs, 0)} Hz"),
        # Dipecah jadi dua sel supaya grid tetap genap 4 kolom — aturan border
        # .tech mengandalkan jumlah sel kelipatan empat.
        _kv("Durasi Rekaman", f"{_num(durasi, 1)} dtk" if durasi else "—"),
        _kv("Jumlah Sampel", _int(ir.size) if ir.size else "—"),
    ])

    strip = _ppg_strip_svg(ir, fs)
    strip_block = (f'<h2>{_icon("wave")}Rekaman Gelombang Denyut (PPG)</h2>{strip}'
                   if strip else "")

    ident = "".join([
        _kv("ID Subjek", rec.subject_id or "—"),
        _kv("Usia", f"{_num(usia, 0)} tahun"),
        _kv("Jenis Kelamin", gender_txt),
        _kv("Kondisi Pengambilan", kondisi_txt),
        _kv("Perangkat", rec.device_id or "—"),
        _kv("Waktu Sesi", sesi.strftime("%d/%m/%Y · %H:%M WIB")),
    ])

    fname = f"Laporan-Antaraga-{(rec.subject_id or 'subjek')}-{sesi.strftime('%Y%m%d-%H%M')}"
    autoprint_js = (
        "window.addEventListener('load', () => setTimeout(() => window.print(), 350));"
        if autoprint else ""
    )
    logo = _logo_data_uri()
    logo_html = (f'<img src="{logo}" alt="antaraga">' if logo
                 else f'<div style="font-size:20pt;font-weight:800;color:{BRAND}">antaraga</div>')

    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{fname}</title>
<style>{_CSS}</style>
</head>
<body>

<div class="bar">
  <button onclick="window.print()">Cetak / Simpan sebagai PDF</button>
  <span>Pada dialog cetak pilih <b>Save as PDF</b> · ukuran <b>A4</b> · aktifkan
        <b>Background graphics</b> agar warna ikut tercetak.</span>
</div>

<div class="sheet">

  <div class="kop">
    <div class="kop-l">
      {logo_html}
      <div class="sub">Health Analytics Laboratory<br>Smartband Deteksi Risiko Stroke Berbasis AI</div>
    </div>
    <div class="kop-r">
      <h1>LAPORAN HASIL PEMERIKSAAN</h1>
      <div class="h1s">Sesi Kalibrasi Sensor &amp; Parameter Vital</div>
    </div>
  </div>
  <div class="kop-rule"></div>

  <dl class="meta">
    <div><dt>No. Laporan</dt><dd>{no_doc}</dd></div>
    <div><dt>Tanggal Terbit</dt><dd>{_tgl_panjang(terbit)}</dd></div>
    <div><dt>Metode</dt><dd>PPG 3-Kanal &amp; Alat Rujukan</dd></div>
    <div><dt>Kode Verifikasi</dt><dd>{kode}</dd></div>
  </dl>

  <h2>{_icon("user")}Data Subjek</h2>
  <dl class="ident">{ident}</dl>

  <h2>{_icon("doc")}Ringkasan Tanda Vital</h2>
  <div class="tiles">{tiles}</div>

  <h2>{_icon("flask")}Hasil Pemeriksaan Laboratorium &amp; Vital</h2>
  <table>
    <thead><tr>
      <th>Parameter Pemeriksaan</th>
      <th style="text-align:right">Hasil</th>
      <th>Satuan</th>
      <th>Nilai Rujukan</th>
      <th style="text-align:right">Interpretasi</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>

  {strip_block}

  <h2>{_icon("chip")}Parameter Teknis Sensor</h2>
  <dl class="tech">{tech}</dl>

  <h2>{_icon("doc")}Interpretasi Hasil</h2>
  <div class="interp"><ul>{interp}</ul></div>

  <h2>{_icon("shield")}Faktor Risiko Stroke</h2>
  <div class="risk">{risk_html}</div>

  <div class="sign">
    <div class="note">
      <b>Catatan:</b> Nilai gula darah, kolesterol, asam urat, dan tekanan darah pada laporan ini
      berasal dari alat ukur rujukan (invasif/standar medis) yang direkam berdampingan dengan
      sinyal PPG sebagai data kalibrasi model. Nilai rujukan mengacu pada pedoman PERKENI, PERHI,
      dan NCEP ATP III. Laporan ini merupakan dokumen hasil pengukuran penelitian dan
      <b>bukan pengganti diagnosis dokter</b>. Interpretasi akhir tetap memerlukan penilaian
      tenaga medis berwenang beserta riwayat klinis subjek.
    </div>
    <div class="ttd">
      <div>Bandung, {_tgl_panjang(terbit)}</div>
      <div class="sp"></div>
      <span class="nm">Penanggung Jawab Pengukuran</span>
      <span class="rl">Tim Riset ANTARAGA · PKM-KC 2026</span>
    </div>
  </div>

  <div class="foot">
    <span>ANTARAGA HEALTH ANALYTICS · {no_doc}</span>
    <span>Rekaman #{rec.id} · Verifikasi {kode}</span>
    <span>Dicetak {terbit.strftime('%d/%m/%Y %H:%M')} WIB</span>
  </div>

</div>

<script>{autoprint_js}</script>
</body>
</html>"""
