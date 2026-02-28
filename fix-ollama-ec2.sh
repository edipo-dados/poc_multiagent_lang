#!/bin/bash
# Fix Ollama connection on EC2 - Use actual host IP

set -e

echo "🔧 Fixing Ollama Connection on EC2"
echo "===================================="
echo ""

# Get the host IP
HOST_IP=$(hostname -I | awk '{print $1}')
echo "📍 Detected host IP: $HOST_IP"
echo ""

# Check if Ollama is running
echo "🔍 Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running on localhost:11434"
else
    echo "❌ Ollama is NOT running on localhost:11434"
    echo "   Start it with: ollama serve"
    exit 1
fi
echo ""

# Configure Ollama to listen on all interfaces
echo "🔧 Configuring Ollama to listen on all interfaces..."
sudo systemctl stop ollama 2>/dev/null || true
export OLLAMA_HOST=0.0.0.0:11434
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 3
echo "✅ Ollama restarted"
echo ""

# Update .env with actual host IP
echo "📝 Updating .env with host IP: $HOST_IP"
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://$HOST_IP:11434
OLLAMA_MODEL=llama2
EOF
echo "✅ .env updated"
echo ""

# Restart backend
echo "🔄 Restarting backend container..."
docker compose restart backend
echo "✅ Backend restarted"
echo ""

# Wait for backend
echo "⏳ Waiting for backend to start..."
sleep 8
echo ""

# Test connection from container
echo "🧪 Testing connection from container to host..."
docker compose exec backend sh -c "curl -s http://$HOST_IP:11434/api/tags" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Container can reach Ollama on host!"
else
    echo "❌ Container CANNOT reach Ollama on host"
    echo "   This might be a firewall issue"
fi
echo ""

# Check health
echo "🏥 Checking API health..."
curl -s http://localhost:8000/health | jq '.' || curl -s http://localhost:8000/health
echo ""

# Show recent logs
echo "📋 Recent backend logs:"
docker compose logs backend --tail 20 | grep -E "(Ollama|Sentinel|ERROR)" || echo "No relevant messages"
echo ""

echo "✅ Configuration complete!"
echo ""
echo "🧪 Test the API:"
echo "curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"regulatory_text\":\"Test\",\"repo_path\":\"/app/fake_pix_repo\"}'"
