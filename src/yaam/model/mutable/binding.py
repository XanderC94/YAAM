'''
Binding model module
'''
from pathlib import Path
from yaam.model.type.binding import BindingType
from yaam.model.immutable.binding import Binding

class MutableBinding(Binding):
    '''
    Mutable Addon binding model
    '''

    def __init__(self,
        name: str, path: Path = Path(),
        enabled: bool = False, updateable: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):
        
        super().__init__(
            name=name,
            path=path,
            enabled=enabled,
            updateable=updateable,
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

    @Binding.updateable.setter
    def updateable(self, updateable : bool):
        '''
        Set whether or not this addon should be updated
        '''
        self._updateable = updateable

    @Binding.enabled.setter
    def enabled(self, enabled : bool) -> str:
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

    @staticmethod
    def from_dict(json_obj:dict, binding_type: BindingType):
        '''
        Create object representation of this class from dict representation
        '''
        return MutableBinding(
            json_obj["name"],
            Path(json_obj.get("path", "")),
            json_obj.get("enabled", False),
            json_obj.get("update", False),
            binding_type
        )