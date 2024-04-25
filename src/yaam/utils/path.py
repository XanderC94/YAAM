'''
Path utils module
'''

from os import path as pathutils
from pathlib import Path


def mkpath(s: str) -> Path:
    '''
    Return an expanded and resolved pathlib.Path object
    '''
    return Path(pathutils.expandvars(s)).resolve()
