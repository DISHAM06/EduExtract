from fastapi import APIRouter
from backend.models.schemas import HealthStatus
from backend.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/status", response_model=HealthStatus, summary="System Health Check")
async def health_check():
    """
    Returns system health status, active settings, and dependencies check.
    Gracefully handles missing optional dependencies like OpenCV.
    """
    try:
        import cv2  # optional dependency
        opencv_available = True
    except Exception:
        opencv_available = False

    return HealthStatus(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        ocr_engine="EasyOCR",
        opencv_available=opencv_available,
    )
