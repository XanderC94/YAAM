'''
ZIP helper functions module
'''
from typing import List
from zipfile import ZipFile

def get_root_dirs(zip: ZipFile) -> List[str]:
    '''
    Returns the names of all the root directories in the archive
    '''

    return [
        _.filename for _ in zip.filelist
        if _.filename.count('/') == 1 and _.is_dir()
    ]

def get_root_items(zip: ZipFile) -> List[str]:
    '''
    Returns the names of all the root items (directories and files) in the archive
    '''

    return [
        _.filename for _ in zip.filelist
        if _.filename.count('/') == 0 or (_.filename.count('/') == 1 and _.is_dir()) 
    ]

