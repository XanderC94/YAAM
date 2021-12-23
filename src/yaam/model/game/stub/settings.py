'''
Abstract Game Incarnation model class
'''
import pickle
from typing import List
from yaam.utils.logger import static_logger as logger
from yaam.model.type.binding import BindingType
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

    def add_addon_base(self, base: AddonBase) -> bool:
        ret = False
        if base.name not in self._bases:
            self._bases[base.name] = base
            ret = True

        return ret

    def add_addon_binding(self, binding: Binding) -> bool:
        ret = False
        if binding.typing not in self._bindings or binding.name not in self._bindings[binding.typing]:
            self._bindings[binding.typing][binding.name] = binding
            ret = True

        return ret

    def synthetize(self) -> List[Addon]:
        '''
        Creates addons incarnations from bases and bindings
        '''
        addons : List[Addon] = list()

        # build addons incarnations by binding
        for binding_type in BindingType:
            if binding_type in self._bindings:
                for (addon_name, binding) in self._bindings[binding_type].items():

                    addon_base = self._bases.get(addon_name, None)

                    if addon_base is not None:
                        addon = Addon(addon_base, binding)
                        addons.append(addon)

        logger().info(msg=f"Incarnated {len(addons)} addons...")

        return addons

    def digest(self) -> str:
        '''
        Return a unique digest representation of the object state
        '''
        hasher = Hasher.SHA512.create()

        hasher.update(self._binding_type.name.encode(encoding='utf-8'))

        for _ in self._args.values():
            hasher.update(pickle.dumps([_.meta.name, _.value, _.enabled]))

        for _ in self._bases.values():
            hasher.update(pickle.dumps([
                _.name, _.uri, _.dependencies
            ]))

        for bindings in self._bindings.values():
            for binding in bindings.values():
                hasher.update(pickle.dumps([
                    str(binding.path), binding.typing, binding.enabled, binding.updateable
                ]))

        return hasher.hexdigest()
