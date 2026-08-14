import cv2
from chemistry.molscribe_model import get_molscribe_model

def image_to_smiles(image_path: str):
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    model = get_molscribe_model()

    result = model.predict_images([img])[0]

    return result["smiles"]
