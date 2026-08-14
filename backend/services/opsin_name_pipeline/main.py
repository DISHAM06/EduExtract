from opsin_name_pipeline.opsin_client import name_to_smiles
from opsin_name_pipeline.smiles_to_chemfig import smiles_to_chemfig
from shared.latex_renderer import render_chemfig

from shared.pdf_to_image import pdf_to_png
import os

def run_pipeline(chemical_name: str):
    print("[INFO] Input chemical name:", chemical_name)

    smiles = name_to_smiles(chemical_name)
    if not smiles:
        print("[ERROR] OPSIN failed")
        return
    

    print("[INFO] SMILES:", smiles)

    chemfig = smiles_to_chemfig(smiles)
    print("[INFO] Rendering diagram...")

    pdf = render_chemfig(chemfig, output_name=chemical_name)
    png = pdf_to_png(pdf)

    print("\n✅ IMAGE GENERATED:")
    print(png)
    print("\n👉 Open this image in VS Code to preview.")

if __name__ == "__main__":
    run_pipeline("benzene")
