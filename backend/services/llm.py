"""
LLM Provider Interface and Implementations

This module provides a protocol-based interface for LLM providers and concrete
implementations for Ollama, OpenAI, Gemini, and a fallback local LLM.
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


class OpenAILLM:
    """LLM provider using OpenAI API."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1"):
        """
        Initialize OpenAI LLM provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use (default: gpt-3.5-turbo)
            base_url: Base URL for OpenAI API (default: https://api.openai.com/v1)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        logger.info(f"Initialized OpenAILLM with model={model}")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using OpenAI API.
        
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
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


class GeminiLLM:
    """LLM provider using Google Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini LLM provider.
        
        Args:
            api_key: Google API key
            model: Model name to use (default: gemini-2.0-flash)
                   Can be with or without 'models/' prefix
        """
        self.api_key = api_key
        # Ensure model name has correct format (add prefix only if not present)
        if model.startswith("models/"):
            self.model = model
        else:
            self.model = f"models/{model}"
        logger.info(f"Initialized GeminiLLM with model={self.model}")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: The input prompt text
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            requests.RequestException: If API call fails
        """
        try:
            # Use v1beta for now as it's more stable
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Log the response for debugging
            logger.debug(f"Gemini API response: {result}")
            
            # Handle different response structures
            try:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Unexpected Gemini response structure: {result}")
                # Try alternative structure
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate:
                        content = candidate["content"]
                        # Try direct text field
                        if "text" in content:
                            return content["text"]
                        # Try parts array
                        if "parts" in content and len(content["parts"]) > 0:
                            if "text" in content["parts"][0]:
                                return content["parts"][0]["text"]
                # If all else fails, return error message
                raise ValueError(f"Could not parse Gemini response: {result}")
        except requests.RequestException as e:
            logger.error(f"Gemini API call failed: {e}")
            raise


def get_llm() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Checks the LLM_TYPE environment variable and returns the corresponding
    implementation. Defaults to "ollama" if not set.
    
    Environment Variables:
        LLM_TYPE: Type of LLM to use ("ollama", "openai", "gemini", or "local", default: "ollama")
        
        For Ollama:
            OLLAMA_BASE_URL: Base URL for Ollama API (default: http://localhost:11434)
            OLLAMA_MODEL: Model name for Ollama (default: llama2)
        
        For OpenAI:
            OPENAI_API_KEY: OpenAI API key (required)
            OPENAI_MODEL: Model name (default: gpt-3.5-turbo)
            OPENAI_BASE_URL: Base URL (default: https://api.openai.com/v1)
        
        For Gemini:
            GEMINI_API_KEY: Google API key (required)
            GEMINI_MODEL: Model name (default: gemini-2.0-flash)
    
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If LLM_TYPE is not recognized or required env vars are missing
    """
    llm_type = os.getenv("LLM_TYPE", "ollama").lower()
    
    if llm_type == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        return OllamaLLM(base_url=base_url, model=model)
    elif llm_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI LLM")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        return OpenAILLM(api_key=api_key, model=model, base_url=base_url)
    elif llm_type == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for Gemini LLM")
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        return GeminiLLM(api_key=api_key, model=model)
    elif llm_type == "local":
        return LocalLLM()
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}. Must be 'ollama', 'openai', 'gemini', or 'local'")
