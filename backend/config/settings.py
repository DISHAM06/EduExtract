import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduExtract"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    
    # Storage settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "temp_data" / "uploads"
    EXPORT_DIR: Path = BASE_DIR / "temp_data" / "exports"
    
    # OCR settings
    OCR_LANGUAGES: list[str] = ["en"]
    OCR_CONFIDENCE_THRESHOLD: float = 0.3
    
    # Max file size (50MB)
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
