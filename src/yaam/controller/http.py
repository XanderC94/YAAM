'''
Http Requests manager class module
'''

from typing import Callable
import requests
from yaam.utils import github
from yaam.utils.exceptions import GitHubException
from yaam.utils.logger import static_logger as logger
from yaam.model.config import AppConfig
from yaam.model.options import Option

class HttpRequestManager(object):
    '''
    Http requests manager class
    '''

    def __init__(self, config: AppConfig) -> None:
        self.__config = config
        self.__gh_session : requests.Session = None
        self.__gh_user = self.__config.get_property(Option.GITHUB_USER)
        self.__gh_api_token = self.__config.get_property(Option.GITHUB_API_TOKEN)

    def __enter__(self):
        self.init_sessions()
        return self

    def __exit__(self, type, value, traceback):
        self.close_sessions()

    def init_sessions(self):
        if self.__gh_session is None:
            self.__gh_session = github.api.open_session(self.__gh_user, self.__gh_api_token)

    def close_sessions(self):
        if self.__gh_session is not None:
            self.__gh_session.close()

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

    def get(self, url: str, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARGS>
        '''
        def __get_internal() -> requests.Response:
            response = None
            if github.api.assert_latest_release_url(url):
                response = self.__gh_session.get(url, **kwargs)
            else:
                response = requests.get(url, **kwargs)
            return response

        return self.__request_wrapper(__get_internal)

    def head(self, url: str, **kwargs) -> requests.Response:
        '''
        HTTP HEAD <URL> <ARGS>
        '''
        def __head_internal() -> requests.Response:
            response = None
            if github.api.assert_latest_release_url(url):
                response = self.__gh_session.head(url, **kwargs)
            else:
                response = requests.head(url, **kwargs)
            return response

        return self.__request_wrapper(__head_internal)

    def get_download(self, url: str, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARG>

        first checks if the provided link is a GITHUB API link
        and recover the latest release download link
        '''

        download_uri = None
        if github.api.assert_latest_release_url(url):
            download_uri = github.api.fetch_latest_release_download_url(
                url, self.__gh_session, **kwargs
            )
        else:
            download_uri = url

        return self.get(download_uri, **kwargs)
        