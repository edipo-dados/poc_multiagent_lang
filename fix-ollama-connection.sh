#!/bin/bash
# Fix Ollama connection from Docker container to host

echo "🔧 Fixing Ollama connection configuration..."

# Update .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama2
EOF

echo "✅ Updated .env file"

# Restart backend container
echo "🔄 Restarting backend container..."
docker compose restart backend

echo "⏳ Waiting for backend to start..."
sleep 5

# Check health
echo "🏥 Checking health status..."
curl -s http://localhost:8000/health | jq '.'

echo ""
echo "✅ Configuration updated!"
echo ""
echo "📋 Next steps:"
echo "1. Test the API: curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"regulatory_text\":\"Test\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo "2. Check logs: docker compose logs backend --tail 50"
echo "3. Verify Ollama connection in logs (should not see 'Connection refused' anymore)"
