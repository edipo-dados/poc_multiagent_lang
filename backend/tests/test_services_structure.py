"""
Structure tests for services.

Verifies that service classes are properly defined and importable.
These tests don't require external dependencies to be installed.
"""

import pytest
import inspect


def test_vector_store_service_exists():
    """Test that VectorStoreService class is defined."""
    from backend.services.vector_store import VectorStoreService
    
    assert inspect.isclass(VectorStoreService)


def test_vector_store_service_has_required_methods():
    """Test that VectorStoreService has all required methods."""
    from backend.services.vector_store import VectorStoreService
    
    required_methods = [
        'search_similar',
        'upsert_embedding',
        'get_embedding_count',
        'get_embedding'
    ]
    
    for method_name in required_methods:
        assert hasattr(VectorStoreService, method_name)
        method = getattr(VectorStoreService, method_name)
        assert callable(method)


def test_embedding_service_exists():
    """Test that EmbeddingService class is defined."""
    from backend.services.embeddings import EmbeddingService
    
    assert inspect.isclass(EmbeddingService)


def test_embedding_service_has_required_methods():
    """Test that EmbeddingService has all required methods."""
    from backend.services.embeddings import EmbeddingService
    
    required_methods = [
        'encode',
        'encode_batch',
        'get_dimension'
    ]
    
    for method_name in required_methods:
        assert hasattr(EmbeddingService, method_name)
        method = getattr(EmbeddingService, method_name)
        assert callable(method)


def test_embedding_service_default_model():
    """Test that EmbeddingService has correct default model."""
    from backend.services.embeddings import EmbeddingService
    
    service = EmbeddingService()
    assert service.model_name == "sentence-transformers/all-MiniLM-L6-v2"


def test_init_embeddings_script_has_main():
    """Test that init_embeddings script has main function."""
    from backend.scripts import init_embeddings
    
    assert hasattr(init_embeddings, 'main')
    assert callable(init_embeddings.main)


def test_init_embeddings_script_has_initialize_function():
    """Test that init_embeddings script has initialize_embeddings function."""
    from backend.scripts import init_embeddings
    
    assert hasattr(init_embeddings, 'initialize_embeddings')
    assert callable(init_embeddings.initialize_embeddings)
