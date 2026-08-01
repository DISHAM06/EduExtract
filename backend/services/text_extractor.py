import re
from typing import List, Tuple
from backend.models.schemas import OCRItem, HeadingItem, ReferenceItem

class TextExtractor:
    """
    Parses OCR streams into structured plain text, headings hierarchy,
    and reference lists.
    """

    HEADING_PATTERNS = [
        re.compile(r"^(?:\d+\.|\d+\.\d+|\d+\.\d+\.\d+)\s+[A-Z].*"),  # e.g., "1. Introduction", "2.1 Methods"
        re.compile(r"^(?:ABSTRACT|INTRODUCTION|RELATED WORK|METHODOLOGY|EXPERIMENTAL RESULTS|DISCUSSION|CONCLUSION|REFERENCES)$", re.IGNORECASE),
        re.compile(r"^[A-Z0-9\s]{4,40}$") # All caps short headings
    ]

    REFERENCE_PATTERNS = [
        re.compile(r"^\[\d+\]\s+.*"), # IEEE style: [1] J. Smith...
        re.compile(r"^\(\w+,\s*\d{4}\)\s+.*"), # Harvard style: (Smith, 2021)...
        re.compile(r"^\d+\.\s+[A-Z]\w+.*") # 1. Smith J. et al...
    ]

    def extract(self, ocr_items: List[OCRItem]) -> Tuple[List[HeadingItem], List[ReferenceItem]]:
        headings: List[HeadingItem] = []
        references: List[ReferenceItem] = []

        is_reference_section = False

        for item in ocr_items:
            text = item.text.strip()
            page = item.page

            # Check if reference section starts
            if re.match(r"^REFERENCES?$", text, re.IGNORECASE):
                is_reference_section = True
                headings.append(HeadingItem(text=text, level=1, page=page, bbox=item.bbox))
                continue

            # Parse Headings
            heading_matched = False
            for pattern in self.HEADING_PATTERNS:
                if pattern.match(text) and len(text) < 80:
                    level = 1
                    if "." in text[:5]:
                        level = min(3, text[:5].count(".") + 1)
                    headings.append(HeadingItem(text=text, level=level, page=page, bbox=item.bbox))
                    heading_matched = True
                    break

            if heading_matched:
                continue

            # Parse References
            if is_reference_section:
                references.append(ReferenceItem(text=text, page=page))
            else:
                for r_pattern in self.REFERENCE_PATTERNS:
                    if r_pattern.match(text):
                        references.append(ReferenceItem(text=text, page=page))
                        break

        return headings, references
