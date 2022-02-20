'''
Abstract Game Incarnation model class
'''
import pickle
import shutil
from typing import List

from yaam.model.appcontext import GameContext
from yaam.model.game.abstract.settings import AbstractYaamGameSettings
from yaam.model.immutable.argument import ArgumentSynthesis
from yaam.model.mutable.addon import Addon, IAddon
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.argument import Argument
from yaam.model.mutable.binding import Binding
from yaam.model.type.binding import BindingType
from yaam.utils.hashing import Hasher
from yaam.utils.json.io import consume_json_entries, read_json, write_json
from yaam.utils.json.repr import jsonrepr
from yaam.utils.logger import static_logger as logger
from yaam.utils.normalize import normalize_abs_path


class YaamGameSettings(AbstractYaamGameSettings[
            AddonBase, Binding, Argument
        ]):
    '''
    Yaam Game Settings model class stub
    '''

    def __init__(self, context: GameContext, default_binding: BindingType = BindingType.AGNOSTIC):

        super().__init__(context.yaam_game_dir, default_binding)

        self._context = context

    def add_addon_base(self, base: AddonBase) -> bool:
        ret = False
        if base.name not in self._bases:
            self._bases[base.name] = base
            ret = True

        return ret

    def add_addon_binding(self, binding: Binding) -> bool:
        ret = False
        if binding.typing not in self._bindings or binding.name not in self._bindings[binding.typing]:
            self._bindings[binding.typing][binding.name] = binding
            ret = True

        return ret

    def load(self) -> bool:
        # Load arguments
        consume_json_entries(
            read_json(self._context.args_path), {"arguments": self._load_arguments}
        )

        # Load Addon bases
        consume_json_entries(
            read_json(self._context.addons_path), {"addons": self._load_addon_bases}
        )

        # Load Argument enabled-disabled settings
        settings_json_obj = read_json(self._context.settings_path)

        consume_json_entries(
            settings_json_obj, {"arguments": self._incarnate_arguments}
        )

        # need to know the current binding type to correctly load the addons bindings
        if self.has_argument("dx9") and self.argument("dx9").enabled:
            self._binding_type = BindingType.D3D9
        elif self.has_argument("dx10") and self.argument("dx10").enabled:
            self._binding_type = BindingType.D3D10
        elif self.has_argument("dx11") and self.argument("dx11").enabled:
            self._binding_type = BindingType.D3D11
        elif self.has_argument("dx12") and self.argument("dx12").enabled:
            self._binding_type = BindingType.D3D12
        elif self.has_argument("vulkan") and self.argument("vulkan").enabled:
            self._binding_type = BindingType.VULKAN

        # Load Addons bindings
        consume_json_entries(
            settings_json_obj, {"bindings": self._load_bindings}
        )

        # read naming map
        naming_map_obj = read_json(self._context.naming_map_path)
        consume_json_entries(
            naming_map_obj, {"namings": self._load_namings}
        )

        logger().info(msg=f"Chosen bindings {self._binding_type.name}.")
        logger().info(msg=f"Loaded {len(self._args)} arguments...")
        logger().info(msg=f"Loaded {len(self._bases)} bases...")
        logger().info(msg=f"Loaded {sum([ len(_) for _ in self._bindings.values() ])} bindings...")

        n_dangling_bases = self._resolve_dangling_bases()

        logger().info(msg=f"Resolved {n_dangling_bases} danglings addon bases...")

        return len(self._bases) > 0

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

    def synthetize(self) -> List[IAddon[AddonBase, Binding]]:
        '''
        Creates addons incarnations from bases and bindings
        '''
        addons: List[IAddon[AddonBase, Binding]] = list()

        # build addons incarnations by binding
        for binding_type in BindingType:
            if binding_type in self._bindings:
                for (addon_name, binding) in self._bindings[binding_type].items():

                    addon_base = self._bases.get(addon_name, None)
                    naming_rules = self._naming_map.get(binding_type, dict()).get(addon_name, dict())

                    if addon_base is not None:
                        addon = Addon(addon_base, binding, naming_rules)
                        addons.append(addon)

        logger().info(msg=f"Incarnated {len(addons)} addons...")

        return addons

    def digest(self) -> str:
        '''
        Return a unique digest representation of the object state
        '''
        hasher = Hasher.SHA512.create()

        hasher.update(self._binding_type.name.encode(encoding='utf-8'))

        for _ in self._args.values():
            hasher.update(pickle.dumps([_.meta.name, _.value, _.enabled]))

        for _ in self._bases.values():
            hasher.update(pickle.dumps([
                _.name, _.uri, _.dependencies
            ]))

        for bindings in self._bindings.values():
            for binding in bindings.values():
                hasher.update(pickle.dumps([
                    str(binding.path), binding.typing, binding.is_enabled, binding.is_updateable
                ]))

        return hasher.hexdigest()

    def _load_arguments(self, json_obj: list):
        for _ in json_obj:
            self.add_argument(Argument.from_json(_))

    def _update_argument(self, synth: ArgumentSynthesis):
        if self.has_argument(synth.name):
            arg = self.argument(synth.name)
            arg.value = arg.meta.typing.reify(synth.value)
            arg.enabled = True

    def _incarnate_arguments(self, json_obj: list):
        for _ in json_obj:
            self._update_argument(ArgumentSynthesis.from_json(_))

    def _load_addon_bases(self, json_obj: list):
        for _ in json_obj:
            self.add_addon_base(AddonBase.from_json(_))

    def _load_namings(self, json_obj: list):
        for (key, namings) in json_obj.items():
            binding_type = BindingType.from_string(key)
            if binding_type not in self._naming_map:
                self._naming_map[binding_type] = dict()

            for _ in namings:
                self._naming_map[binding_type][_["addon"]] = _["naming"]

    def _load_bindings(self, json_obj: dict):
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

    def _resolve_dangling_bases(self):
        n_dangling_bases = 0
        # build addons incarnations by binding
        for bindings in self._bindings.values():
            for addon_name in bindings:
                if not self.has_addon_base(addon_name):
                    # create base for dangling binding
                    addon_base = AddonBase(addon_name)
                    self.add_addon_base(addon_base)  # add placeholder
                    n_dangling_bases += 1

        return n_dangling_bases
