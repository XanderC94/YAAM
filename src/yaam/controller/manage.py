'''
Addon enable-disable management module
'''

import os

from pathlib import Path
from typing import Iterable
from yaam.controller.metadata import MetadataCollector
from yaam.controller.update.updater import AddonUpdater
from yaam.model.type.binding import BindingType
# import yaam.utils.metadata as meta
from yaam.model.mutable.addon import Addon
from yaam.utils.logger import static_logger as logger


class AddonManager(object):
    '''
    Addon management class
    '''

    def __init__(self, metadata: MetadataCollector, updater: AddonUpdater, binding_type: BindingType) -> None:
        self.__metadata = metadata
        self.__updater = updater
        self.__binding_type = binding_type

        self.__default_request_args = {
            'timeout': 120,
            'allow_redirects': True,
            'headers': {
                'cache-control': 'no-cache',
                'pragma': 'no-cache'
            }
        }

    def initialize_metadata(self, addons: Iterable[Addon], prefetch_updates: bool, force_updates: bool, ignore_disabled: bool):
        '''
        Initialize local and remote metadata
        '''

        logger().info(msg="Fetching all addon metadata...")

        self.__metadata.load_local_metadata(addons)

        if prefetch_updates:
            self.__metadata.load_remote_metadata(addons, False, **self.__default_request_args)
            self.__updater.preload_addons_updates(addons, self.__metadata, ignore_disabled, force_updates)

    def resolve_renames(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
        '''
        Detect and resolve renamed addons by aligning physical names to pointed ones
        '''

        for addon in addons:
            metadata = self.__metadata.get_local_metadata(addon)
            binding_namings = metadata.namings.get(addon.binding.typing, dict())

            modified: bool = False
            if len(binding_namings) > 0:
                if len(addon.naming) > 0:
                    for (key, new_rule) in addon.naming.items():
                        prev_rule = binding_namings.get(key, None)
                        if self.__check_and_rename(addon, prev_rule, new_rule):
                            binding_namings[key] = new_rule
                            modified = True

                elif not addon.binding.is_headless:
                    new_rule = addon.binding.default_naming
                    for (key, prev_rule) in binding_namings.items():
                        if new_rule.endswith(Path(prev_rule).suffix):
                            if self.__check_and_rename(addon, prev_rule, new_rule):
                                binding_namings[key] = new_rule
                                modified = True
                                break

            if modified:
                self.__metadata.save_metadata(metadata, metadata.uri)

    def __check_and_rename(self, addon: Addon, prev_rule: str, new_rule: str) -> bool:
        '''
        ...
        '''
        ret: bool = False
        if prev_rule is not None and new_rule is not None and prev_rule != new_rule:
            logger().info(msg=f"Detected a name change in {addon.base.name}: {prev_rule} is now {new_rule}")
            prev_target = addon.binding.workspace / prev_rule
            new_target = addon.binding.workspace / new_rule
            if prev_target.exists():
                prev_target.rename(new_target)
            ret = True
        return ret

    def __get_naming_rules(self, addon: Addon) -> list:

        metadata = self.__metadata.get_local_metadata(addon)

        type_naming_rules = dict()
        if metadata is not None:
            type_naming_rules = metadata.namings.get(addon.binding.typing, dict())

        naming_rules = []
        if len(type_naming_rules) == 0:
            if not addon.binding.is_headless:
                naming_rules.append(addon.binding.default_naming)
        else:
            naming_rules = [
                _ for _ in type_naming_rules.values()
                if _.endswith(addon.binding.typing.suffix)
            ]

        return naming_rules

    def disable_addons(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
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
            if not addon.binding.is_enabled:
                if addon.binding.is_dll() or addon.binding.is_file():

                    workspace = addon.binding.workspace

                    naming_rules = self.__get_naming_rules(addon)

                    for _ in naming_rules:
                        path = workspace / _

                        can_disable = True
                        path_disabled = Path(f"{path}.disabled")
                        if addon.base.is_shader:
                            # I need to match pointed shader path
                            # but most shaders share the same name
                            # therefore they can't be disabled indiscrimately
                            if self.__match_metainfo(addon) or (
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

    def restore_addons(self, addons: Iterable[Addon], prev: Iterable[Addon] = None) -> int:
        '''
        Restore disabled addons.
        @addons : Iterable[Addon] -- The list of addons to be enabled (.dll only, .exe are filtered out)
        '''
        ret = 0
        for addon in addons:
            if addon.binding.is_enabled:
                if addon.binding.is_dll() or addon.binding.is_file():

                    workspace = addon.binding.workspace

                    naming_rules = self.__get_naming_rules(addon)

                    for _ in naming_rules:
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

    def __match_metainfo(self, addon: Addon, alt_path: Path = None) -> bool:
        '''
        Returns whether there are matching info between the addon
        and the linked .dll file
        '''

        any_match = False

        # metadata = meta.get_wfile_metadata(alt_path if alt_path is not None else addon.binding.path)

        # any_match = (
        #     addon.base.name.lower() in metadata.get('Name', '').lower()
        # ) or (
        #     metadata.get('Company', '').lower() in [_.lower() for _ in addon.base.contributors]
        # ) or (
        #     addon.base.name.lower() in metadata.get('Company', '').lower()
        # ) or (
        #     metadata.get('Company', '').lower() in addon.base.name.lower()
        # ) or (
        #     addon.base.name.lower() in metadata.get('File description', '').lower()
        # ) or (
        #     any(_.lower() in metadata.get('File description', '').lower() for _ in addon.base.contributors)
        # )

        return any_match

    def update_addons(self, addons: Iterable[Addon], force_updates: bool = False) -> None:
        '''
        Updated the provided addons with the update metadata results provided by the metadata collector
        '''

        self.__updater.update_addons(addons, self.__metadata, force_updates, **self.__default_request_args)
