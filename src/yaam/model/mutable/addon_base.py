'''
Addon base module
'''
from typing import List
from yaam.model.mutable.uri_info import UriInfo
from yaam.utils.json.jsonkin import Jsonkin

class AddonBase(Jsonkin):
    '''
    Base Addon class
    '''

    def __init__(self,
        name: str = str(),
        uri: str = str(),
        uri_info: UriInfo = None,
        description: str = str(),
        contribs: List[str] = None,
        dependencies: List[str] = None,
        chainloads: List[str] = None,
        is_shader: bool = False):

        self._name = name
        self._uri = uri
        self._uri_info = uri_info
        self._description = description
        self._contributors: List[str] = contribs if contribs else list()
        self._dependencies: List[str] = dependencies if dependencies else list()
        self._chainloads: List[str] = chainloads if chainloads else list()

        self._is_shader = is_shader

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, o: object) -> bool:
        if issubclass(type(o), AddonBase):
            return hash(self) == hash(o)
        elif isinstance(o, str):
            return self._name == o

        return super().__eq__(o)

    @property
    def name(self) -> str:
        '''
        The name of the addon
        '''
        return self._name

    @property
    def uri(self) -> str:
        '''
        The uri of the addon
        '''
        return self._uri

    @property
    def uri_info(self) -> UriInfo:
        '''
        Return useful info about the URI
        '''
        return self._uri_info

    @property
    def description(self) -> str:
        '''
        A description of the addon
        '''
        return self._description

    @property
    def contributors(self) -> List[str]:
        '''
        A list of people which contribued to the addon development
        '''
        return self._contributors

    @property
    def dependencies(self) -> List[str]:
        '''
        A list of the addon dependencies.
        '''
        return self._dependencies

    @property
    def chainloads(self) -> List[str]:
        '''
        A list of the addon chainload-able names.
        '''
        return self._chainloads

    @property
    def is_shader(self)-> bool:
        '''
        Return whether this addon is a shader library or not
        '''
        return self._is_shader

    @name.setter
    def name(self, new_name: str) -> None:
        '''
        Set the addon name
        '''
        self._name = new_name

    @uri.setter
    def uri(self, new_uri: str) -> None:
        '''
        Set the addon update url
        '''
        self._uri = new_uri

    @description.setter
    def description(self, new_description: str) -> None:
        '''
        Set the addon description
        '''
        self._description = new_description

    @contributors.setter
    def contributors(self, contribs: List[str]):
        '''
        Set the list of contributors
        '''
        self._contributors = contribs

    @dependencies.setter
    def dependencies(self, dependencies: List[str]):
        '''
        Set the list of dependencies
        '''
        self._dependencies = dependencies

    @chainloads.setter
    def chainloads(self, chainloads: List[str]):
        '''
        Set the list of chainload-able names
        '''
        self._chainloads = chainloads

    @is_shader.setter
    def is_shader(self, is_shader: bool):
        '''
        Set if this addon represents a shader library or not
        '''
        self._is_shader = is_shader

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Return this class object from dict representation
        '''
        return AddonBase(
            name=json_obj['name'],
            uri=json_obj.get('uri', None),
            uri_info=UriInfo.from_json(json_obj.get('uri_info', dict())),
            description=json_obj.get('description', ""),
            contribs=json_obj.get('contribs', []),
            dependencies=json_obj.get('dependencies', []),
            chainloads=json_obj.get('chainloads', []),
            is_shader=json_obj.get('is_shader', False)
        )

    def to_json(self) -> dict:
        '''
        Map the json rapresentation into an object of this class
        '''
        return {
            'name': self.name,
            'uri': self.uri,
            'uri_info': self.uri_info.to_json(),
            'description': self.description,
            'contribs': self.contributors,
            'dependencies': self.dependencies,
            'chainloads': self.chainloads,
            'is_shader': self.is_shader
        }
