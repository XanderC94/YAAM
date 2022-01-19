'''
Datastreamed addons updater module
'''
from os import makedirs
from pathlib import Path
import shutil
from typing import Dict
from urllib.parse import urlparse
from requests.models import Response
from yaam.controller.update.results import UpdateResult
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import process
from yaam.utils import response as responses

class DatastreamUpdater(object):
    '''
    Static datastream addon updater class
    '''

    def __init__(self, code = UpdateResult.NONE) -> None:
        self.__code = code
        self.naming: Dict[str, str] = dict()

    def __fallback_addon_name(self, response: Response, addon: Addon) -> str:
        response_alias : str = None

        addon_suffix = ".dll" if addon.binding.is_dll() else ".exe"
        if not addon.binding.is_headless:
            addon_suffix = addon.binding.path.suffix

        if len(addon.naming) > 0:
            for key in addon.naming:
                if responses.find_filename(response, key):
                    response_alias = key
            if response_alias is None:
                response_alias = list(addon.naming.keys())[0]
        elif not addon.binding.is_headless:
            response_alias = addon.binding.path.name
        else:
            response_alias = f"{addon.base.name.replace(' ', '_').lower()}{addon_suffix}"

        return response_alias

    def update_from_datastream(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Update addon from simple datastream
        '''
        ret_code = self.__code

        unpack_dir : Path = addon.binding.workspace
        makedirs(unpack_dir, exist_ok=True)

        rename_enabled : bool = addon.binding.is_dll() or addon.binding.is_file()

        # write file on disk
        try:
            can_add_alias = False
            # Compute original response filename
            response_alias : str = responses.get_filename(response)
            # If the name is not found by normal meanings of http-header / url parsing...
            # hoping it never happens.
            if response_alias is None:
                response_alias = self.__fallback_addon_name(response, addon)

            # default rename specified by addon path
            unpack_alias = response_alias
            if rename_enabled and not addon.binding.is_headless:
                can_add_alias = True
                unpack_alias = addon.binding.path.name
            # If a rename map is set and has matches
            # follow that instead of default
            if rename_enabled:
                can_add_alias = True
                unpack_alias = addon.naming.get(response_alias, unpack_alias)

            # write the file at the given path
            with open(unpack_dir / unpack_alias, 'wb') as _:
                _.write(response.content)

            # Add the rename map (given or generated) to addon metadata
            if can_add_alias and rename_enabled:
                self.naming[response_alias] = unpack_alias

        except IOError as ex:
            logger().error(ex)
            ret_code = ret_code.error()
        else:
            ret_code = ret_code.complete()

        return ret_code

    ####################################################################################################################

    def update_from_installer(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Update addon from installer datastream
        '''

        ret_code = self.__code

        try:
            installer_dir = addon.binding.path.parent / "installer"

            installer_name : str = Path(urlparse(response.url).path).name
            installer_path = installer_dir / installer_name

            makedirs(installer_dir, exist_ok=True)

            with open(installer_path, 'wb') as _:
                _.write(response.content)

            if "msi" in installer_path.suffix:
                process.run_command(f"msiexec.exe /i {installer_path}", slack=0)
            else:
                process.run(installer_path, installer_dir, slack=0)

            shutil.rmtree(installer_dir)

        except IOError as ex:
            logger().error(ex)
            ret_code = ret_code.error()
        else:
            ret_code = ret_code.complete()

        return ret_code
