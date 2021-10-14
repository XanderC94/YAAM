'''
Abstract Game Incarnation model class
'''

from yaam.model.mutable.argument import MutableArgument
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.addon import MutableAddon, MutableAddonBase
from yaam.model.game.abstract_settings import AbstractYaamGameSettings

class YaamGameSettingsStub(AbstractYaamGameSettings[
        MutableAddon, MutableBinding, MutableArgument, MutableAddonBase
    ]):
    '''
    Yaam Game Settings model class stub
    '''
