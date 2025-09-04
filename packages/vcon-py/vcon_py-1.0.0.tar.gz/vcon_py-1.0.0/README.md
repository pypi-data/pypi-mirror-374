# vcontacts-wrapper (vconpy)

A lightweight Python package to prepare arguments and run **Vcontacts**,  
a tool to compute surface areas in contact using the constrained Voronoi procedure from the paper:  

> **Quantification of protein surfaces, volumes and atom-atom contacts using a constrained Voronoi procedure**  
> (doi: [10.1093/bioinformatics/18.10.1365](https://doi.org/10.1093/bioinformatics/18.10.1365))

This wrapper makes it easy to call the `Vcontacts` executables (`vcon_surfaces` or `vcon_nrgten`) directly from Python, capture their output, and optionally parse `.vcon` files into Python dictionaries.

---

## Installation

```bash
pip install vcon-py
```

---

## Example Usage

```python
from vconpy import run_vcon

# Run Vcontacts
result_surfaces = run_vcon(
    "/path/to/receptor.pdb",
    vcon_type="surfaces"
)

# Run Vcontacts and return a dictionary instead of outputting a file
result_nrgten = run_vcon(
    "/path/to/receptor.pdb",
    as_dictionary=True
)

# NRGTEN requires setting showbonded as True
result_nrgten = run_vcon(
    "/path/to/receptor.pdb",
    as_dictionary=True,
    showbonded=True
)

print(result_nrgten.surface_dictionary)  # dict of atom-atom contact areas
```

---

## Arguments

| Argument         | Type   | Description                                                                                                                      | Default      |
|------------------|--------|----------------------------------------------------------------------------------------------------------------------------------|--------------|
| `pdb_filename`   | `str`  | Path to the input PDB file.                                                                                                      | **Required** |
| `showbonded`     | `bool` | If `True`, include covalently bonded atoms in the contacts (`-all` flag).                                                        | `False`      |
| `normalize`      | `bool` | If `True`, normalize contacts to percent of total contact area. Otherwise, contacts are given in SAS units (Å²). (`-norm` flag). | `False`      |
| `planedef`       | `str`  | Plane definition for analysis. Options: `X` (extended radical plane), `R` (radical plane), `B` (bisecting plane).                | `None`       |
| `as_dictionary`  | `bool` | If `True`, returns a Python dictionary. The `.vcon` file is deleted after parsing.                                               | `False`      |

---

## Returns

The function returns a `VconResult` namedtuple with the following fields:

| Field                | Type   | Description                                                            |
|----------------------|--------|------------------------------------------------------------------------|
| `vcon_filename`      | `str`  | Path to the generated `.vcon` file.                                    |
| `surface_dictionary` | `dict` | Dictionary of atom-atom contact areas (only if `as_dictionary=True`).  |
| `stdout`             | `str`  | Standard output from the Vcontacts process.                            |
| `stderr`             | `str`  | Standard error from the Vcontacts process.                             |
| `returncode`         | `int`  | Exit code from the Vcontacts process.                                  |

---

## Raises

| Error       | Condition                                                                 |
|-------------|---------------------------------------------------------------------------|
| `ValueError` | Raised if the input file does not exist, or if `vcon_type` is invalid.   |
| `VconError`  | Raised if the Vcontacts executable is missing, not executable, or fails. |

---
