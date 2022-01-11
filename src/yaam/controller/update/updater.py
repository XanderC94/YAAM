'''
GW2SL update utility module
'''

from pathlib import Path
from typing import Iterable
from yaam.controller.http import HttpRequestManager
from yaam.controller.metadata import MetadataCollector
from yaam.controller.update.datastream_updater import DatastreamUpdater
from yaam.controller.update.results import UpdateResult
from yaam.controller.update.signature_checker import SignatureChecker
from yaam.controller.update.zip_updater import ZipUpdater
from yaam.model.config import AppConfig
from yaam.model.options import Option
from yaam.model.mutable.addon import Addon
import yaam.utils.validators.url as validator
from yaam.utils.logger import static_logger as logger
import yaam.utils.response as responses

class AddonUpdater(object):
    '''
    Addon updater class
    '''

    def __init__(self, config: AppConfig, metadata: MetadataCollector, http: HttpRequestManager) -> None:
        self.__config = config
        self.__http = http
        self.__meta_collector = metadata

        super().__init__()

    def update_addons(self, addons: Iterable[Addon]):
        '''
        Updates the provided addons

        @addons: list -- list of addons to updated
        '''

        force_update = (self.__config.get_property(Option.UPDATE_ADDONS)
            and self.__config.get_property(Option.FORCE_ACTION))

        for addon in addons:
            self.update_addon(addon, force_update)

    def update_addon(self, addon: Addon, force: bool = False):
        '''
        Update the provided addon if possible

        @addon: Addon -- addon to updated
        '''
        ret_code = UpdateResult.NONE

        logger().debug(msg=f"{addon.base.name}({addon.binding.path.name})")

        if not addon.binding.is_enabled:
            ret_code = UpdateResult.DISABLED
        elif not validator.url(addon.base.uri):
            logger().info(msg=f"No valid update URL provided for {addon.base.name}({addon.binding.path.name}).")
            ret_code = UpdateResult.INVALID_URL
        elif not addon.binding.path.exists() or addon.binding.is_updateable:
            ret_code = self.__update_addon_internal(addon, force)
        else:
            ret_code = UpdateResult.NO_UPDATE
            logger().info(msg=f"Skipping {addon.base.name}({addon.binding.path.name}) update.")

        return ret_code

    def __update_addon_internal(self, addon: Addon, force: bool = False) -> UpdateResult:

        ret_code = UpdateResult.NONE

        default_request_args = {
            'timeout':10,
            'allow_redirects':True,
            'headers':{
                'cache-control': 'no-cache',
                'pragma': 'no-cache'
            }
        }

        # check HASH / SIGNATURE before downloading the resource
        logger().info(msg=f"Fetching {addon.base.name} metadata...")

        metadata = self.__meta_collector.get_local_metadata(addon)
        remote_metadata = self.__meta_collector.get_remote_metadata(addon, **default_request_args)
        remote_metadata.namings = metadata.namings

        # ETAG is apparently inconsistent for latest release in github api
        # so the check is currently only done by means of the <last-modified> HTTP header tag
        if len(metadata.last_modified) == 0 or remote_metadata.last_modified != metadata.last_modified or force:
            
            logger().info(msg="Local and remote metadata mismatch or empty.")

            logger().info(msg=f"Downloading {addon.base.name}...")

            response = self.__http.get_download(addon.base.uri, **default_request_args)

            if response is not None:

                logger().info(msg=f"Downloaded {addon.base.name}.")

                # checking the hash signature as well as to not update needessly
                # since remote metadata might be lacking in some cases
                [ret_code, remote_metadata.hash_signature] = SignatureChecker.check_signatures(response.content, addon, metadata)

                if ret_code == UpdateResult.TO_CREATE or ret_code == UpdateResult.TO_UPDATE or force:

                    logger().info(msg=ret_code.message(addon))

                    if responses.is_zip_content(response):
                        uploader = ZipUpdater(ret_code)
                        ret_code = uploader.update_from_zip(response, addon)
                        remote_metadata.namings[addon.binding.typing] = uploader.naming
                    else:
                        uploader = DatastreamUpdater(ret_code)
                        if addon.base.uri_info.is_installer:
                            ret_code = uploader.update_from_installer(response, addon)
                        else:
                            ret_code = uploader.update_from_datastream(response, addon)
                        remote_metadata.namings[addon.binding.typing] = uploader.naming

                    logger().info(msg=ret_code.message(addon))

                # local metadata must be updated if:
                # - an addon has been created or updated
                # - addon metadatas don't match but the addon signatures do
                if ret_code in [UpdateResult.CREATED, UpdateResult.UPDATED, UpdateResult.UP_TO_DATE] or force:
                    self.__meta_collector.save_metadata(remote_metadata, Path(metadata.uri))
            else:
                logger().error(msg="Received invalid response from addon update uri. Skipping...")
                ret_code = UpdateResult.DOWNLOAD_FAILED
        else:
            logger().info(msg="Local and remote metadata match.")
            ret_code = UpdateResult.UP_TO_DATE

        return ret_code
