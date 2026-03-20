#!/bin/sh
set -e

# Symlink config files from data volume if they exist
[ -f /app/data/.env ] && ln -sf /app/data/.env /app/.env
[ -f /app/data/config.yaml ] && ln -sf /app/data/config.yaml /app/config.yaml
[ -f /app/data/maskinporten_privat.pem ] && ln -sf /app/data/maskinporten_privat.pem /app/maskinporten_privat.pem

# Start FastAPI backend (background)
python -m uvicorn wenche.api:app \
  --host 127.0.0.1 \
  --port 8000 \
  --log-level info &

# Start SvelteKit frontend (foreground)
cd /app/frontend
PORT=3000 HOST=0.0.0.0 API_URL=http://127.0.0.1:8000 node build
