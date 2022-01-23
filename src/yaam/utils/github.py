'''
Github API helper module
'''

import re
from typing import List
import requests
from requests.sessions import Session
from yaam.utils.json.jsonkin import Jsonkin
from yaam.utils.logger import static_logger as logger

from yaam.utils.exceptions import GitHubException

class Asset(Jsonkin):
    '''
    GitHub API download asset
    '''

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.browser_download_url = url

    def to_json(self) -> dict:
        return vars(self)

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Return ad Asset instence from its json repr
        '''
        return Asset(
            name=json_obj.get('name', str()),
            url=json_obj.get('browser_download_url', str())
        )

class API(object):
    '''
    github api static class
    '''

    @staticmethod
    def open_session(user = str(), token = str()):
        '''
        Create github api session
        '''
        github = requests.Session()
        if len(user) > 0 and len(token) > 0:
            github.auth = (user, token)

        return github

    @staticmethod
    def assert_github_api_url(url: str):
        '''
        Assert whether the given url matches
        https://api.github.com/(.+)
        '''
        api_github_regex = r"https:\/\/api\.github\.com\/(.+)"
        return re.match(api_github_regex, url) is not None

    @staticmethod
    def assert_latest_release_url(url: str):
        '''
        Assert whether the given url matches
        https://api.github.com/repos/(.+)/releases/latest
        '''
        api_github_latest_release_regex = r"https:\/\/api\.github\.com\/repos\/(.+)\/releases\/latest"
        return re.match(api_github_latest_release_regex, url) is not None

    @staticmethod
    def fetch_latest_release_assets(url: str, github: Session, **kwargs) -> List[Asset]:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        target_uris = []

        if API.assert_latest_release_url(url):
            response = github.get(url, **kwargs)

            logger().debug(msg=f"x-ratelimit-remaining: {response.headers.get('x-ratelimit-remaining', -1)}")
            logger().debug(msg=f"x-ratelimit-used: {response.headers.get('x-ratelimit-used', -1)}")

            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:

                json_data : dict = response.json()

                for asset in json_data.get('assets', dict()):
                    if 'browser_download_url' in asset:
                        target_uris.append(Asset.from_json(asset))
            else:
                raise GitHubException("Github API response not in JSON format")

        return target_uris
