'''
Release execution module
'''

import os
from pathlib import Path
import sys
from yaam.model.context import AppContext
from yaam.utils.logger import init_static_logger, logging
from yaam.utils.exceptions import exception_handler
from main import run_main

if __name__ == "__main__":

    # Add crash handler
    sys.excepthook = exception_handler

    WORK_DIR = Path(os.getcwd())
    TEMP_DIR = Path(os.getenv("TEMP"))

    logger = init_static_logger(
        # logger_name='Yaam-logger',
        log_level=logging.INFO,
        log_file=TEMP_DIR/"yaam-release.log"
    )

    logger.info(msg=WORK_DIR)

    app_context = AppContext()

    app_context.create_app_environment()

    execution_result = run_main(app_context)

    sys.exit(execution_result)
