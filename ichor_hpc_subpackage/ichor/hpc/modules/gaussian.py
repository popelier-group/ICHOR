from ichor.hpc.machine import Machine
from ichor.hpc.modules.modules import Modules

GaussianModules = Modules()


GaussianModules[Machine.csf3] = [
    "apps/binapps/gaussian/g09d01_em64t",
]

GaussianModules[Machine.csf4] = [
    "gaussian/g16c01_em64t_detectcpu",
]

GaussianModules[Machine.ffluxlab] = [
    "apps/gaussian/g09",
]

GaussianModules[Machine.local] = [
    "test/gaussian/module",
]
