'''
Addon module
'''
from typing import List
from yaam.model.immutable.binding import Binding

class AddonBase(object):
    '''
    Immutable Base Addon Class
    '''
    def __init__(self,
        name: str, update_url: str = str(),
        descr: str = str(), contribs: List[str] = None):

        self._name = name
        self._update_url = update_url
        self._descr = descr
        self._contributors: List[str] = contribs if contribs else list()

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

    @staticmethod
    def from_dict(json: dict):
        '''
        Return this class object from dict representation
        '''
        return AddonBase(
            json['name'],
            json['uri'] if 'uri' in json else "",
            json['description'] if 'description' in json else "",
            json['contribs'] if 'contribs' in json else []
        )

class Addon(AddonBase, Binding):
    '''
    Immutable Addon incarnation class
    '''

    def __init__(self, base: AddonBase, binding: Binding):

        AddonBase.__init__(self,
            name=base.name,
            update_url=base.update_url,
            descr=base.description,
            contribs=base.contributors
        )

        Binding.__init__(self,
            name=base.name,
            path=binding.path,
            enabled=binding.is_enabled,
            update=binding.is_updateable,
            binding_type=binding.typing
        )

    def __hash__(self) -> int:
        return hash((self.name, self.typing))

    def __eq__(self, o: object) -> bool:

        if issubclass(type(o), Addon):
            return super().__eq__(o)
        elif issubclass(type(o), AddonBase):
            return self.name == o.name

        return super().__eq__(o)

    @property
    def is_valid(self) -> bool:
        '''
        Return whether this addon has a valid configuration or not.
        Name should not be empty and the path should be an existing one.
        '''
        return len(self.name) and self.path.exists()

    def to_table(self) -> dict:
        '''
        Return a partial dict repr of the addon
        '''
        table : dict = {}

        table['name'] = self.name
        table['path'] = self.path.name
        table['update'] = self.is_updateable
        table['enabled'] = self.is_enabled

        return table
        