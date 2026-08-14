from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.models.schemas import (
    ChemistryExtractRequest,
    ChemistryExtractResponse,
    ChemistryRenderRequest,
    ChemistryRenderResponse,
    ChemistryResolveNameRequest,
    ChemistryResolveNameResponse,
)

router = APIRouter(prefix="/api/v1/chemistry", tags=["Chemistry"])


class _StubChemistryService:
    """Lightweight stub service to keep the chemistry router importable until pipelines are integrated."""

    def extract_from_image(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Chemistry extraction not integrated yet")

    def resolve_name(self, name: str) -> Dict[str, Any]:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Name resolution not integrated yet")

    def render_smiles(self, smiles: str) -> Dict[str, Any]:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Rendering not integrated yet")


service = _StubChemistryService()


@router.post("/extract", response_model=ChemistryExtractResponse, summary="Extract chemistry from an image")
async def extract_from_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    image_bytes = await file.read()
    return service.extract_from_image(image_bytes, file.filename or "upload")


@router.post("/resolve-name", response_model=ChemistryResolveNameResponse, summary="Resolve a chemical name to SMILES")
async def resolve_name(payload: ChemistryResolveNameRequest) -> Dict[str, Any]:
    return service.resolve_name(payload.name)


@router.post("/render", response_model=ChemistryRenderResponse, summary="Render a SMILES string")
async def render_smiles(payload: ChemistryRenderRequest) -> Dict[str, Any]:
    return service.render_smiles(payload.smiles)
