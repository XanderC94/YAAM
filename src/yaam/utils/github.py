'''
Github API helper module
'''

import re
import requests
from requests.sessions import Session
from yaam.utils.logger import static_logger as logger

from yaam.utils.exceptions import GitHubException

class api(object):
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
    def fetch_latest_release_download_url(url: str, github: Session, **kwargs) -> str:
        '''
        Assert if url is a github api request for a latest release metadata
        and return the 'browser_download_url' link

        If it's not a github api request, returns the provided url.
        If it's a github api request but no valid metadata is found, raise Exception

        '''
        target_uri = url

        if api.assert_latest_release_url(url):
            response = github.get(url, **kwargs)

            logger().debug(msg=f"x-ratelimit-remaining: {response.headers.get('x-ratelimit-remaining', -1)}")
            logger().debug(msg=f"x-ratelimit-used: {response.headers.get('x-ratelimit-used', -1)}")

            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:

                json_data : dict = response.json()

                if 'assets' in json_data.keys():

                    if len(json_data['assets']) == 1 and 'browser_download_url' in json_data['assets'][0]:

                        target_uri = json_data['assets'][0]['browser_download_url']

                    elif len(json_data['assets']) > 0:

                        valid_assets = []
                        for asset in json_data['assets']:
                            if 'browser_download_url' in asset:
                                valid_assets.append(asset)

                        # Since download are too much etherogeneous
                        # I can only let the user choose the desired resource
                        # to be downloaded
                        print(f"Found {len(valid_assets)} resources:\n")

                        i : int = 0
                        for asset in valid_assets:
                            print(f"{i}. {asset['name']}")
                            i+=1

                        index = input(f"\nWhich one should be downloaded? Choose between [0, ..., {i - 1}]: ")
                        while not str(index).isnumeric() or int(index) < 0 or int(index) > i - 1:
                            index = input(f"\nChoose between [0, ..., {i - 1}]: ")

                        target_uri = valid_assets[int(index)]['browser_download_url']
                    else:
                        raise GitHubException("Github API pointing to invalid latest release!")
            else:
                raise GitHubException("Github API response not in JSON format")

        return target_uri
