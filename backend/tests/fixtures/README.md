# Test Fixtures

This directory contains reusable test fixtures for the regulatory-ai-poc project.

## Contents

### regulatory_texts.py
Sample regulatory texts in Brazilian Portuguese for testing the pipeline:

- **SHORT_REGULATION**: ~70 words - Basic regulation about CPF validation
- **MEDIUM_REGULATION**: ~323 words - Security requirements for Pix transactions
- **LONG_REGULATION**: ~1230 words - Comprehensive governance and compliance regulation
- **REGULATION_WITH_DEADLINE**: Explicit deadline (December 31, 2024)
- **REGULATION_WITH_PIX**: Specific to Pix QR Code requirements
- **INFORMATIONAL_TEXT**: Non-regulatory informational text (no changes)
- **ALL_REGULATORY_TEXTS**: Dictionary containing all texts for easy iteration

### mock_responses.py
Mock responses for all agents and services:

#### Agent Responses
- **MOCK_SENTINEL_RESPONSE**: Change detected with high risk
- **MOCK_SENTINEL_NO_CHANGE**: No regulatory changes detected
- **MOCK_SENTINEL_MEDIUM_RISK**: Medium risk change detected
- **MOCK_TRANSLATOR_RESPONSE**: Structured regulatory model
- **MOCK_TRANSLATOR_COMPLEX_RESPONSE**: Complex regulation with multiple requirements
- **MOCK_TRANSLATOR_QR_CODE_RESPONSE**: QR Code specific regulation
- **MOCK_CODEREADER_RESPONSE**: List of impacted files with relevance scores
- **MOCK_CODEREADER_QR_CODE_RESPONSE**: QR Code related files
- **MOCK_CODEREADER_EMPTY_RESPONSE**: No files found
- **MOCK_IMPACT_RESPONSE**: Detailed impact analysis for multiple files
- **MOCK_IMPACT_QR_CODE_RESPONSE**: QR Code specific impacts
- **MOCK_IMPACT_LOW_SEVERITY_RESPONSE**: Low severity impacts
- **MOCK_SPEC_GENERATOR_RESPONSE**: Technical specification document
- **MOCK_SPEC_GENERATOR_QR_CODE_RESPONSE**: QR Code spec document
- **MOCK_KIRO_PROMPT_RESPONSE**: Development prompt
- **MOCK_KIRO_PROMPT_QR_CODE_RESPONSE**: QR Code development prompt

#### Service Responses
- **MOCK_VECTOR_SEARCH_RESULTS**: Vector search results with scores
- **MOCK_VECTOR_SEARCH_NO_RESULTS**: Empty search results
- **MOCK_DATABASE_RESPONSES**: Database operation responses (save, get, list)

#### Complete State Objects
- **MOCK_COMPLETE_STATE**: Full GlobalState with all fields populated
- **MOCK_STATE_WITH_ERROR**: State object with error condition

## Usage Examples

### Using Regulatory Texts

```python
from backend.tests.fixtures import SHORT_REGULATION, ALL_REGULATORY_TEXTS

# Use a specific text
def test_sentinel_with_short_text():
    result = sentinel_agent.process(SHORT_REGULATION)
    assert result.change_detected is True

# Iterate over all texts
def test_all_regulatory_texts():
    for name, text in ALL_REGULATORY_TEXTS.items():
        result = process_text(text)
        assert result is not None
```

### Using Mock Responses

```python
from backend.tests.fixtures import MOCK_SENTINEL_RESPONSE, MOCK_TRANSLATOR_RESPONSE
from backend.models.regulatory import RegulatoryModel

# Mock LLM response
def test_sentinel_parsing(mocker):
    mocker.patch('backend.agents.sentinel.llm_call', return_value=MOCK_SENTINEL_RESPONSE)
    result = sentinel_agent.analyze(text)
    assert result['change_detected'] is True

# Create model from mock
def test_regulatory_model():
    model = RegulatoryModel(**MOCK_TRANSLATOR_RESPONSE)
    assert model.title == "Validação de CPF/CNPJ para transações Pix"
    assert len(model.requirements) == 3
```

### Using Mock Vector Search

```python
from backend.tests.fixtures import MOCK_VECTOR_SEARCH_RESULTS

def test_codereader_with_mock_search(mocker):
    mocker.patch('backend.services.vector_store.search', return_value=MOCK_VECTOR_SEARCH_RESULTS)
    result = codereader_agent.find_files(regulatory_model)
    assert len(result) == 3
    assert result[0]['file_path'] == "fake_pix_repo/domain/validators.py"
```

### Using Complete State Objects

```python
from backend.tests.fixtures import MOCK_COMPLETE_STATE
from backend.models.state import GlobalState

def test_with_complete_state():
    state = GlobalState(**MOCK_COMPLETE_STATE)
    assert state.change_detected is True
    assert state.risk_level == "high"
    assert len(state.impacted_files) > 0
```

## Data Alignment

All mock responses are designed to align with the data models:
- `backend/models/state.py` - GlobalState
- `backend/models/regulatory.py` - RegulatoryModel
- `backend/models/impact.py` - ImpactedFile, Impact

The fixtures can be directly used to instantiate these models without modification.

## Extending Fixtures

To add new fixtures:

1. Add the fixture to the appropriate file (regulatory_texts.py or mock_responses.py)
2. Export it in __init__.py
3. Document it in this README
4. Ensure it aligns with the relevant data models
