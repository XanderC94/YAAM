'''
Yaam command line options module
'''
from enum import Enum
from collections import namedtuple
from typing import Any, Set, List

OptionEntry = namedtuple(
    typename='OptionEntry',
    field_names=['index', 'aliases', 'default', 'action', 'descr'],
    defaults=[int(), set(), None, str(), str()]
)

OptionGroupEntry = namedtuple(
    typename='OptionGroupEntry',
    field_names=['index', 'options', 'mutually_exclusive'],
    defaults=[int(), list(), False]
)

class Option(Enum):
    '''
    Yaam command line options
    '''
    UPDATE_ADDONS = OptionEntry(
        index=0,
        aliases=set(["update", "update-addons", "update_addons", "u"]),
        default=False,
        descr="Only update addons without running the game",
        action="store_true"
    )

    RUN_STACK = OptionEntry(
        index=1,
        aliases=set(["run", "run-stack", "run_stack", "r"]),
        default=False,
        descr="Only run the game without updating the addons",
        action="store_true"
    )

    EDIT = OptionEntry(
        index=2,
        aliases=set(["edit", "e"]),
        default=False,
        descr="Run YAAM edit repl",
        action="store_true"
    )

    AUTOCLOSE = OptionEntry(
        index=3,
        aliases=set(["auto-close", "auto_close", "a"]),
        default=False,
        descr="Auto close YAAM after main script completed",
        action="store_true"
    )

    def __hash__(self) -> int:
        return hash(tuple([self.index, *[ _ for _ in self.aliases ], self.default]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        else:
            return False

    @property
    def aliases(self) -> Set[str]:
        '''
        Return option aliases
        '''
        return self.value.aliases

    @property
    def index(self) -> int:
        '''
        return option index
        '''
        return self.value.index

    @property
    def default(self) -> Any:
        '''
        Return default option value
        '''
        return self.value.default

    @property
    def descr(self) -> str:
        '''
        Return option description (help)
        '''
        return self.value.descr

    @property
    def action(self) -> str:
        '''
        Return the option action upon specification
        '''
        return self.value.action

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        obj = None

        for _ in Option:
            if str_repr == _.name or str_repr in _.aliases:
                obj = _
                break

        return obj

#############################################################

class OptionGroup(Enum):
    '''
    Yaam command line options groups
    '''
    EXECUTION_MODE=OptionGroupEntry(
        index=0,
        options=[Option.RUN_STACK, Option.UPDATE_ADDONS],
        mutually_exclusive=True
    )

    GLOBAL=OptionGroupEntry(
        index=1,
        options=[Option.EDIT, Option.AUTOCLOSE],
        mutually_exclusive=False
    )

    def __hash__(self) -> int:
        return hash(tuple([self.index, *[ hash(_) for _ in self.options]]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        else:
            return False

    @property
    def options(self) -> List[Option]:
        '''
        Return options
        '''
        return self.value.options

    @property
    def index(self) -> tuple:
        '''
        return option index
        '''
        return self.value.index

    def is_mutally_exclusive(self) -> bool:
        '''
        Return if the options in the group are mutually exclusive
        '''
        return self.value.mutually_exclusive

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        obj = None

        for _ in Option:
            if str_repr == _.name:
                obj = _
                break

        return obj
