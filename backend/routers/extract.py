import datetime
from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import (
    ExtractionRequest,
    ExtractionResult,
    DocumentMetadata,
    ChemicalData,
)
from backend.config.settings import settings
from backend.utils.logger import logger

router = APIRouter(tags=["Extract"])


@router.post("/extract", response_model=ExtractionResult, summary="Execute Document Extraction Pipeline (chemistry-only)")
async def extract_document(request: ExtractionRequest):
    """
    Simplified extraction endpoint kept for chemistry-focused workflows.
    This endpoint currently only validates document presence and returns an empty chemical result.
    The legacy multi-extractor pipeline has been removed.
    """
    doc_dir = settings.UPLOAD_DIR / request.document_id
    if not doc_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document ID '{request.document_id}' not found. Please upload document first."
        )

    # Build minimal metadata
    page_files = list(doc_dir.glob("page_*.png"))
    metadata = DocumentMetadata(
        document_id=request.document_id,
        original_filename=f"{request.document_id}.pdf",
        file_type="PDF/IMAGE",
        file_size_bytes=sum(p.stat().st_size for p in page_files) if page_files else 0,
        total_pages=len(page_files),
        processed_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Return an empty chemical data placeholder for now
    result = ExtractionResult(
        document_id=request.document_id,
        status="completed",
        metadata=metadata,
        chemical_data=ChemicalData(compounds=[], structures=[]),
    )

    logger.info(f"Stubbed extraction completed for '{request.document_id}'.")
    return result
