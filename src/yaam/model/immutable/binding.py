'''
Binding model module
'''
from pathlib import Path
from yaam.model.type.binding import BindingType

class Binding(object):
    '''
    Immutable Addon binding model
    '''

    def __init__(self,
        name: str, path: Path = Path(),
        enabled: bool = False, updateable: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):

        self._name = name
        self._path = path
        self._enabled = enabled
        self._updateable = updateable
        self._binding_type = binding_type

    def __hash__(self) -> int:
        return hash((self.name, self.typing))

    @property
    def name(self) -> str:
        '''
        Returns the Addon name
        '''
        return self._name

    @property
    def path(self) -> Path:
        '''
        Returns the addon path
        '''
        return self._path

    @property
    def updateable(self) -> bool:
        '''
        Returns whether or not this addon should be updated
        '''
        return self._updateable

    @property
    def enabled(self) -> bool:
        '''
        Returns whether or not this addon is enabled
        '''
        return self._enabled

    @property
    def typing(self) -> BindingType:
        '''
        Returns the addon binding type
        '''
        return self._binding_type

    def is_dll(self) -> bool:
        '''
        Returns whether this addon is a .dll or not
        '''
        return self._path.suffix == ".dll"

    def is_exe(self) -> bool:
        '''
        Return whether this addon is an .exe or not
        '''
        return self._path.suffix == ".exe"

    @staticmethod
    def from_dict(json_obj:dict, binding_type: BindingType):
        '''
        Create object representation of this class from dict representation
        '''
        return Binding(
            json_obj["name"],
            Path(json_obj.get("path", "")),
            json_obj.get("enabled", False),
            json_obj.get("update", False),
            binding_type
        )
