import re
from typing import List, Dict
import sympy as sp


class SymbolicMathChecker:
    """Verifica cálculos con SymPy (exacto y gratis)."""
    
    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')
    
    def check_derivative(self, expression: str, result: str, var='x') -> Dict:
        try:
            expr = sp.sympify(expression)
            expected = sp.sympify(result)
            computed = sp.diff(expr, sp.Symbol(var))
            is_correct = sp.simplify(computed - expected) == 0
            return {
                "correct": is_correct,
                "computed": str(computed) if not is_correct else None
            }
        except Exception as e:
            return {"correct": None, "error": str(e)}
    
    def check_integral(self, expression: str, result: str, var='x') -> Dict:
        try:
            result_sym = sp.sympify(result)
            expected = sp.sympify(expression)
            derivative = sp.diff(result_sym, sp.Symbol(var))
            is_correct = sp.simplify(derivative - expected) == 0
            return {"correct": is_correct}
        except Exception as e:
            return {"correct": None, "error": str(e)}
    
    def check_equality(self, lhs: str, rhs: str) -> Dict:
        try:
            lhs_sym = sp.sympify(lhs)
            rhs_sym = sp.sympify(rhs)
            is_correct = sp.simplify(lhs_sym - rhs_sym) == 0
            return {"correct": is_correct}
        except Exception as e:
            return {"correct": None, "error": str(e)}
    
    def extract_and_check(self, text: str) -> List[Dict]:
        """Extrae patrones matemáticos del texto y los verifica."""
        errors = []
        
        # Derivadas
        deriv_patterns = [
            r"d/d([a-z])\s*\(([^)]+)\)\s*=\s*([^.\n]+)",
            r"\frac\{d\}\{d([a-z])\}\s*\(([^)]+)\)\s*=\s*([^.\n]+)"
        ]
        for pattern in deriv_patterns:
            for match in re.finditer(pattern, text):
                var, expr, result = match.group(1), match.group(2), match.group(3)
                check = self.check_derivative(expr.strip(), result.strip(), var)
                if check.get("correct") is False:
                    errors.append({
                        "type": "cálculo",
                        "severity": "crítico",
                        "location": f"d/d{var}({expr}) = {result}",
                        "description": "La derivada es incorrecta",
                        "correction": f"El resultado correcto es: {check.get('computed', 'revisar')}",
                        "engine": "SymPy"
                    })
        
        # Integrales
        int_patterns = [r"∫\s*([^.\n]+?)\s*d([a-z])\s*=\s*([^.\n]+)"]
        for pattern in int_patterns:
            for match in re.finditer(pattern, text):
                expr, var, result = match.group(1), match.group(2), match.group(3)
                check = self.check_integral(expr.strip(), result.strip(), var)
                if check.get("correct") is False:
                    errors.append({
                        "type": "cálculo",
                        "severity": "crítico",
                        "location": f"∫{expr}d{var} = {result}",
                        "description": "La integral es incorrecta",
                        "correction": "Revisar técnicas de integración",
                        "engine": "SymPy"
                    })
        
        return errors
