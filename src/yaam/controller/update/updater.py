'''
GW2SL update utility module
'''

from typing import Dict, Iterable
from requests import Response as UpdatePacket
from yaam.controller.http import HttpRequestManager
from yaam.controller.metadata import MetadataCollector
from yaam.controller.update.datastream_updater import DatastreamUpdater
from yaam.controller.update.results import UpdateResult
from yaam.controller.update.zip_updater import ZipUpdater
from yaam.model.mutable.addon import Addon
from yaam.model.mutable.metadata import AddonMetadata
from yaam.utils.exceptions import GitHubException
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger
import yaam.utils.response as responses


class AddonUpdateData(object):
    '''
    Addon update data class
    '''

    def __init__(self, addon_name: str = "", status: UpdateResult = UpdateResult.NONE, http_response: UpdatePacket = None) -> None:
        self.addon_name = addon_name
        self.status = status
        self.http_response = http_response


class AddonUpdater(object):
    '''
    Addon updater class
    '''

    def __init__(self, http: HttpRequestManager) -> None:
        self.__http = http

        self.__addons_updates_preloaded: bool = False
        self.__cached_addons_updates: Dict[str, AddonUpdateData] = dict()

        super().__init__()

    def preload_addons_updates(self, addons: Iterable[Addon], metadata_collector: MetadataCollector,
                               ignore_disabled: bool = False, force_update: bool = False, **kwargs) -> None:
        '''
        Preload update data for the given addon collection
        '''

        self.unload_addons_updates()

        for _ in addons:

            update_data = AddonUpdateData(_.base.name)

            if not _.base.uri.is_valid():
                logger().info(msg=f"No valid update URL provided for {_.base.name}({_.binding.path.name}).")
                update_data.status = UpdateResult.INVALID_URL
            elif not _.binding.path.exists() or _.binding.is_updateable:

                if not ignore_disabled or _.binding.is_enabled:
                    update_data = self.__fetch_addon_updates(_, metadata_collector, force_update, **kwargs)

            else:
                update_data.status = UpdateResult.NO_UPDATE
                logger().info(msg=f"Skipping {_.base.name} updates checks.")

            self.__cached_addons_updates[_.base.name] = update_data

        self.__addons_updates_preloaded = True

    def __fetch_addon_updates(self, addon: Addon, metadata_collector: MetadataCollector, force_update: bool, **kwargs) -> AddonUpdateData:
        '''
        Preload updates data for the given addon
        '''

        udpate_data = AddonUpdateData(addon.base.name)

        local_metadata = metadata_collector.get_local_metadata(addon)
        remote_metadata = metadata_collector.get_remote_metadata(addon)

        if remote_metadata is None:
            udpate_data.status = UpdateResult.NO_METADATA
        elif local_metadata is None:
            udpate_data.status = UpdateResult.NO_METADATA
        else:

            # If path doesn't exists and is not disabled
            # then the addon need to be installed from scratch
            # NOTE: In order to propery support updates of disabled addons
            # we should also check the existence of their disabled path
            # or multiple paths in the addon is headless
            if not addon.binding.path.exists() and addon.binding.is_enabled:
                udpate_data.status = UpdateResult.TO_INSTALL
            else:
                logger().info(msg=f"Checking updates for {addon.base.name}...")

                if len(local_metadata.last_modified) == 0:
                    logger().warning(msg=f"{addon.base.name} Local timestamp is missing!")

                # ETAG is apparently inconsistent for latest release in github api
                # so the check is currently only done by means of the <last-modified> HTTP header tag
                if remote_metadata.last_modified != local_metadata.last_modified:
                    udpate_data.status = UpdateResult.TO_UPDATE

                    logger().debug(msg=f"Timestamp mismatch \'{local_metadata.last_modified}\' =\\= \'{remote_metadata.last_modified}\'.")
                else:
                    udpate_data.status = UpdateResult.UP_TO_DATE

            if udpate_data.status in [UpdateResult.TO_UPDATE, UpdateResult.TO_INSTALL] or force_update:

                logger().debug(msg=f"Downloading {addon.base.name} from {addon.base.uri}...")

                # NOTE: Is it possible to check the HASH SIGNATURE before downloading the resource?
                try:
                    udpate_data.http_response = self.__http.get_download(addon.base.uri, **kwargs)
                except GitHubException as ghex:
                    logger().error(msg=str(ghex))

                if udpate_data.http_response is not None and len(udpate_data.http_response.content) > 0:

                    logger().debug(msg=f"Downloaded {addon.base.name} from {addon.base.uri}.")

                    remote_metadata.namings = local_metadata.namings

                    # Compute and store the update content hash signature in order to
                    # check it against the local signature as to not update needessly
                    # since remote timestamp might be absent sometimes
                    remote_metadata.hash_signature = Hasher.SHA256.make_hash_from_bytes(udpate_data.http_response.content)

                    if remote_metadata.hash_signature != local_metadata.hash_signature:
                        udpate_data.status = UpdateResult.TO_UPDATE
                    else:
                        udpate_data.status = UpdateResult.UP_TO_DATE

                elif udpate_data.http_response is None:
                    udpate_data.status = UpdateResult.HTTP_REQUEST_FAILED
                elif len(udpate_data.http_response.content) == 0:
                    udpate_data.status = UpdateResult.EMPTY_CONTENT

        udpate_data.status.log_download(addon)

        return udpate_data

    def unload_addons_updates(self):
        '''
        Unload cached addon updates
        '''
        self.__addons_updates_preloaded = False
        self.__cached_addons_updates.clear()

    def update_addons(self, addons: Iterable[Addon], metadata_collector: MetadataCollector, force_update: bool = False, **kwargs):
        '''
        Updates the provided addons

        @addons: list -- list of addons to updated
        '''

        if not self.__addons_updates_preloaded:
            self.preload_addons_updates(addons, metadata_collector, force_update, **kwargs)

        for _ in addons:
            # Currently disabled addons can't be updated...
            if _.binding.is_enabled:
                self.update_addon(_, metadata_collector, force_update)

    def update_addon(self, addon: Addon, metadata_collector: MetadataCollector, force: bool = False):
        '''
        Update the provided addon if possible

        @addon: Addon -- addon to updated
        '''
        ret_code = UpdateResult.NO_UPDATE

        local = metadata_collector.get_local_metadata(addon)
        remote = metadata_collector.get_remote_metadata(addon)

        if local is not None and remote is not None:

            update = self.__cached_addons_updates.get(addon.base.name, None)

            if update is not None and update.http_response is not None:

                ret_code = update.status

                if ret_code in [UpdateResult.TO_INSTALL, UpdateResult.TO_UPDATE] or force:

                    ret_code.log_update(addon)

                    ret_code = self.__update_addon(addon, remote, update.http_response)

                    ret_code.log_update(addon)

                # local metadata must be updated if:
                # - an addon has been created or updated
                # - addon metadatas don't match (e.g.: date) but the addon signatures do
                if ret_code in [UpdateResult.INSTALLED, UpdateResult.UPDATED, UpdateResult.UP_TO_DATE] or force:
                    if remote != local:
                        metadata_collector.save_metadata(remote, local.uri)

            elif ret_code in [UpdateResult.TO_INSTALL, UpdateResult.TO_UPDATE]:
                logger().debug("Empty update data. Skipping update.")

        return ret_code

    def __update_addon(self, addon: Addon, metadata: AddonMetadata, update_data: UpdatePacket) -> UpdateResult:
        '''
        Update the provided addon if possible
        '''
        ret_code = UpdateResult.NO_UPDATE

        if responses.is_zip_content(update_data):
            zip_updater = ZipUpdater(ret_code)
            ret_code = zip_updater.update_from_zip(update_data, addon)
            metadata.namings[addon.binding.typing] = zip_updater.naming
        else:
            data_stream_updater = DatastreamUpdater(ret_code)
            if addon.base.is_installer:
                ret_code = data_stream_updater.update_from_installer(update_data, addon)
            else:
                ret_code = data_stream_updater.update_from_datastream(update_data, addon)
            metadata.namings[addon.binding.typing] = data_stream_updater.naming

        return ret_code
