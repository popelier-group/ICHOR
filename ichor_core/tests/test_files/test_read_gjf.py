from pathlib import Path
from typing import List, Optional

from ichor.core.atoms import Atom, Atoms
from ichor.core.common.units import AtomicDistance
from ichor.core.files import GJF

from tests.path import get_cwd
from tests.test_atoms import _test_atoms_coords
from tests.test_files import _assert_val_optional

example_dir = example_dir = (
    get_cwd(__file__) / ".." / ".." / ".." / "example_files" / "example_gjfs"
)


def _test_read_gjf(
    gjf_file: Path,
    link0: Optional[List[str]] = None,
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    title: Optional[str] = None,
    charge: Optional[int] = None,
    spin_multiplicity: Optional[int] = None,
    atoms: Optional[Atoms] = None,
):

    "Test function for .gjf Gaussian input file."

    gjf = GJF(gjf_file)

    _assert_val_optional(gjf.link0, link0)
    _assert_val_optional(gjf.method, method)
    _assert_val_optional(gjf.basis_set, basis_set)
    _assert_val_optional(gjf.keywords, keywords)
    _assert_val_optional(gjf.title, title)
    _assert_val_optional(gjf.charge, charge)
    _assert_val_optional(gjf.spin_multiplicity, spin_multiplicity)
    _test_atoms_coords(gjf.atoms, atoms, AtomicDistance.Angstroms)


def test_water_standard():

    expected_atoms = Atoms(
        [
            Atom("O", -0.99873211, 3.65062916, 0.00994269),
            Atom("H", -0.62416886, 4.26690992, -0.45055934),
            Atom("H", -0.54401474, 2.89586390, 0.23152816),
        ]
    )

    _test_read_gjf(
        example_dir / "water_standard.gjf",
        method="B3LYP",
        basis_set="6-31+g(d,p)",
        keywords=["output=wfn", "nosymm"],
        title="WATER0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_water_aug_cc_pVTZ():

    expected_atoms = Atoms(
        [
            Atom("O", -0.99873211, 3.65062916, 0.00994269),
            Atom("H", -0.62416886, 4.26690992, -0.45055934),
            Atom("H", -0.54401474, 2.89586390, 0.23152816),
        ]
    )

    _test_read_gjf(
        example_dir / "water_aug-cc-pVTZ.gjf",
        method="B3LYP",
        basis_set="aug-cc-pVTZ",
        keywords=["nosymm", "output=wfn"],
        title="WATER0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_water_ccsd():

    expected_atoms = Atoms(
        [
            Atom("O", -14.18489633, 2.78702924, 21.97580519),
            Atom("H", -14.50376292, 2.49728039, 21.10071552),
            Atom("H", -14.12730590, 3.75706408, 21.85961217),
        ]
    )

    _test_read_gjf(
        example_dir / "water_ccsd.gjf",
        method="CCSD(T)",
        basis_set="aug-cc-pVDZ",
        keywords=["nosymm"],
        title="WATER0001",
        link0=[
            "chk=TRAINING_SET/WATER0001/WATER0001.chk",
            "nproc=2",
            "mem=1GB",
        ],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_ammonia_standard():

    expected_atoms = Atoms(
        [
            Atom("N", 1.30610788, -29.77550072, -0.39451506),
            Atom("H", 0.88322943, -29.08071028, -1.14190493),
            Atom("H", 1.46749713, -29.22282070, 0.46703669),
            Atom("H", 2.11921902, -30.18852549, -0.75438182),
        ]
    )

    _test_read_gjf(
        example_dir / "ammonia_standard.gjf",
        method="B3LYP",
        basis_set="6-31+g(d,p)",
        keywords=["nosymm", "output=wfn"],
        title="AMMONIA0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_formamide_standard():

    expected_atoms = Atoms(
        [
            Atom("C", 3.24078329, 1.87070735, 2.61356454),
            Atom("O", 2.63418361, 0.90388896, 2.99206038),
            Atom("N", 2.74798428, 3.18075790, 2.55472586),
            Atom("H", 4.24315370, 1.94368994, 2.10760323),
            Atom("H", 1.91980469, 3.61981117, 3.08803184),
            Atom("H", 3.39639749, 3.90997876, 2.20587250),
        ]
    )

    _test_read_gjf(
        example_dir / "formamide_standard.gjf",
        method="B3LYP",
        basis_set="6-31+g(d,p)",
        keywords=[
            "CPHF(GRID=FINE)",
            "output=wfn",
            "INT(GRID=ULTRAFINE)",
            "nosymm",
        ],
        title="FORMAMIDE0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_paracetamol_standard():

    expected_atoms = Atoms(
        [
            Atom("C", 1.20745000, -0.82175000, -0.09285000),
            Atom("C", 1.67645000, -1.62375000, 0.967150004),
            Atom("C", 1.01345000, -1.60975000, 2.23615000),
            Atom("C", -0.13355000, -0.80775000, 2.42315000),
            Atom("C", -0.63455000, -0.00075000, 1.33015000),
            Atom("C", 0.04645000, 0.02525000, 0.09515000),
            Atom("H", 2.66545000, -1.98675000, 0.79915000),
            Atom("O", 1.54545000, -2.41575000, 3.19615000),
            Atom("H", -0.65455000, -0.89275000, 3.43415000),
            Atom("H", -1.51555000, 0.63425000, 1.51115000),
            Atom("H", 1.78845000, -0.76375000, -0.99685000),
            Atom("N", -0.30855000, 0.78225000, -1.01285000),
            Atom("C", -1.33655000, 1.67525000, -1.35485000),
            Atom("H", 0.23245000, 0.47325000, -1.83185000),
            Atom("O", -2.10555000, 2.15725000, -0.53085000),
            Atom("C", -1.42255000, 1.95725000, -2.90185000),
            Atom("H", -0.44555000, 2.21125000, -3.30085000),
            Atom("H", -2.23655000, 2.68525000, -3.16685000),
            Atom("H", -1.68455000, 1.11225000, -3.54285000),
            Atom("H", 2.30245000, -2.79075000, 2.74015000),
        ]
    )

    _test_read_gjf(
        example_dir / "paracetamol_standard.gjf",
        method="B3LYP",
        basis_set="6-31+g(d,p)",
        keywords=["output=wfn", "nosymm"],
        title="PARACETAMOL0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )


def test_water_opt_freq():

    expected_atoms = Atoms(
        [
            Atom("O", -0.99873211, 3.65062916, 0.00994269),
            Atom("H", -0.62416886, 4.26690992, -0.45055934),
            Atom("H", -0.54401474, 2.89586390, 0.23152816),
        ]
    )

    _test_read_gjf(
        example_dir / "water_opt_freq.gjf",
        method="B3LYP",
        basis_set="6-31+g(d,p)",
        keywords=["output=wfn", "nosymm", "opt", "freq"],
        title="WATER0001",
        link0=["nproc=2", "mem=1GB"],
        charge=0,
        spin_multiplicity=1,
        atoms=expected_atoms,
    )
