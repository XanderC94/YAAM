'''
Base game module
'''

from typing import List
from copy import deepcopy
from yaam.model.appcontext import GameContext
from yaam.model.game.contract.base import IGame
from yaam.model.type.binding import BindingType
from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.mutable.addon import IAddon
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.argument import Argument
from yaam.model.mutable.binding import Binding
from yaam.utils.logger import static_logger as logger

IYGS = IYaamGameSettings[AddonBase, Binding, Argument]


class AbstractGame(IGame[AddonBase, Binding]):
    '''
    Game class trait
    '''
    def __init__(self, config: IGameConfiguration, settings: IYGS, context: GameContext) -> None:
        self._config = config
        self._yaam_settings = settings
        self._context = context

    @property
    def context(self) -> GameContext:
        '''
        Return the current game context
        '''
        return self._context

    @property
    def config(self) -> IGameConfiguration:
        '''
        Return the game configuration
        '''
        return self._config

    @property
    def settings(self) -> IYGS:
        '''
        Return yaam's game setting
        '''
        return self._yaam_settings

    def synthetize(self) -> List[IAddon[AddonBase, Binding]]:
        '''
        Synthetize a coherent list of addons to enable / disable / update / ...
        '''
        binding_lut = set([
            BindingType.EXE,
            BindingType.AGNOSTIC,
            BindingType.FILE,
            self.settings.binding_type,
        ])

        addons_copy = deepcopy(self.settings.synthetize())

        # override addon settings
        # for those not in the LUT
        for addon in addons_copy:
            if addon.binding.typing not in binding_lut:
                addon.binding.is_enabled = False

        # automated shader selection
        index = None

        shader_priority = [self.settings.binding_type, BindingType.AGNOSTIC]
        for shader in shader_priority:
            for (i, addon) in enumerate(addons_copy):
                if addon.base.is_shader and addon.binding.typing == shader and addon.binding.is_enabled:
                    # first matching is chosen as shader
                    index = i
                    break

            if index is not None:
                break

        if index is None:
            logger().info(msg="No compatible shader composition could be created. Disabling any enabled shader.")

        for (i, addon) in enumerate(addons_copy):
            if i != index and addon.base.is_shader and addon.binding.is_enabled:
                addon.binding.is_enabled = False

        return addons_copy
