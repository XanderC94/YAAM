'''
Timer class module
'''
import time

class Timer(object):
    '''
    Timer class
    '''

    def __init__(self) -> None:
        self.__tick : float = 0
        self.__tock : float = 0
        self.__tock_called = False

    def tick(self):
        '''
        Register timer start
        '''
        self.__tick = time.time()
        self.__tock_called = False

    def tock(self):
        '''
        Register timer end
        '''
        self.__tock = time.time()
        self.__tock_called = True
    
    def delta(self):
        '''
        Compute delta

        * computes tock-tick if tock has been called
        * computes current_time-tick if tock has been called 
        or tick has been called after a tock

        '''
        if self.__tock_called:
            return self.__tock - self.__tick
        else:
            return time.time() - self.__tick
