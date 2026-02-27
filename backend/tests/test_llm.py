"""
Unit tests for LLM provider interface and implementations.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from backend.services.llm import OllamaLLM, LocalLLM, get_llm


class TestOllamaLLM:
    """Test cases for OllamaLLM implementation."""
    
    def test_initialization(self):
        """Test OllamaLLM initialization with default parameters."""
        llm = OllamaLLM()
        assert llm.base_url == "http://localhost:11434"
        assert llm.model == "llama2"
    
    def test_initialization_custom_params(self):
        """Test OllamaLLM initialization with custom parameters."""
        llm = OllamaLLM(base_url="http://custom:8080", model="mistral")
        assert llm.base_url == "http://custom:8080"
        assert llm.model == "mistral"
    
    @patch('backend.services.llm.requests.post')
    def test_generate_success(self, mock_post):
        """Test successful text generation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Generated text"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("Test prompt")
        
        assert result == "Generated text"
        mock_post.assert_called_once()
        
        # Verify API call parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        assert call_args[1]["json"]["model"] == "llama2"
        assert call_args[1]["json"]["prompt"] == "Test prompt"
        assert call_args[1]["json"]["stream"] is False
        assert call_args[1]["json"]["options"]["num_predict"] == 1000
    
    @patch('backend.services.llm.requests.post')
    def test_generate_with_max_tokens(self, mock_post):
        """Test text generation with custom max_tokens."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Short text"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("Test prompt", max_tokens=500)
        
        assert result == "Short text"
        call_args = mock_post.call_args
        assert call_args[1]["json"]["options"]["num_predict"] == 500
    
    @patch('backend.services.llm.requests.post')
    def test_generate_connection_error(self, mock_post):
        """Test handling of connection errors."""
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        llm = OllamaLLM()
        with pytest.raises(requests.RequestException):
            llm.generate("Test prompt")
    
    @patch('backend.services.llm.requests.post')
    def test_generate_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_post.return_value = mock_response
        
        llm = OllamaLLM()
        with pytest.raises(requests.RequestException):
            llm.generate("Test prompt")
    
    @patch('backend.services.llm.requests.post')
    def test_generate_empty_response(self, mock_post):
        """Test handling of empty response from API."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("Test prompt")
        
        assert result == ""


class TestLocalLLM:
    """Test cases for LocalLLM fallback implementation."""
    
    def test_initialization(self):
        """Test LocalLLM initialization."""
        llm = LocalLLM()
        assert llm is not None
    
    def test_generate_returns_fallback_message(self):
        """Test that generate returns a fallback message."""
        llm = LocalLLM()
        result = llm.generate("Test prompt")
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "fallback" in result.lower()
    
    def test_generate_with_max_tokens(self):
        """Test that generate accepts max_tokens parameter."""
        llm = LocalLLM()
        result = llm.generate("Test prompt", max_tokens=500)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestGetLLM:
    """Test cases for get_llm factory function."""
    
    @patch.dict('os.environ', {}, clear=True)
    def test_default_returns_ollama(self):
        """Test that get_llm returns OllamaLLM by default."""
        llm = get_llm()
        assert isinstance(llm, OllamaLLM)
        assert llm.base_url == "http://localhost:11434"
        assert llm.model == "llama2"
    
    @patch.dict('os.environ', {'LLM_TYPE': 'ollama'})
    def test_explicit_ollama(self):
        """Test explicit ollama type."""
        llm = get_llm()
        assert isinstance(llm, OllamaLLM)
    
    @patch.dict('os.environ', {'LLM_TYPE': 'OLLAMA'})
    def test_case_insensitive(self):
        """Test that LLM_TYPE is case-insensitive."""
        llm = get_llm()
        assert isinstance(llm, OllamaLLM)
    
    @patch.dict('os.environ', {'LLM_TYPE': 'local'})
    def test_local_type(self):
        """Test local LLM type."""
        llm = get_llm()
        assert isinstance(llm, LocalLLM)
    
    @patch.dict('os.environ', {
        'LLM_TYPE': 'ollama',
        'OLLAMA_BASE_URL': 'http://custom:9999',
        'OLLAMA_MODEL': 'mistral'
    })
    def test_custom_ollama_config(self):
        """Test custom Ollama configuration from environment."""
        llm = get_llm()
        assert isinstance(llm, OllamaLLM)
        assert llm.base_url == "http://custom:9999"
        assert llm.model == "mistral"
    
    @patch.dict('os.environ', {'LLM_TYPE': 'invalid'})
    def test_invalid_type_raises_error(self):
        """Test that invalid LLM type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown LLM type"):
            get_llm()


class TestLLMProviderProtocol:
    """Test that implementations conform to LLMProvider protocol."""
    
    def test_ollama_has_generate_method(self):
        """Test that OllamaLLM has generate method."""
        llm = OllamaLLM()
        assert hasattr(llm, 'generate')
        assert callable(llm.generate)
    
    def test_local_has_generate_method(self):
        """Test that LocalLLM has generate method."""
        llm = LocalLLM()
        assert hasattr(llm, 'generate')
        assert callable(llm.generate)
    
    def test_generate_signature(self):
        """Test that generate methods have correct signature."""
        import inspect
        
        ollama_sig = inspect.signature(OllamaLLM.generate)
        local_sig = inspect.signature(LocalLLM.generate)
        
        # Both should have 'prompt' and 'max_tokens' parameters
        assert 'prompt' in ollama_sig.parameters
        assert 'max_tokens' in ollama_sig.parameters
        assert 'prompt' in local_sig.parameters
        assert 'max_tokens' in local_sig.parameters
