# Troubleshooting Guide - Regulatory AI POC

## Current Issues and Solutions

### 1. ✅ FIXED: Translator Agent - Ollama Connection Refused

**Problem:** 
```
Ollama API call failed: HTTPConnectionPool(host='localhost', port=11434): 
Max retries exceeded with url: /api/generate (Caused by NewConnectionError(
"HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: 
[Errno 111] Connection refused"))
```

**Root Cause:** Docker container trying to connect to `localhost:11434`, but Ollama runs on the host machine, not inside the container.

**Solution:**
1. Use `host.docker.internal` instead of `localhost` in `.env`:
   ```bash
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```

2. Add `extra_hosts` to `docker-compose.yml`:
   ```yaml
   backend:
     extra_hosts:
       - "host.docker.internal:host-gateway"
   ```

3. Deploy the fix:
   ```bash
   bash fix-ollama-connection.sh
   ```

**Verification:**
```bash
# Check logs - should NOT see "Connection refused"
docker compose logs backend --tail 50 | grep -i ollama

# Test API
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"regulatory_text":"Test regulation","repo_path":"/app/fake_pix_repo"}'
```

---

### 2. ⚠️ PENDING: CodeReader Agent - Returns Empty Results

**Problem:**
```
CodeReader Agent: Using temporary sync wrapper - returning empty impacted_files
```

**Root Cause:** 
- CodeReader agent is async but LangGraph runs in sync context
- Vector store has no embeddings populated yet

**Solution (Part 1 - Temporary Wrapper):**
Already implemented in `backend/orchestrator/graph.py` - returns empty list to prevent crashes.

**Solution (Part 2 - Populate Embeddings):**
```bash
# Inside the backend container
docker compose exec backend python -m backend.scripts.populate_embeddings_sync
```

**Solution (Part 3 - Fix Async/Sync Issue):**
Options:
1. Convert CodeReader to fully synchronous (recommended for LangGraph)
2. Use proper async handling with nest_asyncio (already added to requirements)
3. Run CodeReader in a separate thread pool

**Status:** Temporarily disabled, needs proper implementation.

---

### 3. Database Connection Issues

**Problem:** Health check shows `"database":"disconnected"`

**Common Causes:**
1. Wrong DATABASE_URL format
2. PostgreSQL not ready yet
3. Network issues between containers

**Solutions:**

**Check 1: Verify DATABASE_URL**
```bash
# Inside container, should use service name 'postgres', not 'localhost'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
```

**Check 2: Verify PostgreSQL is running**
```bash
docker compose ps
docker compose logs postgres --tail 20
```

**Check 3: Test connection manually**
```bash
docker compose exec backend python -c "
from backend.database.connection import get_db_session
import asyncio
async def test():
    async for session in get_db_session():
        print('✅ Database connected!')
        break
asyncio.run(test())
"
```

---

## Quick Diagnostics

### Check All Services Status
```bash
# Service status
docker compose ps

# Health check
curl http://localhost:8000/health | jq '.'

# Backend logs
docker compose logs backend --tail 50

# Frontend logs
docker compose logs frontend --tail 20

# Database logs
docker compose logs postgres --tail 20
```

### Test Ollama on Host
```bash
# Check if Ollama is running
curl http://localhost:11434/api/generate -d '{
  "model":"llama2",
  "prompt":"Hello",
  "stream":false
}'

# List available models
curl http://localhost:11434/api/tags
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Full analysis (requires embeddings)
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "regulatory_text":"RESOLUÇÃO BCB Nº 789/2024 - Teste",
    "repo_path":"/app/fake_pix_repo"
  }' | jq '.'
```

---

## Common Error Messages

### "Connection refused" (Port 11434)
- **Cause:** Container can't reach Ollama on host
- **Fix:** Use `host.docker.internal:11434` instead of `localhost:11434`

### "Can't patch loop of type uvloop.Loop"
- **Cause:** Async/sync conflict with nest_asyncio
- **Fix:** Already handled with temporary wrapper, needs proper async implementation

### "No module named 'nest_asyncio'"
- **Cause:** Missing dependency
- **Fix:** Already added to `requirements-prod.txt`, rebuild container

### "database disconnected"
- **Cause:** Wrong DATABASE_URL or PostgreSQL not ready
- **Fix:** Use `postgres:5432` not `localhost:5433` inside container

### "vector_store unavailable"
- **Cause:** No embeddings populated yet
- **Fix:** Run `populate_embeddings_sync.py` script

---

## Performance Notes

### Ollama Response Times
- First request: 10-30 seconds (model loading)
- Subsequent requests: 2-5 seconds
- Model: llama2 (3.8GB)
- Instance: t3.small (2 vCPU, 2GB RAM) - may be slow

### Optimization Options
1. Use smaller model: `ollama pull llama2:7b-chat-q4_0` (faster, less accurate)
2. Upgrade instance: t3.medium or larger
3. Use OpenAI API instead (faster but costs money)

---

## Next Steps

1. ✅ Fix Ollama connection (use this guide)
2. ⏳ Populate vector store embeddings
3. ⏳ Fix CodeReader async/sync issue
4. ⏳ Test full pipeline end-to-end
5. ⏳ Monitor performance and optimize if needed
