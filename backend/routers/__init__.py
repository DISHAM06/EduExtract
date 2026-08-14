from .health import router as health_router
from .upload import router as upload_router
from .extract import router as extract_router
from .download import router as download_router
from .chemistry import router as chemistry_router

__all__ = [
    "health_router",
    "upload_router",
    "extract_router",
    "download_router",
    "chemistry_router"
]
