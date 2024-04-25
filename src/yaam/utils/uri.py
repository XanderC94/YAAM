'''
URI class module
'''
import os
from pathlib import Path as OSPath, PureWindowsPath
from furl import furl
# from furl import Path as URIPath
import yaam.utils.validators.url as validators


class URI(furl):
    '''
    URI wrapper class implementation
    '''

    def __init__(self, uri: str = None, **kwargs) -> None:
        super().__init__(uri, **kwargs)

    def __str__(self) -> str:
        return self.tostr()

    def parent(self):
        '''
        Returns the parent URI
        '''

        new_uri = self.copy()
        path = os.path.normpath(str(OSPath(self.pathstr).parent))
        path = PureWindowsPath(path).as_posix()
        new_uri.path = path

        return new_uri

    def is_valid(self) -> bool:
        '''
        Returns whether the contained URI is a valid one
        '''
        return validators.url(str(self))
