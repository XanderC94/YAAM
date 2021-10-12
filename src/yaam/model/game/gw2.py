'''
Guild Wars 2 model class
'''
from collections import defaultdict
import json

import os

from pathlib import Path
from bs4 import BeautifulSoup

from yaam.utils.logger import static_logger as logger
from yaam.model.binding_type import BindingType
from yaam.model.mutable.addon import MutableAddonBase, MutableAddon, MutableBinding
from yaam.model.immutable.argument import Argument, ArgumentIncarnation
from yaam.model.game.abstract import AbstractGame
from yaam.model.incarnator import Incarnator
from yaam.model.game.incarnation import AbstractGameIncarnation

#############################################################################################
#############################################################################################

class GuildWars2(AbstractGame):
    '''
    Guild Wars 2 model class
    '''

    def __init__(self, appdata: Path):

        super().__init__(appdata)

        self._config_path = self._app_data / "Guild Wars 2" / "GFXSettings.Gw2-64.exe.xml"
        self._root = Path("C:\\Program Files\\Guild Wars 2")
        self._exe = "Gw2-64.exe"

    @property
    def bin_directory(self) -> Path:
        return self.root / ("bin64" if "64" in self._exe else "bin")

    def load(self) -> bool:

        load_ok = False

        logger().info(msg = f"Reading root path from {self.config_path}.", )

        with open(self.config_path, encoding="utf-8") as _:

            gw2_config_xml = BeautifulSoup(_, features="xml")
            gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

            self._root = Path(gw2_app_token.find("INSTALLPATH")['Value'])
            self._exe = gw2_app_token.find("EXECUTABLE")['Value']

            logger().info(msg=f"GW2 location is {self.path}.")

            if not self.path.exists():
                logger().info(msg=f"Location {self.path} doesn't exists!")
            else:
                load_ok = True

        if load_ok:
            # Load all addons with default bindings
            working_dir = Path(os.getcwd())
            defaults_path = working_dir / "res/default"
            arguments_metedata_path = defaults_path / "arguments.json"
            addons_metedata_path = defaults_path / "addons.json"

            if arguments_metedata_path.exists():
                with open(arguments_metedata_path, encoding="utf-8") as _:
                    json_obj = json.load(_)
                    if "arguments" in json_obj:
                        for obj in json_obj["arguments"]:
                            argument = Argument.from_dict(obj)
                            self.add_argument(argument)

                if len(self.arguments) > 0:
                    logger().info(msg="Default Arguments loaded...")

            if addons_metedata_path.exists():
                with open(addons_metedata_path, encoding="utf-8") as _:
                    json_obj = json.load(_)
                    if "addons" in json_obj:
                        for obj in json_obj["addons"]:
                            base = MutableAddonBase.from_dict(obj)
                            self.add_addon(base)

                if len(self.addons) > 0:
                    logger().info(msg="Default Addons loaded...")

        return load_ok

#############################################################################################
#############################################################################################

class GuildWars2Incarnation(AbstractGameIncarnation):
    '''
    Guild Wars 2 Incarnation model class
    '''

    def __init__(self, game: GuildWars2):

        super().__init__(game)

        self._config_path = self.game.config_path.parent / "Settings.json"

    def load(self) -> bool:

        load_ok : bool = False

        if self.config_path.exists():

            with open(self.config_path, encoding="utf-8") as _:

                settings = json.load(_)

                self.__objectify_json_settings(settings)

                if "dx11" in self._args:
                    self._binding_type = BindingType.DXGI_11

                load_ok = True

        return load_ok and self._incarnate_addons()

    def __objectify_json_settings(self, json_obj: dict) -> None:

        self._args.clear()
        self._bindings.clear()

        if "arguments" in json_obj:
            for obj in json_obj['arguments']:
                arginc = ArgumentIncarnation.from_string(obj)
                self.add_argument(arginc)

        if "addons" in json_obj:
            for obj in json_obj['addons']:
                base = MutableAddonBase.from_dict(obj)
                self.game.add_addon(base)

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

                        obj['path'] = self.root / Path(obj['path'])
                    
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

                    addon_base = self.game.addon(addon_name)
                    if addon_base is None:
                        addon_base = MutableAddonBase(addon_name)

                    addon = MutableAddon(addon_base, binding)

                    if binding_type not in binding_lut or binding_lut[binding_type] is False:
                        addon.is_enabled = False
                    elif binding_type is BindingType.SHADER and binding_lut[binding_type] is True:
                        binding_lut[binding_type] = False # Only one shader

                    self.add_addon(addon)

        for base in self.game.addons:
            if not self.has_addon(base.name):
                self.add_addon(MutableAddon(base, MutableBinding(base.name)))

        return len(self._addons)

#############################################################################################
#############################################################################################

class GuildWars2Incarnator(Incarnator[Path, GuildWars2Incarnation]):
    '''
    Guild Wars 2 model class incarnator
    '''
    def incarnate(self, decoration: Path = None) -> GuildWars2Incarnation:
        gw2inc = None
        with GuildWars2(decoration) as gw2meta:
            gw2inc = GuildWars2Incarnation(gw2meta)
            gw2inc.load()
        return gw2inc
