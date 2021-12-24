'''
Uri info model class module
'''
from yaam.utils.json.jsonkin import Jsonkin

class UriInfo(Jsonkin):
    '''
    Addon base uri info class
    '''

    def __init__(self, is_installer : bool = False, is_offline = True) -> None:
        self._is_installer = is_installer
        self._is_offline = is_offline

    @property
    def is_installer(self) -> bool:
        '''
        Return if the companion uri points to an installer
        '''
        return self._is_installer

    @property
    def is_offline(self) -> bool:
        '''
        Return if the companion uri points to an offline installer
        '''
        return self._is_offline

    @is_installer.setter
    def is_installer(self, is_installer:bool) -> bool:
        '''
        Return if the companion uri points to an installer
        '''
        self._is_installer = is_installer

    @is_offline.setter
    def is_offline(self, is_offline:bool) -> bool:
        '''
        Return if the companion uri points to an offline installer
        '''
        self._is_offline = is_offline

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Return this class object from dict representation
        '''
        return UriInfo(
            is_installer=json_obj.get('is_installer', False),
            is_offline=json_obj.get('is_offline', True)
        )

    def to_json(self) -> dict:
        '''
        Map the json rapresentation into an object of this class
        '''
        return {
            'is_installer': self.is_installer,
            'is_offline': self.is_offline
        }
