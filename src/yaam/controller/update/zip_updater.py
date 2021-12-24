'''
Zipped addons updater module
'''
from os import makedirs
from pathlib import Path
import shutil
from typing import Tuple
from zipfile import BadZipfile, ZipFile
from requests.models import Response
from yaam.controller.update.results import UpdateResult
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import process
import yaam.utils.response as responses
import yaam.utils.zip as zip_helper

class ZipUpdater(object):
    '''
    Static zipped addons updater class
    '''
    @staticmethod
    def __check_zip_hash(content: ZipFile, signature_path : Path, addon: Addon) -> Tuple[UpdateResult, str]:

        ret_code = UpdateResult.NO_UPDATE

        remote_signature = None
        local_signature = None

        is_not_online_installer = not addon.base.uri_info.is_installer or addon.base.uri_info.is_offline

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

                remote_signature = Hasher.SHA256.make_hash_from_bytes(content.fp.read())
                logger().info(msg=f"Remote hash is {remote_signature}.")

                if remote_signature == local_signature:
                    logger().info(msg="Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    if local_signature is None:
                        logger().info(msg="Local addon zip signature is missing. Updating...")
                    else:
                        logger().info(msg="New addon update found. Downloading...")
                    ret_code = UpdateResult.TO_UPDATE
        else:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
            remote_signature = Hasher.SHA256.make_hash_from_bytes(content.fp.read())
            ret_code = UpdateResult.TO_CREATE

        return (ret_code, remote_signature)

    @staticmethod
    def __unpack_zip(content: ZipFile, unpack_dir: Path, unpack_alias: str, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)

        root_items = zip_helper.get_root_items(content)

        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        for item in content.filelist:

            extraction_target = Path(content.extract(item, unpack_dir))

            curr_unpack_stem = extraction_target.stem if unpack_alias is None else unpack_alias

            # in case of a single directory inside the zip,
            # the folder will be unpacked to the parent directory
            # all the non-folder sub-root item will be renamed to the target addon filename
            if is_single_root_folder and item.filename not in root_dirs:

                target_file = extraction_target.parent.parent / f"{extraction_target.stem}{extraction_target.suffix}"
                if root_dirs[0].rfind(extraction_target.parent.name) >= 0:
                    target_file = extraction_target.parent.parent / f"{curr_unpack_stem}{extraction_target.suffix}"

                extraction_target = extraction_target.replace(target_file)

            elif item.filename in root_items and not item.is_dir():
                target_file = extraction_target.parent / f"{curr_unpack_stem}{extraction_target.suffix}"
                extraction_target = extraction_target.replace(target_file)

            logger().info(msg=f"Created {addon.base.name}({extraction_target.name})...")

        if is_single_root_folder:
            shutil.rmtree(unpack_dir / root_dirs[0])

        ret_code = UpdateResult.UNPACKING_OK

        return ret_code

    @staticmethod
    def __unpack_installer_zip(content: ZipFile, unpack_dir: Path, addon: Addon) -> Tuple[UpdateResult, Path]:
        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)

        root_items = zip_helper.get_root_items(content)

        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        content.extractall(unpack_dir)

        logger().info(msg=f"Unpacked {addon.base.name} installer to {str(unpack_dir)}...")

        ret_code = UpdateResult.UNPACKING_OK

        content_lookup_dir = unpack_dir if not is_single_root_folder else unpack_dir / root_dirs[0]

        installer_path = None
        for _ in content_lookup_dir.iterdir():
            if _.is_file() and "installer" in _.name:
                installer_path = _
                break

        if installer_path is None:
            for _ in content_lookup_dir.iterdir():
                if _.is_file() and ("exe" in _.suffix or "msi" in _.suffix):
                    installer_path = _
                    break

        return (ret_code, installer_path)

    @staticmethod
    def update_from_zip(response: Response, addon: Addon):
        '''
        Updated a zipped addon package
        '''
        ret_code = UpdateResult.NONE

        logger().info(msg=f"Unpacking zipped {addon.base.name}...")

        # if the content is a zip,
        # unpack all the content in the parent directory
        # of file pointed by the addon path
        try:
            zip_content : ZipFile = responses.unpack_zip(response.content)
        except BadZipfile as ex:
            logger().error(msg=str(ex))
            return UpdateResult.INVALID_ZIP

        unpack_dir : Path = None
        unpack_stem = None

        if addon.binding.path.is_file():
            unpack_dir : Path = addon.binding.path.parent
            # renaming enabled only for dlls (for now)
            unpack_stem = addon.binding.path.stem if addon.binding.is_dll() else None
        else:
            # if an addon doesn't specify a name (points to a folder)
            # item are unpacked as-is (no rename) but will normally
            # repacked to the root directoy if the zip root is a single folder
            unpack_dir : Path = addon.binding.path

        signature_path = None

        if unpack_stem is None:
            stem = addon.base.name.replace(' ', '_').lower()
            signature_path = unpack_dir / f"{stem}.zip.signature"
        else:
            signature_path = unpack_dir / f"{unpack_stem}.zip.signature"

        [ret_code, remote_signature] = ZipUpdater.__check_zip_hash(zip_content, signature_path, addon)

        if ret_code == UpdateResult.TO_CREATE or ret_code == UpdateResult.TO_UPDATE:
            try:

                if not unpack_dir.exists():
                    makedirs(unpack_dir)

                if addon.base.uri_info.is_installer:
                    installer_dir = unpack_dir / "installer"
                    if not installer_dir.exists():
                        makedirs(installer_dir)
                    [ret_code, installer_path] = ZipUpdater.__unpack_installer_zip(zip_content, installer_dir, addon)

                    logger().info(msg=f"Launching installer {installer_path}")
                    if "msi" in installer_path.suffix:
                        process.run("msiexec.exe", installer_dir, [f"/i {installer_path}"], slack=0)
                    else:
                        process.run(installer_path, installer_dir, slack=0)

                    shutil.rmtree(installer_dir)
                else:
                    ret_code = ZipUpdater.__unpack_zip(zip_content, unpack_dir, unpack_stem, addon)

                with open(signature_path, 'w', encoding='utf-8') as _:
                    _.write(remote_signature)

                ret_code = ret_code.complete()

            except IOError as ex:
                logger().error(ex)
                ret_code = ret_code.error()
                
        return ret_code
