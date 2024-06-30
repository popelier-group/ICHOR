from typing import Callable, Optional

import numpy as np
from ichor.core.atoms.alf import ALF
from ichor.core.calculators.c_matrix_calculator import calculate_c_matrix
from ichor.core.common import constants
from ichor.core.common.types import Coordinates3D, VarReprMixin
from ichor.core.common.units import AtomicDistance


class Atom(VarReprMixin, Coordinates3D):
    """
    The Atom class is used for ONE atom in ONE timestep.

    e.g. If we have 1000 timesteps in the trajectory, with 6 atoms in each timestep,
    the we will have 6000 Atom instances in total.
    """

    def __init__(
        self,
        ty: str,
        x: float,
        y: float,
        z: float,
        index: Optional[int] = None,
        parent: Optional["ichor.core.atoms.Atoms"] = None,  # noqa F821
        units: AtomicDistance = AtomicDistance.Angstroms,
    ):
        # to be read in from coordinate line
        # element of atom
        self.type: str = ty.capitalize()
        # these are used for the actual names, eg. O1 H2 H3, so the atom_number starts at 1
        self._index: Optional[int] = index

        self._parent: Optional["ichor.core.atoms.Atoms"] = parent  # noqa F821
        Coordinates3D.__init__(self, x, y, z)
        self.units: AtomicDistance = units

    @classmethod
    def from_atom(cls, atom: "Atom") -> "Atom":  # noqa F821
        return Atom(
            atom.type,
            atom.x,
            atom.y,
            atom.z,
            atom._index,
            atom._parent,
            atom.units,
        )

    def to_angstroms(self) -> "Atom":  # noqa F821
        """Convert the coordiantes to Angstroms"""
        new_atom = Atom.from_atom(self)
        if new_atom.units == AtomicDistance.Bohr:
            new_atom.coordinates *= constants.bohr2ang
            new_atom.units = AtomicDistance.Angstroms
        return new_atom

    def to_bohr(self) -> "Atom":  # noqa F821
        """Convert the coordiantes to Bohr"""
        new_atom = Atom.from_atom(self)
        if new_atom.units == AtomicDistance.Angstroms:
            new_atom.coordinates *= constants.ang2bohr
            new_atom.units = AtomicDistance.Bohr
        return new_atom

    @property
    def index(self) -> int:
        """Returns the integer assigned to the atom, calculated from the trajectory file. Indices start at 1.
        This number is given to every atom in the trajectory, so atoms of the same type(element)
        can be distinguished."""
        if self._index is None:
            raise ValueError(
                f"'index' is not defined for '{self.__class__.__name__}({self.type} {self.x} {self.y} {self.z})'"
            )
        return self._index

    @index.setter
    def index(self, idx: int):
        """Sets the index of the atom (this is 1-indexed by default)."""
        self._index = idx

    @property
    def parent(self) -> "ichor.core.atoms.Atoms":  # noqa F821
        """Returns the parent instance (an instance of `Atoms` class) that holds self (an instance of `Atom`).

        :raises ValueError: if parent is not defined
        :return: parent instance of type `Atoms`
        :rtype: ichor.core.atoms.Atoms
        """

        if self._parent is None:
            raise ValueError(
                f"'parent' is not defined for '{self.__class__.__name__}({self.type} {self.x} {self.y} {self.z})'"
            )
        return self._parent

    @parent.setter
    def parent(self, parent: "ichor.core.atoms.Atoms"):  # noqa F821
        """Setter method for ._parent attribute.

        :param parent: The parent instance (of type `Atoms`) which holds self (an `Atom` instance)
        :type parent: ichor.core.atoms.Atoms
        """
        self._parent = parent

    @property
    def nuclear_charge(self) -> float:
        """Returns the nuclear charge of the atom as a float

        :return: the nuclear change of the atom
        :rtype: float
        """
        return constants.type2nuclear_charge[self.type]

    @property
    def i(self) -> int:
        """Returns the index of the atom, if used in any arrays/list in Python.

        :return: the index of the atom (0-indexed)
        :rtype: int
        """
        return self.index - 1

    @property
    def name(self) -> str:
        """Returns the name of the Atom instance, which is later used to distinguish atoms when making GPR models.
        The number in the name starts at 1 (inclusive).
        e.g. O1

        :return: the name of the atom (the type + the index of the atom (the indices start from 1))
        :rtype: str
        """
        return f"{self.type}{self.index}"

    @property
    def mass(self) -> float:
        """Returns the mass of the atom

        :return: The atomic mass of the atom
        :rtype: float
        """
        return round(constants.type2mass[self.type], 6)

    @property
    def radius(self):
        """Returns the covalent radius of the given Atom instance.

        :return: Covalent radius of the Atom instance (as defined by the atom type)
        :rtype: float
        """
        return round(constants.type2rad[self.type], 2)

    @property
    def vdwr(self):  # todo: fix
        """Returns the Van der Waals radius of the given Atom instance.

        :return: The Van der Waals radius of the atom (as defined by the atom type)
        :rtype: float
        """
        return round(constants.type2vdwr[self.type], 2)

    @property
    def electronegativity(self) -> float:
        """Returns the electronegativity of the Atom instance

        :return: The electronegativity of the atom (as defined by the atom type)
        :rtype: float
        """
        return constants.type2electronegativity[self.type]

    @property
    def valence(self) -> int:
        """Returns the valence of the `Atom` instance

        :return: the valence of the atom (as defined by the atom type)
        :rtype: int
        """
        return constants.type2valence[self.type]

    # TODO: this is not correct as we only need to look at the outer shell.
    # @property
    # def unpaired_electrons(self):
    #     """Returns the number of unpaired electrons of the atom

    #     :return: _description_
    #     :rtype: _type_
    #     """

    #     return constants.type2orbital[self.type].value - self.valence

    @property
    def coordinates_string(self) -> str:
        """Returns the coordinate string representation of the atom

        :return: coordinate string of atom (x, y, z coordinates)
        :rtype: str
        """
        width = str(16)
        precision = str(8)
        return f"{self.x:{width}.{precision}f}{self.y:{width}.{precision}f}{self.z:{width}.{precision}f}"

    @property
    def xyz_string(self) -> str:
        """Returns the atom type and coordinates for one Atom instance.
        This is used to write out an xyz file, which expects
        entries in the form of atom_type x_coordinate, y_coordinate, z_coordinate

        :return: coordinate string of atom with atom type (atom.type x, y, z)
        :rtype: str
        """
        return f"{self.type:<3s}{self.coordinates_string}"

    def vec_to(self, other: "Atom") -> np.ndarray:  # noqa F821
        """
        Calculates the vector from self to other
        :param other: atom to calculate the vector to
        :return: the vector from self to other as numpy array
        """
        return other.coordinates - self.coordinates

    def dist(self, other: "Atom") -> float:  # noqa F821
        """
        Calculated the distance between self and other
        :param other: atom to calculate the distance to
        :return: the distance between self and other as a float
        """
        d = self.coordinates - other.coordinates
        return np.sqrt(d.dot(d))

    def angle(self, atom1: "Atom", atom2: "Atom") -> float:  # noqa F821
        """
        Angle subtending atom1-self-atom2
        :param atom1: atom bonded to self
        :param atom2: other atom bonded to self
        :return: angle subtending atom1-self-atom2 as float
        """
        d1 = self.coordinates - atom1.coordinates
        d2 = self.coordinates - atom2.coordinates
        return np.arccos(d1.dot(d2) / (np.sqrt(d1.dot(d1)) * np.sqrt(d2.dot(d2))))

    def dihedral(
        self, atom1: "Atom", atom2: "Atom", atom3: "Atom"
    ) -> float:  # noqa F821
        """Caluclates dihedral angle between the current atom and three other atoms

        :param atom1: first atom in dihedral
        :param atom2: second atom in dihedral
        :param atom3: third atom in dihedral
        :return: The dihedral angle between the 4 atoms
        """

        p0 = self.coordinates
        p1 = atom1.coordinates
        p2 = atom2.coordinates
        p3 = atom3.coordinates
        b0 = p0 - p1
        b1 = p2 - p1
        b2 = p3 - p2
        # Normalize b1 so that it does not influence magnitude of vector rejections
        b1 /= np.linalg.norm(b1)
        # Vector rejections
        v = b0 - np.dot(b0, b1) * b1
        w = b2 - np.dot(b2, b1) * b1
        x = np.dot(v, w)
        y = np.dot(np.cross(b1, v), w)
        angle_radians = np.arctan2(y, x)
        angle_degrees = np.degrees(angle_radians)
        return angle_degrees

    def connectivity(
        self, connectivity_calculator: Callable[..., np.ndarray]
    ) -> np.ndarray:
        """
        Returns the 1D np.array corresponding to the connectivity of ONE Atom with respect to all other Atom
        instances that are held in an Atoms instance.
        For an `Atom` instance, this is only one row of the full connectivity matrix
        of the Atoms instance that is self.parent.
        However, to compute the connectivity in the first place,
        we need access to the `Atoms` instance (self.parent).

        :param connectivity_calculator: function which calculates connectivity for given atom.
        """
        return connectivity_calculator(self.parent)[self.i]

    def bonded_atoms(self, connectivity_calculator: Callable[..., list]) -> list:
        """Returns a list of Atom instances to which this Atom instance is connected

        :param connectivity_calculator: function which calculates connectivity for given atom.
        :return: A list of `Atom` instances to which this atom is bonded to
        """
        connectivity_matrix_row = self.connectivity(connectivity_calculator)
        return [
            self.parent[connected_atom]
            for connected_atom in connectivity_matrix_row.nonzero()[0]
        ]

    def bonded_atoms_names(self, connectivity_calculator: Callable[..., list]) -> list:
        """Returns a list of the names of Atom instances to which this Atom instance is connected

        :param connectivity_calculator: function which calculates connectivity for given atom.
        :return: A list of atom names (str) to which this atom is bonded to
        """
        connectivity_matrix_row = self.connectivity(connectivity_calculator)
        return [
            self.parent[connected_atom].name
            for connected_atom in connectivity_matrix_row.nonzero()[0]
        ]

    def bonded_atoms_i(self, connectivity_calculator: Callable[..., list]) -> list:
        """Returns a list of Atom indices to which this Atom instance is connected

        :param connectivity_calculator: function which calculates connectivity for given atom.
        :return: A list of atom indices to which this atom is bonded to (these are 0-indexed)
        """
        connectivity_matrix_row = self.connectivity(connectivity_calculator)
        return [
            self.parent[connected_atom].i
            for connected_atom in connectivity_matrix_row.nonzero()[0]
        ]

    def alf(self, alf_calculator: Callable[..., ALF], *args, **kwargs) -> ALF:
        """Returns an instance of ALF. This ALF is ONLY for this Atom.

        e.g. If we have an Atoms instance for the water monomer,
        the ALF for the whole water monomer can be written as [[0,1,2], [1,0,2], [2,0,1]],
        while the ALF for the first atom only is [0,1,2]

        [0,1,2] contains the indices for the central atom, x-axis atom,
        and xy-plane atom. These indices start at 0 to index Python objects correctly.

        :param alf_calculator: function which calculates Atomic Local Frame for given atom.
        :return: An `ALF` instance which contains the origin atom index
            (self.i) as well as the x-axis and optionally xy-plane index.
            For two-atom systems, there is only an x-axis index.
        """
        return alf_calculator(self, *args, **kwargs)

    def alf_array(
        self, alf_calculator: Callable[..., np.ndarray], *args, **kwargs
    ) -> np.ndarray:
        """Returns a list containing the index of the central atom, the x-axis atom, and the xy-plane atom.
        THere indices are what are used in python lists (as they start at 0).

        :param alf_calculator: function which calculates Atomic Local Frame for given atom.
        :return: A numpy array containing the central atom index (self.i), as well as the x-axis and xy-plane indices.
        """
        alf = self.alf(alf_calculator, *args, **kwargs)
        return np.array([alf.origin_idx, alf.x_axis_idx, alf.xy_plane_idx])

    def C(self, alf: ALF) -> np.ndarray:
        """
        Mills, M.J.L., Popelier, P.L.A., 2014.
        Electrostatic Forces: Formulas for the First Derivatives of a Polarizable,
        Anisotropic Electrostatic Potential Energy Function Based on Machine Learning.
        Journal of Chemical Theory and Computation 10, 3840-3856.. doi:10.1021/ct500565g

        Eq. 25-30

        :param alf: An atomic local frame (ALF instance) which is then used to calculate the C matrix for a given ALF.
        :return: A 3x3 rotation matrix (C matrix) which rotates from Global cartesian to local frame
            where the origin (0,0,0) is the current atom, the x-axis is the x-axis atom, the xy-plane is defined by the
            xy-plane atom, and the z-axis is orthogonal to the xy-plane.
        """
        return calculate_c_matrix(self, alf)

    def features(
        self, feature_calculator: Callable[..., np.ndarray], *args, **kwargs
    ) -> np.ndarray:
        """Returns a 1D 3N-6 np.ndarray of the features for the current Atom instance.

        :param feature_calculator: A function used to calculate features from the `Atom` instance
        :param args: positional arguments to pass to feature calculator function.
        :param kwargs: key word arguments to pass to the feature calculator function. Check the feature calculator
            to see what required key word arguments the calculator needs to function.
        :return: The features associated with self.

        .. note::
            The current implementation allows us to fairly easily switch between features as we can change the
            calculator that is being used, as well as pass in new key word arguments to the given calculator.
        """

        return feature_calculator(self, *args, **kwargs)

    def __str__(self):
        """Print out the atom name (containing atom type and index as used in model making), as well as
        coordinates of the atom
        """
        return f"{self.name} {self.coordinates_string}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name:<3s}{self.coordinates_string})"

    def __eq__(self, other: "Atom") -> bool:  # noqa F821
        """Equality check for two `Atom` instances

        :param other: other instance of `Atom`
        :type other: `Atom`
        :raises ValueError: If both objects are not instance of `Atom`
        :return: True if the atom names are the same, false otherwise
        :rtype: bool
        """
        # TODO: figure out a good way to check equality, but why do we need this in the first place?
        if isinstance(other, Atom):
            return (
                self.name == other.name
            )  # <- is this how we want to compare equality?
        # elif isinstance(other, int):  # <- this is a bit stupid and caused a lot of errors
        #     return self.index == other
        else:
            raise ValueError(
                f"Cannot compare type({type(other)}) with type({type(self)})"
            )

    def __hash__(self):
        return hash(str(self.index) + str(self.coordinates_string))

    def __sub__(self, other: "Atom"):  # noqa F821
        """Implements subtraction for two `Atom` instances

        :param other: `Atom` instance
        :type other: `Atom`
        :return: self with the coordinates of the other `Atom` instance subtracted
        :rtype: `Atom`
        """
        self.coordinates -= other.coordinates
        return self
