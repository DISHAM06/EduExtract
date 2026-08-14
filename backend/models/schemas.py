from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BoundingBox(BaseModel):
    ymin: int
    xmin: int
    ymax: int
    xmax: int


class DocumentMetadata(BaseModel):
    document_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    total_pages: int
    processed_at: str


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


class ExtractionRequest(BaseModel):
    document_id: str
    enable_preprocessing: bool = True
    extract_chemical: bool = True


class ExtractionResult(BaseModel):
    document_id: str
    status: str = "completed"
    metadata: DocumentMetadata
    chemical_data: ChemicalData = Field(default_factory=ChemicalData)


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


class ChemistryExtractRequest(BaseModel):
    pass


class ChemistryExtractResponse(BaseModel):
    smiles: str
    canonical_smiles: str
    metadata: Dict[str, Any]
    rendering: Dict[str, Any]


class ChemistryResolveNameRequest(BaseModel):
    name: str


class ChemistryResolveNameResponse(BaseModel):
    smiles: str
    canonical_smiles: str
    metadata: Dict[str, Any]
    rendering: Dict[str, Any]


class ChemistryRenderRequest(BaseModel):
    smiles: str


class ChemistryRenderResponse(BaseModel):
    smiles: str
    latex: str
    png_path: Optional[str] = None
    status: str
