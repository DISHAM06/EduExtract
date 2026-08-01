import os
import requests
from typing import Optional, Dict, Any, List

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

def check_backend_health() -> Optional[Dict[str, Any]]:
    try:
        res = requests.get(f"{BACKEND_URL}/status", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def upload_files_to_backend(files: List) -> Optional[Dict[str, Any]]:
    url = f"{BACKEND_URL}/upload"
    files_payload = []
    
    for f in files:
        files_payload.append(("files", (f.name, f.getvalue(), f.type)))

    try:
        res = requests.post(url, files=files_payload, timeout=60)
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": res.json().get("detail", "Upload failed.")}
    except Exception as e:
        return {"error": str(e)}

def run_extraction_pipeline(document_id: str, options: Dict[str, bool]) -> Optional[Dict[str, Any]]:
    url = f"{BACKEND_URL}/extract"
    payload = {
        "document_id": document_id,
        "enable_preprocessing": options.get("enable_preprocessing", True),
        "extract_text": options.get("extract_text", True),
        "extract_tables": options.get("extract_tables", True),
        "extract_equations": options.get("extract_equations", True),
        "extract_chemical": options.get("extract_chemical", True),
        "extract_graphs": options.get("extract_graphs", True)
    }

    try:
        res = requests.post(url, json=payload, timeout=300)
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": res.json().get("detail", "Extraction failed.")}
    except Exception as e:
        return {"error": str(e)}

def get_download_url(document_id: str, fmt: str) -> str:
    return f"{BACKEND_URL}/download/{document_id}?format={fmt}"
