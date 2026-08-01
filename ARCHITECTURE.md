# 🏛️ EduExtract System Architecture & Design Specification

EduExtract is designed as a **decoupled, modular micro-architecture** following the principles of **Clean Architecture** and **SOLID Design**.

---

## 📐 Architecture Diagram

```
                       +------------------------+
                       |   Streamlit Frontend   |
                       |  (User Dashboard App)  |
                       +-----------+------------+
                                   | REST API (HTTP)
                                   v
                       +------------------------+
                       |    FastAPI Backend     |
                       |       (main.py)        |
                       +-----------+------------+
                                   |
             +---------------------+---------------------+
             |                     |                     |
             v                     v                     v
     +---------------+     +---------------+     +---------------+
     |  routers/     |     |  routers/     |     |  routers/     |
     |   upload.py   |     |   extract.py  |     |  download.py  |
     +-------+-------+     +-------+-------+     +-------+-------+
             |                     |                     |
             |                     v (Dependency         |
             |                        Injection)         |
             |             +-----------------------+     |
             |             |  services/            |     |
             |             |   - preprocessing.py  |     |
             |             |   - ocr_service.py    |     |
             |             |   - text_extractor.py |     |
             |             |   - table_extractor.py|     |
             |             |   - equation_ext...   |     |
             |             |   - chemical_ext...   |     |
             |             |   - graph_ext...      |     |
             |             +-----------+-----------+     |
             |                         |                 |
             v                         v                 v
     +-----------------------------------------------------------+
     |                    utils/ & models/                       |
     |   - schemas.py (Pydantic DTOs)                            |
     |   - image_utils.py (OpenCV Transformation Utilities)      |
     |   - file_utils.py (PDF Render & Exporters JSON/MD/CSV)    |
     |   - logger.py (Structured Python Logging)                 |
     +-----------------------------------------------------------+
```

---

## 🔬 Core System Layers

### 1. Presentation Layer (`frontend/` & `backend/routers/`)
- **Streamlit Frontend**: Renders live document previews, handles drag-and-drop document uploads, displays processing status bars, and renders sectioned results with download options.
- **FastAPI APIRouters**: Endpoints (`/upload`, `/extract`, `/download`, `/status`) handle HTTP validation, multipart form parsing, and response serialization.

### 2. Service & Pipeline Layer (`backend/services/`)
- **Preprocessing Service**: Cleans input document images using bilateral noise reduction, skew correction via Hough line transform, and adaptive thresholding.
- **OCR Service**: Encapsulates EasyOCR into a thread-safe singleton wrapper that returns structured bounding box coordinates `[ymin, xmin, ymax, xmax]` and confidence scores.
- **Text & Heading Extractor**: Analyzes font spatial height and regex patterns to build document outlines and citation reference lists.
- **Table Extractor**: Isolates horizontal and vertical grid lines via OpenCV morphological operations (`MORPH_RECT`), builds cell matrices, and maps cell text from OCR items.
- **Equation Extractor**: Identifies dense mathematical notation, converts algebraic forms to LaTeX syntax, and flags display math blocks (`$$...$$`).
- **Chemical Extractor**: Parses IUPAC compound names, molecular formulas ($H_2SO_4$, $NaCl$, $C_6H_6$), and detects aromatic ring contours.
- **Graph Extractor**: Isolates visual non-text figures and charts, pairing them with adjacent captions (`Figure X:`).

### 3. Domain & Data Layer (`backend/models/` & `backend/utils/`)
- **Pydantic Schemas**: Strict data validation for requests, responses, bounding boxes, metadata, and extraction results.
- **File Utilities**: PDF rasterization via PyMuPDF (fitz), temporary storage management, and formatting exporters to Markdown and CSV Zip archives.

---

## ⚖️ Key Design Decisions

1. **Clean Architecture without Database Overhead**: Storage is managed cleanly on the local filesystem with structured UUIDs (`doc_xxxxxxxx`), ensuring zero external DB dependencies while keeping extraction stateless and easily scalable.
2. **Dependency Injection**: FastAPI `Depends` is used across router endpoints for easy service mockability and testing.
3. **Modular Pipeline**: Every extractor module operates independently; clients can selectively enable or disable individual extraction modules in `ExtractionRequest`.
