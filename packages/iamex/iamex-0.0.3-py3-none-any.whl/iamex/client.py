"""
Cliente principal para consumir la API de modelos de inferencia
"""

import requests
from typing import Dict, Any, Optional


class PromptClient:
    """Cliente para enviar prompts a modelos de inferencia"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el cliente
        
        Args:
            api_key: Clave de API para autenticación (opcional por ahora)
        """
        self.api_key = api_key
        # Endpoint real de iam-hub
        self.base_url = "https://iam-hub.iamexprogramers.site/api/v1"
        self.session = requests.Session()
        
        # Configurar headers básicos
        self.session.headers.update({
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def send_prompt(self, prompt: str, model: str = "dencias si no se tienen", system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """
        Envía un prompt al modelo especificado
        
        Args:
            prompt: El prompt del usuario a enviar
            model: Modelo a usar (por defecto 'IAM-advanced')
            system_prompt: Prompt del sistema (opcional)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Respuesta de la API como diccionario
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_payload(prompt, model, system_prompt, **kwargs)
        
        try:
            response = self.session.post(
                f"{self.base_url}/prompt-model",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error al enviar prompt: {str(e)}")
    
    def send_messages(self, messages: list, model: str = "IAM-advanced", **kwargs) -> Dict[str, Any]:
        """
        Envía mensajes al modelo especificado usando formato de conversación
        
        Args:
            messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "mensaje"}]
            model: Modelo a usar (por defecto 'IAM-advanced')
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Respuesta de la API como diccionario
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_messages_payload(messages, model, **kwargs)
        
        try:
            response = self.session.post(
                f"{self.base_url}/prompt-model",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error al enviar mensajes: {str(e)}")
    
    def _prepare_payload(self, prompt: str, model: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de prompt"""
        # Estructura exacta que espera la API para prompts
        payload = {
            'apikey': self.api_key,
            'model': model,
            'prompt': prompt
        }
        
        # Agregar parámetros adicionales si se proporcionan
        if system_prompt:
            payload['system_prompt'] = system_prompt
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'prompt', 'system_prompt']:
                payload[key] = value
        
        return payload
    
    def _prepare_messages_payload(self, messages: list, model: str, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de mensajes"""
        # Estructura que espera la API con messages
        payload = {
            'apikey': self.api_key,
            'model': model,
            'messages': messages
        }
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'messages']:
                payload[key] = value
        
        return payload
    
    def get_models(self) -> Dict[str, Any]:
        """Obtiene la lista de modelos disponibles"""
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error al obtener modelos: {str(e)}")
