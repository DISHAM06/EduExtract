import os
import uuid
import cv2
import numpy as np
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from backend.models.schemas import UploadResponse
from backend.config.settings import settings
from backend.utils.file_utils import save_uploaded_file, convert_pdf_to_images
from backend.utils.logger import logger

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=UploadResponse, summary="Upload PDF or Image Document(s)")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    Accepts one PDF or multiple academic document images (.png, .jpg, .jpeg, .pdf).
    Saves document files and prepares page frames for processing.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    doc_dir = settings.UPLOAD_DIR / doc_id
    os.makedirs(doc_dir, exist_ok=True)

    first_file = files[0]
    ext = Path(first_file.filename).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {settings.ALLOWED_EXTENSIONS}"
        )

    total_pages = 0

    if ext == ".pdf":
        # Handle PDF Upload
        pdf_bytes = await first_file.read()
        if len(pdf_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum allowed size.")

        pdf_path = save_uploaded_file(pdf_bytes, f"input{ext}", doc_dir)
        try:
            images = convert_pdf_to_images(pdf_path)
            total_pages = len(images)
            for page_num, img_np in images:
                page_path = doc_dir / f"page_{page_num}.png"
                cv2.imwrite(str(page_path), img_np)
        except Exception as e:
            logger.error(f"Failed to process uploaded PDF: {e}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"PDF parsing error: {str(e)}")

        filename = first_file.filename
        file_type = "PDF"

    else:
        # Handle Multiple Image Uploads
        for idx, file in enumerate(files, 1):
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS or file_ext == ".pdf":
                continue
            
            img_bytes = await file.read()
            if len(img_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
                continue

            nparr = np.frombuffer(img_bytes, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_np is not None:
                total_pages += 1
                page_path = doc_dir / f"page_{total_pages}.png"
                cv2.imwrite(str(page_path), img_np)

        if total_pages == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid images were processed.")

        filename = f"{total_pages}_images_batch"
        file_type = "IMAGE_BATCH"

    logger.info(f"Successfully processed upload for document_id '{doc_id}' with {total_pages} pages.")

    return UploadResponse(
        document_id=doc_id,
        filename=filename,
        file_type=file_type,
        total_pages=total_pages,
        message="Upload processed successfully. Ready for extraction."
    )
