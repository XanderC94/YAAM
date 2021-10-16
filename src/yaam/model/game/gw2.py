'''
Guild Wars 2 model class
'''

import json

from pathlib import Path
from typing import Callable, Any, Dict, List, Tuple
from bs4 import BeautifulSoup

from yaam.model.game.config import IGameConfiguration
from yaam.model.game.game import Game, IGameIncarnator
from yaam.model.game.settings import IYaamGameSettings
from yaam.model.immutable.argument import ArgumentSynthesis
from yaam.model.immutable.binding import Binding
from yaam.utils.exceptions import ConfigLoadException

from yaam.utils.logger import static_logger as logger
from yaam.model.binding_type import BindingType
from yaam.model.mutable.addon import MutableAddon
from yaam.model.mutable.addon_base import MutableAddonBase
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.argument import MutableArgument
from yaam.model.game.abstract_config import AbstractGameConfiguration
from yaam.model.game.yaam_settings import YaamGameSettings
from yaam.model.context import ApplicationContext, GameContext
from yaam.utils.normalize import normalize_abs_path

Mapper = Callable[[Any], Any]
Consumer = Callable[[Any], None]
SwissKnife = Dict[str, Tuple[Mapper, Consumer]]

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

class YaamGW2Settings(YaamGameSettings):
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
        if (binding.typing not in self._bindings) or (binding.name not in self._bindings[binding.typing]):
            self._bindings[binding.typing][binding.name] = binding

    def add_chain(self, chain: List[str]):
        '''
        Add a new chainload sequence
        '''
        self._chains.append(chain)

    def load(self) -> bool:

        self.__load_list_props(self._context.args_path, {
            "arguments": (MutableArgument.from_dict, self.add_argument)
        })

        self.__load_list_props(self._context.addons_path, {
            "addons": (MutableAddonBase.from_dict, self.add_base)
        })

        self.__load_list_props(self._context.chains_path, {
            "chains": (lambda x: x, self.add_chain)
        })

        self.__load_dict_props(self._context.bindings_path, {
            "bindings": (self.__load_bindings, lambda x: None)
        })

        logger().info(msg=f"Loaded {len(self._args)} arguments...")
        logger().info(msg=f"Loaded {len(self._bases)} bases...")
        logger().info(msg=f"Loaded {sum([ len(_) for _ in self._bindings.values() ])} bindings...")
        logger().info(msg=f"Loaded {len(self._chains)} chainload sequences...")


        status = self.__incarnate_addons()

        # load enabled-disabled settings
        self.__load_list_props(self._settings_path, {
            "arguments": (ArgumentSynthesis.from_string, self.__update_arguments)
        })
        
        self.__load_dict_props(self._settings_path, {
            "bindings": (self.__update_bindings, lambda x: None)
        })

        if self.has_argument("dx11") and self.argument("dx11").enabled:
            self._binding_type = BindingType.DXGI_11
        elif self.has_argument("dx12") and self.argument("dx12").enabled:
            self._binding_type = BindingType.DXGI_12

        logger().info(msg=f"Chosen bindings {self._binding_type.name}.")

        return status

    def __load_list_props(self, path:Path, mappers: SwissKnife):
        '''
        Load and fill specified list props
        '''
        if path.exists():
            with open(path, encoding="utf-8", mode='r') as _:
                json_obj = json.load(_)
                for (key, (mapper, consumer)) in mappers.items():
                    if key in json_obj:
                        for obj in json_obj[key]:
                            consumer(mapper(obj))

    def __load_dict_props(self, path: Path, mappers: SwissKnife):
        '''
        Load and fill specified dict props
        '''
        if path.exists():
            with open(path, encoding="utf-8", mode='r') as _:
                json_obj = json.load(_)
                for (key, (mapper, consumer)) in mappers.items():
                    if key in json_obj:
                        consumer(mapper(json_obj[key]))

    def __load_bindings(self, json_obj: dict):
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
                self.add_binding(binding)

    def __update_bindings(self, json_obj: dict):
        for (key, value) in json_obj.items():
            binding_type = BindingType.from_string(key)
            for _ in value:
                b = Binding.from_dict(_, binding_type)
                if binding_type in self._bindings and b.name in self._bindings[binding_type]:
                    binding = self._bindings[binding_type][b.name]
                    binding.enabled = b.enabled
                    binding.updateable = b.updateable
                    # binding.path = b.path


    def __update_arguments(self, synth: ArgumentSynthesis):
        if self.has_argument(synth.name):
            arg = self.argument(synth.name)
            arg.value = synth.value
            arg.enabled = True

    def __incarnate_addons(self) -> bool:
        '''
        Creates addons incarnations from bases and bindings
        '''
        # build addons incarnations by binding
        for binding_type in BindingType:
            if binding_type in self._bindings:
                for (addon_name, binding) in self._bindings[binding_type].items():

                    addon_base = self._bases.get(addon_name, None)

                    if addon_base is None:
                        # create base for dangling binding
                        addon_base = MutableAddonBase(addon_name)
                        self.add_base(addon_base) # add placeholder

                    addon = MutableAddon(addon_base, binding)

                    self.add_addon(addon)

        # create binding dangling bases
        for (addon_name, base) in self._bases.items():
            if addon_name not in self._addons:
                binding = Binding(addon_name)
                self.add_binding(binding) # add placeholder
                addon = MutableAddon(base, binding)
                self.add_addon(addon)

        logger().info(msg=f"Incarnated {len(self._addons)} addons...")

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
        gw2_config = GW2Config(app_context.appdata_dir)

        if not gw2_config.load():
            raise ConfigLoadException(gw2_config.path)

        game_context = app_context.create_game_environment(gw2_config.name, gw2_config.game_root)

        yaam_gw2_settings = YaamGW2Settings(game_context, gw2_config.native_binding)
        yaam_gw2_settings.load()

        return GuildWars2(gw2_config, yaam_gw2_settings)
