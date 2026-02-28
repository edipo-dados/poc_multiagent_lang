#!/bin/bash

# Script para resolver conflito de portas no EC2
# Execute: bash fix-port-conflict.sh

set -e

echo "🔍 Verificando e limpando portas..."

# Parar TODOS os containers Docker primeiro
echo "🐳 Parando TODOS os containers Docker..."
docker stop $(docker ps -aq) 2>/dev/null || echo "Nenhum container rodando"

# Remover containers parados
echo "🗑️  Removendo containers parados..."
docker rm $(docker ps -aq) 2>/dev/null || echo "Nenhum container para remover"

# Parar docker compose especificamente
echo "🐳 Parando docker compose..."
docker compose down 2>/dev/null || echo "Docker compose já parado"

# Verificar e matar processos nas portas
echo "🔍 Verificando porta 8000..."
PORT_8000=$(sudo lsof -ti :8000 2>/dev/null)
if [ ! -z "$PORT_8000" ]; then
    echo "⚠️  Porta 8000 em uso pelo processo: $PORT_8000"
    sudo kill -9 $PORT_8000
    echo "✅ Processo finalizado"
else
    echo "✅ Porta 8000 livre"
fi

echo "🔍 Verificando porta 8501..."
PORT_8501=$(sudo lsof -ti :8501 2>/dev/null)
if [ ! -z "$PORT_8501" ]; then
    echo "⚠️  Porta 8501 em uso pelo processo: $PORT_8501"
    sudo kill -9 $PORT_8501
    echo "✅ Processo finalizado"
else
    echo "✅ Porta 8501 livre"
fi

echo "🔍 Verificando porta 5432..."
PORT_5432=$(sudo lsof -ti :5432 2>/dev/null)
if [ ! -z "$PORT_5432" ]; then
    echo "⚠️  Porta 5432 em uso pelo processo: $PORT_5432"
    sudo kill -9 $PORT_5432
    echo "✅ Processo finalizado"
else
    echo "✅ Porta 5432 livre"
fi

# Aguardar um pouco
echo "⏳ Aguardando portas liberarem..."
sleep 3

# Verificar novamente
echo ""
echo "📊 Status final das portas:"
sudo lsof -i :8000 2>/dev/null || echo "✅ Porta 8000: LIVRE"
sudo lsof -i :8501 2>/dev/null || echo "✅ Porta 8501: LIVRE"
sudo lsof -i :5432 2>/dev/null || echo "✅ Porta 5432: LIVRE"

echo ""
echo "✅ Limpeza concluída! Agora execute:"
echo "   ./deploy.sh"
