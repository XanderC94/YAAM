'''
Web Assets modules
'''

from typing import List
from yaam.utils.counter import ForwardCounter
from yaam.utils.exceptions import AssetException
from yaam.utils.json.jsonkin import Jsonkin
from yaam.utils.uri import URI


class Asset(Jsonkin):
    '''
    Web resource downloadable asset
    '''

    def __init__(self, name: str, url: URI) -> None:
        self.name = name
        self.download_url = url

    def to_json(self) -> dict:
        return vars(self)


class Release(Jsonkin):
    '''
    Web resource release data
    '''

    def __init__(self, name: str, tag: str, timestamp: str, is_draft: bool, is_prerelease: bool, assets: List[Asset]) -> None:
        self.name = name
        self.tag = tag
        self.timestamp = timestamp
        self.is_draft = is_draft
        self.is_prerelease = is_prerelease
        self.assets = assets

    def to_json(self) -> dict:
        return vars(self)


def assets_followup(assets: List[Asset]) -> URI:
    download_uri = None

    if len(assets) == 1:
        download_uri = assets[0].download_url
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
            download_uri = assets[int(choice) - 1].download_url
        else:
            raise AssetException("Skipped resource download by user...")
    else:
        raise AssetException("URL pointing to invalid or empty latest release!")

    return download_uri
