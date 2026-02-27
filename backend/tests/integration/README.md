# Integration Tests

This directory contains end-to-end integration tests for the regulatory-ai-poc system.

## Test Files

- `test_e2e.py`: End-to-end pipeline tests that verify complete system behavior

## Running Integration Tests

### Prerequisites

Integration tests require the following services to be running:

1. **PostgreSQL with pgvector** (port 5432)
   - Database: `regulatory_ai`
   - User: `postgres`
   - Password: `postgres`

2. **Ollama LLM Service** (port 11434)
   - Model: `llama2` or compatible

### Running with Docker Compose

The easiest way to run integration tests is using Docker Compose, which starts all required services:

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Run integration tests
python -m pytest backend/tests/integration/test_e2e.py -v
```

### Running Locally

If you want to run tests locally without Docker:

1. Start PostgreSQL with pgvector:
   ```bash
   # Using Docker
   docker run -d \
     --name postgres-test \
     -e POSTGRES_DB=regulatory_ai \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -p 5432:5432 \
     pgvector/pgvector:pg16
   ```

2. Start Ollama:
   ```bash
   # Install and start Ollama
   ollama serve
   
   # Pull required model
   ollama pull llama2
   ```

3. Run tests:
   ```bash
   python -m pytest backend/tests/integration/test_e2e.py -v
   ```

## Test Coverage

The integration tests verify:

- **Full Pipeline Execution**: All six agents execute in the correct sequence
- **Agent Outputs**: Each agent generates its expected outputs
- **State Propagation**: State is properly passed between agents
- **Audit Logging**: Executions are persisted to the database
- **Error Handling**: Pipeline halts correctly on agent failures
- **Different Inputs**: Various regulatory text types are handled correctly

## Test Structure

### TestEndToEndPipeline
Tests the complete analysis pipeline with different regulatory texts:
- Short regulations (~100 words)
- Medium regulations (~500 words)
- Pix-specific regulations
- Agent execution sequence verification
- Output generation verification
- State propagation verification

### TestPipelineErrorHandling
Tests error handling and recovery:
- Pipeline halts on agent failure
- Partial state is saved on failure
- Error messages are properly propagated

### TestPipelineWithDifferentInputs
Tests pipeline behavior with various input characteristics:
- Multiple requirements
- Explicit deadlines
- Different regulatory formats

## Mocking Strategy

Some tests use mocking to avoid external dependencies:
- `test_agents_execute_in_correct_sequence`: Mocks all agents to verify execution order
- `test_audit_log_creation`: Mocks database session to verify audit log creation
- `test_pipeline_halts_on_agent_failure`: Mocks translator agent to simulate failure
- `test_partial_state_saved_on_failure`: Mocks database session to verify partial state saving

## Troubleshooting

### Connection Refused Errors

If you see `ConnectionRefusedError` or `[WinError 1225]`:
- Ensure PostgreSQL is running on port 5432
- Check database credentials match the configuration
- Verify pgvector extension is installed

### LLM Service Errors

If you see `HTTPConnectionPool(host='localhost', port=11434)` errors:
- Ensure Ollama is running on port 11434
- Verify the llama2 model is downloaded
- Check Ollama service status

### Async Event Loop Errors

If you see `asyncio.run() cannot be called from a running event loop`:
- This is expected when running tests with pytest-asyncio
- The tests are designed to work without async decorators
- Ensure you're not mixing async and sync test execution

## CI/CD Integration

For CI/CD pipelines, use Docker Compose to ensure all services are available:

```yaml
# Example GitHub Actions workflow
- name: Start services
  run: docker-compose up -d

- name: Wait for services
  run: sleep 10

- name: Run integration tests
  run: python -m pytest backend/tests/integration/test_e2e.py -v

- name: Stop services
  run: docker-compose down
```
