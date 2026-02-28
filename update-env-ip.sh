#!/bin/bash
# Simple script to update .env with correct host IP

# Get host IP
HOST_IP=$(hostname -I | awk '{print $1}')

echo "🔧 Updating .env with host IP: $HOST_IP"

# Update .env
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://$HOST_IP:11434
OLLAMA_MODEL=llama2
EOF

echo "✅ .env updated"
echo ""
echo "📋 Current .env content:"
cat .env
echo ""
echo "🔄 Now restart backend: docker compose restart backend"
