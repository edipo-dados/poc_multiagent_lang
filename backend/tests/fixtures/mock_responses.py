"""
Mock responses for testing agents and services.

Contains mock data for:
- LLM responses from each agent
- Vector search results
- Database responses
"""

from datetime import datetime, UTC
from backend.models.regulatory import RegulatoryModel
from backend.models.impact import ImpactedFile, Impact


# ============================================================================
# SENTINEL AGENT MOCK RESPONSES
# ============================================================================

MOCK_SENTINEL_RESPONSE = {
    "change_detected": True,
    "risk_level": "high",
    "reasoning": "Detected mandatory security requirements for Pix transactions with specific deadline"
}

MOCK_SENTINEL_NO_CHANGE = {
    "change_detected": False,
    "risk_level": "low",
    "reasoning": "Text is informational only, no regulatory changes detected"
}

MOCK_SENTINEL_MEDIUM_RISK = {
    "change_detected": True,
    "risk_level": "medium",
    "reasoning": "Optional improvements suggested but not mandatory"
}


# ============================================================================
# TRANSLATOR AGENT MOCK RESPONSES
# ============================================================================

MOCK_TRANSLATOR_RESPONSE = {
    "title": "Validação de CPF/CNPJ para transações Pix",
    "description": "Resolução que estabelece validação obrigatória de documentos CPF/CNPJ para transações Pix acima de R$ 5.000,00",
    "requirements": [
        "Implementar validação de CPF/CNPJ para transações acima de R$ 5.000,00",
        "Verificar autenticidade do documento junto à Receita Federal",
        "Rejeitar transações com documentos inválidos"
    ],
    "deadlines": [
        {
            "date": "2024-12-31",
            "description": "Prazo final para implementação da validação"
        }
    ],
    "affected_systems": ["Pix", "validação", "pagamentos"]
}

MOCK_TRANSLATOR_COMPLEX_RESPONSE = {
    "title": "Requisitos de segurança para transações Pix",
    "description": "Resolução abrangente estabelecendo múltiplos requisitos de segurança, autenticação multifator e limites transacionais para o sistema Pix",
    "requirements": [
        "Implementar autenticação multifator para transações de alto valor",
        "Análise de comportamento do usuário em tempo real",
        "Bloqueio temporário de transações suspeitas",
        "Notificação imediata ao usuário sobre transações bloqueadas",
        "Confirmação adicional para transações noturnas acima de R$ 5.000,00",
        "Registro detalhado de todas as tentativas de transação"
    ],
    "deadlines": [
        {
            "date": "2024-10-17",
            "description": "Prazo de 180 dias para adequação completa aos requisitos"
        }
    ],
    "affected_systems": ["Pix", "autenticação", "segurança", "notificações", "auditoria"]
}

MOCK_TRANSLATOR_QR_CODE_RESPONSE = {
    "title": "Alteração em requisitos de QR Code dinâmico Pix",
    "description": "Resolução que modifica os campos obrigatórios para geração de QR Codes dinâmicos em transações Pix",
    "requirements": [
        "Incluir identificador único da transação (txid) no QR Code",
        "Incluir valor da transação em centavos",
        "Incluir chave Pix, nome e cidade do recebedor",
        "Incluir timestamp de geração e prazo de validade (máximo 24 horas)",
        "Seguir padrão EMV QR Code",
        "Validar todos os campos obrigatórios nas APIs",
        "Retornar erro específico para QR Codes expirados"
    ],
    "deadlines": [
        {
            "date": "2024-11-01",
            "description": "Entrada em vigor da resolução"
        },
        {
            "date": "2024-10-31",
            "description": "Prazo de 60 dias para adequação dos sistemas"
        }
    ],
    "affected_systems": ["Pix", "QR Code", "API", "validação"]
}


# ============================================================================
# CODEREADER AGENT MOCK RESPONSES
# ============================================================================

MOCK_CODEREADER_RESPONSE = [
    {
        "file_path": "fake_pix_repo/domain/validators.py",
        "relevance_score": 0.92,
        "snippet": "def validate_cpf(cpf: str) -> bool:\n    \"\"\"Validate CPF format and check digit.\"\"\"\n    cpf = re.sub(r'[^0-9]', '', cpf)\n    if len(cpf) != 11:\n        return False"
    },
    {
        "file_path": "fake_pix_repo/api/endpoints.py",
        "relevance_score": 0.87,
        "snippet": "@router.post(\"/pix/transfer\")\nasync def create_pix_transfer(\n    transfer: PixTransferRequest,\n    db: Session = Depends(get_db)\n) -> PixTransferResponse:"
    },
    {
        "file_path": "fake_pix_repo/services/pix_service.py",
        "relevance_score": 0.85,
        "snippet": "class PixService:\n    def __init__(self, db: Session):\n        self.db = db\n    \n    async def process_transfer(self, transfer_data: dict) -> dict:"
    }
]

MOCK_CODEREADER_QR_CODE_RESPONSE = [
    {
        "file_path": "fake_pix_repo/services/qr_code_generator.py",
        "relevance_score": 0.95,
        "snippet": "def generate_dynamic_qr_code(transaction_data: dict) -> str:\n    \"\"\"Generate EMV-compliant dynamic QR code for Pix transaction.\"\"\"\n    payload = {\n        'merchant_name': transaction"
    },
    {
        "file_path": "fake_pix_repo/api/schemas.py",
        "relevance_score": 0.88,
        "snippet": "class QRCodeRequest(BaseModel):\n    amount: Decimal\n    pix_key: str\n    description: Optional[str] = None\n    expiration_minutes: int = 30"
    },
    {
        "file_path": "fake_pix_repo/domain/qr_code_validator.py",
        "relevance_score": 0.82,
        "snippet": "def validate_qr_code_payload(payload: dict) -> bool:\n    \"\"\"Validate QR code payload structure and required fields.\"\"\"\n    required_fields = ['amount', 'pix_key"
    }
]

MOCK_CODEREADER_EMPTY_RESPONSE = []


# ============================================================================
# IMPACT AGENT MOCK RESPONSES
# ============================================================================

MOCK_IMPACT_RESPONSE = [
    {
        "file_path": "fake_pix_repo/domain/validators.py",
        "impact_type": "validation",
        "severity": "high",
        "description": "A função validate_cpf precisa ser estendida para consultar a Receita Federal em tempo real, não apenas validar o formato. Atualmente apenas valida dígitos verificadores.",
        "suggested_changes": [
            "Adicionar integração com API da Receita Federal",
            "Implementar cache de consultas para otimização",
            "Adicionar tratamento de timeout e fallback",
            "Criar testes para validação online de CPF"
        ]
    },
    {
        "file_path": "fake_pix_repo/api/endpoints.py",
        "impact_type": "business_logic",
        "severity": "high",
        "description": "O endpoint create_pix_transfer precisa adicionar validação de valor mínimo (R$ 5.000,00) antes de chamar a validação de CPF da Receita Federal.",
        "suggested_changes": [
            "Adicionar verificação de valor da transação",
            "Chamar validação de CPF apenas se valor > R$ 5.000,00",
            "Retornar erro específico se CPF inválido",
            "Atualizar documentação da API com novo requisito"
        ]
    },
    {
        "file_path": "fake_pix_repo/services/pix_service.py",
        "impact_type": "business_logic",
        "severity": "medium",
        "description": "O método process_transfer deve incorporar a lógica de validação de CPF para transações de alto valor antes de processar a transferência.",
        "suggested_changes": [
            "Adicionar chamada ao validador de CPF",
            "Implementar lógica de retry em caso de falha na consulta",
            "Adicionar logging de validações realizadas",
            "Atualizar métricas para incluir taxa de rejeição por CPF inválido"
        ]
    }
]

MOCK_IMPACT_QR_CODE_RESPONSE = [
    {
        "file_path": "fake_pix_repo/services/qr_code_generator.py",
        "impact_type": "business_logic",
        "severity": "high",
        "description": "A função generate_dynamic_qr_code precisa ser atualizada para incluir todos os campos obrigatórios: txid, timestamp, prazo de validade e seguir padrão EMV.",
        "suggested_changes": [
            "Adicionar campo txid (identificador único) ao payload",
            "Incluir timestamp de geração no formato ISO 8601",
            "Adicionar campo de expiração (máximo 24 horas)",
            "Validar conformidade com padrão EMV QR Code",
            "Adicionar cidade do recebedor ao payload"
        ]
    },
    {
        "file_path": "fake_pix_repo/api/schemas.py",
        "impact_type": "schema_change",
        "severity": "medium",
        "description": "O schema QRCodeRequest precisa incluir novos campos obrigatórios e validar prazo de validade máximo de 24 horas.",
        "suggested_changes": [
            "Adicionar campo receiver_city como obrigatório",
            "Adicionar validação de expiration_minutes <= 1440 (24 horas)",
            "Adicionar campo txid gerado automaticamente",
            "Atualizar documentação do schema"
        ]
    },
    {
        "file_path": "fake_pix_repo/domain/qr_code_validator.py",
        "impact_type": "validation",
        "severity": "high",
        "description": "O validador precisa verificar todos os novos campos obrigatórios e retornar erro específico para QR Codes expirados.",
        "suggested_changes": [
            "Adicionar validação de txid (formato UUID)",
            "Validar presença de timestamp e expiração",
            "Implementar verificação de QR Code expirado",
            "Retornar código de erro específico para expiração",
            "Validar conformidade com padrão EMV"
        ]
    }
]

MOCK_IMPACT_LOW_SEVERITY_RESPONSE = [
    {
        "file_path": "fake_pix_repo/utils/logging.py",
        "impact_type": "business_logic",
        "severity": "low",
        "description": "Adicionar logging adicional para auditoria de validações de CPF conforme requisitos regulatórios.",
        "suggested_changes": [
            "Incluir log de todas as consultas à Receita Federal",
            "Adicionar timestamp e resultado da validação",
            "Implementar retenção de logs por 5 anos"
        ]
    }
]


# ============================================================================
# SPEC GENERATOR AGENT MOCK RESPONSES
# ============================================================================

MOCK_SPEC_GENERATOR_RESPONSE = """# Especificação Técnica: Validação de CPF/CNPJ para Transações Pix

## 1. Visão Geral
Implementar validação obrigatória de CPF/CNPJ junto à Receita Federal para transações Pix acima de R$ 5.000,00.

## 2. Requisitos Funcionais

### 2.1 Validação de Documento
- Transações acima de R$ 5.000,00 devem validar CPF/CNPJ em tempo real
- Consulta deve ser feita à API da Receita Federal
- Transações com documentos inválidos devem ser rejeitadas

### 2.2 Performance
- Timeout de 5 segundos para consulta à Receita Federal
- Cache de resultados por 24 horas
- Fallback em caso de indisponibilidade da API

## 3. Arquivos Impactados

### 3.1 fake_pix_repo/domain/validators.py
**Severidade:** Alta
**Mudanças:**
- Adicionar integração com API da Receita Federal
- Implementar cache de consultas
- Adicionar tratamento de timeout

### 3.2 fake_pix_repo/api/endpoints.py
**Severidade:** Alta
**Mudanças:**
- Adicionar verificação de valor da transação
- Chamar validação apenas se valor > R$ 5.000,00
- Retornar erro específico para CPF inválido

### 3.3 fake_pix_repo/services/pix_service.py
**Severidade:** Média
**Mudanças:**
- Incorporar lógica de validação de CPF
- Implementar retry em caso de falha
- Adicionar logging de validações

## 4. Prazo
**Deadline:** 31 de dezembro de 2024

## 5. Testes Necessários
- Teste de integração com API da Receita Federal
- Teste de timeout e fallback
- Teste de cache
- Teste de rejeição de CPF inválido
"""

MOCK_SPEC_GENERATOR_QR_CODE_RESPONSE = """# Especificação Técnica: Atualização de QR Code Dinâmico Pix

## 1. Visão Geral
Atualizar geração de QR Codes dinâmicos para incluir novos campos obrigatórios e seguir padrão EMV.

## 2. Requisitos Funcionais

### 2.1 Campos Obrigatórios
- txid: identificador único (UUID)
- valor em centavos
- chave Pix do recebedor
- nome e cidade do recebedor
- timestamp de geração (ISO 8601)
- prazo de validade (máximo 24 horas)

### 2.2 Validação
- Validar formato EMV QR Code
- Rejeitar QR Codes expirados com erro específico
- Validar todos os campos obrigatórios

## 3. Arquivos Impactados

### 3.1 fake_pix_repo/services/qr_code_generator.py
**Severidade:** Alta
**Mudanças:**
- Adicionar todos os campos obrigatórios
- Implementar padrão EMV
- Adicionar validação de expiração

### 3.2 fake_pix_repo/api/schemas.py
**Severidade:** Média
**Mudanças:**
- Adicionar campo receiver_city
- Validar expiration_minutes <= 1440
- Adicionar campo txid

### 3.3 fake_pix_repo/domain/qr_code_validator.py
**Severidade:** Alta
**Mudanças:**
- Validar novos campos obrigatórios
- Verificar QR Code expirado
- Validar conformidade EMV

## 4. Prazo
**Deadline:** 1º de novembro de 2024

## 5. Testes Necessários
- Teste de geração com todos os campos
- Teste de validação EMV
- Teste de expiração de QR Code
- Teste de erro para campos faltantes
"""


# ============================================================================
# KIRO PROMPT AGENT MOCK RESPONSES
# ============================================================================

MOCK_KIRO_PROMPT_RESPONSE = """Implementar validação de CPF/CNPJ para transações Pix acima de R$ 5.000,00:

1. Atualizar fake_pix_repo/domain/validators.py:
   - Adicionar função validate_cpf_receita_federal() que consulta API da Receita Federal
   - Implementar cache Redis com TTL de 24 horas
   - Adicionar timeout de 5 segundos e fallback

2. Atualizar fake_pix_repo/api/endpoints.py:
   - No endpoint create_pix_transfer, adicionar verificação: if transfer.amount > 5000, chamar validação
   - Retornar erro 400 com mensagem "CPF/CNPJ inválido" se validação falhar

3. Atualizar fake_pix_repo/services/pix_service.py:
   - No método process_transfer, adicionar chamada ao validador antes de processar
   - Implementar retry com backoff exponencial (3 tentativas)
   - Adicionar logging de todas as validações

4. Criar testes:
   - test_cpf_validation_above_threshold.py
   - test_cpf_validation_cache.py
   - test_cpf_validation_timeout.py

Prazo: 31 de dezembro de 2024
"""

MOCK_KIRO_PROMPT_QR_CODE_RESPONSE = """Atualizar geração de QR Code dinâmico Pix para incluir novos campos obrigatórios:

1. Atualizar fake_pix_repo/services/qr_code_generator.py:
   - Adicionar campos: txid (UUID), timestamp (ISO 8601), expiration, receiver_city
   - Implementar validação de padrão EMV QR Code
   - Adicionar verificação de expiração máxima de 24 horas

2. Atualizar fake_pix_repo/api/schemas.py:
   - Adicionar campo receiver_city: str como obrigatório
   - Adicionar validação: expiration_minutes <= 1440
   - Adicionar campo txid gerado automaticamente (UUID4)

3. Atualizar fake_pix_repo/domain/qr_code_validator.py:
   - Adicionar validação de todos os novos campos
   - Implementar verificação de QR Code expirado (comparar timestamp + expiration com now)
   - Retornar erro específico "QR_CODE_EXPIRED" se expirado

4. Criar testes:
   - test_qr_code_new_fields.py
   - test_qr_code_expiration.py
   - test_qr_code_emv_compliance.py

Prazo: 1º de novembro de 2024
"""


# ============================================================================
# VECTOR SEARCH MOCK RESULTS
# ============================================================================

MOCK_VECTOR_SEARCH_RESULTS = [
    {
        "id": "file_1",
        "score": 0.92,
        "metadata": {
            "file_path": "fake_pix_repo/domain/validators.py",
            "content": "def validate_cpf(cpf: str) -> bool:\n    \"\"\"Validate CPF format and check digit.\"\"\"\n    cpf = re.sub(r'[^0-9]', '', cpf)\n    if len(cpf) != 11:\n        return False\n    # Check digit validation logic\n    return True"
        }
    },
    {
        "id": "file_2",
        "score": 0.87,
        "metadata": {
            "file_path": "fake_pix_repo/api/endpoints.py",
            "content": "@router.post(\"/pix/transfer\")\nasync def create_pix_transfer(\n    transfer: PixTransferRequest,\n    db: Session = Depends(get_db)\n) -> PixTransferResponse:\n    \"\"\"Create a new Pix transfer.\"\"\"\n    result = await pix_service.process_transfer(transfer)\n    return result"
        }
    },
    {
        "id": "file_3",
        "score": 0.85,
        "metadata": {
            "file_path": "fake_pix_repo/services/pix_service.py",
            "content": "class PixService:\n    def __init__(self, db: Session):\n        self.db = db\n    \n    async def process_transfer(self, transfer_data: dict) -> dict:\n        \"\"\"Process Pix transfer with validation.\"\"\"\n        # Validation and processing logic\n        return {'status': 'success'}"
        }
    }
]

MOCK_VECTOR_SEARCH_NO_RESULTS = []


# ============================================================================
# DATABASE MOCK RESPONSES
# ============================================================================

MOCK_DATABASE_RESPONSES = {
    "save_execution": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "completed"
    },
    "get_execution": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "raw_regulatory_text": "RESOLUÇÃO BCB Nº 123/2024...",
        "change_detected": True,
        "risk_level": "high",
        "regulatory_model": {
            "title": "Validação de CPF/CNPJ",
            "description": "Resolução sobre validação de documentos",
            "requirements": ["Implementar validação"],
            "deadlines": [{"date": "2024-12-31", "description": "Prazo final"}],
            "affected_systems": ["Pix"]
        },
        "status": "completed",
        "created_at": datetime.now(UTC).isoformat()
    },
    "list_executions": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": datetime.now(UTC).isoformat(),
            "status": "completed",
            "risk_level": "high"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": datetime.now(UTC).isoformat(),
            "status": "completed",
            "risk_level": "medium"
        }
    ]
}


# ============================================================================
# COMPLETE MOCK STATE OBJECTS
# ============================================================================

MOCK_COMPLETE_STATE = {
    "raw_regulatory_text": "RESOLUÇÃO BCB Nº 123/2024\n\nO Banco Central do Brasil resolve...",
    "change_detected": True,
    "risk_level": "high",
    "regulatory_model": {
        "title": "Validação de CPF/CNPJ para transações Pix",
        "description": "Resolução que estabelece validação obrigatória",
        "requirements": ["Implementar validação de CPF/CNPJ"],
        "deadlines": [{"date": "2024-12-31", "description": "Prazo final"}],
        "affected_systems": ["Pix", "validação"]
    },
    "impacted_files": [
        {
            "file_path": "fake_pix_repo/domain/validators.py",
            "relevance_score": 0.92,
            "snippet": "def validate_cpf(cpf: str) -> bool:"
        }
    ],
    "impact_analysis": [
        {
            "file_path": "fake_pix_repo/domain/validators.py",
            "impact_type": "validation",
            "severity": "high",
            "description": "Adicionar integração com Receita Federal",
            "suggested_changes": ["Adicionar API integration"]
        }
    ],
    "technical_spec": "# Especificação Técnica\n\n## Visão Geral\n...",
    "kiro_prompt": "Implementar validação de CPF/CNPJ...",
    "execution_timestamp": datetime.now(UTC).isoformat(),
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "error": None
}

MOCK_STATE_WITH_ERROR = {
    "raw_regulatory_text": "Invalid text",
    "change_detected": None,
    "risk_level": None,
    "regulatory_model": None,
    "impacted_files": [],
    "impact_analysis": [],
    "technical_spec": None,
    "kiro_prompt": None,
    "execution_timestamp": datetime.now(UTC).isoformat(),
    "execution_id": "660e8400-e29b-41d4-a716-446655440001",
    "error": "Failed to parse regulatory text"
}
