'''
GW2SL update utility module
'''

from os import makedirs
from pathlib import Path
from typing import Iterable
from requests.models import Response
from requests.sessions import Session
from urllib3.exceptions import HTTPError
import requests
from requests.exceptions import RequestException
from yaam.controller.update.datastream_updater import DatastreamUpdater
from yaam.controller.update.results import UpdateResult
from yaam.controller.update.signature_checker import SignatureChecker
from yaam.controller.update.zip_updater import ZipUpdater
from yaam.model.config import AppConfig
from yaam.model.mutable.metadata import AddonMetadata
from yaam.model.options import Option
from yaam.utils.exceptions import GitHubException
import yaam.utils.validators.url as validator
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import github
from yaam.utils.json.io import read_json, write_json
import yaam.utils.response as responses
from yaam.utils.hashing import Hasher

class AddonUpdater(object):
    '''
    Addon updater class
    '''

    def __init__(self, config: AppConfig) -> None:
        self.__config = config
        self.__gh_session : Session = None
        
        self.namings = dict()

        super().__init__()

    def update_addons(self, addons: Iterable[Addon]):
        '''
        Updates the provided addons

        @addons: list -- list of addons to updated
        '''

        gh_user = self.__config.get_property(Option.GITHUB_USER)
        gh_api_token = self.__config.get_property(Option.GITHUB_API_TOKEN)
        force_update = self.__config.get_property(Option.UPDATE_ADDONS) and self.__config.get_property(Option.FORCE_ACTION)

        self.__gh_session = github.api.open_session(gh_user, gh_api_token)

        for addon in addons:
            self.update_addon(addon, force_update)

        self.__gh_session.close()

    def get_metadata_path(self, addon: Addon) -> str:
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

    def get_metadata(self, addon: Addon) -> AddonMetadata:
        '''
        Retrieve local addon metadata
        '''
        metadata_path : Path = self.get_metadata_path(addon)
        metadata : AddonMetadata = AddonMetadata.from_json(read_json(metadata_path))
        if len(metadata.hash_signature) == 0 and not addon.binding.is_headless:
            metadata.hash_signature = Hasher.SHA256.make_hash_from_file(addon.binding.path)
        metadata.uri = metadata_path
        return metadata

    def get_remote_metadata(self, addon: Addon, **kwargs) -> AddonMetadata:
        '''
        Retrieve remote addon metadata
        '''
        metadata = None

        try:

            def get(url, **kwargs):
                if github.api.assert_github_api_url(url):
                    # Get the metadata of the github release from api
                    # since metadata of the download link might not be consistent
                    return self.__gh_session.head(url, **kwargs)
                else:
                    return requests.head(url, **kwargs)

            response = get(addon.base.uri, **kwargs)

            if response is not None:

                # detect redirect
                if 'location' in response.headers:
                    response = get(response.headers['location'], **kwargs)

                metadata = AddonMetadata(
                    uri=addon.base.uri,
                    etag=response.headers.get('etag', ''),
                    last_modified=response.headers.get('last-modified', '')
                )

        except RequestException as req_ex:
            logger().error(req_ex)
        except HTTPError as http_ex:
            logger().error(http_ex)
        except TimeoutError as timeout_ex:
            logger().error(timeout_ex)
        except GitHubException as ex:
            logger().error(ex)

        if metadata is None:
            metadata = AddonMetadata()

        return metadata

    def __save_metadata(self, metadata: AddonMetadata, path: Path):
        logger().info(msg=f"Saving addon metadata to {path}")
        if not path.parent.exists():
            makedirs(path.parent)
        write_json(metadata.to_json(), path)

    def __download_addon(self, addon: Addon, **kwargs) -> Response:

        response = None

        try:

            download_uri = None
            if github.api.assert_latest_release_url(addon.base.uri):
                download_uri = github.api.fetch_latest_release_download_url(
                    addon.base.uri, self.__gh_session, **kwargs
                )
            else:
                download_uri = addon.base.uri

            response = requests.get(download_uri, **kwargs)

        except RequestException as req_ex:
            logger().error(req_ex)
        except HTTPError as http_ex:
            logger().error(http_ex)
        except TimeoutError as timeout_ex:
            logger().error(timeout_ex)
        except GitHubException as ex:
            logger().error(ex)

        return response

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
            logger().info(msg=f"Skipping {addon.base.name}({addon.binding.path.name}) update...")

        return ret_code

    def __update_addon_internal(self, addon: Addon, force: bool = False) -> UpdateResult:

        ret_code = UpdateResult.NONE

        default_headers = {
            'cache-control': 'no-cache',
            'pragma': 'no-cache'
        }

        # check HASH / SIGNATURE before downloading the resource
        logger().info(msg=f"Fetching {addon.base.name}({addon.binding.path.name}) metadata...")

        metadata = self.get_metadata(addon)
        remote_metadata = self.get_remote_metadata(addon, timeout=10, allow_redirects=True, headers=default_headers)

        # ETAG is apparently inconsistent for latest release in github api
        # so the check is currently only done by means of the <last-modified> HTTP header tag
        if len(metadata.last_modified) == 0 or remote_metadata.last_modified != metadata.last_modified or force:

            logger().info(msg="Local and remote metadata mismatch or empty.")

            logger().info(msg=f"Downloading {addon.base.name}({addon.binding.path.name})...")

            response = self.__download_addon(addon, timeout=10, allow_redirects=True, headers=default_headers)

            if response is not None:

                logger().info(msg=f"Downloaded {addon.base.name}.")

                # checking the hash signature as well as to not update needessly
                # since remote metadata might be lacking in some cases
                [ret_code, remote_metadata.hash_signature] = SignatureChecker.check_signatures(response.content, addon, metadata)

                if ret_code == UpdateResult.TO_CREATE or ret_code == UpdateResult.TO_UPDATE or force:

                    logger().info(msg=ret_code.message(addon))

                    if responses.is_zip_content(response):
                        uploader = ZipUpdater(ret_code)
                        uploader.namings = self.namings.get(addon.base.name, dict())
                        ret_code = uploader.update_from_zip(response, addon)
                        remote_metadata.namings = uploader.namings
                    else:
                        uploader = DatastreamUpdater(ret_code)
                        uploader.namings = self.namings.get(addon.base.name, dict())
                        if addon.base.uri_info.is_installer:
                            ret_code = uploader.update_from_installer(response, addon)
                        else:
                            ret_code = uploader.update_from_datastream(response, addon)
                        remote_metadata.namings = uploader.namings

                    logger().info(msg=ret_code.message(addon))

                # local metadata must be updated if:
                # - an addon has been created or updated
                # - addon metadatas don't match but the addon signatures do
                if ret_code in [UpdateResult.CREATED, UpdateResult.UPDATED, UpdateResult.UP_TO_DATE]:
                    self.__save_metadata(remote_metadata, Path(metadata.uri))
            else:
                logger().error(msg="Received invalid response from addon update uri. Skipping...")
                ret_code = UpdateResult.DOWNLOAD_FAILED
        else:
            logger().info(msg="Local and remote metadata match.")
            ret_code = UpdateResult.UP_TO_DATE

        return ret_code
