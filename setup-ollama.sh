#!/bin/bash
# Setup Ollama with llama2 model

echo "🚀 Setting up Ollama with llama2 model..."
echo ""

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service to be ready..."
sleep 10

# Pull llama2 model
echo "📥 Pulling llama2 model (this may take a few minutes)..."
docker compose exec ollama ollama pull llama2

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "You can now use Ollama with:"
echo "  OLLAMA_BASE_URL=http://ollama:11434"
echo "  OLLAMA_MODEL=llama2"
