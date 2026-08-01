import easyocr
import numpy as np
from typing import List
from backend.models.schemas import OCRItem, BoundingBox
from backend.config.settings import settings
from backend.utils.logger import logger

class OCRService:
    """
    Singleton service wrapper around EasyOCR Reader for bounding box detection,
    text extraction, and confidence scoring.
    """
    _instance = None
    _reader = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
        return cls._instance

    def _get_reader(self) -> easyocr.Reader:
        if self._reader is None:
            logger.info(f"Initializing EasyOCR Reader for languages: {settings.OCR_LANGUAGES}")
            # gpu=False for max portability in standard environments
            self._reader = easyocr.Reader(settings.OCR_LANGUAGES, gpu=False)
        return self._reader

    def extract_ocr_items(self, image: np.ndarray, page_num: int = 1) -> List[OCRItem]:
        """
        Run OCR on an image and return structured OCRItem list with bounding boxes.
        """
        reader = self._get_reader()
        raw_results = reader.readtext(image)
        
        ocr_items = []
        for bbox_coords, text, conf in raw_results:
            if conf < settings.OCR_CONFIDENCE_THRESHOLD or not text.strip():
                continue

            # EasyOCR returns bbox as [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            xs = [pt[0] for pt in bbox_coords]
            ys = [pt[1] for pt in bbox_coords]
            
            bbox = BoundingBox(
                ymin=int(min(ys)),
                xmin=int(min(xs)),
                ymax=int(max(ys)),
                xmax=int(max(xs))
            )

            ocr_items.append(
                OCRItem(
                    text=text.strip(),
                    confidence=round(float(conf), 4),
                    bbox=bbox,
                    page=page_num
                )
            )

        return ocr_items
