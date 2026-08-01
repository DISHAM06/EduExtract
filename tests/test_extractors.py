from backend.models.schemas import OCRItem, BoundingBox
from backend.services.text_extractor import TextExtractor
from backend.services.equation_extractor import EquationExtractor
from backend.services.chemical_extractor import ChemicalExtractor

def test_text_extractor_headings():
    extractor = TextExtractor()
    ocr_items = [
        OCRItem(text="1. Introduction", confidence=0.95, bbox=BoundingBox(ymin=10, xmin=10, ymax=30, xmax=150), page=1),
        OCRItem(text="This paper presents EduExtract.", confidence=0.99, bbox=BoundingBox(ymin=40, xmin=10, ymax=60, xmax=300), page=1),
        OCRItem(text="REFERENCES", confidence=0.98, bbox=BoundingBox(ymin=70, xmin=10, ymax=90, xmax=120), page=1),
        OCRItem(text="[1] J. Smith, Scientific Extraction 2024.", confidence=0.92, bbox=BoundingBox(ymin=100, xmin=10, ymax=120, xmax=350), page=1),
    ]

    headings, refs = extractor.extract(ocr_items)
    assert len(headings) == 2
    assert headings[0].text == "1. Introduction"
    assert headings[0].level == 1
    assert len(refs) == 1
    assert refs[0].text == "[1] J. Smith, Scientific Extraction 2024."

def test_equation_extractor():
    extractor = EquationExtractor()
    ocr_items = [
        OCRItem(text="E = mc^2", confidence=0.95, bbox=BoundingBox(ymin=10, xmin=10, ymax=30, xmax=100), page=1),
        OCRItem(text="f(x) = x^2 + 2x", confidence=0.90, bbox=BoundingBox(ymin=40, xmin=10, ymax=60, xmax=150), page=1)
    ]
    eqs = extractor.extract_equations(ocr_items, page_num=1)
    assert len(eqs) == 2
    assert "E = mc^{2}" in eqs[0].equation_text

def test_chemical_extractor_compounds():
    extractor = ChemicalExtractor()
    ocr_items = [
        OCRItem(text="Synthesis of Ethanol and Benzene", confidence=0.95, bbox=BoundingBox(ymin=10, xmin=10, ymax=30, xmax=200), page=1),
        OCRItem(text="Formula: C6H12O6", confidence=0.92, bbox=BoundingBox(ymin=40, xmin=10, ymax=60, xmax=150), page=1)
    ]

    dummy_img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    chem_data = extractor.extract_chemical_data(dummy_img, ocr_items, page_num=1)
    
    compound_names = [c.name.lower() for c in chem_data.compounds]
    assert "ethanol" in compound_names
    assert "benzene" in compound_names
    assert "c6h12o6" in [c.formula.lower() for c in chem_data.compounds if c.formula]
