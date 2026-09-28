#!/bin/bash
# ============================================================
#  AI Document Chatbot — Full Server Setup & Deploy Script
#  Run this ONCE on a fresh Ubuntu 22.04 VM
#  Usage: chmod +x deploy.sh && sudo ./deploy.sh
# ============================================================

set -e  # Exit on any error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[✔] $1${NC}"; }
warn()   { echo -e "${YELLOW}[!] $1${NC}"; }
error()  { echo -e "${RED}[✘] $1${NC}"; exit 1; }

# ── 1. System Update ─────────────────────────────────────────
log "Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# ── 2. Install Docker ─────────────────────────────────────────
if ! command -v docker &> /dev/null; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    log "Docker installed successfully."
else
    log "Docker already installed."
fi

# ── 3. Install Docker Compose ─────────────────────────────────
if ! command -v docker compose &> /dev/null; then
    log "Installing Docker Compose plugin..."
    apt-get install -y docker-compose-plugin
fi

# ── 4. Install Ollama ─────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    log "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    log "Ollama installed."
else
    log "Ollama already installed."
fi

# Enable Ollama as a systemd service (always-on, auto-restart)
log "Enabling Ollama as a system service (always online)..."
systemctl enable ollama
systemctl start ollama
sleep 3  # Wait for Ollama to start

# ── 5. Pull the LLM Model ─────────────────────────────────────
MODEL=${OLLAMA_MODEL:-llama3.2:3b}
log "Pulling Ollama model: $MODEL (this may take a few minutes)..."
ollama pull "$MODEL"
log "Model '$MODEL' is ready."

# ── 6. Install Node.js (for building frontend) ────────────────
if ! command -v node &> /dev/null; then
    log "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

# ── 7. Build Frontend ─────────────────────────────────────────
log "Building React frontend..."
cd frontend
npm ci --silent
npm run build
cd ..
log "Frontend build complete."

# ── 8. Start All Services with Docker Compose ─────────────────
log "Starting all services with Docker Compose..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

# ── 9. Wait and Verify ────────────────────────────────────────
log "Waiting for services to start..."
sleep 10

# Check backend health
if curl -s http://localhost:8000/api/health | grep -q "status"; then
    log "Backend is UP and healthy!"
else
    warn "Backend health check failed. Check logs: docker compose logs backend"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags | grep -q "models"; then
    log "Ollama is UP and running!"
else
    warn "Ollama health check failed. Check: systemctl status ollama"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  🌐 App:     http://$(curl -s ifconfig.me)"
echo "  🔌 API:     http://$(curl -s ifconfig.me)/api/"
echo "  📄 Docs:    http://$(curl -s ifconfig.me):8000/docs"
echo "  🤖 Ollama:  Running locally on port 11434"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f        # view all logs"
echo "    docker compose logs backend   # backend logs only"
echo "    systemctl status ollama       # Ollama status"
echo "    ollama list                   # list downloaded models"
echo ""
