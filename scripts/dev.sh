#!/usr/bin/env bash
# Jalankan API lokal + tunnel publik bersamaan untuk dev mode.
#
# Mode 1 — Cloudflare Tunnel (direkomendasikan, URL permanen):
#   ./scripts/dev.sh
#   Butuh: cloudflared + ~/.cloudflared/config.yml sudah dikonfigurasi
#   URL: https://api.antaraga.web.id
#
# Mode 2 — ngrok fallback (URL berubah tiap restart):
#   USE_NGROK=1 ./scripts/dev.sh
#
# Usage: ./scripts/dev.sh [port]

set -uo pipefail

API_PORT="${1:-8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FLUTTER_ENV="$BACKEND_DIR/../antaraga/.env"
CLOUDFLARE_CONFIG="$HOME/.cloudflared/config.yml"
USE_NGROK="${USE_NGROK:-}"

UVICORN_PID=""
TUNNEL_PID=""

cleanup() {
  echo ""
  echo "Menghentikan server..."
  [[ -n "$UVICORN_PID" ]] && kill "$UVICORN_PID" 2>/dev/null
  [[ -n "$TUNNEL_PID" ]] && kill "$TUNNEL_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT INT TERM

cd "$BACKEND_DIR"

echo "Menjalankan API di port $API_PORT..."
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port "$API_PORT" &
UVICORN_PID=$!

if [[ -z "$USE_NGROK" ]] && command -v cloudflared >/dev/null 2>&1 && [[ -f "$CLOUDFLARE_CONFIG" ]]; then
  # ---- Mode Cloudflare Tunnel (default) ----------------------------------
  PUBLIC_URL="https://api.antaraga.web.id"

  echo "Menjalankan Cloudflare Tunnel..."
  cloudflared tunnel --config "$CLOUDFLARE_CONFIG" run \
    > /tmp/antaraga_cloudflared.log 2>&1 &
  TUNNEL_PID=$!
  sleep 3

  echo ""
  echo "=================================================="
  echo "  API lokal  : http://localhost:$API_PORT/docs"
  echo "  URL publik  : $PUBLIC_URL"
  echo "  Firmware    : CLOUD_HOST \"api.antaraga.web.id\"  ← tidak perlu flash ulang"
  echo "=================================================="

  # Update Flutter .env sekali (tidak perlu lagi setelah ini karena URL tetap)
  if [[ -f "$FLUTTER_ENV" ]]; then
    changed=0
    for key in API_BASE_URL_DEV API_BASE_URL_PROD; do
      current=$(grep "^${key}=" "$FLUTTER_ENV" | cut -d= -f2-)
      if [[ "$current" != "$PUBLIC_URL" ]]; then
        if grep -q "^${key}=" "$FLUTTER_ENV"; then
          sed -i.bak "s|^${key}=.*|${key}=$PUBLIC_URL|" "$FLUTTER_ENV"
        else
          echo "${key}=$PUBLIC_URL" >> "$FLUTTER_ENV"
        fi
        changed=1
      fi
    done
    rm -f "$FLUTTER_ENV.bak"
    if [[ "$changed" == "1" ]]; then
      echo "Flutter .env diupdate ke $PUBLIC_URL"
      echo "-> Hot-restart Flutter app sekali."
    else
      echo "Flutter .env sudah benar, tidak ada perubahan."
    fi
  fi

else
  # ---- Fallback: ngrok ---------------------------------------------------
  if ! command -v ngrok >/dev/null 2>&1; then
    echo "Tidak ada cloudflared config maupun ngrok. Install salah satu dulu."
    exit 1
  fi

  NGROK_API="http://127.0.0.1:4040/api/tunnels"
  echo "Menjalankan ngrok (fallback — URL berubah tiap restart)..."
  ngrok http "$API_PORT" --log=stdout > /tmp/antaraga_ngrok.log 2>&1 &
  TUNNEL_PID=$!

  PUBLIC_URL=""
  for _ in $(seq 1 30); do
    sleep 1
    PUBLIC_URL=$(curl -s "$NGROK_API" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ts = d.get('tunnels', [])
    hs = [t['public_url'] for t in ts if t['public_url'].startswith('https')]
    print(hs[0] if hs else '')
except: print('')
" 2>/dev/null)
    [[ -n "$PUBLIC_URL" ]] && break
  done

  [[ -z "$PUBLIC_URL" ]] && { echo "ngrok gagal. Cek: /tmp/antaraga_ngrok.log"; exit 1; }

  echo ""
  echo "=================================================="
  echo "  API lokal : http://localhost:$API_PORT/docs"
  echo "  URL ngrok  : $PUBLIC_URL  ← UPDATE firmware config.h!"
  echo "=================================================="

  if [[ -f "$FLUTTER_ENV" ]]; then
    sed -i.bak "s|^API_BASE_URL_DEV=.*|API_BASE_URL_DEV=$PUBLIC_URL|" "$FLUTTER_ENV"
    rm -f "$FLUTTER_ENV.bak"
    echo "Flutter .env diupdate. Hot-restart Flutter app."
  fi
fi

echo ""
echo "Tekan Ctrl+C untuk berhenti."
wait
