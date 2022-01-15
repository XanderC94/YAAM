'''
Addon enable-disable management module
'''

import os

from pathlib import Path
from typing import Iterable
from yaam.controller.metadata import MetadataCollector
from yaam.model.type.binding import BindingType
import yaam.utils.metadata as meta
from yaam.model.mutable.addon import Addon
from yaam.utils.logger import static_logger as logger

class AddonManager(object):
    '''
    Addon management class
    '''

    def __init__(self, metadata: MetadataCollector, binding_type: BindingType) -> None:
        self.__metadata = metadata
        self.__binding_type = binding_type

    def resolve_renames(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
        '''
        Detect and resolve renamed addons by aligning physical names to pointed ones
        '''

        def check_and_rename(addon : Addon, prev_rule: str, new_rule : str) -> None:
            ret : bool = False
            if prev_rule is not None and new_rule is not None and prev_rule != new_rule:
                logger().info(msg=f"Detected a name change in {addon.base.name}: {prev_rule} is now {new_rule}")
                prev_target = addon.binding.workspace / prev_rule
                new_target = addon.binding.workspace / new_rule
                if prev_target.exists():
                    prev_target.rename(new_target)
                ret = True
            return ret

        for addon in addons:
            metadata = self.__metadata.get_local_metadata(addon)
            binding_namings = metadata.namings.get(addon.binding.typing, dict())

            modified: bool = False
            if len(binding_namings) > 0:
                if len(addon.naming) > 0:
                    for (key, new_rule) in addon.naming.items():
                        prev_rule = binding_namings.get(key, None)
                        if check_and_rename(addon, prev_rule, new_rule):
                            binding_namings[key] = new_rule
                            modified = True

                elif not addon.binding.is_headless:
                    new_rule = addon.binding.default_naming
                    for (key, prev_rule) in binding_namings.items():
                        if new_rule.endswith(Path(prev_rule).suffix):
                            if check_and_rename(addon, prev_rule, new_rule):
                                binding_namings[key] = new_rule
                                modified = True
                                break

            if modified:
                self.__metadata.save_metadata(metadata, metadata.uri)

    def disable_dll_addons(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
        '''
        Overrides the typing of installed addons (.dll -> .dll.disabled)
        @addons : Iterable[Addon] -- The list of addons to be disabled (.dll only, .exe are filtered out)
        '''

        prev_shader: Addon = None
        if prev is not None:
            for addon in prev:
                # There can only be only one shader enabled by design
                # therefore it is sufficient to just find the first enabled shader
                if addon.base.is_shader and addon.binding.is_enabled:
                    prev_shader = addon
                    break

        ret = 0
        for addon in addons:
            if addon.binding.is_dll() and not addon.binding.is_enabled:
                
                metadata = self.__metadata.get_local_metadata(addon)
                
                type_naming_rules = dict()
                if metadata is not None:
                    type_naming_rules = metadata.namings.get(addon.binding.typing, dict())

                naming = []
                if len(type_naming_rules) == 0:
                    if not addon.binding.is_headless:
                        naming.append(addon.binding.default_naming)
                else:
                    naming = list([ _ for _ in type_naming_rules.values() if _.endswith('.dll') ])

                workspace = addon.binding.workspace

                for _ in naming:
                    path = workspace / _

                    can_disable = True
                    path_disabled = Path(f"{path}.disabled")
                    if addon.base.is_shader:
                        # I need to match pointed shader path
                        # but most shaders share the same name
                        # therefore they can't be disabled indiscrimately
                        if self.__match_dll_metainfo(addon) or (
                            # cover for cases where old active shader doesn't have meta informations
                            # since only one shader can be enabled at one time
                            # the only one that can't match for lack of metadata is
                            # the one previously enabled
                            prev_shader is not None and
                            addon.base.name == prev_shader.base.name and
                            addon.binding.typing == prev_shader.binding.typing
                        ):
                            name_ext = addon.base.name.lower().replace(' ', '')
                            path_disabled = Path(f"{path}.{name_ext}")
                        else:
                            can_disable = False
                    
                    if path.exists() and path.is_file() and can_disable:
                        logger().info(msg=f"Addon {addon.base.name}({path.name}) will be suppressed...")
                        os.rename(str(path), str(path_disabled))
                        ret += 1

        return ret

    def restore_dll_addons(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
        '''
        Restore disabled addons.
        @addons : Iterable[Addon] -- The list of addons to be enabled (.dll only, .exe are filtered out)
        '''
        ret = 0
        for addon in addons:
            if addon.binding.is_dll() and addon.binding.is_enabled:

                metadata = self.__metadata.get_local_metadata(addon)

                type_naming_rules = dict()
                if metadata is not None:
                    type_naming_rules = metadata.namings.get(addon.binding.typing, dict())

                namings = []

                if len(type_naming_rules) == 0:
                    if not addon.binding.is_headless:
                        namings.append(addon.binding.default_naming)
                else:
                    namings = list([ _ for _ in type_naming_rules.values() if _.endswith('.dll')])

                workspace = addon.binding.workspace

                for _ in namings:
                    path = workspace / _

                    can_enable = True
                    path_disabled = Path(f"{path}.disabled")
                    if addon.base.is_shader:
                        # Disabled shaders doesn't need meta-information look-up
                        # since their extension is overridden and made unique
                        # and addons name should be unique by design
                        name_ext = addon.base.name.lower().replace(' ', '')
                        path_disabled = Path(f"{path}.{name_ext}")
                        # NOTE: At most, metainfo might be checked on the overridden file
                        # to assert if is another shader with the wrong extension
                        # but it supposed to not be possible
                        # can_enable = match_dll_metainfo(addon, path_disabled)

                    if path_disabled.exists() and can_enable:
                        logger().info(msg=f"Addon {addon.base.name}({path.name}) will be restored...")
                        os.rename(str(path_disabled), str(path))
                        ret += 1

        return ret

    def __match_dll_metainfo(self, addon: Addon, alt_path : Path = None) -> bool:
        '''
        Returns whether there are matching info between the addon
        and the linked .dll file
        '''
        metadata = meta.get_wfile_metadata(alt_path if alt_path is not None else addon.binding.path)

        any_match = (
            addon.base.name.lower() in metadata.get('Name', '').lower()
        ) or (
            metadata.get('Company', '').lower() in [_.lower() for _ in addon.base.contributors]
        ) or (
            addon.base.name.lower() in metadata.get('Company', '').lower()
        ) or (
            metadata.get('Company', '').lower() in addon.base.name.lower()
        ) or (
            addon.base.name.lower() in metadata.get('File description', '').lower()
        ) or (
            any(_.lower() in metadata.get('File description', '').lower() for _ in addon.base.contributors)
        )

        return any_match


    def __restore_bin_dir(self, bin_dir: Path) -> bool:
        '''
        Restore backup folder with active addons.

        @bin_dir : Path -- The current directory where the .dll addons are stored.
        '''

        ret: bool = False

        addons_bak_dir: Path = bin_dir.parent / f"{bin_dir.name}.addons.bak"
        arc_bak_dir: Path = bin_dir.parent / f"{bin_dir.name}.arc.bak"
        def_bak_dir: Path = bin_dir.parent / f"{bin_dir.name}.bak"

        if addons_bak_dir.exists():
            logger().info(msg="Addons will be restored...")

            if not def_bak_dir.exists():
                os.rename(str(bin_dir), str(def_bak_dir))

            os.rename(str(arc_bak_dir), str(bin_dir))

            ret = True

        elif addons_bak_dir.exists(): # backward compatibility

            logger().info(msg="Addons will be restored...")

            if not def_bak_dir.exists():
                os.rename(str(bin_dir), str(def_bak_dir))

            os.rename(str(arc_bak_dir), str(bin_dir))

            ret = True

        return ret

    def __disable_bin_dir(self, bin_dir: Path) -> bool:
        '''
        Overrides the typing of installed addons (.dll -> .dll.disabled)
        @bin_dir : Path -- The vanilla bin directory.
        @addons : List[Addon] -- The list of addons to be disabled (.dll only, .exe are filtered out)
        '''

        ret = False

        addons_bak_dir: Path = bin_dir.parent / f"{bin_dir.name}.addons.bak"
        def_bak_dir: Path = bin_dir.parent / f"{bin_dir.name}.bak"

        if not addons_bak_dir.exists():
            logger().info(msg="Addons will be suppressed...")

            os.rename(str(bin_dir), str(addons_bak_dir))

            if def_bak_dir.exists():
                os.rename(str(def_bak_dir), str(bin_dir))

            ret = True

        return ret
