'''
Addon module
'''
from yaam.model.immutable.binding import Binding
from yaam.model.immutable.addon_base import AddonBase

class Addon(object):
    '''
    Immutable Addon incarnation class
    '''

    def __init__(self, base: AddonBase, binding: Binding):

        self._base = base
        self._binding = binding

    def __hash__(self) -> int:
        return hash((self._binding.name, self._binding.typing))

    def __eq__(self, o: object) -> bool:
        if issubclass(type(o), Addon):
            return self._base == o._base and self._binding == o._binding
        elif issubclass(type(o), AddonBase):
            return self._base == o
        elif issubclass(type(o), Binding):
            return self._binding.name == o.name
        elif isinstance(o, str):
            return self._base.name == o

        return super().__eq__(o)

    @property
    def base(self) -> AddonBase:
        '''
        Return the Addon Base object
        '''
        return self._base

    @property
    def binding(self) -> Binding:
        '''
        Return the Addon Binding object
        '''
        return self._binding

    @property
    def is_valid(self) -> bool:
        '''
        Return whether this addon has a valid configuration or not.
        Name should not be empty and the path should be an existing one.
        '''
        return len(self._base.name) and self._binding.path.exists()

    def to_table(self) -> dict:
        '''
        Return a partial dict repr of the addon
        '''
        table : dict = {}

        table['name'] = self._base.name
        table['path'] = self._binding.path.name
        table['update'] = self._binding.is_updateable
        table['enabled'] = self._binding.is_enabled

        return table
        