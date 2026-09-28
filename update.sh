#!/bin/bash
# ============================================================
#  AI Document Chatbot — Update/Redeploy Script
#  Run this whenever you push new code
#  Usage: ./update.sh
# ============================================================

set -e

GREEN='\033[0;32m'
NC='\033[0m'
log() { echo -e "${GREEN}[✔] $1${NC}"; }

log "Pulling latest code..."
git pull origin main

log "Rebuilding frontend..."
cd frontend
npm ci --silent
npm run build
cd ..

log "Restarting backend container..."
docker compose up -d --build backend

log "Done! App updated."
echo "  🌐 http://$(curl -s ifconfig.me)"
