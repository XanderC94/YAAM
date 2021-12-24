'''
Datastreamed addons updater module
'''
from os import makedirs
from pathlib import Path
import shutil
from urllib.parse import urlparse
from typing import Tuple
from requests.models import Response
from yaam.controller.update.results import UpdateResult
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import process

class DatastreamUpdater(object):
    '''
    Static datastream addon updater class
    '''

    @staticmethod
    def __check_installer_hash(content: bytes, signature_path: Path, addon: Addon) -> Tuple[UpdateResult, str]:

        ret_code = UpdateResult.NO_UPDATE

        is_not_online_installer = not addon.base.uri_info.is_installer or addon.base.uri_info.is_offline

        remote_signature = None
        local_signature = None

        if addon.binding.path.exists():
            if addon.binding.is_updateable and is_not_online_installer:

                logger().info(msg=f"Checking {addon.base.name}({addon.binding.path.name}) updates...")

                # Check if the <addon name>.zip.signature file exists
                if signature_path.exists():
                    with open(signature_path, 'r', encoding='utf-8') as _:
                        local_signature = _.read().replace('\n', '').replace(' ', '')
                        logger().info(msg=f"Local hash is {local_signature}.")
                else:
                    logger().info(msg="Local hash not found.")

                remote_signature = Hasher.SHA256.make_hash_from_bytes(content)
                logger().info(msg=f"Remote hash is {remote_signature}.")

                if remote_signature == local_signature:
                    logger().info(msg="Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    if local_signature is None:
                        logger().info(msg="Local addon installer signature is missing. Installing...")
                    else:
                        logger().info(msg="New addon update found. Downloading...")
                    ret_code = UpdateResult.TO_UPDATE
        else:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
            remote_signature = Hasher.SHA256.make_hash_from_bytes(content)
            ret_code = UpdateResult.TO_CREATE

        return (ret_code, remote_signature)

    @staticmethod
    def update_from_installer(response: Response, addon: Addon):
        '''
        Update addon from installer datastream
        '''

        ret_code = UpdateResult.NONE

        data : bytes = response.content

        installer_dir = addon.binding.path.parent / "installer"

        installer_name : str = Path(urlparse(response.url).path).name
        installer_path = installer_dir / installer_name

        signature_path = addon.binding.path.parent / f"{installer_path.stem}.installer.signature"

        [ret_code, remote_signature] = DatastreamUpdater.__check_installer_hash(data, signature_path, addon)

        if ret_code == UpdateResult.TO_CREATE or ret_code == UpdateResult.TO_UPDATE:

            if not installer_dir.exists():
                makedirs(installer_dir)

            with open(installer_path, 'wb') as installer_file:
                if installer_file.write(data):
                    ret_code = ret_code.complete()
                    logger().info(msg="Done.")
                else:
                    logger().info(msg="Failed.")
                    ret_code = ret_code.error()

            if ret_code == UpdateResult.CREATED or ret_code == UpdateResult.UPDATED:
                try:
                    if "msi" in installer_path.suffix:
                        process.run_command(f"msiexec.exe /i {installer_path}", slack=0)
                    else:
                        process.run(installer_path, installer_dir, slack=0)
                    shutil.rmtree(installer_dir)
                except IOError as ex:
                    logger().error(ex)
                    ret_code = ret_code.error()

            with open(signature_path, 'w', encoding='utf-8') as _:
                _.write(remote_signature)

        return ret_code

    ####################################################################################################################

    @staticmethod
    def __check_datastream_hash(content: bytes, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.NO_UPDATE

        if addon.binding.path.exists():
            if addon.binding.is_updateable:
                logger().info(msg=f"Checking {addon.base.name}({addon.binding.path.name}) updates...")

                remote_hash = Hasher.SHA256.make_hash_from_bytes(content)
                logger().info(msg=f"Remote hash is {remote_hash}.")

                local_hash = Hasher.SHA256.make_hash_from_file(addon.binding.path)
                logger().info(msg=f"Local hash is {local_hash}.")

                if remote_hash == local_hash:
                    logger().info(msg="Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    logger().info(msg="New addon update found. Downloading...")
                    ret_code = UpdateResult.TO_UPDATE
        else:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
            ret_code = UpdateResult.TO_CREATE

        return ret_code

    @staticmethod
    def update_from_datastream(response: Response, addon: Addon):
        '''
        Update addon from simple datastream
        '''
        ret_code = UpdateResult.NONE

        data : bytes = response.content

        ret_code = DatastreamUpdater.__check_datastream_hash(data, addon)

        if ret_code == UpdateResult.TO_CREATE or ret_code == UpdateResult.TO_UPDATE:
            # write file on disk
            if not addon.binding.path.parent.exists():
                makedirs(addon.binding.path.parent)
                with open(addon.binding.path, 'wb') as addon_file:
                    if addon_file.write(data):
                        logger().info(msg="Done.")
                        ret_code = ret_code.complete()
                    else:
                        logger().info(msg="Failed.")
                        ret_code = ret_code.error()

        return ret_code
