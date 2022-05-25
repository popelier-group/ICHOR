from ichor.ichor_hpc.machine_setup.machine_setup import Machine
from ichor.modules.modules import Modules

PythonModules = Modules()

PythonModules[Machine.csf3] = ["apps/anaconda3/5.2.0/bin"]

PythonModules[Machine.ffluxlab] = ["apps/anaconda3/3.7.6"]
