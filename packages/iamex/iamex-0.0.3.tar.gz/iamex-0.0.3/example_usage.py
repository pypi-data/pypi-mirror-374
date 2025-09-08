"""
Ejemplos de uso de la librería iamex
"""

from iamex import PromptClient

def ejemplo_basico():
    """Ejemplo básico de uso"""
    print("=== Ejemplo Básico ===")
    
    # Inicializar cliente sin API key por ahora
    client = PromptClient()
    
    # Enviar prompt simple
    try:
        response = client.send_prompt(
            prompt="Explica qué es la inteligencia artificial en una frase",
            modelo="IAM-advance-Mexico"
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_con_parametros():
    """Ejemplo con parámetros adicionales"""
    print("\n=== Ejemplo con Parámetros ===")
    
    client = PromptClient()
    
    try:
        response = client.send_prompt(
            prompt="¿Cuáles son las ventajas de usar Python?",
            modelo="IAM-advance-Mexico",
            temperature=0.7,
            max_tokens=200
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_obtener_modelos():
    """Ejemplo para obtener modelos disponibles"""
    print("\n=== Obtener Modelos ===")
    
    client = PromptClient()
    
    try:
        models = client.get_models()
        print("Modelos disponibles:", models)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_manejo_errores():
    """Ejemplo de manejo de errores"""
    print("\n=== Manejo de Errores ===")
    
    client = PromptClient()
    
    try:
        response = client.send_prompt(
            prompt="Este prompt fallará",
            modelo="IAM-advance-Mexico"
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error capturado correctamente: {e}")

if __name__ == "__main__":
    print("Ejemplos de uso de iamex")
    print("=" * 40)
    
    # Ejecutar ejemplos
    ejemplo_basico()
    ejemplo_con_parametros()
    ejemplo_obtener_modelos()
    ejemplo_manejo_errores()
    
    print("\n" + "=" * 40)
    print("Ejemplos completados")
