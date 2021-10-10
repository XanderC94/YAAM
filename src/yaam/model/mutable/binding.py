'''
Binding model module
'''
from pathlib import Path
from yaam.model.binding_type import BindingType
from yaam.model.immutable.binding import Binding

class MutableBinding(Binding):
    '''
    Mutable Addon binding model
    '''

    def __init__(self,
        name: str, path: Path = Path(),
        enabled: bool = False, update: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):
        
        super().__init__(
            name=name,
            path=path,
            enabled=enabled,
            update=update,
            binding_type=binding_type
        )

    @Binding.name.setter
    def name(self, new_name : str):
        '''
        Set the Addon name
        '''
        self._name = new_name

    @Binding.path.setter
    def path(self, new_path : Path):
        '''
        Set the Addon path
        '''
        self._path = new_path

    @Binding.is_updateable.setter
    def is_updateable(self, update : bool):
        '''
        Set whether or not this addon should be updated
        '''
        self._update = update

    @Binding.is_enabled.setter
    def is_enabled(self, enabled : bool) -> str:
        '''
        Set whether or not this addon is enabled
        '''
        self._enabled = enabled

    @Binding.typing.setter
    def typing(self, new_binding : BindingType):
        '''
        Set the addon binding type
        '''
        self._binding_type = new_binding
