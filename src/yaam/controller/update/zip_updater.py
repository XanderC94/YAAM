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
        self.namings = dict()

    def __unpack_zip(self, content: ZipFile, unpack_dir: Path, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)
        root_items = zip_helper.get_root_items(content)
        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        # renaming enabled only for dlls
        rename_enabled = addon.binding.is_dll()
        unpack_alias_stem : str = None
        if rename_enabled and len(addon.binding.path.suffix) > 0:
            unpack_alias_stem = addon.binding.path.stem

        logger().info(msg=f"Unpacking zipped {addon.base.name}...")

        for item in content.filelist:

            extraction_target = Path(content.extract(item, unpack_dir))

            if not item.is_dir():
                can_add_alias: bool = False

                extraction_alias = extraction_target.name
                # Default rename: use 'unpack_alias'
                curr_unpack_alias = extraction_alias
                if rename_enabled and unpack_alias_stem is not None:
                    can_add_alias = rename_enabled
                    curr_unpack_alias = f"{unpack_alias_stem}{extraction_target.suffix}"

                # If a rename map is set and has a match
                # use that that instead of default
                if rename_enabled and item.filename in self.namings:
                    can_add_alias = rename_enabled
                    curr_unpack_alias = self.namings.get(item.filename, curr_unpack_alias)

                # in case of a single directory inside the zip,
                # the folder will be unpacked to the parent directory
                # all the non-folder sub-root item will be renamed to the target addon filename
                is_single_root_folder_item : bool = False
                if is_single_root_folder:
                    is_single_root_folder_item = root_dirs[0].rfind(extraction_target.parent.name) > -1
                    # get relative path from single root dir
                    relative_target = extraction_target.relative_to(unpack_dir / root_dirs[0])
                    # apply to supposed unpack dir
                    extraction_target = extraction_target.replace(unpack_dir / relative_target)

                # if the current non-dir item is in the root
                # or is in the root of a single root zip
                # that file can be renamed to the specified alias
                target_file = extraction_target
                if item.filename in root_items or is_single_root_folder_item:
                    can_add_alias = rename_enabled
                    tmp_file = unpack_dir / curr_unpack_alias
                    target_file = extraction_target.replace(tmp_file)

                logger().info(msg=f"Unpacked {target_file.relative_to(unpack_dir)} to {unpack_dir}")

                # Add to or update the naming map (given or generated)
                if can_add_alias and rename_enabled:
                    self.namings[extraction_target.relative_to(unpack_dir)] = curr_unpack_alias

        if is_single_root_folder:
            shutil.rmtree(unpack_dir / root_dirs[0])

        ret_code = UpdateResult.UNPACKING_OK

        return ret_code

    def __find_installer(self, lookup_dir: Path) -> Path:
        installer_path = None

        for _ in lookup_dir.iterdir():
            if _.is_file() and "installer" in _.name:
                installer_path = _
                break

        if installer_path is None:
            for _ in lookup_dir.iterdir():
                if _.is_file() and ("exe" in _.suffix or "msi" in _.suffix):
                    installer_path = _
                    break

        return installer_path

    def __unpack_installer_zip(self, content: ZipFile, unpack_dir: Path, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)
        root_items = zip_helper.get_root_items(content)
        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        logger().info(msg=f"Unpacking zipped {addon.base.name} installer...")

        if not unpack_dir.exists():
            makedirs(unpack_dir)

        content.extractall(unpack_dir)

        logger().info(msg=f"Unpacked {addon.base.name} installer to {unpack_dir}.")

        content_lookup_dir = unpack_dir

        if is_single_root_folder:
            content_lookup_dir = content_lookup_dir / root_dirs[0]

        installer_path = self.__find_installer(content_lookup_dir)

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
            if len(addon.binding.path.suffix) > 0:
                unpack_dir : Path = addon.binding.path.parent
            else:
                # if an addon doesn't specify a name (points to a folder)
                # item are unpacked as-is (no rename) and will be repacked
                # to the root directoy if the zip root is a single folder
                # NOTE: Renaming is possible in this case only with a rename map
                unpack_dir : Path = addon.binding.path

            if not unpack_dir.exists():
                makedirs(unpack_dir)

            if addon.base.uri_info.is_installer:
                self.__unpack_installer_zip(zip_content, unpack_dir / "installer", addon)
            else:
                self.__unpack_zip(zip_content, unpack_dir, addon)

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
