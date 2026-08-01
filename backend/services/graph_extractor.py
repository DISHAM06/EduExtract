import cv2
import numpy as np
import re
import uuid
from typing import List
from backend.models.schemas import FigureData, BoundingBox, OCRItem
from backend.utils.logger import logger

class GraphExtractor:
    """
    Extracts scientific figures, charts, plots, and graphical diagrams,
    associating them with nearby figure captions.
    """

    CAPTION_PATTERNS = [
        re.compile(r"^(?:Figure|Fig\.|Chart|Plot)\s*\d+[:\.]?.*", re.IGNORECASE)
    ]

    def extract_figures(
        self, image: np.ndarray, ocr_items: List[OCRItem], page_num: int = 1
    ) -> List[FigureData]:
        figures: List[FigureData] = []
        
        # 1. Find captions
        captions_map = []
        for item in ocr_items:
            if item.page != page_num:
                continue
            text = item.text.strip()
            for pattern in self.CAPTION_PATTERNS:
                if pattern.match(text):
                    captions_map.append((item.bbox, text))
                    break

        # 2. Identify visual non-text graphical bounding regions via OpenCV edge/contour density
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
            edges = cv2.Canny(gray, 50, 200)
            
            # Dilate to merge figure components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            dilated = cv2.dilate(edges, kernel, iterations=2)

            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            min_figure_area = (image.shape[0] * image.shape[1]) * 0.03
            max_figure_area = (image.shape[0] * image.shape[1]) * 0.70

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if min_figure_area < area < max_figure_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    fig_bbox = BoundingBox(ymin=y, xmin=x, ymax=y + h, xmax=x + w)

                    # Find closest caption below or above figure bounding box
                    matched_caption = None
                    min_dist = float("inf")
                    for cap_bbox, cap_text in captions_map:
                        dist = abs(cap_bbox.ymin - fig_bbox.ymax)
                        if dist < 200 and dist < min_dist:
                            min_dist = dist
                            matched_caption = cap_text

                    # Determine figure type heuristic
                    fig_type = "Chart / Plot" if matched_caption and any(k in matched_caption.lower() for k in ["chart", "plot", "graph"]) else "Scientific Illustration"

                    figures.append(
                        FigureData(
                            figure_id=f"fig_{page_num}_{uuid.uuid4().hex[:6]}",
                            page=page_num,
                            caption=matched_caption,
                            figure_type=fig_type,
                            bbox=fig_bbox
                        )
                    )
        except Exception as e:
            logger.error(f"Error extracting figures on page {page_num}: {e}")

        return figures
