'''
'''
from abc import abstractmethod
from typing import List
from yaam.model.binding_type import BindingType
from yaam.model.incarnator import StaticIncarnator
from yaam.model.game.config import IGameConfiguration
from yaam.model.game.settings import IYaamGameSettings
from yaam.model.context import ApplicationContext
from yaam.model.mutable.addon import MutableAddon
from yaam.model.mutable.addon_base import MutableAddonBase
from yaam.model.mutable.argument import MutableArgument
from yaam.model.mutable.binding import MutableBinding
from yaam.model.synthetizer import Synthetizer

from copy import deepcopy

IYaamGameSettingsStub = IYaamGameSettings[
    MutableAddon, MutableBinding, MutableArgument, MutableAddonBase
]

class Game(Synthetizer[List[MutableAddon]]):
    '''
    Game class trait
    '''
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettingsStub) -> None:
        self._config = config
        self._yaam_settings = settings

    @property
    def config(self) -> IGameConfiguration:
        '''
        Return the game configuration
        '''
        return self._config

    @property
    def settings(self) -> IYaamGameSettingsStub:
        '''
        Return the yaam's game setting
        '''
        return self._yaam_settings

    def synthetize(self) -> List[MutableAddon]:
        '''
        Synthetize a coherent list of addons to enable / disable / update / ...
        '''
        binding_lut = set([
            BindingType.SHADER,
            BindingType.EXE,
            BindingType.AGNOSTIC,
            self.settings.binding,
        ])

        addons_copy = deepcopy(self.settings.addons)

        # override addon settings
        for addon in addons_copy:
            if addon.binding.typing not in binding_lut:
                addon.binding.enabled = False
            elif addon.binding.typing is BindingType.SHADER and addon.binding.typing in binding_lut:
                binding_lut.remove(addon.binding.typing)

        return addons_copy

class IGameIncarnator(StaticIncarnator[ApplicationContext, Game]):
    '''
    Game class static incarnator trait
    '''

    @staticmethod
    @abstractmethod
    def incarnate(app_context: ApplicationContext = None) -> Game:
        '''
        Create an incarnation of the game
        '''
        return None
    