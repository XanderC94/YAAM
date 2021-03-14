'''
Process execution utility function
'''

import time
import subprocess
from pathlib import Path

def run(target: Path, workspace: Path, args: list = None):
    '''
    Run the target process in the specified workspace
    and the provided arguments.

    @target : Path -- process to run
    @workspace : Path -- workspace in which run the process
    @args : list -- list of command line parameters provided to the process
    '''
    print(f"Launching {target.stem}...")

    if args:
        print(f"Arguments: {args}")
        subprocess.Popen(executable=str(target), cwd=str(workspace), args=args)
    else:
        subprocess.Popen(executable=str(target), cwd=str(workspace), args=[])

    time.sleep(5)
