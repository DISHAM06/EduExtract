from molscribe import MolScribe

_model = None

def get_molscribe_model():
    global _model

    if _model is None:
        print("[INFO] Loading MolScribe model (ONE TIME ONLY)...")

        _model = MolScribe(
            model_path="models/molscribe/swin_base_char_aux_1m.pth",
            device="cpu"
        )

        print("[INFO] MolScribe loaded successfully.")

    return _model
    