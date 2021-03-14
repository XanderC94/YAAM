'''
gw2sl main module
'''

import os
import json
from pathlib import Path
import tabulate

from bs4 import BeautifulSoup

from utils.update import restore_addons, disable_addons, update_addons
from utils.process import run
from objects.addon import AddonFactory

#####################################################################

if __name__ == "__main__":

    APPDATA = Path(os.getenv("APPDATA"))

    GW2_CONFIG_XML_PATH = APPDATA / "Guild Wars 2/GFXSettings.Gw2-64.exe.xml"
    GW2_SETTINGS_JSON_PATH = APPDATA / "Guild Wars 2/Settings.json"

    GW2_ROOT = Path("C:\\Program Files\\Guild Wars 2")
    GW2_EXE = "Gw2-64.exe"

    if GW2_CONFIG_XML_PATH.exists():

        print(f"Reading root path from {GW2_CONFIG_XML_PATH}")
        with open(GW2_CONFIG_XML_PATH) as handler:
            gw2_config_xml = BeautifulSoup(handler, features="xml")
            gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

            GW2_ROOT = Path(gw2_app_token.find("INSTALLPATH")['Value'])
            GW2_EXE = gw2_app_token.find("EXECUTABLE")['Value']
    else:
        print("GFXSettings.*.xml not found.\
            If GW2 is installed, run it at least once \
            to create GFXSettings.*.xml config file...")

        exit(0)

    GW2_PATH = GW2_ROOT / GW2_EXE
    GW2_BIN = GW2_ROOT / "bin64"

    print(f"GW2 location is {GW2_PATH} ...")

    if not GW2_PATH.exists():
        print("but location doesn't exists! Closing.")
        exit(0)

    gw2_addons = list()
    gw2_args = set()

    if GW2_SETTINGS_JSON_PATH.exists():
        with open(GW2_SETTINGS_JSON_PATH) as handler:

            gw2_settings = json.load(handler)
            gw2_args = set(gw2_settings['arguments'])

            # Aggiungo la cartella binary ai path incompleti
            for addon in gw2_settings['addons']:
                if addon['path'].endswith('.dll'):
                    if addon['path'].startswith("\\") or addon['path'].startswith("/"):
                        addon['path'] = addon['path'][1:]

                    addon['path'] = GW2_ROOT / addon['path']

                gw2_addons.append(AddonFactory.from_dict(addon))

            print("\nLoaded addons: ")
            data = dict()
            for addon in gw2_settings['addons']:
                for (k, v) in addon.items():
                    if k not in data:
                        data[k] = list()
                    s = str(v)
                    if len(s) > 32:
                        s = ' ... ' + s[-24:]

                    data[k].append(s)

            print(tabulate.tabulate(data, headers="keys", tablefmt='rst', colalign=("left",)))

    is_arcdps_disabled = ("/noArcDPS" in gw2_args) or ("-noArcDPS" in gw2_args)

    print(f"\nArcDPS is enabled? {not is_arcdps_disabled}\n")

    if is_arcdps_disabled:
        disable_addons(GW2_BIN)
    else:
        restore_addons(GW2_BIN)
        update_addons(gw2_addons)

    run(GW2_PATH, GW2_ROOT, gw2_args)

    for addon in gw2_addons:
        if addon.enabled and addon.is_exe():
            run(addon.path, addon.path.parent)

    print("Stack complete. Closing...")

    exit(1)