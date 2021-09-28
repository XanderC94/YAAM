'''
GW2SL utility module
'''

import io
import zipfile
import requests

from enum import Enum

from utils.hashing import Hasher
from objects.addon import Addon

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

def update_addon(addon: Addon):
    '''
    Update where specified or possible the provided addon

    @addon: dict -- addon to updated
    '''
    ret_code = UpdateResult.NONE
    
    if not addon.is_dll():
        ret_code = UpdateResult.NOT_DLL
    elif not addon.enabled:
        ret_code = UpdateResult.DISABLED
    elif not len(addon.update_url):
        print(f"No update URL provided.")
        ret_code = UpdateResult.NO_URL
    else:
        res = requests.get(addon.update_url)

        data : bytes = res.content

        if 'Content-Disposition' in res.headers:
            if res.headers['Content-Disposition'].endswith(".zip"):
                file_like_object = io.BytesIO(res.content)
                zip_data = zipfile.ZipFile(file_like_object)
                for f in zip_data.filelist:
                    if f.filename.endswith(".dll"):
                        h = zip_data.open(f.filename)
                        data = h.read()
                        h.close()
                        break

        ok_code = UpdateResult.NONE
        fail_code = UpdateResult.NONE

        if addon.path.exists():
            if addon.update:
                print(f"Checking {addon.name}({addon.path.name}) updates...")

                remote_hash = Hasher.SHA256.make_hash_from_bytes(data)
                print(f"Remote hash is {remote_hash}.")

                local_hash = Hasher.SHA256.make_hash_from_file(addon.path)
                print(f"Local hash is {local_hash}.")

                if remote_hash == local_hash:
                    print("Addon is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    print("New addon update found. Downloading...", end=" ")
                    ok_code = UpdateResult.UPDATED
                    fail_code = UpdateResult.UPDATE_FAILED
        else:
            print(f"Creating {addon.name}({addon.path.name})...", end=" ")
            ok_code = UpdateResult.CREATED
            fail_code = UpdateResult.CREATE_FAILED
        
        if not ok_code == UpdateResult.NONE and not fail_code == UpdateResult.NONE:
            # write file on disk
            with open(addon.path, 'wb') as addon_file:
                if addon_file.write(data):
                    ret_code = ok_code
                    print("Done.")
                else:
                    ret_code = fail_code
                    print("Failed.")

    return ret_code

def update_addons(addons: list):
    '''
    Update where specified or possible the addons provided by the list

    @addons: list -- list of addons to updated
    '''

    for addon in addons:
        update_addon(addon)
