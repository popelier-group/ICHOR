import re
from pathlib import Path
from typing import List

import numpy as np

from ichor.atoms import Atom, Atoms, ListOfAtoms
from ichor.common.io import mkdir
from ichor.files.file import File, FileState
from ichor.files.gjf import GJF

def spherical_to_cartesian(r, theta, phi) -> List[float]:
    """
    Spherical to cartesian transformation, where r ∈ [0, ∞), θ ∈ [0, π], φ ∈ [-π, π).
        x = rsinθcosϕ
        y = rsinθsinϕ
        z = rcosθ
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(theta)
    return [x, y, z]

def features_to_coordinates(features: np.ndarray) -> np.ndarray:
    """ Converts a given n_points x n_features matrix of features to cartesian coordinates of shape
    n_points x n_atoms x 3

    :param features: a numpy array of shape n_points x n_features
    """

    if features.ndim == 1:
        features = np.expand_dims(features, axis=0)

    all_points = []  # 3d array
    one_point = []  # 2d array

    for row in features:  # iterate over rows, which are individual points

        # origin and x-axis and xy-plane atoms
        one_point.append([0, 0, 0])
        one_point.append([row[0], 0, 0])
        one_point.append(
            spherical_to_cartesian(row[1], np.pi / 2, row[2])
        )  # theta is always pi/2 because it is in the xy plane

        # all other atoms
        for i in range(3, features.shape[-1], 3):
            r = row[i]
            theta = row[i + 1]
            phi = row[i + 2]
            one_point.append(spherical_to_cartesian(r, theta, phi))

        all_points.append(one_point)
        one_point = []

    return np.array(all_points)

class Trajectory(ListOfAtoms, File):
    """Handles .xyz files that have multiple timesteps, with each timestep giving the x y z coordinates of the
    atoms. A user can also initialize an empty trajectory and append `Atoms` instances to it without reading in a .xyz file. This allows
    the user to build custom trajectories containing any sort of geometries.

    :param path: The path to a .xyz file that contains timesteps. Set to None by default as the user can initialize an empty trajectory and built it up
        themselves
    """

    def __init__(self, path: Path = None):
        # if we are making a trajectory from a coordinate file (such as .xyz or dlpoly history) directly
        if path is not None:
            ListOfAtoms.__init__(self)
            File.__init__(self, path)
        # if we are building a trajectory another way without reading a file containing xyz coordinates
        else:
            self.state = FileState.Read  # set the state to read as we don't need to read any file
            ListOfAtoms.__init__(self)

    def _read_file(self, n: int = -1):
        with open(self.path, "r") as f:
            atoms = Atoms()
            for line in f:
                if not line.strip():
                    continue
                elif re.match(r"^\s*\d+$", line):
                    natoms = int(line)
                    while len(atoms) < natoms:
                        line = next(f)
                        if re.match(
                            r"\s*\w+(\s+[+-]?\d+.\d+([Ee]?[+-]?\d+)?){3}", line
                        ):
                            atom_type, x, y, z = line.split()
                            atoms.add(
                                Atom(atom_type, float(x), float(y), float(z))
                            )
                    self.add(atoms)
                    if n > 0 and len(self) >= n:
                        break
                    atoms = Atoms()

    @property
    def filetype(self) -> str:
        return ".xyz"

    def add(self, atoms):
        """Add a list of Atoms (corresponding to one timestep) to the end of the trajectory list"""
        if isinstance(atoms, Atoms):
            self.append(atoms)
        else:
            self.append(Atoms(atoms))

    def rmsd(self, ref=None):
        if ref is None:
            ref = self[0]
        elif isinstance(ref, int):
            ref = self[ref]

        return [ref.rmsd(point) for point in self]

    def to_set(self, root: Path, indices: List[int]):
        """Converts the geometries in the timesteps to gjf files which then can be passed into Gaussian
        to calculate .wfn files."""
        from ichor.globals import GLOBALS

        mkdir(root, empty=True)
        root = Path(root)
        indices.sort(reverse=True)
        for n, i in enumerate(indices):
            path = Path(
                str(GLOBALS.SYSTEM_NAME) + str(n + 1).zfill(4) + ".gjf"
            )
            gjf = GJF(root / path)
            gjf.atoms = self[i]
            gjf.write()
            del self[i]

    def to_dir(self, root: Path, every: int = 1):
        from ichor.globals import GLOBALS

        mkdir(root, empty=True)
        for i, geometry in enumerate(self):
            if i % every == 0:
                path = Path(
                    str(GLOBALS.SYSTEM_NAME) + str(i + 1).zfill(4) + ".gjf"
                )
                gjf = GJF(root / path)
                gjf.atoms = geometry  # matt_todo: GJFs write out a gjf file even if there are no atoms present. This should not be possible
                gjf.write()

    @classmethod
    def features_csv_to_trajectory(
    csv_file: "Path",
    n_features: int,
    atom_types: List[str],
    header=None,
    index_col=None,
    ) -> "Trajectory":

        """ Takes in a csv file containing features and convert it to a `Trajectory` object.
        It assumes that the features start from the first column (column after the index column, if one exists). Feature csv files that 
        are written out by ichor are in Bohr instead of Angstroms for now. After converting to cartesian coordinates, we have to convert
        Bohr to Angstroms because .xyz files are written out in Angstroms (and programs like Avogadro, VMD, etc. expect distances in angstroms).
        Failing to do that will result in xyz files that are in Bohr, so if features are calculated from them again, the features will be wrong.

        :param csv_file: Path to the csv file
        :param n_features: Integer corresponding to the number of features (3N-6)
        :param atom_types: A list of strings corresponding to the atom elements (C, O, H, etc.). This has to be ordered the same way
            as atoms corresponding to the features.
        :param header: Whether the first line of the csv file contains the names of the columns. Default is None. Set to 0 to use the 0th row.
        :param index_col: Whether a column should be used as the index column. Default is None, so no column used. Set to 0 to use 0th column.
        """

        import pandas as pd
        from ichor.constants import bohr2ang

        features_array = pd.read_csv(csv_file, header=header, index_col=index_col).values
        features_array = features_array[:, :n_features]

        # xyz coordinates are currently in bohr, so convert them to angstroms
        xyz_array = features_to_coordinates(features_array)
        xyz_array = bohr2ang * xyz_array

        trajectory = Trajectory()

        for geometry in xyz_array:

            atoms = Atoms()

            for ty, atom_coord in zip(atom_types, geometry):

                atoms.add(Atom(ty, atom_coord[0], atom_coord[1], atom_coord[2]))

            trajectory.add(atoms)

        return trajectory

    def __getitem__(self, item):
        """Used to index a Trajectory instance by a str (eg. trajectory['C1']) or by integer (eg. trajectory[2]),
        remember that indeces in Python start at 0, so trajectory[2] is the 3rd timestep.
        You can use something like (np.array([traj[i].features for i in range(2)]).shape) to features of a slice of
        a trajectory as slice is not implemented in __getitem__"""
        if self.state is not FileState.Read:
            self.read()
        return super().__getitem__(item)

    def __iter__(self):
        """Used to iterate over timesteps (Atoms instances) in places such as for loops"""
        if self.state is not FileState.Read:
            self.read()
        return super().__iter__()

    def __len__(self):
        """Returns the number of timesteps in the Trajectory instance"""
        if self.state is not FileState.Read:
            self.read()
        return super().__len__()
