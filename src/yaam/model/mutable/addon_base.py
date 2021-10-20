'''
Addon base module
'''
from typing import List

class AddonBase(object):
    '''
    Base Addon class
    '''

    def __init__(self,
        name: str,
        uri: str = str(),
        descr: str = str(),
        contribs: List[str] = None,
        dependencies: List[str] = None,
        is_shader: bool = False):

        self._name = name
        self._uri = uri
        self._descr = descr
        self._contributors: List[str] = contribs if contribs else list()
        self._dependencies: List[str] = dependencies if dependencies else list()

        self._is_shader = is_shader

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        if issubclass(type(o), AddonBase):
            return self.__hash__() == o.__hash__()
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
    def description(self) -> str:
        '''
        A description of the addon
        '''
        return self._descr

    @property
    def contributors(self) -> List[str]:
        '''
        A list of people which contribued to the addon development
        '''
        return self._contributors

    @property
    def dependencies(self) -> List[str]:
        '''
        A list of the addon dependencies. Addons that must exists in the addon has to work.
        '''
        return self._dependencies

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
        self._descr = new_description

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

    def set_shader(self, is_shader: bool):
        '''
        Set if this addon represents a shader library or not
        '''
        self._is_shader = is_shader

    @staticmethod
    def from_dict(json_obj: dict):
        '''
        Return this class object from dict representation
        '''
        return AddonBase(
            name=json_obj['name'],
            uri=json_obj.get('uri', None),
            descr=json_obj.get('description', ""),
            contribs=json_obj.get('contribs', []),
            dependencies=json_obj.get('dependencies', []),
            is_shader=json_obj.get('is_shader', False)
        )
