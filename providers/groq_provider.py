import os
import json
from typing import Dict, Any
from groq import Groq
from .base_provider import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    """Proveedor de Groq (gratis, muy rápido)."""
    
    def __init__(self, api_key: str = None, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY no configurada.\n"
                "Obtén una gratis en: https://console.groq.com"
            )
        
        self.client = Groq(api_key=self.api_key)
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "Groq"
    
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        try:
            if json_mode:
                user_prompt += "\n\nResponde ÚNICAMENTE con JSON válido."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else None
            )
            
            content = response.choices[0].message.content
            
            if json_mode:
                return json.loads(content)
            return {"content": content}
        except json.JSONDecodeError as e:
            return {"error": f"JSON inválido: {str(e)}", "raw": content,
                    "has_errors": True, "errors": []}
        except Exception as e:
            return {"error": str(e), "has_errors": True, "errors": [{
                "type": "sistema",
                "severity": "crítico",
                "location": "N/A",
                "description": f"Error Groq: {str(e)}",
                "correction": "Verificar API key y cuota"
            }]}
