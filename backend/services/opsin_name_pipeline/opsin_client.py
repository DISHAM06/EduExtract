import requests

OPSIN_URL = "https://opsin.ch.cam.ac.uk/opsin/{}.json"

def name_to_smiles(chemical_name: str) -> str | None:
    """
    Convert chemical name to SMILES using OPSIN
    """
    url = OPSIN_URL.format(chemical_name.replace(" ", "%20"))

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    return data.get("smiles")
