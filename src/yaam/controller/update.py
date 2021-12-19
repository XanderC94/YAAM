'''
GW2SL update utility module
'''
from os import makedirs
from enum import Enum
from pathlib import Path
import shutil
from typing import Iterable
from requests.models import Response
from urllib3.exceptions import HTTPError
import requests
from requests.exceptions import RequestException
from yaam.utils.exceptions import GitHubException
import yaam.utils.validators.url as validator
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
import yaam.utils.github as github
import yaam.utils.response as respones

class UpdateResult(Enum):
    '''
    Possible results of addon update
    '''
    NO_URL = -5
    UPDATE_FAILED = -4
    CREATE_FAILED = -3
    NOT_DLL = -2
    DELETED = -1
    NONE = 0
    DISABLED = 1
    CREATED = 2
    UPDATED = 3
    UP_TO_DATE = 4

class AddonUpdater(object):
    '''
    Static updater
    '''

    @staticmethod
    def update_addons(addons: Iterable[Addon]):
        '''
        Updates the provided addons

        @addons: list -- list of addons to updated
        '''

        for addon in addons:
            AddonUpdater.update_addon(addon)

    @staticmethod
    def update_addon(addon: Addon):
        '''
        Update the provided addon if specified and when possible

        @addon: Addon -- addon to updated
        '''
        ret_code = UpdateResult.NONE

        ret_code = AddonUpdater.update_dll_addon(addon)

        # Add other types and checks on the ret code ...

        return ret_code

    @staticmethod
    def update_dll_addon(addon: Addon):
        '''
        Addon update routine
        '''
        ret_code = UpdateResult.NONE

        logger().debug(msg=f"{addon.base.name}({addon.binding.path.name})")

        if not addon.binding.is_dll():
            ret_code = UpdateResult.NOT_DLL
        elif not addon.binding.enabled:
            ret_code = UpdateResult.DISABLED
        elif not validator.url(addon.base.uri):
            logger().info(msg=f"No valid update URL provided for {addon.base.name}({addon.binding.path.name}).")
            ret_code = UpdateResult.NO_URL
        else:

            try:

                req_headers = {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }

                download_uri = github.api.fetch_latest_release_download_url(
                    addon.base.uri, timeout=10, allow_redirects=True, headers=req_headers
                )

                response = requests.get(download_uri, timeout=10, allow_redirects=True, headers=req_headers)
                
            except RequestException as req_ex:
                logger().error(req_ex)
            except HTTPError as http_ex:
                logger().error(http_ex)
            except TimeoutError as timeout_ex:
                logger().error(timeout_ex)
            except GitHubException as ex:
                logger().error(ex)
            else:

                if respones.is_zip_content(response):
                    ret_code = AddonUpdater.__update_dll_from_zip(response, addon)
                else:
                    ret_code = AddonUpdater.__update_dll_from_datastream(response, addon)
                
        return ret_code

    @staticmethod
    def __update_dll_from_zip(response: Response, addon: Addon):

        ret_code = UpdateResult.NONE
        ok_code = UpdateResult.NONE
        fail_code = UpdateResult.NONE

        logger().info(msg=f"Unpacking zipped {addon.base.name}.")

        # if the content is a zip,
        # unpack all the content in the parent directory
        # of file pointed by the addon path
        zip_content = respones.unpack_zip(response.content)
        
        unpack_directory : Path = None
        unpack_stem = None

        if addon.binding.path.is_file():
            unpack_directory : Path = addon.binding.path.parent
            unpack_stem = addon.binding.path.stem
        else:
            # if an addon doesn't specify a name (points to a folder)
            # item are unpacked as-is (no rename) but will normally
            # repacked to the root directoy if the zip root is a single folder
            unpack_directory : Path = addon.binding.path

        remote_addon_signature = None
        local_addon_signature = None
        addon_signature_path = None

        if addon.binding.path.exists():
            if addon.binding.updateable:

                if unpack_stem is None:
                    addon_signature_path = unpack_directory / f"{addon.base.name.replace(' ', '_').lower()}.zip.signature"
                else:
                    addon_signature_path = unpack_directory / f"{unpack_stem}.zip.signature"

                # Check if the <addon name>.signature file exists
                if addon_signature_path.exists():
                    with open(addon_signature_path, 'r', encoding='utf-8') as _:
                        local_addon_signature = _.read().replace('\n', '').replace(' ', '')
                        logger().info(msg=f"Local hash is {local_addon_signature}.")
                else:
                    logger().info(msg="Local hash not found.")

                remote_addon_signature = Hasher.SHA256.make_hash_from_bytes(response.content)
                logger().info(msg=f"Remote hash is {remote_addon_signature}.")

                if remote_addon_signature == local_addon_signature:
                    logger().info(msg="Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    if local_addon_signature is None:
                        logger().info(msg="Local addon zip signature is missing. Updating...")
                    else:
                        logger().info(msg="New addon update found. Downloading...")
                    ok_code = UpdateResult.UPDATED
                    fail_code = UpdateResult.UPDATE_FAILED
        else:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
            remote_addon_signature = Hasher.SHA256.make_hash_from_bytes(response.content)
            ok_code = UpdateResult.CREATED
            fail_code = UpdateResult.CREATE_FAILED

        if ok_code == UpdateResult.CREATED or ok_code == UpdateResult.UPDATED:
            try:

                if not unpack_directory.exists():
                    makedirs(unpack_directory)

                root_dirs = [
                    _.filename for _ in zip_content.filelist if _.filename.count('/') == 1 and _.is_dir()
                ]
                
                root_items = [
                    _.filename for _ in zip_content.filelist if _.filename in root_dirs or _.filename.count('/') == 0
                ]

                is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

                ret_code = ok_code
                for item in zip_content.filelist:
                
                    extraction_target = Path(zip_content.extract(item, unpack_directory))
                
                    curr_unpack_stem = extraction_target.stem if unpack_stem is None else unpack_stem
                    
                    logger().info(msg=f"Created {addon.base.name}({curr_unpack_stem}{extraction_target.suffix})...")

                    # in case of a single directory inside the zip,
                    # the folder will be unpacked to the parent directory
                    # all the non-folder sub-root item will be renamed to the target addon filename
                    if is_single_root_folder and item.filename not in root_dirs:
                        
                        target_file = extraction_target.parent.parent / f"{extraction_target.stem}{extraction_target.suffix}"
                        if root_dirs[0].rfind(extraction_target.parent.name) >= 0:
                            target_file = extraction_target.parent.parent / f"{curr_unpack_stem}{extraction_target.suffix}"

                        extraction_target.replace(target_file)

                    elif item.filename in root_items and not item.is_dir():
                        target_file = extraction_target.parent / f"{curr_unpack_stem}{extraction_target.suffix}"
                        extraction_target.replace(target_file)

                if is_single_root_folder:
                    shutil.rmtree(unpack_directory / root_dirs[0])

                if ret_code == ok_code:
                    with open(addon_signature_path, 'w', encoding='utf-8') as _:
                        _.write(remote_addon_signature)
            except IOError as ex:
                logger().error(ex)
                ret_code = fail_code

        return ret_code

    @staticmethod
    def __update_dll_from_datastream(response: Response, addon: Addon):

        ret_code = UpdateResult.NONE
        ok_code = UpdateResult.NONE
        fail_code = UpdateResult.NONE

        data : bytes = response.content

        if addon.binding.path.exists():
            if addon.binding.updateable:
                logger().info(msg=f"Checking {addon.base.name}({addon.binding.path.name}) updates...")

                remote_hash = Hasher.SHA256.make_hash_from_bytes(data)
                logger().info(msg=f"Remote hash is {remote_hash}.")

                local_hash = Hasher.SHA256.make_hash_from_file(addon.binding.path)
                logger().info(msg=f"Local hash is {local_hash}.")

                if remote_hash == local_hash:
                    logger().info(msg="Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    logger().info(msg="New addon update found. Downloading...")
                    ok_code = UpdateResult.UPDATED
                    fail_code = UpdateResult.UPDATE_FAILED
        else:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
            ok_code = UpdateResult.CREATED
            fail_code = UpdateResult.CREATE_FAILED

        if ok_code == UpdateResult.CREATED or ok_code == UpdateResult.UPDATED:
            # write file on disk
            if not addon.binding.path.parent.exists():
                makedirs(addon.binding.path.parent)
            with open(addon.binding.path, 'wb') as addon_file:
                if addon_file.write(data):
                    ret_code = ok_code
                    logger().info(msg="Done.")
                else:
                    ret_code = fail_code
                    logger().info(msg="Failed.")

        return ret_code
