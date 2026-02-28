#!/bin/bash

# Script de Deploy de Emergência - Resolve todos os problemas
# Execute no EC2: bash emergency-deploy.sh

set -e

echo "🚨 DEPLOY DE EMERGÊNCIA - Limpeza completa"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Resolver conflito de merge
echo -e "${BLUE}📥 Resolvendo conflitos do Git...${NC}"
git reset --hard HEAD
git clean -fd
git pull origin main

# 2. Parar TUDO do Docker
echo -e "${BLUE}🛑 Parando TODOS os containers Docker...${NC}"
docker stop $(docker ps -aq) 2>/dev/null || echo "Nenhum container rodando"
docker rm $(docker ps -aq) 2>/dev/null || echo "Nenhum container para remover"
docker compose down -v 2>/dev/null || echo "Docker compose já parado"

# 3. Matar processos nas portas
echo -e "${BLUE}🔫 Matando processos nas portas...${NC}"

# Porta 8000
PORT_8000=$(sudo lsof -ti :8000 2>/dev/null)
if [ ! -z "$PORT_8000" ]; then
    echo -e "${YELLOW}Matando processo na porta 8000: $PORT_8000${NC}"
    sudo kill -9 $PORT_8000 2>/dev/null || true
fi

# Porta 8501
PORT_8501=$(sudo lsof -ti :8501 2>/dev/null)
if [ ! -z "$PORT_8501" ]; then
    echo -e "${YELLOW}Matando processo na porta 8501: $PORT_8501${NC}"
    sudo kill -9 $PORT_8501 2>/dev/null || true
fi

# Porta 5432
PORT_5432=$(sudo lsof -ti :5432 2>/dev/null)
if [ ! -z "$PORT_5432" ]; then
    echo -e "${YELLOW}Matando processo na porta 5432: $PORT_5432${NC}"
    sudo kill -9 $PORT_5432 2>/dev/null || true
fi

# 4. Aguardar portas liberarem
echo -e "${BLUE}⏳ Aguardando portas liberarem...${NC}"
sleep 5

# 5. Verificar se portas estão livres
echo -e "${BLUE}🔍 Verificando portas...${NC}"
if sudo lsof -i :8000 2>/dev/null; then
    echo -e "${RED}❌ Porta 8000 ainda em uso!${NC}"
    echo "Execute manualmente: sudo kill -9 \$(sudo lsof -ti :8000)"
    exit 1
fi

if sudo lsof -i :8501 2>/dev/null; then
    echo -e "${RED}❌ Porta 8501 ainda em uso!${NC}"
    echo "Execute manualmente: sudo kill -9 \$(sudo lsof -ti :8501)"
    exit 1
fi

echo -e "${GREEN}✅ Todas as portas livres!${NC}"

# 6. Limpar cache do Docker
echo -e "${BLUE}🧹 Limpando cache do Docker...${NC}"
docker system prune -f

# 7. Criar .env se não existir
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Criando arquivo .env...${NC}"
    cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
API_HOST=0.0.0.0
API_PORT=8000
EOF
fi

# 8. Build e start
echo -e "${BLUE}🔨 Buildando e iniciando containers...${NC}"
export DOCKER_BUILDKIT=1
docker compose up -d --build

# 9. Aguardar inicialização
echo -e "${BLUE}⏳ Aguardando containers iniciarem...${NC}"
sleep 15

# 10. Verificar status
echo -e "${BLUE}📊 Status dos containers:${NC}"
docker compose ps

# 11. Testar health check
echo -e "${BLUE}🏥 Testando health check...${NC}"
sleep 5
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo -e "${GREEN}✅ Backend respondendo!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend ainda não está respondendo, aguarde mais um pouco${NC}"
fi

echo ""
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "Acesse a aplicação:"
echo "  Frontend: http://\$(curl -s ifconfig.me):8501"
echo "  Backend:  http://\$(curl -s ifconfig.me):8000"
echo ""
echo "Para ver logs:"
echo "  docker compose logs -f"
echo ""
echo "Para popular embeddings:"
echo "  docker compose exec backend python backend/scripts/populate_embeddings_sync.py"
