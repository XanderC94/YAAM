'''
Debug execution module
'''

import os
# from pathlib import Path
from sys import exit as close, stdout
from yaam.utils.logger import static_logger, logging
from main import run_main

if __name__ == "__main__":
    # WORK_DIR = Path(os.path.realpath(__file__)).parent.parent
    # os.chdir(WORK_DIR)

    logger = static_logger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stdout)
    logger.addHandler(handler)

    logger.debug(msg=os.getcwd())

    execution_result = run_main()

    close(execution_result)
