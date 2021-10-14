'''
Object normalizations utils
'''
from pathlib import Path
from typing import Union

def normalize_abs_path(path: Union[str, Path], root: Path) -> Path:
    '''
    Normalize a path to abs
    '''
    new_path = str(path)

    while new_path.startswith("../") or new_path.startswith("..\\"):
        new_path = new_path[3:]

    while new_path.startswith("."):
        new_path = new_path[1:]

    if new_path.startswith("\\") or new_path.startswith("/"):
        new_path = new_path[1:]

    if not Path(new_path).is_absolute():
        new_path = root / new_path

    return new_path
