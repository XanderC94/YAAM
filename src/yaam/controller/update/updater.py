'''
GW2SL update utility module
'''

from typing import Iterable
from requests.sessions import Session
from urllib3.exceptions import HTTPError
import requests
from requests.exceptions import RequestException
from yaam.controller.update.datastream_updater import DatastreamUpdater
from yaam.controller.update.results import UpdateResult
from yaam.controller.update.zip_updater import ZipUpdater
from yaam.model.config import AppConfig
from yaam.model.options import Option
from yaam.utils.exceptions import GitHubException
import yaam.utils.validators.url as validator
from yaam.utils.logger import static_logger as logger
from yaam.model.mutable.addon import Addon
from yaam.utils import github
import yaam.utils.response as responses

class AddonUpdater(object):
    '''
    Addon updater class
    '''

    def __init__(self, config: AppConfig) -> None:
        self.__config = config
        self.__gh_session : Session = None
        super().__init__()

    def update_addons(self, addons: Iterable[Addon]):
        '''
        Updates the provided addons

        @addons: list -- list of addons to updated
        '''

        gh_user = self.__config.get_property(Option.GITHUB_USER)
        gh_api_token = self.__config.get_property(Option.GITHUB_API_TOKEN)

        self.__gh_session = github.api.open_session(gh_user, gh_api_token)

        for addon in addons:
            self.update_addon(addon)

        self.__gh_session.close()

    def update_addon(self, addon: Addon):
        '''
        Update the provided addon if specified and when possible

        @addon: Addon -- addon to updated
        '''
        ret_code = UpdateResult.NONE

        ret_code = self.__update_addon(addon)

        # Add other types and checks on the ret code ...

        return ret_code

    def __update_addon(self, addon: Addon):
        '''
        Addon update routine
        '''
        ret_code = UpdateResult.NONE

        logger().debug(msg=f"{addon.base.name}({addon.binding.path.name})")

        if not addon.binding.is_enabled:
            ret_code = UpdateResult.DISABLED
        elif not validator.url(addon.base.uri):
            logger().info(msg=f"No valid update URL provided for {addon.base.name}({addon.binding.path.name}).")
            ret_code = UpdateResult.INVALID_URL
        else:

            try:

                req_headers = {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }

                download_uri = github.api.fetch_latest_release_download_url(
                    addon.base.uri, self.__gh_session, timeout=10, allow_redirects=True, headers=req_headers
                )

                response = requests.get(download_uri, timeout=10, allow_redirects=True, headers=req_headers)

            except RequestException as req_ex:
                logger().error(req_ex)
            except HTTPError as http_ex:
                logger().error(http_ex)
            except TimeoutError as timeout_ex:
                logger().error(timeout_ex)
            except GitHubException as ex:
                logger().error(ex)
            else:

                if responses.is_zip_content(response):
                    ret_code = ZipUpdater.update_from_zip(response, addon)
                else:
                    if addon.base.uri_info.is_installer:
                        ret_code = DatastreamUpdater.update_from_installer(response, addon)
                    else:
                        ret_code = DatastreamUpdater.update_from_datastream(response, addon)

        return ret_code
