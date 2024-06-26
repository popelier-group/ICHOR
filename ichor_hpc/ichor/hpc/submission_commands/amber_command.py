from pathlib import Path
from typing import List

import ichor.hpc.global_variables

from ichor.core.common.functools import classproperty
from ichor.hpc.global_variables import get_param_from_config
from ichor.hpc.submission_command import SubmissionCommand


class AmberCommand(SubmissionCommand):
    """
    todo: write docs
    """

    def __init__(
        self,
        mol2_file: Path,
        mdin_file: Path,
        system_name: str,
        temperature: float,
        ncores: int,
    ):
        self.mol2_file = mol2_file
        self.mdin_file = mdin_file
        self.temperature = temperature
        self.system_name = system_name
        self.ncores = ncores

    @classproperty
    def group(self) -> bool:
        return False

    @property
    def data(self) -> List[str]:
        """Do not need a datafile for this command."""
        return False

    @classproperty
    def modules(self) -> list:
        """Returns the modules that need to be loaded in order for Gaussian to work on a specific machine"""
        return get_param_from_config(
            ichor.hpc.global_variables.ICHOR_CONFIG,
            ichor.hpc.global_variables.MACHINE,
            "software",
            "amber",
            "modules",
        )

    @property
    def command(self) -> str:
        # TODO: mpi not needed for single molecule simulations
        # TODO: csf3 queue time for 1 core jobs is slow, so run on 2 cores

        # return (
        #     "sander"
        #     if self.ncores == 1
        #     else f"mpirun -n {self.ncores} sander.MPI"
        # )

        return get_param_from_config(
            ichor.hpc.global_variables.ICHOR_CONFIG,
            ichor.hpc.global_variables.MACHINE,
            "software",
            "amber",
            "executable_path",
        )

    def repr(self, *args) -> str:
        """
        Returns a strings which is then written out to the final submission script file.

        The length of `variables` is defined by the length of `self.data`
        """

        mol2_file = self.mol2_file.absolute()
        tleap_script = mol2_file.with_suffix(".tleap")
        frcmod_file = mol2_file.with_suffix(".frcmod")
        prmtop_file = mol2_file.with_suffix(".prmtop")
        inpcrd_file = mol2_file.with_suffix(".inpcrd")

        with open(tleap_script, "w") as f:
            f.write("source leaprc.protein.ff14SB\n")
            f.write("source leaprc.gaff2\n")
            f.write(f"mol = loadmol2 {mol2_file}\n")
            f.write(f"loadamberparams {frcmod_file}\n")
            f.write(f"saveamberparm mol {prmtop_file} {inpcrd_file}\n")
            f.write("quit")

        cmd = ""
        cmd += f"pushd {mol2_file.parent}\n"
        # run antechanmber to modify mol2 file for use in amber
        cmd += f"antechamber -i {mol2_file} -o {mol2_file} -fi mol2 -fo mol2 -c bcc -pf yes -nc -2 -at gaff2 -j 5 -rn {self.system_name}\n"  # noqa E501
        # run parmchk to generate frcmod file
        cmd += f"parmchk2 -i {mol2_file} -f mol2 -o {frcmod_file} -s 2\n"
        # run tleap to generate prmtop and inpcrd

        cmd += f"tleap -f {tleap_script}\n"
        # run amber
        cmd += f"{self.command} -O -i {self.mdin_file.absolute()} -o md.out -p {prmtop_file} -c {inpcrd_file} -inf md.info\n"  # noqa E501

        cmd += "popd\n"
        return cmd
