'''
Addon metadata collector module
'''

from os import makedirs
from pathlib import Path
from typing import Dict, List
from yaam.controller.http import HttpRequestManager
from yaam.model.mutable.addon import Addon
from yaam.model.type.binding import BindingType
from yaam.model.mutable.metadata import AddonMetadata
from yaam.utils.json.io import read_json, write_json
from yaam.utils.logger import static_logger as logger
from yaam.utils.hashing import Hasher

class MetadataCollector(object):
    '''
    Addon metadata collector
    '''

    def __init__(self, http: HttpRequestManager) -> None:
        self.__http = http
        self.__local_metadata: Dict[str, Dict[BindingType,AddonMetadata]] = dict()

    def load_local_metadata(self, addons: List[Addon]):
        '''
        Compute all the local addon metadata
        '''
        self.__local_metadata.clear()
        for _ in addons:
            if _.base.name not in self.__local_metadata:
                self.__local_metadata[_.base.name] = dict()
            self.__local_metadata[_.base.name][_.binding.typing] = self.__get_local_metadata(_)

    def get_local_metadata(self, addon: Addon) ->  AddonMetadata:
        '''
        Get the local addon metadata if exists
        '''
        return self.__local_metadata.get(addon.base.name, dict).get(addon.binding.typing, None)

    def __get_metadata_path(self, addon: Addon) -> str:
        '''
        Compute the addon metadata path from addon info
        '''
        metadata_path : Path = None

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
        metadata_path : Path = self.__get_metadata_path(addon)
        metadata : AddonMetadata = AddonMetadata.from_json(read_json(metadata_path))
        if len(metadata.hash_signature) == 0 and not addon.binding.is_headless:
            metadata.hash_signature = Hasher.SHA256.make_hash_from_file(addon.binding.path)
        metadata.uri = metadata_path
        return metadata

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
                uri=addon.base.uri,
                etag=response.headers.get('etag', ''),
                last_modified=response.headers.get('last-modified', '')
            )

        if metadata is None:
            metadata = AddonMetadata()

        return metadata

    def save_metadata(self, metadata: AddonMetadata, path: Path):
        '''
        Save metadata locally
        '''
        logger().info(msg=f"Saving addon metadata to {path}")
        if not path.parent.exists():
            makedirs(path.parent)
        write_json(metadata.to_json(), path)
