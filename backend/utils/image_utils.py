import cv2
import numpy as np
from PIL import Image
import io

def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to an OpenCV BGR numpy array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes into valid OpenCV array")
    return img

def cv2_to_bytes(img: np.ndarray, ext: str = ".png") -> bytes:
    """Convert OpenCV BGR image array to image bytes."""
    success, encoded_img = cv2.imencode(ext, img)
    if not success:
        raise ValueError("Could not encode OpenCV image to bytes")
    return encoded_img.tobytes()

def crop_bounding_box(img: np.ndarray, bbox: list[int]) -> np.ndarray:
    """
    Crop bounding box [ymin, xmin, ymax, xmax] from OpenCV image array.
    """
    h, w = img.shape[:2]
    ymin, xmin, ymax, xmax = bbox
    ymin = max(0, min(int(ymin), h - 1))
    ymax = max(ymin + 1, min(int(ymax), h))
    xmin = max(0, min(int(xmin), w - 1))
    xmax = max(xmin + 1, min(int(xmax), w))
    return img[ymin:ymax, xmin:xmax]

def convert_to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convert image to single channel grayscale if it is BGR/RGB."""
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img
