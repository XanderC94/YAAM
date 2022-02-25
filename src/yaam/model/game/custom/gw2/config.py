'''
Guild Wars 2 model class
'''
from yaam.utils.path import Path, mkpath
from bs4 import BeautifulSoup
from yaam.utils.logger import static_logger as logger
from yaam.utils.json.io import read_json
from yaam.model.type.binding import BindingType
from yaam.model.game.abstract.config import AbstractGameConfiguration

#############################################################################################


class GW2Config(AbstractGameConfiguration):
    '''
    Guild Wars 2 model class
    '''

    def __init__(self, appdata_dir: Path):

        super().__init__(BindingType.D3D9)

        self._name = "Guild Wars 2"
        self._config_path = appdata_dir / self._name / "GFXSettings.Gw2-64.exe.xml"
        self._root = Path("C:\\Program Files\\Guild Wars 2")
        self._exe = "Gw2-64.exe"

    @property
    def bin_directory(self) -> Path:
        return self._root / ("bin64" if "64" in self._exe else "bin")

    def load(self, init_file_path: Path = None) -> bool:

        load_ok = False

        if init_file_path is not None:
            init_data: dict = read_json(init_file_path)
            self._name = init_data.get('name', self._name)
            self._config_path = mkpath(init_data.get('config_path', self._config_path))

        logger().info(msg=f"Reading game path from {self.path}.")

        if self.path.exists():
            with open(self.path, encoding="utf-8") as _:

                gw2_config_xml = BeautifulSoup(_, features="xml")
                if gw2_config_xml is not None:
                    gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

                    self._root = mkpath(gw2_app_token.find("INSTALLPATH")['Value'])
                    self._exe = gw2_app_token.find("EXECUTABLE")['Value']

                    if self._root.exists():
                        logger().info(msg=f"GW2 location is {self._root}.")
                        load_ok = True
                    else:
                        logger().info(msg=f"{self._root} doesn't exists!")
                else:
                    logger().error(msg=f"Error opening {self.path}")

        else:
            logger().error(msg=f"{self.path} doesn't exists!")

        return load_ok
