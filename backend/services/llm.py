"""
LLM Provider Interface and Implementations

This module provides a protocol-based interface for LLM providers and concrete
implementations for Ollama and a fallback local LLM.
"""

import os
import logging
from typing import Protocol
import requests


logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt text
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
        """
        ...


class OllamaLLM:
    """LLM provider using local Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama LLM provider.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name to use (default: llama2)
        """
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized OllamaLLM with model={model}, base_url={base_url}")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: The input prompt text
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            requests.RequestException: If API call fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise


class LocalLLM:
    """Fallback LLM implementation for when Ollama is not available."""
    
    def __init__(self):
        """Initialize fallback LLM."""
        logger.info("Initialized LocalLLM (fallback implementation)")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using fallback implementation.
        
        This is a simple mock implementation that returns a basic response.
        In a production system, this could use transformers or llama.cpp.
        
        Args:
            prompt: The input prompt text
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
        """
        logger.warning("Using fallback LocalLLM - returning mock response")
        return (
            "This is a fallback response from LocalLLM. "
            "For production use, configure Ollama or implement a proper local model."
        )


def get_llm() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Checks the LLM_TYPE environment variable and returns the corresponding
    implementation. Defaults to "ollama" if not set.
    
    Environment Variables:
        LLM_TYPE: Type of LLM to use ("ollama" or "local", default: "ollama")
        OLLAMA_BASE_URL: Base URL for Ollama API (default: http://localhost:11434)
        OLLAMA_MODEL: Model name for Ollama (default: llama2)
    
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If LLM_TYPE is not recognized
    """
    llm_type = os.getenv("LLM_TYPE", "ollama").lower()
    
    if llm_type == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        return OllamaLLM(base_url=base_url, model=model)
    elif llm_type == "local":
        return LocalLLM()
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}. Must be 'ollama' or 'local'")
