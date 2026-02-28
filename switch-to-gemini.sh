#!/bin/bash

###############################################################################
# Script para Migrar de Ollama para Gemini API
# Resolve problema de RAM insuficiente e melhora performance
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🔄 MIGRANDO DE OLLAMA PARA GEMINI API"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 1. Parar containers
echo "📦 [1/6] Parando containers..."
docker compose down
echo "   ✅ Containers parados"
echo ""

# 2. Backup do .env atual
echo "💾 [2/6] Fazendo backup do .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "   ✅ Backup criado"
echo ""

# 3. Atualizar .env para Gemini
echo "⚙️  [3/6] Atualizando .env para Gemini..."
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=gemini
GEMINI_API_KEY=AIzaSyBVk3MFe3zRRGVMaEslphM3Vd85oS5Rz44
GEMINI_MODEL=gemini-2.0-flash
EOF
echo "   ✅ .env atualizado"
echo ""

# 4. Rebuild backend com código atualizado
echo "🔨 [4/6] Rebuilding backend com fix do Gemini..."
docker compose build --no-cache backend
echo "   ✅ Backend rebuilt"
echo ""

# 5. Subir apenas serviços necessários (SEM Ollama)
echo "🚀 [5/6] Subindo serviços (postgres, backend, frontend)..."
docker compose up -d postgres backend frontend
echo "   ✅ Serviços iniciados"
echo ""

# 6. Aguardar backend iniciar
echo "⏳ [6/6] Aguardando backend iniciar..."
sleep 10

# Verificar se backend está rodando
if docker compose ps backend | grep -q "Up"; then
    echo "   ✅ Backend rodando"
else
    echo "   ❌ Backend não iniciou corretamente"
    echo ""
    echo "Ver logs:"
    echo "  docker compose logs backend"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 CONFIGURAÇÃO ATUAL:"
echo "  LLM: Gemini API (gemini-2.0-flash)"
echo "  Serviços: postgres, backend, frontend"
echo "  Ollama: Removido (economiza RAM)"
echo ""
echo "🔍 VERIFICAR LOGS:"
echo "  docker compose logs -f backend"
echo ""
echo "🧪 TESTAR API:"
echo "  curl -X POST http://localhost:8000/analyze \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"regulatory_text\":\"RESOLUÇÃO BCB Nº 789/2024\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo ""
echo "⚡ PERFORMANCE ESPERADA:"
echo "  Sentinel Agent: ~2-3 segundos"
echo "  Translator Agent: ~3-5 segundos"
echo "  Total: ~10-15 segundos"
echo ""
echo "💡 DICA: Se quiser voltar para Ollama:"
echo "  cp .env.backup.* .env"
echo "  docker compose up -d"
echo "═══════════════════════════════════════════════════════════════"
