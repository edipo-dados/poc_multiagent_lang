#!/bin/bash

###############################################################################
# Script para Limpar Ollama/Docker e Migrar para Gemini
# Libera espaço em disco antes de fazer rebuild
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🧹 LIMPEZA COMPLETA + MIGRAÇÃO PARA GEMINI"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mostrar espaço inicial
echo "📊 ESPAÇO EM DISCO ANTES:"
df -h / | grep -v Filesystem
echo ""

###############################################################################
# FASE 1: PARAR E REMOVER TUDO
###############################################################################
echo "═══════════════════════════════════════════════════════════════"
echo "FASE 1: PARAR E REMOVER CONTAINERS/VOLUMES"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🛑 [1/10] Parando todos os containers..."
docker compose down 2>/dev/null || true
echo "   ✅ Containers parados"
echo ""

echo "🗑️  [2/10] Removendo volume do Ollama..."
docker volume rm poc_multiagent_lang_ollama_data 2>/dev/null || echo "   ℹ️  Volume não existe"
echo "   ✅ Volume removido"
echo ""

echo "🗑️  [3/10] Removendo Ollama do host..."
sudo systemctl stop ollama 2>/dev/null || true
sudo systemctl disable ollama 2>/dev/null || true
sudo rm -rf /usr/local/bin/ollama 2>/dev/null || true
sudo rm -rf /etc/systemd/system/ollama.service 2>/dev/null || true
sudo rm -rf ~/.ollama 2>/dev/null || true
sudo systemctl daemon-reload 2>/dev/null || true
echo "   ✅ Ollama do host removido"
echo ""

###############################################################################
# FASE 2: LIMPAR DOCKER
###############################################################################
echo "═══════════════════════════════════════════════════════════════"
echo "FASE 2: LIMPAR DOCKER (LIBERAR ESPAÇO)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🗑️  [4/10] Removendo containers parados..."
docker container prune -f
echo "   ✅ Containers parados removidos"
echo ""

echo "🗑️  [5/10] Removendo imagens não utilizadas..."
docker image prune -a -f
echo "   ✅ Imagens removidas"
echo ""

echo "🗑️  [6/10] Removendo volumes órfãos..."
docker volume prune -f
echo "   ✅ Volumes órfãos removidos"
echo ""

echo "🗑️  [7/10] Removendo cache de build..."
docker builder prune -a -f
echo "   ✅ Cache de build removido"
echo ""

# Mostrar espaço após limpeza
echo "📊 ESPAÇO EM DISCO APÓS LIMPEZA:"
df -h / | grep -v Filesystem
echo ""

###############################################################################
# FASE 3: CONFIGURAR GEMINI
###############################################################################
echo "═══════════════════════════════════════════════════════════════"
echo "FASE 3: CONFIGURAR GEMINI"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "💾 [8/10] Fazendo backup do .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "   ✅ Backup criado"
echo ""

echo "⚙️  [9/10] Atualizando .env para Gemini..."
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=gemini
GEMINI_API_KEY=AIzaSyBVk3MFe3zRRGVMaEslphM3Vd85oS5Rz44
GEMINI_MODEL=gemini-2.0-flash
EOF
echo "   ✅ .env atualizado"
echo ""

###############################################################################
# FASE 4: REBUILD E INICIAR
###############################################################################
echo "═══════════════════════════════════════════════════════════════"
echo "FASE 4: REBUILD E INICIAR SERVIÇOS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🔨 [10/10] Rebuilding e iniciando serviços..."
echo "   (Isso pode demorar alguns minutos...)"
docker compose build --no-cache backend
echo "   ✅ Backend rebuilt"
echo ""
echo "🚀 Iniciando apenas serviços necessários (SEM Ollama)..."
docker compose up -d postgres backend frontend
echo "   ✅ Serviços iniciados (postgres, backend, frontend)"
echo ""

# Aguardar backend iniciar
echo "⏳ Aguardando backend iniciar (15 segundos)..."
sleep 15

# Verificar status
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ MIGRAÇÃO CONCLUÍDA!"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mostrar espaço final
echo "📊 ESPAÇO EM DISCO FINAL:"
df -h / | grep -v Filesystem
echo ""

echo "📋 STATUS DOS SERVIÇOS:"
docker compose ps
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "🔍 PRÓXIMOS PASSOS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Ver logs do backend:"
echo "   docker compose logs -f backend"
echo ""
echo "2. Testar API:"
echo "   curl -X POST http://localhost:8000/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"regulatory_text\":\"RESOLUÇÃO BCB Nº 789/2024\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo ""
echo "3. Verificar que está usando Gemini nos logs:"
echo "   docker compose logs backend | grep Gemini"
echo ""
echo "   Deve mostrar:"
echo "   ✅ Initialized GeminiLLM with model=models/gemini-2.0-flash"
echo ""
echo "═══════════════════════════════════════════════════════════════"
