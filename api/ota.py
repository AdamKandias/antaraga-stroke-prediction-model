"""
OTA — manajemen firmware Over-The-Air untuk ANTARAGA smartband.

Alur:
  Dashboard                        Server                    ESP32
  ─────────────────────────────    ──────────────────────    ──────────────
  Upload .bin  ──POST /v1/ota/bins──▶ simpan meta + file
  Pilih deploy ─POST /v1/ota/deploy─▶ tandai pending
                                                     ─── GET /v1/ota/check ──▶
                                                     ◀── {pending:true}  ──────
                                                     ─── GET /v1/ota/firmware ──▶
                                                     ◀── binary stream  ────────
                                                     (flash)
                                                     ─── POST /v1/ota/ack ──────▶
                                    tandai installed ◀──────────────────────────
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from api.config import DEVICE_INGEST_KEY

router = APIRouter(tags=["ota"])

_OTA_DIR = Path(os.getenv("OTA_BIN_DIR", str(Path(__file__).parent / "ota_bins")))
_OTA_DIR.mkdir(parents=True, exist_ok=True)

_META_FILE = _OTA_DIR / "_meta.json"
_STATE_FILE = _OTA_DIR / "_state.json"  # {device_id: {pending_fw_id, installed_fw_id}}


# ── persistence helpers ────────────────────────────────────────────────

def _load_meta() -> dict:
    try:
        return json.loads(_META_FILE.read_text()) if _META_FILE.exists() else {}
    except Exception:
        return {}


def _save_meta(m: dict) -> None:
    _META_FILE.write_text(json.dumps(m, indent=2, ensure_ascii=False))


def _load_state() -> dict:
    try:
        return json.loads(_STATE_FILE.read_text()) if _STATE_FILE.exists() else {}
    except Exception:
        return {}


def _save_state(s: dict) -> None:
    _STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))


def _verify_key(authorization: str) -> None:
    if authorization != f"Bearer {DEVICE_INGEST_KEY}":
        raise HTTPException(status_code=403, detail="Invalid device key")


# ── firmware library (dashboard) ───────────────────────────────────────

@router.get("/v1/ota/bins")
def list_firmware() -> list:
    """Daftar semua firmware yang diupload, beserta status deploy per device."""
    meta = _load_meta()
    state = _load_state()

    result = []
    for fw_id, fw in sorted(meta.items(), key=lambda x: x[1]["uploaded_at"], reverse=True):
        pending_devs = [d for d, ds in state.items() if ds.get("pending") == fw_id]
        installed_devs = [d for d, ds in state.items() if ds.get("installed") == fw_id]
        result.append({
            **fw,
            "id": fw_id,
            "bin_exists": (_OTA_DIR / f"{fw_id}.bin").exists(),
            "devices_pending": pending_devs,
            "devices_installed": installed_devs,
        })
    return result


@router.post("/v1/ota/bins")
async def upload_firmware(
    name: str = Query(default=""),
    description: str = Query(default=""),
    file: UploadFile = ...,
) -> dict:
    """Upload file .bin hasil pio run. Belum langsung di-deploy — pilih dulu device-nya."""
    if not (file.filename or "").endswith(".bin"):
        raise HTTPException(400, "File harus berekstensi .bin")
    content = await file.read()
    if len(content) < 4096:
        raise HTTPException(400, "File terlalu kecil — bukan firmware valid")

    fw_id = uuid.uuid4().hex[:12]
    (_OTA_DIR / f"{fw_id}.bin").write_bytes(content)

    meta = _load_meta()
    meta[fw_id] = {
        "name": name.strip() or file.filename or fw_id,
        "description": description.strip(),
        "original_filename": file.filename or "",
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest()[:16],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_meta(meta)
    return {"ok": True, "id": fw_id, **meta[fw_id]}


@router.patch("/v1/ota/bins/{fw_id}")
def update_firmware(
    fw_id: str,
    name: str = Query(default=None),
    description: str = Query(default=None),
) -> dict:
    meta = _load_meta()
    if fw_id not in meta:
        raise HTTPException(404, "Firmware tidak ditemukan")
    if name is not None:
        meta[fw_id]["name"] = name.strip()
    if description is not None:
        meta[fw_id]["description"] = description.strip()
    _save_meta(meta)
    return {"ok": True, **meta[fw_id]}


@router.delete("/v1/ota/bins/{fw_id}")
def delete_firmware(fw_id: str) -> dict:
    meta = _load_meta()
    if fw_id not in meta:
        raise HTTPException(404, "Firmware tidak ditemukan")
    state = _load_state()
    pending_devs = [d for d, ds in state.items() if ds.get("pending") == fw_id]
    if pending_devs:
        raise HTTPException(400, f"Batalkan deploy dulu untuk: {', '.join(pending_devs)}")
    bin_path = _OTA_DIR / f"{fw_id}.bin"
    if bin_path.exists():
        bin_path.unlink()
    del meta[fw_id]
    _save_meta(meta)
    return {"ok": True}


# ── deploy management (dashboard) ─────────────────────────────────────

@router.post("/v1/ota/deploy")
def deploy_firmware(
    firmware_id: str = Query(...),
    device_id: str = Query(...),
) -> dict:
    """Tandai firmware_id sebagai pending untuk device_id — device akan download saat cek berikutnya."""
    meta = _load_meta()
    if firmware_id not in meta:
        raise HTTPException(404, "Firmware tidak ditemukan")
    if not (_OTA_DIR / f"{firmware_id}.bin").exists():
        raise HTTPException(404, "File .bin tidak ada")
    state = _load_state()
    state.setdefault(device_id, {})["pending"] = firmware_id
    _save_state(state)
    return {"ok": True, "device_id": device_id, "firmware_id": firmware_id}


@router.delete("/v1/ota/deploy")
def cancel_deploy(device_id: str = Query(...)) -> dict:
    """Batalkan pending deploy untuk device."""
    state = _load_state()
    if device_id in state:
        state[device_id].pop("pending", None)
        _save_state(state)
    return {"ok": True}


@router.get("/v1/ota/device-status")
def device_ota_status(device_id: str = Query(...)) -> dict:
    """Status OTA terkini untuk satu device (pending + installed)."""
    state = _load_state()
    meta = _load_meta()
    ds = state.get(device_id, {})

    def _fw(fw_id):
        if not fw_id:
            return None
        fw = meta.get(fw_id)
        return {"id": fw_id, **fw} if fw else {"id": fw_id}

    return {
        "device_id": device_id,
        "pending": _fw(ds.get("pending")),
        "installed": _fw(ds.get("installed")),
    }


# ── firmware-facing endpoints (auth: device key) ───────────────────────

@router.get("/v1/ota/check")
def ota_check(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware setiap OTA_CHECK_INTERVAL_MS: ada update yang menunggu?"""
    _verify_key(authorization)
    state = _load_state()
    fw_id = state.get(device_id, {}).get("pending")
    if fw_id and not (_OTA_DIR / f"{fw_id}.bin").exists():
        # File hilang — bersihkan state
        state[device_id].pop("pending", None)
        _save_state(state)
        fw_id = None
    return {"pending": fw_id is not None}


@router.get("/v1/ota/firmware")
def ota_firmware_download(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> FileResponse:
    """Dipanggil firmware: download binary untuk diflash."""
    _verify_key(authorization)
    state = _load_state()
    fw_id = state.get(device_id, {}).get("pending")
    if not fw_id:
        raise HTTPException(404, "Tidak ada firmware pending untuk device ini")
    bin_path = _OTA_DIR / f"{fw_id}.bin"
    if not bin_path.exists():
        raise HTTPException(404, "File .bin tidak ada")
    meta = _load_meta()
    name = meta.get(fw_id, {}).get("name", fw_id)
    return FileResponse(bin_path, media_type="application/octet-stream",
                        filename=f"firmware_{fw_id}.bin",
                        headers={"X-Firmware-Name": name})


@router.post("/v1/ota/ack")
def ota_ack(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware setelah flash berhasil: tandai installed, clear pending."""
    _verify_key(authorization)
    state = _load_state()
    ds = state.setdefault(device_id, {})
    fw_id = ds.pop("pending", None)
    if fw_id:
        ds["installed"] = fw_id
    _save_state(state)
    return {"ok": True, "installed_firmware_id": fw_id}
