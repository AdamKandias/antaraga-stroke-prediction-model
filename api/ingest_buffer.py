"""Thread-safe in-memory rolling buffer untuk batch PPG mentah per device.

Array PPG/RED/IR terlalu besar untuk disimpan di SQLite setiap 500ms.
Modul ini menyimpan WINDOW terakhir per device (default ~10 detik),
hanya dipakai oleh dashboard - bukan histori permanen."""

from collections import deque
from datetime import datetime, timezone
from threading import Lock

WINDOW_BATCHES = 120  # 120 × 500ms = 60 detik sinyal

_lock = Lock()
_buffers: dict[str, deque] = {}


def store(device_id: str, batch: dict) -> None:
    with _lock:
        if device_id not in _buffers:
            _buffers[device_id] = deque(maxlen=WINDOW_BATCHES)
        _buffers[device_id].append({
            **batch,
            "_received_at": datetime.now(timezone.utc).isoformat(),
        })


def get_window(device_id: str) -> list[dict]:
    """Semua batch yang tersimpan (diurutkan lama ke baru)."""
    with _lock:
        buf = _buffers.get(device_id)
        return list(buf) if buf else []


def get_window_s(device_id: str, window_s: float = 10.0) -> list[dict]:
    """Batches dalam window_s detik terakhir (berdasarkan _received_at server)."""
    with _lock:
        buf = _buffers.get(device_id)
        if not buf:
            return []
        batches = list(buf)
    if not batches:
        return []
    cutoff = datetime.now(timezone.utc).timestamp() - window_s
    filtered = []
    for b in batches:
        ts_str = b.get("_received_at", "")
        try:
            ts = datetime.fromisoformat(ts_str).timestamp()
            if ts >= cutoff:
                filtered.append(b)
        except (ValueError, TypeError):
            filtered.append(b)
    return filtered if filtered else batches[-1:]


def get_latest(device_id: str) -> dict | None:
    with _lock:
        buf = _buffers.get(device_id)
        return buf[-1] if buf else None


def list_devices() -> list[str]:
    with _lock:
        return sorted(_buffers.keys())
