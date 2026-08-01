from fastapi import APIRouter
import cv2
from backend.models.schemas import HealthStatus
from backend.config.settings import settings

router = APIRouter(tags=["Health"])

@router.get("/status", response_model=HealthStatus, summary="System Health Check")
async def health_check():
    """
    Returns system health status, active settings, and dependencies check.
    """
    return HealthStatus(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        ocr_engine="EasyOCR",
        opencv_available=cv2.__version__ is not None
    )
