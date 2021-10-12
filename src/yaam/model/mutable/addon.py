'''
Mutable Addon module
'''
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.addon_base import MutableAddonBase
from yaam.model.immutable.addon import Addon

class MutableAddon(Addon):
    '''
    Mutable Addon incarnation class
    '''

    def __init__(self, base: MutableAddonBase, binding: MutableBinding):

        super().__init__(base, binding)
    