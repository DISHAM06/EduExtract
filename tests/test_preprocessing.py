import numpy as np
from backend.services.preprocessing import ImagePreprocessor

def test_image_preprocessing():
    preprocessor = ImagePreprocessor()
    dummy_img = np.ones((500, 500, 3), dtype=np.uint8) * 200

    processed = preprocessor.process(dummy_img)
    assert processed is not None
    assert isinstance(processed, np.ndarray)
    assert processed.shape[0] <= 2000
    assert processed.shape[1] <= 2000
