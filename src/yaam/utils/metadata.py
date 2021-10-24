'''
Metadata utils module
'''

from pathlib import Path
from typing import Dict, List
import win32com.client

def get_windows_namespace(path: Path):
    '''
    Get windows namespace for the specified path
    '''
    shell = None
    namespace = None

    if path.exists():
        __path = path.resolve()
        shell=win32com.client.gencache.EnsureDispatch('Shell.Application', 0)
        namespace = shell.NameSpace(str(__path.parent if __path.is_file() else __path))

    return (shell, namespace)

def get_wfile_metaheader(path: Path, namespace = None) -> List[str]:
    '''
    Get file metadata header
    '''
    header = []
    if path.exists():
        __path = path.resolve()
        if namespace is None:
            [_, namespace] = get_windows_namespace(__path)

        i = 0
        while i >= 0:
            attr = namespace.GetDetailsOf(None, i)
            if attr is None or len(attr) == 0:
                i = -1
            else:
                header.append(attr)
                i += 1

    return header

def get_wfile_metadata(path: Path, namespace = None, header: List[str] = None) ->  Dict[str, str]:
    '''
    Retreive windows file metadata
    '''
    metadata = {}
    if path.exists() and path.is_file():
        __path = path.resolve()
        if namespace is None:
            [_, namespace] = get_windows_namespace(__path)

        if header is None or len(header) == 0:
            header = get_wfile_metaheader(path, namespace)

        target = namespace.ParseName(__path.name)
        for i, attr in enumerate(header):
            value = namespace.GetDetailsOf(target, i)
            if value:
                metadata[attr] = value

    return metadata


if __name__ == "__main__":

    p = Path("C:/opt/Guild Wars 2/")

    for _ in p.iterdir():
        if _.is_file() and '.dll' in _.name:
            print(get_wfile_metadata(path=_))
