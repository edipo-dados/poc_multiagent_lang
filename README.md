# 🤖 POC Multi-Agent Regulatory AI

Sistema multi-agente para análise automatizada de mudanças regulatórias e geração de especificações técnicas de implementação.

## 📋 Visão Geral

Esta POC demonstra um pipeline de 6 agentes especializados que trabalham em sequência para:

1. **Detectar mudanças** em textos regulatórios
2. **Extrair modelo estruturado** das regras
3. **Identificar código impactado** via busca semântica
4. **Analisar impactos** em cada arquivo
5. **Gerar especificação técnica** de implementação
6. **Criar prompt** para desenvolvimento

## 🏗️ Arquitetura

### Stack Tecnológico

- **Backend**: FastAPI + LangGraph
- **Frontend**: Streamlit
- **Database**: PostgreSQL + pgvector
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Orquestração**: Docker Compose

### Agentes

```mermaid
graph LR
    Input[Texto Regulatório] --> Sentinel[1. Sentinel]
    Sentinel --> Translator[2. Translator]
    Translator --> CodeReader[3. CodeReader]
    CodeReader --> Impact[4. Impact]
    Impact --> SpecGen[5. SpecGenerator]
    SpecGen --> KiroPrompt[6. KiroPrompt]
    KiroPrompt --> Output[Prompt Final]
```

1. **Sentinel Agent**: Detecta se há mudança regulatória e avalia nível de risco
2. **Translator Agent**: Extrai modelo estruturado (título, descrição, requisitos)
3. **CodeReader Agent**: Busca arquivos de código relevantes via embeddings
4. **Impact Agent**: Analisa impacto específico em cada arquivo
5. **SpecGenerator Agent**: Gera especificação técnica de implementação
6. **KiroPrompt Agent**: Cria prompt final para desenvolvimento

## 🚀 Deploy Rápido (AWS EC2)

### Pré-requisitos

- EC2 instance (mínimo: t3.medium, 4GB RAM)
- Ubuntu 22.04+
- Docker + Docker Compose instalados
- Chave API do Google Gemini

### Passos

1. **Clone o repositório**
```bash
git clone <repo-url>
cd poc_multiagent_lang
```

2. **Configure variáveis de ambiente**
```bash
cp .env.example .env
nano .env
```

Edite:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/regulatory_ai
LLM_TYPE=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

3. **Inicie os serviços**
```bash
docker compose up -d
```

4. **Popule embeddings do código**
```bash
python3 populate-inline.py
```

5. **Acesse a aplicação**
- Frontend: `http://<seu-ip>:8501`
- Backend API: `http://<seu-ip>:8000/docs`

## 📖 Uso

### Via Frontend (Streamlit)

1. Acesse `http://<seu-ip>:8501`
2. (Opcional) Insira sua chave API do Gemini
3. Cole o texto regulatório
4. Clique em "Analisar"
5. Visualize os resultados em 5 abas:
   - Modelo Regulatório Estruturado
   - Impacto no Código
   - Especificação Técnica
   - Prompt Final
   - Fluxo de Execução (diagrama Mermaid)

### Via API (curl)

```bash
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -H 'X-Gemini-API-Key: sua_chave_aqui' \
  -d '{
    "regulatory_text": "RESOLUÇÃO BCB Nº 789/2024 - Estabelece regras para validação de chaves Pix",
    "repo_path": "/app/fake_pix_repo"
  }'
```

## 🛠️ Scripts Úteis

### Rebuild Limpo (economiza espaço em disco)
```bash
./rebuild-clean.sh
```

Remove containers, imagens, volumes e cache antes de rebuildar.

### Rebuild apenas Frontend
```bash
./rebuild-frontend.sh
```

### Verificar Status
```bash
./check-status.sh
```

### Verificar Embeddings
```bash
./CHECK-EMBEDDINGS.sh
```

## 📁 Estrutura do Projeto

```
.
├── backend/
│   ├── agents/           # 6 agentes especializados
│   ├── database/         # Modelos e conexão
│   ├── models/           # Pydantic models
│   ├── orchestrator/     # LangGraph workflow
│   ├── scripts/          # Scripts de setup
│   ├── services/         # LLM, embeddings, vector store
│   └── tests/            # Testes unitários e integração
├── frontend/
│   └── app.py            # Interface Streamlit
├── fake_pix_repo/        # Repositório exemplo (Pix)
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuração Avançada

### Trocar Modelo LLM

Edite `.env`:
```env
# Gemini (padrão)
LLM_TYPE=gemini
GEMINI_API_KEY=sua_chave
GEMINI_MODEL=gemini-2.5-flash

# OpenAI (alternativa)
LLM_TYPE=openai
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-4
```

Depois:
```bash
docker compose down
docker compose up -d
```

### Adicionar Novo Repositório

1. Copie seu código para dentro do container:
```bash
docker cp /caminho/local backend:/app/seu_repo
```

2. Popule embeddings:
```python
# Edite populate-inline.py
REPO_PATH = "/app/seu_repo"
```

3. Execute:
```bash
python3 populate-inline.py
```

## 🧪 Testes

```bash
# Todos os testes
cd backend
pytest

# Testes específicos
pytest tests/test_orchestrator.py
pytest tests/integration/test_e2e.py

# Com coverage
pytest --cov=. --cov-report=html
```

## 📊 Performance

- **Tempo médio de análise**: 15-20 segundos
- **Sentinel**: ~2s
- **Translator**: ~3s
- **CodeReader**: ~2s
- **Impact**: ~5s (depende do número de arquivos)
- **SpecGen**: ~2s
- **KiroPrompt**: ~1s

## ⚠️ Limitações Conhecidas

1. **CodeReader**: Busca semântica pode não encontrar matches se:
   - Texto regulatório muito diferente do código
   - Código sem comentários/docstrings
   - Threshold de similaridade muito alto

2. **Gemini API**: 
   - Requer chave válida (free tier: 15 RPM)
   - Thinking mode usa tokens internos (precisa max_tokens >= 100)

3. **Recursos**:
   - Mínimo 4GB RAM
   - ~10GB espaço em disco

## 🐛 Troubleshooting

### Backend não inicia
```bash
docker compose logs backend --tail=50
```

Causas comuns:
- `.env` não carregado (use `docker compose down` + `up`, não `restart`)
- Porta 8000 em uso
- PostgreSQL não iniciou

### Frontend em branco
```bash
docker compose down frontend
docker compose up -d --build frontend
```

### Embeddings vazios
```bash
./CHECK-EMBEDDINGS.sh
```

Se vazio, execute:
```bash
python3 populate-inline.py
```

### Gemini API 403/404
- Verifique se a chave está válida
- Gere nova chave em: https://aistudio.google.com/apikey
- Atualize `.env` e faça `docker compose down` + `up`

## 📝 Licença

MIT

## 🤝 Contribuindo

PRs são bem-vindos! Para mudanças grandes, abra uma issue primeiro.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
