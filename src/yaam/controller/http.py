'''

HTTP Requests manager class module

'''

# from pathlib import Path
from typing import Callable, List, Union
# from typing import Optional, Tuple

import requests

from yaam.model.appconfig import AppConfig
from yaam.model.options import Option
from yaam.utils.github import Github as GithubAPI
from yaam.utils.exceptions import GitHubException
from yaam.utils.logger import static_logger as logger
from yaam.utils.uri import URI
from yaam.utils.webasset import Release


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
            self.__gh_session = GithubAPI.open_session(self.__gh_user, self.__gh_api_token)

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
            if GithubAPI.assert_latest_release_url(url) or GithubAPI.assert_release_list_url(url):
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
            if GithubAPI.assert_latest_release_url(url) or GithubAPI.assert_release_list_url(url):
                response = self.__gh_session.head(url, **kwargs)
            else:
                response = self.__web_session.head(url, **kwargs)
            return response

        return self.__request_wrapper(__head_internal)

    def get_downloadable_assets(self, url: URI, **kwargs) -> List[Union[Release, URI]]:
        '''
        HTTP GET <URL> <ARG>

        first checks if the provided link is a GITHUB API link
        and recover the latest release download link
        '''

        releases = []

        if GithubAPI.assert_release_list_url(url):

            if GithubAPI.assert_latest_release_url(url):
                # releases.append(GithubAPI.fetch_latest_release_assets(url, self.__gh_session, **kwargs))
                url = url.parent()

            releases = GithubAPI.fetch_release_list_assets(url, self.__gh_session, **kwargs)

        else:
            releases.append(url)

        return releases
