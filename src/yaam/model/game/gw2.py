'''
Guild Wars 2 model class
'''
import json
from collections import defaultdict

from pathlib import Path
from typing import Callable, Any, Dict, List, Tuple
from bs4 import BeautifulSoup

from yaam.model.game.config import IGameConfiguration
from yaam.model.game.game import Game, IGameIncarnator
from yaam.model.game.settings import IYaamGameSettings
from yaam.utils.exceptions import ConfigLoadException

from yaam.utils.logger import static_logger as logger
from yaam.model.binding_type import BindingType
from yaam.model.mutable.addon import MutableAddon
from yaam.model.mutable.addon_base import MutableAddonBase
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.argument import MutableArgument, ArgumentIncarnation
from yaam.model.game.abstract_config import AbstractGameConfiguration
from yaam.model.game.stub import YaamGameSettingsStub
from yaam.model.context import ApplicationContext, GameContext
from yaam.utils.normalize import normalize_abs_path


#############################################################################################
#############################################################################################

class GW2Config(AbstractGameConfiguration):
    '''
    Guild Wars 2 model class
    '''

    def __init__(self, appdata_dir: Path):

        super().__init__(appdata_dir, BindingType.DXGI_9)

        self._name = "Guild Wars 2"
        self._config_path = self._appdata_dir / self._name / "GFXSettings.Gw2-64.exe.xml"
        self._root = Path("C:\\Program Files\\Guild Wars 2")
        self._exe = "Gw2-64.exe"

    @property
    def bin_directory(self) -> Path:
        return self.game_root / ("bin64" if "64" in self._exe else "bin")

    def load(self) -> bool:

        load_ok = False

        logger().info(msg = f"Reading root path from {self.path}.", )

        with open(self.path, encoding="utf-8") as _:

            gw2_config_xml = BeautifulSoup(_, features="xml")
            gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

            self._root = Path(gw2_app_token.find("INSTALLPATH")['Value'])
            self._exe = gw2_app_token.find("EXECUTABLE")['Value']

            logger().info(msg=f"GW2 location is {self.path}.")

            if not self.path.exists():
                logger().info(msg=f"Location {self.path} doesn't exists!")
            else:
                load_ok = True

        return load_ok

#############################################################################################
#############################################################################################

class YaamGW2Settings(YaamGameSettingsStub):
    '''
    Guild Wars 2 Yaam settings model class
    '''

    def __init__(self, context: GameContext, default_binding: BindingType = BindingType.AGNOSTIC):

        super().__init__(context.yaam_game_dir / "settings.json", default_binding)

        self._context = context

    def add_base(self, base: MutableAddonBase):
        '''
        Add a new addon base
        '''
        if base.name not in self._bases:
            self._bases[base.name] = base

    def add_binding(self, binding: MutableBinding):
        '''
        Add a new addon binding
        '''
        if (binding.typing not in self.bindings) or (binding.name not in self.binding[binding.typing]):
            self.bindings[binding.typing] = binding

    def add_chain(self, chain: List[str]):
        '''
        Add a new chainload sequence
        '''
        self._chains.append(chain)

    def load(self) -> bool:

        load_ok : bool = False

        self._load_props(self._context.args_path, {
            "arguments": (MutableArgument.from_dict, self.add_argument)
        })
        
        self._load_props(self._context.addons_path, {
            "addons": (MutableAddonBase.from_dict, self.add_base)
        })

        self._load_props(self._context.bindings_path, {
            "bindings": (self._load_bindings, lambda x : None)
        })

        self._load_props(self._context.chains_path, {
            "chains": (lambda x : x, self.add_base)
        })
        
        logger().info(msg=f"Loaded {len(self.arguments)} arguments...")
        logger().info(msg=f"Loaded {len(self.addons)} addons...")
        logger().info(msg=f"Loaded {len(self.bindings)} bindings...")
        logger().info(msg=f"Loaded {len(self.chains)} chainload sequences...")
        
        if self.path.exists():
            
            # to do... Load current settings
            with open(self.path, encoding="utf-8", mode='r') as _:

                settings = json.load(_)

                # self.__objectify_json_settings(settings)

                if "dx11" in self._args:
                    self._binding_type = BindingType.DXGI_11

                load_ok = True

        return load_ok and self._incarnate_addons()

    def _load_props(self, path:Path, mappers: Dict[str, Tuple[Callable[[Any], Any], Callable[[Any], None]]]):
        '''
        Load and fill specified prop
        '''
        if path.exists():
            with open(path, encoding="utf-8", mode='r') as _:
                json_obj = json.load(_)
                for (key, (mapper, filler)) in mappers:
                    if key in json_obj:
                        for obj in json_obj[key]:
                            filler(mapper(obj))

    def _load_bindings(self, json_obj: dict):
        for (key, value) in json_obj.items():

            binding_type = BindingType.from_string(key)

            if binding_type not in self._bindings:
                self._bindings[binding_type] = dict()

            for obj in value:
                # remove slashes and make absolute
                if 'path' in obj:
                    obj['path'] = normalize_abs_path(obj['path'], self._context.game_root)

                if binding_type == BindingType.SHADER:
                    # To Do...
                    pass

                binding = MutableBinding.from_dict(obj, binding_type)
                self._bindings[binding_type][binding.name] = binding

    def __objectify_json_settings(self, json_obj: dict) -> None:

        self._args.clear()
        self._bindings.clear()

        if "arguments" in json_obj:
            for obj in json_obj['arguments']:
                arginc = ArgumentIncarnation.from_string(obj)
                if self.has_argument(arginc.name):
                    arg = self.argument(arginc.name)
                    arg.value = arginc.value
                    arg.enabled = True

        if "addons" in json_obj:
            for obj in json_obj['addons']:
                base = MutableAddonBase.from_dict(obj)
                self.add_base(base)

        if "bindings" in json_obj:
            for (key, value) in json_obj['bindings'].items():
                binding_type = BindingType.from_string(key)

                if binding_type not in self._bindings:
                    self._bindings[binding_type] = dict()

                for obj in value:
                    # remove slashes and make absolute
                    if binding_type != BindingType.EXE and 'path' in obj:
                        while obj['path'].startswith("../") or obj['path'].startswith("..\\"):
                            obj['path'] = obj['path'][3:]

                        while obj['path'].startswith("."):
                            obj['path'] = obj['path'][1:]

                        if obj['path'].startswith("\\") or obj['path'].startswith("/"):
                            obj['path'] = obj['path'][1:]

                        obj['path'] = self._context.game_root / Path(obj['path'])
                    
                    if binding_type == BindingType.SHADER:
                        # To Do...
                        pass

                    binding = MutableBinding.from_dict(obj, binding_type)
                    self._bindings[binding_type][binding.name] = binding

    def _incarnate_addons(self) -> bool:

        '''
        Creates addons incarnations from bases and bindings
        '''
        binding_lut = defaultdict(default_factory=lambda:False)
        binding_lut[BindingType.SHADER] = True
        binding_lut[BindingType.EXE] = True
        binding_lut[BindingType.AGNOSTIC] = True
        binding_lut[self.binding] = True

        # build addons incarnations by binding
        for binding_type in BindingType:
            if binding_type in self._bindings:
                for (addon_name, binding) in self._bindings[binding_type].items():

                    addon_base = self.bases[addon_name]
                    if addon_base is None:
                        addon_base = MutableAddonBase(addon_name)

                    addon = MutableAddon(addon_base, binding)

                    if binding_type not in binding_lut or binding_lut[binding_type] is False:
                        addon.is_enabled = False
                    elif binding_type is BindingType.SHADER and binding_lut[binding_type] is True:
                        binding_lut[binding_type] = False # Only one shader

                    self.add_addon(addon)

        return len(self._addons)


    def save(self) -> bool:
        # To Do
        return False

#############################################################################################
#############################################################################################

class GuildWars2(Game, IGameIncarnator):
    '''
    Guild Wars 2 model class incarnator
    '''
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettings) -> None:
        Game.__init__(self, config, settings)

    @staticmethod
    def incarnate(app_context: ApplicationContext = None) -> Game:
        gw2_config = GW2Config(app_context)

        if not gw2_config.load():
            raise ConfigLoadException(gw2_config.path)

        game_context = app_context.create_game_environment(gw2_config.name, gw2_config.game_root)

        yaam_gw2_settings = YaamGW2Settings(game_context, gw2_config.native_binding)
        yaam_gw2_settings.load()

        return GuildWars2(gw2_config, yaam_gw2_settings)
