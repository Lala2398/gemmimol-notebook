# gemmimol-notebook

> An interactive macromolecular structure and electron-density viewer for
> Jupyter and Google Colab — powered by [GemmiMol](https://gemmimol.github.io/).

Open any PDB, COD, or CCD entry — or a local file — in a 3D viewer that shows the
model together with its electron density map, directly inside a notebook cell.
No downloads, no Coot, no setup beyond a single import.

---

## Table of contents

- [Why use it?](#why-use-it)
- [Repository layout](#repository-layout)
- [Installation](#installation)
- [Quick start](#quick-start)
- [`show_gemmimol` — the main viewer](#show_gemmimol--the-main-viewer)
  - [Supported sources](#supported-sources)
  - [Electron density maps](#electron-density-maps)
  - [All parameters](#all-parameters)
- [`find_pdb_by_ligand` — the companion search tool](#find_pdb_by_ligand--the-companion-search-tool)
- [How it works](#how-it-works)
- [Robustness features](#robustness-features)
- [Known limitations](#known-limitations)
- [License](#license)
- [Credits and references](#credits-and-references)

---

## Why use it?

Normally, inspecting a structure means downloading files, launching a program like
Coot, and preparing the data. This project is built for a *quick look*: you type a
code and a 3D model with its electron density map opens instantly in the notebook.
It looks like Coot and the mouse controls feel like Coot — but it is a viewer only.

Typical use cases:

- Quickly screening Dimple results at a synchrotron
- Interactive demonstrations of structures for teaching and presentations
- Showing small molecules from COD (e.g. caffeine) together with their density
- A fast preview of local refinement results

---

## Repository layout

```
gemmimol-notebook/
├── LICENSE                   # MIT license for this wrapper
├── README.md                 # this file
├── show_gemmimol.py          # main viewer  → from show_gemmimol import show_gemmimol
├── find_pdb_by_ligand.py     # companion search tool (optional)
└── [GemmiMolViewer.ipynb](https://github.com/Lala2398/gemmimol-notebook/blob/main/GemmiMolViewer.ipynb)       # demo / tutorial notebook
```

Two independent modules:

| File | Purpose | Import |
|---|---|---|
| `show_gemmimol.py` | The viewer itself | `from show_gemmimol import show_gemmimol` |
| `find_pdb_by_ligand.py` | Find PDB entries containing a ligand (optional helper) | `from find_pdb_by_ligand import find_pdb_by_ligand` |

The two files do not depend on each other. `find_pdb_by_ligand.py` is a convenience
tool for *discovering* which structures contain a ligand; you then open one of them
with `show_gemmimol`.

---

## Installation

The only dependency is the `gemmi` library (used for CIF normalization and density
calculation), plus `requests` for downloads. On Google Colab these are usually
already available; if not:

```bash
!pip install gemmi requests
```

### Option A — in Google Colab

Download the modules into your Colab session, then import:

```python
!pip install gemmi requests -q
!wget -q https://raw.githubusercontent.com/<Lala2398>/gemmimol-notebook/main/show_gemmimol.py
!wget -q https://raw.githubusercontent.com/<Lala2398>/gemmimol-notebook/main/find_pdb_by_ligand.py

from show_gemmimol import show_gemmimol, clear_cache
from find_pdb_by_ligand import find_pdb_by_ligand
```

### Option B — in local Jupyter

Place `show_gemmimol.py` (and optionally `find_pdb_by_ligand.py`) in the same
folder as your notebook, then:

```python
from show_gemmimol import show_gemmimol
```

---

## Quick start

```python
# A PDB structure — the density map loads automatically
show_gemmimol(pdb_id="4UN4")

# Automatic code detection
show_gemmimol(code="4UN4")        # 4 characters   → PDB
show_gemmimol(code="ATP")         # 1–3 characters → CCD ligand
show_gemmimol(code="1542540")     # numeric        → COD small molecule

# A local file
with open("/content/6H0F.cif") as f:
    show_gemmimol(model_text=f.read())
```

---

## `show_gemmimol` — the main viewer

### Supported sources

| Parameter | Description | Example |
|---|---|---|
| `pdb_id` | RCSB / PDBe structure | `pdb_id="4UN4"` |
| `cod_id` | Crystallography Open Database small molecule | `cod_id="1542540"` |
| `ccd_id` | CCD / Ligand Expo monomer code | `ccd_id="ATP"` |
| `code` | Auto-detected code (PDB / CCD / COD) | `code="HEM"` |
| `model_url` | URL of any CIF / PDB file | `model_url="https://..."` |
| `model_text` | File contents read in Python | `model_text=open(...).read()` |

The `code` parameter also accepts an explicit prefix: `"PDB:4UN4"`,
`"COD:1542540"`, `"CCD:ATP"`.

### Electron density maps

The viewer chooses a density strategy automatically based on the source:

| Source | Density strategy |
|---|---|
| PDB macromolecule | PDBe MTZ → PDB-REDO MTZ as fallback |
| COD / CCD small molecule | 2Fo-Fc map computed from the model (`gemmi.DensityCalculatorX`) |
| Local PDB file | PDB ID detected from `_entry.id` → PDBe MTZ |

For macromolecules the map is shown as a **blue** mesh (2Fo-Fc) and a
**green/red** mesh (Fo-Fc difference).

```python
# Disable density entirely
show_gemmimol(pdb_id="4UN4", auto_density=False)

# Disable automatic computation for small molecules
show_gemmimol(code="1542540", auto_compute_for_small=False)

# Finer mesh (higher resolution)
show_gemmimol(code="1542540", d_min=1.0)

# If no MTZ is found for a macromolecule, compute from the model (slow)
show_gemmimol(pdb_id="9R1V", fallback_compute=True)

# Explicit MTZ source
show_gemmimol(
    pdb_id="3KW8",
    mtz_url="https://www.ebi.ac.uk/pdbe/coordinates/files/3kw8_map.mtz",
    mtz_columns=["FWT", "PHWT", "DELFWT", "PHDELWT"],
)
```

### All parameters

```python
show_gemmimol(
    # Model source (provide exactly one)
    model_url=None,
    model_text=None,
    pdb_id=None,
    cod_id=None,
    ccd_id=None,
    code=None,

    # Density map
    mtz_url=None,                  # direct MTZ URL
    mtz_columns=None,              # ["FWT","PHWT"] or a 4-element list
    map_url=None,                  # direct CCP4 map URL (2Fo-Fc)
    diff_map_url=None,             # direct CCP4 difference map URL (Fo-Fc)
    map_bytes=None,                # local CCP4 map (bytes)
    auto_density=True,             # auto PDBe/PDB-REDO MTZ for PDB entries
    fallback_compute=False,        # last-resort computation for macromolecules
    auto_compute_for_small=True,   # auto-computed map for COD/CCD
    d_min=2.0,                     # resolution (Å)

    # Appearance
    width="100%",
    height="720px",
    background="#000000",
    ligand_style="ball&stick",
    ball_size=0.24,
    hydrogens=False,
    verbose=True,                  # print diagnostic logs
)
```

`clear_cache()` clears the in-memory download cache:

```python
from show_gemmimol import clear_cache
clear_cache()
```

---

## `find_pdb_by_ligand` — the companion search tool

Given a CCD ligand code, this returns every PDB entry that contains that ligand.
Use it to discover structures, then open one in the viewer.

```python
from find_pdb_by_ligand import find_pdb_by_ligand

ids = find_pdb_by_ligand("ATP")
print(f"{len(ids)} structures found")
print(ids[:10])

# Open the first hit in the viewer
show_gemmimol(pdb_id=ids[0])
```

The `input()`-based interactive prompt only runs when the file is executed
**directly** (`python find_pdb_by_ligand.py`). Importing the function never
triggers a prompt, so it is safe to use in scripts and notebooks.

---

## How it works

The viewer follows the flow of the official GemmiMol `view.html` demo:

1. **Fetch the model** — for PDB entries, the PDBe `_updated.cif` file is preferred
   (a Gemmi-friendly format), with RCSB as a fallback.
2. **Normalize only when necessary.** PDB files are kept in their original form (to
   preserve spatial alignment with the density map). COD and CCD files are converted
   to mmCIF that Gemmi WASM can read.
3. **Resolve density** — according to the strategy table above.
4. **Build the HTML** — GemmiMol is loaded from CDN, the model is passed to the
   viewer as a Blob URL, and the density map is loaded via `GM.load_maps_from_mtz`.

### Design decisions

- **No manual camera recentering.** GemmiMol finds the model's center on its own and
  positions the camera at an optimal distance — this produces the close, readable
  view seen on the website.
- **PDB files are passed through untouched.** A round-trip normalization can alter
  cell parameters and cause a mismatch between the density and the model.
- **Cache + retry.** The same file is not downloaded twice; network errors are
  retried up to 3 times (the COD server can be unreliable).

---

## Robustness features

- **Automatic retry** — on network failure, retries with 1s/2s/4s backoff.
- **HTTPS → HTTP fallback** — some academic servers have TLS issues.
- **In-memory cache** — cleared with `clear_cache()`.

---

## Known limitations

- The **COD server** (`crystallography.net`) is occasionally unreliable. If errors
  persist, download the file in a browser and load it with `model_text=`.
- **PDB-REDO** does not cover every entry (very new depositions and NMR structures
  may be missing).
- **CCD monomer** files have no experimental density — only a computed map is shown.
- This is a **viewer**, not an editor. Use Coot for serious refinement work.

---

## License

This project — the notebook (`GemmiMolViewer.ipnyb`), `show_gemmimol.py`, and `find_pdb_by_ligand.py` - is
released under the **MIT License**. See the [LICENSE](LICENSE) file.

It depends on third-party software that is **not redistributed** in this repository
and is loaded at runtime (via CDN and pip):

| Component | License | Loaded from |
|---|---|---|
| [GemmiMol](https://github.com/gemmimol/gemmimol) | MPL-2.0 | CDN (`jsdelivr`) |
| [Gemmi](https://github.com/project-gemmi/gemmi) | MPL-2.0 (or LGPL-3.0) | `pip install gemmi` |

---

## Credits and references

- [GemmiMol](https://gemmimol.github.io/) — Marcin Wojdyr
- [GemmiMol GitHub](https://github.com/gemmimol/gemmimol)
- [UglyMol Wiki](https://github.com/uglymol/uglymol/wiki) — integration notes
- [Gemmi](https://gemmi.readthedocs.io/) — crystallography library
- [PDBe](https://www.ebi.ac.uk/pdbe/) and [PDB-REDO](https://pdb-redo.eu/) — MTZ sources
- [COD](http://www.crystallography.net/cod/) — Crystallography Open Database
- [RCSB PDB Search API](https://search.rcsb.org/) — used by `find_pdb_by_ligand`
