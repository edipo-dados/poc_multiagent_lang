#!/bin/bash

###############################################################################
# Script de Limpeza do Servidor EC2
# Remove imagens Docker não utilizadas, containers parados, volumes órfãos,
# cache de build, logs antigos e arquivos temporários
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🧹 LIMPEZA DO SERVIDOR EC2 - INICIANDO"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Função para mostrar espaço em disco
show_disk_space() {
    echo "💾 Espaço em disco:"
    df -h / | grep -v Filesystem
    echo ""
}

# Mostrar espaço inicial
echo "📊 ANTES DA LIMPEZA:"
show_disk_space

###############################################################################
# 1. DOCKER - Remover containers parados
###############################################################################
echo "🗑️  [1/8] Removendo containers parados..."
STOPPED_CONTAINERS=$(docker ps -aq -f status=exited 2>/dev/null || true)
if [ -n "$STOPPED_CONTAINERS" ]; then
    docker rm $STOPPED_CONTAINERS
    echo "   ✅ Containers parados removidos"
else
    echo "   ℹ️  Nenhum container parado encontrado"
fi
echo ""

###############################################################################
# 2. DOCKER - Remover imagens não utilizadas (dangling)
###############################################################################
echo "🗑️  [2/8] Removendo imagens dangling (sem tag)..."
DANGLING_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null || true)
if [ -n "$DANGLING_IMAGES" ]; then
    docker rmi $DANGLING_IMAGES
    echo "   ✅ Imagens dangling removidas"
else
    echo "   ℹ️  Nenhuma imagem dangling encontrada"
fi
echo ""

###############################################################################
# 3. DOCKER - Remover imagens não utilizadas (não referenciadas por containers)
###############################################################################
echo "🗑️  [3/8] Removendo imagens não utilizadas..."
docker image prune -a -f
echo "   ✅ Imagens não utilizadas removidas"
echo ""

###############################################################################
# 4. DOCKER - Remover volumes órfãos
###############################################################################
echo "🗑️  [4/8] Removendo volumes Docker órfãos..."
docker volume prune -f
echo "   ✅ Volumes órfãos removidos"
echo ""

###############################################################################
# 5. DOCKER - Remover redes não utilizadas
###############################################################################
echo "🗑️  [5/8] Removendo redes Docker não utilizadas..."
docker network prune -f
echo "   ✅ Redes não utilizadas removidas"
echo ""

###############################################################################
# 6. DOCKER - Remover cache de build
###############################################################################
echo "🗑️  [6/8] Removendo cache de build Docker..."
docker builder prune -a -f
echo "   ✅ Cache de build removido"
echo ""

###############################################################################
# 7. SISTEMA - Limpar logs antigos do journald
###############################################################################
echo "🗑️  [7/8] Limpando logs do sistema (journald)..."
sudo journalctl --vacuum-time=7d
echo "   ✅ Logs antigos removidos (mantidos últimos 7 dias)"
echo ""

###############################################################################
# 8. SISTEMA - Limpar arquivos temporários e cache
###############################################################################
echo "🗑️  [8/8] Limpando arquivos temporários..."

# Limpar /tmp (arquivos com mais de 7 dias)
sudo find /tmp -type f -atime +7 -delete 2>/dev/null || true

# Limpar cache do apt (se existir)
if command -v apt-get &> /dev/null; then
    sudo apt-get clean
    sudo apt-get autoclean
    echo "   ✅ Cache do apt limpo"
fi

# Limpar cache do pip (se existir)
if [ -d "$HOME/.cache/pip" ]; then
    rm -rf "$HOME/.cache/pip"
    echo "   ✅ Cache do pip limpo"
fi

# Limpar arquivos de log grandes no diretório do usuário
find "$HOME" -name "*.log" -type f -size +100M -delete 2>/dev/null || true

echo "   ✅ Arquivos temporários removidos"
echo ""

###############################################################################
# RESUMO FINAL
###############################################################################
echo "═══════════════════════════════════════════════════════════════"
echo "✅ LIMPEZA CONCLUÍDA COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mostrar espaço final
echo "📊 DEPOIS DA LIMPEZA:"
show_disk_space

echo "═══════════════════════════════════════════════════════════════"
echo "📋 RESUMO DO QUE FOI LIMPO:"
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Containers Docker parados"
echo "✅ Imagens Docker não utilizadas"
echo "✅ Volumes Docker órfãos"
echo "✅ Redes Docker não utilizadas"
echo "✅ Cache de build Docker"
echo "✅ Logs do sistema (>7 dias)"
echo "✅ Arquivos temporários"
echo "✅ Cache do apt e pip"
echo ""
echo "💡 DICA: Execute este script regularmente para manter o servidor limpo"
echo "═══════════════════════════════════════════════════════════════"
