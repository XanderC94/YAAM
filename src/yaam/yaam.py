'''
gw2sl main module
'''

import os
import json
import tabulate

from pathlib import Path
from bs4 import BeautifulSoup

from utils.update import update_addons
from utils.manage import restore_addons, disable_addons
from utils.process import run
from utils.options import OPTION

from objects.render import Render
from objects.addon import AddonFactory

#####################################################################

if __name__ == "__main__":

    APPDATA = Path(os.getenv("APPDATA"))

    GW2_CONFIG_XML_PATH = APPDATA / "Guild Wars 2/GFXSettings.Gw2-64.exe.xml"
    GW2_SETTINGS_JSON_PATH = APPDATA / "Guild Wars 2/Settings.json"

    GW2_ROOT = Path("C:\\Program Files\\Guild Wars 2")
    GW2_EXE = "Gw2-64.exe"

    DXGI_RENDER = Render.DXGI_9

    if GW2_CONFIG_XML_PATH.exists():

        print(f"Reading root path from {GW2_CONFIG_XML_PATH}")
        with open(GW2_CONFIG_XML_PATH) as handler:
            gw2_config_xml = BeautifulSoup(handler, features="xml")
            gw2_app_token = gw2_config_xml.find("GSA_SDK").find("APPLICATION")

            GW2_ROOT = Path(gw2_app_token.find("INSTALLPATH")['Value'])
            GW2_EXE = gw2_app_token.find("EXECUTABLE")['Value']

            # gw2_app_game_settings = gw2_config_xml.find("GSA_SDK").find('GAMESETTINGS')
            # # Check game render
            # gw2_app_dx11_game_render = gw2_app_game_settings.find("OPTION").find_all(Name="dx11 render")
            # is_dx11_render = gw2_app_dx11_game_render is not None

    else:
        print("GFXSettings.*.xml not found.\
            If GW2 is installed, run it at least once \
            to create GFXSettings.*.xml config file...")

        exit(0)

    GW2_PATH = GW2_ROOT / GW2_EXE
    GW2_BIN = GW2_ROOT / "bin64"

    GW2_BIN_D3D9 = GW2_ROOT / "bin64"
    GW2_BIN_D3D11 = GW2_ROOT

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
            
            if ("/dx11" in gw2_args) or ("-dx11" in gw2_args):
                DXGI_RENDER = Render.DXGI_11

            # Aggiungo la cartella root ai path incompleti
            for addon in gw2_settings['addons']:

                # standard dxgi management
                if addon['path'].endswith('.dll'):
                    # remove slashes
                    if addon['path'].startswith("\\") or addon['path'].startswith("/"):
                        addon['path'] = addon['path'][1:]

                    addon['path'] = GW2_ROOT / addon['path']
                
                # dxgi 9 .dll management
                if "path_d3d9" in addon:
                    # remove slashes
                    if addon['path_d3d9'].startswith("\\") or addon['path_d3d9'].startswith("/"):
                        addon['path_d3d9'] = addon['path_d3d9'][1:]

                    addon['path_d3d9'] = GW2_ROOT / addon['path_d3d9']

                gw2_addons.append(AddonFactory.from_dict(addon, DXGI_RENDER))

            print("\nLoaded addons: ")
            data = dict()
            for addon in gw2_addons:
                table = AddonFactory.to_table(addon)
                for (k, v) in table.items():
                    if k not in data:
                        data[k] = list()
                    data[k].append(v)

            print(tabulate.tabulate(data, headers="keys", tablefmt='rst', colalign=("left",)))
    
    print()
    print(f"GW2 render: {DXGI_RENDER.name}")

    # is_arcdps_disabled = sum([1 for _ in OPTION.NO_ARC_DPS.aliases() if _ in gw2_args]) > 0
    # is_arcdps_disabled = is_arcdps_disabled or sum([ 1 for _ in gw2_addons if _.name == "ArcDPS" and not _.enabled], 0) > 0
    # print(f"ArcDPS is enabled? {not is_arcdps_disabled}")

    is_addon_update_only = sum([1 for _ in OPTION.UPDATE_ADDONS.aliases() if _ in gw2_args]) > 0

    disable_addons(gw2_addons, Render.DXGI_9)
    disable_addons(gw2_addons, Render.DXGI_11)
    
    if DXGI_RENDER == Render.DXGI_11:
        disable_addons(gw2_addons, Render.DXGI_9)
        restore_addons(gw2_addons, Render.DXGI_11)
    else:
        disable_addons(gw2_addons, Render.DXGI_11)
        restore_addons(gw2_addons, Render.DXGI_9)
        
    update_addons(gw2_addons)

    if not is_addon_update_only:
        run(GW2_PATH, GW2_ROOT, gw2_args)

        for addon in gw2_addons:
            if addon.enabled and addon.is_exe():
                run(addon.path, addon.path.parent)

        print("Stack complete. Closing...")

    exit(1)