import os
import json
from typing import Dict, Any
from openai import OpenAI
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Proveedor de OpenAI (opcional, de pago)."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "OpenAI"
    
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            if json_mode:
                return json.loads(content)
            return {"content": content}
        except Exception as e:
            return {"error": str(e), "has_errors": True, "errors": [{
                "type": "sistema",
                "severity": "crítico",
                "location": "N/A",
                "description": f"Error OpenAI: {str(e)}",
                "correction": "Verificar API key y cuota"
            }]}
