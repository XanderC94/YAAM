'''
GW2SL update utility module
'''
import io
import zipfile
from os import makedirs
from enum import Enum
from typing import Iterable
import requests
from yaam.utils.validators.url import url as url_validator
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import MutableAddon as Addon

class UpdateResult(Enum):
    '''
    Possible results of addon update
    '''
    NO_URL = -5,
    UPDATE_FAILED = -4,
    CREATE_FAILED = -3,
    NOT_DLL = -2,
    DELETED = -1,
    NONE = 0,
    DISABLED = 1,
    CREATED = 2,
    UPDATED = 3,
    UP_TO_DATE = 4,

def update_addons(addons: Iterable[Addon]):
    '''
    Updates the provided addons

    @addons: list -- list of addons to updated
    '''

    for addon in addons:
        update_addon(addon)

def update_addon(addon: Addon):
    '''
    Update the provided addon if specified and when possible

    @addon: Addon -- addon to updated
    '''
    ret_code = UpdateResult.NONE

    ret_code = update_dll_addon(addon)

    # Add other types and checks on the ret code ...

    return ret_code

def update_dll_addon(addon: Addon):

    ret_code = UpdateResult.NONE
    
    if not addon.binding.is_dll():
        ret_code = UpdateResult.NOT_DLL
    elif not addon.binding.enabled:
        ret_code = UpdateResult.DISABLED
    elif not url_validator(addon.base.update_url):
    # elif not len(addon.update_url):
        logger().info(msg=f"No valid update URL provided for {addon.base.name}({addon.binding.path.name}).")
        ret_code = UpdateResult.NO_URL
    else:
        res = requests.get(addon.base.update_url)

        data : bytes = res.content

        if 'Content-Disposition' in res.headers:
            if res.headers['Content-Disposition'].endswith(".zip"):
                file_like_object = io.BytesIO(res.content)
                zip_data = zipfile.ZipFile(file_like_object)
                for f in zip_data.filelist:
                    if f.filename.endswith(addon.path.suffix):
                        h = zip_data.open(f.filename)
                        data = h.read()
                        h.close()
                        break

        ok_code = UpdateResult.NONE
        fail_code = UpdateResult.NONE

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
        
        if not ok_code == UpdateResult.NONE and not fail_code == UpdateResult.NONE:
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
