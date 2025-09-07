"""
LLM Backend Tests
Tests for different LLM backend implementations
"""

import pytest
import os
import httpx
from unittest.mock import Mock, patch, AsyncMock

from layers.adapter.autogen.llm_backend import (
    LLMBackend,
    OpenAIBackend,
    DeepSeekBackend,
    create_llm_backend
)


@pytest.mark.asyncio
class TestLLMBackend:
    """Test LLM backend base class and implementations"""
    
    @pytest.fixture
    def test_api_key(self):
        """Test API key fixture"""
        return "test-key-12345"
    
    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response fixture"""
        response = Mock()
        response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response",
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        response.raise_for_status = Mock()
        return response
    
    async def test_openai_backend_initialization(self, test_api_key):
        """Test OpenAI backend initialization"""
        backend = OpenAIBackend(
            api_key=test_api_key,
            model="gpt-3.5-turbo"
        )
        
        assert backend.api_key == test_api_key
        assert backend.model == "gpt-3.5-turbo"
        assert backend.base_url == "https://api.openai.com/v1"
        assert isinstance(backend.client, httpx.AsyncClient)
        
        await backend.close()
    
    async def test_deepseek_backend_initialization(self, test_api_key):
        """Test DeepSeek backend initialization"""
        backend = DeepSeekBackend(
            api_key=test_api_key,
            model="deepseek-chat"
        )
        
        assert backend.api_key == test_api_key
        assert backend.model == "deepseek-chat"
        assert backend.base_url == "https://api.deepseek.com/v1"
        assert isinstance(backend.client, httpx.AsyncClient)
        
        await backend.close()
    
    async def test_openai_chat_completion(self, test_api_key, mock_response):
        """Test OpenAI chat completion"""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            backend = OpenAIBackend(api_key=test_api_key)
            
            messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            result = await backend.chat_completion(messages)
            
            assert "choices" in result
            assert result["choices"][0]["message"]["content"] == "Test response"
            
            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args[1]
            assert "json" in call_args
            assert call_args["json"]["messages"] == messages
            
            await backend.close()
    
    async def test_deepseek_chat_completion(self, test_api_key, mock_response):
        """Test DeepSeek chat completion"""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            backend = DeepSeekBackend(api_key=test_api_key)
            
            messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            result = await backend.chat_completion(messages)
            
            assert "choices" in result
            assert result["choices"][0]["message"]["content"] == "Test response"
            
            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args[1]
            assert "json" in call_args
            assert call_args["json"]["messages"] == messages
            
            await backend.close()
    
    async def test_backend_error_handling(self, test_api_key):
        """Test error handling in backends"""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.HTTPError("API error")
            
            backend = OpenAIBackend(api_key=test_api_key)
            
            with pytest.raises(Exception):
                await backend.chat_completion([{"role": "user", "content": "Hello"}])
            
            await backend.close()
    
    def test_create_llm_backend(self, test_api_key):
        """Test backend creation factory function"""
        # Test OpenAI backend creation
        backend1 = create_llm_backend(
            backend_type="openai",
            api_key=test_api_key
        )
        assert isinstance(backend1, OpenAIBackend)
        
        # Test DeepSeek backend creation
        backend2 = create_llm_backend(
            backend_type="deepseek",
            api_key=test_api_key
        )
        assert isinstance(backend2, DeepSeekBackend)
        
        # Test invalid backend type
        with pytest.raises(ValueError):
            create_llm_backend("invalid_type", test_api_key)
    
    def test_api_key_validation(self):
        """Test API key validation"""
        # Test missing API key
        with pytest.raises(ValueError):
            create_llm_backend("openai")
        
        # Test environment variable fallback
        os.environ["OPENAI_API_KEY"] = "test-key"
        backend = create_llm_backend("openai")
        assert isinstance(backend, OpenAIBackend)
        assert backend.api_key == "test-key"
        del os.environ["OPENAI_API_KEY"]
    
    @pytest.mark.integration
    @pytest.mark.api_key_required
    async def test_real_openai_api(self):
        """Test real OpenAI API integration"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("No real OPENAI_API_KEY for integration test")
        
        backend = OpenAIBackend(
            api_key=api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        try:
            messages = [
                {"role": "user", "content": "Say hello in exactly 3 words."}
            ]
            
            result = await backend.chat_completion(messages)
            
            assert "choices" in result
            assert "message" in result["choices"][0]
            assert "content" in result["choices"][0]["message"]
            
        finally:
            await backend.close()
    
    @pytest.mark.integration
    @pytest.mark.api_key_required
    async def test_real_deepseek_api(self):
        """Test real DeepSeek API integration"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("No real DEEPSEEK_API_KEY for integration test")
        
        backend = DeepSeekBackend(
            api_key=api_key,
            model="deepseek-chat",
            temperature=0.1
        )
        
        try:
            messages = [
                {"role": "user", "content": "Say hello in exactly 3 words."}
            ]
            
            result = await backend.chat_completion(messages)
            
            assert "choices" in result
            assert "message" in result["choices"][0]
            assert "content" in result["choices"][0]["message"]
            
        finally:
            await backend.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 