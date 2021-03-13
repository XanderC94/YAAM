
import os
import time 
import json
# import pandas as panda
import tabulate
from pathlib import Path
from bs4 import BeautifulSoup
import gw2sl_utils as gw2_sl
from gw2sl_objects import Addon, AddonFactory

#####################################################################

if __name__ == "__main__":

    APPDATA = Path(os.getenv("APPDATA"))

    gw2_config_xml_path = APPDATA / "Guild Wars 2/GFXSettings.Gw2-64.exe.xml"
    gw2_settings_json_path = APPDATA / "Guild Wars 2/Settings.json"

    gw2_root = Path("C:\\Program Files\\Guild Wars 2")
    gw2_exe  = "Gw2-64.exe"

    if gw2_config_xml_path.exists():

        print(f"Reading root path from {gw2_config_xml_path}")
        with open(gw2_config_xml_path) as handler:
            config = BeautifulSoup(handler, features="xml")
            app = config.find("GSA_SDK").find("APPLICATION")

            gw2_root = Path(app.find("INSTALLPATH")['Value'])
            gw2_exe = app.find("EXECUTABLE")['Value']
    else:
        print("If GW2 is installed, run it at least once to create GFXSettings.*.xml config file...")
        exit(0)

    gw2_path = gw2_root / gw2_exe
    gw2_bin = gw2_root / "bin64"

    print(f"GW2 location is {gw2_path} ...")

    if not gw2_path.exists():
        print("but location doesn't exists! Closing.")
        exit(0)

    gw2_addons = list()
    gw2_args = set()

    if gw2_settings_json_path.exists():
        with open(gw2_settings_json_path) as handler:

            settings = json.load(handler)
            gw2_args = set(settings['arguments'])

            # Aggiungo la cartella binary ai path incompleti
            for addon in settings['addons']:
                if addon['path'].endswith('.dll'):
                    if addon['path'].startswith("\\") or addon['path'].startswith("/"):
                        addon['path'] = addon['path'][1:]

                    addon['path'] = gw2_root / addon['path'];

                gw2_addons.append(AddonFactory.from_dict(addon))

            print("\nLoaded addons: ")
            data= dict()
            for addon in settings['addons']:
                for (k, v) in addon.items():
                    if k not in data:
                        data[k] = list()
                    s = str(v)
                    if len(s) > 32:
                        s = s[:16] + ' ... ' + s[-16:]

                    data[k].append(s)

            table = tabulate.tabulate(data, headers="keys", tablefmt='rst', colalign=("left",))
            print(table)

    is_arcdps_disabled = ("/noArcDPS" in gw2_args) or ("-noArcDPS" in gw2_args)

    print(f"\nArcDPS is enabled? {not is_arcdps_disabled}\n")

    # if "/noArcDPS" in gw2_args:
    #     gw2_args.remove("/noArcDPS")
    
    # if "-noArcDPS" in gw2_args:
    #     gw2_args.remove("-noArcDPS")

    if is_arcdps_disabled:
        gw2_sl.DisableAddons(gw2_bin)
    else:
        gw2_sl.RestoreAddons(gw2_bin)
        gw2_sl.UpdateAddons(gw2_addons)

    gw2_sl.Run(gw2_path, gw2_root, gw2_args)

    for addon in gw2_addons:
        if addon.enabled and addon.is_exe():
            gw2_sl.Run(addon.path, addon.path.parent)

    exit(1)