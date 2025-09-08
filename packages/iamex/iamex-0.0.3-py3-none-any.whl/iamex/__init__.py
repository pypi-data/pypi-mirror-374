"""
iamex - Acceso unificado a múltiples modelos de inferencia AI
"""

from .client import PromptClient

__version__ = "0.0.3"
__author__ = "Inteligencia Artificial México"
__email__ = "hostmaster@iamex.io"

def send_prompt(prompt: str, api_key: str, model: str, max_tokens: int = None, **kwargs):
    """
    Función simple para enviar un prompt usando la API de iamex
    
    Args:
        prompt: El prompt del usuario a enviar
        api_key: Clave de API para autenticación
        model: Modelo a usar (ej: "IAM-advanced", "IAM-advance-Mexico")
        max_tokens: Número máximo de tokens en la respuesta (opcional)
        **kwargs: Parámetros adicionales (system_prompt, temperature, etc.)
        
    Returns:
        Respuesta de la API como diccionario
        
    Example:
        >>> from iamex import send_prompt
        >>> response = send_prompt("Hola, ¿cómo estás?", "tu_api_key_aqui", "IAM-advanced", max_tokens=100)
        >>> print(response)
    """
    client = PromptClient(api_key=api_key)
    
    # Preparar kwargs con max_tokens si se proporciona
    if max_tokens is not None:
        kwargs['max_tokens'] = max_tokens
    
    return client.send_prompt(prompt, model=model, **kwargs)


def send_messages(messages: list, api_key: str, model: str, max_tokens: int = None, **kwargs):
    """
    Función para enviar mensajes usando la API de iamex con formato de conversación
    
    Args:
        messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "mensaje"}]
        api_key: Clave de API para autenticación
        model: Modelo a usar (ej: "IAM-advanced", "IAM-advance-Mexico")
        max_tokens: Número máximo de tokens en la respuesta (opcional)
        **kwargs: Parámetros adicionales (temperature, etc.)
        
    Returns:
        Respuesta de la API como diccionario
        
    Example:
        >>> from iamex import send_messages
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "What are some fun things to do in New York?"}
        ... ]
        >>> response = send_messages(messages, "tu_api_key_aqui", "IAM-advanced", max_tokens=200)
        >>> print(response)
    """
    client = PromptClient(api_key=api_key)
    
    # Preparar kwargs con max_tokens si se proporciona
    if max_tokens is not None:
        kwargs['max_tokens'] = max_tokens
    
    return client.send_messages(messages, model=model, **kwargs)

__all__ = ["PromptClient", "send_prompt", "send_messages"]
