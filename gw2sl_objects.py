from pathlib import Path

class Addon(object):

    def __init__(self, name: str, path: Path, update_url: str, hash_url: str, update: bool, enabled: bool):
        self.__name = name
        self.__path = path
        self.__update_url = update_url
        self.__hash_url = hash_url
        self.__update = update
        self.__enabled = enabled

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def path(self) -> Path:
        return self.__path
    
    @property
    def update_url(self) -> str:
        return self.__update_url

    @property
    def hash_url(self) -> str:
        return self.__hash_url
    
    @property
    def update(self) -> bool:
        return self.__update

    @property
    def enabled(self) -> bool:
        return self.__enabled

    def is_dll(self) -> bool:
        return self.__path.suffix == ".dll"

    def is_exe(self) -> bool:
        return self.__path.suffix == ".exe"

class AddonFactory(object):

    @staticmethod
    def from_dict(json: dict):
        return Addon(
            json['name'],
            Path(json['path']),
            json['uri'],
            json['hash'],
            json['update'],
            json['enabled']
        )
