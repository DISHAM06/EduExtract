import cv2
import numpy as np
import uuid
from typing import List
from backend.models.schemas import TableData, BoundingBox, OCRItem
from backend.utils.logger import logger

class TableExtractor:
    """
    Extracts tabular structures using OpenCV morphological operations
    to identify grid lines, cells, and associated OCR text.
    """

    def extract_tables(self, image: np.ndarray, ocr_items: List[OCRItem], page_num: int = 1) -> List[TableData]:
        tables: List[TableData] = []
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
            # Binarize
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Detect horizontal lines
            kernel_len = max(15, image.shape[1] // 30)
            horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
            horiz_lines = cv2.erode(thresh, horiz_kernel, iterations=1)
            horiz_lines = cv2.dilate(horiz_lines, horiz_kernel, iterations=1)

            # Detect vertical lines
            vert_kernel_len = max(15, image.shape[0] // 30)
            vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_kernel_len))
            vert_lines = cv2.erode(thresh, vert_kernel, iterations=1)
            vert_lines = cv2.dilate(vert_lines, vert_kernel, iterations=1)

            # Combine grid mask
            table_grid = cv2.addWeighted(horiz_lines, 0.5, vert_lines, 0.5, 0.0)
            table_grid = cv2.threshold(table_grid, 0, 255, cv2.THRESH_BINARY)[1]

            # Find table candidate contours
            contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            min_table_area = (image.shape[0] * image.shape[1]) * 0.015

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < min_table_area:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                bbox = BoundingBox(ymin=y, xmin=x, ymax=y + h, xmax=x + w)

                # Collect OCR items residing inside table bounding box
                table_ocr = [
                    item for item in ocr_items 
                    if item.page == page_num and 
                       bbox.xmin <= item.bbox.xmin and item.bbox.xmax <= bbox.xmax and
                       bbox.ymin <= item.bbox.ymin and item.bbox.ymax <= bbox.ymax
                ]

                if not table_ocr:
                    continue

                # Sort text items vertically into rows and horizontally into columns
                rows_map = {}
                for item in sorted(table_ocr, key=lambda i: i.bbox.ymin):
                    # Group items within 15px threshold as same row
                    placed = False
                    for row_y in rows_map:
                        if abs(item.bbox.ymin - row_y) < 15:
                            rows_map[row_y].append(item)
                            placed = True
                            break
                    if not placed:
                        rows_map[item.bbox.ymin] = [item]

                table_matrix = []
                for row_y in sorted(rows_map.keys()):
                    row_items = sorted(rows_map[row_y], key=lambda i: i.bbox.xmin)
                    table_matrix.append([i.text for i in row_items])

                if table_matrix:
                    max_cols = max(len(r) for r in table_matrix)
                    # Normalize row column lengths
                    normalized_matrix = [r + [""] * (max_cols - len(r)) for r in table_matrix]
                    
                    tables.append(
                        TableData(
                            table_id=f"table_{page_num}_{uuid.uuid4().hex[:6]}",
                            page=page_num,
                            rows=len(normalized_matrix),
                            cols=max_cols,
                            matrix=normalized_matrix,
                            bbox=bbox
                        )
                    )
        except Exception as e:
            logger.error(f"Error extracting tables on page {page_num}: {e}")

        return tables
