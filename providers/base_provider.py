from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    """Abstracción para proveedores de LLM."""
    
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        """Ejecuta una conversación con el LLM."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Retorna el nombre del modelo."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor."""
        pass
