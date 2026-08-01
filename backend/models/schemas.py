from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BoundingBox(BaseModel):
    ymin: int
    xmin: int
    ymax: int
    xmax: int

class OCRItem(BaseModel):
    text: str
    confidence: float
    bbox: BoundingBox
    page: int = 1

class DocumentMetadata(BaseModel):
    document_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    total_pages: int
    processed_at: str

class HeadingItem(BaseModel):
    text: str
    level: int
    page: int
    bbox: Optional[BoundingBox] = None

class ReferenceItem(BaseModel):
    text: str
    page: int

class TableData(BaseModel):
    table_id: str
    page: int
    rows: int
    cols: int
    matrix: List[List[str]]
    bbox: Optional[BoundingBox] = None

class EquationData(BaseModel):
    equation_id: str
    equation_text: str
    is_display_math: bool
    page: int
    bbox: Optional[BoundingBox] = None

class CompoundEntity(BaseModel):
    name: str
    formula: Optional[str] = None
    type: str  # e.g., "IUPAC", "Common Formula", "SMILES"
    confidence: float = 1.0

class StructureDiagram(BaseModel):
    diagram_id: str
    page: int
    bbox: BoundingBox
    estimated_bonds: int

class ChemicalData(BaseModel):
    compounds: List[CompoundEntity] = []
    structures: List[StructureDiagram] = []

class FigureData(BaseModel):
    figure_id: str
    page: int
    caption: Optional[str] = None
    figure_type: str  # e.g., "chart/graph", "scientific illustration", "diagram"
    bbox: BoundingBox

class ExtractionRequest(BaseModel):
    document_id: str
    enable_preprocessing: bool = True
    extract_text: bool = True
    extract_tables: bool = True
    extract_equations: bool = True
    extract_chemical: bool = True
    extract_graphs: bool = True

class ExtractionResult(BaseModel):
    document_id: str
    status: str = "completed"
    metadata: DocumentMetadata
    plain_text: List[OCRItem] = []
    headings: List[HeadingItem] = []
    references: List[ReferenceItem] = []
    tables: List[TableData] = []
    equations: List[EquationData] = []
    chemical_data: ChemicalData = Field(default_factory=ChemicalData)
    figures: List[FigureData] = []

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_pages: int
    message: str

class HealthStatus(BaseModel):
    status: str
    app_name: str
    version: str
    ocr_engine: str
    opencv_available: bool
