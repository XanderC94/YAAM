'''
HTTP Requests manager class module
'''

from typing import Callable, List
import requests
from yaam.utils import github
from yaam.utils.counter import ForwardCounter
from yaam.utils.exceptions import GitHubException
from yaam.utils.logger import static_logger as logger
from yaam.model.appconfig import AppConfig
from yaam.model.options import Option
from yaam.utils.uri import URI


class HttpRequestManager(object):
    '''
    Http requests manager class
    '''

    def __init__(self, config: AppConfig) -> None:
        self.__config: AppConfig = config
        self.__web_session: requests.Session = None
        self.__gh_session: requests.Session = None
        self.__gh_user = self.__config.get_property(Option.GITHUB_USER)
        self.__gh_api_token = self.__config.get_property(Option.GITHUB_API_TOKEN)

    def __enter__(self):
        self.init_sessions()
        return self

    def __exit__(self, typing, value, traceback):
        self.close_sessions()

    def init_sessions(self):
        '''
        Start HTTP sessions
        '''
        if self.__gh_session is None:
            self.__gh_session = github.API.open_session(self.__gh_user, self.__gh_api_token)

        if self.__web_session is None:
            self.__web_session = requests.Session()

    def close_sessions(self):
        '''
        End HTTP sessions
        '''
        if self.__gh_session is not None:
            self.__gh_session.close()

        if self.__web_session is not None:
            self.__web_session.close()

    def __request_wrapper(self, func: Callable[[], requests.Response]) -> requests.Response:
        response = None

        try:
            response = func()
        except requests.HTTPError as http_ex:
            logger().error(http_ex)
        except requests.RequestException as req_ex:
            logger().error(req_ex)
        except TimeoutError as timeout_ex:
            logger().error(timeout_ex)
        except GitHubException as ex:
            logger().error(ex)

        return response

    def get(self, url: URI, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARGS>
        '''
        def __get_internal() -> requests.Response:
            response = None
            if github.API.assert_latest_release_url(url):
                response = self.__gh_session.get(url, **kwargs)
            else:
                response = self.__web_session.get(url, **kwargs)
            return response

        return self.__request_wrapper(__get_internal)

    def head(self, url: URI, **kwargs) -> requests.Response:
        '''
        HTTP HEAD <URL> <ARGS>
        '''
        def __head_internal() -> requests.Response:
            response = None
            if github.API.assert_latest_release_url(url):
                response = self.__gh_session.head(url, **kwargs)
            else:
                response = self.__web_session.head(url, **kwargs)
            return response

        return self.__request_wrapper(__head_internal)

    def __assets_followup(self, assets: List[github.Asset]) -> URI:
        download_uri = None

        if len(assets) == 1:
            download_uri = assets[0].browser_download_url
        elif len(assets) > 1:
            # Since download are too much etherogeneous
            # I can only let the user choose the desired resource
            # to be downloaded
            print(f"Found {len(assets)} resources:\n")

            i = ForwardCounter()
            for _ in assets:
                print(f"{i.next()}. {_.name}")

            print()

            choice = input(f"Which one should be downloaded? Choose between [1, ..., {i}, n = skip]: ")
            if choice.isnumeric() and int(choice) > 0 and int(choice) < (i + 1):
                download_uri = assets[int(choice) - 1].browser_download_url
            else:
                raise GitHubException("Skipped resource download by user...")
        else:
            raise GitHubException("Github API pointing to invalid or empty latest release!")

        return download_uri

    def get_download(self, url: URI, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARG>

        first checks if the provided link is a GITHUB API link
        and recover the latest release download link
        '''

        download_uri = None
        if github.API.assert_latest_release_url(url):
            assets = github.API.fetch_latest_release_assets(url, self.__gh_session, **kwargs)
            download_uri = self.__assets_followup(assets)
        else:
            download_uri = url

        return self.get(download_uri, **kwargs) if download_uri is not None else None
