import multiprocessing as mp

from ichor.ichor_hpc.batch_system import ParallelEnvironments
from ichor.ichor_hpc.machine_setup.machine import Machine

PARALLEL_ENVIRONMENT = ParallelEnvironments()

PARALLEL_ENVIRONMENT[Machine.csf3]["smp.pe"] = 2, 32
PARALLEL_ENVIRONMENT[Machine.ffluxlab]["smp"] = 2, 44
PARALLEL_ENVIRONMENT[Machine.local]["mp"] = 2, mp.cpu_count()