# Guia de Inicialização - Regulatory AI POC

## Problema Identificado e Solução

O backend estava falhando devido a problemas de importação de módulos. O Dockerfile foi corrigido para:
- Copiar o código para `/app/backend` 
- Configurar `PYTHONPATH=/app`
- Executar como `backend.main:app`

## Após Reinstalar o Docker

### 1. Verificar se o Docker está funcionando
```bash
docker --version
docker ps
```

### 2. Limpar containers antigos (opcional)
```bash
docker-compose down -v
```

### 3. Iniciar todos os serviços
```bash
docker-compose up -d --build
```

### 4. Verificar se os containers estão rodando
```bash
docker ps
```

Você deve ver 3 containers:
- `multi-agent-ia-postgres-1` (porta 5432)
- `multi-agent-ia-backend-1` (porta 8000)
- `multi-agent-ia-frontend-1` (porta 8501)

### 5. Verificar logs do backend
```bash
docker logs multi-agent-ia-backend-1
```

### 6. Testar o backend
```bash
curl http://localhost:8000/health
```

### 7. Acessar o frontend
Abra no navegador: http://localhost:8501

## Troubleshooting

### Se o backend falhar novamente:
```bash
# Ver logs detalhados
docker logs multi-agent-ia-backend-1 --tail 50

# Reconstruir apenas o backend
docker-compose up -d --build backend
```

### Se o PostgreSQL não estiver pronto:
```bash
# Verificar status do PostgreSQL
docker logs multi-agent-ia-postgres-1

# Aguardar até ver "database system is ready to accept connections"
```

### Testar conexão com o banco:
```bash
docker exec -it multi-agent-ia-postgres-1 psql -U postgres -d regulatory_ai -c "SELECT 1;"
```

## Arquivos Modificados

1. **backend/Dockerfile** - Corrigido para resolver imports
2. **backend/requirements.txt** - Atualizado sentence-transformers e adicionado huggingface-hub

## Próximos Passos

Após os serviços estarem rodando:
1. Acesse http://localhost:8501
2. Cole um texto regulatório de teste
3. Clique em "Analisar"
4. Veja os resultados da análise multi-agente
