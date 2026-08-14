from chemistry.image_to_smiles import image_to_smiles
from chemistry.smiles_to_name import smiles_to_compound_name


if __name__ == "__main__":

    print("\n========== CHEMICAL IMAGE PIPELINE ==========\n")

    image_path = "input/images/benzene.jpg"

    print("[INFO] Extracting SMILES...")
    smiles = image_to_smiles(image_path)
    print("SMILES:", smiles)

    print("[INFO] Converting SMILES to name...")
    name = smiles_to_compound_name(smiles)

    if name:
        print("Compound Name:", name)
    else:
        print("Compound Name: Not found")

    print("\n===========================================\n")
