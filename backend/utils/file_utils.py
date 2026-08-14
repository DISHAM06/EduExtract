import os
import fitz  # PyMuPDF
import json
import csv
import io
import zipfile
from pathlib import Path
from backend.utils.logger import logger

def save_uploaded_file(file_bytes: bytes, filename: str, target_dir: Path) -> Path:
    """Save bytes to target directory with a unique path or preserved name."""
    file_path = target_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path

def convert_pdf_to_images(pdf_path: Path, dpi: int = 200):
    """
    Renders PDF pages into OpenCV BGR numpy arrays using PyMuPDF.
    Returns list of (page_num, image_np).
    """
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to numpy array
            try:
                import numpy as np
                import cv2
            except Exception as e:
                logger.error("Missing dependencies for PDF image conversion: %s", e)
                raise RuntimeError("PDF to image conversion requires NumPy and OpenCV to be installed") from e

            img_data = np.frombuffer(pix.samples, dtype=np.uint8)
            if pix.alpha:
                img_np = img_data.reshape((pix.height, pix.width, 4))
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            else:
                img_np = img_data.reshape((pix.height, pix.width, 3))
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            images.append((page_index + 1, img_bgr))
        doc.close()
    except Exception as e:
        logger.error(f"Error rendering PDF {pdf_path}: {e}")
        raise ValueError(f"Failed to convert PDF to images: {str(e)}")
        
    return images

def export_to_markdown(extraction_data: dict) -> str:
    """Formats raw extraction dictionary into clean Markdown format."""
    md_lines = []
    doc_id = extraction_data.get("document_id", "Extracted Document")
    metadata = extraction_data.get("metadata", {})
    
    md_lines.append(f"# Academic Document Analysis: {doc_id}")
    md_lines.append(f"**Pages Analyzed**: {metadata.get('total_pages', 1)} | **Extracted At**: {metadata.get('processed_at', 'N/A')}\n")
    
    # Headings & Plain Text
    text_data = extraction_data.get("plain_text", [])
    if text_data:
        md_lines.append("## Document Content & Structure\n")
        headings = extraction_data.get("headings", [])
        if headings:
            md_lines.append("### Outline / Headings")
            for h in headings:
                indent = "  " * (h.get("level", 1) - 1)
                md_lines.append(f"{indent}- **{h.get('text')}** (Page {h.get('page')})")
            md_lines.append("")
        
        md_lines.append("### Full Extracted Text")
        for item in text_data:
            md_lines.append(item.get("text", ""))
        md_lines.append("")

    # Tables
    tables = extraction_data.get("tables", [])
    if tables:
        md_lines.append("## Extracted Tables\n")
        for idx, tbl in enumerate(tables, 1):
            md_lines.append(f"### Table {idx} (Page {tbl.get('page')})")
            matrix = tbl.get("matrix", [])
            if matrix:
                # Header line
                headers = matrix[0] if len(matrix) > 0 else []
                md_lines.append("| " + " | ".join(headers) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in matrix[1:]:
                    md_lines.append("| " + " | ".join(row) + " |")
            md_lines.append("")

    # Equations
    eqs = extraction_data.get("equations", [])
    if eqs:
        md_lines.append("## Mathematical Equations\n")
        for idx, eq in enumerate(eqs, 1):
            md_lines.append(f"**Equation {idx} (Page {eq.get('page')})**:")
            md_lines.append(f"$$\n{eq.get('equation_text')}\n$$\n")

    # Chemical Information
    chems = extraction_data.get("chemical_data", {})
    compounds = chems.get("compounds", [])
    structures = chems.get("structures", [])
    if compounds or structures:
        md_lines.append("## Chemical Entities & Structures\n")
        if compounds:
            md_lines.append("### Chemical Compounds & Formulas")
            for c in compounds:
                md_lines.append(f"- **{c.get('name')}** (Formula: `{c.get('formula')}`, Type: {c.get('type')})")
            md_lines.append("")
        if structures:
            md_lines.append(f"**Detected Chemical Structure Diagrams**: {len(structures)} visual elements identified.")
            md_lines.append("")

    # Figures & Graphs
    figs = extraction_data.get("figures", [])
    if figs:
        md_lines.append("## Scientific Figures & Graphs\n")
        for idx, fig in enumerate(figs, 1):
            caption = fig.get("caption", "No caption detected")
            md_lines.append(f"- **Figure {idx} (Page {fig.get('page')})**: {caption}")
        md_lines.append("")

    # References
    refs = extraction_data.get("references", [])
    if refs:
        md_lines.append("## References\n")
        for r in refs:
            md_lines.append(f"- {r.get('text')}")
        md_lines.append("")

    return "\n".join(md_lines)

def export_to_csv_zip(extraction_data: dict) -> bytes:
    """Generates a zip archive containing CSVs of all extracted tables."""
    zip_buffer = io.BytesIO()
    tables = extraction_data.get("tables", [])
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        if not tables:
            # Write empty summary csv if no tables found
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["Notice"])
            writer.writerow(["No structured tables found in document."])
            zip_file.writestr("summary.csv", csv_output.getvalue())
        else:
            for idx, tbl in enumerate(tables, 1):
                csv_output = io.StringIO()
                writer = csv.writer(csv_output)
                matrix = tbl.get("matrix", [])
                for row in matrix:
                    writer.writerow(row)
                zip_file.writestr(f"table_{idx}_page_{tbl.get('page', 1)}.csv", csv_output.getvalue())
                
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
