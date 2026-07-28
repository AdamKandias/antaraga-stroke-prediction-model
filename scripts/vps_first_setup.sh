#!/usr/bin/env bash
# Setup PERTAMA KALI di VPS — jalankan sekali saja sebagai root
# Usage: bash vps_first_setup.sh

set -e

DEPLOY_PATH="/root/antaraga"
REPO_URL="https://github.com/AdamKandias/antaraga-stroke-prediction-model"  # ganti kalau perlu

echo "=== Clone repository ==="
if [[ -d "$DEPLOY_PATH" ]]; then
  echo "Folder sudah ada, skip clone."
else
  git clone "$REPO_URL" "$DEPLOY_PATH"
fi

cd "$DEPLOY_PATH"

echo "=== Buat .env.production ==="
if [[ ! -f ".env.production" ]]; then
  cp .env.example .env.production
  # Generate JWT_SECRET random
  JWT=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
  sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$JWT|" .env.production
  sed -i "s|^DATABASE_URL=sqlite:///\./antaraga.db|DATABASE_URL=sqlite:////app/data/antaraga.db|" .env.production
  sed -i "s|^DEV_MODE=false|DEV_MODE=false|" .env.production
  echo ""
  echo ">>> .env.production dibuat. Edit manual jika perlu:"
  echo "    nano $DEPLOY_PATH/.env.production"
else
  echo ".env.production sudah ada, dilewati."
fi

echo "=== Build & jalankan container ==="
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "=== Container status ==="
docker compose -f docker-compose.prod.yml ps

echo ""
echo "=== Test health check ==="
sleep 5
curl -sf http://localhost:8089/health && echo " -> API OK" || echo " -> API belum siap, tunggu beberapa detik"

echo ""
echo "=============================================="
echo "Selesai! API berjalan di http://localhost:8089"
echo ""
echo "Selanjutnya:"
echo "  1. Tambahkan nginx reverse proxy ke api.antaraga.web.id -> 127.0.0.1:8089"
echo "  2. Set GitHub Secrets:"
echo "     VPS_HOST      = IP VPS kamu"
echo "     VPS_USER      = root"
echo "     VPS_SSH_KEY   = isi dengan private key SSH"
echo "     VPS_PORT      = 22"
echo "     VPS_DEPLOY_PATH = $DEPLOY_PATH"
echo "=============================================="
