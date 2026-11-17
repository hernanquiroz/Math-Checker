import fitz
from dataclasses import dataclass, field
from typing import List


@dataclass
class PageContent:
    page_number: int
    text: str
    images: List[bytes] = field(default_factory=list)
    source: str = "pdf-text"


def extract_pdf_by_pages(pdf_bytes: bytes) -> List[PageContent]:
    """Extrae el contenido del PDF página por página."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                images.append(base_image["image"])
            except Exception:
                pass
        
        pages.append(PageContent(
            page_number=i + 1,
            text=text.strip(),
            images=images,
            source="pdf-text"
        ))
    
    doc.close()
    return pages


def get_page_preview(pdf_bytes: bytes, page_number: int) -> bytes:
    """Renderiza una página del PDF como imagen PNG."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def get_total_pages(pdf_bytes: bytes) -> int:
    """Retorna el número total de páginas."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    doc.close()
    return total
