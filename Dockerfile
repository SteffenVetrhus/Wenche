# ── Stage 1: Build SvelteKit frontend ──
FROM node:22-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Production image ──
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for the SvelteKit server
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY pyproject.toml ./
COPY wenche/ ./wenche/
RUN pip install --no-cache-dir ".[web]"

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build
COPY --from=frontend-build /app/frontend/package.json ./frontend/

# Startup script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Config and data volume
VOLUME ["/app/data"]

ENV WENCHE_ENV=prod
ENV API_URL=http://localhost:8000

EXPOSE 3000

ENTRYPOINT ["./docker-entrypoint.sh"]
