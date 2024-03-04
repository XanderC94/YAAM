'''
Addon metadata collector module
'''

from copy import deepcopy
from os import makedirs
from os import remove as remove_file
from shutil import copy2 as copy_file
from pathlib import Path
from typing import Dict, List
from yaam.controller.http import HttpRequestManager
from yaam.model.appcontext import GameContext
from yaam.model.mutable.addon import Addon
from yaam.model.mutable.metadata import AddonMetadata
from yaam.utils.json.io import read_json, write_json
from yaam.utils.logger import static_logger as logger
from yaam.utils.hashing import Hasher


class MetadataCollector(object):
    '''
    Addon metadata collector
    '''

    def __init__(self, http: HttpRequestManager, context: GameContext) -> None:
        self.__http = http
        self.__context = context
        self.__local_metadata: Dict[str, AddonMetadata] = dict()
        self.__local_metadata_backup: Dict[str, AddonMetadata] = dict()
        self.__remote_metadata: Dict[str, AddonMetadata] = dict()

    def get_local_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Get the local addon metadata if exists
        '''
        return self.__local_metadata.get(addon.base.name, None)

    def get_remote_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Retrieve remote addon metadata
        '''
        return self.__remote_metadata.get(addon.base.name, None)

    def set_local_metadata(self, addon: Addon, metadata: AddonMetadata):
        '''
        Set local metadata for the given addon
        '''
        self.__local_metadata[addon.base.name] = metadata

    def set_remote_metadata(self, addon: Addon, metadata: AddonMetadata):
        '''
        Set remote metadata for the given addon
        '''
        self.__remote_metadata[addon.base.name] = metadata

    def load_local_metadata(self, addons: List[Addon]):
        '''
        Compute all the local addon metadata
        '''

        self.__local_metadata.clear()
        self.__local_metadata_backup.clear()

        self.__manage_backward_compatibility(addons)

        for _ in addons:

            curr_metadata = self.fetch_local_metadata(_)

            if curr_metadata is not None:
                self.set_local_metadata(_, curr_metadata)

        self.__local_metadata_backup = deepcopy(self.__local_metadata)

    def fetch_local_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Compute all the local addon metadata
        '''

        curr_metadata_path = Path(self.__get_metadata_path(addon))

        logger().info(msg=f"Fetching {addon.base.name} local metadata...")
        logger().debug(msg=f"{addon.base.name} metadata storage URI is {curr_metadata_path}")

        curr_metadata = self.__read_metadata_from_local_path(curr_metadata_path, addon)

        if curr_metadata is not None:
            logger().debug(msg=f"Fetching {addon.base.name} local metadata completed.")
        else:
            logger().error(msg=f"Fetched empty metadata for {addon.base.name}...")

        return curr_metadata

    def __get_metadata_path(self, addon: Addon) -> str:
        '''
        Compute the addon metadata path from addon info
        '''
        metadata_path: Path = None

        metadata_stem = addon.base.name.replace(' ', '_').lower()

        metadata_bucket = self.__context.metadata_dir / Hasher.SHA256.make_hash_from_string(str(addon.binding.path))

        metadata_path = metadata_bucket / f"metadata_{metadata_stem}.json"

        return metadata_path

    def __read_metadata_from_local_path(self, metadata_path: Path, addon: Addon) -> AddonMetadata:
        '''
        Retrieve local addon metadata
        '''

        metadata: AddonMetadata = AddonMetadata.from_json(read_json(metadata_path))

        # if its a single physical file and not a collection, we recompute the hash signature...
        if len(metadata.hash_signature) == 0 and not addon.binding.is_headless:
            metadata.hash_signature = Hasher.SHA256.make_hash_from_file(addon.binding.path)

        metadata.uri = metadata_path
        metadata.addon = addon.base.name

        return metadata

    def load_remote_metadata(self, addons: List[Addon], follow: bool = False, **kwargs) -> None:
        '''
        Retrieve remote metadata for the provided addons collection and store them
        '''
        for _ in addons:
            metadata = self.fetch_remote_metadata(_, follow, **kwargs)
            if metadata is not None:
                self.set_remote_metadata(_, metadata)

    def fetch_remote_metadata(self, addon: Addon, follow: bool = False, **kwargs) -> AddonMetadata:
        '''
        Fetch metadata for the given Addon from remote
        '''
        metadata = None

        logger().debug(msg=f"Fetching {addon.base.name} remote metadata from {addon.base.uri}")
        logger().debug(msg=f"{addon.base.name} metadata storage URI is {addon.base.uri}")

        response = self.__http.head(addon.base.uri, **kwargs)

        if response is not None:
            # detect redirect
            if 'location' in response.headers and follow:
                logger().debug(msg=f"Redirecting to {response.headers['location']}")
                response = self.__http.head(response.headers['location'], **kwargs)

            metadata = AddonMetadata(
                addon=addon.base.name,
                uri=addon.base.uri,
                etag=response.headers.get('etag', ''),
                last_modified=response.headers.get('last-modified', '')
            )

            logger().debug(msg=f"Fetching {addon.base.name} remote metadata completed.")

        # if metadata is None:
        #     metadata = AddonMetadata()

        return metadata

    def update_local_metadata(self, remote_metadata: AddonMetadata) -> bool:
        '''
        Update the corresponding local metadata with the remote one
        '''
        if remote_metadata.addon in self.__local_metadata:

            self.__local_metadata[remote_metadata.addon].last_modified = remote_metadata.last_modified
            self.__local_metadata[remote_metadata.addon].etag = remote_metadata.etag

            for binding in self.__local_metadata[remote_metadata.addon].namings:
                if binding in remote_metadata.namings and len(remote_metadata.namings[binding]) > 0:
                    self.__local_metadata[remote_metadata.addon].namings[binding] = remote_metadata.namings[binding]

    def save_local_metadata(self):
        '''
        Save all the local addon metadata
        '''
        self.__local_metadata.clear()
        for (_, metadata) in self.__local_metadata.items():
            self.save_metadata(metadata, metadata.uri)

    def save_metadata(self, metadata: AddonMetadata, path: Path or str):
        '''
        Save metadata locally
        '''

        if isinstance(path, str):
            path = Path(path)

        logger().info(msg=f"Saving {metadata.addon} metadata ...")
        logger().debug(msg=f"{metadata.addon} metadata storage storage URI is {path}")
        makedirs(path.parent, exist_ok=True)
        write_json(metadata.to_json(), path)

    def __manage_backward_compatibility(self, addons: List[Addon]):
        '''
        ...
        '''

        # Move old metadata for backward compatibility
        # To the new destination (YAAM appdata folder)
        logged_once: bool = False

        for _ in addons:

            old_metadata_path = Path(self.__get_metadata_path_old(_))
            curr_metadata_path = Path(self.__get_metadata_path(_))

            if old_metadata_path.exists():

                makedirs(curr_metadata_path.parent, exist_ok=True)

                copy_file(str(old_metadata_path), str(curr_metadata_path))
                remove_file(str(old_metadata_path))

                if not logged_once:
                    logger().info("Updating metadata storage locations...")
                    logged_once = True

                logger().debug(msg=f"Moved {str(old_metadata_path)} to {str(curr_metadata_path)}")

    def __get_metadata_path_old(self, addon: Addon) -> str:
        '''
        Compute the addon metadata path from addon info
        '''
        metadata_path: Path = None

        metadata_stem = addon.base.name.replace(' ', '_').lower()

        if not addon.binding.is_headless:
            metadata_path = addon.binding.path.parent / f"metadata_{metadata_stem}.json"
        else:
            metadata_path = addon.binding.path / f"metadata_{metadata_stem}.json"

        return metadata_path
