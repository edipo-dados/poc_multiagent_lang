"""
Unit tests for Embedding Service.

Tests embedding generation using sentence-transformers model.

NOTE: These tests require sentence-transformers to be installed.
Run: pip install -r backend/requirements.txt
"""

import pytest

# Skip all tests if sentence-transformers is not installed
pytest.importorskip("sentence_transformers")

from backend.services.embeddings import EmbeddingService


def test_embedding_service_initialization():
    """Test that EmbeddingService initializes with default model."""
    service = EmbeddingService()
    assert service.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert service.model is None  # Lazy loading
    assert service.dimension is None


def test_embedding_service_lazy_loading():
    """Test that model is loaded on first use."""
    service = EmbeddingService()
    
    # Model should not be loaded yet
    assert service.model is None
    
    # First encode should load model
    embedding = service.encode("test text")
    
    # Model should now be loaded
    assert service.model is not None
    assert service.dimension == 384


def test_encode_returns_correct_dimension():
    """Test that encode returns 384-dimensional vector."""
    service = EmbeddingService()
    embedding = service.encode("test text")
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)


def test_encode_different_texts_produce_different_embeddings():
    """Test that different texts produce different embeddings."""
    service = EmbeddingService()
    
    embedding1 = service.encode("Python code for Pix transactions")
    embedding2 = service.encode("JavaScript frontend application")
    
    # Embeddings should be different
    assert embedding1 != embedding2


def test_encode_similar_texts_have_high_similarity():
    """Test that similar texts produce similar embeddings."""
    service = EmbeddingService()
    
    embedding1 = service.encode("Pix transaction validation")
    embedding2 = service.encode("Validating Pix transactions")
    
    # Calculate cosine similarity
    import numpy as np
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    # Similar texts should have high similarity (> 0.7)
    assert similarity > 0.7


def test_encode_batch_returns_correct_shape():
    """Test that encode_batch returns correct number of embeddings."""
    service = EmbeddingService()
    
    texts = [
        "First text",
        "Second text",
        "Third text"
    ]
    
    embeddings = service.encode_batch(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)


def test_encode_batch_with_custom_batch_size():
    """Test that encode_batch works with custom batch size."""
    service = EmbeddingService()
    
    texts = ["Text " + str(i) for i in range(10)]
    embeddings = service.encode_batch(texts, batch_size=2)
    
    assert len(embeddings) == 10
    assert all(len(emb) == 384 for emb in embeddings)


def test_encode_batch_empty_list():
    """Test that encode_batch handles empty list."""
    service = EmbeddingService()
    
    embeddings = service.encode_batch([])
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 0


def test_get_dimension():
    """Test that get_dimension returns correct value."""
    service = EmbeddingService()
    
    dimension = service.get_dimension()
    
    assert dimension == 384


def test_encode_empty_string():
    """Test that encode handles empty string."""
    service = EmbeddingService()
    
    embedding = service.encode("")
    
    # Should still return valid embedding
    assert isinstance(embedding, list)
    assert len(embedding) == 384


def test_encode_long_text():
    """Test that encode handles long text."""
    service = EmbeddingService()
    
    # Create long text (model has max sequence length of 256 tokens)
    long_text = "This is a test. " * 200
    
    embedding = service.encode(long_text)
    
    # Should still return valid embedding (model will truncate)
    assert isinstance(embedding, list)
    assert len(embedding) == 384


def test_encode_code_content():
    """Test that encode works with actual code content."""
    service = EmbeddingService()
    
    code = """
def create_pix_transaction(sender: str, receiver: str, amount: float):
    '''Create a new Pix transaction.'''
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    transaction = PixTransaction(
        sender_key=sender,
        receiver_key=receiver,
        amount=amount
    )
    return transaction
"""
    
    embedding = service.encode(code)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384


def test_model_reuse_across_calls():
    """Test that model is reused across multiple encode calls."""
    service = EmbeddingService()
    
    # First call loads model
    service.encode("first")
    model_instance = service.model
    
    # Second call should reuse same model
    service.encode("second")
    assert service.model is model_instance
