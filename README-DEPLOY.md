# 🚀 Guia de Deploy - EC2

## Pré-requisitos no EC2
- Docker instalado ✅
- Docker Compose instalado ✅
- Portas liberadas no Security Group:
  - 22 (SSH)
  - 8000 (Backend)
  - 8501 (Frontend)

## Deploy Inicial

### 1. Conectar ao EC2
```bash
ssh -i sua-chave.pem ubuntu@seu-ip-ec2
```

### 2. Clonar o repositório
```bash
cd ~
git clone https://github.com/edipo-dados/poc_multiagent_lang.git
cd poc_multiagent_lang
```

### 3. Dar permissão ao script de deploy
```bash
chmod +x deploy.sh
```

### 4. Executar deploy
```bash
./deploy.sh
```

## Atualizações Futuras

Quando fizer mudanças no código e quiser atualizar no EC2:

```bash
# No seu PC - fazer push para GitHub
git add .
git commit -m "Descrição das mudanças"
git push origin main

# No EC2 - executar deploy
cd ~/poc_multiagent_lang
./deploy.sh
```

## Comandos Úteis

### Ver logs em tempo real
```bash
docker-compose logs -f
```

### Ver logs de um serviço específico
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart de um serviço
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Parar tudo
```bash
docker-compose down
```

### Limpar tudo e recomeçar
```bash
docker-compose down -v
docker system prune -a -f
./deploy.sh
```

### Ver status dos containers
```bash
docker-compose ps
```

### Testar backend
```bash
curl http://localhost:8000/health
```

## Acessar a Aplicação

- Frontend: `http://SEU-IP-EC2:8501`
- Backend API: `http://SEU-IP-EC2:8000`
- Health Check: `http://SEU-IP-EC2:8000/health`
- API Docs: `http://SEU-IP-EC2:8000/docs`

## Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs backend

# Rebuild forçado
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Erro de memória
```bash
# Limpar recursos não utilizados
docker system prune -a -f
```

### Banco de dados com problema
```bash
# Resetar banco (CUIDADO: apaga dados)
docker-compose down -v
docker-compose up -d
```

## Monitoramento

### Ver uso de recursos
```bash
docker stats
```

### Ver espaço em disco
```bash
df -h
docker system df
```

## Backup

### Backup do banco de dados
```bash
docker-compose exec postgres pg_dump -U postgres regulatory_ai > backup.sql
```

### Restaurar backup
```bash
cat backup.sql | docker-compose exec -T postgres psql -U postgres regulatory_ai
```
