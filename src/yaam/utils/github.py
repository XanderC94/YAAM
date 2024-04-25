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

    @staticmethod
    def open_session(user: str = str(), token: str = str()):
        '''
        Create github api session
        '''
        github = requests.Session()
        if len(user) > 0 and len(token) > 0:
            github.auth = (user, token)

        return github

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

    @staticmethod
    def fetch_latest_release_assets(url: URI, github: Session, **kwargs) -> Release:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        release = None

        if Github.assert_latest_release_url(url):

            response = github.get(url, **kwargs)

            logger().debug(msg=f"x-ratelimit-remaining: {response.headers.get('x-ratelimit-remaining', -1)}")
            logger().debug(msg=f"x-ratelimit-used: {response.headers.get('x-ratelimit-used', -1)}")

            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:

                json_data: dict = response.json()

                tmp: Release = GithubRelease.from_json(json_data)

                if len(tmp.assets) > 0:
                    release = tmp
            else:
                raise GitHubException("Github API response not in JSON format")

        return release

    @staticmethod
    def fetch_release_list_assets(url: URI, github: Session, **kwargs) -> List[Release]:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        target_releases = list()

        if Github.assert_release_list_url(url):

            response = github.get(url, **kwargs)

            logger().debug(msg=f"x-ratelimit-remaining: {response.headers.get('x-ratelimit-remaining', -1)}")
            logger().debug(msg=f"x-ratelimit-used: {response.headers.get('x-ratelimit-used', -1)}")

            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:

                json_data: dict = response.json()

                if isinstance(json_data, list):

                    json_data = sorted(json_data, key=lambda x: x['published_at'], reverse=True)

                    for release_json in json_data:

                        release_obj: Release = GithubRelease.from_json(release_json)

                        if len(release_obj.assets) > 0:
                            target_releases.append(release_obj)
            else:
                raise GitHubException("Github API response not in JSON format")

        return target_releases
