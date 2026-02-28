# 💻 Desenvolvimento Local (Windows)

Guia para rodar a POC Multi-Agent Regulatory AI localmente no Windows.

## 📋 Pré-requisitos

### Software Necessário

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - ✅ Marque "Add Python to PATH" na instalação

2. **PostgreSQL 15+** (ou use SQLite para testes)
   - Download: https://www.postgresql.org/download/windows/
   - Durante instalação, anote usuário/senha

3. **Git**
   - Download: https://git-scm.com/download/win

4. **Google Gemini API Key**
   - Gratuita: https://aistudio.google.com/apikey

## 🚀 Setup Rápido

### 1. Clonar Repositório

```bash
git clone <url-do-repositorio>
cd poc_multiagent_lang
```

### 2. Criar Ambiente Virtual

```bash
# Criar venv
python -m venv venv

# Ativar (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar (CMD)
.\venv\Scripts\activate.bat
```

### 3. Instalar Dependências

```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
pip install -r requirements.txt
cd ..
```

### 4. Configurar Banco de Dados

#### Opção A: PostgreSQL (Recomendado)

```bash
# Criar banco
psql -U postgres
CREATE DATABASE regulatory_ai;
\q

# Configurar .env
copy .env.example .env
notepad .env
```

Edite `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:sua_senha@localhost:5432/regulatory_ai
LLM_TYPE=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

#### Opção B: SQLite (Mais Simples)

Edite `.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./regulatory_ai.db
LLM_TYPE=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Criar Tabelas

```bash
cd backend
python scripts/create_database.py
cd ..
```

### 6. Popular Embeddings

```bash
python populate-inline.py
```

### 7. Iniciar Serviços

#### Terminal 1 - Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend

```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 8. Acessar Aplicação

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs

## 🔧 Scripts Batch (Atalhos)

### run-backend.bat

```batch
@echo off
cd backend
call ..\venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### run-frontend.bat

```batch
@echo off
cd frontend
call ..\venv\Scripts\activate.bat
streamlit run app.py --server.port 8501
```

### run-all-local.bat

```batch
@echo off
echo Starting Backend...
start cmd /k "cd backend && call ..\venv\Scripts\activate.bat && uvicorn main:app --reload"

timeout /t 5

echo Starting Frontend...
start cmd /k "cd frontend && call ..\venv\Scripts\activate.bat && streamlit run app.py"

echo.
echo ✅ Services started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
```

## 🧪 Testes

```bash
# Ativar venv
.\venv\Scripts\activate

# Rodar todos os testes
cd backend
pytest

# Testes específicos
pytest tests/test_orchestrator.py
pytest tests/integration/test_e2e.py

# Com coverage
pytest --cov=. --cov-report=html
```

## 🐛 Troubleshooting

### Erro: "Python não encontrado"

```bash
# Verificar instalação
python --version

# Se não funcionar, reinstale Python marcando "Add to PATH"
```

### Erro: "psycopg2 não instala"

```bash
# Use versão binária
pip install psycopg2-binary
```

### Erro: "asyncpg não conecta"

```bash
# Verificar PostgreSQL rodando
# Windows Services → PostgreSQL → Start

# Testar conexão
psql -U postgres -h localhost
```

### Erro: "ModuleNotFoundError"

```bash
# Verificar venv ativado
# Deve aparecer (venv) no prompt

# Reinstalar dependências
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Frontend não carrega

```bash
# Verificar porta 8501 livre
netstat -ano | findstr :8501

# Se ocupada, matar processo
taskkill /PID <pid> /F

# Ou usar porta diferente
streamlit run app.py --server.port 8502
```

### Backend erro 500

```bash
# Ver logs detalhados
# No terminal do backend, procure stack trace

# Causas comuns:
# 1. .env não carregado → Verificar arquivo existe
# 2. Banco não criado → Rodar create_database.py
# 3. Gemini API inválida → Gerar nova chave
```

## 🔄 Desenvolvimento

### Hot Reload

- **Backend**: `--reload` já ativa hot reload
- **Frontend**: Streamlit recarrega automaticamente

### Adicionar Dependências

```bash
# Backend
cd backend
pip install nova-lib
pip freeze > requirements.txt

# Frontend
cd frontend
pip install nova-lib
pip freeze > requirements.txt
```

### Debugar com VSCode

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Frontend",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "app.py"],
      "cwd": "${workspaceFolder}/frontend"
    }
  ]
}
```

## 📝 Estrutura de Arquivos

```
poc_multiagent_lang/
├── backend/
│   ├── agents/              # 6 agentes
│   ├── database/            # Conexão e modelos
│   ├── models/              # Pydantic schemas
│   ├── orchestrator/        # LangGraph workflow
│   ├── scripts/             # Setup scripts
│   ├── services/            # LLM, embeddings, vector
│   ├── tests/               # Testes
│   ├── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit UI
│   └── requirements.txt
├── fake_pix_repo/           # Código exemplo
├── .env                     # Configuração (não commitar!)
├── .env.example             # Template
├── populate-inline.py       # Popular embeddings
└── README.md
```

## 🎯 Próximos Passos

1. Explore a API em http://localhost:8000/docs
2. Teste diferentes textos regulatórios
3. Adicione seu próprio repositório de código
4. Customize agentes em `backend/agents/`
5. Rode testes: `pytest`

## 📚 Recursos

- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Gemini API**: https://ai.google.dev/docs

## 💡 Dicas

1. Use SQLite para desenvolvimento rápido
2. PostgreSQL para testar busca vetorial
3. Ative venv antes de rodar comandos
4. Use scripts .bat para facilitar
5. Consulte logs para debugar

## 🔒 Segurança

- Nunca commite `.env` no Git
- Use `.env.example` como template
- Gere chaves API separadas para dev/prod
- Mantenha dependências atualizadas: `pip list --outdated`
