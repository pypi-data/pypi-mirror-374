"""
Tests para el cliente PromptClient
"""

import pytest
from unittest.mock import Mock, patch
from iamex import PromptClient


class TestPromptClient:
    """Tests para la clase PromptClient"""
    
    def test_init_without_api_key(self):
        """Test de inicialización sin API key"""
        client = PromptClient()
        assert client.api_key is None
        assert "Content-Type" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"
    
    def test_init_with_api_key(self):
        """Test de inicialización con API key (para futuras versiones)"""
        client = PromptClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "Content-Type" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"
    
    def test_init_uses_fixed_base_url(self):
        """Test de que se usa la URL base fija"""
        client = PromptClient()
        expected_url = "https://nchat-test.iamexprogramers.site/v1"
        assert client.base_url == expected_url
    
    def test_send_prompt_basic(self):
        """Test básico de envío de prompt"""
        with patch('requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "test"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            client = PromptClient()
            response = client.send_prompt("test prompt", modelo="test-model")
            
            assert response == {"response": "test"}
            mock_post.assert_called_once()
    
    def test_send_prompt_with_model(self):
        """Test de envío de prompt con modelo específico"""
        with patch('requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "test"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            client = PromptClient()
            response = client.send_prompt("test prompt", modelo="IAM-advance-Mexico")
            
            # Verificar que se llamó con el modelo correcto
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert payload['model'] == "IAM-advance-Mexico"
    
    def test_send_prompt_requires_model(self):
        """Test de que el modelo es obligatorio"""
        client = PromptClient()
        
        with pytest.raises(TypeError):
            client.send_prompt("test prompt")  # Falta el parámetro modelo
