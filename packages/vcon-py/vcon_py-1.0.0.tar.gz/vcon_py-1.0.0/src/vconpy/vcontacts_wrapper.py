import subprocess
import os
import platform
from collections import namedtuple
from pathlib import Path

VconResult = namedtuple('VconResult', ['vcon_filename', 'surface_dictionary', 'stdout', 'stderr', 'returncode'])


class VconError(Exception):
    """Custom exception for errors related to Vcontacts."""
    pass


def get_surface_dict(vcon_file):
    """ Returns a dict of dicts based on atom numbers (input file must have
        unique atom numbers), containing surface area in contact between
        pairs of atoms.
    """
    with open(vcon_file) as infile:
        text = infile.read()
    vcon_dictionary = dict()
    current_key = None

    for line in text.splitlines():
        # Skip empty lines
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split()

        # Main line (chunk header)
        if len(parts) >= 2 and parts[-2] == 'Sol_acc_surf':
            main_key = int(parts[0])
            vcon_dictionary[main_key] = dict()
            current_key = main_key
        else:
            sub_key = int(parts[0])
            value = float(parts[-2])
            vcon_dictionary[current_key][sub_key] = value
    return vcon_dictionary


def run_vcon(pdb_filename, showbonded=False, normalize=False, planedef=None, as_dictionary=False):
    """
    Executes the VContacts program to process a PDB file and generates a VCON file.

    :param pdb_filename: The file path of the PDB file to be processed.
    :type pdb_filename: str
    :param showbonded: Specifies whether contacts include covalently bonded atoms (default: False | optional).
    :type showbonded: bool, optional
    :param normalize: Contacts normalized to a percent of total contact area otherwise contacts are given in SAS equivalent units (square angstroms) (default: False | optional).
    :type normalize: bool, optional
    :param planedef: Optional parameter for defining specific plane-based interactions in analysis. Options are X, R or B: extended radical plane, radical plane or bisecting dividing plane (default: None).
    :type planedef: str, optional
    :param as_dictionary: If True, returns a dictionary made from the Vcontacts output file. Output file (.vcon) is deleted.
    :type as_dictionary: bool, optional
    :return: Vcontacts output filepath (vcon_filename) as well as stdout, stderr and returncode.
    :rtype: VconResult
    """
    vcon_output_path = os.path.splitext(pdb_filename)[0] + ".vcon"
    executable_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'vcon'))
    if platform.system() == 'Windows':
        executable_path += '.exe'
    if not os.path.isfile(executable_path) or not os.access(executable_path, os.X_OK):
        raise VconError(f"Error: Executable '{executable_path}' not found or not executable.")
    cmd = [executable_path]
    cmd.extend([pdb_filename])
    if showbonded:
        cmd.extend(["-all"])
    if normalize:
        cmd.extend(["-norm"])
    if planedef:
        cmd.extend(["-planedef", planedef.upper()])
    try:
        print(cmd)
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        with open(vcon_output_path, 'w') as f:
            f.write(result.stdout)
        surface_dictionary = None
        if as_dictionary:
            surface_dictionary = get_surface_dict(vcon_output_path)
            os.remove(vcon_output_path)
        return VconResult(vcon_output_path, surface_dictionary, result.stdout, result.stderr, result.returncode)

    except subprocess.CalledProcessError as e:
        error_message = (
            f"Vcontacts failed with exit code {e.returncode}.\n"
            f"Error message:\n{e.stderr.strip()}"
        )
        raise VconError(error_message) from e

