'''
Simple counter class module
'''


class ForwardCounter(object):
    '''
    Simple forward counter class implementation
    '''

    def __init__(self, start: int = 0, step: int = 1) -> None:
        self.__start = start
        self.__step = step
        self.__value = start

    def count(self) -> int:
        '''
        return the current counter value and evaluate the next one
        '''
        res = self.__value
        self.__value += self.__step
        return res

    def __int__(self) -> int:
        '''
        return the current counter value
        '''
        return self.__value

    def __str__(self) -> str:
        '''
        return the counter string representation
        '''
        return str(self.__value)

    def next(self) -> int:
        '''
        evaluate the next counter value and returns it
        '''
        self.__value += self.__step
        return self.__value

    def reset(self) -> None:
        '''
        Reset the counter value to the starting one
        '''
        self.__value = self.__start

    def __add__(self, other) -> int:
        if isinstance(other, int):
            return int(self) + other
        elif isinstance(other, ForwardCounter):
            return int(self) + int(other)
        else:
            raise Exception(f"Invalid sum operation between {type(self)} and {type(other)}")

    def __radd__(self, other) -> int:
        return self.__add__(other)
