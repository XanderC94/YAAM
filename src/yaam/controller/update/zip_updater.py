'''
Zipped addons updater module
'''
from os import makedirs
from pathlib import Path
import shutil
from zipfile import BadZipfile, ZipFile
from requests.models import Response
from yaam.controller.update.results import UpdateResult
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import process
import yaam.utils.response as responses
import yaam.utils.zip as zip_helper

class ZipUpdater(object):
    '''
    Static zipped addons updater class
    '''

    def __init__(self, code = UpdateResult.NONE) -> None:
        self.__code = code

    @staticmethod
    def __unpack_zip(content: ZipFile, unpack_dir: Path, unpack_alias: str, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)

        root_items = zip_helper.get_root_items(content)

        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        logger().info(msg=f"Unpacking zipped {addon.base.name}...")

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

            logger().info(msg=f"Unpacked {extraction_target.name} installer to {unpack_dir}.")

        if is_single_root_folder:
            shutil.rmtree(unpack_dir / root_dirs[0])

        ret_code = UpdateResult.UNPACKING_OK

        return ret_code

    @staticmethod
    def __unpack_installer_zip(content: ZipFile, unpack_dir: Path, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        if not unpack_dir.exists():
            makedirs(unpack_dir)

        root_dirs = zip_helper.get_root_dirs(content)

        root_items = zip_helper.get_root_items(content)

        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        logger().info(msg=f"Unpacking zipped {addon.base.name} installer...")

        content.extractall(unpack_dir)

        logger().info(msg=f"Unpacked {addon.base.name} installer to {unpack_dir}.")

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

        if "msi" in installer_path.suffix:
            process.run_command(f"msiexec.exe /i {installer_path}", slack=0)
        else:
            process.run(installer_path, unpack_dir, slack=0)

        shutil.rmtree(unpack_dir)

        ret_code = UpdateResult.UNPACKING_OK

        return ret_code

    def update_from_zip(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Updated a zipped addon package
        '''
        ret_code = self.__code

        if ret_code == UpdateResult.TO_CREATE:
            logger().info(msg=f"Creating {addon.base.name}({addon.binding.path.name})...")
        else:
            logger().info(msg=f"Updating {addon.base.name}({addon.binding.path.name})...")

        try:
            # if the content is a zip,
            # unpack all the content in the parent directory
            # of file pointed by the addon path
            zip_content : ZipFile = responses.repack_to_zip(response.content)

            unpack_dir : Path = None
            unpack_stem : str = None

            if addon.binding.path.is_file():
                unpack_dir : Path = addon.binding.path.parent
                # renaming enabled only for dlls (for now)
                unpack_stem = addon.binding.path.stem if addon.binding.is_dll() else None
            else:
                # if an addon doesn't specify a name (points to a folder)
                # item are unpacked as-is (no rename) but will normally
                # repacked to the root directoy if the zip root is a single folder
                unpack_dir : Path = addon.binding.path

            if not unpack_dir.exists():
                makedirs(unpack_dir)

            if addon.base.uri_info.is_installer:
                ret_code = ZipUpdater.__unpack_installer_zip(zip_content, unpack_dir / "installer", addon)
            else:
                ret_code = ZipUpdater.__unpack_zip(zip_content, unpack_dir, unpack_stem, addon)

        except IOError as ex:
            logger().error(ex)
            ret_code = ret_code.error()
        except BadZipfile as ex:
            logger().error(msg=str(ex))
            ret_code = UpdateResult.INVALID_ZIP
        else:
            ret_code = ret_code.complete()

            if ret_code == UpdateResult.CREATED:
                logger().info(msg=f"Created {addon.base.name}({addon.binding.path.name}).")
            else:
                logger().info(msg=f"Updated {addon.base.name}({addon.binding.path.name}).")

        return ret_code
