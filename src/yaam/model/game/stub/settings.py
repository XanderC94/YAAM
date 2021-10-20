'''
Abstract Game Incarnation model class
'''

from yaam.model.mutable.argument import MutableArgument
from yaam.model.mutable.binding import Binding
from yaam.model.mutable.addon import Addon, AddonBase
from yaam.model.game.abstract.settings import AbstractYaamGameSettings

class YaamGameSettings(AbstractYaamGameSettings[
        Addon, Binding, MutableArgument, AddonBase
    ]):
    '''
    Yaam Game Settings model class stub
    '''
