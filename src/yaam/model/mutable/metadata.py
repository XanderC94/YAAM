'''
Addon metadata class module
'''
from typing import Dict
from yaam.model.type.binding import BindingType
from yaam.utils.json.jsonkin import Jsonkin


class AddonMetadata(Jsonkin):
    '''
    Addon Meta-data class
    '''

    def __init__(
                self,
                addon: str = '',
                uri: str = '',
                etag: str = '',
                last_modified: str = '',
                hash_signature: str = '',
                naming_map: Dict[BindingType, Dict[str, str]] = None
            ) -> None:

        self.addon = addon
        self.etag = etag
        self.last_modified = last_modified
        self.hash_signature = hash_signature
        self.uri = uri
        self.namings: Dict[BindingType, Dict[str, str]] = naming_map if naming_map is not None else dict()

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Create object representation of this class from dict representation
        '''
        namings = dict()
        for _ in json_obj.get('namings', list()):
            binding_type = BindingType.from_string(_.get('type', 'None'))
            namings[binding_type] = _.get('naming', dict())

        return AddonMetadata(
            addon=json_obj.get('addon', ''),
            etag=json_obj.get('etag', ''),
            last_modified=json_obj.get('last_modified', ''),
            hash_signature=json_obj.get('hash_signature', ''),
            naming_map=namings
        )

    def to_json(self) -> dict:
        '''
        Map the json rapresentation into an object of this class
        '''
        namings = list()

        for (key, value) in self.namings.items():
            namings.append({'type': key.signature, 'naming': dict([(str(o), str(n)) for (o, n) in value.items()])})

        return {
            'addon': self.addon,
            'etag': self.etag,
            'last_modified': self.last_modified,
            'hash_signature': self.hash_signature,
            'namings': namings
        }
