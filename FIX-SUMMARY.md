# 🔧 Fix Summary - Ollama Connection Issue

## Problema Identificado

O Translator Agent estava falhando com erro de conexão:
```
Ollama API call failed: HTTPConnectionPool(host='localhost', port=11434): 
Connection refused
```

**Causa Raiz:** O container Docker tentava conectar em `localhost:11434`, mas o Ollama está rodando no host EC2, não dentro do container.

---

## Solução Implementada

### Mudanças nos Arquivos

#### 1. `.env` - Atualizado
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama2
```

**Mudanças:**
- ✅ `DATABASE_URL`: Mudou de `localhost:5433` para `postgres:5432` (nome do serviço Docker)
- ✅ `LLM_TYPE`: Corrigido de `LLM_PROVIDER` para `LLM_TYPE` (nome correto da variável)
- ✅ `OLLAMA_BASE_URL`: Mudou de `localhost:11434` para `host.docker.internal:11434`

#### 2. `docker-compose.yml` - Adicionado `extra_hosts`
```yaml
backend:
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

Isso permite que o container acesse o host usando `host.docker.internal`.

---

## Como Aplicar o Fix no EC2

### Opção 1: Script Automático (Recomendado)
```bash
# No seu EC2, no diretório do projeto
bash quick-fix-deploy.sh
```

Este script vai:
1. ✅ Atualizar o `.env`
2. ✅ Atualizar o `docker-compose.yml` (com backup)
3. ✅ Reiniciar o backend
4. ✅ Verificar o status
5. ✅ Mostrar os logs

### Opção 2: Manual

```bash
# 1. Atualizar .env
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama2
EOF

# 2. Fazer backup do docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup

# 3. Baixar o novo docker-compose.yml do repositório
# (ou editar manualmente para adicionar extra_hosts no serviço backend)

# 4. Reiniciar o backend
docker compose restart backend

# 5. Verificar
curl http://localhost:8000/health
docker compose logs backend --tail 50
```

---

## Verificação do Fix

### 1. Health Check
```bash
curl http://localhost:8000/health | jq '.'
```

**Esperado:**
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_store": "available",
  "timestamp": "..."
}
```

### 2. Logs do Backend
```bash
docker compose logs backend --tail 50 | grep -i ollama
```

**Esperado:** NÃO deve aparecer "Connection refused"

**Deve aparecer:**
```
Initialized OllamaLLM with model=llama2, base_url=http://host.docker.internal:11434
Translator Agent completed successfully
```

### 3. Teste Completo da API
```bash
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "regulatory_text": "RESOLUÇÃO BCB Nº 789/2024 - Teste de regulação",
    "repo_path": "/app/fake_pix_repo"
  }' | jq '.'
```

**Esperado:** Resposta JSON com análise completa, sem erros de conexão.

---

## Status dos Agentes Após o Fix

| Agente | Status | Observação |
|--------|--------|------------|
| Sentinel | ✅ Funcionando | Detecta mudanças e avalia risco |
| Translator | ✅ Funcionando | Conecta ao Ollama via host.docker.internal |
| CodeReader | ⚠️ Temporário | Retorna lista vazia (precisa popular embeddings) |
| Impact | ⚠️ Limitado | Funciona mas sem arquivos do CodeReader |
| SpecGenerator | ✅ Funcionando | Gera spec mínima |
| KiroPrompt | ✅ Funcionando | Gera prompt mínimo |

---

## Próximos Passos

### 1. Popular Embeddings (Para CodeReader funcionar)
```bash
docker compose exec backend python -m backend.scripts.populate_embeddings_sync
```

### 2. Testar Pipeline Completo
```bash
# Teste com texto regulatório real
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d @test_payload.json
```

### 3. Monitorar Performance
```bash
# Logs em tempo real
docker compose logs backend -f

# Uso de recursos
docker stats
```

---

## Troubleshooting

Se ainda tiver problemas, consulte: `TROUBLESHOOTING.md`

### Verificações Rápidas

1. **Ollama está rodando no host?**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Container consegue alcançar o host?**
   ```bash
   docker compose exec backend ping -c 2 host.docker.internal
   ```

3. **Variáveis de ambiente corretas?**
   ```bash
   docker compose exec backend env | grep -E "(LLM|OLLAMA|DATABASE)"
   ```

---

## Arquivos Criados/Atualizados

- ✅ `.env` - Configuração corrigida
- ✅ `docker-compose.yml` - Adicionado extra_hosts
- ✅ `quick-fix-deploy.sh` - Script de deploy automático
- ✅ `fix-ollama-connection.sh` - Script alternativo
- ✅ `TROUBLESHOOTING.md` - Guia completo de troubleshooting
- ✅ `FIX-SUMMARY.md` - Este arquivo

---

## Comandos Úteis

```bash
# Reiniciar tudo
docker compose restart

# Rebuild se necessário
docker compose up -d --build backend

# Ver logs de todos os serviços
docker compose logs -f

# Parar tudo
docker compose down

# Limpar e recomeçar
docker compose down -v
docker compose up -d
```
