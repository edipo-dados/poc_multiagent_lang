# Deploy Otimizado no EC2

## Requisitos Mínimos
- **Disco**: 15GB (reduzido de 30GB)
- **RAM**: 2GB
- **CPU**: 1 vCPU
- **Instância recomendada**: t3.small ou t3a.small

## Otimizações Aplicadas

### 1. PyTorch CPU-only
- Versão CUDA: ~5GB
- Versão CPU: ~200MB
- **Economia: 4.8GB**

### 2. Requirements de Produção
- Removidas dependências de desenvolvimento
- Removidos pytest, hypothesis, etc
- **Economia: ~500MB**

### 3. Dockerfile Otimizado
- Usa `--no-cache-dir` para não guardar cache do pip
- Remove arquivos temporários do apt
- **Economia: ~1GB**

## Passo a Passo

### 1. Preparar EC2
```bash
# Conectar na instância
ssh -i sua-chave.pem ubuntu@seu-ip

# Atualizar sistema
sudo apt update
sudo apt install -y docker.io docker-compose git

# Adicionar usuário ao grupo docker
sudo usermod -aG docker ubuntu
newgrp docker
```

### 2. Clonar Repositório
```bash
git clone https://github.com/edipo-dados/poc_multiagent_lang.git
cd poc_multiagent_lang
```

### 3. Configurar Variáveis
```bash
# Criar .env
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
EOF
```

### 4. Build Otimizado
```bash
# Build apenas o necessário
docker compose build --no-cache backend

# Verificar tamanho da imagem
docker images | grep backend
# Deve ser ~2GB ao invés de ~7GB
```

### 5. Iniciar Serviços
```bash
# Subir PostgreSQL primeiro
docker compose up -d postgres

# Aguardar inicialização
sleep 10

# Subir backend
docker compose up -d backend

# Subir frontend
docker compose up -d frontend
```

### 6. Popular Embeddings
```bash
# Executar script de inicialização
docker compose exec backend python backend/scripts/init_embeddings.py
```

### 7. Verificar
```bash
# Ver logs
docker compose logs -f backend

# Testar API
curl http://localhost:8000/health

# Acessar frontend
# http://seu-ip:8501
```

## Monitoramento de Espaço

### Verificar uso de disco
```bash
df -h
docker system df
```

### Limpar se necessário
```bash
# Remover imagens não usadas
docker image prune -a

# Remover volumes não usados
docker volume prune

# Limpar tudo (cuidado!)
docker system prune -a --volumes
```

## Troubleshooting

### Se ficar sem espaço durante build
```bash
# Limpar antes de buildar
docker system prune -a --volumes

# Build com menos camadas
docker compose build --no-cache --compress backend
```

### Se o build falhar
```bash
# Ver logs detalhados
docker compose build --progress=plain backend

# Tentar build em etapas
docker compose build postgres
docker compose build backend
docker compose build frontend
```

## Estimativa de Uso de Disco

| Componente | Tamanho |
|------------|---------|
| Sistema Base Ubuntu | 2GB |
| Docker | 500MB |
| PostgreSQL Image | 300MB |
| Backend Image (otimizado) | 2GB |
| Frontend Image | 500MB |
| Volumes (dados) | 500MB |
| **Total** | **~6GB** |
| **Margem de segurança** | +4GB |
| **Recomendado** | **15GB** |

## Alternativa: Deploy Sem Docker

Se ainda assim ficar sem espaço, pode rodar direto no Ubuntu:

```bash
# Instalar Python e PostgreSQL
sudo apt install -y python3.11 python3-pip postgresql postgresql-contrib

# Instalar pgvector
sudo apt install -y postgresql-14-pgvector

# Instalar dependências Python
pip install -r backend/requirements-prod.txt

# Configurar e rodar
# (ver README-LOCAL.md)
```

## Custos AWS

### Instâncias Recomendadas
- **t3.small**: $0.0208/hora (~$15/mês)
- **t3a.small**: $0.0188/hora (~$14/mês)
- **t3.medium**: $0.0416/hora (~$30/mês) - se precisar mais RAM

### Storage
- **15GB EBS gp3**: ~$1.20/mês
- **20GB EBS gp3**: ~$1.60/mês

**Total estimado: $16-32/mês**
