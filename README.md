# 🎓 EduExtract: Intelligent Academic & Scientific Document Processing Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8.svg?style=flat&logo=OpenCV&logoColor=white)](https://opencv.org)
[![EasyOCR](https://img.shields.io/badge/EasyOCR-1.7+-4B8BBE.svg?style=flat)](https://github.com/JaidedAI/EasyOCR)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org)

**EduExtract** is a production-quality backend engineering system designed to parse, extract, and structure rich information from academic papers, scientific PDFs, and complex technical document images.

It follows **Clean Architecture** principles and provides high-performance extraction of plain text, headings, tables, mathematical equations, chemical compound names/formulas, chemical structure diagrams, scientific figures/graphs, captions, and references.

---

## 🌟 Key Features

- ✔ **Multi-Format Document Upload**: Process single/multi-page PDFs or batch image files (`.png`, `.jpg`, `.jpeg`, `.tiff`).
- ✔ **Image Preprocessing**: Skew correction, Otsu & Adaptive thresholding, bilateral noise reduction, and aspect-ratio preserving resizing.
- ✔ **OCR Engine**: Bounding box localization, text extraction, and confidence scoring via EasyOCR.
- ✔ **Table Extraction**: Morphological line detection and cell grid reconstruction mapped to OCR bounding boxes.
- ✔ **Math Equation Extraction**: Specialized math symbol density detection and automated LaTeX formatting (`$$...$$`).
- ✔ **Chemical Entity Extraction**: IUPAC nomenclature, SMILES strings, molecular formulas ($H_2SO_4$, $NaCl$, Ethanol, Benzene), and ring contour detection.
- ✔ **Scientific Figure & Graph Extraction**: Non-text region detection paired with nearby figure/table captions.
- ✔ **Multi-Format Export**: One-click download as **JSON**, **Markdown (.md)**, or **CSV Archive (.zip)**.
- ✔ **Production Backend**: Clean architecture, Pydantic validation, dependency injection, custom exception handling, structured logging, and containerized Docker setup.

---

## 🏗️ Backend Clean Architecture

```
eduextract/
├── backend/
│   ├── main.py                 # FastAPI Application & Global Middleware
│   ├── config/
│   │   └── settings.py         # Pydantic BaseSettings & Environment Config
│   ├── models/
│   │   └── schemas.py          # Request/Response Pydantic Models & DTOs
│   ├── routers/
│   │   ├── health.py           # GET /status (Health checks)
│   │   ├── upload.py           # POST /upload (File uploads & PDF rendering)
│   │   ├── extract.py          # POST /extract (Pipeline Orchestrator)
│   │   └── download.py         # GET /download (JSON, Markdown, CSV exports)
│   ├── services/
│   │   ├── preprocessing.py    # Noise removal, thresholding, skew correction
│   │   ├── ocr_service.py      # EasyOCR singleton wrapper
│   │   ├── text_extractor.py   # Headings hierarchy & reference parsing
│   │   ├── table_extractor.py  # OpenCV line detection & cell matrix building
│   │   ├── equation_extractor.py# Math formula parsing & LaTeX conversion
│   │   ├── chemical_extractor.py# IUPAC regex & molecular structure contours
│   │   └── graph_extractor.py  # Figures, charts & caption pairing
│   └── utils/
│       ├── image_utils.py      # OpenCV conversions & cropping helpers
│       ├── file_utils.py       # PDF rendering, temporary storage & exporters
│       └── logger.py           # Structured Python logger
├── frontend/
│   ├── app.py                  # Streamlit Multi-Tab Dashboard
│   └── utils.py                # REST API Client
├── tests/                      # Pytest Unit Test Suite
├── docker-compose.yml          # Container Orchestration
├── Dockerfile.backend          # FastAPI Docker Image
├── Dockerfile.frontend         # Streamlit Docker Image
├── requirements.txt            # Dependencies
└── ARCHITECTURE.md             # In-depth System Architecture Document
```

---

## ⚡ Quick Start with Docker (Recommended)

Run the entire system with a single command:

```bash
docker compose up --build
```

- **Streamlit Frontend Dashboard**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Status**: [http://localhost:8000/status](http://localhost:8000/status)

---

## 🛠️ Local Installation Guide (Without Docker)

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Backend Server
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run Frontend Dashboard
In a separate terminal window:
```bash
streamlit run frontend/app.py
```

---

## 📡 REST API Documentation

### 1. System Health Check
`GET /status`
- **Response**:
  ```json
  {
    "status": "healthy",
    "app_name": "EduExtract",
    "version": "1.0.0",
    "ocr_engine": "EasyOCR",
    "opencv_available": true
  }
  ```

### 2. Document Upload
`POST /upload`
- **Form Data**: `files` (Multipart PDF or image file list)
- **Response**:
  ```json
  {
    "document_id": "doc_a1b2c3d4e5",
    "filename": "sample_paper.pdf",
    "file_type": "PDF",
    "total_pages": 3,
    "message": "Upload processed successfully. Ready for extraction."
  }
  ```

### 3. Run Complete Extraction Pipeline
`POST /extract`
- **Body**:
  ```json
  {
    "document_id": "doc_a1b2c3d4e5",
    "enable_preprocessing": true,
    "extract_text": true,
    "extract_tables": true,
    "extract_equations": true,
    "extract_chemical": true,
    "extract_graphs": true
  }
  ```
- **Response**: `ExtractionResult` containing metadata, plain text, headings, tables, equations, chemical compounds/structures, figures, and references.

### 4. Download Results
`GET /download/{document_id}?format={json|markdown|csv}`
- **Formats**:
  - `json`: Structured JSON representation
  - `markdown`: Formatted Markdown document (`.md`)
  - `csv`: Zip archive containing extracted tables as `.csv` files

---

## 🧪 Running Unit Tests

Execute the unit test suite with `pytest`:

```bash
pytest tests/ -v
```

---

## 🚀 Future Improvements

1. **GPU Acceleration**: Enable CUDA acceleration for EasyOCR on GPU-enabled instances.
2. **Deep Learning Table Recognition**: Integrate Table Transformer (TATR) for complex nested tables.
3. **Advanced SMILES Extraction**: Integrate MolScribe / ChemDraw ML model for optical chemical structure recognition (OCSR).
4. **Vector Database Integration**: Add Qdrant/Pinecone embeddings for RAG over scientific papers.
