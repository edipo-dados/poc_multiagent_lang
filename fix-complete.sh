#!/bin/bash
# Complete fix for Ollama connection on EC2

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔧 Complete Ollama Fix for EC2                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get host IP
HOST_IP=$(hostname -I | awk '{print $1}')
echo -e "${YELLOW}📍 Host IP detected: $HOST_IP${NC}"
echo ""

# Step 1: Stop Ollama
echo -e "${YELLOW}Step 1: Stopping Ollama...${NC}"
pkill ollama 2>/dev/null || echo "Ollama was not running"
sleep 2
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 2: Start Ollama listening on all interfaces
echo -e "${YELLOW}Step 2: Starting Ollama on 0.0.0.0:11434...${NC}"
export OLLAMA_HOST=0.0.0.0:11434
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5
echo -e "${GREEN}✅ Ollama started${NC}"
echo ""

# Step 3: Verify Ollama is listening
echo -e "${YELLOW}Step 3: Verifying Ollama is listening...${NC}"
if sudo netstat -tlnp 2>/dev/null | grep -q ":11434.*0.0.0.0"; then
    echo -e "${GREEN}✅ Ollama is listening on 0.0.0.0:11434${NC}"
elif sudo ss -tlnp 2>/dev/null | grep -q ":11434.*0.0.0.0"; then
    echo -e "${GREEN}✅ Ollama is listening on 0.0.0.0:11434${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify with netstat/ss, but continuing...${NC}"
fi
echo ""

# Step 4: Test Ollama from localhost
echo -e "${YELLOW}Step 4: Testing Ollama from localhost...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama responds on localhost:11434${NC}"
else
    echo -e "${RED}❌ Ollama NOT responding on localhost:11434${NC}"
    echo "Check logs: cat /tmp/ollama.log"
    exit 1
fi
echo ""

# Step 5: Test Ollama from host IP
echo -e "${YELLOW}Step 5: Testing Ollama from host IP ($HOST_IP)...${NC}"
if curl -s http://$HOST_IP:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama responds on $HOST_IP:11434${NC}"
else
    echo -e "${RED}❌ Ollama NOT responding on $HOST_IP:11434${NC}"
    echo "This might be a firewall issue"
    exit 1
fi
echo ""

# Step 6: Update .env
echo -e "${YELLOW}Step 6: Updating .env file...${NC}"
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://$HOST_IP:11434
OLLAMA_MODEL=llama2
EOF
echo -e "${GREEN}✅ .env updated with:${NC}"
echo "   OLLAMA_BASE_URL=http://$HOST_IP:11434"
echo ""

# Step 7: Restart backend
echo -e "${YELLOW}Step 7: Restarting backend container...${NC}"
docker compose restart backend
echo -e "${GREEN}✅ Backend restarted${NC}"
echo ""

# Step 8: Wait for backend
echo -e "${YELLOW}Step 8: Waiting for backend to start...${NC}"
sleep 10
echo -e "${GREEN}✅ Ready${NC}"
echo ""

# Step 9: Test from container
echo -e "${YELLOW}Step 9: Testing connection from container to host...${NC}"
if docker compose exec backend curl -s http://$HOST_IP:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Container can reach Ollama on host!${NC}"
else
    echo -e "${RED}❌ Container CANNOT reach Ollama on host${NC}"
    echo "This is likely a firewall or network issue"
fi
echo ""

# Step 10: Check health
echo -e "${YELLOW}Step 10: Checking API health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
echo ""

# Step 11: Check logs
echo -e "${YELLOW}Step 11: Checking backend logs for Ollama...${NC}"
docker compose logs backend --tail 30 | grep -i "ollama\|sentinel\|translator" | tail -10
echo ""

# Final test
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧪 Final Test                                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}Testing full API call...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"regulatory_text":"Test regulation","repo_path":"/app/fake_pix_repo"}')

if echo "$RESPONSE" | grep -q "Connection refused"; then
    echo -e "${RED}❌ FAILED: Still getting Connection refused${NC}"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Ollama logs: cat /tmp/ollama.log"
    echo "2. Check backend logs: docker compose logs backend --tail 50"
    echo "3. Verify firewall: sudo iptables -L -n | grep 11434"
    exit 1
elif echo "$RESPONSE" | grep -q "execution_id"; then
    echo -e "${GREEN}✅ SUCCESS! API is working!${NC}"
    echo ""
    echo "Response preview:"
    echo "$RESPONSE" | jq '.execution_id, .change_detected, .risk_level' 2>/dev/null || echo "$RESPONSE" | head -5
else
    echo -e "${YELLOW}⚠️  Unexpected response:${NC}"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Fix Complete!                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  - Ollama: 0.0.0.0:11434"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs backend -f"
echo "  - Health check: curl http://localhost:8000/health"
echo "  - Ollama logs: cat /tmp/ollama.log"
echo ""
