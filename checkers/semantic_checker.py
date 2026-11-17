from typing import Dict, Any
from providers.base_provider import BaseLLMProvider


SYSTEM_PROMPT = """Eres un revisor experto en matemáticas puras y aplicadas.
Analiza demostraciones y ejercicios identificando:

1. ERRORES LÓGICOS: saltos injustificados
2. ERRORES DE CÁLCULO: operaciones algebraicas incorrectas
3. ERRORES CONCEPTUALES: uso incorrecto de teoremas
4. ERRORES DE NOTACIÓN: símbolos mal usados
5. OMISIONES: casos no considerados

FORMATO JSON ESTRICTO:
{
  "has_errors": true/false,
  "errors": [
    {
      "type": "lógico|cálculo|conceptual|notación|omisión",
      "severity": "crítico|medio|menor",
      "location": "frase o línea aproximada",
      "description": "explicación del error",
      "correction": "cómo corregirlo",
      "engine": "LLM"
    }
  ],
  "summary": "resumen general",
  "grade": "A|B|C|D|F"
}

Si no hay errores, devuelve has_errors=false y errors=[]."""


class SemanticChecker:
    """Análisis semántico con LLM."""
    
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
    
    def analyze_page(self, page_text: str, page_number: int) -> Dict[str, Any]:
        user_prompt = f"""Analiza la página #{page_number} del documento matemático.

--- CONTENIDO ---
{page_text}
--- FIN ---"""
        
        result = self.provider.chat(SYSTEM_PROMPT, user_prompt, temperature=0.2)
        
        if "errors" not in result:
            result["errors"] = []
        if "has_errors" not in result:
            result["has_errors"] = len(result["errors"]) > 0
        if "summary" not in result:
            result["summary"] = ""
        if "grade" not in result:
            result["grade"] = "?"
        
        return result
