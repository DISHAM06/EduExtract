import io
import cv2
import numpy as np
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def create_dummy_image_bytes():
    # Create 100x100 white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    success, encoded = cv2.imencode(".png", img)
    return encoded.tobytes()

def test_upload_image_success():
    img_bytes = create_dummy_image_bytes()
    files = [("files", ("test_page.png", img_bytes, "image/png"))]
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["total_pages"] == 1
    assert data["file_type"] == "IMAGE_BATCH"

def test_upload_invalid_extension():
    files = [("files", ("test_file.exe", b"fake binary data", "application/octet-stream"))]
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]
