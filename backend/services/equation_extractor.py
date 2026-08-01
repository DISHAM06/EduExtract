import re
import uuid
from typing import List
from backend.models.schemas import EquationData, OCRItem

class EquationExtractor:
    """
    Extracts mathematical expressions and equations based on math symbol density,
    LaTeX notation patterns, and layout heuristics.
    """

    MATH_PATTERNS = [
        re.compile(r".*[=+\-*/^\\=].*"),
        re.compile(r"\\(?:frac|sum|int|sqrt|lim|matrix|vec|alpha|beta|gamma|theta|lambda|pi|sigma)\b"),
        re.compile(r"^[A-Za-z]\s*[=+-]\s*.*"),  # e.g., "E = mc^2", "f(x) = x^2 + 2x"
        re.compile(r"\b\d+x\s*[+-]\s*\d+y\b")  # Algebraic forms
    ]

    def extract_equations(self, ocr_items: List[OCRItem], page_num: int = 1) -> List[EquationData]:
        equations: List[EquationData] = []
        
        for item in ocr_items:
            if item.page != page_num:
                continue

            text = item.text.strip()

            # Skip short plain words
            if len(text) < 2 or text.isalpha():
                continue

            is_math = False
            for pattern in self.MATH_PATTERNS:
                if pattern.search(text):
                    is_math = True
                    break

            if is_math:
                # Format to LaTeX string if applicable
                latex_text = self._convert_to_latex(text)
                is_display = len(text) > 15 or "=" in text

                equations.append(
                    EquationData(
                        equation_id=f"eq_{page_num}_{uuid.uuid4().hex[:6]}",
                        equation_text=latex_text,
                        is_display_math=is_display,
                        page=page_num,
                        bbox=item.bbox
                    )
                )

        return equations

    def _convert_to_latex(self, raw_text: str) -> str:
        """Helper to enhance raw math text into clean LaTeX syntax."""
        text = raw_text
        text = re.sub(r"(\w+)\^(\d+)", r"\1^{\2}", text)
        text = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", text)
        text = text.replace(" +/- ", " \\pm ")
        text = text.replace(" <= ", " \\le ")
        text = text.replace(" >= ", " \\ge ")
        return text