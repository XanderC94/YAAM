'''
Guild Wars 2 model class
'''

import json

from pathlib import Path
from typing import Callable, Any, Dict, List, Tuple
from bs4 import BeautifulSoup

from yaam.utils.exceptions import ConfigLoadException
from yaam.utils.normalize import normalize_abs_path
from yaam.utils.logger import static_logger as logger

from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.incarnator import IGameIncarnator
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.game.base import Game
from yaam.model.immutable.argument import ArgumentSynthesis

from yaam.model.type.binding import BindingType
from yaam.model.mutable.addon import Addon
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.binding import Binding
from yaam.model.mutable.argument import Argument
from yaam.model.game.abstract.config import AbstractGameConfiguration
from yaam.model.game.stub.settings import YaamGameSettings
from yaam.model.context import AppContext, GameContext

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

        super().__init__(appdata_dir, BindingType.D3D9)

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

    def add_base(self, base: AddonBase):
        '''
        Add a new addon base
        '''
        if base.name not in self._bases:
            self._bases[base.name] = base

    def add_binding(self, binding: Binding):
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
        # Load arguments
        self.__load_list_props(self._context.args_path, {
            "arguments": (Argument.from_dict, self.add_argument)
        })
        # Load Argument enabled-disabled settings
        self.__load_list_props(self._settings_path, {
            "arguments": (ArgumentSynthesis.from_dict, self.__update_arguments)
        })

        if self.has_argument("dx11") and self.argument("dx11").enabled:
            self._binding_type = BindingType.D3D11
        elif self.has_argument("dx12") and self.argument("dx12").enabled:
            self._binding_type = BindingType.D3D12
            
        # Load Addon bases
        self.__load_list_props(self._context.addons_path, {
            "addons": (AddonBase.from_dict, self.add_base)
        })
        # Load Addons bindings
        self.__load_dict_props(self._context.bindings_path, {
            "bindings": (self.__load_bindings, lambda x: None)
        })
        # Load Addons bindings enabled-disabled settings
        self.__load_dict_props(self._settings_path, {
            "bindings": (self.__update_bindings, lambda x: None)
        })
        # Load chainloading sequences
        self.__load_list_props(self._context.chains_path, {
            "chains": (lambda x: x, self.add_chain)
        })
        
        logger().info(msg=f"Chosen bindings {self._binding_type.name}.")
        logger().info(msg=f"Loaded {len(self._args)} arguments...")
        logger().info(msg=f"Loaded {len(self._bases)} bases...")
        logger().info(msg=f"Loaded {sum([ len(_) for _ in self._bindings.values() ])} bindings...")
        logger().info(msg=f"Loaded {len(self._chains)} chainload sequences...")

        return self.__incarnate_addons()

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
                has_custom_path = 'path' in obj
                obj['path'] = normalize_abs_path(obj.get('path', ''), self._context.game_root)
                binding = Binding.from_dict(obj, binding_type)

                # if the binding is a shader and the default name will be replaced with that
                # specified with its current binding type
                # in case of an agnostic binding, the current binding type of the game is used
                if (binding_type.can_shader() or binding_type == BindingType.AGNOSTIC) and not has_custom_path:
                    if binding.name in self._bases and self._bases[binding.name].is_shader():
                        shader_name = binding_type.shader if binding_type.can_shader() else self._binding_type.shader
                        shader_suffix = binding_type.suffix if binding_type.can_shader() else self._binding_type.suffix
                        binding.path = binding.path / f"{shader_name}{shader_suffix}"

                self.add_binding(binding)

    def __update_bindings(self, json_obj: dict):
        for (key, value) in json_obj.items():
            binding_type = BindingType.from_string(key)
            for _ in value:
                binding_setup = Binding.from_dict(_, binding_type)
                if binding_type in self._bindings and binding_setup.name in self._bindings[binding_type]:
                    binding = self._bindings[binding_type][binding_setup.name]
                    binding.enabled = binding_setup.enabled
                    binding.updateable = binding_setup.updateable
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
                        addon_base = AddonBase(addon_name)
                        self.add_base(addon_base) # add placeholder

                    addon = Addon(addon_base, binding)

                    self.add_addon(addon)

        # create binding dangling bases
        for (addon_name, base) in self._bases.items():
            if addon_name not in self._addons:
                binding = Binding(addon_name)
                self.add_binding(binding) # add placeholder
                addon = Addon(base, binding)
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
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettings, game_context: GameContext) -> None:
        Game.__init__(self, config, settings, game_context)

    @staticmethod
    def incarnate(app_context: AppContext = None) -> Game:
        gw2_config = GW2Config(app_context.appdata_dir)

        if not gw2_config.load():
            raise ConfigLoadException(gw2_config.path)

        game_context = app_context.create_game_environment(gw2_config.name, gw2_config.game_root)

        yaam_gw2_settings = YaamGW2Settings(game_context, gw2_config.native_binding)
        yaam_gw2_settings.load()

        return GuildWars2(gw2_config, yaam_gw2_settings, game_context)
