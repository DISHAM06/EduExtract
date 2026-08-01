from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "EduExtract"
    assert data["ocr_engine"] == "EasyOCR"
    assert data["opencv_available"] is True
