"""Image utility helpers with lazy optional dependencies (OpenCV / NumPy).

These helpers deliberately avoid importing heavy native libraries at module
import time so the application can be imported in environments where OpenCV
is not installed (useful for CI and lightweight inspections). If a function
is called and the underlying dependency is missing, a clear RuntimeError is
raised explaining the missing requirement.
"""

try:
    import cv2 as _cv2
except Exception:
    _cv2 = None

try:
    import numpy as _np
except Exception:
    _np = None


def _ensure_cv2():
    if _cv2 is None or _np is None:
        raise RuntimeError("OpenCV and NumPy are required for image utilities but are not installed.")


def bytes_to_cv2(image_bytes: bytes):
    _ensure_cv2()
    nparr = _np.frombuffer(image_bytes, _np.uint8)
    img = _cv2.imdecode(nparr, _cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes into valid OpenCV array")
    return img


def cv2_to_bytes(img, ext: str = ".png") -> bytes:
    _ensure_cv2()
    success, encoded_img = _cv2.imencode(ext, img)
    if not success:
        raise ValueError("Could not encode OpenCV image to bytes")
    return encoded_img.tobytes()


def crop_bounding_box(img, bbox: list[int]):
    _ensure_cv2()
    h, w = img.shape[:2]
    ymin, xmin, ymax, xmax = bbox
    ymin = max(0, min(int(ymin), h - 1))
    ymax = max(ymin + 1, min(int(ymax), h))
    xmin = max(0, min(int(xmin), w - 1))
    xmax = max(xmin + 1, min(int(xmax), w))
    return img[ymin:ymax, xmin:xmax]


def convert_to_grayscale(img):
    _ensure_cv2()
    if len(img.shape) == 3:
        return _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)
    return img
