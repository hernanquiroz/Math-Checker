import json
from typing import Dict, Any
import ollama
from .base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Proveedor de Ollama (100% local y gratis)."""
    
    def __init__(self, api_key: str = None, model: str = "llama3.1"):
        self.model = model
        # Verificar que Ollama esté corriendo
        try:
            ollama.list()
        except Exception as e:
            raise RuntimeError(
                f"Ollama no está corriendo. Instálalo desde https://ollama.com\n"
                f"Luego ejecuta: ollama pull {model}\n"
                f"Error: {str(e)}"
            )
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "Ollama (Local)"
    
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, json_mode: bool = True) -> Dict[str, Any]:
        try:
            if json_mode:
                user_prompt += "\n\nResponde ÚNICAMENTE con JSON válido, sin texto adicional."
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": temperature}
            )
            
            content = response["message"]["content"]
            
            if json_mode:
                # Limpiar posibles markdown code blocks
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
                "description": f"Error Ollama: {str(e)}",
                "correction": "Verificar que Ollama esté corriendo"
            }]}
