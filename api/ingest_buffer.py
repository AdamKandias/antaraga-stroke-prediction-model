"""Thread-safe in-memory rolling buffer untuk batch PPG mentah per device.

Array PPG/RED/IR terlalu besar untuk disimpan di SQLite setiap 500ms.
Modul ini menyimpan WINDOW terakhir per device (default ~10 detik),
hanya dipakai oleh dashboard — bukan histori permanen."""

from collections import deque
from datetime import datetime, timezone
from threading import Lock

WINDOW_BATCHES = 20  # 20 × 500ms = 10 detik sinyal

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


def get_latest(device_id: str) -> dict | None:
    with _lock:
        buf = _buffers.get(device_id)
        return buf[-1] if buf else None


def list_devices() -> list[str]:
    with _lock:
        return sorted(_buffers.keys())
