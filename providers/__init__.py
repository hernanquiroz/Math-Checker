
from .ollama_provider import OllamaProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider


def get_provider(provider_name: str, api_key: str = None, model: str = None):
    providers = {
        "ollama": {
            "class": OllamaProvider,
            "default_model": "llama3.1",
            "models": ["llama3.1", "mistral", "codellama", "gemma2"]
        },
        "gemini": {
            "class": GeminiProvider,
            "default_model": "gemini-3.5-flash-lite",
            "models": ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-flash-latest"]
        },
        "groq": {
            "class": GroqProvider,
            "default_model": "llama-3.3-70b-versatile",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
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
