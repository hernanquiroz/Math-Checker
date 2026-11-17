from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from typing import List, Dict
import io


class PDFExporter:
    """Exporta el reporte a PDF."""
    
    SEVERITY_COLORS = {
        "crítico": HexColor("#e74c3c"),
        "medio": HexColor("#f39c12"),
        "menor": HexColor("#3498db")
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            'TitleCustom', parent=self.styles['Title'],
            fontSize=22, textColor=HexColor("#2c3e50"), spaceAfter=20
        ))
        self.styles.add(ParagraphStyle(
            'HeadingCustom', parent=self.styles['Heading2'],
            fontSize=14, textColor=HexColor("#34495e"), spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            'ErrorText', parent=self.styles['Normal'],
            fontSize=10, leftIndent=10, spaceAfter=5
        ))
    
    def export(self, results: List[Dict], filename: str = "reporte_matematico.pdf") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        
        story = []
        
        story.append(Paragraph("📊 Reporte de Análisis Matemático", self.styles['TitleCustom']))
        story.append(Paragraph("MathChecker v2.0 - 100% Gratuito", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        total_errors = sum(len(r.get('errors', [])) for r in results)
        critical = sum(1 for r in results for e in r.get('errors', [])
                      if e.get('severity') == 'crítico')
        pages_with_errors = sum(1 for r in results if r.get('has_errors'))
        
        story.append(Paragraph("Resumen Ejecutivo", self.styles['HeadingCustom']))
        summary_data = [
            ["Métrica", "Valor"],
            ["Páginas analizadas", str(len(results))],
            ["Páginas con errores", str(pages_with_errors)],
            ["Total de errores", str(total_errors)],
            ["Errores críticos", str(critical)]
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#2c3e50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor("#ecf0f1")),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdc3c7"))
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Análisis Detallado por Página", self.styles['HeadingCustom']))
        
        for result in results:
            page_num = result.get('page', '?')
            grade = result.get('grade', '?')
            errors = result.get('errors', [])
            
            story.append(Paragraph(
                f"<b>Página {page_num}</b> — Calificación: {grade} — "
                f"{len(errors)} error(es)",
                self.styles['HeadingCustom']
            ))
            
            if result.get('summary'):
                story.append(Paragraph(
                    f"<i>{result['summary']}</i>", self.styles['ErrorText']
                ))
            
            if errors:
                for error in errors:
                    severity = error.get('severity', 'medio')
                    color = self.SEVERITY_COLORS.get(severity, HexColor("#000000"))
                    
                    error_text = f"""
                    <font color="{color.hexval()}">● {severity.upper()}</font> |
                    <b>Tipo:</b> {error.get('type', 'N/A')} |
                    <b>Motor:</b> {error.get('engine', 'N/A')}<br/>
                    <b>Ubicación:</b> {error.get('location', 'N/A')}<br/>
                    <b>Error:</b> {error.get('description', 'N/A')}<br/>
                    <b>Corrección:</b> {error.get('correction', 'N/A')}
                    """
                    story.append(Paragraph(error_text, self.styles['ErrorText']))
                    story.append(Spacer(1, 8))
            else:
                story.append(Paragraph("✓ Sin errores detectados", self.styles['ErrorText']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return buffer.getvalue()
