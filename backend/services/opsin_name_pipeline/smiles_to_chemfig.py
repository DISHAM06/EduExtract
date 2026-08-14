def smiles_to_chemfig(smiles: str) -> str:
    """
    Convert SMILES to chemfig LaTeX (basic rules)
    """

    normalized = smiles.replace(" ", "").lower()

    # Benzene (aromatic OR kekule)
    if normalized in ["c1ccccc1", "c1=cc=cc=c1"]:
        return r"\chemfig{*6(-=-=-=)}"

    # Fallback (still safe LaTeX)
    return r"\text{" + smiles + "}"
