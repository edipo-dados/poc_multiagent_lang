#!/bin/bash
# Quick fix deployment script for EC2
# Run this on your EC2 instance to fix the Ollama connection issue

set -e

echo "🚀 Quick Fix Deployment - Ollama Connection"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${YELLOW}📝 Step 1: Updating .env file...${NC}"
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama2
EOF
echo -e "${GREEN}✅ .env updated${NC}"
echo ""

echo -e "${YELLOW}📝 Step 2: Updating docker-compose.yml...${NC}"
# Backup current docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup
echo -e "${GREEN}✅ Backup created: docker-compose.yml.backup${NC}"

# Update docker-compose.yml to add extra_hosts
cat > docker-compose.yml << 'EOF'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: regulatory_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      PIX_REPO_PATH: /app/fake_pix_repo
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./fake_pix_repo:/app/fake_pix_repo

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
EOF
echo -e "${GREEN}✅ docker-compose.yml updated${NC}"
echo ""

echo -e "${YELLOW}🔄 Step 3: Restarting backend container...${NC}"
docker compose restart backend
echo -e "${GREEN}✅ Backend restarted${NC}"
echo ""

echo -e "${YELLOW}⏳ Step 4: Waiting for backend to be ready...${NC}"
sleep 8
echo ""

echo -e "${YELLOW}🏥 Step 5: Checking health status...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

echo -e "${YELLOW}📋 Step 6: Checking recent logs...${NC}"
docker compose logs backend --tail 30 | grep -E "(Ollama|Translator|ERROR|WARNING)" || echo "No Ollama-related messages in recent logs"
echo ""

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "============================================"
echo -e "${YELLOW}📊 Next Steps:${NC}"
echo ""
echo "1. Test the API:"
echo "   curl -X POST http://localhost:8000/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"regulatory_text\":\"Test\",\"repo_path\":\"/app/fake_pix_repo\"}'"
echo ""
echo "2. Check full logs:"
echo "   docker compose logs backend --tail 100"
echo ""
echo "3. Monitor in real-time:"
echo "   docker compose logs backend -f"
echo ""
echo "4. If still having issues, check:"
echo "   - Ollama is running: curl http://localhost:11434/api/tags"
echo "   - Backend can reach host: docker compose exec backend ping -c 2 host.docker.internal"
echo ""
