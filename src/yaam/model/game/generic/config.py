'''
Generic game config class module
'''

from yaam.utils.path import Path, mkpath
from yaam.utils.logger import static_logger as logger
from yaam.model.game.abstract.config import AbstractGameConfiguration
from yaam.model.type.binding import BindingType
from yaam.utils.json.io import read_json


class GenericGameConfig(AbstractGameConfiguration):
    '''
    Guild Wars 2 model class
    '''

    def __init__(self, appdata_dir: Path):

        super().__init__(BindingType.D3D9)

        self._name = "Unknown game"
        self._config_path = appdata_dir
        self._root = Path()
        self._exe = ""

    def load(self, init_file_path: Path = None) -> bool:

        logger().info(msg=f"Reading game path from {init_file_path}.")

        if init_file_path is not None:
            init_data: dict = read_json(init_file_path)
            self._name = init_data.get('name', str())
            self._config_path = mkpath(init_data.get('config_path', str()))
            self._root = mkpath(init_data.get('root', str()))
            self._exe = init_data.get('exe', str())
            self._native_binding_type = BindingType.from_string(init_data.get('binding', 'dx9'))

        return self._config_path.exists() and self._root.exists() and (self._root / self._exe).exists()
