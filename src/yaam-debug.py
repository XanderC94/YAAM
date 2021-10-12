'''
Debug execution module
'''

import os
from pathlib import Path
import sys
from yaam.utils.logger import init_static_logger, logging
from yaam.utils.exceptions import exception_handler
from main import run_main, create_environment

if __name__ == "__main__":

    sys.excepthook = exception_handler

    WORK_DIR = Path(os.getcwd())
    TEMP_DIR = Path(os.getenv("TEMP"))

    logger = init_static_logger(
        # logger_name='Yaam-logger',
        log_level=logging.DEBUG,
        log_file=TEMP_DIR/"yaam-debug.log"
    )

    logger.debug(msg=WORK_DIR)

    create_environment()

    execution_result = run_main()

    sys.exit(execution_result)
