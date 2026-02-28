#!/bin/bash
set -e

echo "=== Fixing Ollama to run in Docker ==="

# Step 1: Stop and disable host Ollama service
echo "Step 1: Stopping host Ollama service..."
sudo systemctl stop ollama || true
sudo systemctl disable ollama || true
sudo pkill -9 ollama || true

# Wait for port to be released
echo "Waiting for port 11434 to be released..."
sleep 3

# Verify port is free
if sudo ss -tlnp | grep -q 11434; then
    echo "ERROR: Port 11434 is still in use!"
    sudo ss -tlnp | grep 11434
    exit 1
fi

echo "✅ Port 11434 is now free"

# Step 2: Update .env to use Docker Ollama service
echo "Step 2: Updating .env to use Docker Ollama..."
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
EOF

echo "✅ .env updated"

# Step 3: Stop existing containers
echo "Step 3: Stopping existing containers..."
docker compose down || true

# Step 4: Start Docker Compose with Ollama
echo "Step 4: Starting Docker Compose..."
docker compose up -d

# Step 5: Wait for Ollama to be ready
echo "Step 5: Waiting for Ollama service to be ready..."
sleep 10

# Step 6: Pull llama2 model
echo "Step 6: Pulling llama2 model in Docker Ollama..."
docker compose exec ollama ollama pull llama2

echo ""
echo "=== ✅ Setup Complete! ==="
echo ""
echo "Ollama is now running in Docker at: http://ollama:11434"
echo "Backend will use service name 'ollama' instead of fixed IP"
echo ""
echo "Test the application:"
echo "curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"regulatory_text\":\"RESOLUÇÃO BCB Nº 789/2024\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo ""
echo "Check logs:"
echo "docker compose logs -f backend"
