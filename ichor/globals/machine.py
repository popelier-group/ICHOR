from enum import Enum


class Machine(Enum):
    """ Enum which is used to define any machines that ICHOR is running on as commands and settings change between different machines."""
    csf3 = "csf3"
    ffluxlab = "ffluxlab"
    local = "local"
