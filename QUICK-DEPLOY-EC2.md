# 🚀 Deploy Rápido no EC2

## Passo a Passo Completo

### 1️⃣ Conectar no EC2
```bash
ssh -i sua-chave.pem ubuntu@seu-ip-ec2
```

### 2️⃣ Instalar Docker (primeira vez apenas)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker ubuntu
newgrp docker
```

### 3️⃣ Clonar o Repositório
```bash
cd ~
git clone https://github.com/edipo-dados/poc_multiagent_lang.git
cd poc_multiagent_lang
```

### 4️⃣ Criar arquivo .env
```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### 5️⃣ Executar Deploy

**Opção A: Deploy Normal**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Opção B: Se der erro de porta ou conflito (RECOMENDADO)**
```bash
chmod +x emergency-deploy.sh
./emergency-deploy.sh
```

O script de emergência faz:
- Resolve conflitos do Git automaticamente
- Para todos os containers Docker
- Mata processos nas portas 8000, 8501, 5432
- Limpa cache do Docker
- Cria .env se não existir
- Faz build e start dos containers

### 6️⃣ Popular Embeddings (após containers iniciarem)
```bash
# Aguardar ~30 segundos para containers iniciarem completamente
sleep 30

# Popular embeddings
docker compose exec backend python backend/scripts/populate_embeddings_sync.py
```

### 7️⃣ Verificar
```bash
# Ver logs
docker compose logs -f

# Testar API
curl http://localhost:8000/health

# Ver status
docker compose ps
```

## 🌐 Acessar a Aplicação

Substitua `SEU-IP-EC2` pelo IP público da sua instância:

- **Frontend**: http://SEU-IP-EC2:8501
- **Backend API**: http://SEU-IP-EC2:8000
- **API Docs**: http://SEU-IP-EC2:8000/docs
- **Health Check**: http://SEU-IP-EC2:8000/health

## 🔄 Atualizações Futuras

Quando fizer mudanças no código:

```bash
# No seu PC
git add .
git commit -m "Descrição das mudanças"
git push origin main

# No EC2
cd ~/poc_multiagent_lang
./deploy.sh
```

## 🛠️ Comandos Úteis

```bash
# Ver logs em tempo real
docker compose logs -f backend

# Restart de um serviço
docker compose restart backend

# Parar tudo
docker compose down

# Ver uso de recursos
docker stats

# Limpar espaço (se necessário)
docker system prune -a
```

## ⚠️ Troubleshooting

### Erro: "port is already allocated" (porta 8000 em uso)

**Solução 1: Usar o script de correção**
```bash
./fix-port-conflict.sh
./deploy.sh
```

**Solução 2: Limpeza manual completa**
```bash
# Parar TODOS os containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Parar docker compose
docker compose down -v

# Verificar processos nas portas
sudo lsof -i :8000
sudo lsof -i :8501

# Matar processos específicos (substitua PID)
sudo kill -9 PID

# Aguardar e tentar novamente
sleep 5
./deploy.sh
```

**Solução 3: Verificar containers antigos**
```bash
# Listar todos os containers (inclusive parados)
docker ps -a

# Remover containers específicos do projeto
docker rm -f $(docker ps -a | grep poc_multiagent_lang | awk '{print $1}')

# Tentar novamente
./deploy.sh
```

**Solução 4: Reiniciar Docker (última opção)**
```bash
sudo systemctl restart docker
sleep 10
./deploy.sh
```

### Container não inicia
```bash
docker compose logs backend
docker compose down
docker compose up -d --build
```

### Erro de memória
```bash
docker system prune -a -f
./deploy.sh
```

### Resetar banco de dados
```bash
docker compose down -v
./deploy.sh
```

## 📊 Requisitos Mínimos EC2

- **Instância**: t3.small ou t3a.small
- **Disco**: 15GB
- **RAM**: 2GB
- **Portas abertas no Security Group**: 22, 8000, 8501

## ✅ Checklist de Deploy

- [ ] EC2 com Docker instalado
- [ ] Portas 22, 8000, 8501 liberadas no Security Group
- [ ] Repositório clonado
- [ ] Arquivo .env criado
- [ ] Deploy executado com sucesso
- [ ] Embeddings populados
- [ ] Frontend acessível no navegador
- [ ] API respondendo no /health

---

**Custo estimado**: ~$16/mês (t3.small + 15GB storage)
