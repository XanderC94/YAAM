'''
Process execution utility module
'''

import time
import subprocess
from typing import Iterable
from pathlib import Path
from yaam.utils.logger import static_logger as logger

def arun(target: Path or str, workspace: Path or str, args: Iterable[str] = None, slack = 3):
    '''
    Run async the target process in the specified workspace and the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    _args = args if args is not None else []
    logger().info("Launching %s %s", target.name if isinstance(target, Path) else target, ' '.join(_args))

    subprocess.Popen(executable=str(target), cwd=str(workspace), args=_args)

    time.sleep(slack)

def run(target: Path or str, workspace: Path or str, args: Iterable[str] = None, slack = 3):
    '''
    Run the target process in the specified workspac with the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    _args = args if args is not None else []
    logger().info("Launching %s %s", target.name if isinstance(target, Path) else target, ' '.join(_args))

    proc = subprocess.Popen(executable=str(target), cwd=str(workspace), args=_args)

    proc.wait()

    time.sleep(slack)
