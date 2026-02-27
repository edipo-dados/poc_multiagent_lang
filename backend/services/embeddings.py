"""
Embedding Generation Service using local sentence-transformers model.

Generates vector embeddings for text using the all-MiniLM-L6-v2 model,
which produces 384-dimensional embeddings suitable for semantic search.

Requirements: 16.4
"""

from typing import Optional
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service for generating text embeddings using local transformer model.
    
    Uses sentence-transformers/all-MiniLM-L6-v2 which:
    - Produces 384-dimensional embeddings
    - Runs locally without API calls
    - Optimized for semantic similarity tasks
    - Fast inference suitable for batch processing
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding service with specified model.
        
        Downloads model on first use if not already cached locally.
        Model is cached in ~/.cache/torch/sentence_transformers/ by default.
        
        Args:
            model_name: HuggingFace model identifier (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.dimension: Optional[int] = None
    
    def _ensure_loaded(self) -> None:
        """
        Lazy load model on first use.
        
        This defers model loading until actually needed, which is useful
        for testing and reduces startup time when embeddings aren't required.
        """
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Converts text into a dense vector representation that captures
        semantic meaning. Similar texts will have similar embeddings
        (high cosine similarity).
        
        Args:
            text: Input text to encode (e.g., code file content, search query)
            
        Returns:
            List of floats representing the embedding vector (384 dimensions)
            
        Requirements: 16.4
        """
        self._ensure_loaded()
        
        # Generate embedding and convert to list
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def encode_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Processes texts in batches for better performance when encoding
        many files. Uses GPU if available, otherwise falls back to CPU.
        
        Args:
            texts: List of input texts to encode
            batch_size: Number of texts to process in each batch (default: 32)
            
        Returns:
            List of embedding vectors, one per input text
            
        Requirements: 16.4
        """
        self._ensure_loaded()
        
        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10  # Show progress for large batches
        )
        
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension for this model.
        
        Returns:
            Embedding vector dimension (384 for all-MiniLM-L6-v2)
        """
        self._ensure_loaded()
        return self.dimension
