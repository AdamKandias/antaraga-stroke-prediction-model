import asyncio
import os
import re
import subprocess
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/firmware", tags=["firmware"])

FIRMWARE_PATH = Path(
    os.getenv("FIRMWARE_PATH", str(Path(__file__).parent.parent / "Firmware"))
)
CONFIG_H = FIRMWARE_PATH / "include" / "config.h"

CONFIG_GROUPS: dict[str, list[str]] = {
    "WiFi": ["WIFI_SSID", "WIFI_PASS", "WIFI_CONNECT_TIMEOUT_MS", "WIFI_RETRY_DELAY_MS"],
    "Cloud": [
        "DEVICE_ID", "CLOUD_HOST", "CLOUD_PORT", "CLOUD_PATH",
        "CLOUD_API_KEY", "CLOUD_INSECURE_TLS", "HTTP_TIMEOUT_MS",
    ],
    "PPG": ["PPG_FS_HZ", "PPG_OVERSAMPLE"],
    "MAX30102": ["MAX_PROFILE_PWA", "MAX_LED_RED", "MAX_LED_IR", "MAX_SAMPLE_AVG"],
    "Streaming": ["SENSOR_SETTLE_MS", "BATCH_MS", "BATCH_POOL"],
    "Baterai": [
        "BATT_DIVIDER_GAIN", "BATT_CAL_TRIM", "BATT_OVERSAMPLE",
        "BATT_PERIOD_MS", "BATT_EMA_ALPHA",
    ],
    "Debug": ["SERIAL_BAUD", "STAT_PERIOD_MS", "VERBOSE_HTTP"],
}


def _parse_config() -> dict[str, str]:
    if not CONFIG_H.exists():
        return {}
    text = CONFIG_H.read_text()
    result: dict[str, str] = {}
    for m in re.finditer(
        r'^[ \t]*#define[ \t]+(\w+)[ \t]+([^/\n]*?)[ \t]*(?://[^\n]*)?$',
        text, re.MULTILINE,
    ):
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        result[key] = val
    return result


def _write_config(updates: dict[str, str]) -> None:
    text = CONFIG_H.read_text()
    for key, new_val in updates.items():
        m = re.search(
            rf'^([ \t]*#define[ \t]+{re.escape(key)}[ \t]+)([^\n]*)',
            text, re.MULTILINE,
        )
        if not m:
            continue
        orig_rest = m.group(2).rstrip()
        orig_val = re.sub(r'[ \t]*//.*$', '', orig_rest).strip()
        replacement = f'"{new_val}"' if orig_val.startswith('"') else new_val
        comment_m = re.search(r'([ \t]*//.*)$', orig_rest)
        comment = comment_m.group(1) if comment_m else ''

        def _sub(match, repl=replacement, cmt=comment):
            return match.group(1) + repl + cmt

        text = re.sub(
            rf'^([ \t]*#define[ \t]+{re.escape(key)}[ \t]+)[^\n]*',
            _sub,
            text,
            flags=re.MULTILINE,
        )
    CONFIG_H.write_text(text)


@router.get("/available")
def firmware_available() -> dict:
    pio = subprocess.run(["which", "pio"], capture_output=True)
    return {
        "firmware_path": str(FIRMWARE_PATH),
        "path_exists": FIRMWARE_PATH.exists(),
        "config_exists": CONFIG_H.exists(),
        "pio_available": pio.returncode == 0,
        "pio_path": pio.stdout.decode().strip() if pio.returncode == 0 else None,
    }


@router.get("/config")
def get_config() -> dict:
    return {"config": _parse_config(), "groups": CONFIG_GROUPS}


@router.put("/config")
def update_config(body: dict) -> dict:
    updates = {k: str(v) for k, v in body.items()}
    _write_config(updates)
    return {"ok": True, "updated": list(updates.keys())}


@router.get("/programs")
def list_programs() -> dict:
    programs: list[dict] = []
    if (FIRMWARE_PATH / "src" / "main.cpp").exists():
        programs.append({
            "id": "main",
            "name": "Main Firmware (PlatformIO)",
            "path": "src/main.cpp",
            "type": "pio",
        })
    prog_dir = FIRMWARE_PATH / ".claude" / "programoptimasi"
    if prog_dir.exists():
        for f in sorted(prog_dir.glob("*.ino")):
            programs.append({
                "id": f.stem,
                "name": f.name,
                "path": str(f.relative_to(FIRMWARE_PATH)),
                "type": "ino",
                "note": "Standalone sketch - buka di Arduino IDE untuk compile & flash",
            })
    return {"programs": programs, "firmware_path": str(FIRMWARE_PATH)}


async def _stream_cmd(cmd: list[str], cwd: Path) -> AsyncIterator[str]:
    yield f"data: [ANTARAGA] $ {' '.join(cmd)}\n\n"
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            yield f"data: {line}\n\n"
        await proc.wait()
        code = proc.returncode
        status = "✓ SELESAI" if code == 0 else f"✗ GAGAL (exit {code})"
        yield f"data: \ndata: [ANTARAGA] {status}\n\n"
        yield f"event: done\ndata: {code}\n\n"
    except FileNotFoundError:
        yield "data: [ERROR] 'pio' tidak ditemukan - install: pip install platformio\n\n"
        yield "event: done\ndata: 1\n\n"
    except Exception as exc:
        yield f"data: [ERROR] {exc}\n\n"
        yield "event: done\ndata: 1\n\n"


@router.get("/build-stream")
async def build_stream() -> StreamingResponse:
    return StreamingResponse(
        _stream_cmd(["pio", "run"], FIRMWARE_PATH),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/flash-stream")
async def flash_stream(port: str = "") -> StreamingResponse:
    cmd = ["pio", "run", "-t", "upload"]
    if port:
        cmd += ["--upload-port", port]
    return StreamingResponse(
        _stream_cmd(cmd, FIRMWARE_PATH),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
