from pdf2image import convert_from_bytes
import pytesseract
from typing import List
from .pdf_extractor import PageContent


def extract_pdf_with_ocr(pdf_bytes: bytes, lang: str = "spa+eng") -> List[PageContent]:
    """Extrae texto usando OCR (Tesseract) para PDFs escaneados."""
    pages = []
    
    try:
        images = convert_from_bytes(pdf_bytes, dpi=300)
        
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang=lang)
            
            pages.append(PageContent(
                page_number=i + 1,
                text=text.strip(),
                images=[img.tobytes()],
                source="ocr"
            ))
        
        return pages
    except Exception as e:
        raise RuntimeError(
            f"Error en OCR. Instala Tesseract:\n"
            f"  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils\n"
            f"  Mac: brew install tesseract tesseract-lang poppler\n"
            f"  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            f"Error: {str(e)}"
        )


def check_tesseract_available() -> bool:
    """Verifica si Tesseract está instalado."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
