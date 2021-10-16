'''
Mutable Addon module
'''
from yaam.model.mutable.binding import MutableBinding, Binding
from yaam.model.mutable.addon_base import MutableAddonBase, AddonBase

class MutableAddon(object):
    '''
    Mutable Addon incarnation class
    '''

    def __init__(self, base: MutableAddonBase, binding: MutableBinding):

        self._base = base
        self._binding = binding

    def __hash__(self) -> int:
        return hash((self._binding.name, self._binding.typing))

    def __eq__(self, o: object) -> bool:
        if issubclass(type(o), AddonBase):
            return self._base == o
        elif issubclass(type(o), Binding):
            return self._binding == o
        elif isinstance(o, str):
            return self._base.name == o

        return super().__eq__(o)

    @property
    def base(self) -> MutableAddonBase:
        '''
        Return the Addon Base object
        '''
        return self._base

    @property
    def binding(self) -> MutableBinding:
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
        table['update'] = self._binding.updateable
        table['enabled'] = self._binding.enabled

        return table
        
    