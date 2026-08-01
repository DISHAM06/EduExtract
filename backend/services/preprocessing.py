import cv2
import numpy as np
from backend.utils.logger import logger

class ImagePreprocessor:
    """
    Image preprocessing pipeline including noise removal, thresholding,
    skew correction, and resizing for enhanced OCR & extraction accuracy.
    """

    @staticmethod
    def remove_noise(img: np.ndarray) -> np.ndarray:
        """Apply Gaussian & Bilateral filtering for noise reduction."""
        if len(img.shape) == 3:
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
        return denoised

    @staticmethod
    def apply_thresholding(img: np.ndarray, method: str = "otsu") -> np.ndarray:
        """
        Binarize image using Otsu's thresholding or Adaptive Gaussian Thresholding.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        if method == "otsu":
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "adaptive":
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        else:
            thresh = gray

        return thresh

    @staticmethod
    def correct_skew(img: np.ndarray) -> np.ndarray:
        """
        Detect text line orientation using minAreaRect and rotate image to correct skew.
        """
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            # Invert colors for contour analysis
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Find coordinates of all non-zero pixels
            coords = np.column_stack(np.where(thresh > 0))
            if coords.size == 0:
                return img

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Ignore tiny negligible angles
            if abs(angle) < 0.5 or abs(angle) > 45:
                return img

            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )
            logger.info(f"Corrected image skew by {angle:.2f} degrees")
            return rotated
        except Exception as e:
            logger.warning(f"Skew correction skipped: {e}")
            return img

    @staticmethod
    def resize_image(img: np.ndarray, max_dim: int = 2000) -> np.ndarray:
        """Resize image while keeping original aspect ratio intact."""
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img

    def process(self, img: np.ndarray) -> np.ndarray:
        """Execute full preprocessing sequence."""
        processed = self.resize_image(img)
        processed = self.correct_skew(processed)
        processed = self.remove_noise(processed)
        return processed
