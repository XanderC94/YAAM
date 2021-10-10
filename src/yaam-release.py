'''
Release execution module
'''

import os
from pathlib import Path
from sys import exit as close, stdout
from logging import handlers
from yaam.utils.logger import static_logger, logging
from main import run_main

if __name__ == "__main__":
    WORK_DIR = Path(os.path.realpath(__file__)).parent

    os.chdir(WORK_DIR)

    APPDATA = Path(os.getenv("APPDATA"))
    YAAM_DIR = APPDATA / "yaam"
    LOG_DIR = YAAM_DIR / "log"

    os.makedirs(LOG_DIR, exist_ok=True)

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    logger = static_logger()
    logger.setLevel(logging.INFO)

    fhandler = handlers.RotatingFileHandler(
        LOG_DIR/"yaam.log",
        mode='w',
        encoding='utf-8',
        backupCount=3,
        maxBytes=(2*1024**2)
    )

    fhandler.setLevel(logging.DEBUG)
    fhandler.setFormatter(log_formatter)

    shandler = logging.StreamHandler(stdout)
    shandler.setLevel(logging.INFO)
    shandler.setFormatter(log_formatter)

    logger.addHandler(shandler)
    logger.addHandler(fhandler)

    logger.info(msg=os.getcwd())

    execution_result = run_main()

    close(execution_result)
