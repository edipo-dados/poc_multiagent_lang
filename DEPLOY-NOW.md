# 🚀 Deploy Agora - Instruções Rápidas

## O Que Foi Corrigido

✅ Conexão do Ollama do container Docker para o host EC2
✅ Variável de ambiente correta (`LLM_TYPE` ao invés de `LLM_PROVIDER`)
✅ URL do banco de dados correta para containers Docker
✅ Configuração do `docker-compose.yml` com `extra_hosts`

---

## Comandos para Executar no EC2

### 1. Fazer Pull das Mudanças
```bash
cd ~/poc_multiagent_lang
git pull origin main
```

### 2. Executar o Script de Fix
```bash
bash quick-fix-deploy.sh
```

**O script vai:**
- ✅ Atualizar o `.env` com as configurações corretas
- ✅ Atualizar o `docker-compose.yml` (com backup)
- ✅ Reiniciar o backend
- ✅ Verificar o status
- ✅ Mostrar os logs

### 3. Verificar se Funcionou
```bash
# Ver os logs (NÃO deve ter "Connection refused")
docker compose logs backend --tail 50 | grep -i ollama

# Testar a API
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "regulatory_text": "RESOLUÇÃO BCB Nº 789/2024 - Teste",
    "repo_path": "/app/fake_pix_repo"
  }'
```

---

## O Que Esperar

### Antes do Fix ❌
```
Ollama API call failed: Connection refused
Translator Agent: Using fallback
```

### Depois do Fix ✅
```
Initialized OllamaLLM with model=llama2, base_url=http://host.docker.internal:11434
Translator Agent completed successfully
```

---

## Se Algo Der Errado

### Opção 1: Ver Logs Detalhados
```bash
docker compose logs backend -f
```

### Opção 2: Verificar Ollama no Host
```bash
curl http://localhost:11434/api/tags
```

### Opção 3: Testar Conexão do Container
```bash
docker compose exec backend ping -c 2 host.docker.internal
```

### Opção 4: Consultar Troubleshooting
```bash
cat TROUBLESHOOTING.md
```

---

## Próximos Passos Após o Fix

1. **Popular Embeddings** (para CodeReader funcionar):
   ```bash
   docker compose exec backend python -m backend.scripts.populate_embeddings_sync
   ```

2. **Testar Pipeline Completo**:
   ```bash
   curl -X POST http://localhost:8000/analyze \
     -H 'Content-Type: application/json' \
     -d '{
       "regulatory_text": "RESOLUÇÃO BCB Nº 789/2024...",
       "repo_path": "/app/fake_pix_repo"
     }' | jq '.'
   ```

3. **Acessar Frontend**:
   ```
   http://SEU_IP_EC2:8501
   ```

---

## Resumo dos Arquivos Modificados

- `.env.example` - Template atualizado com configurações corretas
- `docker-compose.yml` - Adicionado `extra_hosts` para acesso ao host
- `quick-fix-deploy.sh` - Script automático de deploy
- `fix-ollama-connection.sh` - Script alternativo
- `TROUBLESHOOTING.md` - Guia completo de troubleshooting
- `FIX-SUMMARY.md` - Resumo detalhado do fix

---

## Comandos Úteis

```bash
# Reiniciar tudo
docker compose restart

# Ver status
docker compose ps

# Ver logs em tempo real
docker compose logs -f

# Health check
curl http://localhost:8000/health | jq '.'

# Parar tudo
docker compose down

# Rebuild completo (se necessário)
docker compose up -d --build
```

---

## ⚠️ IMPORTANTE: Revogue sua API Key do OpenAI

Você expôs sua chave OpenAI várias vezes na conversa:
```
sk-proj-k1DSxrKn8UGV...
```

**AÇÃO NECESSÁRIA:**
1. Acesse: https://platform.openai.com/api-keys
2. Revogue a chave exposta
3. Crie uma nova chave se precisar usar OpenAI no futuro

Por enquanto, estamos usando Ollama (local), então não precisa da chave OpenAI.

---

## Contato Rápido

Se tiver problemas:
1. Verifique os logs: `docker compose logs backend --tail 100`
2. Consulte: `TROUBLESHOOTING.md`
3. Verifique: `FIX-SUMMARY.md`
