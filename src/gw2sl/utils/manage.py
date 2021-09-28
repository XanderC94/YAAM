
import os

from pathlib import Path
from objects.render import Render
from typing import List
from objects.addon import Addon

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
        print("Addons will be restored...")

        if not def_bak_dir.exists():
            os.rename(str(bin_dir), str(def_bak_dir))

        os.rename(str(arc_bak_dir), str(bin_dir))

        ret = True

    elif addons_bak_dir.exists(): # backward compatibility

        print("Addons will be restored...")

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
        print("Addons will be suppressed...")

        os.rename(str(bin_dir), str(addons_bak_dir))

        if def_bak_dir.exists():
            os.rename(str(def_bak_dir), str(bin_dir))

        ret = True

    return ret

def restore_addons(addons: List[Addon], dxgi : Render) -> int:
    '''
    Restore disabled addons.
    @addons : List[Addon] -- The list of addons to be enabled (.dll only, .exe are filtered out)
    '''
    ret = 0
    for addon in addons:
        if addon.is_dll() and addon.enabled:
            p = addon.path_dxgi(dxgi)
            if Path(f"{p}.disabled").exists():
                print(f"Addon {addon.name}({p.name}) will be restored...")
                os.rename(f"{p}.disabled", str(p))
                ret += 1

    return ret

def disable_addons(addons: List[Addon], dxgi : Render) -> int:
    '''
    Overrides the typing of installed addons (.dll -> .dll.disabled)
    @addons : List[Addon] -- The list of addons to be disabled (.dll only, .exe are filtered out)
    '''

    ret = 0
    for addon in addons:
        if addon.is_dll() and not addon.enabled:
            p = addon.path_dxgi(dxgi)
            if p.exists():
                print(f"Addon {addon.name}({p.name}) will be suppressed...")
                os.rename(str(p), f"{p}.disabled")
                ret += 1

    return ret
