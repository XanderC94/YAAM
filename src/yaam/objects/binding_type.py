from enum import Enum
from typing import Set

class BindingType(Enum):

    AGNOSTIC = (-1, set())
    EXE = (0, set(["exe"]))
    DXGI_9 = (1, set(["dx9", "dxgi9", "d3d9"]))
    DXGI_11 = (2, set(["dx11", "dxgi11", "d3d11"]))
    DXGI_12 = (3, set(["dx12", "dxgi", "dxgi12", "d3d12"]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, BindingType):
            return self.value == o.value
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def aliases(self) -> Set[str]:
        return self.content[1]

    @property
    def value(self) -> int:
        return self.content[0]

    @property
    def content(self) -> tuple:
        return super().value

    @staticmethod
    def from_string(str_repr: str):

        render = BindingType.AGNOSTIC

        for r in BindingType:
            if str_repr == r.name or str_repr in r.aliases:
                render = r
                break
        
        return render