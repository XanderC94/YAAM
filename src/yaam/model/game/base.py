'''
Base game module
'''

from typing import List
from copy import deepcopy
from yaam.model.context import GameContext
from yaam.model.type.binding import BindingType
from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.mutable.addon import Addon
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.argument import Argument
from yaam.model.mutable.binding import Binding
from yaam.patterns.synthetizer import Synthetizer
from yaam.utils.exceptions import Found
from yaam.utils.logger import static_logger as logger

IYGS = IYaamGameSettings[
    Addon, Binding, Argument, AddonBase
]

class Game(Synthetizer[List[Addon]]):
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

    def synthetize(self) -> List[Addon]:
        '''
        Synthetize a coherent list of addons to enable / disable / update / ...
        '''
        binding_lut = set([
            BindingType.EXE,
            BindingType.AGNOSTIC,
            self.settings.binding,
        ])

        addons_copy = deepcopy(self.settings.addons)

        # override addon settings
        # for those not in the LUT
        for addon in addons_copy:
            if addon.binding.typing not in binding_lut:
                addon.binding.enabled = False

        # automated shader selection
        index = None
        try:
            shader_priority = [ self.settings.binding, BindingType.AGNOSTIC, BindingType.EXE ]
            for shader in shader_priority:
                for (i, addon) in enumerate(addons_copy):
                    if addon.base.is_shader and addon.binding.typing == shader and addon.binding.enabled:
                        # first matching is chosen as shader
                        raise Found(i)
        except Found as found:
            index = found.content
        finally:
            if index is None:
                logger().info(msg="No compatible shader composition could be created. Disabling any enabled shader.")

            for (i, addon) in enumerate(addons_copy):
                if i != index and addon.base.is_shader and addon.binding.enabled:
                    addon.binding.enabled = False

        return addons_copy
