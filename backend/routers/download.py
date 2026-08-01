import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse, Response

from backend.config.settings import settings
from backend.utils.file_utils import export_to_markdown, export_to_csv_zip
from backend.utils.logger import logger

router = APIRouter(tags=["Download"])

@router.get("/download/{document_id}", summary="Download Extracted Document Results")
async def download_results(
    document_id: str,
    format: str = Query("json", description="Format to download: 'json', 'markdown', or 'csv'")
):
    """
    Downloads extracted structured document data in JSON, Markdown (.md), or CSV (.zip) format.
    """
    export_json_path = settings.EXPORT_DIR / f"{document_id}.json"
    if not export_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extraction results found for document_id '{document_id}'. Run POST /extract first."
        )

    with open(export_json_path, "r", encoding="utf-8") as f:
        extraction_data = json.load(f)

    fmt = format.lower()

    if fmt == "json":
        return FileResponse(
            path=export_json_path,
            filename=f"eduextract_{document_id}.json",
            media_type="application/json"
        )
    elif fmt == "markdown":
        md_content = export_to_markdown(extraction_data)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="eduextract_{document_id}.md"'}
        )
    elif fmt == "csv":
        zip_bytes = export_to_csv_zip(extraction_data)
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="eduextract_{document_id}_tables.zip"'}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Supported formats: 'json', 'markdown', 'csv'"
        )
