from .ollama_provider import OllamaProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider


def get_provider(provider_name: str, api_key: str = None, model: str = None):
    """Factory para obtener el proveedor correcto."""
    providers = {
        "ollama": {
            "class": OllamaProvider,
            "default_model": "llama3.1",
            "models": ["llama3.1", "mistral", "codellama", "gemma2"]
        },
        "gemini": {
            "class": GeminiProvider,
            "default_model": "gemini-1.5-flash",
            "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
        },
        "groq": {
            "class": GroqProvider,
            "default_model": "llama-3.1-70b-versatile",
            "models": [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768"
            ]
        },
        "openai": {
            "class": OpenAIProvider,
            "default_model": "gpt-4o-mini",
            "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
        }
    }
    
    if provider_name not in providers:
        raise ValueError(f"Proveedor no soportado: {provider_name}")
    
    config = providers[provider_name]
    model = model or config["default_model"]
    return config["class"](api_key=api_key, model=model), config["models"]
