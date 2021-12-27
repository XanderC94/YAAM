'''
Guild Wars 2 model class
'''

import shutil

from pathlib import Path
from bs4 import BeautifulSoup

from yaam.utils.exceptions import ConfigLoadException
from yaam.utils.normalize import normalize_abs_path
from yaam.utils.logger import static_logger as logger
from yaam.utils.json.repr import jsonrepr
from yaam.utils.json.io import read_json, write_json, consume_json_entries

from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.incarnator import IGameIncarnator
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.game.base import Game
from yaam.model.immutable.argument import ArgumentSynthesis

from yaam.model.type.binding import BindingType
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.binding import Binding
from yaam.model.mutable.argument import Argument
from yaam.model.game.abstract.config import AbstractGameConfiguration
from yaam.model.game.stub.settings import YaamGameSettings
from yaam.model.context import AppContext, GameContext

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

        logger().info(msg = f"Reading game path from {self.path}.", )

        if self.path.exists():
            with open(self.path, encoding="utf-8") as _:

                gw2_config_xml = BeautifulSoup(_, features="xml")
                gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

                self._root = Path(gw2_app_token.find("INSTALLPATH")['Value'])
                self._exe = gw2_app_token.find("EXECUTABLE")['Value']

                if self._root.exists():
                    logger().info(msg=f"GW2 location is {self._root}.")
                    load_ok = True
                else:
                    logger().info(msg=f"{self._root} doesn't exists!")
        else:
            logger().info(msg=f"{self.path} doesn't exists!")

        return load_ok

#############################################################################################
#############################################################################################

class YaamGW2Settings(YaamGameSettings):
    '''
    Guild Wars 2 Yaam settings model class
    '''

    def __init__(self, context: GameContext, default_binding: BindingType = BindingType.AGNOSTIC):

        super().__init__(context.yaam_game_dir, default_binding)

        self._context = context

    def load(self) -> bool:
        # Load arguments
        consume_json_entries(
            read_json(self._context.args_path), { "arguments": self.__load_arguments }
        )

        # Load Addon bases
        consume_json_entries(
            read_json(self._context.addons_path), { "addons": self.__load_addon_bases }
        )

        # Load Argument enabled-disabled settings
        settings_json_obj = read_json(self._context.settings_path)

        consume_json_entries(
            settings_json_obj, { "arguments": self.__incarnate_arguments }
        )

        # need to know the current binding type to correctly load the addons bindings
        if self.has_argument("dx11") and self.argument("dx11").enabled:
            self._binding_type = BindingType.D3D11
        elif self.has_argument("dx12") and self.argument("dx12").enabled:
            self._binding_type = BindingType.D3D12

        # Load Addons bindings
        consume_json_entries(
            settings_json_obj, { "bindings": self.__load_bindings }
        )

        # read naming map
        naming_map_obj = read_json(self._context.naming_map_path)
        consume_json_entries(
            naming_map_obj, { "namings": self.__load_namings }
        )

        logger().info(msg=f"Chosen bindings {self._binding_type.name}.")
        logger().info(msg=f"Loaded {len(self._args)} arguments...")
        logger().info(msg=f"Loaded {len(self._bases)} bases...")
        logger().info(msg=f"Loaded {sum([ len(_) for _ in self._bindings.values() ])} bindings...")

        n_dangling_bases = self.__resolve_dangling_bases()

        logger().info(msg=f"Resolved {n_dangling_bases} danglings addon bases...")

        return len(self._bases) > 0

    def __load_arguments(self, json_obj: list):
        for _ in json_obj:
            self.add_argument(Argument.from_json(_))

    def __update_argument(self, synth: ArgumentSynthesis):
        if self.has_argument(synth.name):
            arg = self.argument(synth.name)
            arg.value = arg.meta.typing.reify(synth.value)
            arg.enabled = True

    def __incarnate_arguments(self, json_obj: list):
        for _ in json_obj:
            self.__update_argument(ArgumentSynthesis.from_json(_))

    def __load_addon_bases(self, json_obj: list):
        for _ in json_obj:
            self.add_addon_base(AddonBase.from_json(_))

    def __load_namings(self, json_obj: list):
        for _ in json_obj:
            self._naming_map[_["addon"]] = _["naming"]

    def __load_bindings(self, json_obj: dict):
        for (key, value) in json_obj.items():
            binding_type = BindingType.from_string(key)

            if binding_type not in self._bindings:
                self._bindings[binding_type] = dict()

            for obj in value:
                # remove slashes and make absolute
                has_custom_path = 'path' in obj
                obj['path'] = normalize_abs_path(obj.get('path', ''), self._context.game_root)
                binding = Binding.from_json(obj)
                binding.typing = binding_type

                # if the binding is a shader and the default name will be replaced with that
                # specified with its current binding type
                # in case of an agnostic binding, the current binding type of the game is used
                if (binding_type.can_shader() or binding_type == BindingType.AGNOSTIC) and not has_custom_path:
                    if binding.name in self._bases and self._bases[binding.name].is_shader:
                        shader_name = binding_type.shader if binding_type.can_shader() else self._binding_type.shader
                        shader_suffix = binding_type.suffix if binding_type.can_shader() else self._binding_type.suffix
                        binding.path = binding.path / f"{shader_name}{shader_suffix}"

                self.add_addon_binding(binding)

    def __resolve_dangling_bases(self):
        n_dangling_bases = 0
        # build addons incarnations by binding
        for binding_type in self._bindings:
            for addon_name in self._bindings[binding_type]:
                if not self.has_addon_base(addon_name):
                    # create base for dangling binding
                    addon_base = AddonBase(addon_name)
                    self.add_addon_base(addon_base) # add placeholder
                    n_dangling_bases += 1

        return n_dangling_bases

    def save(self) -> bool:
        '''
        Save game settings to file
        '''

        # first, back-up
        shutil.copyfile(self._context.addons_path, f"{self._context.addons_path}.bak")
        shutil.copyfile(self._context.settings_path, f"{self._context.settings_path}.bak")

        # save new data
        json_addons_obj = {
            'addons': jsonrepr(self._bases.values())
        }

        json_bindings_obj = {
            'arguments': list(
                arg.to_json() for arg in self._args.values() if arg.enabled
            ),
            'bindings': dict(
                (binding_type.name.lower(), jsonrepr(bindings.values()))
                for (binding_type, bindings) in self._bindings.items()
            )
        }

        write_json(json_addons_obj, self._context.addons_path)
        write_json(json_bindings_obj, self._context.settings_path)

        return True

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
