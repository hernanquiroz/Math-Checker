import re
from typing import Dict, Any
from providers.base_provider import BaseLLMProvider


class FormalChecker:
    """Verificación formal (Lean/Coq) asistida por LLM."""
    
    FORMAL_SYSTEMS = {
        "lean": r"(theorem|lemma|def|example|instance)\s+(\w+)",
        "coq": r"(Theorem|Lemma|Definition|Example)\s+(\w+)",
        "agda": r"(module|postulate|data)\s+(\w+)"
    }
    
    SYSTEM_PROMPT = """Eres un experto en asistentes de prueba formales (Lean 4, Coq, Agda).
Analiza el código formal y verifica sintaxis, tipos, pruebas y lógica.

FORMATO JSON:
{
  "formal_system": "lean|coq|agda|none",
  "has_errors": true/false,
  "errors": [
    {
      "type": "sintaxis|tipos|prueba|lógica",
      "severity": "crítico|medio|menor",
      "location": "línea o fragmento",
      "description": "explicación",
      "correction": "corrección",
      "engine": "Formal"
    }
  ],
  "summary": "resumen",
  "grade": "A|B|C|D|F"
}"""
    
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
    
    def detect_formal_system(self, text: str) -> str:
        for system, pattern in self.FORMAL_SYSTEMS.items():
            if re.search(pattern, text):
                return system
        return "none"
    
    def analyze_formal_code(self, text: str, page_number: int) -> Dict[str, Any]:
        system = self.detect_formal_system(text)
        
        if system == "none":
            return {
                "formal_system": "none",
                "has_errors": False,
                "errors": [],
                "summary": "No se detectó código formal",
                "grade": "-"
            }
        
        user_prompt = f"""Analiza el código {system.upper()} de la página #{page_number}:

--- CÓDIGO ---
{text}
--- FIN ---"""
        
        result = self.provider.chat(self.SYSTEM_PROMPT, user_prompt, temperature=0.1)
        result["formal_system"] = system
        return result
