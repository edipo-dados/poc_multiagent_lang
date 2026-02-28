#!/bin/bash

###############################################################################
# Script de Rebuild Limpo - Remove Ollama e Limpa Docker
# Use este script SEMPRE que fizer rebuild para economizar espaço
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🧹 REBUILD LIMPO - REMOVENDO OLLAMA E LIMPANDO DOCKER"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mostrar espaço inicial
echo "📊 ESPAÇO EM DISCO ANTES:"
df -h / | grep -v Filesystem
echo ""

###############################################################################
# FASE 1: PARAR TUDO
###############################################################################
echo "🛑 [1/12] Parando todos os containers..."
docker compose down 2>/dev/null || true
echo "   ✅ Containers parados"
echo ""

###############################################################################
# FASE 2: REMOVER OLLAMA COMPLETAMENTE
###############################################################################
echo "🗑️  [2/12] Removendo Ollama do host..."
sudo systemctl stop ollama 2>/dev/null || true
sudo systemctl disable ollama 2>/dev/null || true
sudo rm -rf /usr/local/bin/ollama 2>/dev/null || true
sudo rm -rf /etc/systemd/system/ollama.service 2>/dev/null || true
sudo rm -rf ~/.ollama 2>/dev/null || true
sudo systemctl daemon-reload 2>/dev/null || true
echo "   ✅ Ollama do host removido"
echo ""

echo "🗑️  [3/12] Removendo volume do Ollama..."
docker volume rm poc_multiagent_lang_ollama_data 2>/dev/null || echo "   ℹ️  Volume não existe"
echo "   ✅ Volume do Ollama removido"
echo ""

echo "🗑️  [4/12] Removendo imagem do Ollama..."
docker rmi ollama/ollama:latest 2>/dev/null || echo "   ℹ️  Imagem não existe"
echo "   ✅ Imagem do Ollama removida"
echo ""

###############################################################################
# FASE 3: LIMPEZA PROFUNDA DO DOCKER
###############################################################################
echo "🗑️  [5/12] Removendo containers parados..."
docker container prune -f
echo "   ✅ Containers parados removidos"
echo ""

echo "🗑️  [6/12] Removendo imagens não utilizadas..."
docker image prune -a -f
echo "   ✅ Imagens não utilizadas removidas"
echo ""

echo "🗑️  [7/12] Removendo volumes órfãos..."
docker volume prune -f
echo "   ✅ Volumes órfãos removidos"
echo ""

echo "🗑️  [8/12] Removendo redes não utilizadas..."
docker network prune -f
echo "   ✅ Redes não utilizadas removidas"
echo ""

echo "🗑️  [9/12] Removendo cache de build..."
docker builder prune -a -f
echo "   ✅ Cache de build removido"
echo ""

###############################################################################
# FASE 4: LIMPEZA DO SISTEMA
###############################################################################
echo "🗑️  [10/12] Limpando logs do sistema..."
sudo journalctl --vacuum-time=3d 2>/dev/null || true
echo "   ✅ Logs antigos removidos"
echo ""

echo "🗑️  [11/12] Limpando cache do sistema..."
sudo apt-get clean 2>/dev/null || true
sudo apt-get autoclean 2>/dev/null || true
rm -rf ~/.cache/pip 2>/dev/null || true
echo "   ✅ Cache do sistema limpo"
echo ""

# Mostrar espaço após limpeza
echo "📊 ESPAÇO EM DISCO APÓS LIMPEZA:"
df -h / | grep -v Filesystem
echo ""

###############################################################################
# FASE 5: REBUILD E INICIAR
###############################################################################
echo "🔨 [12/12] Rebuilding backend..."
docker compose build --no-cache backend
echo "   ✅ Backend rebuilt"
echo ""

echo "🚀 Iniciando serviços (SEM Ollama)..."
docker compose up -d postgres backend frontend
echo "   ✅ Serviços iniciados"
echo ""

# Aguardar backend iniciar
echo "⏳ Aguardando backend iniciar (15 segundos)..."
sleep 15

# Verificar status
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ REBUILD LIMPO CONCLUÍDO!"
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
echo "🎯 PRÓXIMOS PASSOS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Testar API:"
echo "   curl -X POST http://localhost:8000/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"regulatory_text\":\"RESOLUÇÃO BCB Nº 789/2024\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo ""
echo "2. Ver logs:"
echo "   docker compose logs -f backend"
echo ""
echo "3. Verificar espaço:"
echo "   df -h"
echo "   docker system df"
echo ""
echo "═══════════════════════════════════════════════════════════════"
