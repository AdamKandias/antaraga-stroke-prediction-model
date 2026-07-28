import os
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from api.config import DEVICE_INGEST_KEY

router = APIRouter(tags=["ota"])

_OTA_DIR = Path(os.getenv("OTA_BIN_DIR", str(Path(__file__).parent / "ota_bins")))
_OTA_DIR.mkdir(parents=True, exist_ok=True)


def _verify_device_key(authorization: str) -> None:
    if authorization != f"Bearer {DEVICE_INGEST_KEY}":
        raise HTTPException(status_code=403, detail="Invalid device key")


@router.get("/v1/ota/check")
def ota_check(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware: cek apakah ada firmware baru yang menunggu untuk diinstall."""
    _verify_device_key(authorization)
    pending = (_OTA_DIR / f"{device_id}.bin").exists()
    return {"pending": pending, "device_id": device_id}


@router.post("/v1/ota/upload")
async def ota_upload(
    device_id: str = Query(...),
    file: UploadFile = ...,
) -> dict:
    """Dipanggil dashboard: upload file .bin hasil build PlatformIO.
    Setelah upload, firmware di perangkat akan diganti dalam ~OTA_CHECK_INTERVAL_MS detik."""
    if not file.filename or not file.filename.endswith(".bin"):
        raise HTTPException(status_code=400, detail="File harus berekstensi .bin")
    content = await file.read()
    if len(content) < 4096:
        raise HTTPException(status_code=400, detail="File terlalu kecil — bukan firmware valid")
    bin_path = _OTA_DIR / f"{device_id}.bin"
    # Hapus .done lama kalau ada
    done_path = _OTA_DIR / f"{device_id}.bin.done"
    if done_path.exists():
        done_path.unlink()
    bin_path.write_bytes(content)
    return {"ok": True, "device_id": device_id, "size": len(content)}


@router.get("/v1/ota/firmware")
def ota_firmware(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> FileResponse:
    """Dipanggil firmware: download binary untuk diflash."""
    _verify_device_key(authorization)
    bin_path = _OTA_DIR / f"{device_id}.bin"
    if not bin_path.exists():
        raise HTTPException(status_code=404, detail="Tidak ada firmware pending untuk device ini")
    return FileResponse(
        bin_path,
        media_type="application/octet-stream",
        filename=f"firmware_{device_id}.bin",
    )


@router.post("/v1/ota/ack")
def ota_ack(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware setelah flash berhasil — hapus .bin supaya tidak di-flash ulang."""
    _verify_device_key(authorization)
    bin_path = _OTA_DIR / f"{device_id}.bin"
    if bin_path.exists():
        bin_path.rename(bin_path.with_suffix(".bin.done"))
    return {"ok": True}


@router.get("/v1/ota/status")
def ota_status(device_id: str = Query(...)) -> dict:
    """Dipanggil dashboard: cek status OTA untuk device tertentu."""
    bin_path = _OTA_DIR / f"{device_id}.bin"
    done_path = _OTA_DIR / f"{device_id}.bin.done"
    pending = bin_path.exists()
    done = done_path.exists()
    return {
        "device_id": device_id,
        "pending": pending,
        "done": done,
        "bin_size": bin_path.stat().st_size if pending else (done_path.stat().st_size if done else 0),
    }
