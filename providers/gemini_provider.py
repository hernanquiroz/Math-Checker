import os
import json
from typing import Dict, Any
import google.generativeai as genai
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Proveedor de Google Gemini (gratis con límites)."""
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada.\n"
                "Obtén una gratis en: https://aistudio.google.com/apikey"
            )
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "Google Gemini"
    
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        try:
            if json_mode:
                user_prompt += "\n\nResponde ÚNICAMENTE con JSON válido, sin texto adicional."
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            
            content = response.text
            
            if json_mode:
                content = content.strip()
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                    if content.startswith("json"):
                        content = content[4:]
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
                "description": f"Error Gemini: {str(e)}",
                "correction": "Verificar API key y cuota"
            }]}
