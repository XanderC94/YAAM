'''
Custom exception module
'''
from pathlib import Path
import sys
from yaam.utils.logger import static_logger as logger

def exception_handler(ex_type, ex_value, ex_traceback):
    '''
    Uncaught exception handler
    '''
    if issubclass(ex_type, KeyboardInterrupt):
        sys.__excepthook__(ex_type, ex_value, ex_traceback)
        return

    logger().critical("Uncaught exception", exc_info=(ex_type, ex_value, ex_traceback))

class ConfigLoadException(Exception):
    '''
    ConfigLoadException
    '''
    def __init__(self, config_path: Path):
        super().__init__()
        self.config_path = config_path
