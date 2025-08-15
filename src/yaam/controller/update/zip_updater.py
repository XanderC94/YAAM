'''
Zipped addons updater module
'''
from os import makedirs, walk
from pathlib import Path
import shutil
from typing import Dict
from zipfile import BadZipfile, ZipFile
from requests import Response
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

    def __init__(self, code: UpdateResult = UpdateResult.NONE) -> None:
        self.__code = code
        self.naming: Dict[str, str] = dict()

    def __unpack_zip(self, content: ZipFile, unpack_dir: Path, addon: Addon) -> UpdateResult:

        ret_code = UpdateResult.UNPACKING_FAILED

        root_dirs = zip_helper.get_root_dirs(content)
        root_items = zip_helper.get_root_items(content)
        is_single_root_folder = len(root_dirs) == 1 and len(root_items) == 1

        # renaming enabled only for dlls
        rename_enabled = addon.binding.is_dll()

        logger().debug(msg=f"Unpacking zipped {addon.base.name}...")

        tmp_unpack_dir = unpack_dir / "tmp"
        makedirs(tmp_unpack_dir, exist_ok=True)

        for item in content.filelist:

            extraction_path = Path(content.extract(item, tmp_unpack_dir))

            is_single_root_folder_item = is_single_root_folder and root_dirs[0].rfind(extraction_path.parent.name) > -1
            is_root_item = item.filename in root_items or is_single_root_folder_item

            if not item.is_dir():
                can_add_alias: bool = False
                # Original unpack name
                extraction_alias = extraction_path.name
                # Default unpack rename
                curr_unpack_alias = extraction_alias
                # NOTE: In order to avoid renaming every single item in a zip file
                # single-alias renaming is restricted to root items of zips containing addons
                # Can be disabled by simply making the addon path *headless*
                if rename_enabled and not addon.binding.is_headless and is_root_item:
                    can_add_alias = rename_enabled
                    curr_unpack_alias = f"{addon.binding.path.stem}{extraction_path.suffix}"

                # If a rename map is set and has a match
                # use that that instead of default
                # NOTE: In order to not add the items in a zip file
                # to the metadata naming map, check that the map
                # effectively contains the current item filename
                if rename_enabled:
                    if item.filename in addon.naming:
                        can_add_alias = rename_enabled
                        curr_unpack_alias = addon.naming.get(item.filename, curr_unpack_alias)
                    elif item.filename.replace("/", "\\") in addon.naming:
                        can_add_alias = rename_enabled
                        curr_unpack_alias = addon.naming.get(item.filename.replace("/", "\\"), curr_unpack_alias)

                # NOTE: Disabled automatic single-root-folder unpacking (for now)
                # # in case of a single directory inside the zip,
                # # the folder will be unpacked to the parent directory
                # # all the non-folder sub-root item will be renamed to the target addon filename
                # is_single_root_folder_item : bool = False
                # if is_single_root_folder:
                #     is_single_root_folder_item = root_dirs[0].rfind(extraction_target.parent.name) > -1
                #     # get relative path from single root dir
                #     relative_target = extraction_target.relative_to(tmp_unpack_dir / root_dirs[0])
                #     # apply to supposed unpack dir
                #     extraction_target = extraction_target.replace(tmp_unpack_dir / relative_target)

                # if the current non-dir item is in the root
                # or is in the root of a single root zip
                # that file can be renamed to the specified alias
                target_path = extraction_path
                # if item.filename in root_items or is_single_root_folder_item:
                if rename_enabled and can_add_alias and extraction_path != (tmp_unpack_dir / curr_unpack_alias).resolve():
                    target_path = (tmp_unpack_dir / curr_unpack_alias).resolve()
                    makedirs(target_path.parent, exist_ok=True)
                    target_path = extraction_path.replace(target_path)

                logger().debug(msg=f"Unpacked {target_path.relative_to(tmp_unpack_dir)} to {tmp_unpack_dir}")

                # Add to or update the naming map (given or generated)
                if can_add_alias and rename_enabled:
                    self.naming[extraction_path.relative_to(tmp_unpack_dir)] = target_path.relative_to(tmp_unpack_dir)

        if is_single_root_folder:
            n_files = sum([len(fl) for rt, dr, fl in walk(tmp_unpack_dir / root_dirs[0])])
            if n_files == 0:
                shutil.rmtree(tmp_unpack_dir / root_dirs[0])

        shutil.copytree(tmp_unpack_dir, unpack_dir, dirs_exist_ok=True)
        shutil.rmtree(tmp_unpack_dir)

        ret_code = UpdateResult.UNPACKED

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

        logger().debug(msg=f"Unpacking zipped {addon.base.name} installer...")

        makedirs(unpack_dir, exist_ok=True)

        content.extractall(unpack_dir)

        logger().debug(msg=f"Unpacked {addon.base.name} installer to {unpack_dir}.")

        content_lookup_dir = unpack_dir
        if is_single_root_folder:
            content_lookup_dir = content_lookup_dir / root_dirs[0]

        installer_path = self.__find_installer(content_lookup_dir)

        if "msi" in installer_path.suffix:
            process.run_command(f"msiexec.exe /i {installer_path}", slack=0)
        else:
            process.run(installer_path, unpack_dir, slack=0)

        shutil.rmtree(unpack_dir)

        ret_code = UpdateResult.UNPACKED

        return ret_code

    def update_from_zip(self, response: Response, addon: Addon) -> UpdateResult:
        '''
        Updated a zipped addon package
        '''
        ret_code = self.__code

        try:
            # if the content is a zip,
            # unpack all the content in the parent directory
            # of file pointed by the addon path
            zip_content: ZipFile = responses.repack_to_zip(response.content)
            # if an addon doesn't specify a name (points to a folder)
            # item are unpacked as-is (no rename) and will be repacked
            # to the root directoy if the zip root is a single folder
            # NOTE: Renaming is possible in this case only with a rename map
            unpack_dir: Path = addon.binding.workspace

            makedirs(unpack_dir, exist_ok=True)

            if addon.base.is_installer:
                self.__unpack_installer_zip(zip_content, unpack_dir / "installer", addon)
            else:
                self.__unpack_zip(zip_content, unpack_dir, addon)

        except IOError as ex:
            logger().error(msg=str(ex))
            ret_code = ret_code.error()
        except BadZipfile as ex:
            logger().error(msg=str(ex))
            ret_code = UpdateResult.INVALID_ZIP
        else:
            ret_code = ret_code.complete()

        return ret_code
