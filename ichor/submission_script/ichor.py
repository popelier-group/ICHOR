import os
import sys
from pathlib import Path
from typing import List, Optional

from ichor.common.functools import classproperty
from ichor.submission_script.python import PythonCommand


class ICHORCommand(PythonCommand):
    def __init__(
        self, script: Optional[Path] = None, args: Optional[List[str]] = None
    ):
        PythonCommand.__init__(
            self,
            script or Path(sys.argv[0]).resolve(),
            args if args is not None else [],
        )

        from ichor.arguments import Arguments
        from ichor.globals import GLOBALS

        self.args += [f"-c {Arguments.config_file}", f"-u {GLOBALS.UID}"]

    @classproperty
    def group(self) -> bool:
        return False

    def run_function(self, function_to_run, *args):
        arg_str = " ".join(f'"{str(arg)}"' for arg in args)
        self.args += [f"-f {function_to_run} {arg_str}"]