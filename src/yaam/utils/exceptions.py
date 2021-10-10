'''
Custom exception module
'''
from pathlib import Path

class ConfigLoadException(Exception):
    '''
    ConfigLoadException
    '''
    def __init__(self, config_path: Path):
        super().__init__()
        self.config_path = config_path
