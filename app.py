import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from providers import get_provider
from extractors import extract_pdf_by_pages, get_page_preview, extract_pdf_with_ocr, check_tesseract_available
from checkers import SymbolicMathChecker, SemanticChecker, FormalChecker
from exporters import PDFExporter, DocxExporter

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="🧮 MathChecker v2.0 - Gratuito",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .error-card {
        background: linear-gradient(135deg, #fee 0%, #fcc 100%);
        padding: 15px; border-radius: 10px;
        border-left: 5px solid #e74c3c; margin: 10px 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        padding: 15px; border-radius: 10px;
        border-left: 5px solid #f39c12; margin: 10px 0;
    }
    .info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 15px; border-radius: 10px;
        border-left: 5px solid #2196f3; margin: 10px 0;
    }
    .grade-A { color: #27ae60; font-weight: bold; font-size: 24px; }
    .grade-B { color: #2ecc71; font-weight: bold; font-size: 24px; }
    .grade-C { color: #f39c12; font-weight: bold; font-size: 24px; }
    .grade-D { color: #e67e22; font-weight: bold; font-size: 24px; }
    .grade-F { color: #e74c3c; font-weight: bold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("⚙️ Configuración")
    
    st.subheader("🤖 Proveedor LLM (GRATIS)")
    provider_choice = st.selectbox(
        "Elige uno",
        ["Ollama (local, recomendado)", "Google Gemini (gratis)", "Groq (gratis rápido)", "OpenAI (pago)"]
    )
    
    provider_map = {
        "Ollama (local, recomendado)": ("ollama", None, ["llama3.1", "mistral", "codellama", "gemma2"]),
        "Google Gemini (gratis)": ("gemini", "GEMINI_API_KEY", ["gemini-1.5-flash", "gemini-1.5-pro"]),
        "Groq (gratis rápido)": ("groq", "GROQ_API_KEY", ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]),
        "OpenAI (pago)": ("openai", "OPENAI_API_KEY", ["gpt-4o-mini", "gpt-4o"])
    }
    
    prov_name, env_key, models = provider_map[provider_choice]
    
    if env_key:
        api_key = st.text_input(
            f"🔑 API Key ({prov_name.upper()})",
            type="password",
            value=os.getenv(env_key, ""),
            help=f"Obtén gratis en: {'https://aistudio.google.com/apikey' if 'gemini' in prov_name else 'https://console.groq.com' if 'groq' in prov_name else 'https://platform.openai.com'}"
        )
    else:
        api_key = None
        st.info("💡 Ollama no requiere API key. Solo instala Ollama y descarga un modelo.")
    
    model = st.selectbox("Modelo", models)
    
    st.markdown("---")
    st.subheader("📄 Extracción")
    extraction_method = st.radio(
        "Método",
        ["Texto nativo (rápido)", "OCR Tesseract (escaneados)"]
    )
    
    if "OCR" in extraction_method and not check_tesseract_available():
        st.warning("⚠️ Tesseract no instalado. Ver README.")
    
    st.markdown("---")
    st.subheader("🔬 Motores")
    use_symbolic = st.checkbox("✅ SymPy (cálculos exactos)", value=True)
    use_semantic = st.checkbox("✅ LLM (razonamiento)", value=True)
    use_formal = st.checkbox("✅ Lean/Coq (formal)", value=True)
    
    st.markdown("---")
    teacher_mode = st.checkbox("👨‍🏫 Modo profesor", help="Comparar con solucionario")


# ============================================================
# HEADER
# ============================================================
st.title("🧮 MathChecker v2.0")
st.markdown("### Detector Inteligente de Errores Matemáticos - 100% Gratuito")
st.markdown(f"**Motor:** {provider_choice} ({model}) | **Extracción:** {extraction_method}")


# ============================================================
# UPLOAD
# ============================================================
uploaded_file = st.file_uploader("📄 Sube tu PDF matemático", type=["pdf"])

solution_file = None
if teacher_mode:
    solution_file = st.file_uploader("📚 Solucionario (opcional)", type=["pdf"])


# ============================================================
# PROCESAMIENTO
# ============================================================
if uploaded_file:
    needs_key = env_key is not None
    has_key = bool(api_key)
    
    if needs_key and not has_key:
        st.error(f"❌ Configura tu {env_key} en el sidebar o en .env")
    else:
        if st.button("🔍 Analizar documento", type="primary", use_container_width=True):
            pdf_bytes = uploaded_file.read()
            solution_bytes = solution_file.read() if solution_file else None
            
            # 1. EXTRACCIÓN
            with st.spinner("📖 Extrayendo contenido..."):
                try:
                    if "OCR" in extraction_method:
                        pages = extract_pdf_with_ocr(pdf_bytes)
                    else:
                        pages = extract_pdf_by_pages(pdf_bytes)
                    st.session_state['pages'] = pages
                    st.session_state['pdf_bytes'] = pdf_bytes
                    st.success(f"✅ {len(pages)} páginas extraídas")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.stop()
            
            # 2. PROVEEDOR LLM
            try:
                provider, _ = get_provider(prov_name, api_key=api_key, model=model)
            except Exception as e:
                st.error(f"❌ Error LLM: {str(e)}")
                st.stop()
            
            # 3. ANÁLISIS
            with st.spinner("🧠 Analizando..."):
                symbolic = SymbolicMathChecker() if use_symbolic else None
                semantic = SemanticChecker(provider) if use_semantic else None
                formal = FormalChecker(provider) if use_formal else None
                
                results = []
                progress = st.progress(0)
                
                for i, page in enumerate(pages):
                    if not page.text.strip():
                        progress.progress((i + 1) / len(pages))
                        continue
                    
                    page_result = {
                        "page": page.page_number,
                        "source": page.source,
                        "errors": [],
                        "has_errors": False,
                        "summary": "",
                        "grade": "?"
                    }
                    
                    if symbolic:
                        page_result["errors"].extend(symbolic.extract_and_check(page.text))
                    
                    if formal:
                        fr = formal.analyze_formal_code(page.text, page.page_number)
                        if fr.get("formal_system") != "none":
                            page_result["errors"].extend(fr.get("errors", []))
                            page_result["summary"] += f"[{fr['formal_system'].upper()}] {fr.get('summary', '')} "
                    
                    if semantic:
                        lr = semantic.analyze_page(page.text, page.page_number)
                        page_result["errors"].extend(lr.get("errors", []))
                        page_result["summary"] += lr.get("summary", "")
                        page_result["grade"] = lr.get("grade", "?")
                    
                    page_result["has_errors"] = len(page_result["errors"]) > 0
                    results.append(page_result)
                    progress.progress((i + 1) / len(pages))
                
                st.session_state['results'] = results
            
            st.success("✅ ¡Análisis completado!")
            st.rerun()


# ============================================================
# RESULTADOS
# ============================================================
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    pdf_bytes = st.session_state['pdf_bytes']
    
    total_errors = sum(len(r['errors']) for r in results)
    critical = sum(1 for r in results for e in r['errors'] if e.get('severity') == 'crítico')
    pages_err = sum(1 for r in results if r['has_errors'])
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Páginas", len(results))
    c2.metric("⚠️ Con errores", pages_err)
    c3.metric("🔴 Errores", total_errors)
    c4.metric("🚨 Críticos", critical)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Descargar PDF",
            data=PDFExporter().export(results),
            file_name="reporte.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "📥 Descargar Word",
            data=DocxExporter().export(results),
            file_name="reporte.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    st.markdown("---")
    st.subheader("📑 Análisis por página")
    
    for result in results:
        page_num = result['page']
        
        with st.expander(
            f"{'🔴' if result['has_errors'] else '🟢'} Página {page_num} "
            f"— {len(result['errors'])} error(es) — {result['grade']}",
            expanded=(result['has_errors'] and any(e.get('severity') == 'crítico' for e in result['errors']))
        ):
            col_p, col_a = st.columns([1, 2])
            
            with col_p:
                try:
                    img = get_page_preview(pdf_bytes, page_num)
                    st.image(img, use_column_width=True)
                except Exception:
                    pass
            
            with col_a:
                if result.get('summary'):
                    st.info(f"💭 {result['summary']}")
                
                grade = result.get('grade', '?')
                st.markdown(f"**Calificación:** <span class='grade-{grade}'>{grade}</span>",
                           unsafe_allow_html=True)
                
                if result['errors']:
                    for error in result['errors']:
                        sev = error.get('severity', 'medio')
                        card = {'crítico': 'error-card', 'medio': 'warning-card', 'menor': 'info-card'}.get(sev, 'info-card')
                        
                        st.markdown(f"""
                        <div class="{card}">
                            <b>🏷️ {error.get('type', 'N/A')}</b> | 
                            <b>⚡ {sev}</b> | 
                            <b>🔬 {error.get('engine', 'N/A')}</b><br>
                            <b>📍 {error.get('location', 'N/A')}</b><br>
                            <b>❌ {error.get('description', 'N/A')}</b><br>
                            <b>✅ {error.get('correction', 'N/A')}</b>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✨ Sin errores")


st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;'><small>🧮 MathChecker v2.0 | 100% Gratuito | SymPy + LLM</small></div>",
            unsafe_allow_html=True)
