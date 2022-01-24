'''
Base REPL state class module
'''

from abc import abstractmethod
from cmd import Cmd
from yaam.model.game.base import Game


class AREPLState(Cmd):
    '''
    Abstract REPL state class
    '''

    def __init__(self, name: str, game: Game, completekey: str = 'tab', stdin=None, stdout=None) -> None:
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)

        self.__name = name
        self.intro = f"{self.__name} repl started. Use \"help\" or \"?\" to list available interactions."
        self.outro = f"{self.__name} repl ended."
        self.prompt = f"({self.__name}): "
        self._game: Game = game

    @property
    def name(self):
        '''
        Return REPL state name
        '''
        return self.__name

    def preloop(self) -> None:
        '''
        Do stuff before the REPL loop starts
        '''
        return super().preloop()

    def precmd(self, line: str) -> str:
        '''
        Do stuff before the command is evaluated
        '''
        return super().precmd(line)

    def loop(self):
        '''
        Run REPL loop
        '''
        self.cmdloop()

    @abstractmethod
    def _can_complete(self, args: str) -> bool:
        '''
        Return whether or not the mode can be completed
        '''
        return True

    def do_complete(self, args: str):
        '''
        Complete and exit the REPL
        '''
        return self._can_complete(args)

    def do_exit(self, _: str):
        '''
        Exit the REPL without saving progresses
        '''
        return True

    def postcmd(self, stop: bool, line: str) -> bool:
        '''
        Do stuff after the command evaluation has been executed
        '''
        return super().postcmd(stop, line)

    def postloop(self) -> None:
        '''
        Do stuff after the REPL loop has completed
        '''
        print(self.outro)
        return super().postloop()
