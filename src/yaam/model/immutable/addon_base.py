'''
Addon module
'''
from typing import List
from yaam.model.binding_type import BindingType

class AddonBase(object):
    '''
    Immutable Base Addon Class
    '''
    def __init__(self,
        name: str,
        update_url: str = str(),
        descr: str = str(),
        contribs: List[str] = None,
        dependencies: List[str] = None,
        default_binding_type: BindingType = BindingType.AGNOSTIC):

        self._name = name
        self._update_url = update_url
        self._descr = descr
        self._contributors: List[str] = contribs if contribs else list()
        self._decependencies: List[str] = dependencies if dependencies else list()
        self._default_binding_type: BindingType = default_binding_type

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
    def update_url(self) -> str:
        '''
        The update_url of the addon
        '''
        return self._update_url

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
    def dependencies(self):
        '''
        A list of the addon dependencies. Addons that must exists in the addon has to work.
        '''
        return self._decependencies
    
    @property
    def default_binding(self):
        '''
        Return the addon native binding type
        '''
        return self._default_binding_type

    @staticmethod
    def from_dict(json: dict, default_binding_type: BindingType = BindingType.AGNOSTIC):
        '''
        Return this class object from dict representation
        '''
        return AddonBase(
            json['name'],
            json['uri'] if 'uri' in json else "",
            json['description'] if 'description' in json else "",
            json['contribs'] if 'contribs' in json else [],
            default_binding_type
        )
