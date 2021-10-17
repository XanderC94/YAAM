'''
Abstract Game Incarnation model class
'''

from yaam.model.mutable.argument import MutableArgument
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.addon import MutableAddon, MutableAddonBase
from yaam.model.game.abstract.settings import AbstractYaamGameSettings

class YaamGameSettings(AbstractYaamGameSettings[
        MutableAddon, MutableBinding, MutableArgument, MutableAddonBase
    ]):
    '''
    Yaam Game Settings model class stub
    '''
