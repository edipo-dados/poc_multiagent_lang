# 🏠 Executar Localmente (Windows)

## Pré-requisitos

1. **Python 3.11+** instalado
2. **PostgreSQL** instalado e rodando (ou use SQLite para testes)
3. **Git** instalado

## Setup Rápido

### 1. Instalar Dependências

```bash
# Execute o script de setup
run-local.bat
```

Isso vai:
- Criar ambiente virtual
- Instalar todas as dependências
- Configurar o ambiente

### 2. Configurar Banco de Dados

**Opção A - PostgreSQL (Recomendado):**

```sql
-- Criar banco de dados
CREATE DATABASE regulatory_ai;

-- Habilitar extensão pgvector
CREATE EXTENSION vector;
```

**Opção B - SQLite (Para testes rápidos):**

Edite `backend/database/connection.py` e mude para SQLite:
```python
DATABASE_URL = "sqlite+aiosqlite:///./regulatory_ai.db"
```

### 3. Iniciar Aplicação

**Terminal 1 - Backend:**
```bash
run-backend.bat
```

**Terminal 2 - Frontend:**
```bash
run-frontend.bat
```

## Acessar

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Desenvolvimento

### Estrutura de Pastas
```
backend/
  ├── venv/           # Ambiente virtual Python
  ├── agents/         # Agentes LangGraph
  ├── database/       # Modelos e conexão DB
  ├── services/       # Serviços (embeddings, vector store)
  ├── orchestrator/   # Orquestrador principal
  └── main.py         # FastAPI app

frontend/
  ├── venv/           # Ambiente virtual Python
  └── app.py          # Streamlit app
```

### Comandos Úteis

```bash
# Ativar ambiente virtual do backend
cd backend
venv\Scripts\activate.bat

# Rodar testes
pytest

# Verificar código
python -m pylint agents/

# Desativar ambiente virtual
deactivate
```

## Troubleshooting

### Erro: "No module named 'backend'"

Certifique-se de estar no diretório correto e que o PYTHONPATH está configurado:
```bash
set PYTHONPATH=%CD%
```

### Erro: PostgreSQL não conecta

Verifique se o PostgreSQL está rodando:
```bash
pg_isready -h localhost -p 5432
```

Se não estiver, inicie o serviço:
```bash
# Windows Services
services.msc
# Procure por "PostgreSQL" e inicie
```

### Erro: Porta já em uso

Mude a porta no script:
```bash
# Backend
python -m uvicorn main:app --reload --port 8001

# Frontend
streamlit run app.py --server.port 8502
```

## Performance

Para melhor performance local:
- Use SSD
- Mínimo 8GB RAM
- Python 3.11+ (mais rápido)

## Próximos Passos

1. Configure variáveis de ambiente em `.env`
2. Adicione sua API key do OpenAI/Anthropic
3. Teste os endpoints em http://localhost:8000/docs
4. Desenvolva novos agentes em `backend/agents/`
