from rdkit import Chem


def smiles_to_compound_name(smiles: str) -> str | None:
    """
    Convert SMILES to a common compound name (basic mapping).
    """

    if not smiles:
        return None

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    canonical = Chem.MolToSmiles(mol, canonical=True)

    COMMON_NAMES = {
        "c1ccccc1": "benzene",
        "CCO": "ethanol",
        "CO": "methanol",
        "O": "water",
        "CC": "ethane",
    }

    return COMMON_NAMES.get(canonical)
