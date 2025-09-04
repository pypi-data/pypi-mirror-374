# Vcontacts in a Python Package

A lightweight Python package to simplify running **Vcontacts**,  
a tool to compute surface areas in contact using the constrained Voronoi procedure from the paper:  

> **Quantification of protein surfaces, volumes and atom-atom contacts using a constrained Voronoi procedure**  
> (doi: [10.1093/bioinformatics/18.10.1365](https://doi.org/10.1093/bioinformatics/18.10.1365))

This makes it easy to run `Vcontacts` directly from Python, capture the output, and optionally return the result as a Python dictionary.

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
result = run_vcon("/path/to/protein.pdb")

# Run Vcontacts and return a dictionary instead of outputting a file
result_with_dictionary = run_vcon("/path/to/protein.pdb", as_dictionary=True)

# NRGTEN requires setting showbonded as True
result_nrgten = run_vcon("/path/to/protein.pdb", as_dictionary=True, showbonded=True)

print(result_with_dictionary.surface_dictionary)
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
