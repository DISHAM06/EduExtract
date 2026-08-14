import cv2
import torch
from molscribe import MolScribe

# ---------- CONFIG ----------
MODEL_PATH = "models/molscribe/swin_base_char_aux_1m.pth"

# ---------- GLOBAL MODEL CACHE ----------
_model = None


def load_molscribe():
    """
    Load MolScribe model ONLY ONCE (cached).
    """
    global _model

    if _model is None:
        print("[INFO] Loading MolScribe model (one-time)...")
        torch.set_num_threads(1)  # CPU safety

        _model = MolScribe(
            model_path=MODEL_PATH,
            device="cpu"
        )

    return _model


def image_to_smiles(image_path: str) -> str | None:
    """
    Convert chemical structure image → SMILES
    """
    model = load_molscribe()

    img = cv2.imread(image_path)
    if img is None:
        print("[ERROR] Image not found:", image_path)
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # ---- Resize for CPU safety ----
    h, w, _ = img.shape
    if max(h, w) > 1024:
        scale = 1024 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    print("[INFO] Predicting SMILES (CPU, may take ~1–2 min)...")

    try:
        smiles = model.predict_images([img])[0]
        return smiles
    except Exception as e:
        print("[ERROR] MolScribe failed:", e)
        return None
