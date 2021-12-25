'''
Datastreamed addons updater module
'''
from os import makedirs
from pathlib import Path
import shutil
from urllib.parse import urlparse
from requests.models import Response
from yaam.controller.update.results import UpdateResult
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import process

class DatastreamUpdater(object):
    '''
    Static datastream addon updater class
    '''

    def __init__(self, code = UpdateResult.NONE) -> None:
        self.__code = code

    def update_from_datastream(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Update addon from simple datastream
        '''
        ret_code = self.__code

        if ret_code == UpdateResult.TO_CREATE:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
        else:
            logger().info(msg=f"Updating {addon.base.name}({addon.binding.path.name})...")

        if not addon.binding.path.parent.exists():
            makedirs(addon.binding.path.parent)

        # write file on disk
        try:
            with open(addon.binding.path, 'wb') as _:
                _.write(response.content)
        except IOError as ex:
            logger().error(ex)
            ret_code = ret_code.error()
        else:
            ret_code = ret_code.complete()
            if ret_code == UpdateResult.CREATED:
                logger().info(msg=f"Created {addon.base.name}({addon.binding.path.name}).")
            else:
                logger().info(msg=f"Updated {addon.base.name}({addon.binding.path.name}).")

        return ret_code

    ####################################################################################################################

    def update_from_installer(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Update addon from installer datastream
        '''

        ret_code = self.__code

        if ret_code == UpdateResult.TO_CREATE:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
        else:
            logger().info(msg=f"Updating {addon.base.name}({addon.binding.path.name})...")

        try:
            installer_dir = addon.binding.path.parent / "installer"

            installer_name : str = Path(urlparse(response.url).path).name
            installer_path = installer_dir / installer_name

            if not installer_dir.exists():
                makedirs(installer_dir)

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
            if ret_code == UpdateResult.CREATED:
                logger().info(msg=f"Created {addon.base.name}({addon.binding.path.name}).")
            else:
                logger().info(msg=f"Updated {addon.base.name}({addon.binding.path.name}).")

        return ret_code
