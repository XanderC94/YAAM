'''
Abstract Game class module
'''

from pathlib import Path
from yaam.model.type.binding import BindingType
from yaam.model.game.contract.config import IGameConfiguration

class AbstractGameConfiguration(IGameConfiguration):
    '''
    Game model base class
    '''

    def __init__(self, appdata_dir: Path, default_binding : BindingType = BindingType.AGNOSTIC):

        self._name: str = str()
        self._appdata_dir: Path = appdata_dir
        self._config_path: Path = Path()
        self._native_binding_type: BindingType = default_binding
        self._root = Path()
        self._exe = str()

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._config_path

    @property
    def game_root(self) -> Path:
        return self._root

    @property
    def game_path(self) -> Path:
        return self._root / self._exe

    @property
    def native_binding(self) -> BindingType:
        return self._native_binding_type

    @property
    def bin_directory(self) -> Path:
        return self._root / "bin"
