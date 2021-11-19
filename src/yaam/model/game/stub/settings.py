'''
Abstract Game Incarnation model class
'''
import pickle
from yaam.utils.hashing import Hasher

from yaam.model.mutable.argument import Argument
from yaam.model.mutable.binding import Binding
from yaam.model.mutable.addon import Addon, AddonBase
from yaam.model.game.abstract.settings import AbstractYaamGameSettings

class YaamGameSettings(AbstractYaamGameSettings[
        Addon, Binding, Argument, AddonBase
    ]):
    '''
    Yaam Game Settings model class stub
    '''

    def digest(self) -> str:
        '''
        Return a unique digest representation of the object state
        '''
        hasher = Hasher.SHA512.create()

        hasher.update(self._binding_type.name.encode(encoding='utf-8'))

        for _ in self._args.values():
            hasher.update(pickle.dumps([_.meta.name, _.value, _.enabled]))

        for _ in self._addons:
            hasher.update(pickle.dumps([
                _.base.name, _.base.uri, _.base.dependencies,
                str(_.binding.path), _.binding.typing,
                _.binding.enabled, _.binding.updateable
            ]))

        for chain in self._chains:
            for _ in chain:
                hasher.update(pickle.dumps(_))

        return hasher.hexdigest()
