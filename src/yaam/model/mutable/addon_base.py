'''
Addon module
'''
from typing import List
from yaam.model.binding_type import BindingType
from yaam.model.immutable.addon_base import AddonBase

class MutableAddonBase(AddonBase):
    '''
    Mutable Base Addon class
    '''

    def __init__(self,
        name: str,
        update_url: str = str(),
        descr: str = str(),
        contribs: List[str] = None,
        dependencies: List[str] = None,
        default_binding_type: BindingType = BindingType.AGNOSTIC
        ):

        super().__init__(
            name=name,
            update_url=update_url,
            descr=descr,
            contribs=contribs,
            dependencies=dependencies,
            default_binding_type=default_binding_type
        )

    @AddonBase.name.setter
    def name(self, new_name: str) -> None:
        '''
        Set the addon name
        '''
        self._name = new_name

    @AddonBase.update_url.setter
    def update_url(self, new_update_url: str) -> None:
        '''
        Set the addon update url
        '''
        self._update_url = new_update_url

    @AddonBase.description.setter
    def description(self, new_description: str) -> None:
        '''
        Set the addon description
        '''
        self._descr = new_description

    @AddonBase.contributors.setter
    def contributors(self, contribs: List[str]):
        '''
        Set the list of contributors
        '''
        self._contributors = contribs

    @AddonBase.dependencies.setter
    def dependencies(self, dependencies: List[str]):
        '''
        Set the list of dependencies
        '''
        self._dependencies = dependencies

    @staticmethod
    def from_dict(json: dict, default_binding_type: BindingType = BindingType.AGNOSTIC):
        '''
        Return this class object from dict representation
        '''
        return MutableAddonBase(
            json['name'],
            json['uri'] if 'uri' in json else "",
            json['description'] if 'description' in json else "",
            json['contribs'] if 'contribs' in json else [],
            default_binding_type
        )
