from pathlib import Path
from typing import List, Optional

from ichor.batch_system import JobID
from ichor.common.types import MutableValue
from ichor.submission_script import (SCRIPT_NAMES, AIMAllCommand,
                                     SubmissionScript, TimingManager)

# todo: better naming for file and function
def auto_run_aimall(
    npoints: MutableValue,
    atoms: MutableValue = None,
    hold: Optional[JobID] = None,
) -> Optional[JobID]:
    """ Submit an AIMALL job to the workload manager. This job generates .int files."""
    script_name = SCRIPT_NAMES["aimall"]
    aimall_script = SubmissionScript(script_name)
    with TimingManager(aimall_script):
        for point in range(npoints.value):
            aimall_script.add_command(
                AIMAllCommand(Path(f"Point{point+1}"), atoms.value)
            )
    aimall_script.write()
    return aimall_script.submit(hold=hold)
