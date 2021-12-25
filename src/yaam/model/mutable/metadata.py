'''
Addon metadata class module
'''
from yaam.utils.json.jsonkin import Jsonkin

class AddonMetadata(Jsonkin):
    '''
    Addon Meta-data class
    '''

    def __init__(self,
        uri: str = '',
        etag: str = '',
        last_modified: str = '',
        hash_signature: str = '') -> None:

        self.etag = etag
        self.last_modified = last_modified
        self.hash_signature = hash_signature
        self.uri = uri

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Create object representation of this class from dict representation
        '''
        return AddonMetadata(
            etag=json_obj.get('etag', ''),
            last_modified=json_obj.get('last_modified', ''),
            hash_signature=json_obj.get('hash_signature', '')
        )

    def to_json(self):
        '''
        Map the json rapresentation into an object of this class
        '''
        return {
            'etag': self.etag,
            'last_modified': self.last_modified,
            'hash_signature': self.hash_signature
        }
