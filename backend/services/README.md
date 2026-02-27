# Services

This directory contains service layer implementations for the regulatory AI POC.

## Vector Store Service

**File:** `vector_store.py`

Provides semantic search capabilities using PostgreSQL with pgvector extension.

### Key Methods

- `search_similar(query_embedding, top_k, threshold)`: Search for similar code files using cosine similarity
- `upsert_embedding(file_path, content, embedding)`: Insert or update file embedding
- `get_embedding_count()`: Get total number of embeddings
- `get_embedding(file_path)`: Retrieve embedding for specific file

### Usage Example

```python
from backend.database.connection import AsyncSessionLocal
from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingService

# Generate query embedding
embedding_service = EmbeddingService()
query_embedding = embedding_service.encode("Pix transaction validation")

# Search for similar files
async with AsyncSessionLocal() as session:
    vector_store = VectorStoreService(session)
    results = await vector_store.search_similar(
        query_embedding=query_embedding,
        top_k=10,
        threshold=0.5
    )
    
    for result in results:
        print(f"{result.file_path}: {result.relevance_score:.3f}")
```

## LLM Service

**File:** `llm.py`

Provides a protocol-based interface for LLM providers with implementations for Ollama and fallback local LLM.

### Key Components

- `LLMProvider`: Protocol defining the interface for LLM providers
- `OllamaLLM`: Implementation using local Ollama API
- `LocalLLM`: Fallback implementation for when Ollama is not available
- `get_llm()`: Factory function to get the appropriate LLM provider

### Usage Example

```python
from backend.services.llm import get_llm

# Get LLM provider (defaults to Ollama)
llm = get_llm()

# Generate text
response = llm.generate("Analyze this regulatory text: ...", max_tokens=500)
print(response)
```

### Configuration

Configure via environment variables:

- `LLM_TYPE`: Type of LLM to use ("ollama" or "local", default: "ollama")
- `OLLAMA_BASE_URL`: Base URL for Ollama API (default: "http://localhost:11434")
- `OLLAMA_MODEL`: Model name for Ollama (default: "llama2")

### Example Configurations

```bash
# Use Ollama with default settings
export LLM_TYPE=ollama

# Use Ollama with custom model
export LLM_TYPE=ollama
export OLLAMA_MODEL=mistral

# Use fallback local LLM
export LLM_TYPE=local
```

## Embedding Service

**File:** `embeddings.py`

Generates vector embeddings using sentence-transformers model.

### Key Methods

- `encode(text)`: Generate embedding for single text
- `encode_batch(texts, batch_size)`: Generate embeddings for multiple texts
- `get_dimension()`: Get embedding dimension (384)

### Usage Example

```python
from backend.services.embeddings import EmbeddingService

service = EmbeddingService()

# Single text
embedding = service.encode("def create_pix(): pass")
print(f"Embedding dimension: {len(embedding)}")

# Multiple texts
texts = ["text1", "text2", "text3"]
embeddings = service.encode_batch(texts)
print(f"Generated {len(embeddings)} embeddings")
```

## Initialization Script

**File:** `scripts/init_embeddings.py`

Populates the vector store with embeddings for all Python files in the fake Pix repository.

### Usage

```bash
# From project root
python backend/scripts/init_embeddings.py

# Or with custom repository path
PIX_REPO_PATH=path/to/repo python backend/scripts/init_embeddings.py
```

### What It Does

1. Scans the fake Pix repository for all `.py` files
2. Generates embeddings using the EmbeddingService
3. Stores embeddings in the vector store
4. Runs a verification query to test the setup

### Requirements

Before running the initialization script, ensure:

1. PostgreSQL with pgvector extension is running
2. Database connection is configured (DATABASE_URL environment variable)
3. Python dependencies are installed: `pip install -r backend/requirements.txt`

## Testing

### Unit Tests

```bash
# Test vector store service (requires PostgreSQL with pgvector)
pytest backend/tests/test_vector_store.py -v

# Test embedding service (requires sentence-transformers)
pytest backend/tests/test_embeddings.py -v
```

### Integration Test

```bash
# Initialize embeddings and verify
python backend/scripts/init_embeddings.py
```

## Dependencies

- `sentence-transformers==2.2.2`: For generating embeddings
- `pgvector==0.2.4`: For PostgreSQL vector operations
- `sqlalchemy[asyncio]==2.0.23`: For async database operations
- `asyncpg==0.29.0`: PostgreSQL async driver

## Performance Notes

- **Embedding Generation**: ~100ms per file on CPU, faster on GPU
- **Batch Processing**: Use `encode_batch()` for better performance with multiple files
- **Search Performance**: Cosine similarity search is O(n) but optimized with IVFFlat index
- **Model Size**: all-MiniLM-L6-v2 is ~80MB, downloads on first use

## Troubleshooting

### "No module named 'sentence_transformers'"

Install dependencies:
```bash
pip install -r backend/requirements.txt
```

### "No module named 'pgvector'"

Install pgvector Python package:
```bash
pip install pgvector==0.2.4
```

### "pgvector extension not found"

Ensure PostgreSQL has pgvector extension installed. In Docker:
```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
```

### Model download fails

The sentence-transformers model downloads automatically on first use. If download fails:
1. Check internet connection
2. Manually download from HuggingFace: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
3. Place in `~/.cache/torch/sentence_transformers/`
