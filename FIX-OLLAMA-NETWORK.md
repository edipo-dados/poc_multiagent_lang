# 🔧 Fix Ollama Network Access

## Problema

O container Docker está tentando conectar em `172.31.5.241:11434` mas recebe "Connection refused".

**Causa:** O Ollama está escutando apenas em `localhost` (127.0.0.1), não em todas as interfaces de rede.

---

## Solução: Configurar Ollama para Escutar em Todas as Interfaces

### Opção 1: Usando Variável de Ambiente (Recomendado)

```bash
# 1. Parar o Ollama se estiver rodando
pkill ollama

# 2. Configurar para escutar em todas as interfaces
export OLLAMA_HOST=0.0.0.0:11434

# 3. Iniciar Ollama em background
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 4. Verificar se está rodando
sleep 3
curl http://localhost:11434/api/tags
```

### Opção 2: Usando Systemd Service

```bash
# 1. Criar arquivo de configuração
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# 2. Recarregar systemd
sudo systemctl daemon-reload

# 3. Reiniciar Ollama
sudo systemctl restart ollama

# 4. Verificar status
sudo systemctl status ollama
```

### Opção 3: Script Automático

```bash
bash fix-ollama-ec2.sh
```

---

## Atualizar .env com IP do Host

Depois de configurar o Ollama, atualize o `.env`:

```bash
# Obter IP do host
HOST_IP=$(hostname -I | awk '{print $1}')
echo "Host IP: $HOST_IP"

# Atualizar .env
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://$HOST_IP:11434
OLLAMA_MODEL=llama2
EOF

# Reiniciar backend
docker compose restart backend
```

Ou use o script:
```bash
bash update-env-ip.sh
docker compose restart backend
```

---

## Verificações

### 1. Verificar se Ollama está escutando em todas as interfaces

```bash
# Deve mostrar 0.0.0.0:11434 ou seu IP:11434
sudo netstat -tlnp | grep 11434
# ou
sudo ss -tlnp | grep 11434
```

**Esperado:**
```
tcp   0   0   0.0.0.0:11434   0.0.0.0:*   LISTEN   12345/ollama
```

**Problema (se mostrar apenas 127.0.0.1):**
```
tcp   0   0   127.0.0.1:11434   0.0.0.0:*   LISTEN   12345/ollama
```

### 2. Testar conexão do host

```bash
HOST_IP=$(hostname -I | awk '{print $1}')
curl http://$HOST_IP:11434/api/tags
```

### 3. Testar conexão do container

```bash
HOST_IP=$(hostname -I | awk '{print $1}')
docker compose exec backend curl http://$HOST_IP:11434/api/tags
```

### 4. Verificar logs do backend

```bash
docker compose logs backend --tail 50 | grep -i ollama
```

**Esperado (sucesso):**
```
Initialized OllamaLLM with model=llama2, base_url=http://172.31.5.241:11434
Sentinel Agent completed successfully
```

**Problema (falha):**
```
Ollama API call failed: Connection refused
```

---

## Troubleshooting

### Problema: Firewall bloqueando porta 11434

```bash
# Verificar regras do firewall
sudo iptables -L -n | grep 11434

# Se necessário, permitir conexões locais
sudo iptables -I INPUT -s 172.31.0.0/16 -p tcp --dport 11434 -j ACCEPT
```

### Problema: Ollama não inicia com OLLAMA_HOST

```bash
# Ver logs de erro
cat /tmp/ollama.log

# Tentar iniciar manualmente
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

### Problema: Container não consegue resolver IP do host

```bash
# Verificar se container consegue pingar o host
HOST_IP=$(hostname -I | awk '{print $1}')
docker compose exec backend ping -c 2 $HOST_IP

# Verificar rotas de rede do container
docker compose exec backend ip route
```

---

## Comandos Completos (Copie e Cole)

```bash
# 1. Parar Ollama
pkill ollama

# 2. Configurar e iniciar Ollama
export OLLAMA_HOST=0.0.0.0:11434
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

# 3. Verificar se está escutando
sudo netstat -tlnp | grep 11434

# 4. Atualizar .env
HOST_IP=$(hostname -I | awk '{print $1}')
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://$HOST_IP:11434
OLLAMA_MODEL=llama2
EOF

# 5. Reiniciar backend
docker compose restart backend

# 6. Aguardar e testar
sleep 8
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"regulatory_text":"Test","repo_path":"/app/fake_pix_repo"}'
```

---

## Alternativa: Usar network_mode: host

Se nada funcionar, você pode fazer o backend usar a rede do host:

```yaml
# docker-compose.yml
backend:
  network_mode: "host"
  # ... resto da configuração
```

E no `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/regulatory_ai
```

**Desvantagem:** Perde o isolamento de rede do Docker.

---

## Status Esperado Após o Fix

```bash
$ curl http://localhost:8000/health
{
  "status": "healthy",
  "database": "connected",
  "vector_store": "available",
  "timestamp": "..."
}

$ docker compose logs backend --tail 20 | grep Ollama
Initialized OllamaLLM with model=llama2, base_url=http://172.31.5.241:11434
Sentinel Agent completed successfully
Translator Agent completed successfully
```
