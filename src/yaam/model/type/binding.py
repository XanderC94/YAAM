'''
Binding types module
'''
from collections import namedtuple
from enum import Enum
from typing import Set

bindingtype = namedtuple(
    typename='bindingtype',
    field_names=['index', 'signature', 'aliases', 'can_shader', 'shader', 'suffix'],
    defaults=[int(), str(), list(), False, str(), str()]
)

class BindingType(Enum):
    '''
    Addon binary binding type
    '''
    NONE = bindingtype(0, "", set([""]))
    AGNOSTIC = bindingtype(1, "any", set(["agnostic", "none"]), can_shader=True)
    EXE = bindingtype(2, "exe", set(), suffix='.exe')
    D3D9 = bindingtype(3, "d3d9", set(["dx9"]), True, "dxgi", '.dll')
    D3D10 = bindingtype(4, "d3d10", set(["dx10"]), True, "dxgi", '.dll')
    D3D11 = bindingtype(5, "d3d11", set(["dx11"]), True, "dxgi", '.dll')
    D3D12 = bindingtype(6, "d3d12", set(["dx12"]), True, "dxgi", '.dll')
    VULKAN = bindingtype(7, "vulkan", set(["vk"]), True, "vk", '.dll')

    def __eq__(self, o: object) -> bool:
        if isinstance(o, BindingType):
            return self.index == o.index
        else:
            return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(self.index)

    @property
    def index(self) -> int:
        '''
        Return the integer value of the enumeration
        '''
        return super().value.index

    @property
    def signature(self) -> str:
        '''
        Return the preferred alias for the binding
        '''
        return self.value.signature

    @property
    def aliases(self) -> Set[str]:
        '''
        Return the possible aliases for the binding
        '''
        return self.value.aliases

    def can_shader(self) -> bool:
        '''
        Return whether this kind of binding can shader
        '''
        return self.value.can_shader

    @property
    def suffix(self) -> str:
        '''
        Return the file suffix for this binding type
        '''
        return self.value.suffix

    @property
    def shader(self) -> str:
        '''
        Return the preferred shader signature for this binding
        '''
        return self.value.shader

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        binding = BindingType.NONE

        for _ in BindingType:
            if str_repr == _.name or str_repr == _.signature or str_repr in _.aliases:
                binding = _
                break

        return binding
