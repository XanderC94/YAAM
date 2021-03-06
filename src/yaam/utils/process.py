'''
Process execution utility module
'''

import time
from subprocess import CompletedProcess, Popen, run as run_process
from typing import Iterable
from pathlib import Path
from yaam.utils.logger import static_logger as logger


def arun(target: Path or str, workspace: Path or str, args: Iterable[str] = None, slack: int = 3, **kwargs) -> Popen[str]:
    '''
    Run async the target process in the specified workspace and the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    str_args = [str(_) for _ in args] if args is not None else []
    str_target = str(target)
    str_working_dir = str(workspace)

    logger().info("Launching %s %s", target.name if isinstance(target, Path) else target, ' '.join(str_args))

    proc = Popen(executable=str_target, cwd=str_working_dir, args=str_args, **kwargs)

    time.sleep(slack)

    return proc


def run(target: Path or str, workspace: Path or str, args: Iterable[str] = None, slack: int = 3, **kwargs) -> int:
    '''
    Run the target process in the specified workspac with the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    str_args = [str(_) for _ in args] if args is not None else []
    str_target = str(target)
    str_working_dir = str(workspace)

    logger().info("Launching %s %s", target.name if isinstance(target, Path) else target, ' '.join(str_args))

    proc = Popen(executable=str_target, cwd=str_working_dir, args=str_args, **kwargs)

    ret = proc.wait()

    time.sleep(slack)

    return ret


def run_command(command: str, check=False, slack: int = 3, **kwargs) -> CompletedProcess[str]:
    '''
    Run the given string command
    '''
    logger().info("Executing %s", command)

    ret = run_process(command, check=check, **kwargs)

    time.sleep(slack)

    return ret
