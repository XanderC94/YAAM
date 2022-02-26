'''
Addon metadata collector module
'''

from copy import deepcopy
from os import makedirs
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

    def load_local_metadata(self, addons: List[Addon]):
        '''
        Compute all the local addon metadata
        '''

        self.__local_metadata.clear()
        self.__local_metadata_backup.clear()

        for _ in addons:
            if _.base.name not in self.__local_metadata:
                self.__local_metadata[_.base.name] = dict()

            self.__local_metadata[_.base.name] = self.__get_local_metadata(_)

        self.__local_metadata_backup = deepcopy(self.__local_metadata)

    def __get_metadata_path(self, addon: Addon) -> str:
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

    def __get_local_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Retrieve local addon metadata
        '''

        metadata_path: Path = self.__get_metadata_path(addon)
        metadata: AddonMetadata = AddonMetadata.from_json(read_json(metadata_path))

        if len(metadata.hash_signature) == 0 and not addon.binding.is_headless:
            metadata.hash_signature = Hasher.SHA256.make_hash_from_file(addon.binding.path)

        metadata.uri = metadata_path
        metadata.addon = addon.base.name

        return metadata

    def get_local_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Get the local addon metadata if exists
        '''
        return self.__local_metadata.get(addon.base.name, None)

    def get_remote_metadata(self, addon: Addon, follow: bool = False, **kwargs) -> AddonMetadata:
        '''
        Retrieve remote addon metadata
        '''
        metadata = None

        response = self.__http.head(addon.base.uri, **kwargs)

        if response is not None:
            # detect redirect
            if 'location' in response.headers and follow:
                response = self.__http.head(response.headers['location'], **kwargs)

            metadata = AddonMetadata(
                addon=addon.base.name,
                uri=addon.base.uri,
                etag=response.headers.get('etag', ''),
                last_modified=response.headers.get('last-modified', '')
            )

        if metadata is None:
            metadata = AddonMetadata()

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

        logger().info(msg=f"Saving addon metadata to {path}")
        makedirs(path.parent, exist_ok=True)
        write_json(metadata.to_json(), path)
