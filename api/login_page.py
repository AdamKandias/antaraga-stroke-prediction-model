"""Halaman login dashboard — dirakit di Python supaya logo bisa ditanam
sebagai data URI (server ini tidak memasang StaticFiles untuk folder assets).
"""
from __future__ import annotations

from api.calib_report import BRAND, BRAND_DARK, _logo_data_uri


def render_login(error: str = "", next_path: str = "/dashboard") -> str:
    logo = _logo_data_uri()
    logo_html = (f'<img src="{logo}" alt="antaraga">' if logo
                 else f'<div class="wordmark">antaraga</div>')
    err_html = (f'<div class="err" role="alert">{error}</div>' if error else "")
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Masuk · ANTARAGA</title>
<style>
  :root{{--brand:{BRAND};--brand-d:{BRAND_DARK};--ink:#16211f;--mut:#7b8b88;
    --line:#dbe5e3;--bg:#eef1f0;--card:#fff;--err:#b02020;--err-bg:#fceceb}}
  *{{box-sizing:border-box}}
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    padding:24px;background:var(--bg);color:var(--ink);
    font-family:"Inter","Segoe UI",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
    font-size:14px;line-height:1.5}}
  .card{{width:100%;max-width:376px;background:var(--card);border:1px solid var(--line);
    border-radius:12px;padding:32px 30px 28px;box-shadow:0 8px 30px rgba(0,0,0,.08)}}
  .card::before{{content:"";display:block;height:3px;border-radius:2px;margin:-32px -30px 24px;
    background:linear-gradient(90deg,var(--brand) 0 74%,#c9a227 74% 100%);
    border-radius:12px 12px 0 0}}
  img{{height:26px;width:auto;display:block}}
  .wordmark{{font-size:22px;font-weight:800;color:var(--brand)}}
  .sub{{margin:9px 0 22px;font-size:10px;font-weight:700;letter-spacing:.08em;
    text-transform:uppercase;color:var(--mut);line-height:1.6}}
  label{{display:block;font-size:11px;font-weight:700;letter-spacing:.05em;
    text-transform:uppercase;color:var(--mut);margin-bottom:5px}}
  input{{width:100%;font:inherit;padding:9px 11px;border:1px solid var(--line);
    border-radius:7px;background:#fbfcfc;color:var(--ink);margin-bottom:14px}}
  input:focus{{outline:none;border-color:var(--brand);background:#fff;
    box-shadow:0 0 0 3px rgba(0,126,115,.13)}}
  button{{width:100%;font:inherit;font-weight:700;padding:10px;border:0;border-radius:7px;
    background:var(--brand);color:#fff;cursor:pointer;margin-top:4px}}
  button:hover{{background:var(--brand-d)}}
  .err{{background:var(--err-bg);color:var(--err);border-radius:7px;padding:9px 11px;
    font-size:12.5px;font-weight:600;margin-bottom:16px}}
  .foot{{margin-top:20px;padding-top:14px;border-top:1px solid var(--line);
    font-size:10.5px;color:var(--mut);text-align:center;letter-spacing:.02em}}
  @media (prefers-color-scheme:dark){{
    :root{{--ink:#e7efee;--mut:#8fa3a0;--line:#2a3937;--bg:#0f1817;--card:#16211f;
      --err:#ff9c96;--err-bg:#3a1f1e}}
    input{{background:#0f1817}} input:focus{{background:#0f1817}}
    /* Wordmark-nya teal pekat — nyaris hilang di atas kartu gelap. */
    img{{filter:brightness(1.6) saturate(.95)}}
    .wordmark{{color:#19b3a3}}
    button{{background:#00998a}} button:hover{{background:#00b3a1}}
  }}
</style>
</head>
<body>
  <form class="card" method="post" action="/login">
    {logo_html}
    <div class="sub">Health Analytics Laboratory<br>Dashboard Monitoring Perangkat</div>
    {err_html}
    <input type="hidden" name="next_path" value="{next_path}">
    <label for="email">Email</label>
    <input id="email" name="email" type="email" autocomplete="username" required autofocus>
    <label for="password">Kata Sandi</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Masuk</button>
    <div class="foot">Akses terbatas tim riset ANTARAGA · PKM-KC 2026</div>
  </form>
</body>
</html>"""
