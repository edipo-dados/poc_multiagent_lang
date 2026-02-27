# Fake Pix Repository

Este é um repositório simulado de serviço Pix para testes de análise de impacto regulatório. Implementa funcionalidades básicas de um sistema de pagamentos Pix do Brasil.

## Propósito

Este repositório fake serve como base de código para o sistema de análise regulatória testar:
- Busca semântica de arquivos relevantes
- Identificação de impactos técnicos
- Geração de especificações de mudanças
- Criação de prompts de desenvolvimento

## Estrutura do Repositório

```
fake_pix_repo/
├── api/                    # Camada de API REST
│   ├── endpoints.py       # Endpoints FastAPI para operações Pix
│   └── schemas.py         # Modelos Pydantic para request/response
├── domain/                 # Camada de domínio
│   ├── models.py          # Entidades de domínio (Account, Pix, Transaction)
│   └── validators.py      # Validadores de regras de negócio
├── services/               # Camada de serviços (vazia no momento)
├── database/               # Camada de persistência
│   └── models.py          # Modelos SQLAlchemy ORM
└── tests/                  # Testes
    └── test_pix_creation.py
```

## Módulos

### api/endpoints.py
Implementa endpoints REST para operações Pix:

**Contas (Accounts)**
- `POST /api/v1/accounts` - Criar nova conta bancária
- `GET /api/v1/accounts/{account_id}` - Consultar conta por ID

**Chaves Pix**
- `POST /api/v1/pix` - Registrar nova chave Pix
- `GET /api/v1/pix/{pix_key}` - Consultar chave Pix

**Transações**
- `POST /api/v1/transactions` - Criar nova transação Pix
- `GET /api/v1/transactions/{transaction_id}` - Consultar transação por ID
- `GET /api/v1/transactions` - Listar todas as transações

### api/schemas.py
Define modelos Pydantic para validação de entrada/saída:
- `AccountCreate`, `AccountResponse` - Dados de conta
- `PixKeyCreate`, `PixKeyResponse` - Dados de chave Pix
- `TransactionCreate`, `TransactionResponse` - Dados de transação
- `ErrorResponse` - Formato de erro padronizado

### domain/models.py
Entidades de domínio principais:

**Account** - Representa uma conta bancária
```python
@dataclass
class Account:
    id: UUID
    account_number: str
    agency: str
    bank_code: str
    holder_name: str
    holder_document: str
    balance: Decimal
    created_at: datetime
```

**Pix** - Representa um registro de chave Pix
```python
@dataclass
class Pix:
    id: UUID
    key: str
    key_type: PixKeyType  # CPF, CNPJ, EMAIL, PHONE, RANDOM
    account_id: UUID
    created_at: datetime
    is_active: bool
```

**Transaction** - Representa uma transação Pix
```python
@dataclass
class Transaction:
    id: UUID
    sender_key: str
    receiver_key: str
    amount: Decimal
    description: str
    status: TransactionStatus  # PENDING, COMPLETED, FAILED, CANCELLED
    created_at: datetime
    completed_at: Optional[datetime]
```

### domain/validators.py
Validadores de regras de negócio:

**Validação de Chaves Pix**
- `validate_cpf(cpf: str)` - Valida formato de CPF
- `validate_cnpj(cnpj: str)` - Valida formato de CNPJ
- `validate_email(email: str)` - Valida formato de email
- `validate_phone(phone: str)` - Valida formato de telefone brasileiro
- `validate_random_key(key: str)` - Valida formato UUID
- `validate_pix_key(key: str, key_type: PixKeyType)` - Validação unificada

**Validação de Transações**
- `validate_transaction_amount(amount: Decimal)` - Valida valor da transação
  - Mínimo: R$ 0,01
  - Máximo: R$ 100.000,00
  - Máximo 2 casas decimais
- `validate_account_balance(balance: Decimal, withdrawal: Decimal)` - Valida saldo suficiente

### database/models.py
Modelos SQLAlchemy para persistência em banco de dados (PostgreSQL).

## Exemplos de Operações Pix

### 1. Criar uma Conta
```python
POST /api/v1/accounts
{
  "account_number": "12345-6",
  "agency": "0001",
  "bank_code": "001",
  "holder_name": "João Silva",
  "holder_document": "12345678901",
  "initial_balance": 1000.00
}
```

### 2. Registrar Chave Pix
```python
POST /api/v1/pix
{
  "key": "joao@email.com",
  "key_type": "email",
  "account_id": "uuid-da-conta"
}
```

### 3. Criar Transação Pix
```python
POST /api/v1/transactions
{
  "sender_key": "joao@email.com",
  "receiver_key": "maria@email.com",
  "amount": 50.00,
  "description": "Pagamento almoço"
}
```

## Tipos de Chave Pix Suportados

1. **CPF** - Documento de pessoa física (11 dígitos)
2. **CNPJ** - Documento de pessoa jurídica (14 dígitos)
3. **EMAIL** - Endereço de email válido
4. **PHONE** - Telefone brasileiro (10 ou 11 dígitos)
5. **RANDOM** - Chave aleatória no formato UUID

## Regras de Negócio Implementadas

### Validações de Chave Pix
- Chave deve estar no formato correto para o tipo especificado
- Chave não pode estar duplicada no sistema
- Conta associada deve existir

### Validações de Transação
- Valor mínimo: R$ 0,01
- Valor máximo: R$ 100.000,00
- Máximo 2 casas decimais
- Chaves de origem e destino devem existir
- Chaves de origem e destino devem ser diferentes

### Validações de Conta
- Documento do titular não pode estar duplicado
- Saldo inicial deve ser não-negativo

## Armazenamento

Atualmente, o sistema usa armazenamento em memória (dicionários Python) para demonstração. Em produção, seria substituído por operações de banco de dados PostgreSQL usando os modelos SQLAlchemy em `database/models.py`.

## Testes

Execute os testes com:
```bash
pytest fake_pix_repo/tests/
```

## Uso no Sistema de Análise Regulatória

Este repositório é indexado pelo sistema de análise regulatória:

1. **Geração de Embeddings**: Todos os arquivos Python são convertidos em vetores semânticos
2. **Armazenamento**: Embeddings são armazenados no PostgreSQL com pgvector
3. **Busca Semântica**: Quando um texto regulatório menciona "Pix", "transações", "validação", etc., o sistema encontra os arquivos relevantes
4. **Análise de Impacto**: O sistema identifica quais arquivos precisam ser modificados para atender à nova regulação

## Extensão

Para adicionar novos arquivos ao repositório:

1. Crie os arquivos Python necessários
2. Execute o script de inicialização de embeddings:
```bash
docker-compose exec backend python scripts/init_embeddings.py
```
3. Os novos arquivos serão indexados e disponíveis para busca semântica
