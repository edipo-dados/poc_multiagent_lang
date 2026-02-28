# ☁️ Deploy AWS EC2 (Produção)

Guia completo para deploy da POC Multi-Agent Regulatory AI em produção na AWS EC2.

## 📋 Pré-requisitos

### Instância EC2
- **Tipo**: Mínimo t3.medium (2 vCPU, 4GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 20GB+ (recomendado 30GB)
- **Security Group**: Portas liberadas
  - 22 (SSH)
  - 8000 (Backend API)
  - 8501 (Frontend Streamlit)

### Software
- Docker 24.0+
- Docker Compose 2.0+
- Git

### Chave API
- Google Gemini API Key (gratuita): https://aistudio.google.com/apikey

## 🚀 Deploy Passo a Passo

### 1. Conectar ao EC2

```bash
ssh -i sua-chave.pem ubuntu@<seu-ip-ec2>
```

### 2. Instalar Docker (se necessário)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Relogar para aplicar permissões
exit
# Conecte novamente via SSH
```

### 3. Clonar Repositório

```bash
cd ~
git clone <url-do-repositorio>
cd poc_multiagent_lang
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar configurações
nano .env
```

Configure:
```env
# Database (não alterar)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai

# LLM Provider
LLM_TYPE=gemini
GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash
```

Salve com `Ctrl+O`, `Enter`, `Ctrl+X`

### 5. Iniciar Serviços

```bash
# Subir todos os containers
docker compose up -d

# Aguardar inicialização (~30 segundos)
sleep 30

# Verificar status
docker compose ps
```

Você deve ver:
```
NAME                            STATUS
poc_multiagent_lang-backend-1   Up (healthy)
poc_multiagent_lang-frontend-1  Up
poc_multiagent_lang-postgres-1  Up (healthy)
```

### 6. Popular Embeddings do Código

```bash
# Executar script de população
python3 populate-inline.py
```

Saída esperada:
```
✅ Populated 5 files with embeddings
```

### 7. Verificar Funcionamento

```bash
# Testar backend
curl http://localhost:8000/health

# Testar análise completa
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "regulatory_text": "RESOLUÇÃO BCB Nº 789/2024 - Estabelece regras para validação de chaves Pix",
    "repo_path": "/app/fake_pix_repo"
  }' | jq '.change_detected'
```

Deve retornar: `true`

### 8. Acessar Aplicação

- **Frontend**: `http://<seu-ip-ec2>:8501`
- **Backend API Docs**: `http://<seu-ip-ec2>:8000/docs`

## 🔄 Operações Comuns

### Ver Logs

```bash
# Todos os serviços
docker compose logs -f

# Apenas backend
docker compose logs -f backend

# Últimas 50 linhas
docker compose logs backend --tail=50
```

### Restart Serviços

```bash
# Restart completo (NÃO recarrega .env)
docker compose restart

# Restart com reload de .env
docker compose down
docker compose up -d
```

### Rebuild Após Mudanças no Código

```bash
# Rebuild limpo (economiza espaço)
./rebuild-clean.sh

# Rebuild apenas backend
docker compose down backend
docker compose up -d --build backend

# Rebuild apenas frontend
./rebuild-frontend.sh
```

### Atualizar Código do Git

```bash
cd ~/poc_multiagent_lang
git pull origin main
docker compose down
docker compose up -d --build
```

### Verificar Espaço em Disco

```bash
df -h
docker system df
```

### Limpar Espaço

```bash
# Usar script de limpeza completa
./rebuild-clean.sh

# Ou manualmente
docker system prune -af --volumes
```

## 🔧 Configuração Avançada

### Trocar Modelo LLM

#### Para OpenAI

1. Edite `.env`:
```env
LLM_TYPE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

2. Restart:
```bash
docker compose down
docker compose up -d
```

#### Para Outro Modelo Gemini

```env
GEMINI_MODEL=gemini-1.5-pro  # Mais poderoso, mais lento
```

### Adicionar Novo Repositório de Código

1. Copie código para o container:
```bash
docker cp /caminho/local/seu_repo backend:/app/seu_repo
```

2. Edite `populate-inline.py`:
```python
REPO_PATH = "/app/seu_repo"
```

3. Execute:
```bash
python3 populate-inline.py
```

4. Use na API:
```json
{
  "regulatory_text": "...",
  "repo_path": "/app/seu_repo"
}
```

### Configurar Domínio Personalizado

1. Configure DNS apontando para IP do EC2

2. Instale Nginx:
```bash
sudo apt install nginx -y
```

3. Configure reverse proxy:
```bash
sudo nano /etc/nginx/sites-available/regulatory-ai
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

4. Ative:
```bash
sudo ln -s /etc/nginx/sites-available/regulatory-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🐛 Troubleshooting

### Backend não inicia

```bash
# Ver logs
docker compose logs backend --tail=100

# Causas comuns:
# 1. .env não carregado → docker compose down && docker compose up -d
# 2. PostgreSQL não iniciou → docker compose restart postgres
# 3. Porta 8000 ocupada → sudo lsof -i :8000
```

### Frontend em branco

```bash
# Rebuild frontend
docker compose down frontend
docker compose up -d --build frontend

# Ver logs
docker compose logs frontend --tail=50
```

### Gemini API 403/404

```bash
# Verificar chave
cat .env | grep GEMINI_API_KEY

# Gerar nova chave em: https://aistudio.google.com/apikey
# Atualizar .env
nano .env

# Recarregar (IMPORTANTE: down + up, não restart)
docker compose down
docker compose up -d
```

### CodeReader não encontra arquivos

```bash
# Verificar embeddings
./CHECK-EMBEDDINGS.sh

# Se vazio, popular novamente
python3 populate-inline.py

# Verificar logs
docker compose logs backend | grep CodeReader
```

### Sem espaço em disco

```bash
# Limpar tudo
./rebuild-clean.sh

# Ou manualmente
docker system prune -af --volumes
sudo apt clean
sudo journalctl --vacuum-time=3d
```

### Performance lenta

```bash
# Verificar recursos
htop
docker stats

# Causas comuns:
# 1. RAM insuficiente → Upgrade para t3.large (8GB)
# 2. CPU 100% → Trocar para modelo LLM mais leve
# 3. Disco cheio → Limpar com rebuild-clean.sh
```

## 📊 Monitoramento

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# PostgreSQL
docker compose exec postgres pg_isready

# Todos os containers
docker compose ps
```

### Métricas de Performance

```bash
# Recursos por container
docker stats

# Logs de tempo de execução
docker compose logs backend | grep "completed successfully"
```

## 🔒 Segurança

### Recomendações

1. **Não exponha PostgreSQL**: Porta 5432 deve ficar interna
2. **Use HTTPS**: Configure SSL com Let's Encrypt + Nginx
3. **Firewall**: Libere apenas portas necessárias no Security Group
4. **Secrets**: Nunca commite `.env` no Git
5. **Updates**: Mantenha sistema e Docker atualizados

### Configurar HTTPS (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Auto-renovação
sudo certbot renew --dry-run
```

## 📈 Escalabilidade

### Vertical (Mais Recursos)

```bash
# No AWS Console:
# 1. Stop EC2 instance
# 2. Change instance type (ex: t3.large)
# 3. Start instance
# 4. Reconectar e verificar
docker compose ps
```

### Horizontal (Load Balancer)

Para produção real, considere:
- AWS ECS/EKS para orquestração
- RDS PostgreSQL gerenciado
- Application Load Balancer
- Auto Scaling Groups

## 📝 Backup

### Backup Manual

```bash
# Backup do banco
docker compose exec postgres pg_dump -U postgres regulatory_ai > backup.sql

# Backup de embeddings
docker cp backend:/app/fake_pix_repo ./backup_repo

# Backup de configuração
cp .env .env.backup
```

### Restore

```bash
# Restore banco
cat backup.sql | docker compose exec -T postgres psql -U postgres regulatory_ai

# Restore embeddings
docker cp ./backup_repo backend:/app/fake_pix_repo
python3 populate-inline.py
```

## 🎯 Próximos Passos

1. Configure domínio personalizado
2. Adicione HTTPS
3. Configure backup automático
4. Monitore logs e métricas
5. Adicione seus próprios repositórios de código
6. Customize agentes para seu domínio

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique logs: `docker compose logs`
2. Consulte troubleshooting acima
3. Abra issue no repositório
