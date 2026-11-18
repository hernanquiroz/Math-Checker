import os
import json
from typing import Dict, Any
from google import genai
from google.genai import types
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Proveedor de Google Gemini con el NUEVO SDK (google-genai)."""
    
    def __init__(self, api_key: str = None, model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada. Obtén una en: https://aistudio.google.com/apikey")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "Google Gemini"
    
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt,
            )
            if json_mode:
                config.response_mime_type = "application/json"

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
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
            return {
                "error": f"JSON inválido: {str(e)}",
                "has_errors": True,
                "errors": [{"type": "sistema", "severity": "medio", "location": "N/A", "description": "Respuesta no parseable", "correction": "Reintentar"}],
                "summary": "", "grade": "?"
            }
        except Exception as e:
            msg = str(e)
            if "404" in msg or "not found" in msg.lower():
                hint = "Modelo no disponible. Usa 'gemini-3.5-flash-lite' o 'gemini-3.8-flash'. Los modelos 1.5/2.5 fueron retirados."
            elif "429" in msg or "quota" in msg.lower():
                hint = "Cuota gratis agotada. Espera unos minutos o cambia a Groq."
            elif "403" in msg:
                hint = "API key inválida. Regenera en aistudio.google.com/apikey"
            else:
                hint = "Verificar API key y conexión"
            
            return {
                "error": msg,
                "has_errors": True,
                "errors": [{"type": "sistema", "severity": "crítico", "location": "N/A", "description": f"Error Gemini: {msg}", "correction": hint}],
                "summary": "", "grade": "?"
            }
