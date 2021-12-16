'''
YAAM Read-Evaluate-print loop module
'''

from yaam.controller.cmd.state.base import AREPLState
from yaam.controller.cmd.state.create import REPLCreateMode, REPLCreateState
from yaam.model.game.base import Game

class REPL(AREPLState):
    '''
    Yaam REPL class implementation
    '''

    def __init__(self, game: Game, completekey: str = 'tab', stdin = None, stdout = None) -> None:
        super().__init__("YAAM", game, completekey=completekey, stdin=stdin, stdout=stdout)

    def do_new(self, args: str):
        '''
        Create new Addons, Bindings or Chainload sequences

        Example: new <addon | binding | chain>
        '''
        mode = REPLCreateMode.from_string(args)

        if mode is not REPLCreateMode.NONE:
            new_state = REPLCreateState(self.name, mode, self._game, self.completekey, self.stdin, self.stdout)
            new_state.loop()

        return False

    def do_edit(self, args: str):
        '''
        Edit existing Arguments, Addons, Bindings, Chainload sequences

        Example: edit <argument | addon | binding | chain> [name]
        '''
        print("Requested: ", "edit", args)
        return False

    def do_delete(self, args: str):
        '''
        Delete existing Addons, Bindings or Chainload sequences

        Example: delete <addon | binding | chain> [name] [binding-type (opt)]
        '''
        print("Requested: ", "delete", args)
        return False

    def do_list(self, args: str):
        '''
        List existing Addons, Bindings or Chainload sequences

        Example: list <addons | bindings | chains>
        '''
        print("Requested: ", "list", args)
        
        if args.lower() == "addons":
            for base in self._game.settings.bases.values():
                self.stdout.write(f"{str(base)}\n")
        elif args.lower() == "bindings":
            for bindings in self._game.settings.bindings.values():
                for binding in bindings.values():
                    self .stdout.write(f"{str(binding)}\n")

        return False

    def _can_complete(self, args: str) -> bool:
        return True

def repl(game: Game):
    '''
    Run REP loop
    '''
    REPL(game).loop()
