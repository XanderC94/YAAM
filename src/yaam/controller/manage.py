'''
Addon enable-disable management module
'''
import os

from pathlib import Path
from typing import Iterable

from yaam.model.mutable.addon import MutableAddon as Addon
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

def restore_dll_addons(addons: Iterable[Addon]) -> int:
    '''
    Restore disabled addons.
    @addons : Iterable[Addon] -- The list of addons to be enabled (.dll only, .exe are filtered out)
    '''
    ret = 0
    for addon in addons:
        if addon.binding.is_dll() and addon.binding.enabled:
            p = addon.binding.path
            if Path(f"{p}.disabled").exists():
                logger().info(msg=f"Addon {addon.base.name}({p.name}) will be restored...")
                os.rename(f"{p}.disabled", str(p))
                ret += 1

    return ret

def disable_dll_addons(addons: Iterable[Addon]) -> int:
    '''
    Overrides the typing of installed addons (.dll -> .dll.disabled)
    @addons : Iterable[Addon] -- The list of addons to be disabled (.dll only, .exe are filtered out)
    '''

    ret = 0
    for addon in addons:
        if addon.binding.is_dll() and not addon.binding.enabled:
            p = addon.binding.path
            if p.exists():
                logger().info(msg=f"Addon {addon.base.name}({p.name}) will be suppressed...")
                os.rename(str(p), f"{p}.disabled")
                ret += 1

    return ret
