'''
Process execution utility module
'''

import time
import subprocess
from typing import Iterable
from pathlib import Path
from yaam.utils.logger import static_logger as logger

def run(target: Path, workspace: Path, args: Iterable[str] = None, slack = 5):
    '''
    Run the target process in the specified workspace
    and the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    _args = args if args is not None else []
    logger().info("Launching %s %s", target.name, ' '.join(_args))

    subprocess.Popen(executable=str(target), cwd=str(workspace), args=_args)

    time.sleep(slack)
