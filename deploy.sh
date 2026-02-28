#!/bin/bash

# Script de Deploy - Regulatory AI POC
# Execute no EC2: bash deploy.sh

set -e

echo "🚀 Iniciando deploy da aplicação..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Atualizar código do repositório
echo -e "${BLUE}📥 Atualizando código do GitHub...${NC}"
git pull origin main

# Habilitar BuildKit para builds mais rápidos
export DOCKER_BUILDKIT=1

# Parar containers existentes
echo -e "${BLUE}🛑 Parando containers existentes...${NC}"
docker compose down

# Limpar volumes antigos (opcional - descomente se necessário)
# docker compose down -v

# Build e start dos containers
echo -e "${BLUE}🔨 Buildando e iniciando containers...${NC}"
docker compose up -d --build

# Aguardar containers iniciarem
echo -e "${BLUE}⏳ Aguardando containers iniciarem...${NC}"
sleep 10

# Verificar status
echo -e "${BLUE}📊 Status dos containers:${NC}"
docker compose ps

# Testar health check
echo -e "${BLUE}🏥 Testando health check do backend...${NC}"
sleep 5
curl -f http://localhost:8000/health || echo "⚠️  Backend ainda não está respondendo"

echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "Acesse a aplicação:"
echo "  Frontend: http://$(curl -s ifconfig.me):8501"
echo "  Backend:  http://$(curl -s ifconfig.me):8000"
echo ""
echo "Para ver logs:"
echo "  docker compose logs -f"
