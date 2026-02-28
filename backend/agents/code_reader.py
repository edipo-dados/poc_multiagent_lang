"""
CodeReader Agent - Semantic Code Search

The CodeReader Agent identifies relevant code files using semantic search.
It generates a search query from the regulatory model, creates embeddings,
and queries the vector store for the top 10 most similar files.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import logging
from backend.models.state import GlobalState
from backend.services.embeddings import EmbeddingService
from backend.services.vector_store import VectorStoreService
from backend.database.connection import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def code_reader_agent(state: GlobalState) -> GlobalState:
    """
    Query vector store for relevant code files using semantic search.
    
    This agent performs the third step in the multi-agent pipeline:
    1. Generates search query from regulatory_model
    2. Creates embedding for the query using EmbeddingService
    3. Queries VectorStoreService for top 10 similar files
    4. Updates Global State with impacted_files list
    5. Handles empty results case
    
    Args:
        state: GlobalState containing regulatory_model
        
    Returns:
        Updated GlobalState with impacted_files list
        
    Raises:
        Exception: If embedding generation or vector search fails
        
    Requirements:
        - 5.1: Perform semantic search on Vector_Store using regulatory_model
        - 5.2: Retrieve top 10 most relevant code files
        - 5.3: Update Global State with impacted_files list (file paths and relevance scores)
        - 5.4: Use embeddings stored in Vector_Store for similarity matching
        - 5.5: Return empty list if no relevant files found
    """
    logger.info(f"CodeReader Agent starting for execution {state.execution_id}")
    
    try:
        # Validate that regulatory_model exists
        if not state.regulatory_model:
            logger.warning("No regulatory_model found in state - returning empty impacted_files")
            state.impacted_files = []
            return state
        
        # Step 1: Generate search query from regulatory_model
        search_query = _generate_search_query(state.regulatory_model)
        logger.info(f"Generated search query: {search_query[:100]}...")
        
        # Step 2: Create embedding for search query
        embedding_service = EmbeddingService()
        query_embedding = embedding_service.encode(search_query)
        logger.debug(f"Generated embedding with dimension: {len(query_embedding)}")
        
        # Step 3: Query vector store for top 10 similar files
        async with AsyncSessionLocal() as session:
            vector_store = VectorStoreService(session)
            impacted_files = await vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=10,
                threshold=0.3  # Lowered threshold for better results
            )
        
        # Step 4: Update Global State with impacted_files
        # Convert ImpactedFile objects to dicts for state storage
        state.impacted_files = [
            {
                "file_path": file.file_path,
                "relevance_score": file.relevance_score,
                "snippet": file.snippet
            }
            for file in impacted_files
        ]
        
        logger.info(f"CodeReader Agent completed successfully. Found {len(state.impacted_files)} impacted files")
        
        # Log file paths for debugging
        if state.impacted_files:
            for file in state.impacted_files:
                logger.debug(f"  - {file['file_path']} (score: {file['relevance_score']:.3f})")
        else:
            logger.info("No relevant files found above threshold")
        
        return state
        
    except Exception as e:
        logger.error(f"CodeReader Agent failed: {str(e)}", exc_info=True)
        state.error = f"CodeReader Agent error: {str(e)}"
        raise


def _generate_search_query(regulatory_model: dict) -> str:
    """
    Generate search query by combining regulatory model fields.
    
    Combines title, requirements, and affected_systems to create a
    comprehensive search query that captures the semantic meaning
    of the regulatory change.
    
    Args:
        regulatory_model: Dict with title, description, requirements, 
                         deadlines, affected_systems
        
    Returns:
        Search query string combining relevant fields
    """
    query_parts = []
    
    # Add title (most important)
    if regulatory_model.get("title"):
        query_parts.append(regulatory_model["title"])
    
    # Add description for context
    if regulatory_model.get("description"):
        query_parts.append(regulatory_model["description"])
    
    # Add requirements (specific actionable items)
    requirements = regulatory_model.get("requirements", [])
    if requirements:
        # Limit to first 5 requirements to avoid overly long queries
        query_parts.extend(requirements[:5])
    
    # Add affected systems (helps target specific code areas)
    affected_systems = regulatory_model.get("affected_systems", [])
    if affected_systems:
        systems_text = " ".join(affected_systems)
        query_parts.append(f"Systems: {systems_text}")
    
    # Combine all parts with spaces
    search_query = " ".join(query_parts)
    
    logger.debug(f"Search query components: title={bool(regulatory_model.get('title'))}, "
                f"description={bool(regulatory_model.get('description'))}, "
                f"requirements={len(requirements)}, "
                f"affected_systems={len(affected_systems)}")
    
    return search_query
