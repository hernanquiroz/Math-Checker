from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import List, Dict
import io


class DocxExporter:
    """Exporta el reporte a Word."""
    
    SEVERITY_COLORS = {
        "crítico": RGBColor(0xe7, 0x4c, 0x3c),
        "medio": RGBColor(0xf3, 0x9c, 0x12),
        "menor": RGBColor(0x34, 0x98, 0xdb)
    }
    
    def export(self, results: List[Dict]) -> bytes:
        doc = Document()
        
        title = doc.add_heading('Reporte de Análisis Matemático', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subtitle = doc.add_paragraph('MathChecker v2.0 - 100% Gratuito')
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        doc.add_heading('Resumen Ejecutivo', level=1)
        
        total_errors = sum(len(r.get('errors', [])) for r in results)
        critical = sum(1 for r in results for e in r.get('errors', [])
                      if e.get('severity') == 'crítico')
        
        summary_table = doc.add_table(rows=5, cols=2)
        summary_table.style = 'Light Grid Accent 1'
        
        metrics = [
            ("Métrica", "Valor"),
            ("Páginas analizadas", str(len(results))),
            ("Páginas con errores", str(sum(1 for r in results if r.get('has_errors')))),
            ("Total de errores", str(total_errors)),
            ("Errores críticos", str(critical))
        ]
        
        for i, (metric, value) in enumerate(metrics):
            summary_table.rows[i].cells[0].text = metric
            summary_table.rows[i].cells[1].text = value
        
        doc.add_paragraph()
        doc.add_heading('Análisis Detallado por Página', level=1)
        
        for result in results:
            page_num = result.get('page', '?')
            grade = result.get('grade', '?')
            errors = result.get('errors', [])
            
            doc.add_heading(f'Página {page_num} — Calificación: {grade}', level=2)
            
            if result.get('summary'):
                p = doc.add_paragraph()
                run = p.add_run(result['summary'])
                run.italic = True
            
            if errors:
                for error in errors:
                    severity = error.get('severity', 'medio')
                    color = self.SEVERITY_COLORS.get(severity, RGBColor(0, 0, 0))
                    
                    p = doc.add_paragraph()
                    run = p.add_run(f"● {severity.upper()} | ")
                    run.bold = True
                    run.font.color.rgb = color
                    
                    p.add_run(f"Tipo: {error.get('type', 'N/A')} | ")
                    p.add_run(f"Motor: {error.get('engine', 'N/A')}\n")
                    p.add_run(f"Ubicación: {error.get('location', 'N/A')}\n")
                    p.add_run(f"Error: {error.get('description', 'N/A')}\n")
                    p.add_run(f"Corrección: {error.get('correction', 'N/A')}")
                    
                    doc.add_paragraph()
            else:
                p = doc.add_paragraph('✓ Sin errores detectados')
                p.runs[0].font.color.rgb = RGBColor(0x27, 0xae, 0x60)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
