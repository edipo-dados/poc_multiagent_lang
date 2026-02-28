#!/bin/bash

# Script para resolver conflito de portas no EC2
# Execute: bash fix-port-conflict.sh

echo "🔍 Verificando portas em uso..."

# Verificar porta 8000
PORT_8000=$(sudo lsof -ti :8000)
if [ ! -z "$PORT_8000" ]; then
    echo "⚠️  Porta 8000 em uso pelo processo: $PORT_8000"
    echo "🛑 Matando processo..."
    sudo kill -9 $PORT_8000
    echo "✅ Processo finalizado"
else
    echo "✅ Porta 8000 livre"
fi

# Verificar porta 8501
PORT_8501=$(sudo lsof -ti :8501)
if [ ! -z "$PORT_8501" ]; then
    echo "⚠️  Porta 8501 em uso pelo processo: $PORT_8501"
    echo "🛑 Matando processo..."
    sudo kill -9 $PORT_8501
    echo "✅ Processo finalizado"
else
    echo "✅ Porta 8501 livre"
fi

# Parar todos os containers Docker
echo "🐳 Parando containers Docker..."
docker compose down

# Limpar containers órfãos
echo "🧹 Limpando containers órfãos..."
docker container prune -f

echo ""
echo "✅ Portas liberadas! Agora execute:"
echo "   ./deploy.sh"
