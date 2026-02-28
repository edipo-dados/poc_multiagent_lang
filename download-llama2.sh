#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  📥 Baixando modelo llama2 no Ollama Docker                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "⏳ Iniciando download do modelo llama2 (3.8GB)..."
echo "   Isso pode demorar alguns minutos dependendo da conexão."
echo ""

docker compose exec ollama ollama pull llama2

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Modelo llama2 baixado com sucesso!"
    echo ""
    echo "Verificando modelos instalados:"
    docker compose exec ollama ollama list
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  🎉 PRONTO! Agora você pode testar a API                     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Teste com:"
    echo "curl -X POST http://localhost:8000/analyze \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"regulatory_text\":\"RESOLUÇÃO BCB Nº 789/2024\",\"repo_path\":\"/app/fake_pix_repo\"}'"
else
    echo ""
    echo "❌ Erro ao baixar modelo!"
    echo ""
    echo "Verifique:"
    echo "1. Container Ollama está rodando: docker compose ps"
    echo "2. Logs do Ollama: docker compose logs ollama"
    echo "3. DNS funcionando: docker compose exec ollama ping -c 2 registry.ollama.ai"
fi
