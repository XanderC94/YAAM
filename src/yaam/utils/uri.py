'''
URI class module
'''
from furl import furl
import yaam.utils.validators.url as validators


class URI(furl):
    '''
    URI wrapper class implementation
    '''

    def __init__(self, uri: str = None, **kwargs) -> None:
        super().__init__(uri, **kwargs)

    def __str__(self) -> str:
        return self.tostr()

    def is_valid(self) -> bool:
        '''
        Returns whether the contained URI is a valid one
        '''
        return validators.url(str(self))
