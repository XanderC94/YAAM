'''
GW2SL utility module
'''

import os

from enum import Enum
from pathlib import Path

import requests

from utils.hashing import Hasher
from objects.addon import Addon
from objects.render import Render
from typing import List

class UpdateResult(Enum):
    '''
    Possible results of addon update
    '''
    NO_URL = -5,
    UPDATE_FAILED = -4,
    CREATE_FAILED = -3,
    NOT_DLL = -2,
    DELETED = -1,
    DISABLED = 0,
    CREATED = 1,
    UPDATED = 2,
    UP_TO_DATE = 3,

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

def update_addon(addon: Addon):
    '''
    Update where specified or possible the provided addon

    @addon: dict -- addon to updated
    '''

    ret_code = UpdateResult.NOT_DLL

    if addon.is_dll():

        ret_code = UpdateResult.DISABLED

        if addon.path.exists() and addon.enabled:

            if addon.update and len(addon.update_url):
                
                print(f"Checking {addon.name}({addon.path.name}) updates...")

                res = requests.get(addon.update_url)

                remote_hash = Hasher.SHA256.make_hash_from_bytes(res.content)
                print(f"Remote hash is {remote_hash}.")

                local_hash = Hasher.SHA256.make_hash_from_file(addon.path)
                print(f"Local hash is {local_hash}.")

                if remote_hash == local_hash:

                    print("Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE

                else:
                    
                    print("New addon update found. Downloading...", end=" ")
                    # write file on disk
                    with open(addon.path, 'wb') as addon_file:
                        if addon_file.write(res.content):
                            ret_code = UpdateResult.UPDATED
                            print("Done.")
                        else:
                            ret_code = UpdateResult.UPDATE_FAILED
                            print("Failed.")
                
            # elif not addon.enabled:

            #     print(f"Addon {addon.name} is disabled, will be removed...")

            #     os.remove(addon.path)
            #     ret_code = UpdateResult.DELETED

        elif addon.enabled:
            
            print(f"Creating {addon.name}({addon.path.name})...", end=" ")
            if len(addon.update_url):

                res = requests.get(addon.update_url)
                # write file on disk
                with open(addon.path, 'wb') as addon_file:
                    if addon_file.write(res.content):
                        ret_code = UpdateResult.CREATED
                        print("Done.")
                    else:
                        ret_code = UpdateResult.CREATE_FAILED
                        print("Failed.")
            else:
                print(f"No update URL provided.")
                ret_code = UpdateResult.NO_URL

    return ret_code

def update_addons(addons: list):
    '''
    Update where specified or possible the addons provided by the list

    @addons: list -- list of addons to updated
    '''

    for addon in addons:
        update_addon(addon)
