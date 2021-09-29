import json

from pathlib import Path
from bs4 import BeautifulSoup
from typing import Set, Dict

from utils.objectifier import objectify_json_settings

from objects.addon import AddonBase, Binding
from objects.binding_type import BindingType

class GW2:

    def __init__(self, appdata: Path):
        self.__app_data = appdata
        self.__config_path = self.__app_data / "Guild Wars 2/GFXSettings.Gw2-64.exe.xml"
        self.__settings_path = self.__app_data / "Guild Wars 2/Settings.json"
        self.__root = Path("C:\\Program Files\\Guild Wars 2")
        self.__exe = "Gw2-64.exe"

        self.args : Set[str] = set()
        self.bases : Dict[str, AddonBase] = list()
        self.bindings : Dict[BindingType, Dict[str, Binding]] = dict()

        self.__dxgi_type = BindingType.DXGI_9
    
    @property
    def config_path(self) -> Path:
        return self.__config_path

    @property
    def settings_path(self) -> Path:
        return self.__settings_path
    
    @property
    def root(self) -> Path:
        return self.__root

    @property
    def path(self) -> Path:
        return self.root / self.__exe

    @property
    def dxgi(self) -> BindingType:
        return self.__dxgi_type

    @property
    def bin_directory(self) -> Path:
        return self.root / ("bin64" if "64" in self.__exe else "bin")

    def load_config(self) -> bool:

        ok = False

        with open(self.config_path) as handler:

            gw2_config_xml = BeautifulSoup(handler, features="xml")
            gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

            self.__root = Path(gw2_app_token.find("INSTALLPATH")['Value'])
            self.__exe = gw2_app_token.find("EXECUTABLE")['Value']

            # gw2_app_game_settings = gw2_config_xml.find("GSA_SDK").find('GAMESETTINGS')
            # # Check game render
            # gw2_app_dx11_game_render = gw2_app_game_settings.find("OPTION").find_all(Name="dx11 render")
            # is_dx11_render = gw2_app_dx11_game_render is not None

            ok = True

        return ok

    def load_settings(self) -> bool:
        ok : bool = False

        if self.settings_path.exists():
            with open(self.settings_path) as _:

                settings = json.load(_)

                [self.args, self.bases, self.bindings] = objectify_json_settings(self.root, settings)

                if ("/dx11" in self.args) or ("-dx11" in self.args):
                    self.__dxgi_type = BindingType.DXGI_11

                ok = True
                    
        return ok