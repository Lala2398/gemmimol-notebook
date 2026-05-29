"""
pdb_search.py — Helper tool for the GemmiMol Viewer project.

Find all PDB entries that contain a given CCD (ligand) code.
This is an optional companion to `show_gemmimol`: use it to discover
which structures contain a ligand, then open one of them in the viewer.

Usage (as a library):
    from pdb_search import find_pdb_by_ligand
    ids = find_pdb_by_ligand("ATP")
    print(ids[:10])

Usage (interactive, run directly):
    python pdb_search.py
"""

import requests


def find_pdb_by_ligand(ligand_id: str) -> list:
    """
    Finds all PDB IDs containing the given CCD (ligand) code
    (for example: 'ATP', 'HEM').

    Parameters
    ----------
    ligand_id : str
        A 1-3 character CCD ligand code (case-insensitive).

    Returns
    -------
    list[str]
        A list of PDB IDs. Empty list if none found or on error.
    """
    url = "https://search.rcsb.org/rcsbsearch/v2/query"

    query = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id",
                "operator": "exact_match",
                "value": ligand_id.upper()
            }
        },
        "return_type": "entry",
        "request_options": {
            "return_all_hits": True
        }
    }

    try:
        response = requests.post(url, json=query)
        response.raise_for_status()
        data = response.json()
        if "result_set" in data:
            return [item["identifier"] for item in data["result_set"]]
        return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with the API: {e}")
        return []


# Interactive demo — runs ONLY when the file is executed directly,
# never when imported.
if __name__ == "__main__":
    ligand_name = input(
        "Enter the Ligand code (CCD) to search for in the PDB "
        "(example: HEM): "
    ).strip() or "HEM"

    print(f"\nSearching the PDB for '{ligand_name}'...")
    results = find_pdb_by_ligand(ligand_name)

    if results:
        print(f"\nA total of {len(results)} PDB entries were found.")
        print("First 20 PDB IDs:")
        print(", ".join(results[:20]))
    else:
        print(f"\nNo PDB entries were found for '{ligand_name}'.")
