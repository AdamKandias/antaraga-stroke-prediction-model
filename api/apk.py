"""Distribusi berkas APK aplikasi mobile ANTARAGA.

Tombol unduh di halaman utama menunjuk ke `/download/app.apk`, yang selalu
mengalirkan APK versi terbaru yang diunggah lewat dashboard.  Tidak ada nomor
versi di dalam URL supaya tautan yang sudah tersebar tidak pernah basi.

Berkas disimpan di direktori yang dipasang sebagai Docker volume, jadi APK
bertahan melewati pembaruan container -- sama seperti firmware OTA.

Tautan App Store dan Play Store juga diatur dari sini.  Selama masih kosong,
halaman utama menampilkan pesan "segera hadir" alih-alih tautan mati.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(tags=["apk"])

_APK_DIR = Path(os.getenv("APK_DIR", str(Path(__file__).parent / "apk_files")))
_APK_DIR.mkdir(parents=True, exist_ok=True)
_META_PATH = _APK_DIR / "meta.json"

# 300 MB -- APK Flutter rilis biasanya 20-60 MB, batas ini memberi ruang lega
# tanpa membiarkan unggahan yang jelas keliru menghabiskan disk.
_MAX_BYTES = 300 * 1024 * 1024


def _load_meta() -> dict:
    if not _META_PATH.exists():
        return {"builds": [], "store_links": {"app_store": "", "play_store": ""}}
    try:
        data = json.loads(_META_PATH.read_text())
    except Exception:
        return {"builds": [], "store_links": {"app_store": "", "play_store": ""}}
    data.setdefault("builds", [])
    data.setdefault("store_links", {"app_store": "", "play_store": ""})
    return data


def _save_meta(meta: dict) -> None:
    _META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False))


def _latest(meta: dict) -> dict | None:
    builds = meta.get("builds", [])
    return builds[0] if builds else None


# ── Unggah & kelola (dipakai dashboard) ───────────────────────────────────

@router.post("/v1/apk/upload")
async def upload_apk(
    version: str = Query("", description="Versi rilis, mis. 1.0.0"),
    catatan: str = Query("", description="Catatan perubahan"),
    file: UploadFile = ...,
) -> dict:
    """Unggah APK baru.  Yang terbaru otomatis menjadi berkas yang diunduh publik."""
    nama = file.filename or ""
    if not nama.lower().endswith(".apk"):
        raise HTTPException(400, "Berkas harus berekstensi .apk")

    apk_id = uuid.uuid4().hex[:12]
    dest = _APK_DIR / f"{apk_id}.apk"

    ukuran = 0
    try:
        with dest.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                ukuran += len(chunk)
                if ukuran > _MAX_BYTES:
                    out.close()
                    dest.unlink(missing_ok=True)
                    raise HTTPException(
                        413, f"Berkas melebihi batas {_MAX_BYTES // (1024*1024)} MB"
                    )
                out.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(500, f"Gagal menyimpan berkas: {exc}") from exc

    if ukuran == 0:
        dest.unlink(missing_ok=True)
        raise HTTPException(400, "Berkas kosong")

    meta = _load_meta()
    meta["builds"].insert(0, {
        "id": apk_id,
        "nama_asli": nama,
        "version": version.strip(),
        "catatan": catatan.strip(),
        "ukuran": ukuran,
        "diunggah": time.time(),
    })
    _save_meta(meta)

    return {"ok": True, "id": apk_id, "ukuran": ukuran,
            "total_versi": len(meta["builds"]),
            "message": f"APK {version or nama} berhasil diunggah"}


@router.get("/v1/apk/list")
def list_apk() -> dict:
    meta = _load_meta()
    for b in meta["builds"]:
        b["ada_berkas"] = (_APK_DIR / f"{b['id']}.apk").exists()
    return meta


@router.delete("/v1/apk/{apk_id}")
def delete_apk(apk_id: str) -> dict:
    meta = _load_meta()
    sisa = [b for b in meta["builds"] if b["id"] != apk_id]
    if len(sisa) == len(meta["builds"]):
        raise HTTPException(404, "APK tidak ditemukan")
    (_APK_DIR / f"{apk_id}.apk").unlink(missing_ok=True)
    meta["builds"] = sisa
    _save_meta(meta)
    return {"ok": True, "sisa": len(sisa)}


@router.put("/v1/apk/store-links")
def set_store_links(
    app_store: str = Query("", description="URL App Store; kosongkan bila belum terbit"),
    play_store: str = Query("", description="URL Play Store; kosongkan bila belum terbit"),
) -> dict:
    meta = _load_meta()
    meta["store_links"] = {
        "app_store": app_store.strip(),
        "play_store": play_store.strip(),
    }
    _save_meta(meta)
    return {"ok": True, "store_links": meta["store_links"]}


# ── Dibaca halaman utama ──────────────────────────────────────────────────

@router.get("/v1/apk/latest")
def latest_apk() -> dict:
    """Status rilis untuk halaman utama: apakah APK tersedia dan ke mana tombol menuju."""
    meta = _load_meta()
    b = _latest(meta)
    tersedia = bool(b) and (_APK_DIR / f"{b['id']}.apk").exists()
    return {
        "tersedia": tersedia,
        "version": (b or {}).get("version", ""),
        "ukuran": (b or {}).get("ukuran", 0),
        "catatan": (b or {}).get("catatan", ""),
        "diunggah": (b or {}).get("diunggah", 0),
        "url": "/download/app.apk" if tersedia else "",
        "store_links": meta.get("store_links", {}),
    }


@router.get("/download/app.apk", include_in_schema=False)
def download_apk() -> FileResponse:
    """Tautan unduh publik.  URL-nya tetap, isinya selalu versi terbaru."""
    meta = _load_meta()
    b = _latest(meta)
    if not b:
        return JSONResponse(
            status_code=404,
            content={"detail": "APK belum tersedia. Unggah lebih dulu lewat dashboard."},
        )
    path = _APK_DIR / f"{b['id']}.apk"
    if not path.exists():
        return JSONResponse(
            status_code=404,
            content={"detail": "Berkas APK hilang dari penyimpanan."},
        )

    versi = b.get("version") or "terbaru"
    return FileResponse(
        path,
        media_type="application/vnd.android.package-archive",
        filename=f"antaraga-{versi}.apk",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )
