'''
Addon module
'''
from typing import List
from yaam.model.mutable.binding import MutableBinding
from yaam.model.immutable.addon import AddonBase, Addon

class MutableAddonBase(AddonBase):

    '''
    Base Addon Class
    '''
    def __init__(self,
        name: str, update_url: str = str(),
        descr: str = str(), contribs: List[str] = None):

        super().__init__(
            name=name,
            update_url=update_url,
            descr=descr,
            contribs=contribs
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

class MutableAddon(Addon, MutableAddonBase, MutableBinding):
    '''
    Addon incarnation class
    '''

    def __init__(self, base: MutableAddonBase, binding: MutableBinding):

        super().__init__(base, binding)
        