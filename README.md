# 🧮 MathChecker v2.0

Detector inteligente de errores en demostraciones y ejercicios matemáticos. 
**100% gratuito** - usa modelos de IA sin costo.

## ✨ Características

- 🔍 **Detección de errores** en demostraciones matemáticas
- 📄 **Soporte PDF** (texto nativo y escaneados con OCR)
- 🧠 **Motor híbrido**: SymPy (exacto) + LLM (razonamiento)
- 🆓 **100% gratis**: Ollama local, Google Gemini, Groq
- 📊 **Exportación** a PDF y Word
- 👨‍🏫 **Modo profesor**: comparar con solucionario
- 🔬 **Verificación formal** de código Lean/Coq

## 🚀 Instalación rápida

### 1. Clonar repositorio
```bash
git clone https://github.com/TU_USUARIO/math-checker-v2.git
cd math-checker-v2
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar Tesseract (para OCR)
```bash
# Ubuntu/Debian:
sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils

# Mac:
brew install tesseract tesseract-lang poppler

# Windows: descargar de https://github.com/UB-Mannheim/tesseract/wiki
```

### 5. Configurar LLM (elige UNO)

#### Opción A: Ollama (100% local, recomendado)
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull llama3.1
ollama pull mistral
```

#### Opción B: Google Gemini (gratis, en la nube)
1. Ve a https://aistudio.google.com/apikey
2. Crea una API key gratis
3. Guárdala en `.env`: `GEMINI_API_KEY=tu_key`

#### Opción C: Groq (gratis, muy rápido)
1. Ve a https://console.groq.com
2. Crea cuenta y obtén API key
3. Guárdala en `.env`: `GROQ_API_KEY=tu_key`

### 6. Ejecutar
```bash
streamlit run app.py
```

## 📊 Comparativa de proveedores gratuitos

| Proveedor | Velocidad | Calidad | Privacidad | Límite |
|-----------|-----------|---------|------------|--------|
| Ollama | Media | Alta | 🔒 Total | ∞ |
| Gemini | Rápida | Alta | Nube | 15/min |
| Groq | Muy rápida | Alta | Nube | 30/min |

## 🛠️ Tecnologías

- **Streamlit** - Interfaz web
- **SymPy** - Motor simbólico exacto
- **PyMuPDF** - Extracción de PDF
- **Tesseract** - OCR gratuito
- **Ollama/Gemini/Groq** - LLMs gratuitos
- **ReportLab** - Exportación PDF
- **python-docx** - Exportación Word

## 📄 Licencia

MIT License - ver archivo LICENSE
