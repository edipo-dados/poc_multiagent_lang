# Regulatory AI POC

Prova de conceito de arquitetura multi-agente que analisa texto regulatório, identifica impactos em código de serviço Pix, e gera especificações técnicas e prompts para desenvolvimento.

## Visão Geral

O sistema usa LangGraph para orquestração determinística de seis agentes especializados:

1. **Sentinel Agent** - Detecta mudanças e avalia nível de risco
2. **Translator Agent** - Estrutura o texto regulatório em modelo formal
3. **CodeReader Agent** - Identifica arquivos relevantes usando busca semântica
4. **Impact Agent** - Analisa impactos técnicos no código
5. **SpecGenerator Agent** - Gera especificação técnica estruturada
6. **KiroPrompt Agent** - Gera prompt determinístico para desenvolvimento

## Tecnologias

- **Frontend**: Streamlit (interface web Python)
- **Backend**: FastAPI (API assíncrona Python)
- **Orquestração**: LangGraph (fluxo determinístico de agentes)
- **Banco de Dados**: PostgreSQL com pgvector (busca semântica)
- **LLM**: Modelos locais (sem APIs pagas)
- **Deploy**: Docker Compose

## Pré-requisitos

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)

Verifique as instalações:
```bash
docker --version
docker-compose --version
```

## Instalação e Execução

### Início Rápido

1. Clone o repositório:
```bash
git clone <repository-url>
cd regulatory-ai-poc
```

2. Inicie todos os serviços:
```bash
docker-compose up --build
```

Este comando irá:
- Construir as imagens Docker para backend e frontend
- Inicializar o PostgreSQL com extensão pgvector
- Criar as tabelas necessárias (embeddings e audit_logs)
- Iniciar todos os serviços

3. Aguarde até ver as mensagens de inicialização:
```
backend_1   | INFO:     Application startup complete.
frontend_1  | You can now view your Streamlit app in your browser.
postgres_1  | database system is ready to accept connections
```

4. Acesse as interfaces:
   - **Frontend**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **PostgreSQL**: localhost:5432 (usuário: postgres, senha: postgres)

### Parar os Serviços

```bash
docker-compose down
```

Para remover também os volumes (dados do banco):
```bash
docker-compose down -v
```

## Estrutura do Projeto

```
.
├── backend/              # API FastAPI e agentes
│   ├── agents/          # Implementação dos 6 agentes
│   ├── database/        # Modelos e conexão do banco
│   ├── models/          # Modelos de dados Pydantic
│   ├── orchestrator/    # Orquestração LangGraph
│   ├── services/        # Serviços (LLM, embeddings, vector store)
│   ├── scripts/         # Scripts utilitários
│   └── tests/           # Testes unitários e de integração
├── frontend/            # Interface Streamlit
├── fake_pix_repo/       # Repositório fake para testes
└── init.sql            # Script de inicialização do banco
```

## Configuração

### Variáveis de Ambiente

O sistema usa as seguintes variáveis de ambiente (já configuradas no docker-compose.yml):

#### PostgreSQL
- `POSTGRES_DB`: Nome do banco de dados (padrão: `regulatory_ai`)
- `POSTGRES_USER`: Usuário do banco (padrão: `postgres`)
- `POSTGRES_PASSWORD`: Senha do banco (padrão: `postgres`)

#### Backend
- `DATABASE_URL`: URL de conexão com PostgreSQL (padrão: `postgresql://postgres:postgres@postgres:5432/regulatory_ai`)
- `PIX_REPO_PATH`: Caminho para o repositório fake Pix (padrão: `/app/fake_pix_repo`)

#### Frontend
- `BACKEND_URL`: URL do backend (padrão: `http://backend:8000`)

### Personalização

Para alterar as configurações, edite o arquivo `docker-compose.yml` antes de executar `docker-compose up`.

### Portas Utilizadas

- **8501**: Frontend Streamlit
- **8000**: Backend FastAPI
- **5432**: PostgreSQL

Certifique-se de que essas portas estão disponíveis antes de iniciar os serviços.

## Uso

1. Acesse o frontend em http://localhost:8501
2. Cole o texto regulatório na área de texto
3. Clique em "Analisar Impacto"
4. Aguarde o processamento (pode levar alguns segundos)
5. Visualize os resultados em 5 abas:
   - **Modelo Regulatório Estruturado**: JSON com estrutura formal do texto regulatório
   - **Impacto no Código**: Lista de arquivos impactados com análise de severidade
   - **Especificação Técnica**: Documento Markdown com especificação completa
   - **Prompt Final para Desenvolvimento**: Prompt executável para implementação
   - **Fluxo de Execução dos Agentes**: Diagrama Mermaid mostrando o fluxo de execução

## Características

- ✅ Execução 100% local (sem APIs pagas)
- ✅ Orquestração determinística de agentes
- ✅ Busca semântica com pgvector
- ✅ Logs de auditoria completos
- ✅ Visualização do fluxo de agentes
- ✅ Interface web intuitiva

## Troubleshooting

### Porta já em uso
Se alguma porta estiver em uso, você pode alterá-la no `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Altera frontend para porta 8502
```

### Erro de conexão com banco de dados
Aguarde alguns segundos após o `docker-compose up` para que o PostgreSQL inicialize completamente. O backend aguarda automaticamente o health check do banco.

### Reconstruir imagens
Se houver problemas após atualizar o código:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Ver logs de um serviço específico
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Acessar o banco de dados diretamente
```bash
docker-compose exec postgres psql -U postgres -d regulatory_ai
```

## Desenvolvimento

### Executar testes
```bash
cd backend
pytest
```

### Adicionar novos arquivos ao repositório fake Pix
1. Adicione arquivos Python em `fake_pix_repo/`
2. Execute o script de inicialização de embeddings:
```bash
docker-compose exec backend python scripts/init_embeddings.py
```

### Estrutura de dados

O sistema mantém dois tipos de dados no PostgreSQL:

1. **Embeddings**: Vetores semânticos dos arquivos do repositório Pix
2. **Audit Logs**: Histórico completo de todas as análises executadas

Consulte `.kiro/specs/regulatory-ai-poc/` para documentação detalhada de requisitos, design e tarefas.

## API Endpoints

### POST /analyze
Analisa texto regulatório e retorna resultados completos.

**Request:**
```json
{
  "regulatory_text": "string"
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "change_detected": true,
  "risk_level": "high",
  "regulatory_model": {...},
  "impacted_files": [...],
  "impact_analysis": [...],
  "technical_spec": "markdown string",
  "kiro_prompt": "string",
  "graph_visualization": "mermaid string"
}
```

### GET /health
Verifica status dos serviços.

### GET /audit/{execution_id}
Recupera log de auditoria de uma execução específica.

Documentação completa da API: http://localhost:8000/docs

## Licença

Este é um projeto de prova de conceito para fins educacionais.
