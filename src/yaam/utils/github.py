'''
Github API helper module
'''

import re
from typing import List, Union
import requests
# from requests.sessions import Session
from yaam.utils.json.jsonkin import Jsonkin
from yaam.utils.logger import static_logger as logger

from yaam.utils.exceptions import GitHubException
from yaam.utils.uri import URI
from yaam.utils.webasset import Asset, Release


class GithubAsset(Asset):
    '''
    GitHub API download asset
    '''

    @staticmethod
    def from_json(json_obj: dict) -> Asset:
        '''
        Return ad Asset instence from its json repr
        '''
        return Asset(
            name=json_obj.get('name', str()),
            url=URI(json_obj.get('browser_download_url', None))
        )


class GithubRelease(Jsonkin):
    '''
    GitHub API release data
    '''

    @staticmethod
    def from_json(json_obj: dict) -> Release:
        '''
        Return ad Release instence from its json repr
        '''
        return Release(
            name=json_obj.get('name', str()),
            tag=json_obj.get('tag_name', str()),
            timestamp=json_obj.get('published_at', str()),
            is_draft=json_obj.get('draft', False),
            is_prerelease=json_obj.get('prerelease', False),
            assets=[GithubAsset.from_json(_) for _ in json_obj.get('assets', list()) if "browser_download_url" in _]
        )


class Github(object):
    '''
    github api static class
    '''

    def __init__(self, user: str = str(), token: str = str(), header: dict = None) -> None:
        self.__user = user
        self.__api_access_token = token
        # self.__root = URI("https://api.github.com")

        self.__header = header if header is not None else dict()

        self.__init_header(self.__user, self.__api_access_token)

    def __init_header(self, user: str = str(), token: str = str()):

        if len(user) > 0 and len(token) > 0:
            self.__header.update({
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {token}',
                'X-GitHub-Api-Version': '2022-11-28'
            })

    def __prepare_args(self, **kwargs) -> dict:

        args = dict(**kwargs)

        if 'headers' in args:
            args['headers'].update(self.__header)
        else:
            args['headers'] = self.__header

        return args

    @staticmethod
    def open_session(user: str = str(), token: str = str()):
        '''
        Create github api session
        '''

        return Github(user, token)

    @staticmethod
    def assert_api_url(url: URI):
        '''
        Assert whether the given url matches
        https://api.github.com/(.+)
        '''
        api_github_regex = r"https:\/\/api\.github\.com\/(.+)"
        return re.match(api_github_regex, str(url)) is not None

    @staticmethod
    def assert_latest_release_url(url: URI):
        '''
        Assert whether the given url matches
        https://api.github.com/repos/(.+)/releases/latest
        '''
        api_github_latest_release_regex = r"https:\/\/api\.github\.com\/repos\/(.+)\/releases\/latest"
        return re.match(api_github_latest_release_regex, str(url)) is not None

    @staticmethod
    def assert_release_list_url(url: URI):
        '''
        Assert whether the given url matches
        https://api.github.com/repos/(.+)/releases
        '''
        api_github_release_list_regex = r"https:\/\/api\.github\.com\/repos\/(.+)\/releases"
        return re.match(api_github_release_list_regex, str(url)) is not None

    def get(self, url: URI, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARGS>
        '''

        args = self.__prepare_args(**kwargs)

        return requests.get(url, **args)  # pylint: disable=W3101

    def head(self, url: URI, **kwargs) -> requests.Response:
        '''
        HTTP GET <URL> <ARGS>
        '''

        args = self.__prepare_args(**kwargs)

        return requests.head(url, **args)  # pylint: disable=W3101

    def __fetch_release_raw_assets(self, url: URI, **kwargs) -> Union[dict, list]:
        '''
        ...
        '''

        raw_assets = dict()

        response = self.get(url, **kwargs)  # pylint: disable=W3101

        logger().warning(msg=f"x-ratelimit-remaining: {response.headers.get('x-ratelimit-remaining', -1)}")
        logger().warning(msg=f"x-ratelimit-used: {response.headers.get('x-ratelimit-used', -1)}")
        logger().warning(msg=f"x-ratelimit-reset: {response.headers.get('x-ratelimit-reset', -1)}")

        if response.status_code is [200, 206]:

            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:

                raw_assets: dict = response.json()

            else:
                raise GitHubException("Github API response not in JSON format")
        else:
            raise GitHubException(f"Github API response returned with status code {response.status_code}")

        return raw_assets

    def fetch_latest_release_assets(self, url: URI, **kwargs) -> Release:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        release = None

        if self.assert_latest_release_url(url):

            raw_assets = self.__fetch_release_raw_assets(url, **kwargs)

            if isinstance(raw_assets, dict):
                tmp: Release = GithubRelease.from_json(raw_assets)

                if len(tmp.assets) > 0:
                    release = tmp
        else:
            raise GitHubException("Provided url is not a valid github api request for a latest release metadata")

        return release

    def fetch_release_list_assets(self, url: URI, **kwargs) -> List[Release]:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        target_releases = list()

        if self.assert_release_list_url(url):

            raw_assets = self.__fetch_release_raw_assets(url, **kwargs)

            if isinstance(raw_assets, list):

                raw_assets = sorted(raw_assets, key=lambda x: x['published_at'], reverse=True)

                for raw_release_asset in raw_assets:

                    release_asset: Release = GithubRelease.from_json(raw_release_asset)

                    if len(release_asset.assets) > 0:
                        target_releases.append(release_asset)
        else:
            raise GitHubException("Provided url is not a valid github api request for a release list metadata")

        return target_releases
