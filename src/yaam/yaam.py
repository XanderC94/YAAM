'''
gw2sl main module
'''

import os
import tabulate

from pathlib import Path

from utils.update import update_addons
from utils.manage import restore_dll_addons, disable_dll_addons
from utils.process import run
from utils.options import Option

from objects.gw2 import GW2
from objects.binding_type import BindingType
from objects.addon import Addon

from typing import List

#####################################################################

if __name__ == "__main__":

    gw2 = GW2(Path(os.getenv("APPDATA")))

    print(f"Reading root path from {gw2.config_path}")
    
    if not gw2.load_config():
        print("GFXSettings.*.xml not found.\
            If GW2 is installed, run it at least once \
            to create GFXSettings.*.xml config file...")

        exit(0)
    
    print(f"GW2 location is {gw2.path} ...", end=" ")

    if not gw2.path.exists():
        print("but location doesn't exists! Closing.")
        exit(0)

    addons : List[Addon] = list()
    
    if gw2.load_settings():
        
        allowed_binding_types = set([ BindingType.EXE, BindingType.AGNOSTIC, gw2.dxgi ])

        # build addons incarnation
        for binding_type in BindingType:
            if binding_type in gw2.bindings:
                for (addon_name, binding) in gw2.bindings[binding_type].items():
                    if addon_name in gw2.bases:
                        addon = Addon(gw2.bases[addon_name], binding)
                        if not binding_type in allowed_binding_types:
                            addon.set_enabled(False)
                        addons.append(addon)

        print("Loaded addons: ")
        data = dict()
        for addon in addons:
            if addon.typing in allowed_binding_types:
                table = addon.to_table()
                for (k, v) in table.items():
                    if k not in data:
                        data[k] = list()
                    data[k].append(v)

        print(tabulate.tabulate(data, headers="keys", tablefmt='rst', colalign=("left",)))
    
    print(f"GW2 render: {gw2.dxgi.name}")

    is_addon_update_only = sum([1 for _ in Option.UPDATE_ADDONS.aliases if _ in gw2.args]) > 0

    disable_dll_addons(addons)
    restore_dll_addons(addons)
            
    update_addons(addons)

    if not is_addon_update_only:
        run(gw2.path, gw2.root, gw2.args)

        for addon in addons:
            if addon.is_enabled and addon.is_exe():
                run(addon.path, addon.path.parent)

        print("Stack complete. Closing...")

    exit(1)