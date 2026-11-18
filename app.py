import streamlit as st
import os
import hashlib
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

from providers import get_provider
from extractors import extract_pdf_by_pages, get_page_preview, extract_pdf_with_ocr, check_tesseract_available
from checkers import SymbolicMathChecker, SemanticChecker, FormalChecker
from exporters import PDFExporter, DocxExporter

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(page_title="🧮 MathChecker v2.0", page_icon="🧮", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .error-card { background: linear-gradient(135deg, #fee 0%, #fcc 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #e74c3c; margin: 10px 0; }
    .warning-card { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #f39c12; margin: 10px 0; }
    .info-card { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; margin: 10px 0; }
    .grade-A { color: #27ae60; font-weight: bold; font-size: 24px; }
    .grade-B { color: #2ecc71; font-weight: bold; font-size: 24px; }
    .grade-C { color: #f39c12; font-weight: bold; font-size: 24px; }
    .grade-D { color: #e67e22; font-weight: bold; font-size: 24px; }
    .grade-F { color: #e74c3c; font-weight: bold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS: API Key y Caché (SOLUCIÓN AL "CICLO INFINITO" Y LENTITUD)
# ============================================================
def get_api_key(env_name: str) -> str:
    try:
        if env_name in st.secrets:
            return st.secrets[env_name]
    except Exception:
        pass
    return os.getenv(env_name, "")

MAX_WORKERS = 2
MAX_CHARS = 6000
MAX_RETRIES = 3

@st.cache_data(show_spinner=False)
def _analyze_one_page(page_text: str, page_number: int, prov_name: str, api_key: str, model: str, use_symbolic: bool, use_semantic: bool, use_formal: bool) -> dict:
    text = page_text[:MAX_CHARS]
    symbolic = SymbolicMathChecker() if use_symbolic else None
    provider, _ = get_provider(prov_name, api_key=api_key, model=model)
    semantic = SemanticChecker(provider) if use_semantic else None
    formal = FormalChecker(provider) if use_formal else None

    page_result = {"page": page_number, "source": "pdf-text", "errors": [], "has_errors": False, "summary": "", "grade": "?"}

    if symbolic:
        page_result["errors"].extend(symbolic.extract_and_check(text))

    for attempt in range(MAX_RETRIES):
        try:
            if formal:
                fr = formal.analyze_formal_code(text, page_number)
                if fr.get("formal_system") != "none":
                    page_result["errors"].extend(fr.get("errors", []))
                    page_result["summary"] += f"[{fr['formal_system'].upper()}] {fr.get('summary', '')} "

            if semantic:
                lr = semantic.analyze_page(text, page_number)
                err_msg = " ".join(str(e.get("description", "")) for e in lr.get("errors", []))
                if ("429" in err_msg or "quota" in err_msg.lower()) and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt + random.random())
                    continue
                page_result["errors"].extend(lr.get("errors", []))
                page_result["summary"] += lr.get("summary", "")
                page_result["grade"] = lr.get("grade", "?")
            break
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            page_result["errors"].append({"type": "sistema", "severity": "medio", "location": "N/A", "description": f"Fallo tras {MAX_RETRIES} intentos: {e}", "correction": "Reintentar o cambiar modelo", "engine": "LLM"})

    page_result["has_errors"] = len(page_result["errors"]) > 0
    return page_result

def _page_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("⚙️ Configuración")
    st.subheader("🤖 Proveedor LLM")
    
    provider_choice = st.selectbox("Elige uno", [
        "Google Gemini (RECOMENDADO - gratis)",
        "Groq (gratis, muy rápido)",
        "Ollama (solo local, NO en cloud)",
        "OpenAI (de pago)",
    ])

    provider_map = {
        "Google Gemini (RECOMENDADO - gratis)": ("gemini", "GEMINI_API_KEY", ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-flash-latest"], "https://aistudio.google.com/apikey"),
        "Groq (gratis, muy rápido)": ("groq", "GROQ_API_KEY", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"], "https://console.groq.com/keys"),
        "Ollama (solo local, NO en cloud)": ("ollama", None, ["llama3.1", "mistral", "codellama", "gemma2"], None),
        "OpenAI (de pago)": ("openai", "OPENAI_API_KEY", ["gpt-4o-mini", "gpt-4o"], "https://platform.openai.com/api-keys"),
    }

    prov_name, env_key, models, signup_url = provider_map[provider_choice]
    api_key = ""
    
    if env_key:
        api_key = get_api_key(env_key)
        if api_key:
            st.success(f"✅ API Key detectada ({env_key})")
            st.caption(f"Key: {api_key[:8]}...{api_key[-4:]}")
        else:
            st.error(f"❌ No hay API Key de {prov_name.upper()}")
            if signup_url:
                st.markdown(f"👉 Consíguela gratis en: [{signup_url}]({signup_url})")
            st.markdown("👉 Guárdala en **Settings → Secrets** de Streamlit Cloud")
            api_key = st.text_input("O pégala aquí (temporal):", type="password")
    else:
        st.warning("⚠️ Ollama solo funciona en local, NO en Streamlit Cloud")

    model = st.selectbox("Modelo", models)
    st.markdown("---")
    st.subheader("📄 Extracción")
    extraction_method = st.radio("Método", ["Texto nativo (rápido)", "OCR Tesseract (escaneados)"])
    
    if "OCR" in extraction_method and not check_tesseract_available():
        st.warning("⚠️ Tesseract no instalado en el servidor. Usa texto nativo.")
    
    st.markdown("---")
    st.subheader("🔬 Motores")
    use_symbolic = st.checkbox("✅ SymPy (cálculos exactos)", value=True)
    use_semantic = st.checkbox("✅ LLM (razonamiento)", value=True)
    use_formal = st.checkbox("✅ Lean/Coq (formal)", value=True)
    st.markdown("---")
    teacher_mode = st.checkbox("👨‍🏫 Modo profesor", help="Comparar con solucionario")

# ============================================================
# HEADER Y UPLOAD
# ============================================================
st.title("🧮 MathChecker v2.0")
st.markdown("### Detector Inteligente de Errores Matemáticos - 100% Gratuito")
st.markdown(f"**Motor:** {provider_choice} ({model}) | **Extracción:** {extraction_method}")

uploaded_file = st.file_uploader("📄 Sube tu PDF matemático", type=["pdf"])
solution_file = st.file_uploader("📚 Solucionario (opcional)", type=["pdf"]) if teacher_mode else None

# ============================================================
# PROCESAMIENTO
# ============================================================
if uploaded_file:
    needs_key = env_key is not None
    if needs_key and not api_key:
        st.error("❌ Necesitas configurar la API Key. Revisa el sidebar.")
    else:
        if st.button("🔍 Analizar documento", type="primary", use_container_width=True):
            pdf_bytes = uploaded_file.read()
            
            with st.spinner("📖 Extrayendo contenido..."):
                try:
                    pages = extract_pdf_with_ocr(pdf_bytes) if "OCR" in extraction_method else extract_pdf_by_pages(pdf_bytes)
                    st.session_state["pages"] = pages
                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.success(f"✅ {len(pages)} páginas extraídas")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.stop()

            useful_pages = [p for p in pages if len(p.text.strip()) > 20]
            skipped = len(pages) - len(useful_pages)
            if skipped:
                st.info(f"⏭️ {skipped} páginas vacías ignoradas (ahorro de tiempo)")

            if "partial_results" not in st.session_state:
                st.session_state["partial_results"] = {}
            st.session_state["cancel_flag"] = False

            col_btn, col_bar = st.columns([1, 4])
            with col_btn:
                if st.button("⏹️ Detener", use_container_width=True):
                    st.session_state["cancel_flag"] = True
            
            progress = st.progress(0)
            status = st.empty()
            results = []

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
                futures = {
                    ex.submit(_analyze_one_page, p.text, p.page_number, prov_name, api_key, model, use_symbolic, use_semantic, use_formal): p
                    for p in useful_pages
                }
                done = 0
                for fut in as_completed(futures):
                    if st.session_state["cancel_flag"]:
                        status.warning("⏹️ Análisis detenido. Reanuda con 'Analizar'.")
                        break
                    p = futures[fut]
                    try:
                        r = fut.result()
                        results.append(r)
                        st.session_state["partial_results"][_page_hash(p.text)] = r
                    except Exception as e:
                        st.error(f"Página {p.page_number}: {e}")
                    done += 1
                    progress.progress(done / len(useful_pages))
                    status.info(f"🔍 {done}/{len(useful_pages)} páginas (paralelo x{MAX_WORKERS})")

            results.sort(key=lambda r: r["page"])
            st.session_state["results"] = results
            st.success("✅ ¡Análisis completado!")
            st.rerun()

# ============================================================
# RESULTADOS
# ============================================================
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    pdf_bytes = st.session_state["pdf_bytes"]

    total_errors = sum(len(r["errors"]) for r in results)
    critical = sum(1 for r in results for e in r["errors"] if e.get("severity") == "crítico")
    pages_err = sum(1 for r in results if r["has_errors"])

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Páginas", len(results))
    c2.metric("⚠️ Con errores", pages_err)
    c3.metric("🔴 Errores", total_errors)
    c4.metric("🚨 Críticos", critical)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Descargar PDF", data=PDFExporter().export(results), file_name="reporte.pdf", mime="application/pdf", use_container_width=True)
    with col2:
        st.download_button("📥 Descargar Word", data=DocxExporter().export(results), file_name="reporte.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    st.markdown("---")
    st.subheader("📑 Análisis por página")

    for result in results:
        page_num = result["page"]
        with st.expander(f"{'🔴' if result['has_errors'] else '🟢'} Página {page_num} — {len(result['errors'])} error(es) — {result['grade']}", expanded=(result['has_errors'] and any(e.get("severity") == "crítico" for e in result["errors"]))):
            col_p, col_a = st.columns([1, 2])
            with col_p:
                try:
                    st.image(get_page_preview(pdf_bytes, page_num), use_column_width=True)
                except Exception:
                    pass
            with col_a:
                if result.get("summary"):
                    st.info(f"💭 {result['summary']}")
                grade = result.get("grade", "?")
                st.markdown(f"**Calificación:** <span class='grade-{grade}'>{grade}</span>", unsafe_allow_html=True)
                
                if result["errors"]:
                    for error in result["errors"]:
                        sev = error.get("severity", "medio")
                        card = {"crítico": "error-card", "medio": "warning-card", "menor": "info-card"}.get(sev, "info-card")
                        st.markdown(f"""
                        <div class="{card}">
                            <b>🏷️ {error.get('type', 'N/A')}</b> | <b>⚡ {sev}</b> | <b>🔬 {error.get('engine', 'N/A')}</b><br>
                            <b>📍 {error.get('location', 'N/A')}</b><br>
                            <b>❌ {error.get('description', 'N/A')}</b><br>
                            <b>✅ {error.get('correction', 'N/A')}</b>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✨ Sin errores")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;'><small>🧮 MathChecker v2.0 | 100% Gratuito | SymPy + Gemini</small></div>", unsafe_allow_html=True)
