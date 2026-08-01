import os
import json
import cv2
import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from backend.models.schemas import (
    ExtractionRequest,
    ExtractionResult,
    DocumentMetadata,
    OCRItem,
    HeadingItem,
    ReferenceItem,
    TableData,
    EquationData,
    ChemicalData,
    FigureData
)
from backend.config.settings import settings
from backend.services import (
    ImagePreprocessor,
    OCRService,
    TextExtractor,
    TableExtractor,
    EquationExtractor,
    ChemicalExtractor,
    GraphExtractor
)
from backend.utils.logger import logger

router = APIRouter(tags=["Extract"])

# Dependency Injection for services
def get_preprocessor():
    return ImagePreprocessor()

def get_ocr_service():
    return OCRService()

def get_text_extractor():
    return TextExtractor()

def get_table_extractor():
    return TableExtractor()

def get_equation_extractor():
    return EquationExtractor()

def get_chemical_extractor():
    return ChemicalExtractor()

def get_graph_extractor():
    return GraphExtractor()


@router.post("/extract", response_model=ExtractionResult, summary="Execute Document Extraction Pipeline")
async def extract_document(
    request: ExtractionRequest,
    preprocessor: ImagePreprocessor = Depends(get_preprocessor),
    ocr_service: OCRService = Depends(get_ocr_service),
    text_extractor: TextExtractor = Depends(get_text_extractor),
    table_extractor: TableExtractor = Depends(get_table_extractor),
    equation_extractor: EquationExtractor = Depends(get_equation_extractor),
    chemical_extractor: ChemicalExtractor = Depends(get_chemical_extractor),
    graph_extractor: GraphExtractor = Depends(get_graph_extractor)
):
    """
    Executes the modular academic extraction pipeline on an uploaded document ID.
    Performs preprocessing, OCR, text/headings, tables, equations, chemical entities, and scientific graphs extraction.
    """
    doc_dir = settings.UPLOAD_DIR / request.document_id
    if not doc_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document ID '{request.document_id}' not found. Please upload document first."
        )

    # Locate stored page image frames
    page_files = sorted(doc_dir.glob("page_*.png"), key=lambda p: int(p.stem.split("_")[1]))
    if not page_files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No page images found for this document.")

    all_ocr_items: List[OCRItem] = []
    all_headings: List[HeadingItem] = []
    all_references: List[ReferenceItem] = []
    all_tables: List[TableData] = []
    all_equations: List[EquationData] = []
    combined_compounds = []
    combined_structures = []
    all_figures: List[FigureData] = []

    logger.info(f"Starting extraction pipeline for document '{request.document_id}' across {len(page_files)} page(s).")

    for page_idx, page_path in enumerate(page_files, 1):
        image = cv2.imread(str(page_path))
        if image is None:
            continue

        # 1. Preprocessing
        if request.enable_preprocessing:
            image = preprocessor.process(image)

        # 2. OCR Processing
        page_ocr = ocr_service.extract_ocr_items(image, page_num=page_idx)
        all_ocr_items.extend(page_ocr)

        # 3. Text & Headings & References Extraction
        if request.extract_text:
            headings, refs = text_extractor.extract(page_ocr)
            all_headings.extend(headings)
            all_references.extend(refs)

        # 4. Table Extraction
        if request.extract_tables:
            tables = table_extractor.extract_tables(image, page_ocr, page_num=page_idx)
            all_tables.extend(tables)

        # 5. Equation Extraction
        if request.extract_equations:
            eqs = equation_extractor.extract_equations(page_ocr, page_num=page_idx)
            all_equations.extend(eqs)

        # 6. Chemical Data Extraction
        if request.extract_chemical:
            chem_data = chemical_extractor.extract_chemical_data(image, page_ocr, page_num=page_idx)
            combined_compounds.extend(chem_data.compounds)
            combined_structures.extend(chem_data.structures)

        # 7. Scientific Figures & Graphs Extraction
        if request.extract_graphs:
            figs = graph_extractor.extract_figures(image, page_ocr, page_num=page_idx)
            all_figures.extend(figs)

    metadata = DocumentMetadata(
        document_id=request.document_id,
        original_filename=f"{request.document_id}.pdf",
        file_type="PDF/IMAGE",
        file_size_bytes=sum(p.stat().st_size for p in page_files),
        total_pages=len(page_files),
        processed_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    result = ExtractionResult(
        document_id=request.document_id,
        status="completed",
        metadata=metadata,
        plain_text=all_ocr_items,
        headings=all_headings,
        references=all_references,
        tables=all_tables,
        equations=all_equations,
        chemical_data=ChemicalData(compounds=combined_compounds, structures=combined_structures),
        figures=all_figures
    )

    # Cache result JSON to export directory
    export_json_path = settings.EXPORT_DIR / f"{request.document_id}.json"
    with open(export_json_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2)

    logger.info(f"Completed extraction for '{request.document_id}'. Result saved to {export_json_path}.")

    return result
