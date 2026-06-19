#!/usr/bin/env bash
# Jalankan API lokal + ngrok bersamaan untuk dev mode, dan otomatis update
# API_BASE_URL_DEV di .env app Flutter -- jadi tidak perlu cek-cek IP LAN lagi,
# dan langsung bisa dites dari device fisik/emulator mana pun tanpa peduli
# jaringan WiFi yang sama.
#
# Usage: ./scripts/dev.sh [port]

set -uo pipefail

API_PORT="${1:-8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FLUTTER_ENV="$BACKEND_DIR/../antaraga/.env"
NGROK_API="http://127.0.0.1:4040/api/tunnels"

UVICORN_PID=""
NGROK_PID=""

cleanup() {
  echo ""
  echo "Menghentikan API dan ngrok..."
  [[ -n "$UVICORN_PID" ]] && kill "$UVICORN_PID" 2>/dev/null
  [[ -n "$NGROK_PID" ]] && kill "$NGROK_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT INT TERM

if ! command -v ngrok >/dev/null 2>&1; then
  echo "ngrok tidak ditemukan. Install dulu: brew install ngrok"
  exit 1
fi

cd "$BACKEND_DIR"

echo "Menjalankan API di port $API_PORT..."
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port "$API_PORT" &
UVICORN_PID=$!

echo "Menjalankan ngrok..."
ngrok http "$API_PORT" --log=stdout > /tmp/antaraga_ngrok.log 2>&1 &
NGROK_PID=$!

echo "Menunggu ngrok siap..."
NGROK_URL=""
for _ in $(seq 1 30); do
  sleep 1
  NGROK_URL=$(curl -s "$NGROK_API" 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    https = [t['public_url'] for t in tunnels if t['public_url'].startswith('https')]
    print(https[0] if https else (tunnels[0]['public_url'] if tunnels else ''))
except Exception:
    print('')
" 2>/dev/null)
  [[ -n "$NGROK_URL" ]] && break
done

if [[ -z "$NGROK_URL" ]]; then
  echo "Gagal mendapatkan URL ngrok setelah 30 detik. Cek log: /tmp/antaraga_ngrok.log"
  exit 1
fi

echo ""
echo "=================================================="
echo "  API lokal : http://localhost:$API_PORT (docs di /docs)"
echo "  URL ngrok  : $NGROK_URL"
echo "=================================================="

if [[ -f "$FLUTTER_ENV" ]]; then
  if grep -q "^API_BASE_URL_DEV=" "$FLUTTER_ENV"; then
    sed -i.bak "s|^API_BASE_URL_DEV=.*|API_BASE_URL_DEV=$NGROK_URL|" "$FLUTTER_ENV"
    rm -f "$FLUTTER_ENV.bak"
  else
    echo "API_BASE_URL_DEV=$NGROK_URL" >> "$FLUTTER_ENV"
  fi
  echo ""
  echo "API_BASE_URL_DEV di $FLUTTER_ENV sudah diupdate ke URL ngrok di atas."
  echo "-> Hot-restart (bukan cuma hot-reload) app Flutter biar .env baru kepakai."
else
  echo ""
  echo "Tidak ketemu $FLUTTER_ENV -- lewati auto-update .env. Set manual:"
  echo "  API_BASE_URL_DEV=$NGROK_URL"
fi

echo ""
echo "Tekan Ctrl+C untuk berhenti (API dan ngrok ikut mati)."
wait
