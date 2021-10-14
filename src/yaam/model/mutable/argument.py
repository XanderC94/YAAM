'''
Mutable Argument module
'''

from yaam.model.immutable.argument import Argument, ArgumentIncarnation, Incarnator, Any

class MutableArgument(Incarnator[Any, ArgumentIncarnation], object):
    '''
    Mutable Argument model class
    '''

    def __init__(self, arg: Argument, value:Any = None, enabled=False):
        self.value = value
        self.enabled = enabled
        self._argument = arg

    @property
    def argument(self):
        '''
        Returns underlying argument
        '''
        return self._argument

    def incarnate(self, decoration: Any = None) -> ArgumentIncarnation:
        return self.argument.incarnate(decoration=self.value)

    @staticmethod
    def from_dict(json_obj:dict):
        '''
        Return the object representation of this object
        '''
        return MutableArgument(Argument.from_dict(json_obj))
        