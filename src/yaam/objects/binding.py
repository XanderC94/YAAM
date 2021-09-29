from pathlib import Path
from objects.binding_type import BindingType

class Binding:

    def __init__(self, name: str, path: Path, enabled: bool, update: bool, binding_type: BindingType):
        self._name = name
        self._path = path
        self._enabled = enabled
        self._update = update
        self._binding_type = binding_type
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def path(self) -> Path:
        return self._path

    @property
    def is_updateable(self) -> bool:
        return self._update

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @property
    def typing(self) -> BindingType:
        return self._binding_type

    def is_dll(self) -> bool:
        return self._path.suffix == ".dll"

    def is_exe(self) -> bool:
        return self._path.suffix == ".exe"

    @staticmethod
    def from_dict(json:dict, binding_type: BindingType):
        return Binding(
            json["name"],
            Path(json["path"]),
            json["enabled"] if "enabled" in json else False,
            json["update"] if "update" in json else False,
            binding_type
        )
