from pathlib import Path
from objects.render import Render

class Addon(object):

    def __init__(
        self, 
        name: str, 
        path: Path, path_d3d9 : Path, 
        update_url: str, hash_url: str, 
        update: bool, enabled: bool, 
        dxgi: Render = Render.DXGI_9
    ):
        self.__name = name
        self.__path = path
        self.__path_d3d9 = path_d3d9
        self.__update_url = update_url
        self.__hash_url = hash_url
        self.__update = update
        self.__enabled = enabled
        self.__dxgi = dxgi

    @property
    def name(self) -> str:
        return self.__name
    
    def path_dxgi(self, dxgi : Render) -> Path:
        p : Path = Path()

        if dxgi == Render.DXGI_9:
            p = self.path_d3d9              
        elif dxgi == Render.DXGI_11:
            p = self.path_d3d11

        return p
    
    @property
    def path(self) -> Path:
        return self.path_dxgi(self.dxgi)
    
    @property
    def path_d3d9(self) -> Path:
        return self.__path_d3d9
    
    @property
    def path_d3d11(self) -> Path:
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

    @property
    def dxgi(self) -> bool:
        return self.__dxgi

    def is_dll(self) -> bool:
        return self.__path.suffix == ".dll"

    def is_exe(self) -> bool:
        return self.__path.suffix == ".exe"

class AddonFactory(object):

    @staticmethod
    def from_dict(json: dict, dxgi:Render = Render.DXGI_9):
        return Addon(
            json['name'],
            Path(json['path']),
            Path(json['path_d3d9'] if 'path_d3d9' in json else json['path']),
            json['uri'],
            json['hash'],
            json['update'],
            json['enabled'],
            dxgi
        )

    @staticmethod
    def to_table(addon: Addon):
        table : dict = {}

        table['name'] = addon.name
        table['path'] = addon.path.name
        table['update'] = addon.update
        table['enabled'] = addon.enabled

        return table
