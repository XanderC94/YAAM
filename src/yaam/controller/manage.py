'''
Addon enable-disable management module
'''
import os

from pathlib import Path
from typing import Iterable
from yaam.model.context import GameContext
import yaam.utils.metadata as meta
from yaam.model.mutable.addon import Addon
from yaam.utils.logger import static_logger as logger

def restore_bin_dir(bin_dir: Path) -> bool:
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

def disable_bin_dir(bin_dir: Path) -> bool:
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

def disable_dll_addons(addons: Iterable[Addon], game_context: GameContext = None) -> int:
    '''
    Overrides the typing of installed addons (.dll -> .dll.disabled)
    @addons : Iterable[Addon] -- The list of addons to be disabled (.dll only, .exe are filtered out)
    '''

    ret = 0
    for addon in addons:
        if addon.binding.is_dll() and not addon.binding.enabled:
            path = addon.binding.path

            can_disable = True
            path_disabled = Path(f"{path}.disabled")
            if addon.base.is_shader():
                if match_dll_metainfo(addon):
                    name_ext = addon.base.name.lower().replace(' ', '')
                    path_disabled = Path(f"{path}.{name_ext}")
                else:
                    can_disable = False

            if path.exists() and can_disable:
                logger().info(msg=f"Addon {addon.base.name}({path.name}) will be suppressed...")
                os.rename(str(path), str(path_disabled))
                ret += 1

    return ret

def restore_dll_addons(addons: Iterable[Addon], game_context: GameContext = None) -> int:
    '''
    Restore disabled addons.
    @addons : Iterable[Addon] -- The list of addons to be enabled (.dll only, .exe are filtered out)
    '''
    ret = 0
    for addon in addons:
        if addon.binding.is_dll() and addon.binding.enabled:
            path = addon.binding.path

            can_disable = True
            path_disabled = Path(f"{path}.disabled")
            if addon.base.is_shader():
                if match_dll_metainfo(addon):
                    name_ext = addon.base.name.lower().replace(' ', '')
                    path_disabled = Path(f"{path}.{name_ext}")
                else:
                    can_disable = False

            if path_disabled.exists() and can_disable:
                logger().info(msg=f"Addon {addon.base.name}({path.name}) will be restored...")
                os.rename(str(path_disabled), str(path))
                ret += 1

    return ret

def match_dll_metainfo(addon: Addon) -> bool:
    '''
    Returns whether there are matching info between the addon
    and the linked .dll file
    '''
    metadata = meta.get_wfile_metadata(addon.binding.path)

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
