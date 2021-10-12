'''
Simple static logging utility module
'''
import logging
from sys import stdout
from logging import handlers
from pathlib import Path

def static_logger(name = None):
    '''
    Simple static logger
    '''
    return logging.getLogger(name)

def init_static_logger(
        logger_name : str = None,
        log_level = logging.INFO,
        msg_format : str = '%(asctime)s %(levelname)s %(message)s',
        date_format : str = '%Y-%m-%d %H:%M:%S',
        log_file : Path = Path(),
        log_stream = stdout
    ):
    '''
    Initialize the given logger
    '''
    log_formatter = logging.Formatter(msg_format, datefmt=date_format)

    logger = static_logger(logger_name)
    logger.setLevel(log_level)

    if log_file.exists():
        fhandler = handlers.RotatingFileHandler(
            log_file,
            mode='w',
            encoding='utf-8',
            backupCount=3,
            maxBytes=(2*1024**2)
        )

        fhandler.setFormatter(log_formatter)
        fhandler.setLevel(log_level)
        logger.addHandler(fhandler)

    shandler = logging.StreamHandler(log_stream)
    shandler.setLevel(log_level)
    shandler.setFormatter(log_formatter)
    logger.addHandler(shandler)

    return logger
